import azure.functions as func
import json
import logging
from ..shared.monitoring_service import get_monitoring_service

def main(req: func.HttpRequest) -> func.HttpResponse:
    """
    Get performance metrics for monitoring operations.
    
    Query parameters:
    - operation: Filter by operation name (optional)
    - limit: Maximum metrics to return (default: 100)
    
    Returns:
    - Metrics with statistics (min, max, mean, median, stdev, error_rate)
    """
    logging.info('Retrieving performance metrics')
    
    try:
        monitoring = get_monitoring_service()
        operation = req.params.get('operation')
        limit = int(req.params.get('limit', 100))
        
        if operation:
            # Get metrics for specific operation
            metrics = monitoring.get_metrics(operation, limit)
            stats = monitoring.get_metric_statistics(operation)
            
            return func.HttpResponse(
                json.dumps({
                    "operation": operation,
                    "metrics_count": len(metrics),
                    "statistics": stats,
                    "metrics": [m.to_dict() for m in metrics]
                }),
                mimetype="application/json",
                status_code=200
            )
        else:
            # Get statistics for all operations
            all_stats = {}
            for op_name in monitoring.metrics_store.keys():
                all_stats[op_name] = monitoring.get_metric_statistics(op_name)
            
            return func.HttpResponse(
                json.dumps({
                    "operations_monitored": len(all_stats),
                    "statistics": all_stats
                }),
                mimetype="application/json",
                status_code=200
            )
    
    except Exception as e:
        logging.error(f"Error retrieving metrics: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            mimetype="application/json",
            status_code=500
        )
