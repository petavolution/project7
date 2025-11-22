#!/usr/bin/env python3
"""
MVC Module Check Utility for MetaMindIQTrain

This script performs comprehensive checks on all MVC-based modules to ensure
they can be properly loaded and run. It tests module instantiation,
state generation, and basic functionality without requiring a UI.

Usage:
    python check_all_mvc_modules.py [--verbose] [--headless]

Options:
    --verbose: Enable detailed output
    --headless: Run in headless mode (no pygame window)
"""

import os
import sys
import time
import argparse
import importlib
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Set

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Process command line arguments
parser = argparse.ArgumentParser(description="Check all MVC modules in the MetaMindIQTrain system")
parser.add_argument("--verbose", action="store_true", help="Enable detailed output")
parser.add_argument("--headless", action="store_true", help="Run in headless mode")
args = parser.parse_args()

# Enable headless mode if requested
if args.headless:
    os.environ["SDL_VIDEODRIVER"] = "dummy"
    os.environ["SDL_AUDIODRIVER"] = "dummy"

# Initialize results dictionary
results = {
    "passed": [],
    "failed": [],
    "warnings": []
}

def print_header(text):
    """Print a header with decorative formatting."""
    print("\n" + "=" * 80)
    print(f" {text} ".center(80, "="))
    print("=" * 80)

def print_subheader(text):
    """Print a subheader with decorative formatting."""
    print("\n" + "-" * 80)
    print(f" {text} ".center(80, "-"))
    print("-" * 80)

def print_result(name, success, message=""):
    """Print a result with decorative formatting."""
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{status} | {name}{': ' + message if message else ''}")
    
    # Update results
    if success:
        results["passed"].append(name)
    else:
        results["failed"].append((name, message))

def print_warning(name, message):
    """Print a warning with decorative formatting."""
    print(f"⚠️ WARN | {name}: {message}")
    results["warnings"].append((name, message))

def print_verbose(message):
    """Print a message only when verbose mode is enabled."""
    if args.verbose:
        print(f"  INFO | {message}")

print_header("MetaMindIQTrain MVC Module Check")
print(f"Checking MVC modules in: {project_root}")
print(f"Running in {'headless' if args.headless else 'normal'} mode")
print(f"Verbose output: {'enabled' if args.verbose else 'disabled'}")

# Modules to check
mvc_modules = [
    {
        "name": "SymbolMemory MVC",
        "import_path": "MetaMindIQTrain.modules.symbol_memory_mvc", 
        "class_name": "SymbolMemory",
        "args": {"difficulty": 3}
    },
    {
        "name": "MorphMatrix MVC",
        "import_path": "MetaMindIQTrain.modules.morph_matrix_mvc",
        "class_name": "MorphMatrix",
        "args": {"difficulty": 3}
    },
    {
        "name": "ExpandVision MVC",
        "import_path": "MetaMindIQTrain.modules.expand_vision_mvc",
        "class_name": "ExpandVision",
        "args": {"screen_width": 1024, "screen_height": 768}
    }
]

# Try to import pygame without initializing it yet
try:
    import pygame
    pygame_available = True
except ImportError:
    pygame_available = False
    print_warning("Pygame", "Pygame is not available. Running with limited functionality.")

# Check if modules can be imported
print_subheader("Module Import Check")

for module_info in mvc_modules:
    name = module_info["name"]
    import_path = module_info["import_path"]
    
    try:
        print_verbose(f"Importing {import_path}")
        module = importlib.import_module(import_path)
        print_result(name, True, "Module imported successfully")
    except Exception as e:
        print_result(name, False, f"Import failed: {str(e)}")
        continue
    
    # Check if class exists in the module
    try:
        class_name = module_info["class_name"]
        class_obj = getattr(module, class_name)
        print_verbose(f"Found class {class_name} in {import_path}")
    except AttributeError:
        print_result(f"{name} - Class Check", False, f"Class {class_name} not found in module")

# Initialize pygame if available and not in headless mode
if pygame_available and not args.headless:
    pygame.init()
    pygame.display.set_mode((800, 600))

# Check if modules can be instantiated
print_subheader("Module Instantiation Check")

for module_info in mvc_modules:
    name = module_info["name"]
    import_path = module_info["import_path"]
    class_name = module_info["class_name"]
    
    try:
        # Import the module
        module = importlib.import_module(import_path)
        class_obj = getattr(module, class_name)
        
        # Instantiate the class
        args_dict = module_info["args"]
        print_verbose(f"Instantiating {class_name} with args: {args_dict}")
        instance = class_obj(**args_dict)
        print_result(name, True, "Module instantiated successfully")
        
        # Check for MVC components
        if hasattr(instance, "model") and hasattr(instance, "view") and hasattr(instance, "controller"):
            print_verbose("Module has all MVC components")
        else:
            missing = []
            if not hasattr(instance, "model"):
                missing.append("model")
            if not hasattr(instance, "view"):
                missing.append("view")
            if not hasattr(instance, "controller"):
                missing.append("controller")
            print_warning(name, f"Missing MVC components: {', '.join(missing)}")
    except Exception as e:
        print_result(name, False, f"Instantiation failed: {str(e)}")
        continue

# Check if modules can generate state
print_subheader("State Generation Check")

for module_info in mvc_modules:
    name = module_info["name"]
    import_path = module_info["import_path"]
    class_name = module_info["class_name"]
    
    try:
        # Import and instantiate the module
        module = importlib.import_module(import_path)
        class_obj = getattr(module, class_name)
        instance = class_obj(**module_info["args"])
        
        # Generate state
        print_verbose(f"Generating state for {name}")
        state = instance.get_state()
        
        if state is None:
            print_result(name, False, "Module returned None state")
            continue
            
        # Check that state has expected components
        if "components" not in state:
            print_result(name, False, "State missing 'components' key")
            continue
            
        print_result(name, True, f"State generated with {len(state['components'])} components")
        
        # Print some details about the state
        if args.verbose:
            component_types = {}
            for component in state["components"]:
                component_type = component.get("type", "unknown")
                if component_type in component_types:
                    component_types[component_type] += 1
                else:
                    component_types[component_type] = 1
            print_verbose(f"Component types: {component_types}")
    except Exception as e:
        print_result(name, False, f"State generation failed: {str(e)}")
        continue

# Check if modules can handle clicks
print_subheader("Click Handling Check")

for module_info in mvc_modules:
    name = module_info["name"]
    import_path = module_info["import_path"]
    class_name = module_info["class_name"]
    
    try:
        # Import and instantiate the module
        module = importlib.import_module(import_path)
        class_obj = getattr(module, class_name)
        instance = class_obj(**module_info["args"])
        
        # Generate initial state
        initial_state = instance.get_state()
        
        # Simulate a click in the center of the screen
        screen_width = module_info["args"].get("screen_width", 1024)
        screen_height = module_info["args"].get("screen_height", 768)
        center_x = screen_width // 2
        center_y = screen_height // 2
        
        print_verbose(f"Simulating click at ({center_x}, {center_y})")
        instance.handle_click(center_x, center_y)
        
        # Check for state changes
        updated_state = instance.get_state()
        state_changed = initial_state != updated_state
        
        # Some modules might not change state on every click,
        # so we'll just report rather than consider it a failure
        if state_changed:
            print_result(name, True, "State changed after click")
        else:
            print_warning(name, "State did not change after click (might be normal)")
    except Exception as e:
        print_result(name, False, f"Click handling failed: {str(e)}")
        continue

# Clean up pygame if initialized
if pygame_available and not args.headless:
    pygame.quit()

# Print summary
print_subheader("Test Summary")
print(f"Passed: {len(results['passed'])}")
print(f"Failed: {len(results['failed'])}")
print(f"Warnings: {len(results['warnings'])}")

if results['failed']:
    print("\nFailed tests:")
    for name, message in results['failed']:
        print(f"  • {name}: {message}")

if results['warnings']:
    print("\nWarnings:")
    for name, message in results['warnings']:
        print(f"  • {name}: {message}")

if not results['failed']:
    print("\n✅ All critical tests passed!")
else:
    print("\n❌ Some tests failed!")
    sys.exit(1)

print_header("MVC Module Check Complete") 