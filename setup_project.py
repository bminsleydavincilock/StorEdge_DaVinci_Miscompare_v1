#!/usr/bin/env python3
"""
Project setup script for new data science projects
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"[INFO] {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"[SUCCESS] {description} completed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] {description} failed: {e.stderr}")
        return False

def setup_project():
    """Set up the data science project"""
    print("Setting up your new data science project...")
    print("=" * 50)
    
    # Check if Python is available
    if not run_command("py --version", "Checking Python installation"):
        print("[ERROR] Python is not installed or not in PATH")
        return False
    
    # Initialize Git repository
    if not os.path.exists(".git"):
        run_command("git init", "Initializing Git repository")
        run_command("git add .", "Adding files to Git")
        run_command('git commit -m "Initial commit: Project setup"', "Creating initial commit")
    else:
        print("[INFO] Git repository already exists")
    
    # Create virtual environment
    if not os.path.exists("venv"):
        if run_command("py -m venv venv", "Creating virtual environment"):
            print("[INFO] To activate the virtual environment:")
            print("   Windows: venv\\Scripts\\activate")
            print("   Mac/Linux: source venv/bin/activate")
    else:
        print("[INFO] Virtual environment already exists")
    
    # Install requirements
    if os.path.exists("requirements.txt"):
        print("[INFO] To install dependencies, run:")
        print("   pip install -r requirements.txt")
    else:
        print("[WARNING] requirements.txt not found")
    
    # Create additional directories
    directories = [
        "logs",
        "reports",
        "models",
        "data/raw",
        "data/processed", 
        "data/external"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"[INFO] Created directory: {directory}")
    
    print("\n[SUCCESS] Project setup completed!")
    print("\nNext steps:")
    print("1. Activate virtual environment:")
    print("   Windows: venv\\Scripts\\activate")
    print("   Mac/Linux: source venv/bin/activate")
    print("2. Install dependencies: pip install -r requirements.txt")
    print("3. Start Jupyter: jupyter notebook")
    print("4. Begin with notebooks/01_data_exploration.ipynb")
    
    return True

if __name__ == "__main__":
    setup_project()
