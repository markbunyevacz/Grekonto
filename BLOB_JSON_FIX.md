# Blob Storage JSON Concatenation Bug Fix

## Issue Description

Azure Functions runtime blob storage files (host keys and timer state) were being written with multiple JSON objects concatenated without proper delimiters. This creates invalid JSON that cannot be parsed correctly.

### Bug 1: Host Keys File
**File**: `__blobstorage__/61101c10-ca88-4b54-b0c1-711b4ca36fa9`

**Problem**: The file contained a host keys JSON object followed by timer state JSON objects concatenated directly without separators:
```json
{
  "masterKey": {...},
  ...
}{"Last":"...","Next":"...","LastUpdated":"..."}{"Last":"...","Next":"...","LastUpdated":"..."}
```

### Bug 2: Timer State File  
**File**: `__blobstorage__/56554f8d-e581-4b7e-8847-00885225a2af`

**Problem**: Multiple timer state JSON objects concatenated on a single line:
```json
{"Last":"...","Next":"...","LastUpdated":"..."}{"Last":"...","Next":"...","LastUpdated":"..."}
```

## Root Cause

These files are managed by the Azure Functions runtime (not application code). The runtime appears to append JSON objects instead of overwriting files, causing concatenation. This is likely a bug or misconfiguration in how Azurite (local storage emulator) handles blob updates.

## Solution

Created `fix_blob_json.py` script that:
1. Detects concatenated JSON objects using pattern matching (`}{` pattern)
2. Splits concatenated JSON into individual objects
3. Writes fixed content:
   - Single object: Pretty-printed JSON (indented)
   - Multiple objects: JSONL format (one JSON object per line)

## Usage

Run the fix script to check and fix all blob storage files:
```bash
python fix_blob_json.py
```

The script will:
- Scan all files in `__blobstorage__/`
- Detect concatenated JSON
- Create backups (`.backup` files)
- Write fixed content in proper format

## Prevention

Since these files are runtime-managed, the issue may recur. Options:
1. Run `fix_blob_json.py` periodically or before reading these files
2. Monitor Azure Functions/Azurite updates that might fix the root cause
3. Consider using a different storage emulator or configuration

## Testing

Run `test_blob_json_fix.py` to verify the fix handles the reported patterns correctly:
```bash
python test_blob_json_fix.py
```

