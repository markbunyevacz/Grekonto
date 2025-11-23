# Error Handling & Recovery - Complete Guide

**Projekt**: Grekonto AI Automatizáció  
**Verzió**: 1.0
**Utolsó frissítés**: 2025-11-23

## 🎯 Quick Start

### 1. Import Required Modules

```python
from shared.exceptions import (
    ValidationException,
    ProcessingException,
    ExternalServiceException
)
from shared.circuit_breaker import circuit_breaker_manager
from shared.error_recovery import FallbackStrategy, with_recovery
from shared.error_logger import error_logger, ErrorCategory, ErrorSeverity
```

### 2. Raise Specific Exceptions

```python
# Validation error
if not is_valid:
    raise ValidationException(
        "Invalid file format",
        {"filename": filename, "expected": "PDF"}
    )

# Processing error (recoverable)
try:
    result = ocr_client.analyze(document)
except Exception as e:
    raise ProcessingException(
        f"OCR failed: {str(e)}",
        recoverable=True
    )

# External service error
try:
    aoc_result = aoc_client.upload(document)
except Exception as e:
    raise ExternalServiceException(
        f"AOC upload failed: {str(e)}",
        service="AOC"
    )
```

### 3. Use Circuit Breaker

```python
# Register circuit breaker
breaker = circuit_breaker_manager.register(
    "aoc_service",
    failure_threshold=5,
    recovery_timeout=60
)

# Use with function calls
try:
    result = breaker.call(aoc_client.upload, document)
except CircuitBreakerException:
    logger.warning("AOC service unavailable, using fallback")
    result = {"status": "PENDING"}
```

### 4. Implement Recovery Strategies

```python
# Fallback strategy
strategies = [
    FallbackStrategy({"vendor": "Unknown", "amount": 0})
]

# Wrap function with recovery
extract_data = with_recovery(primary_ocr, strategies)
result = extract_data(document)
```

### 5. Log Errors Structurally

```python
error_logger.log_error(
    error_id="UPLOAD_VALIDATION_001",
    message="File validation failed",
    category=ErrorCategory.VALIDATION,
    severity=ErrorSeverity.ERROR,
    context={"filename": "test.pdf", "size": 5242880},
    user_id="user123",
    file_id="file456"
)

# Get error statistics
stats = error_logger.get_error_stats()
print(f"Total errors: {stats['total_errors']}")
print(f"By category: {stats['by_category']}")
```

## 🔄 Common Patterns

### Pattern 1: Validation with Fallback

```python
def validate_and_process(file_data):
    try:
        is_valid, msg = FileValidator.validate_file(file_data)
        if not is_valid:
            raise ValidationException(msg)
        return process_file(file_data)
    except ValidationException as e:
        error_logger.log_error(
            error_id="VAL_001",
            message=e.message,
            category=ErrorCategory.VALIDATION,
            severity=ErrorSeverity.ERROR
        )
        return None  # Fallback
```

### Pattern 2: External Service with Retry

```python
from shared.error_recovery import RetryStrategy

def call_external_service():
    strategies = [
        RetryStrategy(max_retries=3, backoff_factor=2.0),
        FallbackStrategy(default_response)
    ]
    
    wrapped = with_recovery(external_api_call, strategies)
    return wrapped()
```

### Pattern 3: Graceful Degradation

```python
def process_document(doc):
    try:
        # Try AI analysis
        result = ai_analyzer.analyze(doc)
    except ProcessingException as e:
        if e.recoverable:
            # Fall back to rule-based processing
            logger.warning("AI analysis failed, using rule-based processing")
            result = rule_based_analyzer.analyze(doc)
        else:
            raise
    
    return result
```

## 📊 Error Categories

| Category | Use Case | Recoverable |
|----------|----------|-------------|
| VALIDATION | File/data validation | No |
| PROCESSING | Document processing | Yes |
| EXTERNAL_SERVICE | AOC, Document Intelligence | Yes |
| STORAGE | Azure Storage | Yes |
| CONFIGURATION | Missing credentials | No |
| AUTHENTICATION | Auth failures | No |
| AUTHORIZATION | Permission denied | No |
| RATE_LIMIT | Rate limit exceeded | Yes |
| TIMEOUT | Operation timeout | Yes |

## 🚨 Error Severity Levels

| Level | Use Case | Action |
|-------|----------|--------|
| INFO | Informational | Log only |
| WARNING | Potential issue | Log + monitor |
| ERROR | Operation failed | Log + retry |
| CRITICAL | System failure | Log + alert |

## 🔍 Monitoring & Debugging

### Get Error History

```python
# All errors
history = error_logger.get_error_history()

# Filter by category
validation_errors = error_logger.get_error_history(
    category=ErrorCategory.VALIDATION
)

# Filter by severity
critical_errors = error_logger.get_error_history(
    severity=ErrorSeverity.CRITICAL
)

# Limit results
recent_10 = error_logger.get_error_history(limit=10)
```

### Get Circuit Breaker Status

```python
status = circuit_breaker_manager.get_all_status()
# Returns: {
#   "aoc_service": {
#     "state": "CLOSED",
#     "failure_count": 0,
#     "last_failure_time": None
#   }
# }
```

## 🎯 Best Practices

1. **Always use specific exceptions** - Don't catch generic Exception
2. **Include context** - Add relevant data to exception context
3. **Log with category** - Use appropriate ErrorCategory
4. **Implement recovery** - Use fallback strategies for transient failures
5. **Monitor circuit breakers** - Check status regularly
6. **Set appropriate timeouts** - Prevent hanging operations
7. **Test error paths** - Ensure recovery strategies work
8. **Document fallback behavior** - Make degradation explicit

---

## DOKUMENTÁCIÓ VERZIÓ ÉS FRISSÍTÉSI TÖRTÉNET

**Verzió:** 1.0  
**Utolsó frissítés:** 2025-11-23  
**Commit:** TBD

