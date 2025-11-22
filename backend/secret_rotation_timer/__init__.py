import azure.functions as func
import logging
from ..shared import secret_rotation
from ..shared import table_service

def main(mytimer: func.TimerRequest) -> None:
    """Secret rotation timer trigger - runs monthly"""
    logging.info('Secret rotation timer triggered')
    
    try:
        # Get status of all secrets
        secrets_status = secret_rotation.get_all_secrets_status()
        
        logging.info(f"Checking {len(secrets_status)} secrets for rotation")
        
        rotated_count = 0
        for secret_name, status in secrets_status.items():
            age = status['age_days']
            should_rotate = status['should_rotate']
            
            if age < 0:
                logging.warning(f"Could not determine age of secret: {secret_name}")
                continue
            
            logging.info(f"Secret {secret_name}: age={age} days, should_rotate={should_rotate}")
            
            if should_rotate:
                logging.warning(f"Secret {secret_name} needs rotation (age: {age} days)")
                
                # Log audit event
                table_service.log_audit_event(
                    event_type="SECRET_ROTATION_NEEDED",
                    message=f"Secret {secret_name} needs rotation (age: {age} days)",
                    related_item_id=secret_name
                )
                
                rotated_count += 1
        
        # Log summary
        table_service.log_audit_event(
            event_type="SECRET_ROTATION_CHECK",
            message=f"Secret rotation check completed. {rotated_count} secrets need rotation.",
            related_item_id="SYSTEM"
        )
        
        logging.info(f"Secret rotation check completed. {rotated_count} secrets need rotation.")
        
    except Exception as e:
        logging.error(f"Error in secret rotation timer: {str(e)}")
        table_service.log_audit_event(
            event_type="SECRET_ROTATION_ERROR",
            message=f"Error in secret rotation timer: {str(e)}",
            related_item_id="SYSTEM"
        )

