#!/usr/bin/env python3
"""
Script to detect and fix concatenated JSON objects in blob storage files.
Converts concatenated JSON to JSONL format (one JSON object per line).
"""

import os
import json
import glob
import re
from pathlib import Path

def detect_concatenated_json(content):
    """Detect if content has concatenated JSON objects."""
    # Try to parse as single JSON first
    try:
        json.loads(content)
        return False  # Valid single JSON
    except json.JSONDecodeError:
        pass
    
    # Check for multiple JSON objects concatenated
    # Pattern: }{" or }{"
    if re.search(r'\}\s*\{', content):
        return True
    
    # Also check for patterns like: }{"Last": or }{"Next": (timer state objects)
    if re.search(r'\}\s*\{\s*"Last"', content):
        return True
    
    return False

def split_concatenated_json(content):
    """Split concatenated JSON objects into a list."""
    objects = []
    depth = 0
    start = 0
    
    for i, char in enumerate(content):
        if char == '{':
            if depth == 0:
                start = i
            depth += 1
        elif char == '}':
            depth -= 1
            if depth == 0:
                # Found a complete JSON object
                obj_str = content[start:i+1]
                try:
                    obj = json.loads(obj_str)
                    objects.append(obj)
                except json.JSONDecodeError as e:
                    print(f"  Warning: Could not parse JSON object at position {start}: {e}")
    
    return objects

def fix_blob_file(file_path):
    """Fix a single blob file with concatenated JSON."""
    print(f"\nProcessing: {os.path.basename(file_path)}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"  Error reading file: {e}")
        return False
    
    # Check if file is empty
    if not content.strip():
        print("  File is empty, skipping")
        return False
    
    # Try to parse as single JSON first
    try:
        json.loads(content)
        print("  [OK] Valid single JSON, no fix needed")
        return False
    except json.JSONDecodeError:
        pass
    
    # Check for concatenated JSON
    is_concatenated = detect_concatenated_json(content)
    if not is_concatenated:
        # Even if not detected, try to extract multiple JSON objects
        # This handles edge cases where detection might miss the pattern
        objects = split_concatenated_json(content)
        if len(objects) > 1:
            print(f"  [INFO] Found {len(objects)} JSON objects (detection missed pattern)")
            is_concatenated = True
        elif len(objects) == 0:
            print("  [WARN] Invalid JSON but doesn't match concatenated pattern")
            print("  [ERROR] Could not extract any valid JSON objects")
            return False
        else:
            # Single object but invalid JSON - try to parse it anyway
            try:
                json.loads(content)
            except:
                print("  [WARN] Single object but invalid JSON structure")
                return False
    else:
        objects = split_concatenated_json(content)
    
    if not objects:
        print("  [ERROR] No valid JSON objects found")
        return False
    
    print(f"  Found {len(objects)} JSON object(s)")
    
    # Write as JSONL (one JSON per line)
    # For single object, keep as pretty JSON
    # For multiple objects, use JSONL format
    if len(objects) == 1:
        # Single object - write as pretty JSON
        fixed_content = json.dumps(objects[0], indent=2)
    else:
        # Multiple objects - write as JSONL (one per line)
        fixed_content = '\n'.join(json.dumps(obj) for obj in objects)
    
    # Backup original
    backup_path = f"{file_path}.backup"
    try:
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  Created backup: {os.path.basename(backup_path)}")
    except Exception as e:
        print(f"  Warning: Could not create backup: {e}")
    
    # Write fixed content
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(fixed_content)
        print(f"  [FIXED] Fixed: {len(objects)} object(s) written")
        if len(objects) > 1:
            print(f"    Format: JSONL (one JSON object per line)")
        return True
    except Exception as e:
        print(f"  [ERROR] Error writing fixed content: {e}")
        return False

def main():
    """Main function to fix all blob storage files."""
    blob_dir = Path("__blobstorage__")
    
    if not blob_dir.exists():
        print(f"Error: Directory {blob_dir} does not exist")
        return
    
    print("Scanning blob storage files for concatenated JSON...")
    print("=" * 60)
    
    blob_files = list(blob_dir.glob("*"))
    blob_files = [f for f in blob_files if f.is_file() and not f.name.endswith('.backup')]
    
    if not blob_files:
        print("No blob files found")
        return
    
    print(f"Found {len(blob_files)} file(s)")
    
    fixed_count = 0
    for blob_file in blob_files:
        if fix_blob_file(blob_file):
            fixed_count += 1
    
    print("\n" + "=" * 60)
    print(f"Summary: Fixed {fixed_count} out of {len(blob_files)} file(s)")

if __name__ == "__main__":
    main()

