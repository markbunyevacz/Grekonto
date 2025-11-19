import datetime
import logging
import azure.functions as func
from ..shared import imap_client
from ..shared import storage_client

def main(mytimer: func.TimerRequest) -> None:
    utc_timestamp = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat()

    if mytimer.past_due:
        logging.info('The timer is past due!')

    logging.info('Python timer trigger function ran at %s', utc_timestamp)

    # 1. Fetch configurations (Mocking the retrieval of source configs from Table Storage)
    # In a real scenario, we would query Azure Table Storage for active email accounts to poll.
    email_sources = [
        {"host": "imap.gmail.com", "user": "demo@grekonto.com", "password_secret_name": "demo-email-pass"}
    ]

    # 2. Poll Email Sources
    for source in email_sources:
        logging.info(f"Polling email source: {source['user']}")
        try:
            # Mocking the IMAP connection and fetching attachments
            attachments = imap_client.fetch_attachments(source)
            
            for attachment in attachments:
                filename = attachment['filename']
                content = attachment['content']
                
                # 3. Validate File Type (FR-Scope)
                if not filename.lower().endswith(('.pdf', '.jpg', '.png', '.jpeg')):
                    logging.info(f"Skipping unsupported file: {filename}")
                    continue

                # 4. Save to Blob Storage
                blob_name = f"{datetime.datetime.now().strftime('%Y%m%d')}/{filename}"
                storage_client.upload_to_blob("raw-documents", blob_name, content)
                logging.info(f"Uploaded {filename} to raw-documents/{blob_name}")

        except Exception as e:
            logging.error(f"Error polling {source['user']}: {str(e)}")

    logging.info("Ingestion cycle completed.")
