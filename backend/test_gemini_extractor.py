"""
Test script for Gemini structured output extractor.

Usage:
    python test_gemini_extractor.py <path_to_invoice.pdf>

Environment variables:
    GOOGLE_API_KEY: Your Google Gemini API key (required)
    GEMINI_MODEL_ID: Model to use (default: gemini-3-pro-preview)
"""

import os
import sys
import logging
from shared.gemini_extractor import GeminiExtractor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    if len(sys.argv) < 2:
        print("Usage: python test_gemini_extractor.py <path_to_invoice.pdf>")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    
    if not os.path.exists(pdf_path):
        print(f"Error: File not found: {pdf_path}")
        sys.exit(1)
    
    # Check for API key
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("Error: GOOGLE_API_KEY environment variable not set")
        print("Get your API key from: https://aistudio.google.com/app/apikey")
        sys.exit(1)
    
    model_id = os.getenv("GEMINI_MODEL_ID", "gemini-3-pro-preview")
    
    try:
        # Initialize extractor
        extractor = GeminiExtractor(api_key=api_key, model_id=model_id)
        
        # Read PDF file
        with open(pdf_path, 'rb') as f:
            pdf_content = f.read()
        
        logger.info(f"📄 Processing PDF: {pdf_path} ({len(pdf_content)} bytes)")
        
        # Extract data
        result = extractor.extract_from_invoice(pdf_content, filename=os.path.basename(pdf_path))
        
        # Print results
        print("\n" + "="*60)
        print("EXTRACTION RESULTS")
        print("="*60)
        print(f"Company: {result.get('company', 'N/A')}")
        print(f"Date: {result.get('date', 'N/A')}")
        print(f"Address: {result.get('address', 'N/A')}")
        print(f"Total: {result.get('total', 'N/A')}")
        print(f"Confidence: {result.get('confidence', 0):.2%}")
        
        if 'invoice_number' in result:
            print(f"Invoice Number: {result['invoice_number']}")
        
        if 'items' in result and result['items']:
            print(f"\nItems ({len(result['items'])}):")
            for i, item in enumerate(result['items'], 1):
                print(f"  {i}. {item.get('description', 'N/A')}")
                print(f"     Quantity: {item.get('quantity', 0)}")
                print(f"     Gross Worth: {item.get('gross_worth', 0)}")
        
        if 'total_gross_worth' in result:
            print(f"\nTotal Gross Worth: {result['total_gross_worth']}")
        
        print("="*60)
        
    except Exception as e:
        logger.error(f"❌ Extraction failed: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
