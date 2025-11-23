import azure.functions as func
import json
import logging
from ..shared.monitoring_service import get_monitoring_service, AlertLevel

def main(req: func.HttpRequest) -> func.HttpResponse:
    """
    Get active alerts based on performance thresholds.
    
    Query parameters:
    - level: Filter by alert level (INFO, WARNING, CRITICAL)
    - limit: Maximum alerts to return (default: 50)
    
    Returns:
    - List of alerts with details about threshold violations
    """
    logging.info('Retrieving active alerts')
    
    try:
        monitoring = get_monitoring_service()
        
        # Check thresholds and generate alerts
        monitoring.check_thresholds_and_generate_alerts()
        
        # Get alerts
        limit = int(req.params.get('limit', 50))
        level_filter = req.params.get('level')
        
        all_alerts = monitoring.get_active_alerts(limit * 2)  # Get more to filter
        
        # Filter by level if specified
        if level_filter:
            try:
                alert_level = AlertLevel[level_filter]
                filtered_alerts = [a for a in all_alerts 
                                  if a['alert_level'] == alert_level.value]
            except KeyError:
                return func.HttpResponse(
                    json.dumps({"error": f"Invalid alert level: {level_filter}"}),
                    mimetype="application/json",
                    status_code=400
                )
        else:
            filtered_alerts = all_alerts
        
        return func.HttpResponse(
            json.dumps({
                "total_alerts": len(filtered_alerts),
                "alerts": filtered_alerts[:limit],
                "thresholds": monitoring.thresholds
            }),
            mimetype="application/json",
            status_code=200
        )
    
    except Exception as e:
        logging.error(f"Error retrieving alerts: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            mimetype="application/json",
            status_code=500
        )
