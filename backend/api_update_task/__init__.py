import azure.functions as func
import json
import logging
from ..shared import table_service
from ..shared import storage_client
from ..shared.aoc_client import AOCClient

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request to update task status.')

    task_id = req.route_params.get('id')
    
    try:
        req_body = req.get_json()
        new_status = req_body.get('status')
        match_candidate = req_body.get('match_candidate') # New field
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
        # 1. Update Status in Table (and candidate if provided)
        table_service.update_task_status(task_id, new_status, match_candidate)
        
        # 2. If COMPLETED (Approved), try to upload to AOC
        if new_status == 'COMPLETED':
            try:
                client = table_service.get_table_client()
                pk = table_service.get_task_partition_key(task_id)
                entity = client.get_entity(partition_key=pk, row_key=task_id)
                
                extracted = json.loads(entity.get("ExtractedData", "{}"))
                
                # If match_candidate was passed in body, use it. 
                # table_service.update_task_status already saved it to DB, 
                # so getting from entity is safe, or use the local variable.
                candidate = json.loads(entity.get("MatchCandidate", "{}")) if entity.get("MatchCandidate") else {}
                
                document_url = entity.get("DocumentUrl")
                
                aoc_client = AOCClient()
                success = False
                
                # Logic: If we have a candidate (confirmed match), link it.
                match_id = candidate.get("id") or candidate.get("match_id")
                
                if match_id:
                    success = aoc_client.upload_invoice_link(str(match_id), document_url)
                
                if success:
                    logging.info(f"Manual approval: Successfully linked {task_id} to AOC invoice {match_id}")
                    table_service.log_audit_event(
                        event_type="MANUAL_APPROVAL_UPLOAD_SUCCESS",
                        message=f"Manually approved task uploaded to AOC.",
                        related_item_id=task_id,
                        client_name=extracted.get("vendor", "-")
                    )
                    # Zero Data Retention cleanup would happen here if we could reliably get the blob name.
                    # For now, we leave the blob or rely on a separate cleanup job.
                else:
                    logging.warning(f"Manual approval: Failed to link {task_id} to AOC (or no match_id).")

            except Exception as inner_e:
                logging.error(f"Error during AOC upload for manual approval: {inner_e}")
                # We don't fail the request because the status *was* updated.

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
