"""
Gemini Structured Output Extractor - PDF adatkinyerés Gemini 3 Pro Preview-val

Ez a modul a Google Gemini API structured outputs funkcióját használja
Pydantic modellekkel a PDF-ekből való strukturált adatkinyeréshez.

Támogatott mezők (SROIE kompatibilis):
- company: Szállító/Vállalat neve
- date: Számla dátuma
- address: Szállító címe
- total: Végösszeg

További mezők:
- invoice_number: Számlaszám
- items: Tételek listája (description, quantity, gross_worth)
- total_gross_worth: Teljes bruttó érték
"""

import logging
import os
import tempfile
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
from google import genai

from . import sroie_utils

logger = logging.getLogger(__name__)


class InvoiceItem(BaseModel):
    """Számla tétel."""
    description: str = Field(description="A tétel leírása")
    quantity: float = Field(description="A tétel mennyisége", default=1.0)
    gross_worth: float = Field(description="A tétel bruttó értéke", default=0.0)


class InvoiceData(BaseModel):
    """Számla strukturált adatok - SROIE kompatibilis mezőkkel."""
    company: str = Field(description="A szállító/vállalat neve")
    date: str = Field(description="A számla dátuma (DD/MM/YYYY formátumban)")
    address: str = Field(description="A szállító címe")
    total: str = Field(description="A számla végösszege")
    invoice_number: Optional[str] = Field(description="A számlaszám", default=None)
    items: List[InvoiceItem] = Field(description="A számla tételei", default_factory=list)
    total_gross_worth: Optional[float] = Field(description="Teljes bruttó érték", default=None)


class GeminiExtractor:
    """Gemini API-t használó strukturált adatkinyerő PDF-ekből."""
    
    def __init__(self, api_key: Optional[str] = None, model_id: str = "gemini-3-pro-preview"):
        """
        Inicializálja a Gemini extractort.
        
        Args:
            api_key: Google Gemini API kulcs (vagy GOOGLE_API_KEY env változó)
            model_id: A használni kívánt Gemini modell (default: gemini-3-pro-preview)
        """
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY environment variable or api_key parameter required")
        
        self.model_id = model_id
        self.client = genai.Client(api_key=self.api_key)
        logger.info(f"Gemini extractor initialized with model: {model_id}")
    
    def extract_from_invoice(self, document_content: bytes, 
                            filename: Optional[str] = None) -> Dict[str, Any]:
        """
        Kinyeri az adatokat egy számla PDF-ből Gemini structured outputs-szal.

        Args:
            document_content: A számla PDF bináris tartalma
            filename: Opcionális fájlnév (hasznos a File API-ban)

        Returns:
            Dict az extracted adatokkal (company, date, address, total, stb.)

        Raises:
            Exception: Ha a Gemini feldolgozás sikertelen
        """
        logger.info("🤖 Analyzing invoice with Gemini structured outputs")
        
        # Ideiglenes fájlba mentjük a PDF-t
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
            tmp_file.write(document_content)
            tmp_file_path = tmp_file.name
        
        try:
            # Feltöltjük a fájlt a Gemini File API-ba
            display_name = filename or "invoice"
            uploaded_file = self.client.files.upload(
                file=tmp_file_path,
                config={'display_name': display_name}
            )
            
            logger.info(f"File uploaded: {uploaded_file.name} ({uploaded_file.size_bytes} bytes)")
            
            # Token számolás (opcionális, de hasznos a költségkövetéshez)
            try:
                token_count = self.client.models.count_tokens(
                    model=self.model_id,
                    contents=uploaded_file
                )
                logger.info(f"File equals to {token_count.total_tokens} tokens")
            except Exception as e:
                logger.warning(f"Could not count tokens: {e}")
            
            # Strukturált adatkinyerés Pydantic modellel
            prompt = (
                "Extract the structured data from this invoice PDF. "
                "Ensure dates are in DD/MM/YYYY format. "
                "Ensure amounts are properly formatted with 2 decimal places. "
                "Extract all available information including invoice number, items, and totals."
            )
            
            response = self.client.models.generate_content(
                model=self.model_id,
                contents=[prompt, uploaded_file],
                config={
                    'response_mime_type': 'application/json',
                    'response_schema': InvoiceData
                }
            )
            
            # A válasz automatikusan Pydantic modelre konvertálódik
            invoice_data: InvoiceData = response.parsed
            
            # SROIE kompatibilis formátumba alakítjuk
            extracted = {
                "company": sroie_utils.normalize_text(invoice_data.company),
                "date": sroie_utils.normalize_date(invoice_data.date),
                "address": sroie_utils.normalize_text(invoice_data.address),
                "total": sroie_utils.normalize_amount(invoice_data.total),
                "confidence": self._calculate_confidence(invoice_data),
            }
            
            # További mezők hozzáadása, ha elérhetők
            if invoice_data.invoice_number:
                extracted["invoice_number"] = invoice_data.invoice_number
            
            if invoice_data.items:
                extracted["items"] = [
                    {
                        "description": item.description,
                        "quantity": item.quantity,
                        "gross_worth": item.gross_worth
                    }
                    for item in invoice_data.items
                ]
            
            if invoice_data.total_gross_worth is not None:
                extracted["total_gross_worth"] = invoice_data.total_gross_worth
            
            logger.info(f"✅ Gemini extraction successful: {extracted}")
            return extracted
            
        except Exception as e:
            logger.error(f"❌ Gemini extraction failed: {e}", exc_info=True)
            raise
        finally:
            # Töröljük az ideiglenes fájlt
            try:
                os.unlink(tmp_file_path)
            except Exception as e:
                logger.warning(f"Could not delete temp file: {e}")
    
    def _calculate_confidence(self, invoice_data: InvoiceData) -> float:
        """
        Kiszámítja az átlagos konfidencia értéket.
        
        A Gemini structured outputs garantálja a séma betartását,
        de a mezők kitöltöttsége alapján számolunk konfidenciát.
        """
        confidence = 0.5  # Base confidence
        
        # Minden kötelező mező kitöltve = magasabb konfidencia
        required_fields = ["company", "date", "address", "total"]
        filled_fields = sum(1 for field in required_fields if getattr(invoice_data, field))
        
        if filled_fields == len(required_fields):
            confidence += 0.3
        
        # További mezők = még magasabb konfidencia
        if invoice_data.invoice_number:
            confidence += 0.1
        
        if invoice_data.items:
            confidence += 0.1
        
        return min(confidence, 1.0)
    
    def extract_from_form(self, document_content: bytes,
                         form_schema: BaseModel,
                         filename: Optional[str] = None) -> Dict[str, Any]:
        """
        Általános form kinyerés tetszőleges Pydantic modellel.
        
        Args:
            document_content: A form PDF bináris tartalma
            form_schema: Pydantic BaseModel, ami definiálja a form struktúráját
            filename: Opcionális fájlnév
        
        Returns:
            Dict a kinyert adatokkal
        """
        logger.info(f"🤖 Analyzing form with Gemini structured outputs (schema: {form_schema.__name__})")
        
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
            tmp_file.write(document_content)
            tmp_file_path = tmp_file.name
        
        try:
            display_name = filename or "form"
            uploaded_file = self.client.files.upload(
                file=tmp_file_path,
                config={'display_name': display_name}
            )
            
            prompt = "Extract the structured data from this form PDF according to the specified schema."
            
            response = self.client.models.generate_content(
                model=self.model_id,
                contents=[prompt, uploaded_file],
                config={
                    'response_mime_type': 'application/json',
                    'response_schema': form_schema
                }
            )
            
            form_data = response.parsed
            
            # Pydantic modelt dict-re konvertáljuk
            if isinstance(form_data, BaseModel):
                return form_data.model_dump()
            else:
                return dict(form_data)
                
        except Exception as e:
            logger.error(f"❌ Gemini form extraction failed: {e}", exc_info=True)
            raise
        finally:
            try:
                os.unlink(tmp_file_path)
            except Exception as e:
                logger.warning(f"Could not delete temp file: {e}")
