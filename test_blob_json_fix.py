#!/usr/bin/env python3
"""
Test script to verify the blob JSON fix script handles concatenated JSON correctly.
"""

import json
import tempfile
import os
from fix_blob_json import fix_blob_file, detect_concatenated_json, split_concatenated_json

def test_concatenated_timer_states():
    """Test case based on the user's reported bug."""
    # Simulate the concatenated JSON pattern from the user's report
    # File 1: Host keys JSON + timer state JSON objects
    host_keys_json = {
        "masterKey": {
            "name": "master",
            "value": "test_value",
            "encrypted": False
        },
        "functionKeys": [],
        "systemKeys": [],
        "hostName": "localhost:7071",
        "instanceId": "test",
        "source": "runtime",
        "decryptionKeyId": ""
    }
    
    timer_states = [
        {"Last": "2025-11-21T10:00:00+01:00", "Next": "2025-11-21T10:15:00+01:00", "LastUpdated": "2025-11-21T10:00:00+01:00"},
        {"Last": "2025-11-21T14:06:31+01:00", "Next": "2025-11-21T14:15:00+01:00", "LastUpdated": "2025-11-21T14:06:31+01:00"},
        {"Last": "2025-11-21T14:15:39+01:00", "Next": "2025-11-21T14:30:00+01:00", "LastUpdated": "2025-11-21T14:15:39+01:00"}
    ]
    
    # Create concatenated content (bug pattern)
    concatenated = json.dumps(host_keys_json) + ''.join(json.dumps(ts) for ts in timer_states)
    
    print("Test 1: Host keys + timer states concatenated")
    print(f"  Content length: {len(concatenated)}")
    print(f"  Detection: {detect_concatenated_json(concatenated)}")
    
    objects = split_concatenated_json(concatenated)
    print(f"  Extracted objects: {len(objects)}")
    assert len(objects) == 4, f"Expected 4 objects, got {len(objects)}"
    print("  [PASS] Test 1 passed\n")
    
    # Test 2: Multiple timer states only (file 2 pattern)
    timer_only = ''.join(json.dumps(ts) for ts in timer_states[:2])
    
    print("Test 2: Multiple timer states concatenated")
    print(f"  Content length: {len(timer_only)}")
    print(f"  Detection: {detect_concatenated_json(timer_only)}")
    
    objects = split_concatenated_json(timer_only)
    print(f"  Extracted objects: {len(objects)}")
    assert len(objects) == 2, f"Expected 2 objects, got {len(objects)}"
    print("  [PASS] Test 2 passed\n")
    
    # Test 3: Valid single JSON (should not be modified)
    single_json = json.dumps(host_keys_json, indent=2)
    
    print("Test 3: Valid single JSON")
    print(f"  Detection: {detect_concatenated_json(single_json)}")
    assert not detect_concatenated_json(single_json), "Should not detect concatenation in valid JSON"
    print("  [PASS] Test 3 passed\n")
    
    print("All tests passed!")

if __name__ == "__main__":
    test_concatenated_timer_states()

