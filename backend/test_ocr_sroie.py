#!/usr/bin/env python3
"""
OCR Finomhangolási Teszt az SROIE Adatok Alapján - VALÓDI AZURE FELDOLGOZÁS

Módszertan:
- Scannelt számla: 000.jpg-tül indulva
- Adattartalom: 000.csv-tól indulva (szövegdobozok koordinátái)
- Ellenőrző JSON kulcsok: 000.json-tól indulva (company, date, address, total)

Tesztelés:
1. Betöltjük az SROIE tesztadatokat (625 számla)
2. Feldolgozzuk az Azure Document Intelligence-szel
3. Összehasonlítjuk az eredményt a ground truth adatokkal
4. Kiszámítjuk a pontosságot
"""

import os
import json
import glob
import logging
from pathlib import Path
from difflib import SequenceMatcher
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

# SROIE adatok elérési útja
SROIE_DATA_DIR = Path(__file__).parent / "external" / "ICDAR-2019-SROIE" / "data"
SROIE_IMG_DIR = SROIE_DATA_DIR / "img"
SROIE_KEY_DIR = SROIE_DATA_DIR / "key"

# Azure Document Intelligence credentials
def load_credentials():
    """Betölti az Azure credentials-eket a local.settings.json-ből."""
    endpoint = os.getenv("DOCUMENT_INTELLIGENCE_ENDPOINT") or os.getenv("FORM_RECOGNIZER_ENDPOINT")
    key = os.getenv("DOCUMENT_INTELLIGENCE_KEY") or os.getenv("FORM_RECOGNIZER_KEY")

    # Ha nincs environment variable, próbáljuk a local.settings.json-ből
    if not endpoint or not key:
        try:
            settings_path = Path(__file__).parent / "local.settings.json"
            with open(settings_path, 'r') as f:
                settings = json.load(f)
                endpoint = settings.get("Values", {}).get("DOCUMENT_INTELLIGENCE_ENDPOINT")
                key = settings.get("Values", {}).get("DOCUMENT_INTELLIGENCE_KEY")
        except:
            pass

    return endpoint, key

ENDPOINT, KEY = load_credentials()

def normalize_text(text):
    """Normalizálja a szöveget az összehasonlításhoz."""
    if not text:
        return ""
    return str(text).strip().lower()

def calculate_similarity(predicted, ground_truth):
    """Kiszámítja a hasonlóságot két szöveg között (0-1)."""
    pred = normalize_text(predicted)
    truth = normalize_text(ground_truth)
    return SequenceMatcher(None, pred, truth).ratio()

def load_ground_truth(json_file):
    """Betölti a ground truth adatokat a JSON fájlból."""
    try:
        with open(json_file, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading {json_file}: {e}")
        return {}

def process_image_with_azure(image_path):
    """Feldolgozza a képet az Azure Document Intelligence-szel - VALÓDI FELDOLGOZÁS."""
    with open(image_path, 'rb') as f:
        client = DocumentAnalysisClient(endpoint=ENDPOINT, credential=AzureKeyCredential(KEY))
        poller = client.begin_analyze_document("prebuilt-invoice", document=f)
        result = poller.result()

    if not result.documents:
        raise ValueError(f"No documents found in {image_path}")

    doc = result.documents[0]
    fields = doc.fields

    # DocumentField objektumok értékei - kezelni kell az AddressValue objektumokat
    company = fields.get("VendorName").value if fields.get("VendorName") else ""

    # Date normalizálása
    date_val = fields.get("InvoiceDate").value if fields.get("InvoiceDate") else ""
    if date_val:
        # Azure dátum formátuma: datetime.date, konvertálás DD/MM/YYYY-re
        date_str = str(date_val)  # YYYY-MM-DD
        if len(date_str) == 10:  # YYYY-MM-DD
            parts = date_str.split('-')
            date_val = f"{parts[2]}/{parts[1]}/{parts[0]}"  # DD/MM/YYYY

    # Address kezelése - AddressValue objektum
    address_val = fields.get("VendorAddress")
    if address_val:
        addr_obj = address_val.value
        # AddressValue objektumból szöveg összeállítása
        address_parts = []
        if hasattr(addr_obj, 'street_address') and addr_obj.street_address:
            address_parts.append(addr_obj.street_address)
        if hasattr(addr_obj, 'city') and addr_obj.city:
            address_parts.append(addr_obj.city)
        if hasattr(addr_obj, 'state') and addr_obj.state:
            address_parts.append(addr_obj.state)
        if hasattr(addr_obj, 'postal_code') and addr_obj.postal_code:
            address_parts.append(addr_obj.postal_code)
        address_val = ", ".join(address_parts)
    else:
        address_val = ""

    total = str(fields.get("InvoiceTotal").value) if fields.get("InvoiceTotal") else ""

    extracted = {
        "company": company,
        "date": date_val,
        "total": total,
        "address": address_val
    }

    return extracted

def run_test(limit=10):
    """Futtatja a tesztet az SROIE adatokon - VALÓDI AZURE FELDOLGOZÁS."""
    if not ENDPOINT or not KEY:
        logger.error("❌ Azure Document Intelligence credentials REQUIRED!")
        logger.error("   Set DOCUMENT_INTELLIGENCE_ENDPOINT and DOCUMENT_INTELLIGENCE_KEY")
        return
    
    logger.info("🔍 SROIE OCR Finomhangolási Teszt - VALÓDI AZURE FELDOLGOZÁS")
    logger.info(f"📁 Adatok: {SROIE_DATA_DIR}\n")
    
    # Betöltjük az összes képet
    image_files = sorted(glob.glob(str(SROIE_IMG_DIR / "*.jpg")))
    if limit:
        image_files = image_files[:limit]
    
    logger.info(f"📊 Feldolgozandó képek: {len(image_files)}\n")
    
    results = []
    for idx, img_path in enumerate(image_files):
        filename = Path(img_path).stem
        json_path = SROIE_KEY_DIR / f"{filename}.json"
        
        # Betöltjük a ground truth adatokat
        ground_truth = load_ground_truth(json_path)
        if not ground_truth:
            continue
        
        # Feldolgozzuk a képet - VALÓDI AZURE
        logger.info(f"[{idx+1}/{len(image_files)}] Feldolgozás: {filename}.jpg")
        try:
            extracted = process_image_with_azure(img_path)
        except Exception as e:
            logger.error(f"  ❌ Error: {e}")
            continue
        
        # Összehasonlítjuk az eredményt
        scores = {}
        for field in ["company", "date", "address", "total"]:
            gt_val = ground_truth.get(field, "")
            ex_val = extracted.get(field, "")
            score = calculate_similarity(ex_val, gt_val)
            scores[field] = score
        
        results.append({
            "file": filename,
            "scores": scores,
            "ground_truth": ground_truth,
            "extracted": extracted
        })
    
    # Részletes kimenetek
    logger.info(f"\n{'='*100}")
    logger.info("📋 RÉSZLETES EREDMÉNYEK")
    logger.info(f"{'='*100}\n")

    for idx, result in enumerate(results):
        logger.info(f"[{idx+1}] {result['file']}.jpg")
        logger.info("  Ground Truth (JSON):")
        for field, value in result['ground_truth'].items():
            logger.info(f"    {field:12} = {value}")

        logger.info("  Extracted (OCR):")
        for field, value in result['extracted'].items():
            logger.info(f"    {field:12} = {value}")

        logger.info("  Pontosság:")
        for field, score in result['scores'].items():
            status = "✅" if score >= 0.85 else "⚠️ " if score >= 0.70 else "❌"
            logger.info(f"    {field:12} = {score:.2%} {status}")
        logger.info("")

    # Statisztikák
    if results:
        avg_scores = {field: 0 for field in ["company", "date", "address", "total"]}
        for result in results:
            for field in avg_scores:
                avg_scores[field] += result["scores"][field]

        for field in avg_scores:
            avg_scores[field] /= len(results)

        logger.info(f"{'='*100}")
        logger.info("📈 ÁTLAGOS PONTOSSÁG")
        logger.info(f"{'='*100}")
        for field, score in avg_scores.items():
            status = "✅" if score >= 0.85 else "⚠️ " if score >= 0.70 else "❌"
            logger.info(f"  {field:12} = {score:.2%} {status}")

if __name__ == "__main__":
    run_test(limit=625)  # Tesztelés az összes 625 képpel - VALÓDI AZURE FELDOLGOZÁS

