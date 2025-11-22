"""
Benchmark Azure Document Intelligence on SROIE Dataset

This script tests Azure Document Intelligence's prebuilt-invoice model
on the SROIE dataset and compares results with ground truth annotations.
"""

import os
import json
import logging
from pathlib import Path
from azure.core.credentials import AzureKeyCredential
from azure.ai.formrecognizer import DocumentAnalysisClient
from typing import Dict
import time
import sys
import re
from difflib import SequenceMatcher

# Try to import dateutil, fallback to simple parsing
try:
    from dateutil import parser as date_parser
    HAS_DATEUTIL = True
except ImportError:
    HAS_DATEUTIL = False

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# ============================================================================
# SROIE Utility Functions (embedded to avoid import issues)
# ============================================================================

def normalize_text(text):
    """Normalize text based on SROIE standards."""
    if not text:
        return ""

    text = str(text)
    # Replace tabs and newlines with space
    text = re.sub(r"[\t\n]", " ", text)
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def normalize_date(date_str):
    """Normalize date to YYYY-MM-DD format."""
    if not date_str:
        return ""
    try:
        if HAS_DATEUTIL:
            dt = date_parser.parse(str(date_str), dayfirst=True)
            return dt.strftime("%Y-%m-%d")
        else:
            # Simple fallback: just normalize the string
            return str(date_str).strip()
    except:
        return str(date_str)

def normalize_amount(amount_str):
    """Normalize amount to 2 decimal places."""
    if not amount_str:
        return ""
    # Remove currency symbols and non-numeric chars except dot
    val = re.sub(r'[^\d.]', '', str(amount_str))
    try:
        return "{:.2f}".format(float(val))
    except:
        return val

def calculate_similarity(a, b, field_type="text"):
    """Calculate similarity between two strings using SequenceMatcher."""
    if field_type == "date":
        norm_a = normalize_date(a)
        norm_b = normalize_date(b)
    elif field_type == "amount":
        norm_a = normalize_amount(a)
        norm_b = normalize_amount(b)
    else:
        norm_a = normalize_text(a).lower()
        norm_b = normalize_text(b).lower()

    return SequenceMatcher(None, norm_a, norm_b).ratio()

class SROIEBenchmark:
    def __init__(self, endpoint: str, key: str, data_dir: str):
        """
        Initialize benchmark
        
        Args:
            endpoint: Azure Document Intelligence endpoint
            key: Azure Document Intelligence key
            data_dir: Path to SROIE data directory
        """
        self.client = DocumentAnalysisClient(
            endpoint=endpoint,
            credential=AzureKeyCredential(key)
        )
        self.data_dir = Path(data_dir)
        self.img_dir = self.data_dir / "img"
        self.key_dir = self.data_dir / "key"
        
        self.results = []
        self.metrics = {
            "total": 0,
            "company_correct": 0,
            "date_correct": 0,
            "total_correct": 0,
            "address_correct": 0,
            "exact_match": 0,
            "errors": 0
        }
    
    def compare_field(self, predicted: str, ground_truth: str, field_type: str = "text", threshold: float = 0.85) -> bool:
        """
        Compare predicted field with ground truth using SROIE utilities

        Args:
            predicted: Predicted value
            ground_truth: Ground truth value
            field_type: Type of field ("text", "date", "amount")
            threshold: Similarity threshold (0-1)

        Returns:
            True if match, False otherwise
        """
        if not predicted or not ground_truth:
            return False

        # Use embedded calculate_similarity function
        similarity = calculate_similarity(predicted, ground_truth, field_type)
        return similarity >= threshold
    
    def test_single_image(self, image_id: str) -> Dict:
        """
        Test a single image
        
        Args:
            image_id: Image ID (e.g., "000")
            
        Returns:
            Test result dictionary
        """
        img_path = self.img_dir / f"{image_id}.jpg"
        key_path = self.key_dir / f"{image_id}.json"
        
        if not img_path.exists() or not key_path.exists():
            logging.warning(f"Missing files for {image_id}")
            return None
        
        # Load ground truth
        with open(key_path, 'r', encoding='utf-8') as f:
            ground_truth = json.load(f)
        
        # Run Azure Document Intelligence
        try:
            with open(img_path, 'rb') as f:
                image_data = f.read()
            
            logging.info(f"Processing {image_id}...")
            poller = self.client.begin_analyze_document(
                "prebuilt-invoice",
                document=image_data
            )
            result = poller.result()
            
            # Extract fields
            predicted = {
                "company": "",
                "date": "",
                "total": "",
                "address": ""
            }
            
            if result.documents:
                invoice = result.documents[0]

                # Extract VendorName
                vendor_field = invoice.fields.get("VendorName")
                if vendor_field and vendor_field.value:
                    predicted["company"] = str(vendor_field.value)

                # Extract InvoiceDate
                date_field = invoice.fields.get("InvoiceDate")
                if date_field and date_field.value:
                    predicted["date"] = str(date_field.value)

                # Extract VendorAddress
                address_field = invoice.fields.get("VendorAddress")
                if address_field and address_field.value:
                    predicted["address"] = str(address_field.value)

                # Extract InvoiceTotal
                total_field = invoice.fields.get("InvoiceTotal")
                if total_field and total_field.value:
                    if hasattr(total_field.value, "amount"):
                        predicted["total"] = str(total_field.value.amount)
                    else:
                        predicted["total"] = str(total_field.value)
            
            # Compare with ground truth using appropriate field types
            result_dict = {
                "image_id": image_id,
                "ground_truth": ground_truth,
                "predicted": predicted,
                "matches": {
                    "company": self.compare_field(predicted["company"], ground_truth.get("company", ""), field_type="text", threshold=0.85),
                    "date": self.compare_field(predicted["date"], ground_truth.get("date", ""), field_type="date", threshold=0.95),
                    "total": self.compare_field(predicted["total"], ground_truth.get("total", ""), field_type="amount", threshold=0.95),
                    "address": self.compare_field(predicted["address"], ground_truth.get("address", ""), field_type="text", threshold=0.80)
                }
            }
            
            return result_dict
            
        except Exception as e:
            logging.error(f"Error processing {image_id}: {str(e)}")
            return {
                "image_id": image_id,
                "error": str(e)
            }

    def run_benchmark(self, sample_size: int = None, start_id: int = 0):
        """
        Run benchmark on SROIE dataset

        Args:
            sample_size: Number of images to test (None = all)
            start_id: Starting image ID
        """
        # Get all image IDs
        image_files = sorted(self.img_dir.glob("*.jpg"))
        image_ids = [f.stem for f in image_files]

        if sample_size:
            image_ids = image_ids[start_id:start_id + sample_size]

        logging.info(f"Testing {len(image_ids)} images...")
        logging.info("="*80)

        for idx, image_id in enumerate(image_ids):
            result = self.test_single_image(image_id)

            if result:
                self.results.append(result)

                # Update metrics
                self.metrics["total"] += 1

                if "error" in result:
                    self.metrics["errors"] += 1
                else:
                    matches = result["matches"]
                    if matches["company"]:
                        self.metrics["company_correct"] += 1
                    if matches["date"]:
                        self.metrics["date_correct"] += 1
                    if matches["total"]:
                        self.metrics["total_correct"] += 1
                    if matches["address"]:
                        self.metrics["address_correct"] += 1
                    if all(matches.values()):
                        self.metrics["exact_match"] += 1

                # Log progress
                if (idx + 1) % 10 == 0:
                    logging.info(f"Processed {idx + 1}/{len(image_ids)} images")

            # Rate limiting (Azure has limits)
            time.sleep(1)

        logging.info("="*80)
        logging.info("Benchmark completed!")

    def calculate_metrics(self) -> Dict:
        """Calculate final metrics"""
        total = self.metrics["total"] - self.metrics["errors"]

        if total == 0:
            return {
                "total_images": self.metrics["total"],
                "errors": self.metrics["errors"],
                "successful": 0,
                "company_accuracy": 0.0,
                "date_accuracy": 0.0,
                "total_accuracy": 0.0,
                "address_accuracy": 0.0,
                "exact_match_rate": 0.0
            }

        return {
            "total_images": self.metrics["total"],
            "errors": self.metrics["errors"],
            "successful": total,
            "company_accuracy": self.metrics["company_correct"] / total * 100,
            "date_accuracy": self.metrics["date_correct"] / total * 100,
            "total_accuracy": self.metrics["total_correct"] / total * 100,
            "address_accuracy": self.metrics["address_correct"] / total * 100,
            "exact_match_rate": self.metrics["exact_match"] / total * 100
        }

    def save_results(self, output_path: str):
        """Save results to JSON file"""
        output = {
            "metrics": self.calculate_metrics(),
            "results": self.results
        }

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)

        logging.info(f"Results saved to {output_path}")

    def print_summary(self):
        """Print summary of results"""
        metrics = self.calculate_metrics()

        print("\n" + "="*80)
        print("AZURE DOCUMENT INTELLIGENCE - SROIE BENCHMARK RESULTS")
        print("="*80)
        print(f"Total Images Tested: {metrics['total_images']}")
        print(f"Successful: {metrics['successful']}")
        print(f"Errors: {metrics['errors']}")
        print("-"*80)
        print(f"Company Name Accuracy: {metrics['company_accuracy']:.2f}%")
        print(f"Date Accuracy: {metrics['date_accuracy']:.2f}%")
        print(f"Total Amount Accuracy: {metrics['total_accuracy']:.2f}%")
        print(f"Address Accuracy: {metrics['address_accuracy']:.2f}%")
        print("-"*80)
        print(f"Exact Match Rate (all fields): {metrics['exact_match_rate']:.2f}%")
        print("="*80 + "\n")


if __name__ == "__main__":
    import sys

    # Get credentials from environment or local.settings.json
    endpoint = os.getenv("DOCUMENT_INTELLIGENCE_ENDPOINT") or os.getenv("FORM_RECOGNIZER_ENDPOINT")
    key = os.getenv("DOCUMENT_INTELLIGENCE_KEY") or os.getenv("FORM_RECOGNIZER_KEY")

    # If not in environment, try to load from backend/local.settings.json
    if not endpoint or not key:
        try:
            # Try multiple paths
            possible_paths = [
                Path("backend/local.settings.json"),
                Path("../backend/local.settings.json"),
                Path("./local.settings.json"),
            ]

            for settings_path in possible_paths:
                if settings_path.exists():
                    with open(settings_path, 'r') as f:
                        settings = json.load(f)
                        values = settings.get("Values", {})
                        endpoint = endpoint or values.get("DOCUMENT_INTELLIGENCE_ENDPOINT") or values.get("FORM_RECOGNIZER_ENDPOINT")
                        key = key or values.get("DOCUMENT_INTELLIGENCE_KEY") or values.get("FORM_RECOGNIZER_KEY")
                    if endpoint and key:
                        break
        except Exception as e:
            logging.warning(f"Could not load credentials from local.settings.json: {e}")

    if not endpoint or not key:
        print("ERROR: Azure Document Intelligence credentials not found!")
        print("Set DOCUMENT_INTELLIGENCE_ENDPOINT and DOCUMENT_INTELLIGENCE_KEY environment variables")
        print("Or configure them in backend/local.settings.json")
        sys.exit(1)

    # Initialize benchmark
    # Check both possible data locations
    data_dir = "docs/datasets/SROIE_GitHub/data"
    if not Path(data_dir).exists():
        data_dir = "benchmark/SROIE/data"

    benchmark = SROIEBenchmark(endpoint, key, data_dir)

    # Run benchmark on first 50 images (to avoid rate limits and costs)
    sample_size = int(sys.argv[1]) if len(sys.argv) > 1 else 50
    start_id = int(sys.argv[2]) if len(sys.argv) > 2 else 0

    print("\n🚀 Starting Azure Document Intelligence Benchmark on SROIE Dataset")
    print(f"📊 Testing {sample_size} images starting from ID {start_id}")
    print(f"🔗 Endpoint: {endpoint}\n")

    benchmark.run_benchmark(sample_size=sample_size, start_id=start_id)
    benchmark.print_summary()

    # Save results
    output_file = f"benchmark/results_azure_sroie_{sample_size}_{start_id}.json"
    benchmark.save_results(output_file)

