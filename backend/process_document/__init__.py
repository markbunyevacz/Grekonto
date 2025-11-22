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
from ..shared import sroie_utils

def main(myblob: func.InputStream):
    # Generate file ID from blob name
    blob_name = '/'.join(myblob.name.split('/')[1:])  # Remove container name
    file_id = blob_name.replace('/', '_').replace('.', '_')

    logging.info('='*80)
    logging.info(f"🔄 BLOB TRIGGER ACTIVATED")
    logging.info(f"📄 Blob: {myblob.name}")
    logging.info(f"📦 Size: {myblob.length} bytes")
    logging.info(f"🆔 File ID: {file_id}")
    logging.info('='*80)

    try:
        # Update status: OCR started
        table_service.update_processing_status(
            file_id=file_id,
            stage="OCR_STARTED",
            status="IN_PROGRESS",
            message="Starting OCR with Azure Document Intelligence"
        )

        # 1. Call Azure Document Intelligence
        endpoint = os.getenv("DOCUMENT_INTELLIGENCE_ENDPOINT") or os.getenv("FORM_RECOGNIZER_ENDPOINT")
        key = os.getenv("DOCUMENT_INTELLIGENCE_KEY") or os.getenv("FORM_RECOGNIZER_KEY")

        if not endpoint or not key:
            logging.warning("⚠️  Document Intelligence credentials missing. Using mock data.")
            table_service.update_processing_status(
                file_id=file_id,
                stage="OCR_SKIPPED",
                status="SUCCESS",
                message="OCR skipped - credentials not configured. Using mock data."
            )
            extracted_data = {"vendor": "Mock Vendor", "amount": 1000, "currency": "HUF"} # Fallback
        else:
            logging.info(f"🤖 Initializing Azure Document Intelligence")
            logging.info(f"🔗 Endpoint: {endpoint}")

            document_analysis_client = DocumentAnalysisClient(
                endpoint=endpoint, credential=AzureKeyCredential(key)
            )

            # Read blob content
            blob_content = myblob.read()
            logging.info(f"📖 Read {len(blob_content)} bytes from blob")

            logging.info(f"🔍 Starting OCR analysis with prebuilt-invoice model...")
            poller = document_analysis_client.begin_analyze_document(
                "prebuilt-invoice", document=blob_content
            )

            logging.info(f"⏳ Waiting for OCR results...")
            invoices = poller.result()
            logging.info(f"✅ OCR completed!")
            
            # Extract first invoice data
            if invoices.documents:
                invoice = invoices.documents[0]
                logging.info(f"📋 Found {len(invoices.documents)} invoice(s) in document")
                logging.info(f"DEBUG: type(invoice) = {type(invoice)}")
                logging.info(f"DEBUG: type(invoice.fields) = {type(invoice.fields)}")
                logging.info(f"DEBUG: invoice.fields keys = {list(invoice.fields.keys()) if hasattr(invoice.fields, 'keys') else 'No keys'}")

                # Check for special indicators in the full content
                content = invoices.content
                special_indicators = []
                if "Pénzforgalmi elszámolás" in content:
                    special_indicators.append("Pénzforgalmi elszámolás")
                if "Fordított ÁFA" in content:
                    special_indicators.append("Fordított ÁFA")
                if "EPR díj" in content:
                    special_indicators.append("EPR díj")

                def get_value(field_name):
                    field = invoice.fields.get(field_name)
                    return field.value if field else None

                invoice_total = get_value("InvoiceTotal")
                if invoice_total:
                    logging.info(f"DEBUG: type(invoice_total) = {type(invoice_total)}")
                    logging.info(f"DEBUG: dir(invoice_total) = {dir(invoice_total)}")
                    logging.info(f"DEBUG: invoice_total = {invoice_total}")

                extracted_data = {
                    "vendor": sroie_utils.normalize_text(get_value("VendorName")),
                    "vendor_tax_id": get_value("VendorTaxId"),
                    "invoice_id": get_value("InvoiceId"),
                    "invoice_date": sroie_utils.normalize_date(get_value("InvoiceDate")),
                    "amount": getattr(invoice_total, 'amount', None) if invoice_total else None,
                    "currency": getattr(invoice_total, 'symbol', getattr(invoice_total, 'code', None)) if invoice_total else None,
                    "special_indicators": special_indicators
                }
                
                # SROIE Validation (Optional logging)
                missing_fields = sroie_utils.validate_sroie_fields({
                    "company": extracted_data["vendor"],
                    "date": extracted_data["invoice_date"],
                    "total": extracted_data["amount"],
                    "address": "N/A" # Address is not always extracted by invoice model
                })
                if missing_fields:
                    logging.warning(f"⚠️ SROIE Validation: Missing fields: {missing_fields}")

                logging.info(f"📊 Extracted fields:")
                logging.info(f"   • Vendor: {extracted_data.get('vendor')}")
                logging.info(f"   • Tax ID: {extracted_data.get('vendor_tax_id')}")
                logging.info(f"   • Invoice ID: {extracted_data.get('invoice_id')}")
                logging.info(f"   • Amount: {extracted_data.get('amount')} {extracted_data.get('currency')}")
                logging.info(f"   • Date: {extracted_data.get('invoice_date')}")
                if special_indicators:
                    logging.info(f"   • Special indicators: {', '.join(special_indicators)}")
            else:
                logging.warning("⚠️  No invoices found in document")
                extracted_data = {}

        # Update status: OCR completed
        table_service.update_processing_status(
            file_id=file_id,
            stage="OCR_COMPLETED",
            status="SUCCESS",
            message=f"Extracted data from invoice: {extracted_data.get('vendor', 'Unknown')} - {extracted_data.get('amount', 0)} {extracted_data.get('currency', 'HUF')}"
        )

        logging.info('='*80)
        logging.info(f"✅ OCR COMPLETED")
        logging.info(f"📊 Extracted Data: {json.dumps(extracted_data, indent=2)}")
        logging.info('='*80)

        # 2. Run Matching Logic
        table_service.update_processing_status(
            file_id=file_id,
            stage="MATCHING_STARTED",
            status="IN_PROGRESS",
            message="Starting matching with NAV data"
        )

        logging.info('='*80)
        logging.info(f"🔍 STARTING MATCHING ENGINE")
        logging.info('='*80)

        match_result = matching_engine.find_match(extracted_data)

        logging.info('='*80)
        logging.info(f"✅ MATCHING COMPLETED")
        logging.info(f"📊 Match Status: {match_result['status']}")
        logging.info(f"📊 Match Details: {json.dumps(match_result, indent=2)}")
        logging.info('='*80)

        table_service.update_processing_status(
            file_id=file_id,
            stage="MATCHING_COMPLETED",
            status="SUCCESS",
            message=f"Matching completed with status: {match_result['status']}"
        )

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
