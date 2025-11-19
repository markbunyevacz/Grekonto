import os
import json
import logging
from azure.data.tables import TableClient
from azure.core.exceptions import ResourceExistsError

TABLE_NAME = "tasks"
CONN_STR = os.getenv("AzureWebJobsStorage")

def get_table_client():
    if not CONN_STR:
        logging.warning("AzureWebJobsStorage not found. Using mock client if needed or failing.")
        return None
    
    client = TableClient.from_connection_string(conn_str=CONN_STR, table_name=TABLE_NAME)
    try:
        client.create_table()
    except ResourceExistsError:
        pass
    return client

def save_task(task_data):
    """
    Saves a task to the Table Storage.
    task_data should contain 'id' (RowKey), 'status', 'extracted', 'match_candidate', etc.
    PartitionKey will be 'invoice_task'.
    """
    client = get_table_client()
    if not client:
        return

    entity = {
        "PartitionKey": "invoice_task",
        "RowKey": task_data["id"],
        "Status": task_data["status"],
        "Confidence": task_data.get("confidence", 0),
        "DocumentUrl": task_data.get("document_url", ""),
        "ExtractedData": json.dumps(task_data.get("extracted", {})),
        "MatchCandidate": json.dumps(task_data.get("match_candidate", {})) if task_data.get("match_candidate") else None
    }

    try:
        client.upsert_entity(entity)
        logging.info(f"Task {task_data['id']} saved to table.")
    except Exception as e:
        logging.error(f"Failed to save task to table: {str(e)}")

def get_pending_tasks():
    """
    Retrieves all tasks with status YELLOW or RED.
    """
    client = get_table_client()
    if not client:
        return []

    tasks = []
    try:
        # Filter for tasks that are not completed (Green/Approved/Rejected)
        # For simplicity, let's just get everything and filter in code or use a query
        # Query: Status eq 'YELLOW' or Status eq 'RED'
        parameters = {"status1": "YELLOW", "status2": "RED"}
        filter_query = "Status eq @status1 or Status eq @status2"
        
        entities = client.query_entities(query_filter=filter_query, parameters=parameters)

        for entity in entities:
            tasks.append({
                "id": entity["RowKey"],
                "status": entity["Status"],
                "confidence": entity.get("Confidence", 0),
                "document_url": entity.get("DocumentUrl", ""),
                "extracted": json.loads(entity.get("ExtractedData", "{}")),
                "match_candidate": json.loads(entity.get("MatchCandidate", "{}")) if entity.get("MatchCandidate") else None
            })
    except Exception as e:
        logging.error(f"Failed to query tasks: {str(e)}")
    
    return tasks

def update_task_status(task_id, new_status):
    """
    Updates the status of a task.
    """
    client = get_table_client()
    if not client:
        return

    try:
        entity = client.get_entity(partition_key="invoice_task", row_key=task_id)
        entity["Status"] = new_status
        client.update_entity(entity)
        logging.info(f"Task {task_id} status updated to {new_status}.")
    except Exception as e:
        logging.error(f"Failed to update task {task_id}: {str(e)}")
        raise e
