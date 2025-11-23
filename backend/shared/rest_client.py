"""
REST Client - Generic REST API client for external integrations.

Provides:
- Standardized HTTP methods (GET, POST, PUT, DELETE, PATCH)
- Automatic retry logic with exponential backoff
- Request/response logging
- Error handling
- Timeout management
"""

import logging
import requests
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import time

logger = logging.getLogger(__name__)


class RESTClient:
    """
    Generic REST API client for external integrations.
    
    Features:
    - Automatic retry with exponential backoff
    - Request/response logging
    - Timeout management
    - Error handling
    """
    
    def __init__(
        self,
        base_url: str,
        timeout: int = 30,
        max_retries: int = 3,
        backoff_factor: float = 0.5
    ):
        self.base_url = base_url
        self.timeout = timeout
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        self.session = requests.Session()
        self.request_history: List[Dict[str, Any]] = []
    
    def _get_retry_delay(self, attempt: int) -> float:
        """Calculate retry delay with exponential backoff."""
        return self.backoff_factor * (2 ** attempt)
    
    def _log_request(
        self,
        method: str,
        url: str,
        status_code: Optional[int] = None,
        duration_ms: float = 0
    ) -> None:
        """Log request details."""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "method": method,
            "url": url,
            "status_code": status_code,
            "duration_ms": duration_ms
        }
        self.request_history.append(log_entry)
        logger.info(f"REST Request: {method} {url} - {status_code} ({duration_ms}ms)")
    
    def _make_request(
        self,
        method: str,
        endpoint: str,
        headers: Optional[Dict[str, str]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> requests.Response:
        """Make HTTP request with retry logic."""
        url = f"{self.base_url}{endpoint}"
        
        for attempt in range(self.max_retries):
            try:
                start_time = datetime.utcnow()
                
                response = self.session.request(
                    method=method,
                    url=url,
                    headers=headers,
                    json=json_data,
                    params=params,
                    timeout=self.timeout
                )
                
                duration_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
                self._log_request(method, url, response.status_code, duration_ms)
                
                # Retry on 5xx errors
                if response.status_code >= 500 and attempt < self.max_retries - 1:
                    delay = self._get_retry_delay(attempt)
                    logger.warning(f"Server error {response.status_code}, retrying in {delay}s...")
                    time.sleep(delay)
                    continue
                
                return response
            
            except requests.exceptions.Timeout:
                if attempt < self.max_retries - 1:
                    delay = self._get_retry_delay(attempt)
                    logger.warning(f"Request timeout, retrying in {delay}s...")
                    time.sleep(delay)
                else:
                    raise
            
            except requests.exceptions.RequestException as e:
                if attempt < self.max_retries - 1:
                    delay = self._get_retry_delay(attempt)
                    logger.warning(f"Request error: {e}, retrying in {delay}s...")
                    time.sleep(delay)
                else:
                    raise
        
        return response
    
    def get(
        self,
        endpoint: str,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make GET request."""
        response = self._make_request("GET", endpoint, headers=headers, params=params)
        response.raise_for_status()
        return response.json()
    
    def post(
        self,
        endpoint: str,
        data: Dict[str, Any],
        headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Make POST request."""
        response = self._make_request("POST", endpoint, headers=headers, json_data=data)
        response.raise_for_status()
        return response.json()
    
    def put(
        self,
        endpoint: str,
        data: Dict[str, Any],
        headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Make PUT request."""
        response = self._make_request("PUT", endpoint, headers=headers, json_data=data)
        response.raise_for_status()
        return response.json()
    
    def patch(
        self,
        endpoint: str,
        data: Dict[str, Any],
        headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Make PATCH request."""
        response = self._make_request("PATCH", endpoint, headers=headers, json_data=data)
        response.raise_for_status()
        return response.json()
    
    def delete(
        self,
        endpoint: str,
        headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Make DELETE request."""
        response = self._make_request("DELETE", endpoint, headers=headers)
        response.raise_for_status()
        return response.json() if response.text else {}
    
    def get_request_history(self) -> List[Dict[str, Any]]:
        """Get request history."""
        return self.request_history
    
    def clear_history(self) -> None:
        """Clear request history."""
        self.request_history = []

