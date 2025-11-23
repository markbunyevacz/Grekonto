"""
Get job status for async processing.

GET /api/job/{job_id}/status

Retrieves current status and details of a queued/processing job.

Response:
{
    "status": "success",
    "job_id": "uuid",
    "document_id": "doc_001",
    "job_status": "PROCESSING",  # QUEUED, PROCESSING, COMPLETED, FAILED, DLQ
    "priority": "NORMAL",
    "created_at": "2025-11-23T10:00:00",
    "started_at": "2025-11-23T10:00:05",
    "completed_at": null,
    "retry_count": 0,
    "error_message": null,
    "result_metadata": {}
}
"""

import azure.functions as func
import logging
import json

from ..shared.async_queue_manager import get_queue_manager

logger = logging.getLogger(__name__)


def main(req: func.HttpRequest) -> func.HttpResponse:
    """Get job status by job ID."""
    
    logger.info('=' * 80)
    logger.info('📊 GET JOB STATUS REQUEST')
    logger.info('=' * 80)
    
    try:
        job_id = req.route_params.get("job_id")
        
        if not job_id:
            logger.error("❌ No job_id provided")
            return func.HttpResponse(
                json.dumps({
                    "status": "error",
                    "message": "No job_id provided"
                }),
                status_code=400,
                mimetype="application/json"
            )
        
        queue_manager = get_queue_manager()
        job_metadata = queue_manager.get_job_status(job_id)
        
        if not job_metadata:
            logger.warning(f"⚠️  Job not found: {job_id}")
            return func.HttpResponse(
                json.dumps({
                    "status": "error",
                    "message": f"Job not found: {job_id}",
                    "job_id": job_id
                }),
                status_code=404,
                mimetype="application/json"
            )
        
        response_body = {
            "status": "success",
            "job_id": job_metadata.job_id,
            "document_id": job_metadata.document_id,
            "filename": job_metadata.filename,
            "job_status": job_metadata.status.name,
            "priority": job_metadata.priority.name,
            "file_size": job_metadata.file_size,
            "created_at": job_metadata.created_at.isoformat(),
            "started_at": job_metadata.started_at.isoformat() if job_metadata.started_at else None,
            "completed_at": job_metadata.completed_at.isoformat() if job_metadata.completed_at else None,
            "retry_count": job_metadata.retry_count,
            "max_retries": job_metadata.max_retries,
            "error_message": job_metadata.error_message,
            "result_metadata": job_metadata.result_metadata
        }
        
        logger.info(f"✅ Job status retrieved: {job_id} ({job_metadata.status.name})")
        
        return func.HttpResponse(
            json.dumps(response_body),
            status_code=200,
            mimetype="application/json"
        )
    
    except Exception as e:
        logger.error(f"❌ Error: {e}", exc_info=True)
        
        return func.HttpResponse(
            json.dumps({
                "status": "error",
                "message": f"Server error: {str(e)[:100]}"
            }),
            status_code=500,
            mimetype="application/json"
        )
