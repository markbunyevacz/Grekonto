#!/usr/bin/env python3
"""
OCR Extractor Integráció Teszt - Az OCRExtractor osztály tesztelése az első 3 SROIE képpel.
"""

import os
import json
from pathlib import Path
from shared.ocr_extractor import OCRExtractor
from shared import sroie_utils

# Azure credentials
ENDPOINT = os.getenv("DOCUMENT_INTELLIGENCE_ENDPOINT") or os.getenv("FORM_RECOGNIZER_ENDPOINT")
KEY = os.getenv("DOCUMENT_INTELLIGENCE_KEY") or os.getenv("FORM_RECOGNIZER_KEY")

# Ha nincs environment variable, próbáljuk a local.settings.json-ből
if not ENDPOINT or not KEY:
    try:
        settings_path = Path(__file__).parent / "local.settings.json"
        with open(settings_path, 'r') as f:
            settings = json.load(f)
            ENDPOINT = settings.get("Values", {}).get("DOCUMENT_INTELLIGENCE_ENDPOINT")
            KEY = settings.get("Values", {}).get("DOCUMENT_INTELLIGENCE_KEY")
    except:
        pass

if not ENDPOINT or not KEY:
    raise ValueError("Azure Document Intelligence credentials REQUIRED!")

# SROIE adatok
DATA_DIR = Path(__file__).parent / "external" / "ICDAR-2019-SROIE" / "data"
IMG_DIR = DATA_DIR / "img"
KEY_DIR = DATA_DIR / "key"

def load_ground_truth(image_num):
    """Betölti a ground truth adatokat a JSON fájlból."""
    json_path = KEY_DIR / f"{image_num:03d}.json"
    with open(json_path, 'r') as f:
        return json.load(f)

def test_extractor():
    """Teszteli az OCRExtractor-t az első 3 képpel."""
    extractor = OCRExtractor(ENDPOINT, KEY)
    
    print("\n🔍 OCR EXTRACTOR INTEGRÁCIÓ TESZT")
    print("=" * 80)
    
    for i in range(3):
        image_path = IMG_DIR / f"{i:03d}.jpg"
        ground_truth = load_ground_truth(i)
        
        print(f"\n[{i+1}/3] Feldolgozás: {image_path.name}")
        
        # Feldolgozás
        with open(image_path, 'rb') as f:
            extracted = extractor.extract_from_invoice(f.read())
        
        # Összehasonlítás
        print(f"  Ground Truth:")
        for key in ["company", "date", "address", "total"]:
            print(f"    {key:12} = {ground_truth.get(key, '')}")
        
        print(f"  Extracted:")
        for key in ["company", "date", "address", "total"]:
            print(f"    {key:12} = {extracted.get(key, '')}")
        
        print(f"  Pontosság:")
        for key in ["company", "date", "address", "total"]:
            similarity = sroie_utils.calculate_similarity(
                ground_truth.get(key, ""),
                extracted.get(key, ""),
                field_type="date" if key == "date" else "amount" if key == "total" else "text"
            )
            pct = similarity * 100
            status = "✅" if pct >= 90 else "⚠️" if pct >= 70 else "❌"
            print(f"    {key:12} = {pct:6.2f}% {status}")

if __name__ == "__main__":
    test_extractor()

