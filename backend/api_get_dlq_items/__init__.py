import azure.functions as func
import json
import logging
from ..shared import table_service

def main(req: func.HttpRequest) -> func.HttpResponse:
    """Get DLQ items"""
    logging.info('Fetching DLQ items')
    
    try:
        # Get status from query parameters (optional)
        status = req.params.get('status', 'PENDING_REVIEW')
        
        # Get DLQ items
        dlq_items = table_service.get_dlq_items(status=status)
        
        return func.HttpResponse(
            json.dumps({
                "success": True,
                "count": len(dlq_items),
                "status": status,
                "items": dlq_items
            }),
            mimetype="application/json",
            status_code=200
        )
    except Exception as e:
        logging.error(f"Error fetching DLQ items: {str(e)}")
        return func.HttpResponse(
            json.dumps({
                "success": False,
                "error": str(e)
            }),
            mimetype="application/json",
            status_code=500
        )

