import os
import logging
import json
import datetime
from azure.data.tables import TableServiceClient, TableClient
from azure.core.exceptions import ResourceNotFoundError, ResourceExistsError

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

def send_to_dlq(file_id, blob_name, error_message, stage, extracted_data=None):
    """Send failed document to Dead Letter Queue
    
    Implements de-duplication: checks if an entry already exists for this file_id
    to prevent duplicate entries from retries.
    
    Returns:
        tuple: (success: bool, is_new_entry: bool)
        - success: Whether the operation succeeded
        - is_new_entry: True if a new entry was created, False if existing entry was updated
    """
    client = get_table_client("DeadLetterQueue")
    if not client:
        logging.error("Could not get DLQ table client")
        return (False, False)

    try:
        # Validate and sanitize file_id to prevent injection attacks
        # file_id should not contain characters that could break RowKey lookup
        # RowKey in Azure Table Storage has restrictions, but we'll validate anyway
        if not file_id or not isinstance(file_id, str):
            logging.error(f"Invalid file_id provided: {file_id}")
            return (False, False)
        
        # Sanitize file_id: remove or escape problematic characters
        # Azure Table Storage RowKey cannot contain: / \ # ? 
        # But since we're using get_entity (not query), we just need to ensure
        # it's a valid string. However, for defense in depth, we validate it.
        sanitized_file_id = file_id.replace("/", "_").replace("\\", "_").replace("#", "_").replace("?", "_")
        if sanitized_file_id != file_id:
            logging.warning(
                f"file_id contained invalid characters, sanitized: "
                f"{file_id} -> {sanitized_file_id}"
            )
            file_id = sanitized_file_id
        
        # Use file_id as RowKey for atomic de-duplication
        # Try to get existing entity first (atomic check-and-create)
        try:
            existing_entity = client.get_entity(partition_key="DLQ", row_key=file_id)
            # Entity exists, update it instead of creating duplicate
            existing_entity["ErrorMessage"] = error_message
            existing_entity["FailedStage"] = stage
            existing_entity["ExtractedData"] = json.dumps(extracted_data or {})
            existing_entity["LastUpdated"] = datetime.datetime.utcnow().isoformat()
            
            client.update_entity(existing_entity)
            logging.info(f"Updated existing DLQ entry for file_id: {file_id}")
            return (True, False)  # Success, but not a new entry
        except Exception as get_error:
            # Entity doesn't exist (or other error), create new one
            # Check if it's a "not found" error vs other error
            if isinstance(get_error, ResourceNotFoundError):
                # Entity doesn't exist, create new one
                timestamp = datetime.datetime.utcnow()
                entity = {
                    "PartitionKey": "DLQ",
                    "RowKey": file_id,  # Use file_id as RowKey for de-duplication
                    "FileId": file_id,
                    "BlobName": blob_name,
                    "ErrorMessage": error_message,
                    "FailedStage": stage,
                    "ExtractedData": json.dumps(extracted_data or {})
                    "CreatedAt": timestamp.isoformat(),
                    "Status": "PENDING_REVIEW",
                    "RetryCount": 3
                }
                try:
                    client.create_entity(entity)
                    logging.info(f"Document sent to DLQ: {file_id}")
                    return (True, True)  # Success, new entry created
                except ResourceExistsError:
                    # Race condition: another instance created it between get and create
                    # Try to update the now-existing entity
                    try:
                        existing_entity = client.get_entity(
                            partition_key="DLQ", 
                            row_key=file_id
                        )
                        existing_entity["ErrorMessage"] = error_message
                        existing_entity["FailedStage"] = stage
                        existing_entity["ExtractedData"] = json.dumps(extracted_data or {})
                        existing_entity["LastUpdated"] = datetime.datetime.utcnow().isoformat()
                        client.update_entity(existing_entity)
                        logging.info(
                            f"Race condition handled: Updated existing DLQ entry "
                            f"for file_id: {file_id}"
                        )
                        return (True, False)  # Success, but not a new entry
                    except Exception as update_error:
                        logging.error(
                            f"Error updating DLQ entry after race condition: "
                            f"{update_error}"
                        )
                        return (False, False)
            else:
                # Some other error occurred
                raise get_error
        
    except Exception as e:
        logging.error(f"Error sending to DLQ: {str(e)}")
        return (False, False)

def get_dlq_items(status="PENDING_REVIEW"):
    """Get items from Dead Letter Queue
    
    Args:
        status: Status to filter by. Must be one of: PENDING_REVIEW, RESOLVED, REPROCESSED
                Input is validated to prevent OData injection attacks.
    """
    client = get_table_client("DeadLetterQueue")
    if not client:
        return []

    try:
        # Validate status to prevent OData injection
        # Only allow predefined status values
        allowed_statuses = ["PENDING_REVIEW", "RESOLVED", "REPROCESSED"]
        if status not in allowed_statuses:
            logging.warning(
                f"Invalid status '{status}' provided. "
                f"Using default 'PENDING_REVIEW'"
            )
            status = "PENDING_REVIEW"
        
        # Escape single quotes in status (defense in depth)
        # Azure Table Storage OData requires single quotes to be doubled
        escaped_status = status.replace("'", "''")
        filter_query = f"Status eq '{escaped_status}'"
        entities = client.query_entities(filter_query)

        dlq_items = []
        for entity in entities:
            try:
                extracted_data = json.loads(entity.get("ExtractedData", "{}"))
                dlq_items.append({
                    "id": entity["RowKey"],
                    "file_id": entity.get("FileId"),
                    "blob_name": entity.get("BlobName"),
                    "error": entity.get("ErrorMessage"),
                    "stage": entity.get("FailedStage"),
                    "created_at": entity.get("CreatedAt"),
                    "status": entity.get("Status"),
                    "retry_count": entity.get("RetryCount", 0),
                    "extracted_data": extracted_data
                })
            except Exception as e:
                logging.error(f"Error parsing DLQ entity: {str(e)}")
                continue

        logging.info(f"Retrieved {len(dlq_items)} DLQ items with status {status}")
        return dlq_items
    except Exception as e:
        logging.error(f"Error fetching DLQ items: {str(e)}")
        return []

def resolve_dlq_item(dlq_id, resolution_status, resolution_notes=""):
    """Resolve a DLQ item (mark as resolved or reprocessed)
    
    Args:
        dlq_id: The DLQ item ID (RowKey). Must be a valid string.
        resolution_status: Status to set. Must be one of: RESOLVED, REPROCESSED
        resolution_notes: Optional notes about the resolution
    """
    client = get_table_client("DeadLetterQueue")
    if not client:
        return False

    try:
        # Validate resolution_status to prevent injection
        allowed_statuses = ["RESOLVED", "REPROCESSED"]
        if resolution_status not in allowed_statuses:
            logging.error(
                f"Invalid resolution_status '{resolution_status}'. "
                f"Must be one of: {allowed_statuses}"
            )
            return False
        
        # Validate and sanitize dlq_id
        if not dlq_id or not isinstance(dlq_id, str):
            logging.error(f"Invalid dlq_id provided: {dlq_id}")
            return False
        
        # Sanitize dlq_id (defense in depth)
        sanitized_dlq_id = dlq_id.replace("/", "_").replace("\\", "_").replace("#", "_").replace("?", "_")
        if sanitized_dlq_id != dlq_id:
            logging.warning(
                f"dlq_id contained invalid characters, sanitized: "
                f"{dlq_id} -> {sanitized_dlq_id}"
            )
            dlq_id = sanitized_dlq_id
        
        # Sanitize resolution_notes (escape single quotes if used in queries later)
        # For now, just limit length to prevent abuse
        if resolution_notes and len(resolution_notes) > 1000:
            logging.warning("resolution_notes too long, truncating")
            resolution_notes = resolution_notes[:1000]
        
        entity = client.get_entity(partition_key="DLQ", row_key=dlq_id)
        entity["Status"] = resolution_status
        entity["ResolutionNotes"] = resolution_notes
        entity["ResolvedAt"] = datetime.datetime.utcnow().isoformat()

        client.update_entity(entity)
        logging.info(f"DLQ item {dlq_id} resolved with status {resolution_status}")
        return True
    except Exception as e:
        logging.error(f"Error resolving DLQ item: {str(e)}")
        return False
