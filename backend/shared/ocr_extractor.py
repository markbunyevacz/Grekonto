"""
OCR Extractor - Finomhangolt adatkinyerés az SROIE módszertana alapján

Támogatott mezők:
- company: Szállító/Vállalat neve
- date: Számla dátuma
- address: Szállító címe
- total: Végösszeg
"""

import logging
from typing import Dict, Any, Optional
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential
from . import sroie_utils

logger = logging.getLogger(__name__)

class OCRExtractor:
    """OCR adatkinyerés Azure Document Intelligence-szel."""
    
    def __init__(self, endpoint: str, key: str):
        self.client = DocumentAnalysisClient(endpoint=endpoint, credential=AzureKeyCredential(key))
    
    def extract_from_invoice(self, document_content: bytes) -> Dict[str, Any]:
        """
        Kinyeri az adatokat egy számla képből - VALÓDI AZURE FELDOLGOZÁS.

        Args:
            document_content: A számla képének bináris tartalma

        Returns:
            Dict az extracted adatokkal (company, date, address, total)

        Raises:
            Exception: Ha az Azure feldolgozás sikertelen
        """
        logger.info("🤖 Analyzing invoice with Azure Document Intelligence")
        poller = self.client.begin_analyze_document("prebuilt-invoice", document_content)
        result = poller.result()

        if not result.documents:
            raise ValueError("No documents found in analysis result")

        doc = result.documents[0]
        fields = doc.fields

        # Kinyerjük az adatokat
        extracted = {
            "company": self._extract_vendor(fields),
            "date": self._extract_date(fields),
            "address": self._extract_address(fields),
            "total": self._extract_total(fields),
            "confidence": self._calculate_confidence(fields)
        }

        logger.info(f"✅ Extraction successful: {extracted}")
        return extracted
    
    def _extract_vendor(self, fields: Dict) -> str:
        """Kinyeri a szállító nevét."""
        # Próbáljuk az invoice modellt
        if "VendorName" in fields and fields["VendorName"].value:
            return sroie_utils.normalize_text(fields["VendorName"].value)
        
        # Fallback: receipt modell
        if "MerchantName" in fields and fields["MerchantName"].value:
            return sroie_utils.normalize_text(fields["MerchantName"].value)
        
        return ""
    
    def _extract_date(self, fields: Dict) -> str:
        """Kinyeri a számla dátumát."""
        if "InvoiceDate" in fields and fields["InvoiceDate"].value:
            return sroie_utils.normalize_date(fields["InvoiceDate"].value)
        
        if "TransactionDate" in fields and fields["TransactionDate"].value:
            return sroie_utils.normalize_date(fields["TransactionDate"].value)
        
        return ""
    
    def _extract_address(self, fields: Dict) -> str:
        """Kinyeri a szállító címét."""
        if "VendorAddress" in fields and fields["VendorAddress"].value:
            addr_val = fields["VendorAddress"].value
            # AddressValue objektum kezelése
            if hasattr(addr_val, 'street_address'):
                # AddressValue objektum - összeállítjuk a szöveget
                address_parts = []
                if addr_val.street_address:
                    address_parts.append(addr_val.street_address)
                if addr_val.city:
                    address_parts.append(addr_val.city)
                if addr_val.state:
                    address_parts.append(addr_val.state)
                if addr_val.postal_code:
                    address_parts.append(addr_val.postal_code)
                return sroie_utils.normalize_text(", ".join(address_parts))
            else:
                # Szöveges cím
                return sroie_utils.normalize_text(str(addr_val))

        return ""
    
    def _extract_total(self, fields: Dict) -> str:
        """Kinyeri a végösszeget."""
        if "InvoiceTotal" in fields and fields["InvoiceTotal"].value:
            total = fields["InvoiceTotal"].value
            if hasattr(total, 'amount'):
                return sroie_utils.normalize_amount(total.amount)
            return sroie_utils.normalize_amount(total)
        
        if "Total" in fields and fields["Total"].value:
            total = fields["Total"].value
            if hasattr(total, 'amount'):
                return sroie_utils.normalize_amount(total.amount)
            return sroie_utils.normalize_amount(total)
        
        return ""
    
    def _calculate_confidence(self, fields: Dict) -> float:
        """Kiszámítja az átlagos konfidencia értéket."""
        confidences = []
        for field_name in ["VendorName", "InvoiceDate", "InvoiceTotal"]:
            if field_name in fields and fields[field_name].confidence:
                confidences.append(fields[field_name].confidence)
        
        return sum(confidences) / len(confidences) if confidences else 0.0
    


