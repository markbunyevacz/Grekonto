import azure.functions as func
import logging
import json
import os
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential
from ..shared.async_queue_manager import get_queue_manager, JobStatus
from ..shared import table_service
from ..shared import storage_client
from ..shared import matching_engine
from ..shared.aoc_client import AOCClient
from ..shared.ocr_extractor import OCRExtractor

logger = logging.getLogger(__name__)

def main(mytimer: func.TimerRequest) -> None:
    """Process queued documents for OCR and matching."""
    logger.info('🔄 Queue worker timer triggered')
    
    try:
        queue_manager = get_queue_manager()
        
        # Get jobs from queue (high to low priority)
        jobs = []
        
        # Try high priority queue
        try:
            if queue_manager.channel:
                method, properties, body = queue_manager.channel.basic_get(
                    queue_manager.high_priority_queue
                )
                if body:
                    job_data = json.loads(body)
                    jobs.append((job_data, method.delivery_tag if method else None))
                    logger.info(f"📋 Got high priority job: {job_data.get('job_id')}")
        except Exception as e:
            logger.warning(f"⚠️  Error getting high priority job: {e}")
        
        # Try normal priority queue
        try:
            if queue_manager.channel and len(jobs) < 5:
                method, properties, body = queue_manager.channel.basic_get(
                    queue_manager.normal_priority_queue
                )
                if body:
                    job_data = json.loads(body)
                    jobs.append((job_data, method.delivery_tag if method else None))
                    logger.info(f"📋 Got normal priority job: {job_data.get('job_id')}")
        except Exception as e:
            logger.warning(f"⚠️  Error getting normal priority job: {e}")
        
        if not jobs:
            logger.debug("📭 No jobs in queue")
            return
        
        # Process each job
        for job_data, delivery_tag in jobs:
            try:
                _process_job(job_data, queue_manager, delivery_tag)
            except Exception as e:
                logger.error(f"❌ Error processing job: {e}")
                if delivery_tag and queue_manager.channel:
                    try:
                        queue_manager.channel.basic_nack(delivery_tag, requeue=True)
                    except:
                        pass
    
    except Exception as e:
        logger.error(f"❌ Queue worker error: {e}")

def _process_job(job_data: dict, queue_manager, delivery_tag) -> None:
    """Process a single job from the queue."""
    file_id = job_data.get('document_id')
    blob_path = job_data.get('blob_path')
    filename = job_data.get('filename')
    
    logger.info(f"🔄 Processing job: {file_id}")
    
    try:
        # Get blob content
        logger.info(f"📥 Downloading blob: {blob_path}")
        blob_content = storage_client.download_from_blob("raw-documents", blob_path)
        
        # Update status: OCR started
        table_service.update_processing_status(
            file_id=file_id,
            stage="OCR_STARTED",
            status="IN_PROGRESS",
            message="Starting OCR with Azure Document Intelligence"
        )
        
        # Call Azure Document Intelligence with OCR Extractor - VALÓDI FELDOLGOZÁS
        endpoint = os.getenv("DOCUMENT_INTELLIGENCE_ENDPOINT") or os.getenv("FORM_RECOGNIZER_ENDPOINT")
        key = os.getenv("DOCUMENT_INTELLIGENCE_KEY") or os.getenv("FORM_RECOGNIZER_KEY")

        if not endpoint or not key:
            logger.error("❌ Azure Document Intelligence credentials REQUIRED!")
            table_service.update_processing_status(
                file_id=file_id,
                stage="OCR_FAILED",
                status="FAILED",
                message="Azure Document Intelligence credentials missing"
            )
            return

        try:
            extractor = OCRExtractor(endpoint, key)
            ocr_result = extractor.extract_from_invoice(blob_content)

            # Map OCR result to our format
            extracted_data = {
                "vendor": ocr_result.get("company", ""),
                "amount": ocr_result.get("total", ""),
                "currency": "EUR",  # Default currency
                "date": ocr_result.get("date", ""),
                "address": ocr_result.get("address", ""),
                "confidence": ocr_result.get("confidence", 0)
            }
            logger.info(f"✅ OCR completed: {extracted_data}")
        except Exception as e:
            logger.error(f"❌ OCR extraction error: {e}")
            table_service.update_processing_status(
                file_id=file_id,
                stage="OCR_FAILED",
                status="FAILED",
                message=f"OCR extraction failed: {str(e)}"
            )
            return
        
        # Update status: OCR completed
        table_service.update_processing_status(
            file_id=file_id,
            stage="OCR_COMPLETED",
            status="SUCCESS",
            message=f"Extracted data from invoice: {extracted_data.get('vendor')} - {extracted_data.get('amount')} {extracted_data.get('currency')}"
        )
        
        # Matching
        logger.info("🔍 Starting matching...")
        match_result = matching_engine.match_invoice(extracted_data)
        logger.info(f"✅ Matching completed: {match_result}")
        
        # Update status: Matching completed
        table_service.update_processing_status(
            file_id=file_id,
            stage="MATCHING_COMPLETED",
            status="SUCCESS",
            message=f"Matching completed with status: {match_result.get('status')}"
        )
        
        # Acknowledge job
        if delivery_tag and queue_manager.channel:
            queue_manager.channel.basic_ack(delivery_tag)
            logger.info(f"✅ Job acknowledged: {file_id}")
        
    except Exception as e:
        logger.error(f"❌ Job processing failed: {e}")
        table_service.update_processing_status(
            file_id=file_id,
            stage="ERROR",
            status="ERROR",
            message=f"Processing failed: {str(e)}"
        )
        if delivery_tag and queue_manager.channel:
            try:
                queue_manager.channel.basic_nack(delivery_tag, requeue=True)
            except:
                pass

