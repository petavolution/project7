#!/usr/bin/env python3
"""
Direct Module Runner

A simple script to run a module directly, bypassing the module system.
Uses absolute imports to avoid import issues.

Usage:
    python run_module_direct.py unified_symbol_memory
"""

import os
import sys
import time
import logging
import importlib.util
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("direct_runner")

# Project setup
project_root = Path(__file__).parent.parent.absolute()
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root.parent))

def run_module(module_name):
    """Run the module directly.
    
    Args:
        module_name: Name of the module to run
    """
    try:
        # Import directly from files to avoid package issues
        logger.info(f"Loading module: {module_name}")
        
        # Import component system
        component_path = project_root / "core" / "unified_component_system.py"
        logger.info(f"Loading component system from: {component_path}")
        
        comp_spec = importlib.util.spec_from_file_location(
            "unified_component_system", component_path)
        comp_module = importlib.util.module_from_spec(comp_spec)
        comp_spec.loader.exec_module(comp_module)
        
        # Get required classes from component system
        Component = comp_module.Component
        UI = comp_module.UI
        ComponentFactory = comp_module.ComponentFactory
        
        # Import renderer
        renderer_path = project_root / "clients" / "pygame" / "unified_renderer.py"
        logger.info(f"Loading renderer from: {renderer_path}")
        
        renderer_spec = importlib.util.spec_from_file_location(
            "unified_renderer", renderer_path)
        renderer_module = importlib.util.module_from_spec(renderer_spec)
        renderer_spec.loader.exec_module(renderer_module)
        
        # Get renderer class
        UnifiedRenderer = renderer_module.UnifiedRenderer
        
        # Load the module
        module_path = project_root / "modules" / f"{module_name}.py"
        logger.info(f"Loading module from: {module_path}")
        
        if not module_path.exists():
            logger.error(f"Module not found: {module_path}")
            return False
            
        mod_spec = importlib.util.spec_from_file_location(module_name, module_path)
        mod = importlib.util.module_from_spec(mod_spec)
        mod_spec.loader.exec_module(mod)
        
        # Find the module class
        module_class = None
        for attr_name in dir(mod):
            attr = getattr(mod, attr_name)
            if (hasattr(attr, "__module__") and 
                attr.__module__ == module_name and
                hasattr(attr, "build_ui")):
                module_class = attr
                break
        
        if not module_class:
            logger.error(f"No module class found in {module_name}")
            return False
            
        logger.info(f"Found module class: {module_class.__name__}")
        
        # Create module instance
        module_instance = module_class()
        
        # Initialize renderer
        renderer = UnifiedRenderer(
            screen_width=1024,
            screen_height=768,
            title=f"MetaMindIQTrain - {module_name}"
        )
        
        if not renderer.initialize():
            logger.error("Failed to initialize renderer")
            return False
            
        # Initialize module
        if hasattr(module_instance, "initialize"):
            logger.info("Initializing module")
            module_instance.initialize()
            
        # Main loop
        logger.info("Starting main loop")
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
            
            # Render UI - convert to state dictionary
            state = {"ui": ui.to_dict() if hasattr(ui, "to_dict") else ui}
            renderer.render(state)
            
        # Shutdown
        logger.info("Shutting down")
        if hasattr(module_instance, "shutdown"):
            module_instance.shutdown()
            
        renderer.shutdown()
        return True
        
    except Exception as e:
        import traceback
        logger.error(f"Error running module {module_name}: {e}")
        traceback.print_exc()
        return False
        
def main():
    if len(sys.argv) < 2:
        print("Usage: python run_module_direct.py MODULE_NAME")
        return 1
        
    module_name = sys.argv[1]
    success = run_module(module_name)
    return 0 if success else 1
    
if __name__ == "__main__":
    sys.exit(main()) 