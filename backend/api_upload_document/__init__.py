import azure.functions as func
import logging
import json
from ..shared import storage_client
from ..shared import table_service
import datetime

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('='*80)
    logging.info('📤 UPLOAD REQUEST RECEIVED')
    logging.info('='*80)

    try:
        filename = None
        file_content = None

        # 1. Try to get file from multipart/form-data (req.files)
        if req.files:
            for name, f in req.files.items():
                filename = f.filename
                file_content = f.stream.read()
                logging.info(f"📎 File received via multipart: {filename} ({len(file_content)} bytes)")
                break

        # 2. Fallback: Check if body is binary and filename is in headers (Legacy support)
        if not file_content:
            filename_header = req.headers.get('x-filename')
            if filename_header:
                filename = filename_header
                file_content = req.get_body()
                logging.info(f"📎 File received via header: {filename} ({len(file_content)} bytes)")

        if not file_content or not filename:
            logging.error("❌ No file content or filename provided")
            return func.HttpResponse(
                 "Please upload a file using multipart/form-data (field 'file') or provide 'x-filename' header with binary body.",
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
            message=f"File uploaded to blob storage. Waiting for OCR processing..."
        )

        logging.info('='*80)
        logging.info(f'✅ UPLOAD COMPLETED: {filename}')
        logging.info(f'📊 Next: Blob trigger will start OCR processing')
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
