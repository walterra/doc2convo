#!/usr/bin/env python3
# Copyright (c) 2025 Walter M. Rafelsberger
# Licensed under the MIT License. See LICENSE file for details.

"""
Fast license header checker for VS Code integration.
Returns exit code 0 if header exists, 1 if missing.
"""

import sys
import os

LICENSE_HEADER_LINES = [
    "# Copyright (c) 2025 Walter M. Rafelsberger",
    "# Licensed under the MIT License. See LICENSE file for details."
]

def has_license_header(file_path):
    """Check if file has license header."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Look for license header in first 10 lines
        file_content = ''.join(lines[:10])
        
        return all(line.strip() in file_content for line in LICENSE_HEADER_LINES)
    
    except Exception:
        return False

def main():
    if len(sys.argv) != 2:
        print("Usage: python check_license_header.py <file.py>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    
    if not file_path.endswith('.py'):
        sys.exit(0)  # Not a Python file, skip
    
    if not os.path.exists(file_path):
        sys.exit(1)  # File doesn't exist
    
    if has_license_header(file_path):
        sys.exit(0)  # Header exists
    else:
        sys.exit(1)  # Header missing

if __name__ == '__main__':
    main()