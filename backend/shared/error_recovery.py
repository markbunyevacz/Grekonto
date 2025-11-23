"""
Error recovery and fallback mechanisms.

Implements graceful degradation strategies when primary operations fail,
allowing the system to continue with reduced functionality.
"""

import logging
from typing import Callable, Any, Optional, Tuple
from functools import wraps

logger = logging.getLogger(__name__)


class RecoveryStrategy:
    """Base class for recovery strategies."""
    
    def can_recover(self, exception: Exception) -> bool:
        """Check if this strategy can handle the exception."""
        raise NotImplementedError
    
    def recover(self, *args, **kwargs) -> Any:
        """Execute recovery strategy."""
        raise NotImplementedError


class FallbackStrategy(RecoveryStrategy):
    """Use fallback value when operation fails."""
    
    def __init__(self, fallback_value: Any):
        self.fallback_value = fallback_value
    
    def can_recover(self, exception: Exception) -> bool:
        return True
    
    def recover(self, *args, **kwargs) -> Any:
        logger.warning(f"⚠️  Using fallback value: {self.fallback_value}")
        return self.fallback_value


class RetryStrategy(RecoveryStrategy):
    """Retry operation with exponential backoff."""
    
    def __init__(self, max_retries: int = 3, backoff_factor: float = 2.0):
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        self.retry_count = 0
    
    def can_recover(self, exception: Exception) -> bool:
        return self.retry_count < self.max_retries
    
    def recover(self, func: Callable, *args, **kwargs) -> Any:
        """Retry with exponential backoff."""
        import time
        
        self.retry_count += 1
        wait_time = self.backoff_factor ** (self.retry_count - 1)
        
        logger.info(
            f"🔄 Retry attempt {self.retry_count}/{self.max_retries} "
            f"(waiting {wait_time}s)"
        )
        time.sleep(wait_time)
        
        return func(*args, **kwargs)


class DegradedModeStrategy(RecoveryStrategy):
    """Switch to degraded mode with reduced functionality."""
    
    def __init__(self, degraded_func: Callable):
        self.degraded_func = degraded_func
    
    def can_recover(self, exception: Exception) -> bool:
        return True
    
    def recover(self, *args, **kwargs) -> Any:
        logger.warning("⚠️  Switching to degraded mode")
        return self.degraded_func(*args, **kwargs)


def with_recovery(
    primary_func: Callable,
    recovery_strategies: list,
    error_handler: Optional[Callable] = None
) -> Callable:
    """
    Decorator for error recovery with fallback strategies.
    
    Args:
        primary_func: Primary function to execute
        recovery_strategies: List of recovery strategies to try
        error_handler: Optional error handler function
    """
    @wraps(primary_func)
    def wrapper(*args, **kwargs):
        try:
            return primary_func(*args, **kwargs)
        except Exception as e:
            logger.error(f"❌ Primary operation failed: {str(e)}")
            
            if error_handler:
                error_handler(e)
            
            # Try recovery strategies
            for strategy in recovery_strategies:
                try:
                    if strategy.can_recover(e):
                        logger.info(f"🔄 Attempting recovery with {strategy.__class__.__name__}")
                        
                        if isinstance(strategy, RetryStrategy):
                            return strategy.recover(primary_func, *args, **kwargs)
                        elif isinstance(strategy, DegradedModeStrategy):
                            return strategy.recover(*args, **kwargs)
                        else:
                            return strategy.recover(*args, **kwargs)
                except Exception as recovery_error:
                    logger.warning(
                        f"⚠️  Recovery strategy failed: {str(recovery_error)}"
                    )
                    continue
            
            # All recovery strategies failed
            logger.error("❌ All recovery strategies exhausted")
            raise
    
    return wrapper


class ErrorRecoveryManager:
    """Manages error recovery for different operations."""
    
    def __init__(self):
        self.recovery_configs = {}
    
    def register_recovery(
        self,
        operation_name: str,
        strategies: list
    ):
        """Register recovery strategies for an operation."""
        self.recovery_configs[operation_name] = strategies
        logger.info(f"📋 Registered recovery for: {operation_name}")
    
    def execute_with_recovery(
        self,
        operation_name: str,
        func: Callable,
        *args,
        **kwargs
    ) -> Any:
        """Execute operation with registered recovery strategies."""
        strategies = self.recovery_configs.get(operation_name, [])
        
        if not strategies:
            logger.warning(f"⚠️  No recovery strategies for: {operation_name}")
            return func(*args, **kwargs)
        
        return with_recovery(func, strategies)(*args, **kwargs)


# Global recovery manager
recovery_manager = ErrorRecoveryManager()

