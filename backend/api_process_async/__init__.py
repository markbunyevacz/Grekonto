"""
Async document processing API endpoint.

POST /api/process-async

Submits a document for asynchronous processing and returns job ID for tracking.
The document is queued for processing without blocking the client request.

Request Body:
{
    "document_id": "doc_001",
    "filename": "invoice.pdf",
    "blob_path": "uploads/invoice.pdf",
    "file_size": 102400,
    "priority": "HIGH",  # or NORMAL, LOW
    "tags": {
        "source": "email",
        "user_id": "user123"
    }
}

Response:
{
    "status": "success",
    "job_id": "uuid",
    "message": "Document queued for async processing",
    "tracking_url": "/api/job/{job_id}/status"
}

Features:
- Priority-based job queuing
- Immediate response with job tracking ID
- Non-blocking async processing
- Detailed job status tracking
- Error handling and retry logic
"""

import azure.functions as func
import logging
import json
from typing import Dict, Any, Optional

from ..shared.async_queue_manager import (
    get_queue_manager, JobPriority, JobStatus
)
from ..shared.monitoring_service import get_monitoring_service
from ..shared.table_service import get_table_service_client

logger = logging.getLogger(__name__)


def main(req: func.HttpRequest) -> func.HttpResponse:
    """
    Submit document for async processing.
    
    Returns: 202 Accepted with job ID for tracking
    """
    logger.info('=' * 80)
    logger.info('📤 ASYNC PROCESS REQUEST RECEIVED')
    logger.info('=' * 80)
    
    try:
        # Parse request body
        try:
            req_body = req.get_json()
        except ValueError as e:
            logger.error(f"❌ Invalid JSON in request: {e}")
            return func.HttpResponse(
                json.dumps({
                    "status": "error",
                    "message": "Invalid JSON in request body"
                }),
                status_code=400,
                mimetype="application/json"
            )
        
        # Validate required fields
        document_id = req_body.get("document_id")
        filename = req_body.get("filename")
        blob_path = req_body.get("blob_path")
        file_size = req_body.get("file_size", 0)
        priority_str = req_body.get("priority", "NORMAL")
        tags = req_body.get("tags", {})
        
        if not all([document_id, filename, blob_path]):
            logger.error("❌ Missing required fields: document_id, filename, blob_path")
            return func.HttpResponse(
                json.dumps({
                    "status": "error",
                    "message": "Missing required fields: document_id, filename, blob_path"
                }),
                status_code=400,
                mimetype="application/json"
            )
        
        # Parse priority
        try:
            priority = JobPriority[priority_str.upper()]
        except KeyError:
            logger.warning(f"⚠️  Invalid priority: {priority_str}, using NORMAL")
            priority = JobPriority.NORMAL
        
        # Get queue manager
        queue_manager = get_queue_manager()
        
        # Enqueue job
        job_id = queue_manager.enqueue_job(
            document_id=document_id,
            filename=filename,
            blob_path=blob_path,
            file_size=file_size,
            priority=priority,
            tags=tags
        )
        
        logger.info(f"✅ Job enqueued successfully: {job_id}")
        
        # Record monitoring metric
        try:
            monitoring_service = get_monitoring_service()
            session_id = tags.get("session_id", "async")
            monitoring_service.record_metric(
                session_id,
                {
                    "operation_name": "async_job_enqueue",
                    "success": True,
                    "metadata": {
                        "job_id": job_id,
                        "priority": priority.name,
                        "file_size_mb": file_size / 1024 / 1024
                    }
                }
            )
        except Exception as e:
            logger.warning(f"⚠️  Failed to record monitoring metric: {e}")
        
        # Update table service if available
        try:
            table_service = get_table_service()
            table_service.update_processing_status(
                file_id=document_id,
                stage="QUEUED",
                status="QUEUED",
                message=f"Job queued for async processing: {job_id}",
                metadata={
                    "job_id": job_id,
                    "priority": priority.name,
                    "queued_at": str(__import__('datetime').datetime.utcnow())
                }
            )
        except Exception as e:
            logger.warning(f"⚠️  Failed to update table service: {e}")
        
        # Return 202 Accepted response
        response_body = {
            "status": "success",
            "job_id": job_id,
            "document_id": document_id,
            "priority": priority.name,
            "status_code": 202,
            "message": "Document queued for async processing",
            "tracking_url": f"/api/job/{job_id}/status"
        }
        
        logger.info(f"📝 Response: {json.dumps(response_body)}")
        
        return func.HttpResponse(
            json.dumps(response_body),
            status_code=202,  # Accepted
            mimetype="application/json"
        )
    
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}", exc_info=True)
        
        error_response = {
            "status": "error",
            "message": f"Server error: {str(e)[:100]}",
            "status_code": 500
        }
        
        return func.HttpResponse(
            json.dumps(error_response),
            status_code=500,
            mimetype="application/json"
        )
