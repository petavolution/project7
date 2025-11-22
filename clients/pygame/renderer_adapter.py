#!/usr/bin/env python3
"""
Renderer Adapter for MetaMindIQTrain

This module provides adapters to connect MVC-based modules and renderers
with the existing renderer system, enabling a gradual transition to the
new architecture without breaking compatibility.

Key features:
1. Transparent mapping between old and new rendering systems
2. Event handling translation
3. State conversion
4. Progressive upgrade path
"""

import pygame
import logging
from typing import Dict, List, Any, Tuple, Optional, Union, Callable

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MVCRendererAdapter:
    """Adapter for MVC renderers to work with the existing system."""
    
    def __init__(self, mvc_renderer, module):
        """Initialize the adapter.
        
        Args:
            mvc_renderer: Instance of an MVC-based renderer
            module: Training module instance
        """
        self.mvc_renderer = mvc_renderer
        self.module = module
        
        # Set up event handlers
        self._setup_event_handlers()
    
    def _setup_event_handlers(self):
        """Set up event handlers for the MVC renderer."""
        if hasattr(self.mvc_renderer, "set_event_handlers"):
            # These callbacks will be called by the renderer
            # when the user interacts with UI components
            self.mvc_renderer.set_event_handlers(
                on_pattern_click=self._on_pattern_click,
                on_submit_click=self._on_submit_click,
                on_next_click=self._on_next_click
            )
    
    def _on_pattern_click(self, pattern_index):
        """Handle pattern click event.
        
        Args:
            pattern_index: Index of the clicked pattern
        """
        # Forward to module for processing
        if hasattr(self.module, "process_input"):
            self.module.process_input({
                "action": "select_pattern",
                "pattern_index": pattern_index
            })
    
    def _on_submit_click(self):
        """Handle submit button click event."""
        # Forward to module for processing
        if hasattr(self.module, "process_input"):
            self.module.process_input({
                "action": "submit"
            })
    
    def _on_next_click(self):
        """Handle next button click event."""
        # Forward to module for processing
        if hasattr(self.module, "process_input"):
            self.module.process_input({
                "action": "next_round"
            })
    
    def render(self, state=None):
        """Render the module using the MVC renderer.
        
        Args:
            state: Optional state override
        """
        # Get state from module if not provided
        if state is None and hasattr(self.module, "get_state"):
            state = self.module.get_state()
        
        # Render using MVC renderer
        self.mvc_renderer.render(state)
    
    def handle_event(self, event, state=None):
        """Handle a pygame event.
        
        Args:
            event: Pygame event
            state: Optional state override
            
        Returns:
            Result of event handling
        """
        # Get state from module if not provided
        if state is None and hasattr(self.module, "get_state"):
            state = self.module.get_state()
        
        # Let the MVC renderer handle the event first
        if hasattr(self.mvc_renderer, "handle_event"):
            handled = self.mvc_renderer.handle_event(event, state)
            if handled:
                return {"result": "handled_by_renderer"}
        
        # If not handled by the renderer, try direct module handling
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Left mouse button click
            if hasattr(self.module, "handle_click"):
                result = self.module.handle_click(event.pos[0], event.pos[1])
                return result
        
        # Event not handled
        return {"result": "no_action"}
    
    def update(self, dt):
        """Update the renderer state.
        
        Args:
            dt: Time delta in seconds
        """
        if hasattr(self.mvc_renderer, "update"):
            self.mvc_renderer.update(dt)


class ModuleAdapter:
    """Adapter for MVC modules to work with the existing system."""
    
    def __init__(self, mvc_module):
        """Initialize the adapter.
        
        Args:
            mvc_module: Instance of an MVC-based module
        """
        self.mvc_module = mvc_module
    
    def handle_click(self, x, y):
        """Handle mouse click events.
        
        Args:
            x: X coordinate of click
            y: Y coordinate of click
            
        Returns:
            Result dictionary
        """
        return self.mvc_module.handle_click(x, y)
    
    def update(self, dt):
        """Update module state based on elapsed time.
        
        Args:
            dt: Time delta since last update in seconds
        """
        self.mvc_module.update(dt)
    
    def get_state(self):
        """Get the current module state.
        
        Returns:
            Dictionary with state information
        """
        return self.mvc_module.get_state()
    
    def process_input(self, input_data):
        """Process input data.
        
        Args:
            input_data: Input data dictionary
            
        Returns:
            Result dictionary
        """
        return self.mvc_module.process_input(input_data)
    
    def build_ui(self):
        """Build the UI component tree.
        
        Returns:
            UI component tree specification
        """
        if hasattr(self.mvc_module, "build_ui"):
            return self.mvc_module.build_ui()
        return None


def create_mvc_renderer(module, screen, renderer_class):
    """Create an MVC renderer adapter for a module.
    
    Args:
        module: Training module instance
        screen: Pygame screen surface
        renderer_class: MVC renderer class to instantiate
        
    Returns:
        Renderer adapter instance
    """
    # Create the MVC renderer
    mvc_renderer = renderer_class(screen)
    
    # Create and return the adapter
    return MVCRendererAdapter(mvc_renderer, module)


def create_mvc_module(module_class, *args, **kwargs):
    """Create an MVC module adapter.
    
    Args:
        module_class: MVC module class to instantiate
        *args: Positional arguments for the module constructor
        **kwargs: Keyword arguments for the module constructor
        
    Returns:
        Module adapter instance
    """
    # Create the MVC module
    mvc_module = module_class(*args, **kwargs)
    
    # Create and return the adapter
    return ModuleAdapter(mvc_module) 