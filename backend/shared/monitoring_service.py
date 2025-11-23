"""
Comprehensive monitoring and audit trail service for Grekonto.

This module provides:
1. Request tracking with session IDs and timestamps
2. Performance metrics collection and aggregation
3. Alert generation based on error rates and thresholds
4. Redis persistence for historical analysis
5. Compliance audit logging

Traditional DMS Weakness: Limited logging, no performance metrics, difficult troubleshooting.
This Implementation: Built-in monitoring tracks all requests with session IDs, timestamps,
and performance metrics, enabling historical analysis and compliance auditing.
"""

import json
import logging
import os
import time
import uuid
import statistics
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict, field
from enum import Enum
from functools import wraps

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

logger = logging.getLogger(__name__)


class AlertLevel(Enum):
    """Alert severity levels."""
    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"


class EventType(Enum):
    """Types of monitorable events."""
    REQUEST_START = "REQUEST_START"
    REQUEST_COMPLETE = "REQUEST_COMPLETE"
    REQUEST_ERROR = "REQUEST_ERROR"
    PROCESSING_START = "PROCESSING_START"
    PROCESSING_COMPLETE = "PROCESSING_COMPLETE"
    PROCESSING_ERROR = "PROCESSING_ERROR"
    EXTERNAL_SERVICE_CALL = "EXTERNAL_SERVICE_CALL"
    DATABASE_OPERATION = "DATABASE_OPERATION"
    AUTHENTICATION = "AUTHENTICATION"
    AUTHORIZATION = "AUTHORIZATION"
    SECURITY_EVENT = "SECURITY_EVENT"
    PERFORMANCE_ANOMALY = "PERFORMANCE_ANOMALY"


@dataclass
class PerformanceMetric:
    """Tracks performance metrics for requests/operations."""
    operation_name: str
    duration_ms: float
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    success: bool = True
    error_message: Optional[str] = None
    memory_used_mb: Optional[float] = None
    items_processed: Optional[int] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class AuditEvent:
    """Represents an audit trail event."""
    session_id: str
    event_type: EventType
    timestamp: str
    user_id: Optional[str]
    resource_id: Optional[str]
    action: str
    result: str  # SUCCESS, FAILURE, PARTIAL
    message: str
    details: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        event_dict = asdict(self)
        event_dict['event_type'] = self.event_type.value
        return event_dict


@dataclass
class Alert:
    """Represents a generated alert."""
    alert_level: AlertLevel
    title: str
    message: str
    timestamp: str
    threshold_value: float
    current_value: float
    affected_metric: str
    
    def to_dict(self) -> Dict[str, Any]:
        alert_dict = asdict(self)
        alert_dict['alert_level'] = self.alert_level.value
        return alert_dict


class MonitoringService:
    """
    Comprehensive monitoring service for tracking requests, performance metrics,
    and audit trails with Redis persistence.
    
    Features:
    - Session-based request tracking with unique IDs
    - Performance metrics collection and statistical analysis
    - Automatic alert generation based on thresholds
    - Redis persistence for historical analysis
    - Compliance audit logging
    - In-memory fallback for development
    """
    
    def __init__(self, redis_url: Optional[str] = None):
        """
        Initialize monitoring service.
        
        Args:
            redis_url: Redis connection URL (defaults to env var or local)
        """
        self.redis_url = redis_url or os.environ.get("REDIS_MONITORING", 
                                                      "redis://localhost:6379/1")
        self.redis_client: Optional[redis.Redis] = None
        self.use_redis = False
        
        # In-memory storage for development/fallback
        self.metrics_store: Dict[str, List[PerformanceMetric]] = {}
        self.audit_store: Dict[str, AuditEvent] = {}
        self.alerts: List[Alert] = []
        self.sessions: Dict[str, Dict[str, Any]] = {}
        
        # Thresholds for alert generation (105-131)
        self.thresholds = {
            "error_rate": 0.05,              # 5% error rate
            "response_time_ms": 5000,        # 5 second response time
            "failed_requests": 10,           # 10 failed requests
            "memory_threshold_mb": 1024,     # 1GB memory usage
        }
        
        self._initialize_redis()
    
    def _initialize_redis(self) -> None:
        """Initialize Redis connection with fallback to in-memory storage."""
        if not REDIS_AVAILABLE:
            logger.info("Redis module not available, using in-memory storage")
            return
        
        try:
            self.redis_client = redis.from_url(self.redis_url, decode_responses=True)
            # Test connection
            self.redis_client.ping()
            self.use_redis = True
            logger.info(f"Connected to Redis for monitoring at {self.redis_url}")
        except Exception as e:
            logger.warning(f"Failed to connect to Redis for monitoring: {e}. "
                          f"Using in-memory storage.")
            self.use_redis = False
    
    # ===== Session Management (105-131) =====
    
    def create_session(self, user_id: Optional[str] = None, 
                      context: Optional[Dict[str, Any]] = None) -> str:
        """
        Create a new monitoring session with unique session ID.
        
        Args:
            user_id: Optional user identifier
            context: Optional context dictionary
            
        Returns:
            Session ID for tracking
        """
        session_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().isoformat()
        
        session_data = {
            "session_id": session_id,
            "user_id": user_id,
            "created_at": timestamp,
            "context": context or {},
            "request_count": 0,
            "error_count": 0,
            "total_duration_ms": 0,
        }
        
        self.sessions[session_id] = session_data
        
        # Persist to Redis if available (173-180)
        if self.use_redis:
            try:
                redis_key = f"session:{session_id}"
                self.redis_client.setex(
                    redis_key,
                    24 * 3600,  # 24 hour expiration
                    json.dumps(session_data)
                )
            except Exception as e:
                logger.error(f"Failed to store session in Redis: {e}")
        
        logger.info(f"Session created: {session_id} for user: {user_id}")
        return session_id
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session data by ID."""
        # Try Redis first
        if self.use_redis:
            try:
                redis_key = f"session:{session_id}"
                session_data = self.redis_client.get(redis_key)
                if session_data:
                    return json.loads(session_data)
            except Exception as e:
                logger.error(f"Failed to retrieve session from Redis: {e}")
        
        # Fall back to in-memory
        return self.sessions.get(session_id)
    
    def end_session(self, session_id: str) -> bool:
        """End a monitoring session."""
        try:
            if session_id in self.sessions:
                del self.sessions[session_id]
            
            if self.use_redis:
                self.redis_client.delete(f"session:{session_id}")
            
            logger.info(f"Session ended: {session_id}")
            return True
        except Exception as e:
            logger.error(f"Error ending session {session_id}: {e}")
            return False
    
    # ===== Performance Metrics Tracking (105-131) =====
    
    def record_metric(self, session_id: str, metric: PerformanceMetric) -> None:
        """
        Record a performance metric.
        
        Args:
            session_id: Session identifier
            metric: PerformanceMetric object
        """
        # Store in memory
        if metric.operation_name not in self.metrics_store:
            self.metrics_store[metric.operation_name] = []
        
        self.metrics_store[metric.operation_name].append(metric)
        
        # Update session statistics
        if session_id in self.sessions:
            self.sessions[session_id]["request_count"] += 1
            self.sessions[session_id]["total_duration_ms"] += metric.duration_ms
            if not metric.success:
                self.sessions[session_id]["error_count"] += 1
        
        # Persist to Redis (173-180)
        if self.use_redis:
            try:
                redis_key = f"metric:{session_id}:{metric.operation_name}"
                metric_dict = metric.to_dict()
                self.redis_client.lpush(redis_key, json.dumps(metric_dict))
                # Set expiration (30 days for metrics)
                self.redis_client.expire(redis_key, 30 * 24 * 3600)
            except Exception as e:
                logger.error(f"Failed to store metric in Redis: {e}")
    
    def get_metrics(self, operation_name: str, 
                   limit: int = 100) -> List[PerformanceMetric]:
        """Get metrics for a specific operation."""
        if operation_name in self.metrics_store:
            metrics = self.metrics_store[operation_name][-limit:]
            return metrics
        return []
    
    def get_metric_statistics(self, operation_name: str) -> Dict[str, float]:
        """
        Calculate statistics for operation metrics.
        
        Returns:
            Dictionary with min, max, mean, median, stdev, error_rate
        """
        metrics = self.get_metrics(operation_name, limit=1000)
        
        if not metrics:
            return {
                "operation": operation_name,
                "count": 0,
                "message": "No metrics available"
            }
        
        durations = [m.duration_ms for m in metrics]
        successful = [m for m in metrics if m.success]
        error_rate = 1.0 - (len(successful) / len(metrics))
        
        stats = {
            "operation": operation_name,
            "count": len(metrics),
            "min_ms": min(durations),
            "max_ms": max(durations),
            "mean_ms": statistics.mean(durations),
            "median_ms": statistics.median(durations),
            "stdev_ms": statistics.stdev(durations) if len(durations) > 1 else 0,
            "error_rate": error_rate,
            "success_count": len(successful),
            "error_count": len(metrics) - len(successful),
        }
        
        return stats
    
    # ===== Request Tracking =====
    
    def start_request(self, session_id: str, endpoint: str, 
                     method: str = "POST") -> str:
        """
        Track the start of a request.
        
        Args:
            session_id: Session identifier
            endpoint: API endpoint
            method: HTTP method
            
        Returns:
            Request tracking ID
        """
        request_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().isoformat()
        
        event = AuditEvent(
            session_id=session_id,
            event_type=EventType.REQUEST_START,
            timestamp=timestamp,
            user_id=None,
            resource_id=endpoint,
            action=f"{method} {endpoint}",
            result="STARTED",
            message=f"Request started for {endpoint}"
        )
        
        self._log_audit_event(event)
        return request_id
    
    def complete_request(self, session_id: str, request_id: str, 
                        endpoint: str, duration_ms: float,
                        success: bool = True, error_msg: Optional[str] = None) -> None:
        """
        Track the completion of a request.
        
        Args:
            session_id: Session identifier
            request_id: Request tracking ID
            endpoint: API endpoint
            duration_ms: Duration in milliseconds
            success: Whether request was successful
            error_msg: Optional error message
        """
        timestamp = datetime.utcnow().isoformat()
        
        event = AuditEvent(
            session_id=session_id,
            event_type=EventType.REQUEST_COMPLETE,
            timestamp=timestamp,
            user_id=None,
            resource_id=endpoint,
            action=f"REQUEST {request_id}",
            result="SUCCESS" if success else "FAILURE",
            message=f"Request completed in {duration_ms}ms",
            details={
                "request_id": request_id,
                "duration_ms": duration_ms,
                "error": error_msg
            }
        )
        
        self._log_audit_event(event)
        
        # Record metric
        metric = PerformanceMetric(
            operation_name=endpoint,
            duration_ms=duration_ms,
            success=success,
            error_message=error_msg
        )
        self.record_metric(session_id, metric)
    
    # ===== Audit Trail Logging =====
    
    def _log_audit_event(self, event: AuditEvent) -> None:
        """
        Log an audit trail event.
        
        Args:
            event: AuditEvent object
        """
        # Store in memory
        event_key = f"{event.session_id}:{event.timestamp}:{event.event_type.value}"
        self.audit_store[event_key] = event
        
        # Persist to Redis (173-180)
        if self.use_redis:
            try:
                redis_key = f"audit:{event.session_id}"
                event_dict = event.to_dict()
                self.redis_client.lpush(redis_key, json.dumps(event_dict))
                # Set expiration (90 days for audit logs - compliance requirement)
                self.redis_client.expire(redis_key, 90 * 24 * 3600)
            except Exception as e:
                logger.error(f"Failed to store audit event in Redis: {e}")
        
        logger.debug(f"Audit event: {event.event_type.value} - {event.action}")
    
    def log_security_event(self, session_id: str, user_id: Optional[str],
                          action: str, result: str, message: str,
                          details: Optional[Dict[str, Any]] = None) -> None:
        """
        Log a security-related event.
        
        Args:
            session_id: Session identifier
            user_id: User identifier
            action: Security action (e.g., LOGIN_ATTEMPT, PERMISSION_DENIED)
            result: SUCCESS, FAILURE, PARTIAL
            message: Human-readable message
            details: Optional detailed information
        """
        event = AuditEvent(
            session_id=session_id,
            event_type=EventType.SECURITY_EVENT,
            timestamp=datetime.utcnow().isoformat(),
            user_id=user_id,
            resource_id=None,
            action=action,
            result=result,
            message=message,
            details=details or {}
        )
        
        self._log_audit_event(event)
    
    def get_audit_logs(self, session_id: Optional[str] = None,
                      limit: int = 100) -> List[Dict[str, Any]]:
        """
        Retrieve audit logs.
        
        Args:
            session_id: Optional session to filter by
            limit: Maximum number of logs to return
            
        Returns:
            List of audit log entries
        """
        logs = []
        
        # Try Redis first if available
        if self.use_redis and session_id:
            try:
                redis_key = f"audit:{session_id}"
                audit_entries = self.redis_client.lrange(redis_key, 0, limit - 1)
                for entry in audit_entries:
                    logs.append(json.loads(entry))
                return logs
            except Exception as e:
                logger.error(f"Failed to retrieve audit logs from Redis: {e}")
        
        # Fall back to in-memory
        if session_id:
            for key, event in self.audit_store.items():
                if event.session_id == session_id:
                    logs.append(event.to_dict())
        else:
            logs = [event.to_dict() for event in self.audit_store.values()]
        
        # Sort by timestamp descending and limit
        logs.sort(key=lambda x: x['timestamp'], reverse=True)
        return logs[:limit]
    
    # ===== Alert Generation (214-247) =====
    
    def check_thresholds_and_generate_alerts(self) -> List[Alert]:
        """
        Check performance thresholds and generate alerts if exceeded.
        
        Returns:
            List of generated alerts
        """
        new_alerts = []
        
        # Check each operation's metrics
        for operation_name in self.metrics_store.keys():
            stats = self.get_metric_statistics(operation_name)
            
            if stats.get('count', 0) == 0:
                continue
            
            # Alert on high error rate
            if stats['error_rate'] > self.thresholds['error_rate']:
                alert = Alert(
                    alert_level=AlertLevel.WARNING,
                    title="High Error Rate Detected",
                    message=f"Operation '{operation_name}' has error rate of "
                           f"{stats['error_rate']:.1%}",
                    timestamp=datetime.utcnow().isoformat(),
                    threshold_value=self.thresholds['error_rate'],
                    current_value=stats['error_rate'],
                    affected_metric=f"{operation_name}.error_rate"
                )
                new_alerts.append(alert)
            
            # Alert on slow response times
            if stats.get('mean_ms', 0) > self.thresholds['response_time_ms']:
                alert = Alert(
                    alert_level=AlertLevel.WARNING,
                    title="Slow Response Time Detected",
                    message=f"Operation '{operation_name}' average response time is "
                           f"{stats['mean_ms']:.0f}ms",
                    timestamp=datetime.utcnow().isoformat(),
                    threshold_value=self.thresholds['response_time_ms'],
                    current_value=stats['mean_ms'],
                    affected_metric=f"{operation_name}.mean_response_time"
                )
                new_alerts.append(alert)
            
            # Alert on many failures
            if stats['error_count'] >= self.thresholds['failed_requests']:
                alert = Alert(
                    alert_level=AlertLevel.CRITICAL,
                    title="High Number of Failed Requests",
                    message=f"Operation '{operation_name}' has {stats['error_count']} "
                           f"failed requests",
                    timestamp=datetime.utcnow().isoformat(),
                    threshold_value=self.thresholds['failed_requests'],
                    current_value=float(stats['error_count']),
                    affected_metric=f"{operation_name}.error_count"
                )
                new_alerts.append(alert)
        
        # Store alerts
        self.alerts.extend(new_alerts)
        
        # Log alerts
        for alert in new_alerts:
            logger.warning(f"ALERT [{alert.alert_level.value}]: {alert.title} - "
                          f"{alert.message}")
        
        return new_alerts
    
    def get_active_alerts(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get recent active alerts.
        
        Args:
            limit: Maximum number of alerts to return
            
        Returns:
            List of recent alerts
        """
        return [alert.to_dict() for alert in self.alerts[-limit:]]
    
    def set_threshold(self, metric_name: str, threshold_value: float) -> None:
        """
        Set alert threshold for a metric.
        
        Args:
            metric_name: Name of metric (e.g., 'error_rate', 'response_time_ms')
            threshold_value: Threshold value
        """
        if metric_name in self.thresholds:
            old_value = self.thresholds[metric_name]
            self.thresholds[metric_name] = threshold_value
            logger.info(f"Threshold updated: {metric_name} from {old_value} to "
                       f"{threshold_value}")
        else:
            self.thresholds[metric_name] = threshold_value
            logger.info(f"New threshold added: {metric_name} = {threshold_value}")
    
    # ===== Utility Methods =====
    
    def get_health_status(self) -> Dict[str, Any]:
        """
        Get overall system health status.
        
        Returns:
            Dictionary with health metrics
        """
        total_metrics = sum(len(metrics) for metrics in self.metrics_store.values())
        total_audit_entries = len(self.audit_store)
        active_sessions = len(self.sessions)
        active_alerts = len(self.alerts)
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "redis_connected": self.use_redis,
            "total_metrics_recorded": total_metrics,
            "total_audit_entries": total_audit_entries,
            "active_sessions": active_sessions,
            "active_alerts": active_alerts,
            "operations_monitored": len(self.metrics_store),
        }
    
    def reset_metrics(self) -> None:
        """Reset all metrics (for testing purposes)."""
        self.metrics_store.clear()
        self.audit_store.clear()
        self.alerts.clear()
        self.sessions.clear()
        logger.info("All monitoring data reset")


# Global monitoring service instance
_monitoring_service: Optional[MonitoringService] = None


def get_monitoring_service() -> MonitoringService:
    """Get or create global monitoring service instance."""
    global _monitoring_service
    if _monitoring_service is None:
        _monitoring_service = MonitoringService()
    return _monitoring_service


def track_request(endpoint: str, method: str = "POST"):
    """
    Decorator to automatically track requests.
    
    Usage:
        @track_request("/api/upload", "POST")
        def handle_upload(req):
            return {"status": "success"}
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            monitoring = get_monitoring_service()
            
            # Get or create session
            session_id = kwargs.get('session_id') or str(uuid.uuid4())
            request_id = monitoring.start_request(session_id, endpoint, method)
            
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                duration_ms = (time.time() - start_time) * 1000
                monitoring.complete_request(session_id, request_id, endpoint,
                                           duration_ms, success=True)
                return result
            except Exception as e:
                duration_ms = (time.time() - start_time) * 1000
                monitoring.complete_request(session_id, request_id, endpoint,
                                           duration_ms, success=False,
                                           error_msg=str(e))
                raise
        
        return wrapper
    return decorator


def performance_timer(operation_name: str):
    """
    Decorator to track operation performance.
    
    Usage:
        @performance_timer("document_processing")
        def process_document(doc):
            pass
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            monitoring = get_monitoring_service()
            session_id = str(uuid.uuid4())
            
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                duration_ms = (time.time() - start_time) * 1000
                
                metric = PerformanceMetric(
                    operation_name=operation_name,
                    duration_ms=duration_ms,
                    success=True,
                    items_processed=kwargs.get('items', None)
                )
                monitoring.record_metric(session_id, metric)
                return result
            except Exception as e:
                duration_ms = (time.time() - start_time) * 1000
                metric = PerformanceMetric(
                    operation_name=operation_name,
                    duration_ms=duration_ms,
                    success=False,
                    error_message=str(e)
                )
                monitoring.record_metric(session_id, metric)
                raise
        
        return wrapper
    return decorator
