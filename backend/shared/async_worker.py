"""
Asynchronous worker for processing queued documents.

This module provides:
1. Job consumption from RabbitMQ queues
2. Pipeline execution with timing tracking
3. Error handling and retry logic
4. Batch processing capabilities
5. Status updates during processing

Traditional DMS Weakness: Synchronous processing blocks requests, no background workers.
This Implementation: Async workers consume jobs from queues, execute processing pipelines
with detailed timing, and update status without blocking client requests.
"""

import json
import logging
import time
import threading
from typing import Dict, Optional, Any, Callable
from datetime import datetime
import sys
import os

try:
    import pika
    RABBITMQ_AVAILABLE = True
except ImportError:
    RABBITMQ_AVAILABLE = False

from .async_queue_manager import (
    get_queue_manager, JobMetadata, JobStatus, JobPriority
)
from .pipeline_tracker import (
    get_pipeline_tracker, PipelineStage, StageMetrics
)
from .monitoring_service import get_monitoring_service, PerformanceMetric
from .table_service import get_table_service
from .storage_client import get_storage_client

logger = logging.getLogger(__name__)


class AsyncWorker:
    """
    Worker for consuming and processing async jobs from queues.
    
    Features:
    - Consumes jobs from priority-based queues
    - Executes document processing pipeline
    - Tracks performance with pipeline tracker
    - Updates status via table service
    - Handles errors and retries
    """

    def __init__(
        self,
        worker_id: str,
        process_function: Callable,
        queue_manager=None,
        pipeline_tracker=None,
        monitoring_service=None,
        table_service=None,
        batch_size: int = 1,
        prefetch_count: int = 1
    ):
        """
        Initialize async worker.
        
        Args:
            worker_id: Unique worker identifier
            process_function: Function to process documents
            queue_manager: Queue manager instance
            pipeline_tracker: Pipeline tracker instance
            monitoring_service: Monitoring service instance
            table_service: Table service instance
            batch_size: Number of jobs to process in batch
            prefetch_count: Number of jobs to prefetch from queue
        """
        self.worker_id = worker_id
        self.process_function = process_function
        self.queue_manager = queue_manager or get_queue_manager()
        self.pipeline_tracker = pipeline_tracker or get_pipeline_tracker()
        self.monitoring_service = monitoring_service or get_monitoring_service()
        self.table_service = table_service or get_table_service()
        self.storage_client = get_storage_client()
        
        self.batch_size = batch_size
        self.prefetch_count = prefetch_count
        self.running = False
        self.jobs_processed = 0
        self.jobs_failed = 0

    def start(self) -> None:
        """Start worker thread."""
        self.running = True
        worker_thread = threading.Thread(
            target=self._worker_loop,
            name=f"AsyncWorker-{self.worker_id}",
            daemon=True
        )
        worker_thread.start()
        logger.info(f"✅ Worker started: {self.worker_id}")

    def stop(self) -> None:
        """Stop worker gracefully."""
        self.running = False
        logger.info(f"⏹️  Worker stopped: {self.worker_id}")

    def _worker_loop(self) -> None:
        """Main worker loop consuming jobs from queues."""
        while self.running:
            try:
                # Try to get jobs from queues (high to low priority)
                jobs = self._get_jobs_from_queues()
                
                if not jobs:
                    time.sleep(0.5)  # Brief sleep if no jobs
                    continue
                
                # Process batch
                for job_metadata in jobs:
                    if not self.running:
                        break
                    
                    self._process_job(job_metadata)
                    
            except Exception as e:
                logger.error(f"❌ Worker loop error: {e}")
                time.sleep(1)

    def _get_jobs_from_queues(self) -> list:
        """Get jobs from priority queues."""
        jobs = []
        
        if not self.queue_manager.channel:
            return jobs
        
        try:
            # Try high priority queue first
            method, properties, body = self.queue_manager.channel.basic_get(
                self.queue_manager.high_priority_queue
            )
            if body:
                job_data = json.loads(body)
                jobs.append(JobMetadata.from_dict(job_data))
                self.queue_manager.channel.basic_ack(method.delivery_tag)
        except Exception as e:
            logger.warning(f"⚠️  Error getting high priority job: {e}")
        
        if len(jobs) < self.batch_size:
            try:
                # Try normal priority queue
                method, properties, body = self.queue_manager.channel.basic_get(
                    self.queue_manager.normal_priority_queue
                )
                if body:
                    job_data = json.loads(body)
                    jobs.append(JobMetadata.from_dict(job_data))
                    self.queue_manager.channel.basic_ack(method.delivery_tag)
            except Exception as e:
                logger.warning(f"⚠️  Error getting normal priority job: {e}")
        
        if len(jobs) < self.batch_size:
            try:
                # Try low priority queue
                method, properties, body = self.queue_manager.channel.basic_get(
                    self.queue_manager.low_priority_queue
                )
                if body:
                    job_data = json.loads(body)
                    jobs.append(JobMetadata.from_dict(job_data))
                    self.queue_manager.channel.basic_ack(method.delivery_tag)
            except Exception as e:
                logger.warning(f"⚠️  Error getting low priority job: {e}")
        
        return jobs

    def _process_job(self, job_metadata: JobMetadata) -> None:
        """
        Process a single job with pipeline tracking.
        
        Args:
            job_metadata: Job to process
        """
        try:
            logger.info(f"📥 Processing job: {job_metadata.job_id}")
            
            # Start pipeline execution tracking
            execution_id = self.pipeline_tracker.start_execution(
                document_id=job_metadata.document_id,
                filename=job_metadata.filename,
                file_size=job_metadata.file_size
            )
            
            # Update job status
            self.queue_manager.update_job_status(
                job_metadata.job_id,
                JobStatus.PROCESSING
            )
            
            # Update table service
            self.table_service.update_processing_status(
                file_id=job_metadata.document_id,
                stage="ASYNC_PROCESSING",
                status="IN_PROGRESS",
                message=f"Processing started by worker {self.worker_id}"
            )
            
            # Stage 1: Download document from blob
            stage_1 = self.pipeline_tracker.start_stage(
                execution_id,
                PipelineStage.UPLOAD,
                metadata={"action": "download"}
            )
            
            try:
                document_content = self._download_document(job_metadata.blob_path)
                stage_1.items_processed = len(document_content)
                stage_1.success_count = 1
                self.pipeline_tracker.complete_stage(execution_id, stage_1, success=True)
            except Exception as e:
                stage_1.error_count = 1
                self.pipeline_tracker.complete_stage(
                    execution_id, stage_1, success=False,
                    error_message=str(e)
                )
                raise
            
            # Stage 2: Validation
            stage_2 = self.pipeline_tracker.start_stage(
                execution_id,
                PipelineStage.VALIDATION,
                metadata={"document_id": job_metadata.document_id}
            )
            
            try:
                is_valid = self._validate_document(document_content)
                stage_2.items_processed = 1
                stage_2.success_count = 1 if is_valid else 0
                self.pipeline_tracker.complete_stage(execution_id, stage_2, success=is_valid)
            except Exception as e:
                stage_2.error_count = 1
                self.pipeline_tracker.complete_stage(
                    execution_id, stage_2, success=False,
                    error_message=str(e)
                )
                raise
            
            # Stage 3-7: Execute user's processing function
            stage_process = self.pipeline_tracker.start_stage(
                execution_id,
                PipelineStage.EXTRACTION,
                metadata={"job_id": job_metadata.job_id}
            )
            
            try:
                result = self.process_function(
                    document_content,
                    job_metadata.document_id,
                    execution_id=execution_id
                )
                stage_process.items_processed = 1
                stage_process.success_count = 1
                stage_process.metadata["result_summary"] = str(result)[:200]
                self.pipeline_tracker.complete_stage(execution_id, stage_process, success=True)
            except Exception as e:
                stage_process.error_count = 1
                self.pipeline_tracker.complete_stage(
                    execution_id, stage_process, success=False,
                    error_message=str(e)
                )
                raise
            
            # Mark job as completed
            self.queue_manager.update_job_status(
                job_metadata.job_id,
                JobStatus.COMPLETED,
                result_metadata={"execution_id": execution_id}
            )
            
            # Complete execution
            execution = self.pipeline_tracker.complete_execution(
                execution_id, success=True
            )
            
            # Record performance metrics
            if execution:
                metric = PerformanceMetric(
                    operation_name="async_document_processing",
                    duration_ms=execution.total_duration_ms,
                    success=True,
                    metadata={
                        "job_id": job_metadata.job_id,
                        "file_size_mb": job_metadata.file_size / 1024 / 1024,
                        "stages": len(execution.stages)
                    }
                )
                session_id = job_metadata.tags.get("session_id", "async")
                self.monitoring_service.record_metric(session_id, metric)
            
            # Update table service final status
            self.table_service.update_processing_status(
                file_id=job_metadata.document_id,
                stage="ASYNC_PROCESSING",
                status="SUCCESS",
                message=f"Processing completed in {execution.total_duration_ms:.2f}ms",
                metadata={
                    "execution_id": execution_id,
                    "throughput_mb_per_sec": execution.throughput_items_per_second
                }
            )
            
            self.jobs_processed += 1
            logger.info(f"✅ Job completed: {job_metadata.job_id} ({execution.total_duration_ms:.2f}ms)")
            
        except Exception as e:
            logger.error(f"❌ Job processing failed: {job_metadata.job_id}: {e}")
            self.jobs_failed += 1
            
            # Update job status
            if self.queue_manager.mark_job_for_retry(job_metadata.job_id):
                logger.info(f"🔄 Job queued for retry: {job_metadata.job_id}")
            else:
                logger.warning(f"❌ Moving job to DLQ: {job_metadata.job_id}")
                self.queue_manager.move_to_dlq(
                    job_metadata.job_id,
                    f"Max retries exceeded: {str(e)}"
                )
            
            # Update table service
            self.table_service.update_processing_status(
                file_id=job_metadata.document_id,
                stage="ASYNC_PROCESSING",
                status="FAILED",
                message=f"Processing failed: {str(e)[:100]}"
            )
            
            # Complete execution as failed
            if 'execution_id' in locals():
                self.pipeline_tracker.complete_execution(
                    execution_id, success=False,
                    error_message=str(e)
                )

    def _download_document(self, blob_path: str) -> bytes:
        """Download document from blob storage."""
        # Extract container and blob name
        parts = blob_path.split('/', 1)
        if len(parts) != 2:
            raise ValueError(f"Invalid blob path: {blob_path}")
        
        container_name, blob_name = parts
        content = self.storage_client.download_from_blob(container_name, blob_name)
        
        if not content:
            raise Exception(f"Failed to download document: {blob_path}")
        
        return content

    def _validate_document(self, content: bytes) -> bool:
        """Validate document content."""
        if not content or len(content) == 0:
            raise ValueError("Empty document content")
        
        return True

    def get_stats(self) -> Dict[str, Any]:
        """Get worker statistics."""
        return {
            "worker_id": self.worker_id,
            "running": self.running,
            "jobs_processed": self.jobs_processed,
            "jobs_failed": self.jobs_failed,
            "success_rate": (self.jobs_processed / (self.jobs_processed + self.jobs_failed) * 100) 
                          if (self.jobs_processed + self.jobs_failed) > 0 else 0.0
        }


class WorkerPool:
    """
    Manages a pool of async workers.
    
    Features:
    - Create and manage multiple workers
    - Load balancing across workers
    - Pool statistics
    - Graceful shutdown
    """

    def __init__(self, worker_count: int = 3, process_function: Callable = None):
        """Initialize worker pool."""
        self.worker_count = worker_count
        self.process_function = process_function
        self.workers: Dict[str, AsyncWorker] = {}
        self.lock = threading.Lock()

    def start(self) -> None:
        """Start all workers in pool."""
        for i in range(self.worker_count):
            worker_id = f"worker_{i}"
            worker = AsyncWorker(
                worker_id=worker_id,
                process_function=self.process_function
            )
            worker.start()
            
            with self.lock:
                self.workers[worker_id] = worker
        
        logger.info(f"✅ Worker pool started with {self.worker_count} workers")

    def stop(self) -> None:
        """Stop all workers gracefully."""
        with self.lock:
            for worker in self.workers.values():
                worker.stop()
        
        logger.info(f"⏹️  Worker pool stopped")

    def get_pool_stats(self) -> Dict[str, Any]:
        """Get statistics for entire pool."""
        total_processed = 0
        total_failed = 0
        worker_stats = []
        
        with self.lock:
            for worker in self.workers.values():
                stats = worker.get_stats()
                worker_stats.append(stats)
                total_processed += stats["jobs_processed"]
                total_failed += stats["jobs_failed"]
        
        return {
            "pool_size": self.worker_count,
            "total_jobs_processed": total_processed,
            "total_jobs_failed": total_failed,
            "overall_success_rate": (total_processed / (total_processed + total_failed) * 100)
                                   if (total_processed + total_failed) > 0 else 0.0,
            "workers": worker_stats
        }


# Global worker pool
_worker_pool: Optional[WorkerPool] = None


def get_worker_pool() -> WorkerPool:
    """Get or create global worker pool."""
    global _worker_pool
    if _worker_pool is None:
        _worker_pool = WorkerPool(worker_count=3)
    return _worker_pool
