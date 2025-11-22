import azure.functions as func
import json
import logging
from ..shared import table_service

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request to get processing status.')

    file_id = req.route_params.get('id')
    
    if not file_id:
        return func.HttpResponse(
             "Please pass a file ID in the route",
             status_code=400
        )

    try:
        status = table_service.get_processing_status(file_id)
        
        if not status:
            return func.HttpResponse(
                json.dumps({"error": "Status not found", "file_id": file_id}),
                mimetype="application/json",
                status_code=404
            )
        
        return func.HttpResponse(
            json.dumps(status),
            mimetype="application/json",
            status_code=200
        )
    except Exception as e:
        logging.error(f"Error fetching status: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            mimetype="application/json",
            status_code=500
        )

