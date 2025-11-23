"""
Custom exception hierarchy for Grekonto error handling.

Provides specific exception types for different failure scenarios,
enabling targeted error handling and graceful degradation.
"""

import logging
from typing import Optional, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class GrekontException(Exception):
    """Base exception for all Grekonto errors."""
    
    def __init__(
        self,
        message: str,
        error_code: str = "UNKNOWN_ERROR",
        context: Optional[Dict[str, Any]] = None,
        recoverable: bool = False
    ):
        self.message = message
        self.error_code = error_code
        self.context = context or {}
        self.recoverable = recoverable
        self.timestamp = datetime.utcnow().isoformat()
        super().__init__(self.message)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for logging/response."""
        return {
            "error_code": self.error_code,
            "message": self.message,
            "context": self.context,
            "recoverable": self.recoverable,
            "timestamp": self.timestamp
        }


class ValidationException(GrekontException):
    """File/data validation failures."""
    
    def __init__(self, message: str, context: Optional[Dict] = None):
        super().__init__(
            message=message,
            error_code="VALIDATION_ERROR",
            context=context,
            recoverable=False
        )


class ProcessingException(GrekontException):
    """Document processing failures."""
    
    def __init__(self, message: str, context: Optional[Dict] = None, recoverable: bool = False):
        super().__init__(
            message=message,
            error_code="PROCESSING_ERROR",
            context=context,
            recoverable=recoverable
        )


class ExternalServiceException(GrekontException):
    """External service failures (AOC, Document Intelligence, etc.)."""
    
    def __init__(self, message: str, service: str = "", context: Optional[Dict] = None):
        context = context or {}
        context["service"] = service
        super().__init__(
            message=message,
            error_code=f"SERVICE_ERROR_{service.upper()}",
            context=context,
            recoverable=True
        )


class RecoverableException(GrekontException):
    """Transient failures that can be retried."""
    
    def __init__(self, message: str, context: Optional[Dict] = None, retry_count: int = 0):
        context = context or {}
        context["retry_count"] = retry_count
        super().__init__(
            message=message,
            error_code="RECOVERABLE_ERROR",
            context=context,
            recoverable=True
        )


class StorageException(GrekontException):
    """Azure Storage failures."""
    
    def __init__(self, message: str, context: Optional[Dict] = None):
        super().__init__(
            message=message,
            error_code="STORAGE_ERROR",
            context=context,
            recoverable=True
        )


class ConfigurationException(GrekontException):
    """Configuration/environment issues."""
    
    def __init__(self, message: str, context: Optional[Dict] = None):
        super().__init__(
            message=message,
            error_code="CONFIG_ERROR",
            context=context,
            recoverable=False
        )


class CircuitBreakerException(GrekontException):
    """Circuit breaker is open - service unavailable."""
    
    def __init__(self, service: str, context: Optional[Dict] = None):
        context = context or {}
        context["service"] = service
        super().__init__(
            message=f"Circuit breaker open for {service}. Service temporarily unavailable.",
            error_code="CIRCUIT_BREAKER_OPEN",
            context=context,
            recoverable=True
        )

