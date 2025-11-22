#!/usr/bin/env python3
"""
Setup Executable Permissions

This script finds all Python files in the project and marks them as executable.
"""

import os
import sys
import subprocess
from pathlib import Path

# Get project root
project_root = Path(__file__).parent.parent.absolute()


def mark_as_executable(file_path):
    """Mark a file as executable using chmod +x.
    
    Args:
        file_path: Path to the file
        
    Returns:
        True if successful, False otherwise
    """
    try:
        os.chmod(file_path, os.stat(file_path).st_mode | 0o111)
        print(f"Made executable: {file_path}")
        return True
    except Exception as e:
        print(f"Error making {file_path} executable: {e}")
        return False


def find_python_files():
    """Find all Python files in the project.
    
    Returns:
        List of Path objects for Python files
    """
    python_files = []
    
    # Find Python files
    for root, dirs, files in os.walk(project_root):
        # Skip __pycache__ and virtual environment directories
        if "__pycache__" in root or "venv" in root or ".venv" in root:
            continue
            
        for file in files:
            if file.endswith(".py"):
                file_path = Path(root) / file
                python_files.append(file_path)
    
    return python_files


def setup_executables():
    """Make all Python files executable."""
    python_files = find_python_files()
    
    # Priority files that should definitely be executable
    priority_files = [
        "run_unified_client.py",
        "unified_symbol_memory.py",
        "unified_morph_matrix.py",
        "unified_expand_vision.py",
        "test_modules.py",
        "test_component_system.py"
    ]
    
    # First handle priority files
    priority_paths = []
    for python_file in python_files:
        if python_file.name in priority_files:
            priority_paths.append(python_file)
    
    # Mark priority files as executable
    print("Making priority files executable...")
    for file_path in priority_paths:
        mark_as_executable(file_path)
    
    # Now handle all other Python files
    print("\nMaking all Python files executable...")
    success_count = 0
    for file_path in python_files:
        if file_path in priority_paths:
            continue  # Skip already processed priority files
            
        if mark_as_executable(file_path):
            success_count += 1
    
    print(f"\nMade {success_count} out of {len(python_files)} Python files executable")
    print(f"Priority files: {len(priority_paths)}")
    print(f"Total files processed: {len(python_files)}")


if __name__ == "__main__":
    print(f"Setting up executable permissions for Python files in {project_root}")
    setup_executables()
    print("Done!") 