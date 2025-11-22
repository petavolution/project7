#!/usr/bin/env python3
"""
PyGame Client for MetaMindIQTrain

This is the main client for the PyGame implementation of MetaMindIQTrain.
It handles initialization, event processing, module loading, and rendering.
"""

import pygame
import sys
import logging
import time
import os
from typing import Dict, Any, Optional, List, Tuple

# Try to import from the package first
try:
    from MetaMindIQTrain.core.theme import Theme, get_theme, set_theme
    from MetaMindIQTrain.core.config import load_config
    from MetaMindIQTrain.clients.pygame.renderer_manager import (
        RendererManager, get_renderer, get_adapter, 
        update_performance_metrics, render_debug_overlay
    )
except ImportError:
    # For direct execution during development
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))
    from core.theme import Theme, get_theme, set_theme
    from core.config import load_config
    from clients.pygame.renderer_manager import (
        RendererManager, get_renderer, get_adapter, 
        update_performance_metrics, render_debug_overlay
    )

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PyGameClient:
    """Main client for the PyGame implementation."""
    
    def __init__(self, width=1440, height=1024, fullscreen=False, theme=None, config_path=None):
        """Initialize the PyGame client.
        
        Args:
            width: Screen width (default: 1440)
            height: Screen height (default: 1024)
            fullscreen: Whether to start in fullscreen mode
            theme: Theme to use (optional)
            config_path: Path to configuration file (optional)
        """
        # Initialize PyGame
        pygame.init()
        
        # Load configuration
        self.config = load_config(config_path) if config_path else {}
        
        # Apply configuration settings
        width = self.config.get('screen_width', width)
        height = self.config.get('screen_height', height)
        fullscreen = self.config.get('fullscreen', fullscreen)
        
        # Set up display
        flags = pygame.HWSURFACE | pygame.DOUBLEBUF
        if fullscreen:
            flags |= pygame.FULLSCREEN
        
        # Create screen
        self.screen = pygame.display.set_mode((width, height), flags)
        pygame.display.set_caption("MetaMindIQTrain")
        
        # Set up clock for frame rate limiting
        self.clock = pygame.time.Clock()
        self.target_fps = self.config.get('fps', 60)
        
        # Initialize renderer manager
        self.renderer_manager = RendererManager.get_instance(self.screen, theme)
        
        # Active module state
        self.active_module = None
        self.active_renderer = None
        self.active_adapter = None
        
        # Application state
        self.running = True
        self.paused = False
        self.show_debug = self.config.get('show_debug', False)
        
        # Set up theme if provided
        if theme:
            set_theme(theme)
            
        # Set up assets path
        self.assets_path = os.path.join(os.path.dirname(__file__), '..', '..', 'assets')
        
        logger.info(f"PyGame client initialized: {width}x{height}, fps={self.target_fps}")
    
    def load_module(self, module_id):
        """Load a module.
        
        Args:
            module_id: ID of the module to load
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Clean up previous module if any
            self.unload_current_module()
            
            # Create new renderer and adapter
            self.active_renderer = get_renderer(module_id, self.screen)
            self.active_adapter = get_adapter(module_id, self.screen)
            
            # Set active module
            self.active_module = module_id
            
            logger.info(f"Module loaded: {module_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error loading module {module_id}: {e}")
            return False
    
    def unload_current_module(self):
        """Unload the current module."""
        if self.active_module:
            logger.info(f"Unloading module: {self.active_module}")
            
            # Clean up renderer and adapter if any
            self.active_renderer = None
            self.active_adapter = None
            
            # Clear active module
            self.active_module = None
    
    def handle_events(self):
        """Handle PyGame events.
        
        Returns:
            True if should continue running, False if should exit
        """
        for event in pygame.event.get():
            # Handle quit event
            if event.type == pygame.QUIT:
                return False
            
            # Handle key events
            if event.type == pygame.KEYDOWN:
                # ESC to quit
                if event.key == pygame.K_ESCAPE:
                    return False
                
                # F1 to toggle debug info
                if event.key == pygame.K_F1:
                    self.show_debug = not self.show_debug
                
                # F11 to toggle fullscreen
                if event.key == pygame.K_F11:
                    self.toggle_fullscreen()
                
                # F5 to reload module
                if event.key == pygame.K_F5 and self.active_module:
                    self.load_module(self.active_module)
                
                # Space to pause
                if event.key == pygame.K_SPACE:
                    self.paused = not self.paused
            
            # Handle window resize
            if event.type == pygame.VIDEORESIZE:
                self.on_resize(event.w, event.h)
            
            # Pass event to active module
            if self.active_adapter:
                result = self.active_adapter.handle_event(event)
                if result and isinstance(result, dict) and 'action' in result:
                    # Handle module actions
                    action = result['action']
                    if action == 'quit':
                        return False
                    elif action == 'reload':
                        self.load_module(self.active_module)
                    elif action == 'load_module' and 'module_id' in result:
                        self.load_module(result['module_id'])
        
        return True
    
    def toggle_fullscreen(self):
        """Toggle fullscreen mode."""
        # Get current display info
        info = pygame.display.Info()
        current_w, current_h = info.current_w, info.current_h
        
        # Toggle fullscreen flag
        is_fullscreen = bool(pygame.display.get_surface().get_flags() & pygame.FULLSCREEN)
        new_flags = pygame.HWSURFACE | pygame.DOUBLEBUF
        
        if not is_fullscreen:
            # Switch to fullscreen
            new_flags |= pygame.FULLSCREEN
            self.screen = pygame.display.set_mode((0, 0), new_flags)
        else:
            # Switch to windowed
            self.screen = pygame.display.set_mode((1440, 1024), new_flags)
        
        # Update renderer manager with new screen
        new_w, new_h = self.screen.get_size()
        self.on_resize(new_w, new_h)
    
    def on_resize(self, width, height):
        """Handle window resize.
        
        Args:
            width: New screen width
            height: New screen height
        """
        # Update renderer manager
        self.renderer_manager.handle_resize(width, height)
        
        # Reload current module if any
        if self.active_module:
            self.load_module(self.active_module)
    
    def render(self):
        """Render the current frame."""
        # Clear screen
        self.screen.fill((0, 0, 0))
        
        # Render active module if any
        if self.active_renderer and not self.paused:
            self.active_renderer.render({"module_id": self.active_module})
        elif self.active_adapter and not self.paused:
            self.active_adapter.render()
        
        # Render debug information if enabled
        if self.show_debug:
            render_debug_overlay(True, True, self.screen)
        
        # Update display
        pygame.display.flip()
    
    def run(self):
        """Run the main loop."""
        try:
            # Main loop
            while self.running:
                # Handle events
                self.running = self.handle_events()
                
                # Render frame
                self.render()
                
                # Update performance metrics
                update_performance_metrics(self.screen)
                
                # Limit frame rate
                self.clock.tick(self.target_fps)
                
        except Exception as e:
            logger.error(f"Error in main loop: {e}")
            
        finally:
            # Clean up resources
            self.cleanup()
    
    def cleanup(self):
        """Clean up resources."""
        logger.info("Cleaning up resources")
        
        # Unload current module
        self.unload_current_module()
        
        # Clean up renderer manager
        self.renderer_manager.cleanup()
        
        # Quit PyGame
        pygame.quit()

def main():
    """Main entry point for the PyGame client."""
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description='MetaMindIQTrain PyGame Client')
    parser.add_argument('--width', type=int, default=1440, help='Screen width')
    parser.add_argument('--height', type=int, default=1024, help='Screen height')
    parser.add_argument('--fullscreen', action='store_true', help='Start in fullscreen mode')
    parser.add_argument('--module', type=str, help='Module to load')
    parser.add_argument('--config', type=str, help='Path to configuration file')
    parser.add_argument('--debug', action='store_true', help='Show debug information')
    args = parser.parse_args()
    
    # Create client
    client = PyGameClient(
        width=args.width,
        height=args.height,
        fullscreen=args.fullscreen,
        config_path=args.config
    )
    
    # Set debug flag
    client.show_debug = args.debug
    
    # Load module if specified
    if args.module:
        client.load_module(args.module)
    
    # Run client
    client.run()

if __name__ == "__main__":
    main() 