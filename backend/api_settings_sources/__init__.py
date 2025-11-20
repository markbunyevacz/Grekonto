import azure.functions as func
import json
import logging
from ..shared import table_service

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request for settings sources.')

    method = req.method

    if method == "GET":
        try:
            sources = table_service.get_sources()
            return func.HttpResponse(
                json.dumps(sources),
                mimetype="application/json",
                status_code=200
            )
        except Exception as e:
            logging.error(f"Error fetching sources: {str(e)}")
            return func.HttpResponse(
                json.dumps({"error": str(e)}),
                mimetype="application/json",
                status_code=500
            )

    elif method == "POST":
        try:
            req_body = req.get_json()
            # Basic validation
            if not req_body.get('partner') or not req_body.get('server'):
                 return func.HttpResponse(
                    "Missing required fields",
                    status_code=400
                )
            
            source_id = table_service.save_source(req_body)
            return func.HttpResponse(
                json.dumps({"id": source_id, "message": "Source saved successfully"}),
                mimetype="application/json",
                status_code=200
            )
        except ValueError:
            return func.HttpResponse(
                 "Invalid body",
                 status_code=400
            )
        except Exception as e:
            logging.error(f"Error saving source: {str(e)}")
            return func.HttpResponse(
                json.dumps({"error": str(e)}),
                mimetype="application/json",
                status_code=500
            )
    
    return func.HttpResponse(
        "Method not allowed",
        status_code=405
    )
