#!/usr/bin/env python3
# Copyright (c) 2025 Walter M. Rafelsberger
# Licensed under the MIT License. See LICENSE file for details.

"""
Script to add license headers to Python files.
Usage: python scripts/add_license_header.py [file1.py] [file2.py] ...
       python scripts/add_license_header.py --all  # Process all .py files
"""

import argparse
import os
import sys
from pathlib import Path

LICENSE_HEADER = """# Copyright (c) 2025 Walter M. Rafelsberger
# Licensed under the MIT License. See LICENSE file for details.
"""

def has_license_header(content):
    """Check if file already has a license header."""
    lines = content.split('\n')
    for line in lines[:10]:  # Check first 10 lines
        if 'Copyright' in line and 'Walter M. Rafelsberger' in line:
            return True
    return False

def add_license_header(file_path):
    """Add license header to a Python file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if has_license_header(content):
            print(f"✓ {file_path} already has license header")
            return False
        
        lines = content.split('\n')
        
        # Find insertion point (after shebang if present)
        insert_line = 0
        if lines and lines[0].startswith('#!'):
            insert_line = 1
        
        # Insert license header
        new_lines = (
            lines[:insert_line] + 
            [LICENSE_HEADER.strip()] + 
            [''] + 
            lines[insert_line:]
        )
        
        new_content = '\n'.join(new_lines)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f"✓ Added license header to {file_path}")
        return True
        
    except Exception as e:
        print(f"✗ Error processing {file_path}: {e}")
        return False

def find_python_files(directory='.'):
    """Find all Python files that are tracked by git."""
    import subprocess
    
    try:
        # Get all git-tracked files
        result = subprocess.run(['git', 'ls-files'], 
                              capture_output=True, text=True, check=True)
        git_files = result.stdout.strip().split('\n')
        
        # Filter for Python files
        python_files = [f for f in git_files if f.endswith('.py')]
        
        return python_files
        
    except subprocess.CalledProcessError:
        print("Warning: Not in a git repository or git command failed")
        # Fallback to directory walking with exclusions
        python_files = []
        for root, dirs, files in os.walk(directory):
            # Skip virtual environments and other directories
            dirs[:] = [d for d in dirs if d not in ['doc2convo-env', '.git', '__pycache__', '.venv', 'node_modules']]
            
            for file in files:
                if file.endswith('.py'):
                    python_files.append(os.path.join(root, file))
        
        return python_files

def main():
    parser = argparse.ArgumentParser(description='Add license headers to Python files')
    parser.add_argument('files', nargs='*', help='Python files to process')
    parser.add_argument('--all', action='store_true', help='Process all Python files in project')
    
    args = parser.parse_args()
    
    if args.all:
        files = find_python_files()
        print(f"Found {len(files)} Python files")
    elif args.files:
        files = args.files
    else:
        print("Error: Specify files or use --all flag")
        sys.exit(1)
    
    processed = 0
    modified = 0
    
    for file_path in files:
        if not os.path.exists(file_path):
            print(f"✗ File not found: {file_path}")
            continue
        
        processed += 1
        if add_license_header(file_path):
            modified += 1
    
    print(f"\nProcessed {processed} files, modified {modified} files")

if __name__ == '__main__':
    main()