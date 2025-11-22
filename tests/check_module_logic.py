#!/usr/bin/env python3
"""
Script to check the core module logic without requiring pygame.
This will verify that the essential module functionality works properly.
"""

import sys
import os
import traceback
import uuid
import importlib
from pathlib import Path

# Add the project root to the Python path to make imports work
# Adjust path to work from tests directory
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

def print_module_info(module):
    """Print basic information about a module."""
    info = [
        f"Name: {module.name}",
        f"Description: {module.description}",
        f"Level: {module.level}",
        f"Has start_challenge: {hasattr(module, 'start_challenge')}",
        f"Has get_state: {hasattr(module, 'get_state')}",
        f"Has process_input: {hasattr(module, 'process_input')}",
    ]
    
    for item in info:
        print(f"  - {item}")

def test_core_module(module_id):
    """Test the core functionality of a module."""
    print(f"\n## Testing {module_id} module ##")
    
    try:
        # Import the module registry
        from MetaMindIQTrain.module_registry import create_module_instance
        
        # Configure display to avoid warnings
        from MetaMindIQTrain.module_registry import configure_modules_display
        configure_modules_display(1440, 1024)
        
        # Create module instance
        session_id = str(uuid.uuid4())
        module = create_module_instance(module_id, session_id)
        print(f"✅ Successfully created module instance")
        
        # Print module info
        print_module_info(module)
        
        # Test state functionality
        if hasattr(module, 'get_state'):
            state = module.get_state()
            print("\nModule state contains:")
            for key, value in state.items():
                if isinstance(value, (list, dict)) and len(str(value)) > 50:
                    print(f"  - {key}: [complex data]")
                else:
                    print(f"  - {key}: {value}")
        
        # Test starting a challenge
        if hasattr(module, 'start_challenge'):
            module.start_challenge()
            print("\n✅ Successfully started challenge")
            
            # Check state after starting challenge
            if hasattr(module, 'get_state'):
                state = module.get_state()
                print("Module state after challenge start:")
                for key in ['level', 'score']:
                    if key in state:
                        print(f"  - {key}: {state[key]}")
        
        # Test level operations
        if hasattr(module, 'advance_level'):
            original_level = module.level
            module.advance_level()
            print(f"\n✅ Advanced level: {original_level} -> {module.level}")
        
        if hasattr(module, 'reset_level'):
            module.reset_level()
            print(f"✅ Reset level: now at level {module.level}")
            
        return True
        
    except Exception as e:
        print(f"❌ Error testing {module_id} module: {e}")
        return False

def main():
    """Run tests on core module functionality."""
    print("=" * 60)
    print("TESTING MODULE LOGIC (WITHOUT PYGAME)")
    print("=" * 60)
    
    # Test each module
    modules_to_test = [
        "symbol_memory",
        "expand_vision"
    ]
    
    results = {}
    for module_id in modules_to_test:
        success = test_core_module(module_id)
        results[module_id] = "PASS" if success else "FAIL"
    
    # Print summary
    print("\n" + "=" * 60)
    print("TEST RESULTS")
    print("=" * 60)
    
    for module_id, result in results.items():
        print(f"{module_id}: {result}")
    
    print("\nNote: Pygame is required for visual rendering but missing in this environment.")
    print("The core module logic tests verify that the module functionality works properly.")

if __name__ == "__main__":
    main() 