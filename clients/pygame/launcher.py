#!/usr/bin/env python3
"""
Launcher for the MetaMindIQTrain PyGame client.

This module provides a simple way to launch the PyGame client
with proper configuration including dark theme support.
"""

import os
import sys
import time
import logging
import argparse
from pathlib import Path

import pygame

from MetaMindIQTrain.clients.pygame.client import ModularPyGameClient

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Run the MetaMindIQTrain PyGame client."""
    parser = argparse.ArgumentParser(description="Launch MetaMindIQTrain PyGame client")
    
    parser.add_argument("--server-url", type=str, default="http://localhost:5000",
                       help="URL of the MetaMindIQTrain server")
    parser.add_argument("--width", type=int, default=1024,
                       help="Window width")
    parser.add_argument("--height", type=int, default=768,
                       help="Window height")
    parser.add_argument("--module", type=str, default=None,
                       help="Module to start directly")
    parser.add_argument("--light-theme", action="store_true",
                       help="Use light theme instead of dark theme")
    parser.add_argument("--fullscreen", action="store_true",
                       help="Run in fullscreen mode")
    
    args = parser.parse_args()
    
    try:
        # Initialize pygame
        pygame.init()
        
        # Set window title
        pygame.display.set_caption("MetaMindIQTrain")
        
        # Set icon if available
        try:
            script_dir = Path(__file__).resolve().parent
            icon_path = script_dir / "assets" / "icon.png"
            
            if icon_path.exists():
                icon = pygame.image.load(str(icon_path))
                pygame.display.set_icon(icon)
        except Exception as e:
            logger.warning(f"Could not load icon: {e}")
        
        # Create configuration
        config = {
            'server_url': args.server_url,
            'width': args.width,
            'height': args.height,
            'fullscreen': args.fullscreen,
        }
        
        # Create and run client
        client = ModularPyGameClient(config=config, dark_theme=not args.light_theme)
        
        # Connect to server
        connected = client.connect()
        
        if not connected and not args.module:
            logger.warning("Could not connect to server, starting in offline mode")
        
        # Start specific module if requested
        if args.module:
            client.start_session(args.module)
        
        # Run main loop
        client.run()
        
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
    except Exception as e:
        logger.error(f"Error running client: {e}")
        import traceback
        traceback.print_exc()
    finally:
        pygame.quit()
        logger.info("Client shutdown complete")

if __name__ == "__main__":
    main() 