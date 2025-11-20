import dropbox
import logging
from typing import List, Dict, Any
from . import key_vault_client

def fetch_files(source_config: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Fetches files from a Dropbox folder.
    source_config should contain: 'folder_path', 'access_token_secret_name'
    """
    folder_path = source_config.get('folder_path', '')
    secret_name = source_config.get('access_token_secret_name')
    
    if not secret_name:
        logging.error("Missing access_token_secret_name for Dropbox source")
        return []

    try:
        access_token = key_vault_client.get_secret(secret_name)
        dbx = dropbox.Dropbox(access_token)
        
        downloaded_files = []
        
        # List files in folder
        result = dbx.files_list_folder(folder_path)
        
        while True:
            for entry in result.entries:
                if isinstance(entry, dropbox.files.FileMetadata):
                    _, res = dbx.files_download(entry.path_lower)
                    downloaded_files.append({
                        'filename': entry.name,
                        'content': res.content
                    })
            
            if not result.has_more:
                break
            result = dbx.files_list_folder_continue(result.cursor)
            
        return downloaded_files

    except Exception as e:
        logging.error(f"Error fetching files from Dropbox: {str(e)}")
        return []
