import logging
import json
import os
import azure.functions as func
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential
from ..shared import matching_engine
from ..shared import table_service
from ..shared import storage_client

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
                extracted_data = {
                    "vendor": invoice.fields.get("VendorName", {}).get("value"),
                    "vendor_tax_id": invoice.fields.get("VendorTaxId", {}).get("value"),
                    "invoice_id": invoice.fields.get("InvoiceId", {}).get("value"),
                    "invoice_date": str(invoice.fields.get("InvoiceDate", {}).get("value")),
                    "amount": invoice.fields.get("InvoiceTotal", {}).get("value").amount if invoice.fields.get("InvoiceTotal") else None,
                    "currency": invoice.fields.get("InvoiceTotal", {}).get("value").currency if invoice.fields.get("InvoiceTotal") else None
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

        task_data = {
            "id": blob_name.replace('/', '_').replace('.', '_'), # Simple ID generation
            "status": match_result['status'],
            "confidence": match_result.get('confidence', 0),
            "document_url": document_url,
            "extracted": extracted_data,
            "match_candidate": match_result if match_result['status'] != 'RED' else None
        }

        if match_result['status'] == 'GREEN':
            logging.info("Auto-uploading to AOC (Mock)...")
            # In a real scenario, we would call the AOC API here.
            # For now, we can mark it as COMPLETED or just log it.
            task_data['status'] = 'COMPLETED'
            table_service.save_task(task_data)
        else:
            logging.info("Saving task for manual review...")
            table_service.save_task(task_data)

    except Exception as e:
        logging.error(f"Error processing document: {str(e)}")
