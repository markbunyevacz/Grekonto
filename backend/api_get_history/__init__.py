import azure.functions as func
import logging
import json
from ..shared import table_service

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request to get history.')

    try:
        logs = table_service.get_audit_logs(limit=50)
        return func.HttpResponse(
            json.dumps(logs),
            mimetype="application/json",
            status_code=200
        )
    except Exception as e:
        logging.error(f"Error fetching history: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            mimetype="application/json",
            status_code=500
        )
