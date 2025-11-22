import azure.functions as func
import azure.durable_functions as df
import logging
from ..shared import matching_engine
from ..shared import table_service

def activity_matching(extracted_data: dict) -> dict:
    """Match extracted data with NAV items"""
    try:
        logging.info("Starting matching activity")
        
        # Call matching engine
        match_result = matching_engine.find_best_match(extracted_data)
        
        logging.info(f"Matching completed with status: {match_result.get('status')}")
        
        return {
            "success": True,
            "match_result": match_result
        }
    except Exception as e:
        logging.error(f"Matching activity failed: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

main = df.ActivityFunction(activity_matching)

