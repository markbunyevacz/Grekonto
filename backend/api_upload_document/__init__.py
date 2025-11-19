import azure.functions as func
import logging
import json
from ..shared import storage_client
import datetime

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request to upload a document.')

    try:
        # Check if the request is multipart/form-data
        # Azure Functions Python worker has limited support for parsing multipart/form-data directly in some versions,
        # but let's assume we can get the file from req.files or parse the body.
        # Standard way in v2 model or using libraries.
        # For simplicity in this environment, let's assume the body IS the file content and filename is in headers
        # or use a simple JSON with base64 if multipart is hard.
        
        # However, standard way:
        # file = req.files.get('file')
        # But req.files is not always available in the default HttpRequest object depending on the worker version.
        
        # Let's try to use the body directly if it's a binary upload, or check headers.
        filename = req.headers.get('x-filename')
        if not filename:
             return func.HttpResponse("Please provide x-filename header", status_code=400)

        file_content = req.get_body()
        
        if not file_content:
             return func.HttpResponse("File content is empty", status_code=400)

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
