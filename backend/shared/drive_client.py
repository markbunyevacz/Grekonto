from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import io
import logging
from typing import List, Dict, Any
from . import key_vault_client
import json

def fetch_files(source_config: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Fetches files from a Google Drive folder.
    source_config should contain: 'folder_id', 'service_account_secret_name'
    """
    folder_id = source_config.get('folder_id')
    secret_name = source_config.get('service_account_secret_name')
    
    if not folder_id or not secret_name:
        logging.error("Missing folder_id or service_account_secret_name for Google Drive source")
        return []

    try:
        service_account_info_str = key_vault_client.get_secret(secret_name)
        service_account_info = json.loads(service_account_info_str)
        
        creds = service_account.Credentials.from_service_account_info(
            service_account_info, scopes=['https://www.googleapis.com/auth/drive.readonly']
        )
        
        service = build('drive', 'v3', credentials=creds)
        
        # Query for files in the folder
        results = service.files().list(
            q=f"'{folder_id}' in parents and trashed = false",
            fields="nextPageToken, files(id, name, mimeType)"
        ).execute()
        
        items = results.get('files', [])
        downloaded_files = []
        
        for item in items:
            file_id = item['id']
            file_name = item['name']
            
            # Skip folders
            if item['mimeType'] == 'application/vnd.google-apps.folder':
                continue
                
            request = service.files().get_media(fileId=file_id)
            fh = io.BytesIO()
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while done is False:
                status, done = downloader.next_chunk()
            
            downloaded_files.append({
                'filename': file_name,
                'content': fh.getvalue()
            })
            
        return downloaded_files

    except Exception as e:
        logging.error(f"Error fetching files from Google Drive: {str(e)}")
        return []
