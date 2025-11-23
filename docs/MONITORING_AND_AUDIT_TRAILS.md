# Monitoring & Audit Trails Implementation

**Projekt**: Grekonto AI Automatizáció  
**Verzió**: 1.0  
**Utolsó frissítés**: 2025-11-23

## 🎯 Overview

Comprehensive monitoring and audit trail system that addresses traditional DMS weaknesses by providing:

1. **Built-in Request Tracking** - All requests tracked with session IDs, timestamps, and performance metrics
2. **Performance Metrics** - Historical analysis enables proactive optimization
3. **Alert Generation** - Automatic alerts based on error rates and performance thresholds
4. **Compliance Auditing** - Immutable audit trails for regulatory compliance
5. **Redis Persistence** - Historical data storage for long-term analysis

### Traditional DMS Weakness
Limited logging, no performance metrics, difficult troubleshooting → Silent failures and inability to track issues

### This Implementation
- ✅ Session-based request tracking with unique IDs
- ✅ Real-time performance metrics collection
- ✅ Redis persistence for 90+ days compliance retention
- ✅ Automatic alert generation based on thresholds
- ✅ Immutable audit trail for compliance

---

## 📁 Components

### 1. **monitoring_service.py** (Lines 105-131, 173-180, 214-247)

Comprehensive monitoring service with request tracking, metrics collection, and alert generation.

**Key Features:**
- Session management with unique session IDs
- Performance metric collection and statistical analysis
- Request lifecycle tracking (start → completion)
- Alert generation based on configurable thresholds
- Redis persistence for metrics and audit events

**Main Classes:**

#### `MonitoringService`
```python
monitoring = MonitoringService(redis_url="redis://localhost:6379/1")

# Session Management (105-131)
session_id = monitoring.create_session(user_id="user123")
session_data = monitoring.get_session(session_id)
monitoring.end_session(session_id)

# Performance Metrics (105-131)
metric = PerformanceMetric(
    operation_name="document_processing",
    duration_ms=1250.5,
    success=True,
    items_processed=5
)
monitoring.record_metric(session_id, metric)

# Request Tracking
request_id = monitoring.start_request(session_id, "/api/upload", "POST")
# ... perform operation ...
monitoring.complete_request(
    session_id, request_id, "/api/upload",
    duration_ms=2500, success=True
)

# Alert Generation (214-247)
alerts = monitoring.check_thresholds_and_generate_alerts()
for alert in alerts:
    print(f"ALERT [{alert.alert_level}]: {alert.title}")

# Query Results
stats = monitoring.get_metric_statistics("document_processing")
# Returns: min_ms, max_ms, mean_ms, median_ms, stdev_ms, error_rate

recent_alerts = monitoring.get_active_alerts(limit=50)
health_status = monitoring.get_health_status()
```

**Performance Statistics Example:**
```json
{
  "operation": "document_processing",
  "count": 150,
  "min_ms": 245.3,
  "max_ms": 5840.2,
  "mean_ms": 1250.5,
  "median_ms": 1180.0,
  "stdev_ms": 890.3,
  "error_rate": 0.02,
  "success_count": 147,
  "error_count": 3
}
```

**Alert Thresholds (Configurable):**
```python
monitoring.set_threshold("error_rate", 0.05)              # 5% error rate
monitoring.set_threshold("response_time_ms", 5000)        # 5 second max
monitoring.set_threshold("failed_requests", 10)           # 10 failures max
monitoring.set_threshold("memory_threshold_mb", 1024)     # 1GB max
```

**Redis Persistence (173-180):**
- Sessions stored for 24 hours
- Metrics stored for 30 days with historical analysis
- Audit logs stored for 90 days (compliance requirement)
- Automatic expiration and cleanup

---

### 2. **audit_logger.py**

Enhanced audit logging for compliance and security with immutable event trails.

**Key Features:**
- Specialized audit event logging
- Compliance level tracking (STANDARD/ENHANCED/CRITICAL)
- Security event tracking (authentication, authorization, data access)
- Change tracking for sensitive data
- Compliance report generation
- Failed authentication monitoring

**Main Classes:**

#### `AuditLogger`
```python
from shared.audit_logger import get_audit_logger, AuditCategory, ComplianceLevel

audit = get_audit_logger()

# Authentication Logging
audit.log_authentication(
    actor="user@example.com",
    resource="/api/upload",
    result="SUCCESS",
    session_id="sess_123",
    ip_address="192.168.1.1"
)

# Authorization Logging
audit.log_authorization(
    actor="user@example.com",
    resource="document_123",
    permission="READ",
    result="ALLOWED"
)

# Data Access Logging
audit.log_data_access(
    actor="system_service",
    resource="AuditLogs table",
    operation="READ",
    result="SUCCESS",
    record_count=150
)

# Data Change Tracking
audit.log_data_change(
    actor="admin@example.com",
    resource="user_settings",
    old_value={"email": "old@example.com"},
    new_value={"email": "new@example.com"},
    reason="Email update request"
)

# Security Events
audit.log_security_event(
    actor="unknown",
    event_type="FAILED_AUTH_ATTEMPTS",
    resource="/api/upload",
    result="FAILURE",
    severity="CRITICAL",
    details={"attempts": 5, "time_window": "5 minutes"}
)

# Configuration Changes
audit.log_configuration_change(
    actor="admin@example.com",
    component="monitoring_service",
    setting="error_rate_threshold",
    old_value=0.05,
    new_value=0.03
)
```

**Compliance Reports:**
```python
from datetime import datetime, timedelta

start = datetime(2025, 11, 1)
end = datetime(2025, 11, 30)

report = audit.generate_compliance_report(start, end)

# Returns:
{
    "start_date": "2025-11-01T00:00:00",
    "end_date": "2025-11-30T23:59:59",
    "generated_at": "2025-11-23T15:30:45.123456",
    "total_events": 2547,
    "by_category": {
        "AUTHENTICATION": 342,
        "AUTHORIZATION": 156,
        "DATA_ACCESS": 1834,
        "SECURITY": 215
    },
    "by_result": {
        "SUCCESS": 2412,
        "FAILURE": 87,
        "PARTIAL": 48
    },
    "by_actor": {
        "user@example.com": 1234,
        "admin@example.com": 456,
        "system_service": 857
    },
    "by_severity": {
        "INFO": 2000,
        "WARNING": 487,
        "CRITICAL": 60
    },
    "critical_events_count": 60,
    "critical_events_sample": [...]
}
```

**Compliance Levels:**
- **STANDARD** (30 days): Regular operations
- **ENHANCED** (90 days): Sensitive operations, authorization
- **CRITICAL** (2 years): Security events, configuration changes, data modifications

---

## 🔌 API Endpoints

### 1. **GET /api/metrics**
Retrieve performance metrics for monitoring operations.

**Parameters:**
- `operation` (optional): Filter by operation name
- `limit` (optional, default: 100): Maximum metrics to return

**Response:**
```json
{
  "operation": "document_processing",
  "metrics_count": 45,
  "statistics": {
    "operation": "document_processing",
    "count": 45,
    "min_ms": 245.3,
    "max_ms": 5840.2,
    "mean_ms": 1250.5,
    "error_rate": 0.02,
    "success_count": 44,
    "error_count": 1
  },
  "metrics": [...]
}
```

**All Operations:**
```json
{
  "operations_monitored": 3,
  "statistics": {
    "document_processing": {...},
    "ocr_extraction": {...},
    "validation": {...}
  }
}
```

---

### 2. **GET /api/alerts**
Get active alerts based on performance thresholds.

**Parameters:**
- `level` (optional): Filter by alert level (INFO, WARNING, CRITICAL)
- `limit` (optional, default: 50): Maximum alerts to return

**Response:**
```json
{
  "total_alerts": 3,
  "alerts": [
    {
      "alert_level": "WARNING",
      "title": "High Error Rate Detected",
      "message": "Operation 'document_processing' has error rate of 5.0%",
      "timestamp": "2025-11-23T15:30:45.123456",
      "threshold_value": 0.05,
      "current_value": 0.05,
      "affected_metric": "document_processing.error_rate"
    },
    {
      "alert_level": "CRITICAL",
      "title": "High Number of Failed Requests",
      "message": "Operation 'validation' has 15 failed requests",
      "timestamp": "2025-11-23T15:25:10.654321",
      "threshold_value": 10.0,
      "current_value": 15.0,
      "affected_metric": "validation.error_count"
    }
  ],
  "thresholds": {
    "error_rate": 0.05,
    "response_time_ms": 5000,
    "failed_requests": 10,
    "memory_threshold_mb": 1024
  }
}
```

---

### 3. **GET /api/audit-logs**
Retrieve audit logs for compliance and security review.

**Parameters:**
- `category` (optional): Filter by category (AUTHENTICATION, AUTHORIZATION, DATA_ACCESS, etc.)
- `actor` (optional): Filter by actor/user
- `start_date` (optional): Start date (ISO format)
- `end_date` (optional): End date (ISO format)
- `limit` (optional, default: 100): Maximum logs to return

**Response:**
```json
{
  "total_events": 42,
  "filters_applied": {
    "category": "AUTHENTICATION",
    "actor": null,
    "start_date": null,
    "end_date": null
  },
  "events": [
    {
      "event_id": "EVT_20251123150010_ABC12345",
      "timestamp": "2025-11-23T15:00:10.123456",
      "category": "AUTHENTICATION",
      "action": "AUTHENTICATION_ATTEMPT",
      "actor": "user@example.com",
      "resource": "/api/upload",
      "result": "SUCCESS",
      "ip_address": "192.168.1.100",
      "session_id": "sess_20251123_abc123",
      "severity": "INFO",
      "details": {}
    },
    {
      "event_id": "EVT_20251123145530_XYZ98765",
      "timestamp": "2025-11-23T14:55:30.654321",
      "category": "AUTHORIZATION",
      "action": "AUTHORIZATION_CHECK",
      "actor": "user@example.com",
      "resource": "document_456",
      "result": "DENIED",
      "ip_address": "192.168.1.100",
      "severity": "WARNING",
      "details": {"permission": "ADMIN"}
    }
  ]
}
```

---

### 4. **GET /api/monitoring-status**
Get overall monitoring and audit status.

**Response:**
```json
{
  "system_health": {
    "timestamp": "2025-11-23T15:30:45.123456",
    "redis_connected": true,
    "total_metrics_recorded": 1234,
    "total_audit_entries": 5678,
    "active_sessions": 12,
    "active_alerts": 3,
    "operations_monitored": 5
  },
  "recent_alerts": [
    {
      "alert_level": "WARNING",
      "title": "High Error Rate Detected",
      "message": "Operation 'document_processing' has error rate of 5.0%",
      "timestamp": "2025-11-23T15:30:45.123456",
      "threshold_value": 0.05,
      "current_value": 0.05,
      "affected_metric": "document_processing.error_rate"
    }
  ],
  "recent_audit_events": [...],
  "timestamp": "2025-11-23T15:30:45.123456"
}
```

---

## 🔧 Integration Examples

### Example 1: Track Document Processing Request

```python
from shared.monitoring_service import get_monitoring_service, track_request

monitoring = get_monitoring_service()

# Create session
session_id = monitoring.create_session(user_id="user@example.com")

# Start tracking
request_id = monitoring.start_request(session_id, "/api/process-document", "POST")

try:
    # Your processing logic
    start = time.time()
    result = process_document(doc_data)
    duration_ms = (time.time() - start) * 1000
    
    # Complete successfully
    monitoring.complete_request(
        session_id, request_id, "/api/process-document",
        duration_ms=duration_ms, success=True
    )
    
    return {"status": "success", "result": result}

except Exception as e:
    duration_ms = (time.time() - start) * 1000
    
    # Complete with error
    monitoring.complete_request(
        session_id, request_id, "/api/process-document",
        duration_ms=duration_ms, success=False,
        error_msg=str(e)
    )
    
    raise

finally:
    # End session
    monitoring.end_session(session_id)
```

### Example 2: Using Decorators for Automatic Tracking

```python
from shared.monitoring_service import track_request, performance_timer

# Track entire request
@track_request("/api/upload", "POST")
def handle_upload(req, session_id):
    return process_upload(req)

# Track operation performance
@performance_timer("ocr_extraction")
def extract_text_from_image(image_data, items=None):
    return ocr_service.extract(image_data)

# Use with session tracking
session_id = get_monitoring_service().create_session()
result = handle_upload(request, session_id=session_id)
```

### Example 3: Log Security Events

```python
from shared.audit_logger import get_audit_logger

audit = get_audit_logger()

# Log login attempt
audit.log_authentication(
    actor=username,
    resource="/api/upload",
    result="SUCCESS" if authenticated else "FAILURE",
    session_id=session_id,
    ip_address=request.remote_addr,
    error_msg="Invalid credentials" if not authenticated else None
)

# Log access denial
if not has_permission:
    audit.log_authorization(
        actor=username,
        resource=document_id,
        permission="WRITE",
        result="DENIED",
        ip_address=request.remote_addr
    )

# Log data export
audit.log_data_access(
    actor=username,
    resource="reports_table",
    operation="EXPORT",
    result="SUCCESS",
    record_count=1500
)
```

### Example 4: Generate Compliance Report

```python
from shared.audit_logger import get_audit_logger
from datetime import datetime, timedelta
import json

audit = get_audit_logger()

# Monthly report
today = datetime.utcnow()
month_start = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(seconds=1)

report = audit.generate_compliance_report(month_start, month_end)

# Generate report file
with open(f"compliance_report_{today.strftime('%Y%m%d')}.json", "w") as f:
    json.dump(report, f, indent=2)

# Failed authentications in last 24 hours
failed_auths = audit.get_failed_authentications(hours=24)
print(f"Failed login attempts: {len(failed_auths)}")

for event in failed_auths:
    print(f"  - {event.actor} from {event.ip_address} at {event.timestamp}")
```

### Example 5: Monitor Thresholds and Alerts

```python
from shared.monitoring_service import get_monitoring_service

monitoring = get_monitoring_service()

# Adjust thresholds for stricter monitoring
monitoring.set_threshold("error_rate", 0.02)              # 2% instead of 5%
monitoring.set_threshold("response_time_ms", 3000)        # 3s instead of 5s

# Check for alerts
alerts = monitoring.check_thresholds_and_generate_alerts()

# Send notifications for critical alerts
for alert in alerts:
    if alert.alert_level == AlertLevel.CRITICAL:
        send_email_alert(
            subject=alert.title,
            body=alert.message,
            recipients=["admin@example.com"]
        )
    else:
        log_to_monitoring_system(alert)

# View active alerts
current_alerts = monitoring.get_active_alerts(limit=20)
```

---

## 📊 Monitoring Dashboard Queries

### Query 1: Get Operation Performance Summary

```python
def get_performance_summary():
    monitoring = get_monitoring_service()
    
    summary = {}
    for op_name in monitoring.metrics_store.keys():
        stats = monitoring.get_metric_statistics(op_name)
        summary[op_name] = {
            "total_calls": stats['count'],
            "success_rate": 1 - stats['error_rate'],
            "avg_response_ms": stats['mean_ms'],
            "p95_response_ms": stats['max_ms'],  # Approximation
            "error_count": stats['error_count']
        }
    
    return summary
```

### Query 2: Find Problem Operations

```python
def find_problem_operations(error_threshold=0.05, response_time_threshold=5000):
    monitoring = get_monitoring_service()
    problems = {}
    
    for op_name in monitoring.metrics_store.keys():
        stats = monitoring.get_metric_statistics(op_name)
        
        issues = []
        if stats['error_rate'] > error_threshold:
            issues.append(f"High error rate: {stats['error_rate']:.1%}")
        if stats['mean_ms'] > response_time_threshold:
            issues.append(f"Slow response: {stats['mean_ms']:.0f}ms avg")
        
        if issues:
            problems[op_name] = {
                "issues": issues,
                "stats": stats
            }
    
    return problems
```

### Query 3: Audit Trail Search

```python
def search_user_actions(username, days=7):
    audit = get_audit_logger()
    
    start = datetime.utcnow() - timedelta(days=days)
    
    events = audit.get_events(
        start_time=start,
        actor=username,
        limit=1000
    )
    
    # Group by action type
    by_action = {}
    for event in events:
        if event.action not in by_action:
            by_action[event.action] = []
        by_action[event.action].append({
            "time": event.timestamp,
            "resource": event.resource,
            "result": event.result
        })
    
    return by_action
```

---

## 🔐 Security Considerations

1. **Immutable Audit Trail**: Events cannot be modified, only viewed
2. **Compliance Retention**: Critical events retained for 2 years per regulatory requirements
3. **Session Isolation**: Each session has unique ID for request correlation
4. **Performance Metrics**: Separate storage to prevent tampering with audit logs
5. **Error Handling**: All sensitive information logged securely
6. **Redis Encryption**: In production, use Redis with TLS/SSL

---

## 📈 Deployment Checklist

- [ ] Configure Redis connection string in environment
- [ ] Set appropriate retention policies
- [ ] Configure alert thresholds based on baselines
- [ ] Set up email alerts for CRITICAL alerts
- [ ] Enable Azure Table Storage for audit persistence
- [ ] Configure backup strategy for audit logs
- [ ] Set up monitoring dashboard
- [ ] Train team on audit log review
- [ ] Document custom thresholds
- [ ] Set up compliance report generation schedule

---

## 🧪 Testing

```bash
# Test metrics collection
curl http://localhost:7071/api/metrics

# Test alerts
curl http://localhost:7071/api/alerts?level=WARNING

# Test audit logs
curl http://localhost:7071/api/audit-logs?category=AUTHENTICATION

# Test monitoring status
curl http://localhost:7071/api/monitoring-status
```

---

## 📝 Next Steps

1. Integrate monitoring into all API endpoints
2. Set up Grafana dashboard for visualization
3. Configure email/Slack alerts
4. Implement automatic report generation
5. Set up compliance export functionality
6. Add performance trending analysis
