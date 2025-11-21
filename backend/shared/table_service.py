def update_task_status(task_id, new_status, match_candidate=None):
    """
    Updates the status of a task.
    If match_candidate is provided, it updates that too.
    """
    client = get_table_client()
    if not client:
        return

    pk = get_task_partition_key(task_id)

    try:
        entity = client.get_entity(partition_key=pk, row_key=task_id)
        entity["Status"] = new_status
        
        if match_candidate:
             entity["MatchCandidate"] = json.dumps(match_candidate)
             
        client.update_entity(entity)
        logging.info(f"Task {task_id} status updated to {new_status}.")
    except Exception as e:
        logging.error(f"Failed to update task {task_id}: {str(e)}")
        raise e
