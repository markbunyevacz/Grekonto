import os
import json
import glob
import time
import logging
from dotenv import load_dotenv
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential
from shared import sroie_utils

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load environment variables
load_dotenv()

# Try loading from local.settings.json if not in env
if not os.getenv("DOCUMENT_INTELLIGENCE_ENDPOINT"):
    settings_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "local.settings.json")
    if os.path.exists(settings_path):
        try:
            with open(settings_path, "r") as f:
                settings = json.load(f)
                values = settings.get("Values", {})
                if "DOCUMENT_INTELLIGENCE_ENDPOINT" in values:
                    os.environ["DOCUMENT_INTELLIGENCE_ENDPOINT"] = values["DOCUMENT_INTELLIGENCE_ENDPOINT"]
                if "DOCUMENT_INTELLIGENCE_KEY" in values:
                    os.environ["DOCUMENT_INTELLIGENCE_KEY"] = values["DOCUMENT_INTELLIGENCE_KEY"]
                if "FORM_RECOGNIZER_ENDPOINT" in values:
                    os.environ["FORM_RECOGNIZER_ENDPOINT"] = values["FORM_RECOGNIZER_ENDPOINT"]
                if "FORM_RECOGNIZER_KEY" in values:
                    os.environ["FORM_RECOGNIZER_KEY"] = values["FORM_RECOGNIZER_KEY"]
        except Exception as e:
            logging.warning(f"Failed to load local.settings.json: {e}")

ENDPOINT = os.getenv("DOCUMENT_INTELLIGENCE_ENDPOINT") or os.getenv("FORM_RECOGNIZER_ENDPOINT")
KEY = os.getenv("DOCUMENT_INTELLIGENCE_KEY") or os.getenv("FORM_RECOGNIZER_KEY")

if not ENDPOINT or not KEY:
    logging.error("Azure Document Intelligence credentials not found in environment variables.")
    exit(1)

# Paths
# BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# SROIE_IMG_DIR = os.path.join(BASE_DIR, "external", "ICDAR-2019-SROIE", "data", "img")
# SROIE_KEY_DIR = os.path.join(BASE_DIR, "external", "ICDAR-2019-SROIE", "data", "key")

# User provided path
SROIE_ROOT = r"C:\Users\Admin\.cursor\Grekonto\docs\datasets\SROIE_GitHub\data"
SROIE_IMG_DIR = os.path.join(SROIE_ROOT, "img")
SROIE_KEY_DIR = os.path.join(SROIE_ROOT, "key")

def analyze_document(client, file_path):
    with open(file_path, "rb") as f:
        poller = client.begin_analyze_document("prebuilt-receipt", document=f)
        result = poller.result()
    
    if not result.documents:
        return {}

    doc = result.documents[0]
    fields = doc.fields

    # Map Azure fields to SROIE fields
    # SROIE keys: company, date, address, total
    
    extracted = {}
    
    # Company / Vendor Name
    if "MerchantName" in fields:
        extracted["company"] = fields["MerchantName"].value
    elif "VendorName" in fields: # Fallback if using invoice model
        extracted["company"] = fields["VendorName"].value
        
    # Address
    if "MerchantAddress" in fields:
        val = fields["MerchantAddress"].value
        # Address might be an AddressValue object or string
        if hasattr(val, 'street_address'):
             extracted["address"] = f"{val.street_address}, {val.city}, {val.state}, {val.postal_code}" # Simplified
        else:
            extracted["address"] = str(val)
    elif "VendorAddress" in fields:
        extracted["address"] = str(fields["VendorAddress"].value)

    # Date
    if "TransactionDate" in fields:
        extracted["date"] = str(fields["TransactionDate"].value)
    elif "InvoiceDate" in fields:
        extracted["date"] = str(fields["InvoiceDate"].value)

    # Total
    if "Total" in fields:
        val = fields["Total"].value
        # Total might be CurrencyValue
        if hasattr(val, 'amount'):
            extracted["total"] = str(val.amount)
        else:
            extracted["total"] = str(val)
    elif "InvoiceTotal" in fields:
        val = fields["InvoiceTotal"].value
        if hasattr(val, 'amount'):
            extracted["total"] = str(val.amount)
        else:
            extracted["total"] = str(val)

    return extracted

def main():
    client = DocumentAnalysisClient(endpoint=ENDPOINT, credential=AzureKeyCredential(KEY))
    
    image_files = sorted(glob.glob(os.path.join(SROIE_IMG_DIR, "*.jpg")))
    
    # Limit for testing (uncomment to test on a small subset)
    # image_files = image_files[:20] 
    
    logging.info(f"Found {len(image_files)} images to process.")
    
    results = []
    
    for img_path in image_files:
        filename = os.path.basename(img_path)
        file_id = os.path.splitext(filename)[0]
        key_path = os.path.join(SROIE_KEY_DIR, f"{file_id}.json")
        
        if not os.path.exists(key_path):
            logging.warning(f"Key file not found for {filename}, skipping.")
            continue
            
        with open(key_path, "r", encoding="utf-8") as f:
            ground_truth = json.load(f)
            
        logging.info(f"Processing {filename}...")
        try:
            start_time = time.time()
            extracted = analyze_document(client, img_path)
            duration = time.time() - start_time
            
            # Compare
            scores = {}
            for field in ["company", "date", "address", "total"]:
                gt_val = ground_truth.get(field, "")
                ex_val = extracted.get(field, "")
                
                field_type = "text"
                if field == "date":
                    field_type = "date"
                elif field == "total":
                    field_type = "amount"
                    
                score = sroie_utils.calculate_similarity(gt_val, ex_val, field_type)
                scores[field] = score
                
            logging.info(f"  Scores: {scores}")
            
            results.append({
                "file": filename,
                "scores": scores,
                "ground_truth": ground_truth,
                "extracted": extracted,
                "duration": duration
            })
            
        except Exception as e:
            logging.error(f"Error processing {filename}: {e}")
            
    # Calculate average scores
    if not results:
        logging.info("No results to aggregate.")
        return

    avg_scores = {field: 0.0 for field in ["company", "date", "address", "total"]}
    for res in results:
        for field in avg_scores:
            avg_scores[field] += res["scores"].get(field, 0.0)
            
    for field in avg_scores:
        avg_scores[field] /= len(results)
        
    logging.info("="*50)
    logging.info("BENCHMARK RESULTS")
    logging.info(f"Processed {len(results)} documents.")
    logging.info("Average Similarity Scores:")
    for field, score in avg_scores.items():
        logging.info(f"  {field.capitalize()}: {score:.4f}")
    logging.info("="*50)

    # Save detailed results
    with open("benchmark_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, default=str)
    logging.info("Detailed results saved to benchmark_results.json")

if __name__ == "__main__":
    main()
