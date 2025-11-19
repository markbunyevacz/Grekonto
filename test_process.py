import requests
import time
import os

BASE_URL = "http://localhost:7071/api"

def test_full_process():
    print("--- Starting End-to-End Test ---")

    # 1. Create a dummy invoice file
    filename = "test_invoice_001.pdf"
    with open(filename, "wb") as f:
        f.write(b"%PDF-1.4 dummy content for testing")
    
    print(f"[1] Created dummy file: {filename}")

    # 2. Upload the file
    print("[2] Uploading file...")
    try:
        with open(filename, "rb") as f:
            # Sending as binary body with header, matching the API implementation
            headers = {"x-filename": filename, "Content-Type": "application/pdf"}
            response = requests.post(f"{BASE_URL}/upload", data=f, headers=headers)
        
        if response.status_code == 200:
            print(f"    Upload successful: {response.json()}")
        else:
            print(f"    Upload failed: {response.status_code} - {response.text}")
            return
    except Exception as e:
        print(f"    Error during upload: {e}")
        return

    # 3. Poll for the task to appear
    print("[3] Waiting for processing (Polling /api/tasks)...")
    task_id = None
    for i in range(10): # Wait up to 20 seconds
        try:
            response = requests.get(f"{BASE_URL}/tasks")
            if response.status_code == 200:
                tasks = response.json()
                # Look for our file. The ID is generated from blob name.
                # Blob name format: manual_upload/YYYYMMDD/filename
                # ID format: manual_upload_YYYYMMDD_filename (slashes replaced by underscores)
                
                # We can just look for the most recent one or one with "Mock Vendor"
                for task in tasks:
                    if "Mock Vendor" in str(task.get('extracted', {}).get('vendor')):
                        print(f"    Found processed task! ID: {task['id']}")
                        print(f"    Status: {task['status']}")
                        task_id = task['id']
                        break
                
                if task_id:
                    break
            
            print("    Waiting...")
            time.sleep(2)
        except Exception as e:
            print(f"    Error polling tasks: {e}")
            time.sleep(2)

    if not task_id:
        print("    Timeout: Task did not appear in the list. (Is the Blob Trigger running?)")
        # For the sake of the test, if we can't find it (maybe trigger is slow or Azurite issue),
        # we can't proceed to approve it.
        return

    # 4. Approve the task
    print(f"[4] Approving task {task_id}...")
    try:
        response = requests.post(f"{BASE_URL}/tasks/{task_id}/status", json={"status": "COMPLETED"})
        if response.status_code == 200:
            print(f"    Approval successful: {response.json()}")
        else:
            print(f"    Approval failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"    Error approving task: {e}")

    # 5. Verify it's completed
    print("[5] Verifying completion...")
    try:
        response = requests.get(f"{BASE_URL}/tasks")
        tasks = response.json()
        found = False
        for task in tasks:
            if task['id'] == task_id:
                print(f"    Task {task_id} is still in the list with status: {task['status']}")
                if task['status'] == 'COMPLETED':
                     print("    (This is expected if the list returns all tasks, or unexpected if it filters)")
                found = True
                break
        
        if not found:
            print("    Task is no longer in the pending list. Test Passed!")
        elif found and task['status'] == 'COMPLETED':
             print("    Task is marked as COMPLETED. Test Passed!")
        else:
             print("    Task status was not updated correctly.")

    except Exception as e:
        print(f"    Error verifying: {e}")

    # Cleanup
    if os.path.exists(filename):
        os.remove(filename)

if __name__ == "__main__":
    test_full_process()
