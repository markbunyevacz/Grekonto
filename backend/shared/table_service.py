import os
import logging
import json
import datetime
from azure.data.tables import TableServiceClient, TableClient
from azure.core.exceptions import ResourceNotFoundError

def get_table_service_client():
    """Get Azure Table Service Client"""
    connect_str = os.getenv('AzureWebJobsStorage')
    if not connect_str or connect_str == "UseDevelopmentStorage=true":
        logging.warning("Using Azurite development storage for tables")
        # Full Azurite connection string for local development
        connect_str = "DefaultEndpointsProtocol=http;AccountName=devstoreaccount1;AccountKey=Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw==;BlobEndpoint=http://127.0.0.1:10000/devstoreaccount1;QueueEndpoint=http://127.0.0.1:10001/devstoreaccount1;TableEndpoint=http://127.0.0.1:10002/devstoreaccount1;"

    return TableServiceClient.from_connection_string(connect_str)

def get_table_client(table_name="Tasks"):
    """Get a specific table client"""
    try:
        service_client = get_table_service_client()
        table_client = service_client.get_table_client(table_name)

        # Create table if it doesn't exist
        try:
            service_client.create_table(table_name)
            logging.info(f"Created table: {table_name}")
        except:
            pass  # Table already exists

        return table_client
    except Exception as e:
        logging.error(f"Error getting table client: {str(e)}")
        return None

def get_task_partition_key(task_id):
    """Generate partition key for a task"""
    # Simple partitioning by date prefix or just use a constant for PoC
    return "TASKS"

def save_task(task_data):
    """Save a task to Table Storage"""
    client = get_table_client("Tasks")
    if not client:
        logging.error("Could not get table client")
        return

    try:
        entity = {
            "PartitionKey": get_task_partition_key(task_data['id']),
            "RowKey": task_data['id'],
            "Status": task_data['status'],
            "Confidence": task_data.get('confidence', 0),
            "DocumentUrl": task_data.get('document_url', ''),
            "ExtractedData": json.dumps(task_data.get('extracted', {})),
            "MatchCandidate": json.dumps(task_data.get('match_candidate', {})) if task_data.get('match_candidate') else '',
            "CreatedAt": task_data.get('created_at', datetime.datetime.utcnow().isoformat())
        }

        client.upsert_entity(entity)
        logging.info(f"Task {task_data['id']} saved successfully")
    except Exception as e:
        logging.error(f"Error saving task: {str(e)}")
        raise e

def get_pending_tasks():
    """Get all pending tasks (YELLOW or RED status)"""
    client = get_table_client("Tasks")
    if not client:
        return []

    try:
        # Query for tasks with YELLOW or RED status
        filter_query = "Status eq 'YELLOW' or Status eq 'RED'"
        entities = client.query_entities(filter_query)

        tasks = []
        for entity in entities:
            try:
                extracted = json.loads(entity.get("ExtractedData", "{}"))
                match_candidate = json.loads(entity.get("MatchCandidate", "{}")) if entity.get("MatchCandidate") else None

                tasks.append({
                    "id": entity["RowKey"],
                    "status": entity.get("Status", "UNKNOWN"),
                    "confidence": entity.get("Confidence", 0),
                    "document_url": entity.get("DocumentUrl", ""),
                    "extracted": extracted,
                    "match_candidate": match_candidate,
                    "created_at": entity.get("CreatedAt", "")
                })
            except Exception as e:
                logging.error(f"Error parsing task entity: {str(e)}")
                continue

        logging.info(f"Retrieved {len(tasks)} pending tasks")
        return tasks
    except Exception as e:
        logging.error(f"Error fetching pending tasks: {str(e)}")
        return []

def update_task_status(task_id, new_status, match_candidate=None):
    """
    Updates the status of a task.
    If match_candidate is provided, it updates that too.
    """
    client = get_table_client()
    if not client:
        return

    pk = get_task_partition_key(task_id)

    try:
        entity = client.get_entity(partition_key=pk, row_key=task_id)
        entity["Status"] = new_status

        if match_candidate:
             entity["MatchCandidate"] = json.dumps(match_candidate)

        client.update_entity(entity)
        logging.info(f"Task {task_id} status updated to {new_status}.")
    except Exception as e:
        logging.error(f"Failed to update task {task_id}: {str(e)}")
        raise e

def log_audit_event(event_type, message, related_item_id="", client_name=""):
    """Log an audit event to Table Storage"""
    client = get_table_client("AuditLogs")
    if not client:
        return

    try:
        timestamp = datetime.datetime.utcnow()
        entity = {
            "PartitionKey": timestamp.strftime("%Y%m%d"),
            "RowKey": f"{timestamp.isoformat()}_{event_type}",
            "EventType": event_type,
            "Message": message,
            "RelatedItemId": related_item_id,
            "ClientName": client_name,
            "Timestamp": timestamp.isoformat()
        }

        client.upsert_entity(entity)
        logging.info(f"Audit event logged: {event_type}")
    except Exception as e:
        logging.error(f"Error logging audit event: {str(e)}")

def get_audit_logs(limit=50):
    """Get recent audit logs"""
    client = get_table_client("AuditLogs")
    if not client:
        return []

    try:
        entities = list(client.list_entities())
        # Sort by timestamp descending
        entities.sort(key=lambda x: x.get("Timestamp", ""), reverse=True)
        entities = entities[:limit]

        logs = []
        for entity in entities:
            logs.append({
                "time": entity.get("Timestamp", ""),
                "file": entity.get("RelatedItemId", ""),
                "client": entity.get("ClientName", ""),
                "result": entity.get("EventType", ""),
                "user": "System",
                "message": entity.get("Message", "")
            })

        return logs
    except Exception as e:
        logging.error(f"Error fetching audit logs: {str(e)}")
        return []

def check_duplicate_invoice(vendor_tax_id, invoice_id):
    """Check if an invoice has already been processed"""
    if not vendor_tax_id or not invoice_id:
        return False

    client = get_table_client("ProcessedInvoices")
    if not client:
        return False

    try:
        pk = vendor_tax_id
        rk = invoice_id

        entity = client.get_entity(partition_key=pk, row_key=rk)
        return True  # Found duplicate
    except ResourceNotFoundError:
        # Not a duplicate, save it
        try:
            entity = {
                "PartitionKey": pk,
                "RowKey": rk,
                "ProcessedAt": datetime.datetime.utcnow().isoformat()
            }
            client.upsert_entity(entity)
        except:
            pass
        return False
    except Exception as e:
        logging.error(f"Error checking duplicate: {str(e)}")
        return False

def get_sources():
    """Get configured data sources"""
    client = get_table_client("DataSources")
    if not client:
        return []

    try:
        entities = client.list_entities()
        sources = []
        for entity in entities:
            sources.append({
                "id": entity["RowKey"],
                "partner": entity.get("Partner", ""),
                "server": entity.get("Server", ""),
                "port": entity.get("Port", ""),
                "user": entity.get("User", ""),
                "password": entity.get("Password", ""),
                "type": entity.get("Type", "email")
            })
        return sources
    except Exception as e:
        logging.error(f"Error fetching sources: {str(e)}")
        return []

def save_source(source_data):
    """Save a data source configuration"""
    client = get_table_client("DataSources")
    if not client:
        return False

    try:
        entity = {
            "PartitionKey": "SOURCES",
            "RowKey": source_data.get('partner', datetime.datetime.utcnow().isoformat()),
            "Partner": source_data.get('partner', ''),
            "Server": source_data.get('server', ''),
            "Port": source_data.get('port', '993'),
            "User": source_data.get('user', ''),
            "Password": source_data.get('password', ''),
            "Type": source_data.get('type', 'email')
        }

        client.upsert_entity(entity)
        logging.info(f"Source saved: {source_data.get('partner')}")
        return True
    except Exception as e:
        logging.error(f"Error saving source: {str(e)}")
        return False

def search_candidates(query):
    """Search for matching candidates (mock implementation for now)"""
    # This would query the AOC system or cached NAV data
    # For now, return empty list
    logging.info(f"Searching for candidates with query: {query}")
    return []

def update_processing_status(file_id, stage, status, message="", error=None):
    """
    Update processing status for a file
    Stages: UPLOADED, OCR_STARTED, OCR_COMPLETED, MATCHING_STARTED, MATCHING_COMPLETED, COMPLETED, FAILED
    Status: IN_PROGRESS, SUCCESS, ERROR
    """
    client = get_table_client("ProcessingStatus")
    if not client:
        return

    try:
        timestamp = datetime.datetime.utcnow().isoformat()

        # Try to get existing entity
        try:
            entity = client.get_entity(partition_key="STATUS", row_key=file_id)
        except:
            # Create new entity
            entity = {
                "PartitionKey": "STATUS",
                "RowKey": file_id,
                "FileName": file_id,
                "StartedAt": timestamp,
                "Stages": "[]"
            }

        # Parse existing stages
        stages = json.loads(entity.get("Stages", "[]"))

        # Add new stage
        stage_entry = {
            "stage": stage,
            "status": status,
            "message": message,
            "timestamp": timestamp
        }

        if error:
            stage_entry["error"] = str(error)
            logging.error(f"[{file_id}] {stage} - ERROR: {error}")
        else:
            logging.info(f"[{file_id}] {stage} - {status}: {message}")

        stages.append(stage_entry)

        # Update entity
        entity["Stages"] = json.dumps(stages)
        entity["CurrentStage"] = stage
        entity["CurrentStatus"] = status
        entity["LastUpdated"] = timestamp

        if status == "ERROR":
            entity["OverallStatus"] = "FAILED"
            entity["ErrorMessage"] = message
        elif stage == "COMPLETED":
            entity["OverallStatus"] = "COMPLETED"
        else:
            entity["OverallStatus"] = "IN_PROGRESS"

        client.upsert_entity(entity)

    except Exception as e:
        logging.error(f"Error updating processing status: {str(e)}")

def get_processing_status(file_id):
    """Get processing status for a file"""
    client = get_table_client("ProcessingStatus")
    if not client:
        return None

    try:
        entity = client.get_entity(partition_key="STATUS", row_key=file_id)

        return {
            "file_id": entity["RowKey"],
            "file_name": entity.get("FileName", ""),
            "overall_status": entity.get("OverallStatus", "UNKNOWN"),
            "current_stage": entity.get("CurrentStage", ""),
            "current_status": entity.get("CurrentStatus", ""),
            "started_at": entity.get("StartedAt", ""),
            "last_updated": entity.get("LastUpdated", ""),
            "error_message": entity.get("ErrorMessage", ""),
            "stages": json.loads(entity.get("Stages", "[]"))
        }
    except Exception as e:
        logging.error(f"Error getting processing status: {str(e)}")
        return None
