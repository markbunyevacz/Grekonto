import logging
from thefuzz import fuzz
from .aoc_client import AOCClient
from . import table_service

def find_match(extracted_data):
    """
    Matches extracted invoice data against open NAV items.
    """
    vendor_tax_id = extracted_data.get("vendor_tax_id")
    invoice_id = extracted_data.get("invoice_id")
    amount = extracted_data.get("amount")

    # 0. Duplicate Detection (FR-09)
    if table_service.check_duplicate_invoice(vendor_tax_id, invoice_id):
        return {"status": "RED", "reason": "Duplicate invoice detected"}

    # Fetch real NAV Data from AOC/RLB Database
    aoc_client = AOCClient()
    nav_open_items = aoc_client.get_open_items()
    
    if not nav_open_items:
        logging.warning("No open items retrieved from AOC. Proceeding with empty list.")
        nav_open_items = []

    # 1. Hard Match Logic
    for item in nav_open_items:
        # Check for exact match on tax_id and amount
        # Also check invoice_id if available in item for stricter hard match, 
        # but requirement emphasizes amount and tax_id usually.
        # However, if we have invoice_id, we should probably use it for hard match too if it matches exactly.
        if item.get("tax_id") == vendor_tax_id and item.get("amount") == amount:
             # If invoice IDs are present and mismatch, it might not be a hard match?
             # For now keeping existing logic but adding invoice_id check if it helps?
             # The existing code was: if item["tax_id"] == vendor_tax_id and item["amount"] == amount:
             # I will keep it but maybe verify invoice_id if it exists?
             # Let's stick to the existing hard match logic but ensure keys exist.
             return {"status": "GREEN", "match_id": item["id"], "confidence": 100}

    # 2. Soft Match Logic (Fuzzy)
    for item in nav_open_items:
        if item.get("tax_id") == vendor_tax_id:
            # Check if amount is close (within 5 HUF)
            if abs(item.get("amount", 0) - (amount or 0)) <= 5:
                 return {"status": "YELLOW", "match_id": item["id"], "confidence": 90, "reason": "Amount mismatch within tolerance"}
            
            # Fuzzy match on Invoice Number (sorszám)
            nav_invoice_id = str(item.get("invoice_id", ""))
            extracted_invoice_id = str(invoice_id or "")
            
            if nav_invoice_id and extracted_invoice_id:
                ratio = fuzz.ratio(nav_invoice_id.lower(), extracted_invoice_id.lower())
                if ratio >= 80: # Threshold for soft match
                    return {"status": "YELLOW", "match_id": item["id"], "confidence": ratio, "reason": f"Fuzzy match on invoice number ({ratio}%)"}
    
    return {"status": "RED", "reason": "No matching open item found"}
