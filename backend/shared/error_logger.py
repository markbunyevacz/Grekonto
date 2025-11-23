"""
Structured error logging for comprehensive error tracking and analysis.

Provides detailed error context, categorization, and audit trail for debugging
and compliance purposes.
"""

import logging
import json
import traceback
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class ErrorSeverity(Enum):
    """Error severity levels."""
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class ErrorCategory(Enum):
    """Error categories for classification."""
    VALIDATION = "VALIDATION"
    PROCESSING = "PROCESSING"
    EXTERNAL_SERVICE = "EXTERNAL_SERVICE"
    STORAGE = "STORAGE"
    CONFIGURATION = "CONFIGURATION"
    AUTHENTICATION = "AUTHENTICATION"
    AUTHORIZATION = "AUTHORIZATION"
    RATE_LIMIT = "RATE_LIMIT"
    TIMEOUT = "TIMEOUT"
    UNKNOWN = "UNKNOWN"


class ErrorLog:
    """Structured error log entry."""
    
    def __init__(
        self,
        error_id: str,
        message: str,
        category: ErrorCategory,
        severity: ErrorSeverity,
        context: Optional[Dict[str, Any]] = None,
        exception: Optional[Exception] = None,
        user_id: Optional[str] = None,
        file_id: Optional[str] = None
    ):
        self.error_id = error_id
        self.message = message
        self.category = category
        self.severity = severity
        self.context = context or {}
        self.exception = exception
        self.user_id = user_id
        self.file_id = file_id
        self.timestamp = datetime.utcnow().isoformat()
        self.stack_trace = None
        
        if exception:
            self.stack_trace = traceback.format_exc()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for logging."""
        return {
            "error_id": self.error_id,
            "timestamp": self.timestamp,
            "message": self.message,
            "category": self.category.value,
            "severity": self.severity.value,
            "context": self.context,
            "user_id": self.user_id,
            "file_id": self.file_id,
            "stack_trace": self.stack_trace
        }
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), default=str)


class ErrorLogger:
    """Structured error logging."""
    
    def __init__(self):
        self.error_history = []
        self.max_history = 1000
    
    def log_error(
        self,
        error_id: str,
        message: str,
        category: ErrorCategory,
        severity: ErrorSeverity,
        context: Optional[Dict] = None,
        exception: Optional[Exception] = None,
        user_id: Optional[str] = None,
        file_id: Optional[str] = None
    ) -> ErrorLog:
        """Log structured error."""
        error_log = ErrorLog(
            error_id=error_id,
            message=message,
            category=category,
            severity=severity,
            context=context,
            exception=exception,
            user_id=user_id,
            file_id=file_id
        )
        
        # Store in history
        self.error_history.append(error_log)
        if len(self.error_history) > self.max_history:
            self.error_history.pop(0)
        
        # Log based on severity
        log_message = f"[{error_log.category.value}] {message}"
        
        if severity == ErrorSeverity.CRITICAL:
            logger.critical(log_message, extra={"error_log": error_log.to_dict()})
        elif severity == ErrorSeverity.ERROR:
            logger.error(log_message, extra={"error_log": error_log.to_dict()})
        elif severity == ErrorSeverity.WARNING:
            logger.warning(log_message, extra={"error_log": error_log.to_dict()})
        else:
            logger.info(log_message, extra={"error_log": error_log.to_dict()})
        
        return error_log
    
    def get_error_history(
        self,
        category: Optional[ErrorCategory] = None,
        severity: Optional[ErrorSeverity] = None,
        limit: int = 100
    ) -> list:
        """Get error history with optional filtering."""
        history = self.error_history
        
        if category:
            history = [e for e in history if e.category == category]
        
        if severity:
            history = [e for e in history if e.severity == severity]
        
        return history[-limit:]
    
    def get_error_stats(self) -> Dict[str, Any]:
        """Get error statistics."""
        if not self.error_history:
            return {"total_errors": 0}
        
        stats = {
            "total_errors": len(self.error_history),
            "by_category": {},
            "by_severity": {},
            "recent_errors": [e.to_dict() for e in self.error_history[-10:]]
        }
        
        for error in self.error_history:
            cat = error.category.value
            sev = error.severity.value
            
            stats["by_category"][cat] = stats["by_category"].get(cat, 0) + 1
            stats["by_severity"][sev] = stats["by_severity"].get(sev, 0) + 1
        
        return stats


# Global error logger
error_logger = ErrorLogger()

