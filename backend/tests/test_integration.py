import requests
import time
import os
import unittest
import json

BASE_URL = "http://localhost:7071/api"

class TestIntegration(unittest.TestCase):

    def setUp(self):
        # Ensure backend is running
        try:
            requests.get(f"{BASE_URL}/settings/sources")
        except requests.exceptions.ConnectionError:
            self.fail("Backend is not running. Please start 'func start' in backend folder.")

    def test_full_process_flow(self):
        print("\n--- Starting Integration Test ---")

        # 1. Create a dummy invoice file
        filename = "integration_test_invoice.pdf"
        with open(filename, "wb") as f:
            f.write(b"%PDF-1.4 dummy content for integration testing")
        
        print(f"[1] Created dummy file: {filename}")

        # 2. Upload the file
        print("[2] Uploading file...")
        with open(filename, "rb") as f:
            # Using multipart/form-data as per new implementation
            files = {'file': (filename, f, 'application/pdf')}
            response = requests.post(f"{BASE_URL}/upload", files=files)
        
        self.assertEqual(response.status_code, 200, f"Upload failed: {response.text}")
        print(f"    Upload successful: {response.json()}")

        # 3. Poll for the task to appear
        print("[3] Waiting for processing...")
        task_id = None
        found_task = None
        
        for i in range(15): # Wait up to 30 seconds
            try:
                response = requests.get(f"{BASE_URL}/tasks")
                if response.status_code == 200:
                    tasks = response.json()
                    # Look for our file
                    for task in tasks:
                        # Check if ID contains our filename (sanitized)
                        if filename.replace('.', '_') in task['id']:
                            found_task = task
                            task_id = task['id']
                            break
                    
                    if task_id:
                        break
                
                time.sleep(2)
            except Exception as e:
                print(f"    Error polling tasks: {e}")
                time.sleep(2)

        self.assertIsNotNone(task_id, "Timeout: Task did not appear in the list.")
        print(f"    Found processed task! ID: {task_id}")
        print(f"    Status: {found_task['status']}")

        # 4. Validate Extracted Data (Mocked in this environment, but checking structure)
        print("[4] Validating Extracted Data...")
        extracted = found_task.get('extracted', {})
        self.assertIn('vendor', extracted)
        self.assertIn('amount', extracted)
        # Since we don't have real OCR, we expect the fallback "Mock Vendor" or similar if configured
        # or empty if OCR failed gracefully.
        # Based on previous grep, fallback is "Mock Vendor"
        if extracted.get('vendor') == "Mock Vendor":
             print("    Confirmed Mock Vendor extraction (Fallback active).")

        # 5. Validate Matching Logic
        print("[5] Validating Matching Logic...")
        # We expect RED or YELLOW depending on mock data.
        # If "Mock Vendor" is used, it might not match anything in the mock NAV items unless we added one.
        # Let's just assert it has a status.
        self.assertIn(found_task['status'], ['RED', 'YELLOW', 'GREEN'])

        # 6. Approve the task
        print(f"[6] Approving task {task_id}...")
        response = requests.post(f"{BASE_URL}/tasks/{task_id}/status", json={"status": "COMPLETED"})
        self.assertEqual(response.status_code, 200, f"Approval failed: {response.text}")

        # 7. Verify it's completed
        print("[7] Verifying completion...")
        # Wait a moment for update to propagate if needed (Table Storage is fast though)
        time.sleep(1)
        
        response = requests.get(f"{BASE_URL}/tasks")
        tasks = response.json()
        updated_task = next((t for t in tasks if t['id'] == task_id), None)
        
        # Depending on implementation, completed tasks might be removed from "pending" list
        # or stay with status COMPLETED.
        # The get_pending_tasks function filters by YELLOW or RED.
        # So it should disappear from the list.
        
        if updated_task:
            self.assertNotEqual(updated_task['status'], 'COMPLETED', "Task found in pending list but has COMPLETED status (Should be filtered out)")
            # If it's still there, it must not be completed?
            # Actually, if get_pending_tasks filters by status, and we updated it to COMPLETED,
            # it should NOT be in the list returned by get_pending_tasks.
            pass 
        else:
            print("    Task correctly removed from pending list.")

        # Cleanup
        if os.path.exists(filename):
            os.remove(filename)

if __name__ == '__main__':
    unittest.main()
