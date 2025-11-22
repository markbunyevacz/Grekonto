import azure.functions as func
import azure.durable_functions as df
import logging
import os
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential
from ..shared import sroie_utils

def activity_ocr(blob_data: dict) -> dict:
    """Extract text and data from document using Azure Document Intelligence"""
    try:
        logging.info(f"Processing OCR for: {blob_data['blob_name']}")
        
        # Get credentials
        endpoint = os.getenv("DOCUMENT_INTELLIGENCE_ENDPOINT") or os.getenv("FORM_RECOGNIZER_ENDPOINT")
        key = os.getenv("DOCUMENT_INTELLIGENCE_KEY") or os.getenv("FORM_RECOGNIZER_KEY")
        
        if not endpoint or not key:
            logging.warning("Document Intelligence credentials missing. Using mock data.")
            return {
                "success": True,
                "extracted_data": {
                    "vendor": "Mock Vendor",
                    "amount": 1000,
                    "currency": "HUF"
                }
            }
        
        # Initialize client
        client = DocumentAnalysisClient(endpoint=endpoint, credential=AzureKeyCredential(key))
        
        # Analyze document
        with open(blob_data['blob_path'], "rb") as f:
            poller = client.begin_analyze_document("prebuilt-invoice", document=f)
        
        result = poller.result()
        
        # Extract invoice data
        extracted_data = sroie_utils.extract_invoice_data_from_form_recognizer(result)
        
        logging.info(f"OCR completed for: {blob_data['blob_name']}")
        
        return {
            "success": True,
            "extracted_data": extracted_data
        }
    except Exception as e:
        logging.error(f"OCR activity failed: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

main = df.ActivityFunction(activity_ocr)

