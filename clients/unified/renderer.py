#!/usr/bin/env python3
"""
Unified Renderer

This module provides a platform-agnostic renderer for the MetaMindIQTrain platform,
using an adapter pattern to support multiple rendering backends.
"""

import logging
from typing import Dict, Any, Optional, Protocol
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

class PlatformAdapter(ABC):
    """Interface for platform-specific rendering adapters."""
    
    @abstractmethod
    def initialize(self, width: int, height: int) -> None:
        """Initialize the platform adapter.
        
        Args:
            width: Screen width in pixels
            height: Screen height in pixels
        """
        pass
        
    @abstractmethod
    def render_component(self, component_type: str, component_id: str, 
                         component_data: Dict[str, Any]) -> None:
        """Render a component on the platform.
        
        Args:
            component_type: Type of component to render
            component_id: ID of the component
            component_data: Component state data
        """
        pass
        
    @abstractmethod
    def clear(self) -> None:
        """Clear the screen."""
        pass
        
    @abstractmethod
    def update(self) -> None:
        """Update the display (e.g., swap buffers, refresh screen)."""
        pass
        
    @abstractmethod
    def shutdown(self) -> None:
        """Shutdown the platform adapter."""
        pass

class UnifiedRenderer:
    """Platform-agnostic renderer with efficient delta rendering."""
    
    def __init__(self, platform_adapter: PlatformAdapter, width: int = 1024, height: int = 768):
        """Initialize the unified renderer.
        
        Args:
            platform_adapter: Platform-specific adapter for rendering
            width: Screen width in pixels
            height: Screen height in pixels
        """
        self.adapter = platform_adapter
        self.width = width
        self.height = height
        self.component_cache = {}
        
        # Initialize the platform adapter
        self.adapter.initialize(width, height)
        logger.info(f"Initialized unified renderer with {type(platform_adapter).__name__}")
        
    def render(self, state: Dict[str, Dict[str, Any]], 
              force_full_render: bool = False) -> None:
        """Render components based on their type.
        
        Args:
            state: Dictionary mapping component IDs to component data
            force_full_render: Force rendering of all components regardless of cache
        """
        if force_full_render:
            # Clear component cache to force full render
            self.component_cache = {}
            # Clear the screen
            self.adapter.clear()
            logger.debug("Forcing full render")
        
        # Track rendered components for cleanup
        rendered_components = set()
        
        # Render components
        for component_id, component_data in state.items():
            rendered_components.add(component_id)
            
            # Only render if changed from cache
            if (force_full_render or
                component_id not in self.component_cache or 
                component_data != self.component_cache[component_id]):
                
                component_type = component_data.get('type', 'unknown')
                
                try:
                    self.adapter.render_component(
                        component_type, 
                        component_id, 
                        component_data
                    )
                    
                    # Update cache
                    self.component_cache[component_id] = component_data.copy()
                    logger.debug(f"Rendered component: {component_id} of type {component_type}")
                except Exception as e:
                    logger.error(f"Error rendering component {component_id} of type {component_type}: {e}")
        
        # Remove cached components that no longer exist
        removed_components = set(self.component_cache.keys()) - rendered_components
        for component_id in removed_components:
            del self.component_cache[component_id]
            logger.debug(f"Removed component from cache: {component_id}")
        
        # Update the display
        self.adapter.update()
        
    def clear(self) -> None:
        """Clear the screen and component cache."""
        self.component_cache = {}
        self.adapter.clear()
        self.adapter.update()
        logger.debug("Cleared renderer screen and cache")
        
    def shutdown(self) -> None:
        """Shutdown the renderer."""
        self.adapter.shutdown()
        logger.info("Renderer shut down") 