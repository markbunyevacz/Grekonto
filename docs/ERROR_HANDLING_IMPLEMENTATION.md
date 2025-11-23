# Error Handling & Recovery Implementation

**Projekt**: Grekonto AI Automatizáció
**Verzió**: 1.0
**Utolsó frissítés**: 2025-11-23
**Commit**: b93816ba

## 🎯 Overview

Comprehensive error handling and recovery system that prevents silent failures, provides user-friendly messages, and implements graceful degradation with multiple recovery strategies.

## ✅ Components Implemented

### 1. **Custom Exception Hierarchy** (`backend/shared/exceptions.py`)

Specific exception types for different failure scenarios:

```python
# Base exception with context and recovery info
GrekontException(message, error_code, context, recoverable)

# Specific exception types:
- ValidationException      # File/data validation failures
- ProcessingException      # Document processing failures
- ExternalServiceException # External service failures (AOC, Document Intelligence)
- RecoverableException     # Transient failures that can be retried
- StorageException         # Azure Storage failures
- ConfigurationException   # Configuration/environment issues
- CircuitBreakerException  # Circuit breaker is open
```

**Features:**
- ✅ Specific error codes for categorization
- ✅ Context dictionary for additional information
- ✅ Recoverable flag for retry logic
- ✅ Timestamp tracking
- ✅ Serialization to dict/JSON

### 2. **Circuit Breaker Pattern** (`backend/shared/circuit_breaker.py`)

Prevents cascading failures by monitoring service health:

```python
CircuitBreaker(
    name="service_name",
    failure_threshold=5,      # Open after 5 failures
    recovery_timeout=60,      # Try recovery after 60s
    expected_exception=Exception
)

# States: CLOSED (normal) → OPEN (failing) → HALF_OPEN (testing) → CLOSED
```

**Features:**
- ✅ Three-state pattern (CLOSED, OPEN, HALF_OPEN)
- ✅ Automatic recovery attempts
- ✅ Exponential backoff
- ✅ Status monitoring
- ✅ Global circuit breaker manager

### 3. **Error Recovery Strategies** (`backend/shared/error_recovery.py`)

Multiple recovery strategies for graceful degradation:

```python
# Fallback to default value
FallbackStrategy(fallback_value="default")

# Retry with exponential backoff
RetryStrategy(max_retries=3, backoff_factor=2.0)

# Switch to degraded mode
DegradedModeStrategy(degraded_func)

# Decorator for automatic recovery
@with_recovery(primary_func, [strategy1, strategy2])
def operation():
    pass
```

**Features:**
- ✅ Multiple recovery strategies
- ✅ Automatic strategy selection
- ✅ Exponential backoff for retries
- ✅ Degraded mode support
- ✅ Error handler callbacks

### 4. **Structured Error Logging** (`backend/shared/error_logger.py`)

Comprehensive error tracking and analysis:

```python
error_logger.log_error(
    error_id="ERR001",
    message="File validation failed",
    category=ErrorCategory.VALIDATION,
    severity=ErrorSeverity.ERROR,
    context={"filename": "test.pdf"},
    user_id="user123",
    file_id="file456"
)
```

**Features:**
- ✅ Error categorization (VALIDATION, PROCESSING, EXTERNAL_SERVICE, etc.)
- ✅ Severity levels (INFO, WARNING, ERROR, CRITICAL)
- ✅ Error history tracking
- ✅ Filtering and statistics
- ✅ Stack trace capture
- ✅ JSON serialization

## 📊 Test Results

**Total Tests**: 16  
**Passed**: 16 ✅  
**Failed**: 0  
**Success Rate**: 100%

### Test Coverage

| Component | Tests | Status |
|-----------|-------|--------|
| Custom Exceptions | 4 | ✅ |
| Circuit Breaker | 4 | ✅ |
| Error Recovery | 4 | ✅ |
| Error Logger | 4 | ✅ |

## 🔄 Integration Examples

### Example 1: File Upload with Validation

```python
from shared.exceptions import ValidationException
from shared.error_logger import error_logger, ErrorCategory, ErrorSeverity

try:
    is_valid, error_msg = FileValidator.validate_file(filename, content, mime_type)
    if not is_valid:
        raise ValidationException(error_msg, {"filename": filename})
except ValidationException as e:
    error_logger.log_error(
        error_id="UPLOAD_001",
        message=e.message,
        category=ErrorCategory.VALIDATION,
        severity=ErrorSeverity.ERROR,
        context=e.context,
        file_id=file_id
    )
    return {"error": e.message}, 400
```

### Example 2: External Service with Circuit Breaker

```python
from shared.circuit_breaker import circuit_breaker_manager

breaker = circuit_breaker_manager.register(
    "aoc_service",
    failure_threshold=5,
    recovery_timeout=60
)

try:
    result = breaker.call(aoc_client.upload_document, match_result, blob_data)
except CircuitBreakerException:
    # Service unavailable, use fallback
    return {"status": "PENDING", "message": "AOC service temporarily unavailable"}
```

### Example 3: Graceful Degradation

```python
from shared.error_recovery import FallbackStrategy, with_recovery

def primary_ocr():
    return document_intelligence_client.analyze(blob_data)

def fallback_ocr():
    return {"vendor": "Unknown", "amount": 0}  # Rule-based fallback

strategies = [FallbackStrategy(fallback_ocr())]
extract_data = with_recovery(primary_ocr, strategies)()
```

## 🚀 Production Deployment

### Configuration

Set environment variables:
```bash
ERROR_LOG_LEVEL=INFO
CIRCUIT_BREAKER_THRESHOLD=5
CIRCUIT_BREAKER_TIMEOUT=60
MAX_RETRIES=3
RETRY_BACKOFF_FACTOR=2.0
```

### Monitoring

Access error statistics:
```python
stats = error_logger.get_error_stats()
# Returns: {
#   "total_errors": 42,
#   "by_category": {"VALIDATION": 10, "PROCESSING": 32},
#   "by_severity": {"ERROR": 35, "WARNING": 7},
#   "recent_errors": [...]
# }
```

## 📋 Files Created

- `backend/shared/exceptions.py` - Custom exception hierarchy
- `backend/shared/circuit_breaker.py` - Circuit breaker pattern
- `backend/shared/error_recovery.py` - Recovery strategies
- `backend/shared/error_logger.py` - Structured error logging
- `backend/tests/test_error_handling.py` - Comprehensive tests

---

## DOKUMENTÁCIÓ VERZIÓ ÉS FRISSÍTÉSI TÖRTÉNET

**Verzió:** 1.0  
**Utolsó frissítés:** 2025-11-23  
**Commit:** TBD

