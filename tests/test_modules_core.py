#!/usr/bin/env python3

"""
Test core module functionality without requiring pygame.
This script checks if all modules can be loaded and their core functionality works correctly.
"""

import sys
import os
import traceback
from importlib import import_module
from pathlib import Path

# Add the project root to the Python path to make imports work
# Adjust path to work from tests directory
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

def print_separator(title):
    """Print a separator with a title for better readability."""
    print("\n" + "=" * 80)
    print(f" {title} ".center(80, "="))
    print("=" * 80 + "\n")

def test_module(module_name):
    """Test a specific module's core functionality."""
    print(f"Testing module: {module_name}")
    try:
        # Import the module registry
        from MetaMindIQTrain.module_registry import create_module_instance, configure_modules_display
        
        # Set mock display settings to avoid pygame
        os.environ['SDL_VIDEODRIVER'] = 'dummy'
        
        # Configure display settings
        configure_modules_display(1280, 720)
        
        # Create a module instance
        module_instance = create_module_instance(module_name, "test_session_123")
        
        if module_instance:
            print(f"✓ Successfully created module instance for {module_name}")
            print(f"  - Level: {module_instance.level}")
            print(f"  - Score: {module_instance.score}")
            print(f"  - Message: {module_instance.message}")
            
            # Test module state
            print("\nTesting module state...")
            if hasattr(module_instance, 'initialize_state'):
                module_instance.initialize_state()
                print(f"✓ State initialized")
            else:
                print(f"! No initialize_state method found, using current state")
            
            # Test starting a challenge
            print("\nTesting challenge functionality...")
            if hasattr(module_instance, 'start_challenge'):
                module_instance.start_challenge()
                print(f"✓ Challenge started")
                print(f"  - New level: {module_instance.level}")
            else:
                print(f"! No start_challenge method found")
            
            return True
        else:
            print(f"✗ Failed to create module instance for {module_name}")
            return False
    except Exception as e:
        print(f"✗ Error testing {module_name}: {e}")
        traceback.print_exc()
        return False

def main():
    """Main function to test all modules."""
    print_separator("META MIND IQ TRAIN - CORE MODULE TEST")
    
    # List of modules to test
    modules_to_test = ["symbol_memory", "expand_vision", "morph_matrix"]
    
    # Test results
    results = {}
    
    for module_name in modules_to_test:
        print_separator(f"TESTING MODULE: {module_name}")
        results[module_name] = test_module(module_name)
    
    # Print summary
    print_separator("TEST SUMMARY")
    for module_name, result in results.items():
        status = "PASS" if result else "FAIL"
        print(f"{module_name}: {status}")
    
    # Overall result
    if all(results.values()):
        print("\nAll module core functionality tests passed!")
    else:
        print("\nSome module tests failed. See details above.")

if __name__ == "__main__":
    main() 