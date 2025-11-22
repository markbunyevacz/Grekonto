import logging
import azure.functions as func
import azure.durable_functions as df
from ..shared import table_service

async def main(myblob: func.InputStream, starter: str) -> None:
    """Blob trigger - start orchestration"""
    
    # Generate file ID from blob name
    blob_name = '/'.join(myblob.name.split('/')[1:])  # Remove container name
    file_id = blob_name.replace('/', '_').replace('.', '_')
    
    logging.info('='*80)
    logging.info(f"🔄 BLOB TRIGGER ACTIVATED (Orchestrator Starter)")
    logging.info(f"📄 Blob: {myblob.name}")
    logging.info(f"📦 Size: {myblob.length} bytes")
    logging.info(f"🆔 File ID: {file_id}")
    logging.info('='*80)
    
    try:
        # Prepare blob data
        blob_data = {
            "blob_name": blob_name,
            "blob_path": myblob.name,
            "blob_url": f"https://{myblob.uri.split('/')[2]}/{myblob.name}",
            "size": myblob.length,
            "container_name": myblob.name.split('/')[0]
        }
        
        # Log audit event
        table_service.log_audit_event(
            event_type="PROCESSING_STARTED",
            message=f"Document processing started via orchestrator",
            related_item_id=blob_name
        )
        
        # Update processing status
        table_service.update_processing_status(
            file_id=file_id,
            stage="ORCHESTRATION_STARTED",
            status="IN_PROGRESS",
            message="Starting orchestration"
        )
        
        # Start orchestration
        client = df.DurableOrchestrationClient(starter)
        instance_id = await client.start_new(
            "orchestrator_process_document",
            input_=blob_data
        )
        
        logging.info(f"Started orchestration: {instance_id}")
        
        # Log audit event
        table_service.log_audit_event(
            event_type="ORCHESTRATION_STARTED",
            message=f"Orchestration started with instance ID: {instance_id}",
            related_item_id=blob_name
        )
        
    except Exception as e:
        logging.error(f"Error starting orchestration: {str(e)}")
        
        # Log audit event
        table_service.log_audit_event(
            event_type="ORCHESTRATION_START_FAILED",
            message=f"Failed to start orchestration: {str(e)}",
            related_item_id=blob_name
        )
        
        # Update processing status
        table_service.update_processing_status(
            file_id=file_id,
            stage="ORCHESTRATION_START_FAILED",
            status="ERROR",
            message=f"Failed to start orchestration",
            error=str(e)
        )

