"""
Tests for error handling and recovery system.
"""

import unittest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared.exceptions import (
    ValidationException,
    ProcessingException,
    ExternalServiceException,
    CircuitBreakerException
)
from shared.circuit_breaker import CircuitBreaker, CircuitState
from shared.error_recovery import (
    FallbackStrategy,
    RetryStrategy,
    DegradedModeStrategy,
    with_recovery
)
from shared.error_logger import (
    ErrorLogger,
    ErrorCategory,
    ErrorSeverity
)


class TestCustomExceptions(unittest.TestCase):
    """Test custom exception types."""
    
    def test_validation_exception(self):
        """Test ValidationException."""
        exc = ValidationException("Invalid file", {"filename": "test.txt"})
        self.assertEqual(exc.error_code, "VALIDATION_ERROR")
        self.assertFalse(exc.recoverable)
        self.assertEqual(exc.context["filename"], "test.txt")
    
    def test_processing_exception(self):
        """Test ProcessingException."""
        exc = ProcessingException("OCR failed", recoverable=True)
        self.assertEqual(exc.error_code, "PROCESSING_ERROR")
        self.assertTrue(exc.recoverable)
    
    def test_external_service_exception(self):
        """Test ExternalServiceException."""
        exc = ExternalServiceException("AOC timeout", service="AOC")
        self.assertEqual(exc.error_code, "SERVICE_ERROR_AOC")
        self.assertTrue(exc.recoverable)
        self.assertEqual(exc.context["service"], "AOC")
    
    def test_exception_to_dict(self):
        """Test exception serialization."""
        exc = ValidationException("Test error")
        exc_dict = exc.to_dict()
        self.assertIn("error_code", exc_dict)
        self.assertIn("message", exc_dict)
        self.assertIn("timestamp", exc_dict)


class TestCircuitBreaker(unittest.TestCase):
    """Test circuit breaker pattern."""
    
    def setUp(self):
        self.breaker = CircuitBreaker(
            name="test_service",
            failure_threshold=3,
            recovery_timeout=1
        )
    
    def test_circuit_closed_success(self):
        """Test circuit breaker in closed state."""
        def success_func():
            return "success"
        
        result = self.breaker.call(success_func)
        self.assertEqual(result, "success")
        self.assertEqual(self.breaker.state, CircuitState.CLOSED)
    
    def test_circuit_opens_on_failures(self):
        """Test circuit breaker opens after threshold."""
        def failing_func():
            raise Exception("Service error")

        for _ in range(3):
            try:
                self.breaker.call(failing_func)
            except Exception:
                pass

        self.assertEqual(self.breaker.state, CircuitState.OPEN)
    
    def test_circuit_rejects_when_open(self):
        """Test circuit breaker rejects calls when open."""
        from datetime import datetime, timedelta

        self.breaker.state = CircuitState.OPEN
        # Set last failure time to recent past (within recovery timeout)
        self.breaker.last_failure_time = datetime.utcnow() - timedelta(seconds=0.5)

        with self.assertRaises(CircuitBreakerException):
            self.breaker.call(lambda: "test")
    
    def test_circuit_half_open_recovery(self):
        """Test circuit breaker recovery."""
        self.breaker.state = CircuitState.OPEN
        self.breaker.last_failure_time = None
        
        def success_func():
            return "recovered"
        
        result = self.breaker.call(success_func)
        self.assertEqual(result, "recovered")
        self.assertEqual(self.breaker.state, CircuitState.CLOSED)


class TestErrorRecovery(unittest.TestCase):
    """Test error recovery strategies."""
    
    def test_fallback_strategy(self):
        """Test fallback strategy."""
        strategy = FallbackStrategy("fallback_value")
        result = strategy.recover()
        self.assertEqual(result, "fallback_value")
    
    def test_retry_strategy(self):
        """Test retry strategy."""
        strategy = RetryStrategy(max_retries=3)

        call_count = [0]
        def failing_func():
            call_count[0] += 1
            if call_count[0] < 3:
                raise Exception("Temporary failure")
            return "success"

        # First two calls fail, third succeeds
        try:
            strategy.recover(failing_func)
        except Exception:
            pass

        self.assertEqual(strategy.retry_count, 1)
    
    def test_degraded_mode_strategy(self):
        """Test degraded mode strategy."""
        def degraded_func(*args, **kwargs):
            return "degraded_result"
        
        strategy = DegradedModeStrategy(degraded_func)
        result = strategy.recover()
        self.assertEqual(result, "degraded_result")
    
    def test_with_recovery_decorator(self):
        """Test recovery decorator."""
        call_count = [0]
        
        def primary_func():
            call_count[0] += 1
            if call_count[0] == 1:
                raise Exception("First call fails")
            return "success"
        
        strategies = [FallbackStrategy("fallback")]
        wrapped = with_recovery(primary_func, strategies)
        
        result = wrapped()
        self.assertEqual(result, "fallback")


class TestErrorLogger(unittest.TestCase):
    """Test error logging."""
    
    def setUp(self):
        self.logger = ErrorLogger()
    
    def test_log_error(self):
        """Test error logging."""
        error_log = self.logger.log_error(
            error_id="ERR001",
            message="Test error",
            category=ErrorCategory.VALIDATION,
            severity=ErrorSeverity.ERROR
        )
        
        self.assertEqual(error_log.error_id, "ERR001")
        self.assertEqual(error_log.category, ErrorCategory.VALIDATION)
    
    def test_error_history(self):
        """Test error history."""
        for i in range(5):
            self.logger.log_error(
                error_id=f"ERR{i:03d}",
                message=f"Error {i}",
                category=ErrorCategory.PROCESSING,
                severity=ErrorSeverity.ERROR
            )
        
        history = self.logger.get_error_history()
        self.assertEqual(len(history), 5)
    
    def test_error_filtering(self):
        """Test error filtering."""
        self.logger.log_error(
            error_id="ERR001",
            message="Validation error",
            category=ErrorCategory.VALIDATION,
            severity=ErrorSeverity.ERROR
        )
        
        self.logger.log_error(
            error_id="ERR002",
            message="Processing error",
            category=ErrorCategory.PROCESSING,
            severity=ErrorSeverity.WARNING
        )
        
        validation_errors = self.logger.get_error_history(
            category=ErrorCategory.VALIDATION
        )
        self.assertEqual(len(validation_errors), 1)
    
    def test_error_stats(self):
        """Test error statistics."""
        self.logger.log_error(
            error_id="ERR001",
            message="Error 1",
            category=ErrorCategory.VALIDATION,
            severity=ErrorSeverity.ERROR
        )
        
        stats = self.logger.get_error_stats()
        self.assertIn("total_errors", stats)
        self.assertIn("by_category", stats)
        self.assertIn("by_severity", stats)


if __name__ == '__main__':
    unittest.main()

