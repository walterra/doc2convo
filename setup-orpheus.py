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
    
    # Install Orpheus requirements
    print("\nInstalling Orpheus TTS requirements...")
    try:
        # Change to orpheus directory and install requirements
        subprocess.run([
            sys.executable, "-m", "pip", "install", 
            "-r", "requirements.txt"
        ], cwd="orpheus-tts-local", check=True)
        print("✓ Orpheus requirements installed successfully")
    except subprocess.CalledProcessError:
        print("Error: Failed to install Orpheus requirements")
        print("Note: If you encounter issues with the 'wave' package, you can manually install:")
        print("  torch>=2.0.0 numpy>=1.20.0 sounddevice>=0.4.4 requests>=2.25.0 snac>=1.2.1")
        sys.exit(1)
    
    # Create or update .env file with PYTHONPATH
    env_file = Path(".env")
    pythonpath_line = f'PYTHONPATH="${{PYTHONPATH}}:{orpheus_dir.absolute()}"\n'
    
    if env_file.exists():
        content = env_file.read_text()
        if "orpheus-tts-local" not in content:
            print("\nUpdating .env file with PYTHONPATH...")
            with open(env_file, "a") as f:
                f.write(f"\n# Orpheus TTS support\n{pythonpath_line}")
            print("✓ .env file updated")
        else:
            print("✓ .env file already configured")
    else:
        print("\nCreating .env file with PYTHONPATH...")
        with open(env_file, "w") as f:
            f.write(f"# Orpheus TTS support\n{pythonpath_line}")
        print("✓ .env file created")
    
    print("\n✅ Orpheus TTS setup complete!")
    print("\nTo use Orpheus TTS:")
    print("1. Make sure LM Studio is running with the orpheus-3b-0.1-ft model")
    print("2. Enable API server at http://127.0.0.1:1234")
    print("3. Use --tts-engine orpheus flag with doc2md-convo.py or md-convo2mp3.py")
    print("\nNote: When running the tools, make sure to source .env or set PYTHONPATH:")
    print(f"  export {pythonpath_line.strip()}")


if __name__ == "__main__":
    main()