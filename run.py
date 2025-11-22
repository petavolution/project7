#!/usr/bin/env python3
"""
MetaMindIQTrain Runner

This is the main entry point for the MetaMindIQTrain application.
It initializes and runs the application with the specified settings.
"""

import argparse
import logging
import sys
import os
import traceback
from pathlib import Path

# Ensure the package is in the path
project_root = Path(__file__).resolve().parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Configure logging to both console and debug-log.txt
DEBUG_LOG_FILE = project_root / 'debug-log.txt'

# Create detailed formatter for file
file_formatter = logging.Formatter(
    '%(asctime)s | %(levelname)-8s | %(name)-30s | %(funcName)-20s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Create simple formatter for console
console_formatter = logging.Formatter(
    '%(levelname)-8s | %(name)-20s | %(message)s'
)

# Get root logger
root_logger = logging.getLogger()
root_logger.setLevel(logging.DEBUG)

# Clear existing handlers
root_logger.handlers = []

# File handler - captures everything to debug-log.txt
try:
    file_handler = logging.FileHandler(DEBUG_LOG_FILE, mode='w', encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)
except Exception as e:
    print(f"Warning: Could not create debug log file: {e}")

# Console handler - shows info and above
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(console_formatter)
root_logger.addHandler(console_handler)

logger = logging.getLogger('MetaMindIQTrain')

def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description='Run the MetaMindIQTrain application')
    
    parser.add_argument(
        '--width', type=int, default=1024,
        help='Window width (default: 1024)'
    )
    parser.add_argument(
        '--height', type=int, default=768,
        help='Window height (default: 768)'
    )
    parser.add_argument(
        '--backend', type=str, default='auto',
        choices=['auto', 'pygame', 'webgl', 'headless'],
        help='Renderer backend (default: auto)'
    )
    parser.add_argument(
        '--module', type=str,
        help='Module to start automatically'
    )
    parser.add_argument(
        '--show-fps', action='store_true',
        help='Show FPS counter'
    )
    parser.add_argument(
        '--debug', action='store_true',
        help='Enable debug logging'
    )
    
    return parser.parse_args()

def main():
    """Run the application."""
    args = parse_args()

    # Set debug logging if requested
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        console_handler.setLevel(logging.DEBUG)
        logger.debug("Debug logging enabled")

    logger.info("=" * 60)
    logger.info("MetaMindIQTrain - Starting")
    logger.info("=" * 60)
    logger.info(f"Python version: {sys.version}")
    logger.info(f"Platform: {sys.platform}")
    logger.info(f"Project root: {project_root}")
    logger.info(f"Debug log: {DEBUG_LOG_FILE}")

    app = None

    try:
        # Import the application - try multiple approaches for robustness
        logger.debug("Importing application module...")
        try:
            from core.app import get_application
            logger.debug("Imported from core.app")
        except ImportError as e:
            logger.debug(f"Failed to import from core.app: {e}")
            try:
                from MetaMindIQTrain.core.app import get_application
                logger.debug("Imported from MetaMindIQTrain.core.app")
            except ImportError as e2:
                logger.error(f"Failed to import application: {e2}")
                raise

        # Get the application instance
        logger.debug("Getting application instance...")
        app = get_application()

        # Initialize the application
        title = "MetaMindIQTrain - Advanced Cognitive Training"
        logger.info(f"Initializing application ({args.width}x{args.height}, backend={args.backend})")
        if not app.initialize(args.width, args.height, title, args.backend):
            logger.error("Failed to initialize application")
            return 1

        logger.info(f"Application initialized with {app.renderer.get_backend_name()} backend")

        # Set FPS display if requested
        if args.show_fps:
            app.toggle_fps_display()

        # Start a module if specified
        if args.module:
            logger.info(f"Attempting to start module: {args.module}")
            if not app.start_module(args.module):
                logger.warning(f"Could not start module '{args.module}'")
                # Use the first available module as a fallback
                modules = app.list_modules()
                if modules:
                    logger.info(f"Starting fallback module: {modules[0]['id']}")
                    app.start_module(modules[0]['id'])

        # Run the application
        logger.info("Entering main loop...")
        app.run()

        # Shutdown
        logger.info("Shutting down application...")
        app.shutdown()

        logger.info("=" * 60)
        logger.info("Application exited normally")
        logger.info("=" * 60)
        return 0

    except KeyboardInterrupt:
        logger.info("Application interrupted by user (Ctrl+C)")
        if app:
            try:
                app.shutdown()
            except Exception as shutdown_error:
                logger.error(f"Error during shutdown: {shutdown_error}")
        return 0

    except Exception as e:
        logger.error(f"Fatal error: {type(e).__name__}: {e}")
        logger.debug(f"Full traceback:\n{traceback.format_exc()}")

        # Write error to debug log
        with open(DEBUG_LOG_FILE, 'a') as f:
            f.write(f"\n\n{'='*60}\n")
            f.write(f"FATAL ERROR: {type(e).__name__}: {e}\n")
            f.write(f"{'='*60}\n")
            f.write(traceback.format_exc())

        if app:
            try:
                app.shutdown()
            except Exception as shutdown_error:
                logger.error(f"Error during emergency shutdown: {shutdown_error}")

        return 1

if __name__ == "__main__":
    sys.exit(main())
 