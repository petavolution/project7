#!/usr/bin/env python3
"""
run_visual.py - Unified launcher for MetaMindIQTrain visual modules

This script provides a simple way to launch any of the visual training modules
with customizable parameters. It acts as a central entry point to make testing
and training sessions easier to start.
"""

import os
import sys
import argparse
import logging
import importlib.util
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("MetaMindIQTrain")

def import_module_from_path(module_name, file_path):
    """Import a module from a file path."""
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    if spec is None:
        return None
    
    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
        return module
    except Exception as e:
        logger.error(f"Failed to load module {module_name}: {e}")
        return None

def main():
    """Main function to parse arguments and launch the selected visual module."""
    parser = argparse.ArgumentParser(description="Run MetaMindIQTrain visual modules")
    
    parser.add_argument(
        "module",
        choices=["symbol_memory", "expand_vision", "morph_matrix", "all"],
        help="The module to run or 'all' to run all modules sequentially"
    )
    
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging"
    )
    
    parser.add_argument(
        "--duration",
        type=int,
        default=60,
        help="Duration in seconds for each module (default: 60)"
    )
    
    parser.add_argument(
        "--fullscreen",
        action="store_true",
        help="Run in fullscreen mode"
    )

    args = parser.parse_args()
    
    # Set debug logging if requested
    if args.debug:
        logger.setLevel(logging.DEBUG)
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Determine which modules to run
    modules_to_run = []
    if args.module == "all":
        modules_to_run = ["symbol_memory", "expand_vision", "morph_matrix"]
    else:
        modules_to_run = [args.module]
    
    # Run each selected module
    for module_name in modules_to_run:
        module_file = f"{module_name}_visual.py"
        if not os.path.exists(module_file):
            logger.error(f"Module file not found: {module_file}")
            continue
        
        logger.info(f"Running module: {module_name}")
        
        # Import the module
        visual_module = import_module_from_path(f"{module_name}_visual", module_file)
        if visual_module is None:
            logger.error(f"Failed to import {module_file}")
            continue
        
        # Run the module's main function with arguments
        try:
            if hasattr(visual_module, 'main'):
                visual_module.main(
                    duration=args.duration,
                    fullscreen=args.fullscreen,
                    debug=args.debug
                )
            else:
                logger.error(f"Module {module_name} does not have a main function")
        except Exception as e:
            logger.error(f"Error running {module_name}: {e}", exc_info=True)
    
    logger.info("All modules completed")

if __name__ == "__main__":
    main() 