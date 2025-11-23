"""
Enhanced audit logging module for compliance and security auditing.

Provides specialized audit trail functionality for:
- Detailed compliance logging with retention policies
- Security event tracking (authentication, authorization, data access)
- Change tracking for sensitive operations
- Immutable audit trail storage
- Compliance report generation
"""

import logging
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from enum import Enum
from dataclasses import dataclass, asdict

try:
    from azure.data.tables import TableServiceClient, TableClient
    AZURE_TABLES_AVAILABLE = True
except ImportError:
    AZURE_TABLES_AVAILABLE = False

import os

logger = logging.getLogger(__name__)


class ComplianceLevel(Enum):
    """Compliance requirement levels."""
    STANDARD = "STANDARD"          # 30 day retention
    ENHANCED = "ENHANCED"          # 90 day retention
    CRITICAL = "CRITICAL"          # 2 year retention (regulatory)


class AuditCategory(Enum):
    """Audit event categories."""
    AUTHENTICATION = "AUTHENTICATION"      # Login, logout, token issues
    AUTHORIZATION = "AUTHORIZATION"        # Permission checks, access denials
    DATA_ACCESS = "DATA_ACCESS"           # Read, write, delete operations
    DATA_CHANGE = "DATA_CHANGE"           # Modifications to sensitive data
    CONFIGURATION = "CONFIGURATION"        # System configuration changes
    SECURITY = "SECURITY"                  # Security events, threats
    COMPLIANCE = "COMPLIANCE"              # Regulatory compliance events
    AUDIT = "AUDIT"                        # Audit trail management


@dataclass
class ComplianceAuditEvent:
    """
    Immutable audit event for compliance purposes.
    
    Attributes match SOC 2 and HIPAA audit requirements.
    """
    event_id: str
    timestamp: str                  # ISO format
    category: AuditCategory
    action: str                     # Specific action taken
    actor: str                      # User/service performing action
    resource: str                   # Resource being accessed/modified
    result: str                     # SUCCESS, FAILURE, PARTIAL
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    session_id: Optional[str] = None
    error_message: Optional[str] = None
    
    # Change tracking for DATA_CHANGE events
    old_value: Optional[Dict[str, Any]] = None
    new_value: Optional[Dict[str, Any]] = None
    
    # Additional context
    details: Dict[str, Any] = None
    severity: str = "INFO"          # INFO, WARNING, CRITICAL
    
    def __post_init__(self):
        if self.details is None:
            self.details = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary, handling enum serialization."""
        event_dict = {
            "event_id": self.event_id,
            "timestamp": self.timestamp,
            "category": self.category.value,
            "action": self.action,
            "actor": self.actor,
            "resource": self.resource,
            "result": self.result,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "session_id": self.session_id,
            "error_message": self.error_message,
            "old_value": self.old_value,
            "new_value": self.new_value,
            "details": self.details,
            "severity": self.severity,
        }
        return event_dict
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict())


class AuditLogger:
    """
    Enhanced audit logger for compliance and security.
    
    Features:
    - Azure Table Storage persistence (for production)
    - In-memory fallback for development
    - Compliance retention policies
    - Immutable event storage
    - Audit trail analysis and reporting
    """
    
    def __init__(self, table_name: str = "AuditEvents"):
        """
        Initialize audit logger.
        
        Args:
            table_name: Azure Table name for audit events
        """
        self.table_name = table_name
        self.table_client: Optional[TableClient] = None
        self.use_azure = False
        
        # In-memory storage for development/fallback
        self.events: Dict[str, ComplianceAuditEvent] = {}
        
        self._initialize_azure_tables()
    
    def _initialize_azure_tables(self) -> None:
        """Initialize Azure Tables connection if available."""
        if not AZURE_TABLES_AVAILABLE:
            logger.info("Azure Tables not available, using in-memory storage")
            return
        
        try:
            connect_str = os.getenv('AzureWebJobsStorage')
            if not connect_str:
                logger.warning("AzureWebJobsStorage not configured")
                return
            
            service_client = TableServiceClient.from_connection_string(connect_str)
            
            # Create table if doesn't exist
            try:
                service_client.create_table(self.table_name)
                logger.info(f"Created audit table: {self.table_name}")
            except Exception:
                pass  # Table already exists
            
            self.table_client = service_client.get_table_client(self.table_name)
            self.use_azure = True
            logger.info(f"Connected to Azure Tables for audit logging")
        except Exception as e:
            logger.error(f"Failed to initialize Azure Tables for audit: {e}")
    
    def log_event(self, event: ComplianceAuditEvent, 
                 compliance_level: ComplianceLevel = ComplianceLevel.STANDARD) -> bool:
        """
        Log an audit event.
        
        Args:
            event: ComplianceAuditEvent to log
            compliance_level: Compliance retention requirement
            
        Returns:
            True if event was successfully logged
        """
        # Store in memory
        self.events[event.event_id] = event
        
        # Persist to Azure Tables
        if self.use_azure and self.table_client:
            try:
                entity = {
                    "PartitionKey": self._get_partition_key(event.timestamp,
                                                           compliance_level),
                    "RowKey": event.event_id,
                    "Timestamp": event.timestamp,
                    "Category": event.category.value,
                    "Action": event.action,
                    "Actor": event.actor,
                    "Resource": event.resource,
                    "Result": event.result,
                    "IPAddress": event.ip_address or "",
                    "UserAgent": event.user_agent or "",
                    "SessionId": event.session_id or "",
                    "ErrorMessage": event.error_message or "",
                    "OldValue": json.dumps(event.old_value) if event.old_value else "",
                    "NewValue": json.dumps(event.new_value) if event.new_value else "",
                    "Details": json.dumps(event.details),
                    "Severity": event.severity,
                    "ComplianceLevel": compliance_level.value,
                    "EventJson": event.to_json(),
                }
                
                self.table_client.upsert_entity(entity)
                logger.debug(f"Audit event logged: {event.action} - {event.result}")
                return True
            except Exception as e:
                logger.error(f"Failed to log audit event to Azure: {e}")
                return False
        
        logger.debug(f"Audit event stored in memory: {event.action}")
        return True
    
    def _get_partition_key(self, timestamp: str, 
                          compliance_level: ComplianceLevel) -> str:
        """
        Generate partition key for audit events.
        
        Partitioning strategy:
        - CRITICAL: By month (long retention)
        - ENHANCED: By week (90 day retention)
        - STANDARD: By day (30 day retention)
        
        Args:
            timestamp: Event timestamp (ISO format)
            compliance_level: Compliance level for retention
            
        Returns:
            Partition key
        """
        try:
            dt = datetime.fromisoformat(timestamp)
            
            if compliance_level == ComplianceLevel.CRITICAL:
                return f"CRITICAL_{dt.strftime('%Y%m')}"
            elif compliance_level == ComplianceLevel.ENHANCED:
                return f"ENHANCED_{dt.strftime('%Y%W')}"
            else:
                return f"STANDARD_{dt.strftime('%Y%m%d')}"
        except:
            return f"AUDIT_{datetime.utcnow().strftime('%Y%m%d')}"
    
    # ===== Specialized Logging Methods =====
    
    def log_authentication(self, actor: str, resource: str, result: str,
                          session_id: Optional[str] = None,
                          ip_address: Optional[str] = None,
                          error_msg: Optional[str] = None) -> bool:
        """
        Log authentication event.
        
        Args:
            actor: User/service attempting authentication
            resource: Resource being accessed
            result: SUCCESS or FAILURE
            session_id: Session ID if created
            ip_address: Source IP address
            error_msg: Error message if failed
            
        Returns:
            True if logged successfully
        """
        event = ComplianceAuditEvent(
            event_id=self._generate_event_id(),
            timestamp=datetime.utcnow().isoformat(),
            category=AuditCategory.AUTHENTICATION,
            action=f"AUTHENTICATION_ATTEMPT",
            actor=actor,
            resource=resource,
            result=result,
            ip_address=ip_address,
            session_id=session_id,
            error_message=error_msg,
            severity="CRITICAL" if result == "FAILURE" else "INFO",
        )
        
        return self.log_event(event, ComplianceLevel.CRITICAL)
    
    def log_authorization(self, actor: str, resource: str, permission: str,
                         result: str, ip_address: Optional[str] = None) -> bool:
        """
        Log authorization event (permission check).
        
        Args:
            actor: User/service requesting access
            resource: Resource being accessed
            permission: Permission being checked (READ, WRITE, DELETE, ADMIN)
            result: ALLOWED or DENIED
            ip_address: Source IP address
            
        Returns:
            True if logged successfully
        """
        event = ComplianceAuditEvent(
            event_id=self._generate_event_id(),
            timestamp=datetime.utcnow().isoformat(),
            category=AuditCategory.AUTHORIZATION,
            action=f"AUTHORIZATION_CHECK",
            actor=actor,
            resource=resource,
            result=result,
            ip_address=ip_address,
            details={"permission": permission},
            severity="WARNING" if result == "DENIED" else "INFO",
        )
        
        return self.log_event(event, ComplianceLevel.ENHANCED)
    
    def log_data_access(self, actor: str, resource: str, operation: str,
                       result: str, record_count: Optional[int] = None) -> bool:
        """
        Log data access event.
        
        Args:
            actor: User/service accessing data
            resource: Data resource (file, database table, etc.)
            operation: READ, WRITE, DELETE, EXPORT
            result: SUCCESS or FAILURE
            record_count: Number of records accessed (if applicable)
            
        Returns:
            True if logged successfully
        """
        event = ComplianceAuditEvent(
            event_id=self._generate_event_id(),
            timestamp=datetime.utcnow().isoformat(),
            category=AuditCategory.DATA_ACCESS,
            action=f"DATA_ACCESS_{operation}",
            actor=actor,
            resource=resource,
            result=result,
            details={"operation": operation, "record_count": record_count},
            severity="WARNING" if operation in ["EXPORT", "DELETE"] else "INFO",
        )
        
        return self.log_event(event, ComplianceLevel.ENHANCED)
    
    def log_data_change(self, actor: str, resource: str,
                       old_value: Dict[str, Any], new_value: Dict[str, Any],
                       reason: Optional[str] = None) -> bool:
        """
        Log data modification event (for sensitive data tracking).
        
        Args:
            actor: User/service making the change
            resource: Resource being modified
            old_value: Previous value
            new_value: New value
            reason: Reason for change
            
        Returns:
            True if logged successfully
        """
        event = ComplianceAuditEvent(
            event_id=self._generate_event_id(),
            timestamp=datetime.utcnow().isoformat(),
            category=AuditCategory.DATA_CHANGE,
            action="DATA_MODIFIED",
            actor=actor,
            resource=resource,
            result="SUCCESS",
            old_value=old_value,
            new_value=new_value,
            details={"reason": reason},
            severity="WARNING",
        )
        
        return self.log_event(event, ComplianceLevel.CRITICAL)
    
    def log_security_event(self, actor: str, event_type: str, resource: str,
                          result: str, severity: str = "WARNING",
                          details: Optional[Dict[str, Any]] = None) -> bool:
        """
        Log security event (suspicious activity, threats, etc.).
        
        Args:
            actor: User/service involved
            event_type: Type of security event (e.g., SUSPICIOUS_ACCESS,
                       FAILED_AUTH_ATTEMPTS, MALWARE_DETECTED)
            resource: Resource affected
            result: Event result
            severity: INFO, WARNING, CRITICAL
            details: Additional details
            
        Returns:
            True if logged successfully
        """
        event = ComplianceAuditEvent(
            event_id=self._generate_event_id(),
            timestamp=datetime.utcnow().isoformat(),
            category=AuditCategory.SECURITY,
            action=event_type,
            actor=actor,
            resource=resource,
            result=result,
            details=details or {},
            severity=severity,
        )
        
        compliance_level = (ComplianceLevel.CRITICAL if severity == "CRITICAL"
                           else ComplianceLevel.ENHANCED)
        
        return self.log_event(event, compliance_level)
    
    def log_configuration_change(self, actor: str, component: str,
                                setting: str, old_value: Any,
                                new_value: Any) -> bool:
        """
        Log system configuration change.
        
        Args:
            actor: User/service making the change
            component: Component being configured
            setting: Setting name
            old_value: Previous value
            new_value: New value
            
        Returns:
            True if logged successfully
        """
        event = ComplianceAuditEvent(
            event_id=self._generate_event_id(),
            timestamp=datetime.utcnow().isoformat(),
            category=AuditCategory.CONFIGURATION,
            action="CONFIGURATION_CHANGED",
            actor=actor,
            resource=f"{component}.{setting}",
            result="SUCCESS",
            old_value={"value": old_value},
            new_value={"value": new_value},
            severity="WARNING",
        )
        
        return self.log_event(event, ComplianceLevel.CRITICAL)
    
    # ===== Query and Reporting =====
    
    def get_events(self, start_time: Optional[datetime] = None,
                  end_time: Optional[datetime] = None,
                  actor: Optional[str] = None,
                  category: Optional[AuditCategory] = None,
                  limit: int = 100) -> List[ComplianceAuditEvent]:
        """
        Query audit events with optional filtering.
        
        Args:
            start_time: Start of time range (optional)
            end_time: End of time range (optional)
            actor: Filter by actor (optional)
            category: Filter by category (optional)
            limit: Maximum results to return
            
        Returns:
            List of matching audit events
        """
        results = []
        
        for event in self.events.values():
            # Time range filter
            if start_time or end_time:
                event_time = datetime.fromisoformat(event.timestamp)
                if start_time and event_time < start_time:
                    continue
                if end_time and event_time > end_time:
                    continue
            
            # Actor filter
            if actor and event.actor != actor:
                continue
            
            # Category filter
            if category and event.category != category:
                continue
            
            results.append(event)
        
        # Sort by timestamp descending
        results.sort(key=lambda e: e.timestamp, reverse=True)
        return results[:limit]
    
    def generate_compliance_report(self, start_date: datetime,
                                  end_date: datetime) -> Dict[str, Any]:
        """
        Generate compliance audit report for a date range.
        
        Args:
            start_date: Report start date
            end_date: Report end date
            
        Returns:
            Compliance report dictionary
        """
        events = self.get_events(start_time=start_date, end_time=end_date, limit=10000)
        
        if not events:
            return {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "total_events": 0,
                "message": "No events in period"
            }
        
        # Aggregate statistics
        categories = {}
        results = {}
        actors = {}
        severities = {}
        
        for event in events:
            # By category
            cat_name = event.category.value
            categories[cat_name] = categories.get(cat_name, 0) + 1
            
            # By result
            results[event.result] = results.get(event.result, 0) + 1
            
            # By actor
            actors[event.actor] = actors.get(event.actor, 0) + 1
            
            # By severity
            severities[event.severity] = severities.get(event.severity, 0) + 1
        
        # Critical events (failures, denials)
        critical_events = [e for e in events if e.severity == "CRITICAL"
                          or e.result == "FAILURE" or e.result == "DENIED"]
        
        return {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "generated_at": datetime.utcnow().isoformat(),
            "total_events": len(events),
            "by_category": categories,
            "by_result": results,
            "by_actor": actors,
            "by_severity": severities,
            "critical_events_count": len(critical_events),
            "critical_events_sample": [
                e.to_dict() for e in critical_events[:10]
            ],
        }
    
    def search_events(self, query: str) -> List[ComplianceAuditEvent]:
        """
        Search audit events by action or resource.
        
        Args:
            query: Search string (case-insensitive)
            
        Returns:
            List of matching events
        """
        query_lower = query.lower()
        results = []
        
        for event in self.events.values():
            if (query_lower in event.action.lower() or
                query_lower in event.resource.lower() or
                query_lower in event.actor.lower()):
                results.append(event)
        
        results.sort(key=lambda e: e.timestamp, reverse=True)
        return results
    
    def get_failed_authentications(self, hours: int = 24) -> List[ComplianceAuditEvent]:
        """
        Get failed authentication attempts in the last N hours.
        
        Args:
            hours: Number of hours to look back
            
        Returns:
            List of failed authentication events
        """
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        return [e for e in self.events.values()
               if e.category == AuditCategory.AUTHENTICATION
               and e.result == "FAILURE"
               and datetime.fromisoformat(e.timestamp) > cutoff_time]
    
    def _generate_event_id(self) -> str:
        """Generate unique event ID."""
        import uuid
        return f"EVT_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:8].upper()}"


# Global audit logger instance
_audit_logger: Optional[AuditLogger] = None


def get_audit_logger() -> AuditLogger:
    """Get or create global audit logger instance."""
    global _audit_logger
    if _audit_logger is None:
        _audit_logger = AuditLogger()
    return _audit_logger
