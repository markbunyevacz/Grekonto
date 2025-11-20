import os
import requests
import logging
from typing import List, Dict, Optional, Any
from . import key_vault_client

class AOCClient:
    def __init__(self):
        self.base_url = os.environ.get("AOC_API_BASE_URL", "https://api.aoc-accounting.com/v1")
        self.api_key_secret_name = os.environ.get("AOC_API_KEY_SECRET_NAME", "aoc-api-key")
        self._api_key = None

    def _get_api_key(self) -> str:
        if not self._api_key:
            self._api_key = key_vault_client.get_secret(self.api_key_secret_name)
        return self._api_key

    def _get_headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self._get_api_key()}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

    def get_open_items(self) -> List[Dict[str, Any]]:
        """
        Fetches open items (NAV data) from the AOC/RLB system.
        """
        url = f"{self.base_url}/open-items"
        try:
            response = requests.get(url, headers=self._get_headers())
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logging.error(f"Error fetching open items from AOC: {str(e)}")
            # Fallback to empty list or raise depending on requirements. 
            # For now, returning empty list to prevent crash, but logging error.
            return []

    def upload_invoice_link(self, invoice_id: str, document_url: str) -> bool:
        """
        Links a processed document URL to an existing invoice record in AOC.
        """
        url = f"{self.base_url}/invoices/{invoice_id}/link-document"
        payload = {"document_url": document_url}
        try:
            response = requests.post(url, json=payload, headers=self._get_headers())
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException as e:
            logging.error(f"Error linking document to invoice {invoice_id}: {str(e)}")
            return False

    def create_pending_invoice(self, extracted_data: Dict[str, Any], document_url: str) -> Optional[str]:
        """
        Creates a new pending invoice record if no match is found.
        Returns the new invoice ID.
        """
        url = f"{self.base_url}/invoices/pending"
        payload = {
            "extracted_data": extracted_data,
            "document_url": document_url
        }
        try:
            response = requests.post(url, json=payload, headers=self._get_headers())
            response.raise_for_status()
            return response.json().get("id")
        except requests.exceptions.RequestException as e:
            logging.error(f"Error creating pending invoice: {str(e)}")
            return None
