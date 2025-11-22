import os
import logging
from azure.storage.blob import BlobServiceClient

def get_connection_string():
    """Get the storage connection string, with fallback to Azurite"""
    connect_str = os.getenv('AzureWebJobsStorage')

    if not connect_str or connect_str == "UseDevelopmentStorage=true":
        logging.warning("Using Azurite development storage")
        # Full Azurite connection string for local development
        connect_str = "DefaultEndpointsProtocol=http;AccountName=devstoreaccount1;AccountKey=Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw==;BlobEndpoint=http://127.0.0.1:10000/devstoreaccount1;QueueEndpoint=http://127.0.0.1:10001/devstoreaccount1;TableEndpoint=http://127.0.0.1:10002/devstoreaccount1;"

    return connect_str

def upload_to_blob(container_name, blob_name, data):
    """
    Uploads data to Azure Blob Storage.
    """
    try:
        connect_str = get_connection_string()
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
        connect_str = get_connection_string()
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
        return ""

def delete_blob(container_name, blob_name):
    """
    Deletes a blob from Azure Blob Storage.
    """
    try:
        connect_str = get_connection_string()
        blob_service_client = BlobServiceClient.from_connection_string(connect_str)
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
        
        if blob_client.exists():
            blob_client.delete_blob()
            logging.info(f"Blob {blob_name} deleted from {container_name}.")
        else:
            logging.warning(f"Blob {blob_name} not found in {container_name}.")
            
    except Exception as e:
        logging.error(f"Failed to delete blob: {str(e)}")
