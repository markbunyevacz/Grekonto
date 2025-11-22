import azure.functions as func
import json
import logging
from ..shared import secret_rotation

def main(req: func.HttpRequest) -> func.HttpResponse:
    """Get secret rotation status"""
    logging.info('Fetching secret rotation status')
    
    try:
        # Get status of all secrets
        secrets_status = secret_rotation.get_all_secrets_status()
        
        # Count secrets that need rotation
        needs_rotation = sum(1 for s in secrets_status.values() if s['should_rotate'])
        
        return func.HttpResponse(
            json.dumps({
                "success": True,
                "secrets_checked": len(secrets_status),
                "needs_rotation": needs_rotation,
                "secrets": secrets_status
            }),
            mimetype="application/json",
            status_code=200
        )
    except Exception as e:
        logging.error(f"Error fetching secret status: {str(e)}")
        return func.HttpResponse(
            json.dumps({
                "success": False,
                "error": str(e)
            }),
            mimetype="application/json",
            status_code=500
        )

