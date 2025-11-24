import re
from difflib import SequenceMatcher
from string import ascii_uppercase, digits, punctuation
from dateutil import parser

# SROIE Vocabulary from task3/src/my_data.py
VOCAB = ascii_uppercase + digits + punctuation + " \t\n"

def normalize_text(text):
    """
    Normalize text based on SROIE standards.
    - Converts to lowercase (optional, but good for comparison)
    - Removes characters not in VOCAB (if strict)
    - Replaces tabs/newlines with spaces
    - Strips whitespace
    """
    if not text:
        return ""
    
    text = str(text)
    
    # SROIE specific cleaning: replace tabs and newlines with space
    text = re.sub(r"[\t\n]", " ", text)
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

def normalize_date(date_str):
    """
    Normalize date to DD/MM/YYYY format (SROIE standard).
    Accepts various formats and converts to DD/MM/YYYY.
    """
    if not date_str:
        return ""
    try:
        # Try to parse date and return DD/MM/YYYY (SROIE format)
        dt = parser.parse(str(date_str), dayfirst=True)
        return dt.strftime("%d/%m/%Y")
    except:
        return str(date_str)

def normalize_amount(amount_str):
    """
    Normalize amount to 2 decimal places.
    Removes currency symbols.
    """
    if not amount_str:
        return ""
    # Remove currency symbols and non-numeric chars except dot
    val = re.sub(r'[^\d.]', '', str(amount_str))
    try:
        return "{:.2f}".format(float(val))
    except:
        return val

def calculate_similarity(a, b, field_type="text"):
    """
    Calculate similarity between two strings using SequenceMatcher.
    Handles dates in DD/MM/YYYY format, amounts, and text.
    """
    if field_type == "date":
        # Normalize both dates to DD/MM/YYYY format
        norm_a = normalize_date(a)
        norm_b = normalize_date(b)
    elif field_type == "amount":
        # Normalize amounts to 2 decimal places
        norm_a = normalize_amount(a)
        norm_b = normalize_amount(b)
    else:
        # Text comparison (case-insensitive)
        norm_a = normalize_text(a).lower()
        norm_b = normalize_text(b).lower()

    return SequenceMatcher(None, norm_a, norm_b).ratio()

def validate_sroie_fields(data):
    """
    Validate if the extracted data contains the required SROIE fields.
    Returns a list of missing or invalid fields.
    """
    required_fields = ["company", "date", "address", "total"]
    missing = []
    
    for field in required_fields:
        if not data.get(field):
            missing.append(field)
            
    return missing
