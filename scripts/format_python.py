#!/usr/bin/env python3
# Copyright (c) 2025 Walter M. Rafelsberger
# Licensed under the MIT License. See LICENSE file for details.

"""
Combined formatter that adds license headers and runs formatting.
Usage: python scripts/format_python.py <file.py>
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(cmd, cwd=None):
    """Run a command and return success status."""
    try:
        result = subprocess.run(
            cmd, shell=True, cwd=cwd, 
            capture_output=True, text=True
        )
        return result.returncode == 0
    except Exception:
        return False

def main():
    if len(sys.argv) != 2:
        print("Usage: python format_python.py <file.py>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    
    if not file_path.endswith('.py'):
        sys.exit(0)  # Not a Python file
    
    if not os.path.exists(file_path):
        sys.exit(1)  # File doesn't exist
    
    workspace_root = Path(__file__).parent.parent
    venv_python = workspace_root / "doc2convo-env" / "bin" / "python"
    
    # Step 1: Add license header if missing
    header_cmd = f'"{venv_python}" scripts/add_license_header.py "{file_path}"'
    run_command(header_cmd, cwd=workspace_root)
    
    # Step 2: Format with isort
    isort_cmd = f'"{venv_python}" -m isort "{file_path}"'
    run_command(isort_cmd, cwd=workspace_root)
    
    # Step 3: Format with black
    black_cmd = f'"{venv_python}" -m black "{file_path}"'
    run_command(black_cmd, cwd=workspace_root)
    
    print(f"Formatted {file_path}")

if __name__ == '__main__':
    main()