import azure.functions as func
import json
import logging
from ..shared import table_service

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request to get tasks.')

    try:
        tasks = table_service.get_pending_tasks()
        
        # If no tasks found in table (e.g. first run), return mock data for demo purposes
        if not tasks:
             tasks = [
                {
                    "id": "task_1",
                    "status": "YELLOW",
                    "confidence": 90,
                    "document_url": "https://via.placeholder.com/400x600.png?text=Invoice+Image",
                    "extracted": {
                        "vendor": "MVM Next Zrt.",
                        "amount": 14200,
                        "currency": "HUF",
                        "date": "2024-11-15",
                        "invoice_id": "MVM-2024/888"
                    },
                    "match_candidate": {
                        "id": 101,
                        "vendor": "MVM Next Zrt.",
                        "amount": 14200,
                        "currency": "HUF",
                        "date": "2024-10-15", # Date mismatch
                        "reason": "Date mismatch (Oct vs Nov)"
                    }
                },
                {
                    "id": "task_2",
                    "status": "RED",
                    "confidence": 0,
                    "document_url": "https://via.placeholder.com/400x600.png?text=Unknown+Invoice",
                    "extracted": {
                        "vendor": "Unknown Vendor",
                        "amount": 500,
                        "currency": "EUR",
                        "date": "2024-11-18",
                        "invoice_id": "INV-999"
                    },
                    "match_candidate": None
                }
            ]

        return func.HttpResponse(
            json.dumps(tasks),
            mimetype="application/json",
            status_code=200
        )
    except Exception as e:
        logging.error(f"Error fetching tasks: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            mimetype="application/json",
            status_code=500
        )
