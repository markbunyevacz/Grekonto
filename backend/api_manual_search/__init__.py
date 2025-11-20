import azure.functions as func
import json
import logging
from ..shared import table_service

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request for manual search.')

    query = req.params.get('q')
    
    if not query:
        return func.HttpResponse(
             "Please pass a query string 'q'",
             status_code=400
        )

    try:
        results = table_service.search_candidates(query)
        return func.HttpResponse(
            json.dumps(results),
            mimetype="application/json",
            status_code=200
        )
    except Exception as e:
        logging.error(f"Error searching: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            mimetype="application/json",
            status_code=500
        )
