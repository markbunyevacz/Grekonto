import azure.functions as func
import json
import logging
from ..shared.monitoring_service import get_monitoring_service
from ..shared.audit_logger import get_audit_logger

def main(req: func.HttpRequest) -> func.HttpResponse:
    """
    Get overall monitoring and audit status.
    
    Returns:
    - System health metrics
    - Session statistics
    - Active alerts count
    - Recent audit events
    """
    logging.info('Retrieving monitoring status')
    
    try:
        monitoring = get_monitoring_service()
        audit_logger = get_audit_logger()
        
        # Get health status
        health = monitoring.get_health_status()
        
        # Get sample data
        recent_alerts = monitoring.get_active_alerts(limit=10)
        recent_audit_logs = audit_logger.get_events(limit=10)
        
        return func.HttpResponse(
            json.dumps({
                "system_health": health,
                "recent_alerts": recent_alerts,
                "recent_audit_events": [e.to_dict() for e in recent_audit_logs],
                "timestamp": health['timestamp']
            }),
            mimetype="application/json",
            status_code=200
        )
    
    except Exception as e:
        logging.error(f"Error retrieving monitoring status: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            mimetype="application/json",
            status_code=500
        )
