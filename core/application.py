#!/usr/bin/env python3
"""
Core Application Class for MetaMindIQTrain

This module provides the main Application class that ties together the component
system, context system, and renderer to create a cohesive application framework.
"""

import logging
import time
import sys
from typing import Dict, Any, Optional, List, Callable, Type, Union

from MetaMindIQTrain.core.renderer import get_renderer, Renderer
from MetaMindIQTrain.core.component_system import Component, UIComponent, mount_component_tree, unmount_component_tree
from MetaMindIQTrain.core.context import ContextAware
from MetaMindIQTrain.core.app_context import (
    initialize_app_context, set_app_initialized, set_app_loading, set_app_error,
    update_performance_metrics, track_component_render, PERFORMANCE_METRICS
)
from MetaMindIQTrain.core.module_registry import ModuleRegistry
from MetaMindIQTrain.core.context_manager import ContextManager
from MetaMindIQTrain.core.fps_counter import FPSCounter

logger = logging.getLogger(__name__)

class Application:
    """Core application class that manages the main loop, events, and rendering."""
    
    def __init__(self, app_name: str = "MetaMindIQTrain"):
        """Initialize the application."""
        self.app_name = app_name
        self.running = False
        self.renderer = None
        self.root_component = None
        self.module_registry = ModuleRegistry()
        self.context_manager = ContextManager()
        self.fps_counter = FPSCounter()
        self.is_initialized = False
        
        # Set up logging
        logging.basicConfig(level=logging.INFO, 
                          format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        
    def initialize(self, width: int = 800, height: int = 600, 
                  renderer_backend: str = "auto", title: str = None) -> bool:
        """Initialize the application and renderer."""
        if title is None:
            title = self.app_name
            
        # Initialize the renderer
        self.renderer = get_renderer()
        if not self.renderer.initialize(width, height, renderer_backend, title):
            return False
            
        # Create root component
        from MetaMindIQTrain.core.component_system import Container
        self.root_component = Container("root")
        self.root_component.set_size(width, height)
        
        self.is_initialized = True
        return True
        
    def set_root_component(self, component) -> None:
        """Set the root component."""
        # Unmount old component if exists
        if self.root_component:
            unmount_component_tree(self.root_component)
            
        # Set and mount new component
        self.root_component = component
        mount_component_tree(component)
        
    def run(self) -> int:
        """Run the application main loop."""
        if not self.is_initialized:
            return 1
            
        self.running = True
        
        try:
            # Main loop
            while self.running and self.renderer.is_running():
                # Process events
                events = self.renderer.process_events()
                for event in events:
                    if event.get("type") == "quit":
                        self.running = False
                        break
                
                # Render
                self.renderer.clear((0, 0, 0, 255))
                if self.root_component:
                    self.renderer.render_component(self.root_component)
                self.renderer.present()
            
            # Cleanup
            self.renderer.shutdown()
            return 0
            
        except Exception as e:
            return 1

# Global application instance
_app_instance = None

def get_application() -> Application:
    """Get the global application instance.
    
    Returns:
        Application instance
    """
    global _app_instance
    if _app_instance is None:
        _app_instance = Application()
    return _app_instance 