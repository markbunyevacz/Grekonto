import os
import logging
from azure.storage.blob import BlobServiceClient

def upload_to_blob(container_name, blob_name, data):
    """
    Uploads data to Azure Blob Storage.
    """
    try:
        connect_str = os.getenv('AzureWebJobsStorage')
        if not connect_str:
            logging.warning("AzureWebJobsStorage env var not found. Skipping blob upload (Local Dev Mode).")
            return

        blob_service_client = BlobServiceClient.from_connection_string(connect_str)
        container_client = blob_service_client.get_container_client(container_name)
        
        # Create container if it doesn't exist
        if not container_client.exists():
            container_client.create_container()

        blob_client = container_client.get_blob_client(blob_name)
        blob_client.upload_blob(data, overwrite=True)
        
    except Exception as e:
        logging.error(f"Failed to upload blob: {str(e)}")
        raise

def generate_sas_url(container_name, blob_name):
    """
    Generates a SAS URL for a blob.
    """
    try:
        connect_str = os.getenv('AzureWebJobsStorage')
        if not connect_str:
            return "https://via.placeholder.com/400x600.png?text=Local+Dev+Mode"

        blob_service_client = BlobServiceClient.from_connection_string(connect_str)
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
        
        from azure.storage.blob import generate_blob_sas, BlobSasPermissions
        from datetime import datetime, timedelta

        sas_token = generate_blob_sas(
            account_name=blob_client.account_name,
            container_name=container_name,
            blob_name=blob_name,
            account_key=blob_service_client.credential.account_key,
            permission=BlobSasPermissions(read=True),
            expiry=datetime.utcnow() + timedelta(hours=1)
        )
        
        return f"{blob_client.url}?{sas_token}"
    except Exception as e:
        logging.error(f"Failed to generate SAS URL: {str(e)}")
        return "https://via.placeholder.com/400x600.png?text=Error+Generating+URL"
