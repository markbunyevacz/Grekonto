import azure.functions as func
import azure.durable_functions as df
import json
import logging

async def main(req: func.HttpRequest, client: df.DurableOrchestrationClient) -> func.HttpResponse:
    """Get orchestration status"""
    logging.info('Fetching orchestration status')
    
    try:
        # Get instance ID from query parameters
        instance_id = req.params.get('instance_id')
        
        if not instance_id:
            return func.HttpResponse(
                json.dumps({
                    "success": False,
                    "error": "instance_id is required"
                }),
                mimetype="application/json",
                status_code=400
            )
        
        # Get orchestration status
        status = await client.get_status(instance_id)
        
        if status is None:
            return func.HttpResponse(
                json.dumps({
                    "success": False,
                    "error": f"Instance {instance_id} not found"
                }),
                mimetype="application/json",
                status_code=404
            )
        
        return func.HttpResponse(
            json.dumps({
                "success": True,
                "instance_id": instance_id,
                "runtime_status": status.runtime_status.name,
                "input": status.input,
                "output": status.output,
                "created_time": status.created_time.isoformat() if status.created_time else None,
                "last_updated_time": status.last_updated_time.isoformat() if status.last_updated_time else None
            }),
            mimetype="application/json",
            status_code=200
        )
    except Exception as e:
        logging.error(f"Error fetching orchestration status: {str(e)}")
        return func.HttpResponse(
            json.dumps({
                "success": False,
                "error": str(e)
            }),
            mimetype="application/json",
            status_code=500
        )

