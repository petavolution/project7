#!/usr/bin/env python3
"""
Simple Module Runner

A simplified test script that runs unified modules by listing files directly.

Usage:
    python simple_module_runner.py --list
    python simple_module_runner.py [module_name]
    
Example:
    python simple_module_runner.py unified_symbol_memory
"""

import os
import sys
import glob
import time
import importlib.util
from pathlib import Path

# Get the absolute path to the project root
project_root = str(Path(__file__).parent.parent.absolute())

# Add project root to Python path
if project_root not in sys.path:
    sys.path.insert(0, project_root)

def list_modules():
    """List all unified modules in the modules directory."""
    modules_dir = os.path.join(project_root, "modules")
    pattern = os.path.join(modules_dir, "unified_*.py")
    
    print("Available unified modules:")
    for file_path in sorted(glob.glob(pattern)):
        module_name = os.path.basename(file_path)[:-3]  # Remove the .py extension
        print(f"  - {module_name}")

def run_module(module_name):
    """Run the specified module.
    
    Args:
        module_name: Name of the module to run
    
    Returns:
        0 if successful, 1 otherwise
    """
    # Check if module exists
    module_path = os.path.join(project_root, "modules", f"{module_name}.py")
    if not os.path.exists(module_path):
        print(f"Error: Module '{module_name}' not found at {module_path}")
        return 1
        
    try:
        # Import component system
        from core.unified_component_system import ComponentFactory, UI
        
        # Import renderer
        from clients.pygame.unified_renderer import UnifiedRenderer
        
        # Import the module
        print(f"Loading module from: {module_path}")
        spec = importlib.util.spec_from_file_location(module_name, module_path)
        if not spec or not spec.loader:
            print(f"Error: Failed to load module spec for {module_name}")
            return 1
            
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        
        # Find module class
        module_class = None
        for attr_name in dir(mod):
            attr = getattr(mod, attr_name)
            if (hasattr(attr, "__module__") and 
                attr.__module__ == module_name and
                hasattr(attr, "build_ui")):
                module_class = attr
                break
        
        if not module_class:
            print(f"Error: No module class found in {module_name} with build_ui method")
            return 1
            
        # Create module instance
        module_instance = module_class()
        
        # Initialize renderer
        renderer = UnifiedRenderer(screen_width=1024, screen_height=768, title=f"MetaMindIQTrain - {module_name}")
        if not renderer.initialize():
            print("Error: Failed to initialize renderer")
            return 1
            
        # Initialize module
        if hasattr(module_instance, "initialize"):
            module_instance.initialize()
            
        # Main loop
        running = True
        last_time = time.time()
        
        while running:
            # Calculate elapsed time
            current_time = time.time()
            dt = current_time - last_time
            last_time = current_time
            
            # Update module
            if hasattr(module_instance, "update"):
                module_instance.update(dt)
                
            # Process events
            events = renderer.process_events()
            for event in events:
                if event["type"] == "quit":
                    running = False
                elif hasattr(module_instance, "handle_event"):
                    module_instance.handle_event(event)
                    
            # Build UI
            ui = UI()
            module_instance.build_ui(ui)
            
            # Render UI
            renderer.render(ui)
            
        # Shutdown module
        if hasattr(module_instance, "shutdown"):
            module_instance.shutdown()
            
        # Shutdown renderer
        renderer.shutdown()
        
        return 0
        
    except Exception as e:
        import traceback
        print(f"Error running module {module_name}: {e}")
        traceback.print_exc()
        return 1

def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python simple_module_runner.py --list")
        print("Usage: python simple_module_runner.py [module_name]")
        return 1
        
    if sys.argv[1] == "--list":
        list_modules()
        return 0
        
    return run_module(sys.argv[1])

if __name__ == "__main__":
    sys.exit(main()) 