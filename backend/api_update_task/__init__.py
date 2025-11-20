import azure.functions as func
import json
import logging
from ..shared import table_service

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request to update task status.')

    task_id = req.route_params.get('id')
    
    try:
        req_body = req.get_json()
        new_status = req_body.get('status')
    except ValueError:
        return func.HttpResponse(
             "Invalid body",
             status_code=400
        )

    if not task_id or not new_status:
        return func.HttpResponse(
             "Please pass a task ID in the route and status in the request body",
             status_code=400
        )

    try:
        table_service.update_task_status(task_id, new_status)
        return func.HttpResponse(
            json.dumps({"message": "Status updated successfully"}),
            mimetype="application/json",
            status_code=200
        )
    except Exception as e:
        logging.error(f"Error updating task: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            mimetype="application/json",
            status_code=500
        )
