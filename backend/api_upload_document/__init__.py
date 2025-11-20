import azure.functions as func
import logging
import json
from ..shared import storage_client
import datetime

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request to upload a document.')

    try:
        filename = None
        file_content = None

        # 1. Try to get file from multipart/form-data (req.files)
        if req.files:
            for name, f in req.files.items():
                filename = f.filename
                file_content = f.stream.read()
                break
        
        # 2. Fallback: Check if body is binary and filename is in headers (Legacy support)
        if not file_content:
            filename_header = req.headers.get('x-filename')
            if filename_header:
                filename = filename_header
                file_content = req.get_body()

        if not file_content or not filename:
             return func.HttpResponse(
                 "Please upload a file using multipart/form-data (field 'file') or provide 'x-filename' header with binary body.", 
                 status_code=400
            )

        # Upload to Blob Storage
        # We use the same container as the timer trigger: "raw-documents"
        blob_name = f"manual_upload/{datetime.datetime.now().strftime('%Y%m%d')}/{filename}"
        storage_client.upload_to_blob("raw-documents", blob_name, file_content)

        return func.HttpResponse(
            json.dumps({"message": f"File {filename} uploaded successfully", "blob": blob_name}),
            mimetype="application/json",
            status_code=200
        )

    except Exception as e:
        logging.error(f"Error uploading file: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            mimetype="application/json",
            status_code=500
        )
