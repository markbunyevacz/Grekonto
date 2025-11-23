import azure.functions as func
import json
import logging
from ..shared.audit_logger import get_audit_logger, AuditCategory
from datetime import datetime, timedelta

def main(req: func.HttpRequest) -> func.HttpResponse:
    """
    Get audit logs for compliance and security review.
    
    Query parameters:
    - category: Filter by category (AUTHENTICATION, AUTHORIZATION, DATA_ACCESS, etc.)
    - actor: Filter by actor/user
    - start_date: Start date (ISO format, optional)
    - end_date: End date (ISO format, optional)
    - limit: Maximum logs to return (default: 100)
    
    Returns:
    - List of audit events
    """
    logging.info('Retrieving audit logs')
    
    try:
        audit_logger = get_audit_logger()
        
        # Parse parameters
        limit = int(req.params.get('limit', 100))
        actor = req.params.get('actor')
        category_str = req.params.get('category')
        start_date_str = req.params.get('start_date')
        end_date_str = req.params.get('end_date')
        
        # Parse dates
        start_date = None
        end_date = None
        
        if start_date_str:
            try:
                start_date = datetime.fromisoformat(start_date_str)
            except ValueError:
                return func.HttpResponse(
                    json.dumps({"error": f"Invalid start_date format: {start_date_str}"}),
                    mimetype="application/json",
                    status_code=400
                )
        
        if end_date_str:
            try:
                end_date = datetime.fromisoformat(end_date_str)
            except ValueError:
                return func.HttpResponse(
                    json.dumps({"error": f"Invalid end_date format: {end_date_str}"}),
                    mimetype="application/json",
                    status_code=400
                )
        
        # Parse category
        category = None
        if category_str:
            try:
                category = AuditCategory[category_str]
            except KeyError:
                return func.HttpResponse(
                    json.dumps({"error": f"Invalid category: {category_str}"}),
                    mimetype="application/json",
                    status_code=400
                )
        
        # Get events
        events = audit_logger.get_events(
            start_time=start_date,
            end_time=end_date,
            actor=actor,
            category=category,
            limit=limit
        )
        
        return func.HttpResponse(
            json.dumps({
                "total_events": len(events),
                "filters_applied": {
                    "category": category_str,
                    "actor": actor,
                    "start_date": start_date_str,
                    "end_date": end_date_str
                },
                "events": [e.to_dict() for e in events]
            }),
            mimetype="application/json",
            status_code=200
        )
    
    except Exception as e:
        logging.error(f"Error retrieving audit logs: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            mimetype="application/json",
            status_code=500
        )
