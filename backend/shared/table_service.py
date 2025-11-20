import os
import json
import logging
from azure.data.tables import TableClient
from azure.core.exceptions import ResourceExistsError
import uuid
import datetime

TABLE_NAME = "tasks"
AUDIT_TABLE_NAME = "auditlogs"
INDEX_TABLE_NAME = "invoiceindex"
TASK_INDEX_TABLE_NAME = "taskindex"
CONN_STR = os.getenv("AzureWebJobsStorage")

def get_table_client(table_name=TABLE_NAME):
    if not CONN_STR:
        logging.warning("AzureWebJobsStorage not found. Using mock client if needed or failing.")
        return None
    
    client = TableClient.from_connection_string(conn_str=CONN_STR, table_name=table_name)
    try:
        client.create_table()
    except ResourceExistsError:
        pass
    return client

def log_audit_event(event_type, message, user="System", related_item_id=None, client_name="-"):
    """
    Logs an event to the audit table.
    PartitionKey: YYYY-MM
    RowKey: Inverted Timestamp + UUID
    """
    client = get_table_client(AUDIT_TABLE_NAME)
    if not client:
        return

    now = datetime.datetime.utcnow()
    partition_key = now.strftime('%Y-%m')
    # Inverted timestamp for reverse chronological order
    inverted_time = (datetime.datetime.max - now).total_seconds()
    row_key = f"{inverted_time:020.6f}_{uuid.uuid4()}"

    entity = {
        "PartitionKey": partition_key,
        "RowKey": row_key,
        "EventTime": now,
        "EventType": event_type,
        "Message": message,
        "User": user,
        "RelatedItemId": related_item_id,
        "ClientName": client_name
    }

    try:
        client.create_entity(entity)
    except Exception as e:
        logging.error(f"Failed to log audit event: {str(e)}")

def get_audit_logs(limit=50):
    """
    Retrieves recent audit logs.
    """
    client = get_table_client(AUDIT_TABLE_NAME)
    if not client:
        return []

    logs = []
    try:
        # Query current month partition
        now = datetime.datetime.utcnow()
        partition_key = now.strftime('%Y-%m')
        
        # In a real app, we might need to query previous month if current is empty
        filter_query = f"PartitionKey eq '{partition_key}'"
        entities = client.query_entities(query_filter=filter_query)
        
        # Since we use inverted timestamp in RowKey, they come back sorted if we scan? 
        # Azure Table Storage returns in RowKey order.
        # So they should be latest first.
        
        count = 0
        for entity in entities:
            logs.append({
                "time": entity["EventTime"].strftime('%H:%M') if entity["EventTime"].date() == now.date() else entity["EventTime"].strftime('%Y-%m-%d %H:%M'),
                "file": entity.get("RelatedItemId", "-"),
                "client": entity.get("ClientName", "-"),
                "result": entity["EventType"],
                "user": entity["User"],
                "message": entity["Message"]
            })
            count += 1
            if count >= limit:
                break
                
    except Exception as e:
        logging.error(f"Error fetching audit logs: {str(e)}")
    
    return logs

def save_task_index(task_row_key, task_partition_key):
    """
    Saves an entry to the task index table for O(1) lookup by ID.
    PartitionKey: task_index
    RowKey: TaskID
    """
    client = get_table_client(TASK_INDEX_TABLE_NAME)
    if not client: return
    entity = {
        "PartitionKey": "task_index",
        "RowKey": task_row_key,
        "TaskPartitionKey": task_partition_key
    }
    try:
        client.upsert_entity(entity)
    except Exception as e:
        logging.error(f"Failed to save task index: {e}")

def get_task_partition_key(task_id):
    """
    Retrieves the PartitionKey for a given Task ID.
    """
    client = get_table_client(TASK_INDEX_TABLE_NAME)
    if not client: return "invoice_task" # Fallback for old data
    try:
        entity = client.get_entity(partition_key="task_index", row_key=task_id)
        return entity["TaskPartitionKey"]
    except:
        return "invoice_task" # Fallback

def save_task(task_data):
    """
    Saves a task to the Table Storage.
    task_data should contain 'id' (RowKey), 'status', 'extracted', 'match_candidate', etc.
    PartitionKey will be derived from created_at (YYYY-MM) to improve scalability.
    """
    client = get_table_client()
    if not client:
        return

    # Determine PartitionKey
    # If task_data has 'created_at', use it. Otherwise use current date.
    created_at = task_data.get("created_at")
    if not created_at:
        created_at = datetime.datetime.utcnow().isoformat()
        task_data["created_at"] = created_at
    
    # Parse created_at to get YYYY-MM
    try:
        dt = datetime.datetime.fromisoformat(str(created_at).replace('Z', '+00:00'))
        partition_key = dt.strftime('%Y-%m')
    except:
        partition_key = datetime.datetime.utcnow().strftime('%Y-%m')

    entity = {
        "PartitionKey": partition_key,
        "RowKey": task_data["id"],
        "Status": task_data["status"],
        "Confidence": task_data.get("confidence", 0),
        "DocumentUrl": task_data.get("document_url", ""),
        "ExtractedData": json.dumps(task_data.get("extracted", {})),
        "MatchCandidate": json.dumps(task_data.get("match_candidate", {})) if task_data.get("match_candidate") else None,
        "CreatedAt": created_at
    }

    try:
        client.upsert_entity(entity)
        logging.info(f"Task {task_data['id']} saved to table with PK {partition_key}.")
        
        # Save to Task Index for lookup by ID
        save_task_index(task_data["id"], partition_key)

        # Also update the Invoice Index for duplicate checking
        extracted = task_data.get("extracted", {})
        vendor_tax_id = extracted.get("vendor_tax_id")
        invoice_id = extracted.get("invoice_id")
        
        if vendor_tax_id and invoice_id:
            save_invoice_index(vendor_tax_id, invoice_id, task_data["id"], partition_key)
            
    except Exception as e:
        logging.error(f"Failed to save task to table: {str(e)}")

def save_invoice_index(vendor_tax_id, invoice_id, task_row_key, task_partition_key):
    """
    Saves an entry to the invoice index table for O(1) duplicate checking.
    PartitionKey: VendorTaxID
    RowKey: InvoiceID
    """
    client = get_table_client(INDEX_TABLE_NAME)
    if not client: return

    entity = {
        "PartitionKey": vendor_tax_id,
        "RowKey": invoice_id,
        "TaskRowKey": task_row_key,
        "TaskPartitionKey": task_partition_key
    }
    try:
        client.upsert_entity(entity)
    except Exception as e:
        logging.error(f"Failed to save invoice index: {str(e)}")

def check_duplicate_invoice(vendor_tax_id, invoice_id):
    """
    Checks if an invoice with the same Vendor Tax ID and Invoice ID already exists.
    Returns True if duplicate found, False otherwise.
    Uses the Index Table for O(1) lookup.
    """
    client = get_table_client(INDEX_TABLE_NAME)
    if not client or not vendor_tax_id or not invoice_id:
        return False

    try:
        # O(1) lookup
        client.get_entity(partition_key=vendor_tax_id, row_key=invoice_id)
        return True
    except Exception:
        # Entity not found
        return False

def get_pending_tasks():
    """
    Retrieves all tasks with status YELLOW or RED.
    Queries recent partitions (Current Month and Previous Month).
    """
    client = get_table_client()
    if not client:
        return []

    tasks = []
    try:
        # We need to query across partitions. 
        # For scalability, we only check the current and previous month.
        # Older pending tasks might be considered "stale" or require a separate archival query.
        
        now = datetime.datetime.utcnow()
        partitions = [
            now.strftime('%Y-%m'),
            (now.replace(day=1) - datetime.timedelta(days=1)).strftime('%Y-%m')
        ]
        
        parameters = {"status1": "YELLOW", "status2": "RED"}
        
        for pk in partitions:
            filter_query = f"PartitionKey eq '{pk}' and (Status eq @status1 or Status eq @status2)"
            try:
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
            except Exception:
                continue # Partition might not exist

    except Exception as e:
        logging.error(f"Error getting pending tasks: {str(e)}")
        
    return tasks

def update_task_status(task_id, new_status):
    """
    Updates the status of a task.
    """
    client = get_table_client()
    if not client:
        return

    pk = get_task_partition_key(task_id)

    try:
        entity = client.get_entity(partition_key=pk, row_key=task_id)
        entity["Status"] = new_status
        client.update_entity(entity)
        logging.info(f"Task {task_id} status updated to {new_status}.")
    except Exception as e:
        logging.error(f"Failed to update task {task_id}: {str(e)}")
        raise e

def get_sources():
    """
    Retrieves all configured data sources.
    """
    client = get_table_client("sources")
    if not client:
        return []

    sources = []
    try:
        entities = client.list_entities()
        for entity in entities:
            sources.append({
                "id": entity["RowKey"],
                "partner": entity.get("Partner", ""),
                "server": entity.get("Server", ""),
                "port": entity.get("Port", ""),
                "user": entity.get("User", ""),
                # Don't return password in plain text if possible, or handle securely
                "password": entity.get("Password", "") 
            })
    except Exception as e:
        logging.error(f"Failed to query sources: {str(e)}")
    
    return sources

def save_source(source_data):
    """
    Saves a data source configuration.
    """
    client = get_table_client("sources")
    if not client:
        return

    entity = {
        "PartitionKey": "email_source",
        "RowKey": source_data.get("id", str(uuid.uuid4())),
        "Partner": source_data.get("partner", ""),
        "Server": source_data.get("server", ""),
        "Port": source_data.get("port", ""),
        "User": source_data.get("user", ""),
        "Password": source_data.get("password", "")
    }

    try:
        client.upsert_entity(entity)
        logging.info(f"Source {entity['RowKey']} saved.")
        return entity["RowKey"]
    except Exception as e:
        logging.error(f"Failed to save source: {str(e)}")
        raise e

def search_candidates(query):
    """
    Searches for candidates or tasks matching the query.
    """
    client = get_table_client() # tasks table
    if not client:
        return []

    results = []
    try:
        # Simple search: scan all and filter in memory (inefficient for large data but ok for prototype)
        # Or use OData filter if possible. OData 'contains' is not supported on all fields in Table Storage.
        # We will fetch all and filter.
        entities = client.list_entities()
        
        query_lower = query.lower()
        
        for entity in entities:
            extracted = json.loads(entity.get("ExtractedData", "{}"))
            candidate = json.loads(entity.get("MatchCandidate", "{}")) if entity.get("MatchCandidate") else {}
            
            vendor = extracted.get("vendor_name", "") or candidate.get("vendor_name", "")
            amount = str(extracted.get("total_amount", "") or candidate.get("amount", ""))
            
            if query_lower in vendor.lower() or query_lower in amount:
                results.append({
                    "id": entity["RowKey"],
                    "vendor": vendor,
                    "amount": amount,
                    "date": extracted.get("invoice_date", "") or candidate.get("date", ""),
                    "status": entity["Status"]
                })
                
    except Exception as e:
        logging.error(f"Failed to search tasks: {str(e)}")
        
    return results
