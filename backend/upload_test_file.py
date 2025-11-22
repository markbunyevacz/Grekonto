import os
import sys
from azure.storage.blob import BlobServiceClient
import json

# Load environment variables from local.settings.json
SETTINGS_PATH = os.path.join(os.path.dirname(__file__), 'local.settings.json')
# Default Azurite connection string
CONNECT_STR = "DefaultEndpointsProtocol=http;AccountName=devstoreaccount1;AccountKey=Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw==;BlobEndpoint=http://127.0.0.1:10000/devstoreaccount1;QueueEndpoint=http://127.0.0.1:10001/devstoreaccount1;TableEndpoint=http://127.0.0.1:10002/devstoreaccount1;"

if os.path.exists(SETTINGS_PATH):
    try:
        with open(SETTINGS_PATH, 'r') as f:
            settings = json.load(f)
            values = settings.get('Values', {})
            # Only use the one from settings if it's not the shortcut "UseDevelopmentStorage=true" which sometimes fails in python sdk
            if 'AzureWebJobsStorage' in values and values['AzureWebJobsStorage'] != "UseDevelopmentStorage=true":
                CONNECT_STR = values['AzureWebJobsStorage']
    except Exception as e:
        print(f"Warning: Could not load settings from {SETTINGS_PATH}: {e}")

CONTAINER_NAME = "raw-documents"
SOURCE_FILE = os.path.join(os.path.dirname(__file__), "external", "ICDAR-2019-SROIE", "data", "img", "000.jpg")
DEST_BLOB_NAME = "manual_upload/20251122/000.jpg"

def upload_file():
    if not os.path.exists(SOURCE_FILE):
        print(f"Error: Source file not found at {SOURCE_FILE}")
        return

    try:
        blob_service_client = BlobServiceClient.from_connection_string(CONNECT_STR)
        
        # Create container if it doesn't exist
        container_client = blob_service_client.get_container_client(CONTAINER_NAME)
        if not container_client.exists():
            container_client.create_container()
            print(f"Created container '{CONTAINER_NAME}'")

        # Upload blob
        blob_client = blob_service_client.get_blob_client(container=CONTAINER_NAME, blob=DEST_BLOB_NAME)
        
        with open(SOURCE_FILE, "rb") as data:
            blob_client.upload_blob(data, overwrite=True)
            
        print(f"Successfully uploaded {SOURCE_FILE}")
        print(f"To: {CONTAINER_NAME}/{DEST_BLOB_NAME}")
        print(f"Expected File ID: {DEST_BLOB_NAME.replace('/', '_').replace('.', '_')}")

    except Exception as e:
        print(f"Error uploading file: {e}")

if __name__ == "__main__":
    upload_file()
