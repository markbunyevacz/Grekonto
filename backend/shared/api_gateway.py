"""
API Gateway - Clean RESTful API design with FastAPI and proper HTTP status codes.

Provides a unified interface for all external integrations with standardized
request/response formats and comprehensive error handling.
"""

import logging
from typing import Dict, Any, Optional, List
from enum import Enum
from datetime import datetime
import json

logger = logging.getLogger(__name__)


class HTTPStatusCode(Enum):
    """HTTP Status Codes."""
    OK = 200
    CREATED = 201
    ACCEPTED = 202
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    CONFLICT = 409
    UNPROCESSABLE_ENTITY = 422
    RATE_LIMITED = 429
    INTERNAL_ERROR = 500
    SERVICE_UNAVAILABLE = 503


class APIResponse:
    """Standardized API response format."""
    
    def __init__(
        self,
        status_code: int,
        data: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None,
        message: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.status_code = status_code
        self.data = data or {}
        self.error = error
        self.message = message
        self.metadata = metadata or {}
        self.timestamp = datetime.utcnow().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        response = {
            "status_code": self.status_code,
            "timestamp": self.timestamp,
            "success": 200 <= self.status_code < 300
        }
        
        if self.message:
            response["message"] = self.message
        
        if self.data:
            response["data"] = self.data
        
        if self.error:
            response["error"] = self.error
        
        if self.metadata:
            response["metadata"] = self.metadata
        
        return response
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict())


class APIGateway:
    """
    Unified API Gateway for all external integrations.
    
    Provides:
    - Standardized request/response formats
    - Proper HTTP status codes
    - Error handling and logging
    - Rate limiting support
    - Request validation
    """
    
    def __init__(self):
        self.integrations: Dict[str, Any] = {}
        self.request_log: List[Dict[str, Any]] = []
    
    def register_integration(self, name: str, client: Any) -> None:
        """Register an external integration client."""
        self.integrations[name] = client
        logger.info(f"Registered integration: {name}")
    
    def get_integration(self, name: str) -> Optional[Any]:
        """Get registered integration client."""
        return self.integrations.get(name)
    
    def success_response(
        self,
        data: Dict[str, Any],
        status_code: int = 200,
        message: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> APIResponse:
        """Create a success response."""
        return APIResponse(
            status_code=status_code,
            data=data,
            message=message or "Request successful",
            metadata=metadata
        )
    
    def error_response(
        self,
        error: str,
        status_code: int = 400,
        message: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> APIResponse:
        """Create an error response."""
        return APIResponse(
            status_code=status_code,
            error=error,
            message=message or "Request failed",
            metadata=metadata
        )
    
    def created_response(
        self,
        data: Dict[str, Any],
        message: Optional[str] = None
    ) -> APIResponse:
        """Create a 201 Created response."""
        return APIResponse(
            status_code=201,
            data=data,
            message=message or "Resource created successfully"
        )
    
    def accepted_response(
        self,
        data: Dict[str, Any],
        message: Optional[str] = None
    ) -> APIResponse:
        """Create a 202 Accepted response."""
        return APIResponse(
            status_code=202,
            data=data,
            message=message or "Request accepted for processing"
        )
    
    def not_found_response(
        self,
        resource: str,
        identifier: str
    ) -> APIResponse:
        """Create a 404 Not Found response."""
        return APIResponse(
            status_code=404,
            error=f"{resource} not found",
            message=f"Could not find {resource} with identifier: {identifier}"
        )
    
    def conflict_response(
        self,
        message: str
    ) -> APIResponse:
        """Create a 409 Conflict response."""
        return APIResponse(
            status_code=409,
            error="Conflict",
            message=message
        )
    
    def rate_limited_response(
        self,
        retry_after: int
    ) -> APIResponse:
        """Create a 429 Rate Limited response."""
        return APIResponse(
            status_code=429,
            error="Rate limit exceeded",
            message=f"Please retry after {retry_after} seconds",
            metadata={"retry_after": retry_after}
        )
    
    def internal_error_response(
        self,
        error: str,
        request_id: Optional[str] = None
    ) -> APIResponse:
        """Create a 500 Internal Server Error response."""
        metadata = {}
        if request_id:
            metadata["request_id"] = request_id
        
        return APIResponse(
            status_code=500,
            error="Internal server error",
            message=error,
            metadata=metadata
        )
    
    def service_unavailable_response(
        self,
        service: str
    ) -> APIResponse:
        """Create a 503 Service Unavailable response."""
        return APIResponse(
            status_code=503,
            error="Service unavailable",
            message=f"{service} is currently unavailable"
        )
    
    def log_request(
        self,
        method: str,
        endpoint: str,
        status_code: int,
        duration_ms: float,
        user_id: Optional[str] = None
    ) -> None:
        """Log API request."""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "method": method,
            "endpoint": endpoint,
            "status_code": status_code,
            "duration_ms": duration_ms,
            "user_id": user_id
        }
        self.request_log.append(log_entry)
        logger.info(f"API Request: {method} {endpoint} - {status_code} ({duration_ms}ms)")


# Global gateway instance
_gateway: Optional[APIGateway] = None


def get_gateway() -> APIGateway:
    """Get or create the global API gateway instance."""
    global _gateway
    if _gateway is None:
        _gateway = APIGateway()
    return _gateway

