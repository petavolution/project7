#!/usr/bin/env python3
"""
Update Test Configuration

This script updates the configuration settings used in tests.
It can be used to change things like screen dimensions across all test files.
"""

import sys
import os
from pathlib import Path

# Get the absolute path to the tests directory
TESTS_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = TESTS_DIR.parent

def print_separator(title):
    """Print a separator with a title for better readability."""
    print("\n" + "=" * 80)
    print(f" {title} ".center(80, "="))
    print("=" * 80 + "\n")

def update_config(width, height):
    """Update the configuration settings in MetaMindIQTrain/config.py.
    
    Args:
        width: New screen width
        height: New screen height
        
    Returns:
        True if the update was successful, False otherwise
    """
    config_file = PROJECT_ROOT / "MetaMindIQTrain" / "config.py"
    
    if not config_file.exists():
        print(f"Error: Config file not found at {config_file}")
        return False
    
    # Read the current config file
    with open(config_file, "r") as f:
        lines = f.readlines()
    
    # Update the screen dimensions
    new_lines = []
    for line in lines:
        if line.strip().startswith("SCREEN_WIDTH ="):
            new_lines.append(f"SCREEN_WIDTH = {width}\n")
        elif line.strip().startswith("SCREEN_HEIGHT ="):
            new_lines.append(f"SCREEN_HEIGHT = {height}\n")
        else:
            new_lines.append(line)
    
    # Write the updated config back to the file
    with open(config_file, "w") as f:
        f.writelines(new_lines)
    
    print(f"Updated screen dimensions in {config_file} to {width}x{height}")
    return True

def main():
    """Main function."""
    print_separator("UPDATE TEST CONFIGURATION")
    
    print("This script updates the configuration settings used in tests.")
    print("Current settings:")
    
    # Import current settings
    try:
        sys.path.append(str(PROJECT_ROOT))
        from MetaMindIQTrain.config import SCREEN_WIDTH, SCREEN_HEIGHT
        print(f"Screen dimensions: {SCREEN_WIDTH}x{SCREEN_HEIGHT}")
    except ImportError:
        print("Error: Could not import configuration settings")
        return 1
    
    # Ask for new dimensions
    try:
        width = input(f"Enter new screen width (current: {SCREEN_WIDTH}, press Enter to keep): ")
        width = int(width) if width else SCREEN_WIDTH
        
        height = input(f"Enter new screen height (current: {SCREEN_HEIGHT}, press Enter to keep): ")
        height = int(height) if height else SCREEN_HEIGHT
    except ValueError:
        print("Error: Width and height must be integers")
        return 1
    
    # Confirm update
    if width == SCREEN_WIDTH and height == SCREEN_HEIGHT:
        print("No changes to make.")
        return 0
    
    print(f"\nUpdating screen dimensions to {width}x{height}")
    confirm = input("Proceed? (y/n): ").lower() == 'y'
    
    if not confirm:
        print("Update cancelled.")
        return 0
    
    # Update config
    result = update_config(width, height)
    
    if result:
        print("\nConfiguration updated successfully!")
        print("You should run the tests to verify that everything works correctly with the new settings:")
        print("python tests/run_all_tests.py")
        return 0
    else:
        print("\nFailed to update configuration.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 