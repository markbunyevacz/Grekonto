# Error Handling Improvements Implementation Guide

**Projekt**: Grekonto AI Automatizáció  
**Verzió**: 1.0
**Utolsó frissítés**: 2025-11-23

## 🎯 Recommended Implementation Order

### Phase 1: Custom Exception Hierarchy (Priority 1)

**File**: `backend/shared/exceptions.py`

```python
class GrekontException(Exception):
    """Base exception for all Grekonto errors"""
    def __init__(self, message, error_code=None, context=None):
        self.message = message
        self.error_code = error_code or "UNKNOWN_ERROR"
        self.context = context or {}
        super().__init__(self.message)

class ValidationException(GrekontException):
    """File/data validation failures"""
    pass

class ProcessingException(GrekontException):
    """Document processing failures"""
    pass

class ExternalServiceException(GrekontException):
    """External service failures (AOC, Document Intelligence)"""
    pass

class RecoverableException(GrekontException):
    """Transient failures that can be retried"""
    pass
```

### Phase 2: Circuit Breaker Pattern (Priority 1)

**File**: `backend/shared/circuit_breaker.py`

```python
class CircuitBreaker:
    """Prevents cascading failures"""
    
    def __init__(self, failure_threshold=5, timeout=60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
    
    def call(self, func, *args, **kwargs):
        if self.state == "OPEN":
            if self._should_attempt_reset():
                self.state = "HALF_OPEN"
            else:
                raise ExternalServiceException(
                    "Service unavailable (circuit open)"
                )
        
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise
    
    def _on_success(self):
        self.failure_count = 0
        self.state = "CLOSED"
    
    def _on_failure(self):
        self.failure_count += 1
        self.last_failure_time = time.time()
        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"
    
    def _should_attempt_reset(self):
        return (time.time() - self.last_failure_time) > self.timeout
```

### Phase 3: Enhanced Retry Logic (Priority 1)

**File**: `backend/shared/retry_policy.py`

```python
class RetryPolicy:
    """Exponential backoff retry logic"""
    
    def __init__(self, max_retries=3, base_delay=1, max_delay=60):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
    
    def execute(self, func, *args, **kwargs):
        for attempt in range(self.max_retries + 1):
            try:
                return func(*args, **kwargs)
            except RecoverableException as e:
                if attempt == self.max_retries:
                    raise
                
                delay = min(
                    self.base_delay * (2 ** attempt) + random.uniform(0, 1),
                    self.max_delay
                )
                logging.warning(
                    f"Attempt {attempt + 1} failed, retrying in {delay}s: {e}"
                )
                time.sleep(delay)
            except Exception:
                raise
```

### Phase 4: Error Monitoring (Priority 2)

**File**: `backend/shared/error_monitor.py`

```python
class ErrorMonitor:
    """Tracks error metrics and triggers alerts"""
    
    def __init__(self):
        self.error_counts = {}
        self.error_rates = {}
    
    def record_error(self, error_type, context=None):
        key = error_type.__name__
        self.error_counts[key] = self.error_counts.get(key, 0) + 1
        
        # Check alert thresholds
        if self.error_counts[key] > 10:
            self._trigger_alert(error_type, context)
    
    def _trigger_alert(self, error_type, context):
        logging.critical(
            f"ERROR THRESHOLD EXCEEDED: {error_type.__name__}",
            extra={"context": context}
        )
```

### Phase 5: Structured Error Responses (Priority 2)

**File**: `backend/shared/error_response.py`

```python
class ErrorResponse:
    """Standardized error response format"""
    
    @staticmethod
    def create(exception, request_id=None):
        return {
            "error": {
                "code": getattr(exception, 'error_code', 'UNKNOWN'),
                "message": str(exception),
                "context": getattr(exception, 'context', {}),
                "request_id": request_id,
                "timestamp": datetime.utcnow().isoformat()
            }
        }
```

## 📋 Integration Checklist

- [ ] Create custom exception hierarchy
- [ ] Implement circuit breaker pattern
- [ ] Add exponential backoff retry logic
- [ ] Integrate error monitoring
- [ ] Update all API endpoints with structured responses
- [ ] Add error tracking to DLQ
- [ ] Implement error analytics dashboard
- [ ] Add alerting rules
- [ ] Document error codes
- [ ] Create error recovery runbooks

## 🚀 Expected Benefits

✅ Prevent cascading failures  
✅ Faster error recovery  
✅ Better error visibility  
✅ Reduced manual intervention  
✅ Improved system reliability  
✅ Better user experience  

---

## DOKUMENTÁCIÓ VERZIÓ ÉS FRISSÍTÉSI TÖRTÉNET

**Verzió:** 1.0  
**Utolsó frissítés:** 2025-11-23  
**Commit:** TBD

