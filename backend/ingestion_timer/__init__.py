import datetime
import logging
import azure.functions as func
from ..shared import imap_client
from ..shared import storage_client
from ..shared import drive_client
from ..shared import dropbox_client
from ..shared import key_vault_client
from ..shared import table_service
from ..shared.file_validator import FileValidator

def main(mytimer: func.TimerRequest) -> None:
    utc_timestamp = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat()

    if mytimer.past_due:
        logging.info('The timer is past due!')

    logging.info('Python timer trigger function ran at %s', utc_timestamp)

    # 1. Fetch configurations
    sources = []
    try:
        db_sources = table_service.get_sources()
        for s in db_sources:
            sources.append({
                "type": "email",
                "host": s.get("server"),
                "port": s.get("port"),
                "user": s.get("user"),
                "password": s.get("password")
            })
    except Exception as e:
        logging.error(f"Error fetching sources from table: {e}")

    # 2. Poll Sources
    for source in sources:
        logging.info(f"Polling source: {source.get('type')} - {source.get('user') or source.get('folder_id') or source.get('folder_path')}")
        try:
            files = []
            
            if source['type'] == 'email':
                email_config = source.copy()
                if not email_config.get('password') and email_config.get('password_secret_name'):
                     email_config['password'] = key_vault_client.get_secret(email_config['password_secret_name'])
                files = imap_client.fetch_attachments(email_config)
            
            elif source['type'] == 'drive':
                files = drive_client.fetch_files(source)
                
            elif source['type'] == 'dropbox':
                files = dropbox_client.fetch_files(source)

            for file_data in files:
                filename = file_data['filename']
                content = file_data['content']
                
                # 3. Validate File Type (Strict MIME type validation + file signature verification)
                is_valid, error_msg = FileValidator.validate_file(filename, content)
                if not is_valid:
                    logging.warning(f"❌ File validation failed for '{filename}': {error_msg}")
                    continue

                # 4. Save to Blob Storage
                blob_name = f"{datetime.datetime.now().strftime('%Y%m%d')}/{filename}"
                storage_client.upload_to_blob("raw-documents", blob_name, content)
                logging.info(f"✅ Uploaded {filename} to raw-documents/{blob_name}")

        except Exception as e:
            logging.error(f"Error polling source {source}: {str(e)}")

    logging.info("Ingestion cycle completed.")
