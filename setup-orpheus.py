#!/usr/bin/env python3
# Copyright (c) 2025 Walter M. Rafelsberger
# Licensed under the MIT License. See LICENSE file for details.

"""
Setup script for Orpheus TTS support
Clones and configures orpheus-tts-local for use with doc2convo
"""

import os
import subprocess
import sys
from pathlib import Path


def main():
    print("Setting up Orpheus TTS support for doc2convo...")
    
    # Check if orpheus-tts-local already exists
    orpheus_dir = Path("orpheus-tts-local")
    
    if orpheus_dir.exists():
        print("✓ orpheus-tts-local directory already exists")
        # In non-interactive mode or when stdin is not available, just update
        if not sys.stdin.isatty():
            print("Updating to latest version...")
            subprocess.run(["git", "-C", "orpheus-tts-local", "pull"], check=True)
        else:
            response = input("Do you want to update it? (y/n): ").lower().strip()
            if response == 'y':
                print("Pulling latest changes...")
                subprocess.run(["git", "-C", "orpheus-tts-local", "pull"], check=True)
            else:
                print("Keeping existing installation")
    else:
        print("Cloning orpheus-tts-local repository...")
        try:
            subprocess.run([
                "git", "clone", 
                "git@github.com:stanek-michal/orpheus-tts-local.git"
            ], check=True)
            print("✓ Repository cloned successfully")
        except subprocess.CalledProcessError:
            print("Error: Failed to clone repository. Make sure you have SSH access to GitHub.")
            sys.exit(1)
    
    # Fix Orpheus requirements.txt by removing the 'wave' package
    print("\nFixing Orpheus requirements.txt...")
    req_file = Path("orpheus-tts-local/requirements.txt")
    if req_file.exists():
        # Read requirements and filter out wave package
        with open(req_file, 'r') as f:
            lines = f.readlines()
        
        # Remove lines containing wave package (it's part of Python stdlib)
        filtered_lines = [line for line in lines if not line.strip().startswith('wave')]
        
        # Write back if changes were made
        if len(filtered_lines) != len(lines):
            with open(req_file, 'w') as f:
                f.writelines(filtered_lines)
            print("✓ Removed problematic 'wave' package from requirements.txt")
    
    # Install Orpheus requirements
    print("Installing Orpheus TTS requirements...")
    try:
        # Change to orpheus directory and install requirements
        subprocess.run([
            sys.executable, "-m", "pip", "install", 
            "-r", "requirements.txt"
        ], cwd="orpheus-tts-local", check=True)
        print("✓ Orpheus requirements installed successfully")
    except subprocess.CalledProcessError:
        print("Error: Failed to install Orpheus requirements")
        print("Note: If you encounter issues, you can manually install:")
        print("  torch>=2.0.0 numpy>=1.20.0 sounddevice>=0.4.4 requests>=2.25.0 snac>=1.2.1")
        sys.exit(1)
    
    print("✓ Orpheus TTS directory is ready for direct imports")
    
    print("\n✅ Orpheus TTS setup complete!")
    print("\nTo use Orpheus TTS:")
    print("1. Make sure LM Studio is running with the orpheus-3b-0.1-ft model")
    print("2. Enable API server at http://127.0.0.1:1234")
    print("3. Use --tts-engine orpheus flag with doc2md-convo.py or md-convo2mp3.py")
    print("\nNote: The tools will automatically import from the local orpheus-tts-local directory.")


if __name__ == "__main__":
    main()