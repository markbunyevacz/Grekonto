import azure.functions as func
import azure.durable_functions as df
import logging
from ..shared import aoc_client
from ..shared import table_service
from ..shared import storage_client

def activity_upload(data: dict) -> dict:
    """Upload to AOC system"""
    try:
        logging.info("Starting upload activity")
        
        match_result = data['match_result']
        blob_data = data['blob_data']
        
        # Initialize AOC client
        aoc = aoc_client.AOCClient()
        
        # Upload document
        upload_result = aoc.upload_document(
            match_result=match_result,
            blob_data=blob_data
        )
        
        # If successful, delete blob (Zero Data Retention)
        if upload_result.get('status') == 'GREEN':
            try:
                storage_client.delete_blob(
                    container_name=blob_data.get('container_name', 'documents'),
                    blob_name=blob_data.get('blob_name')
                )
                logging.info(f"Blob deleted after successful upload: {blob_data.get('blob_name')}")
            except Exception as e:
                logging.warning(f"Could not delete blob: {str(e)}")
        
        logging.info("Upload completed successfully")
        
        return {
            "success": True,
            "upload_result": upload_result
        }
    except Exception as e:
        logging.error(f"Upload activity failed: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

main = df.ActivityFunction(activity_upload)

