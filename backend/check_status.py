import os
from azure.data.tables import TableClient

CONNECT_STR = "DefaultEndpointsProtocol=http;AccountName=devstoreaccount1;AccountKey=Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw==;BlobEndpoint=http://127.0.0.1:10000/devstoreaccount1;QueueEndpoint=http://127.0.0.1:10001/devstoreaccount1;TableEndpoint=http://127.0.0.1:10002/devstoreaccount1;"
TABLE_NAME = "ProcessingStatus" # Correct table name
FILE_ID = "manual_upload_20251122_000_jpg"

def check_status():
    try:
        table_client = TableClient.from_connection_string(conn_str=CONNECT_STR, table_name=TABLE_NAME)
        
        # Try to get the entity
        # PartitionKey is usually the file_id or a fixed value depending on implementation.
        # Let's try querying by RowKey which is likely the file_id
        
        filter_query = f"RowKey eq '{FILE_ID}'"
        entities = list(table_client.query_entities(filter_query))
        
        if not entities:
            print(f"No status found for File ID: {FILE_ID}")
            return

        print(f"Status for {FILE_ID}:")
        for entity in entities:
            print(f"  Current Status: {entity.get('CurrentStatus')}")
            print(f"  Current Stage: {entity.get('CurrentStage')}")
            print(f"  Overall Status: {entity.get('OverallStatus')}")
            print(f"  Last Updated: {entity.get('LastUpdated')}")
            print(f"  Stages History: {entity.get('Stages')}")
            print("-" * 20)

    except Exception as e:
        print(f"Error checking status: {e}")

if __name__ == "__main__":
    check_status()
