import azure.functions as func
import logging
import json
from ..shared import storage_client
from ..shared import table_service
from ..shared.file_validator import FileValidator, FileValidationError
from ..shared.async_queue_manager import get_queue_manager, JobPriority
import datetime

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('='*80)
    logging.info('📤 UPLOAD REQUEST RECEIVED')
    logging.info('='*80)

    try:
        filename = None
        file_content = None
        content_type = None

        # 1. Try to get file from multipart/form-data (req.files)
        if req.files:
            for name, f in req.files.items():
                filename = f.filename
                file_content = f.stream.read()
                content_type = f.content_type  # Get MIME type from request
                logging.info(f"📎 File received via multipart: {filename} ({len(file_content)} bytes)")
                break

        # 2. Fallback: Check if body is binary and filename is in headers (Legacy support)
        if not file_content:
            filename_header = req.headers.get('x-filename')
            if filename_header:
                filename = filename_header
                file_content = req.get_body()
                content_type = req.headers.get('content-type')
                logging.info(f"📎 File received via header: {filename} ({len(file_content)} bytes)")

        if not file_content or not filename:
            logging.error("❌ No file content or filename provided")
            return func.HttpResponse(
                 "Please upload a file using multipart/form-data (field 'file') or provide 'x-filename' header with binary body.",
                 status_code=400
            )

        # Validate uploaded file (MIME type, size, signature)
        logging.info(f"🔍 Starting file validation for: {filename}")
        is_valid, error_message = FileValidator.validate_file(filename, file_content, content_type)
        if not is_valid:
            logging.error(f"❌ FILE VALIDATION FAILED: {error_message}")
            return func.HttpResponse(
                json.dumps({"error": f"File validation failed: {error_message}"}),
                mimetype="application/json",
                status_code=400
            )

        # Generate blob name and file ID
        blob_name = f"manual_upload/{datetime.datetime.now().strftime('%Y%m%d')}/{filename}"
        file_id = blob_name.replace('/', '_').replace('.', '_')

        logging.info(f"📝 Generated blob name: {blob_name}")
        logging.info(f"🆔 File ID: {file_id}")

        # Initialize processing status
        table_service.update_processing_status(
            file_id=file_id,
            stage="UPLOAD_STARTED",
            status="IN_PROGRESS",
            message=f"Starting upload of {filename}"
        )

        # Upload to Blob Storage
        logging.info(f"☁️  Uploading to blob storage: raw-documents/{blob_name}")
        storage_client.upload_to_blob("raw-documents", blob_name, file_content)
        logging.info(f"✅ Upload successful!")

        # Update status
        table_service.update_processing_status(
            file_id=file_id,
            stage="UPLOADED",
            status="SUCCESS",
            message=f"File uploaded to blob storage. Queuing for OCR processing..."
        )

        # Queue the document for async processing
        logging.info(f"📋 Queuing document for async processing...")
        try:
            queue_manager = get_queue_manager()
            job_id = queue_manager.enqueue_job(
                document_id=file_id,
                filename=filename,
                blob_path=blob_name,
                file_size=len(file_content),
                priority=JobPriority.NORMAL,
                tags={"source": "manual_upload"}
            )
            logging.info(f"✅ Document queued successfully! Job ID: {job_id}")

            # Update status with job ID
            table_service.update_processing_status(
                file_id=file_id,
                stage="QUEUED",
                status="IN_PROGRESS",
                message=f"Document queued for OCR processing",
                metadata={"job_id": job_id}
            )
        except Exception as e:
            logging.warning(f"⚠️  Failed to queue document: {e}. Will rely on blob trigger.")

        logging.info('='*80)
        logging.info(f'✅ UPLOAD COMPLETED: {filename}')
        logging.info(f'📊 Next: Async worker will start OCR processing')
        logging.info('='*80)

        return func.HttpResponse(
            json.dumps({
                "message": f"File {filename} uploaded successfully",
                "blob": blob_name,
                "file_id": file_id,
                "status_url": f"/api/status/{file_id}"
            }),
            mimetype="application/json",
            status_code=200
        )

    except Exception as e:
        logging.error('='*80)
        logging.error(f"❌ UPLOAD FAILED: {str(e)}")
        logging.error('='*80)
        logging.exception(e)

        if 'file_id' in locals():
            table_service.update_processing_status(
                file_id=file_id,
                stage="UPLOAD_FAILED",
                status="ERROR",
                message="Upload failed",
                error=e
            )

        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            mimetype="application/json",
            status_code=500
        )
