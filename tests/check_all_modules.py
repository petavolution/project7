#!/usr/bin/env python3
"""
Check All Modules

This script checks whether all modules can be successfully loaded and created.
It prints information about each module and tests basic functionality.
"""

import sys
import os
import importlib
import uuid
from pathlib import Path

# Add the project root to the Python path to make imports work
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

# Try to import pygame, but don't fail if not available
PYGAME_AVAILABLE = False
try:
    import pygame
    print(f"pygame-ce {pygame.__version__} (SDL {pygame.get_sdl_version()})")
    print(f"Using {pygame.__name__} {pygame.__version__}")
    PYGAME_AVAILABLE = True
except ImportError:
    print("Warning: pygame not available, running in headless mode")

def print_separator(message):
    """Print a separator with a centered message."""
    print("\n" + "=" * 80)
    print(message.center(80))
    print("=" * 80)

def check_module(module_id):
    """Check if a module can be loaded and created.
    
    Args:
        module_id: The ID of the module to check
        
    Returns:
        tuple: (success, module) where success is a bool and module is the module instance or None
    """
    try:
        # Import the module registry
        from MetaMindIQTrain.module_registry import create_module_instance
        
        # Create module instance
        session_id = str(uuid.uuid4())
        module = create_module_instance(module_id, session_id)
        
        # Print module info
        print(f"✓ Successfully loaded module: {module.name}")
        print(f"  - ID: {module_id}")
        print(f"  - Description: {module.description}")
        print(f"  - Level: {module.level}")
        
        # Test module functionality
        if hasattr(module, 'start_challenge'):
            module.start_challenge()
            print(f"✓ Module.start_challenge() executed successfully")
        
        if hasattr(module, 'advance_level'):
            original_level = module.level
            module.advance_level()
            print(f"✓ Module.advance_level() executed successfully (Level {original_level} -> {module.level})")
            
        return True, module
    except Exception as e:
        print(f"✗ Error loading module {module_id}: {e}")
        return False, None

def main():
    """Run the module check."""
    print_separator("CHECKING ALL METAMINDIQTRAIN MODULES")
    
    # Configure display settings for all modules
    from MetaMindIQTrain.module_registry import configure_modules_display
    configure_modules_display(1440, 1024)
    
    # Initialize pygame if available (for modules that require it)
    if PYGAME_AVAILABLE:
        pygame.init()
        # Create a dummy screen for pygame (hidden)
        screen = pygame.display.set_mode((1, 1), pygame.HIDDEN)
    
    # List of modules to check
    modules = [
        "test_module",
        "morph_matrix", 
        "expand_vision",
        "symbol_memory"
    ]
    
    # Check each module
    results = {}
    for module_id in modules:
        print_separator(f"CHECKING MODULE: {module_id}")
        success, _ = check_module(module_id)
        results[module_id] = "PASS" if success else "FAIL"
    
    # Print summary
    print_separator("TEST RESULTS SUMMARY")
    
    for module_id, result in results.items():
        print(f"{module_id}: {result}")
    
    # Calculate overall result
    total = len(results)
    passed = sum(1 for result in results.values() if result == "PASS")
    
    print(f"\nTotal modules: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {total - passed}")
    
    if passed == total:
        print("\nAll modules passed the basic loading test!")
    
    # Clean up pygame if it was initialized
    if PYGAME_AVAILABLE:
        pygame.quit()

if __name__ == "__main__":
    main() 