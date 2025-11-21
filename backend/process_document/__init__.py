import logging
import json
import os
import datetime
import azure.functions as func
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential
from ..shared import matching_engine
from ..shared import table_service
from ..shared import storage_client
from ..shared.aoc_client import AOCClient

def main(myblob: func.InputStream):
    logging.info(f"Python blob trigger function processed blob \n"
                 f"Name: {myblob.name} \n"
                 f"Blob Size: {myblob.length} bytes")

    try:
        # 1. Call Azure Document Intelligence
        endpoint = os.getenv("FORM_RECOGNIZER_ENDPOINT")
        key = os.getenv("FORM_RECOGNIZER_KEY")

        if not endpoint or not key:
            logging.warning("Form Recognizer credentials missing. Skipping OCR.")
            extracted_data = {"vendor": "Mock Vendor", "amount": 1000, "currency": "HUF"} # Fallback
        else:
            document_analysis_client = DocumentAnalysisClient(
                endpoint=endpoint, credential=AzureKeyCredential(key)
            )
            
            # Read blob content
            blob_content = myblob.read()
            
            poller = document_analysis_client.begin_analyze_document(
                "prebuilt-invoice", document=blob_content
            )
            invoices = poller.result()
            
            # Extract first invoice data
            if invoices.documents:
                invoice = invoices.documents[0]

                # Check for special indicators in the full content
                content = invoices.content
                special_indicators = []
                if "Pénzforgalmi elszámolás" in content:
                    special_indicators.append("Pénzforgalmi elszámolás")
                if "Fordított ÁFA" in content:
                    special_indicators.append("Fordított ÁFA")
                if "EPR díj" in content:
                    special_indicators.append("EPR díj")

                extracted_data = {
                    "vendor": invoice.fields.get("VendorName", {}).get("value"),
                    "vendor_tax_id": invoice.fields.get("VendorTaxId", {}).get("value"),
                    "invoice_id": invoice.fields.get("InvoiceId", {}).get("value"),
                    "invoice_date": str(invoice.fields.get("InvoiceDate", {}).get("value")),
                    "amount": invoice.fields.get("InvoiceTotal", {}).get("value").amount if invoice.fields.get("InvoiceTotal") else None,
                    "currency": invoice.fields.get("InvoiceTotal", {}).get("value").currency if invoice.fields.get("InvoiceTotal") else None,
                    "special_indicators": special_indicators
                }
            else:
                extracted_data = {}

        logging.info(f"Extracted Data: {json.dumps(extracted_data)}")

        # 2. Run Matching Logic
        match_result = matching_engine.find_match(extracted_data)
        logging.info(f"Match Result: {match_result['status']}")

        # 3. Save Result to Table Storage
        # Generate SAS URL for the blob
        # myblob.name is usually "container/blobname"
        container_name = myblob.name.split('/')[0]
        blob_name = '/'.join(myblob.name.split('/')[1:])
        document_url = storage_client.generate_sas_url(container_name, blob_name)

        # Log start of processing
        table_service.log_audit_event(
            event_type="PROCESSING_STARTED",
            message=f"Started processing {blob_name}",
            related_item_id=blob_name,
            client_name=extracted_data.get("vendor", "-")
        )

        task_data = {
            "id": blob_name.replace('/', '_').replace('.', '_'), # Simple ID generation
            "status": match_result['status'],
            "confidence": match_result.get('confidence', 0),
            "document_url": document_url,
            "extracted": extracted_data,
            "match_candidate": match_result if match_result['status'] != 'RED' else None,
            "created_at": datetime.datetime.utcnow().isoformat()
        }

        if match_result['status'] == 'GREEN':
            logging.info("Auto-uploading to AOC...")
            
            # Call AOC API
            aoc_client = AOCClient()
            upload_success = False
            
            # If we have a match_id (invoice internal ID in AOC), link it
            if match_result.get('match_id'):
                upload_success = aoc_client.upload_invoice_link(str(match_result['match_id']), document_url)
            
            if upload_success:
                logging.info("Successfully linked document to AOC invoice.")
                task_data['status'] = 'COMPLETED'
                table_service.save_task(task_data)

                table_service.log_audit_event(
                    event_type="MATCH",
                    message=f"Document matched automatically. AOC Upload: Success",
                    related_item_id=blob_name,
                    client_name=extracted_data.get("vendor", "-")
                )
                
                # Zero Data Retention: Delete the blob after successful processing
                logging.info(f"Deleting blob {blob_name} from {container_name}...")
                storage_client.delete_blob(container_name, blob_name)
            else:
                logging.error("Failed to link document to AOC. Keeping task as GREEN for manual review.")
                # Save as GREEN so it appears in manual review or we can treat it as error
                table_service.save_task(task_data)
                
                table_service.log_audit_event(
                    event_type="MATCH_UPLOAD_FAILED",
                    message=f"Document matched but AOC upload failed.",
                    related_item_id=blob_name,
                    client_name=extracted_data.get("vendor", "-")
                )

        else:
            logging.info("Saving task for manual review...")
            table_service.save_task(task_data)
            
            table_service.log_audit_event(
                event_type="MANUAL_REVIEW_REQUIRED",
                message=f"Document requires manual review. Status: {match_result['status']}",
                related_item_id=blob_name,
                client_name=extracted_data.get("vendor", "-")
            )

    except Exception as e:
        logging.error(f"Error processing document: {str(e)}")
        # Re-raise exception to trigger Azure Functions Retry Policy (defined in function.json)
        raise e
