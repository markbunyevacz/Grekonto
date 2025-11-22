import azure.functions as func
import azure.durable_functions as df
import logging

def orchestrator_function(context: df.DurableOrchestrationContext):
    """Orchestrate document processing workflow"""
    
    blob_data = context.get_input()
    logging.info(f"Starting orchestration for: {blob_data.get('blob_name')}")
    
    try:
        # 1. OCR Activity
        logging.info("Starting OCR activity")
        ocr_result = yield context.call_activity(
            "activity_ocr",
            blob_data
        )
        
        if not ocr_result.get("success"):
            raise Exception(f"OCR failed: {ocr_result.get('error')}")
        
        logging.info("OCR completed successfully")
        
        # 2. Matching Activity
        logging.info("Starting matching activity")
        match_result = yield context.call_activity(
            "activity_matching",
            ocr_result.get("extracted_data")
        )
        
        if not match_result.get("success"):
            logging.warning(f"Matching returned non-success: {match_result.get('error')}")
        
        logging.info("Matching completed")
        
        # 3. Upload Activity
        logging.info("Starting upload activity")
        upload_result = yield context.call_activity(
            "activity_upload",
            {
                "match_result": match_result,
                "blob_data": blob_data
            }
        )
        
        if not upload_result.get("success"):
            raise Exception(f"Upload failed: {upload_result.get('error')}")
        
        logging.info("Upload completed successfully")
        
        return {
            "status": "SUCCESS",
            "result": upload_result
        }
        
    except Exception as e:
        logging.error(f"Orchestration failed: {str(e)}")
        return {
            "status": "FAILED",
            "error": str(e)
        }

main = df.Orchestrator.create(orchestrator_function)

