import azure.functions as func
import json
import logging
from ..shared import table_service

def main(req: func.HttpRequest) -> func.HttpResponse:
    """Resolve a DLQ item"""
    logging.info('Resolving DLQ item')
    
    try:
        # Get request body
        req_body = req.get_json()
        
        dlq_id = req_body.get('dlq_id')
        resolution_status = req_body.get('resolution_status', 'RESOLVED')
        resolution_notes = req_body.get('resolution_notes', '')
        
        if not dlq_id:
            return func.HttpResponse(
                json.dumps({
                    "success": False,
                    "error": "dlq_id is required"
                }),
                mimetype="application/json",
                status_code=400
            )
        
        # Resolve DLQ item
        success = table_service.resolve_dlq_item(
            dlq_id=dlq_id,
            resolution_status=resolution_status,
            resolution_notes=resolution_notes
        )
        
        if success:
            # Log audit event
            table_service.log_audit_event(
                event_type="DLQ_ITEM_RESOLVED",
                message=f"DLQ item resolved: {dlq_id}",
                related_item_id=dlq_id
            )
            
            return func.HttpResponse(
                json.dumps({
                    "success": True,
                    "message": "DLQ item resolved"
                }),
                mimetype="application/json",
                status_code=200
            )
        else:
            return func.HttpResponse(
                json.dumps({
                    "success": False,
                    "error": "Failed to resolve DLQ item"
                }),
                mimetype="application/json",
                status_code=500
            )
    except Exception as e:
        logging.error(f"Error resolving DLQ item: {str(e)}")
        return func.HttpResponse(
            json.dumps({
                "success": False,
                "error": str(e)
            }),
            mimetype="application/json",
            status_code=500
        )

