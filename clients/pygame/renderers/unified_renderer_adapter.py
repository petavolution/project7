#!/usr/bin/env python3
"""
Unified Renderer Adapter for MetaMindIQTrain

This module provides an adapter between the legacy renderer API and the new
component-based renderer system. It allows existing code to work with the
new rendering system without significant changes.
"""

import pygame
import logging
import time
from typing import Dict, Any, List, Tuple, Optional, Set, Union, Callable

# Try to import from the package first
try:
    from MetaMindIQTrain.core.theme import Theme, get_theme
    from MetaMindIQTrain.core.unified_component_system import (
        Component, Container, Text, Image, Button, 
        Rectangle, Circle, Line, Grid, FlexContainer
    )
    from MetaMindIQTrain.clients.pygame.renderers.base_component_renderer import BaseComponentRenderer
    from MetaMindIQTrain.clients.pygame.renderers.optimized_renderer import OptimizedRenderer
except ImportError:
    # For direct execution during development
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))
    from core.theme import Theme, get_theme
    from core.unified_component_system import (
        Component, Container, Text, Image, Button, 
        Rectangle, Circle, Line, Grid, FlexContainer
    )
    from clients.pygame.renderers.base_component_renderer import BaseComponentRenderer
    from clients.pygame.renderers.optimized_renderer import OptimizedRenderer

# Configure logging
logger = logging.getLogger(__name__)

class UnifiedRendererAdapter:
    """
    Adapter that bridges between the old renderer API and the new component-based system.
    
    This adapter allows existing code to use the new rendering system without
    significant changes. It translates between the old state-based API and the
    new component-based API.
    """
    
    def __init__(self, screen: pygame.Surface, module_id: str):
        """Initialize the unified renderer adapter.
        
        Args:
            screen: PyGame screen surface
            module_id: ID of the module to adapt
        """
        self.screen = screen
        self.module_id = module_id
        self.width = screen.get_width()
        self.height = screen.get_height()
        
        # Create optimized renderer
        self.renderer = OptimizedRenderer(screen, module_id)
        
        # State tracking
        self.state = {}
        self.event_handlers = {}
        
        # Register default event handlers
        self._register_default_event_handlers()
        
        # Performance tracking
        self.last_render_time = 0
        self.frame_count = 0
        
        logger.info(f"Unified renderer adapter initialized for {module_id}")
    
    def _register_default_event_handlers(self):
        """Register default event handlers for common events."""
        # Mouse click handler
        self.register_event_handler(pygame.MOUSEBUTTONDOWN, self._handle_click)
        
        # Mouse motion handler
        self.register_event_handler(pygame.MOUSEMOTION, self._handle_mouse_motion)
        
        # Key press handler
        self.register_event_handler(pygame.KEYDOWN, self._handle_key_press)
    
    def register_event_handler(self, event_type: int, handler: Callable):
        """Register an event handler for a specific event type.
        
        Args:
            event_type: PyGame event type to handle
            handler: Function to call when the event occurs
        """
        self.event_handlers[event_type] = handler
    
    def _handle_click(self, event: pygame.event.Event) -> Optional[Dict[str, Any]]:
        """Handle mouse click events.
        
        Args:
            event: PyGame event to handle
            
        Returns:
            Optional[Dict[str, Any]]: Event data if handled, None otherwise
        """
        # Extract click position
        pos = event.pos
        button = event.button
        
        # Create event data
        event_data = {
            'type': 'click',
            'x': pos[0],
            'y': pos[1],
            'button': button
        }
        
        # Update state
        self.state.update({
            'last_click': pos,
            'last_click_time': time.time(),
            'last_click_button': button
        })
        
        return event_data
    
    def _handle_mouse_motion(self, event: pygame.event.Event) -> Optional[Dict[str, Any]]:
        """Handle mouse motion events.
        
        Args:
            event: PyGame event to handle
            
        Returns:
            Optional[Dict[str, Any]]: Event data if handled, None otherwise
        """
        # Extract motion data
        pos = event.pos
        rel = event.rel
        buttons = event.buttons
        
        # Create event data
        event_data = {
            'type': 'mousemotion',
            'x': pos[0],
            'y': pos[1],
            'dx': rel[0],
            'dy': rel[1],
            'buttons': buttons
        }
        
        # Update state
        self.state.update({
            'mouse_pos': pos,
            'mouse_buttons': buttons
        })
        
        return event_data
    
    def _handle_key_press(self, event: pygame.event.Event) -> Optional[Dict[str, Any]]:
        """Handle key press events.
        
        Args:
            event: PyGame event to handle
            
        Returns:
            Optional[Dict[str, Any]]: Event data if handled, None otherwise
        """
        # Extract key data
        key = event.key
        unicode = event.unicode if hasattr(event, 'unicode') else ''
        mod = event.mod if hasattr(event, 'mod') else 0
        
        # Create event data
        event_data = {
            'type': 'keypress',
            'key': key,
            'unicode': unicode,
            'mod': mod,
            'ctrl': bool(mod & pygame.KMOD_CTRL),
            'shift': bool(mod & pygame.KMOD_SHIFT),
            'alt': bool(mod & pygame.KMOD_ALT)
        }
        
        # Update state
        self.state.update({
            'last_key': key,
            'last_key_time': time.time()
        })
        
        return event_data
    
    def update_state(self, new_state: Dict[str, Any]):
        """Update the module state.
        
        Args:
            new_state: New state to update with
        """
        self.state.update(new_state)
    
    def handle_event(self, event: pygame.event.Event) -> Optional[Dict[str, Any]]:
        """Handle a PyGame event.
        
        Args:
            event: PyGame event to handle
            
        Returns:
            Optional[Dict[str, Any]]: Event data if handled, None otherwise
        """
        # Check if we have a handler for this event type
        if event.type in self.event_handlers:
            # Call the handler
            return self.event_handlers[event.type](event)
        
        # No handler found
        return None
    
    def render(self) -> bool:
        """Render the current state.
        
        Returns:
            bool: True if rendering was successful
        """
        # Record start time for performance tracking
        start_time = time.time()
        
        # Ensure state has module_id
        render_state = self.state.copy()
        render_state['module_id'] = self.module_id
        
        # Render using component renderer
        result = self.renderer.render(render_state)
        
        # Update performance metrics
        self.last_render_time = time.time() - start_time
        self.frame_count += 1
        
        return result
    
    def create_legacy_renderer_state(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Create a state dictionary compatible with the legacy renderer API.
        
        Args:
            state: Current component-based state
            
        Returns:
            Dict[str, Any]: Legacy renderer compatible state
        """
        # Create basic legacy state
        legacy_state = {
            'module_id': self.module_id,
            'screen_width': self.width,
            'screen_height': self.height,
            'theme': get_theme().id if get_theme() else 'default'
        }
        
        # Copy over relevant keys from component state
        for key, value in state.items():
            if key not in legacy_state:
                legacy_state[key] = value
        
        return legacy_state
    
    def create_component_state(self, legacy_state: Dict[str, Any]) -> Dict[str, Any]:
        """Create a component-based state from a legacy renderer state.
        
        Args:
            legacy_state: Legacy renderer state
            
        Returns:
            Dict[str, Any]: Component-based state
        """
        # Create basic component state
        component_state = {
            'module_id': self.module_id
        }
        
        # Copy over all keys from legacy state
        component_state.update(legacy_state)
        
        return component_state
    
    def get_stats(self) -> Dict[str, Any]:
        """Get rendering statistics.
        
        Returns:
            Dict[str, Any]: Dictionary of rendering statistics
        """
        # Get renderer stats
        renderer_stats = self.renderer.get_render_stats()
        
        # Add adapter-specific stats
        stats = {
            'adapter_render_time': self.last_render_time * 1000,  # ms
            'frame_count': self.frame_count,
            'registered_handlers': len(self.event_handlers)
        }
        
        # Combine stats
        stats.update(renderer_stats)
        
        return stats
    
    def cleanup(self):
        """Clean up resources."""
        # Clean up renderer
        self.renderer.cleanup()
        
        # Clear state and handlers
        self.state.clear()
        self.event_handlers.clear()
        
        logger.info(f"Unified renderer adapter cleaned up for {self.module_id}") 