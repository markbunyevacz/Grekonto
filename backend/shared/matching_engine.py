import logging
from thefuzz import fuzz

def find_match(extracted_data):
    """
    Matches extracted invoice data against open NAV items.
    """
    # Mock NAV Data (In reality, this comes from AOC/RLB Database)
    nav_open_items = [
        {"id": 101, "vendor": "MVM Next Zrt.", "tax_id": "12345678-2-44", "amount": 14200, "currency": "HUF", "date": "2024-11-15"},
        {"id": 102, "vendor": "Praktiker Kft.", "tax_id": "87654321-2-13", "amount": 45990, "currency": "HUF", "date": "2024-11-16"}
    ]

    vendor_tax_id = extracted_data.get("vendor_tax_id")
    amount = extracted_data.get("amount")

    # 1. Hard Match Logic
    for item in nav_open_items:
        if item["tax_id"] == vendor_tax_id and item["amount"] == amount:
            return {"status": "GREEN", "match_id": item["id"], "confidence": 100}

    # 2. Soft Match Logic (Fuzzy)
    # Example: Check if amount is close (within 5 HUF)
    for item in nav_open_items:
        if item["tax_id"] == vendor_tax_id:
            if abs(item["amount"] - (amount or 0)) <= 5:
                 return {"status": "YELLOW", "match_id": item["id"], "confidence": 90, "reason": "Amount mismatch within tolerance"}
    
    return {"status": "RED", "reason": "No matching open item found"}
