#!/usr/bin/env python3
"""
Renderer Factory for MetaMindIQTrain PyGame Client

This module provides a centralized factory for creating renderers with
consistent styling and optimization across different modules. It leverages
the unified component system and theme system to ensure visual consistency
between web and PyGame implementations.

Key features:
1. Theme-aware rendering
2. Component reuse and pooling
3. Cached rendering for improved performance
4. Simplified renderer creation API
5. Consistent visual styles across modules
"""

import pygame
import logging
import importlib
import inspect
import os
from typing import Dict, Any, Optional, List, Tuple, Type, Union

# Try to import from the package first
try:
    from MetaMindIQTrain.core.theme import Theme, get_theme, set_theme
    from MetaMindIQTrain.core.unified_component_system import ComponentFactory, UI
    from MetaMindIQTrain.clients.pygame.renderers.enhanced_generic_renderer import EnhancedGenericRenderer
    from MetaMindIQTrain.clients.pygame.unified_renderer import UnifiedRenderer
    from MetaMindIQTrain.clients.pygame.optimized_renderer import OptimizedRenderer
    from MetaMindIQTrain.clients.pygame.renderers.base_component_renderer import BaseComponentRenderer
except ImportError:
    # For direct execution during development
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))
    from core.theme import Theme, get_theme, set_theme
    from core.unified_component_system import ComponentFactory, UI
    from clients.pygame.renderers.enhanced_generic_renderer import EnhancedGenericRenderer
    from clients.pygame.unified_renderer import UnifiedRenderer
    from clients.pygame.optimized_renderer import OptimizedRenderer
    from clients.pygame.renderers.base_component_renderer import BaseComponentRenderer

# Configure logging
logger = logging.getLogger(__name__)

class RendererFactory:
    """Factory for creating and managing renderers."""
    
    def __init__(self, screen, theme=None, default_width=None, default_height=None):
        """Initialize the renderer factory.
        
        Args:
            screen: PyGame screen surface
            theme: Theme to use for renderers (optional)
            default_width: Default width for renderers (optional)
            default_height: Default height for renderers (optional)
        """
        self.screen = screen
        self.default_width = default_width or screen.get_width()
        self.default_height = default_height or screen.get_height()
        
        # Set theme if provided
        self._ensure_theme(theme)
        
        # Cache of renderer instances
        self.renderer_cache = {}
        
        # Custom renderer mappings
        self.custom_renderers = {}
        
        # Initialize fonts
        self._initialize_fonts()
    
    def _initialize_fonts(self):
        """Initialize fonts for renderers."""
        pygame.font.init()
        
        # Create standard fonts
        font_name = pygame.font.get_default_font()
        self.title_font = pygame.font.Font(font_name, 28)
        self.regular_font = pygame.font.Font(font_name, 20)
        self.small_font = pygame.font.Font(font_name, 14)
        
        # Try to load custom fonts if available
        try:
            # Look for fonts in assets directory
            font_path = os.path.join(os.path.dirname(__file__), '..', '..', 'assets', 'fonts')
            
            # Load custom fonts if available
            custom_title_font = os.path.join(font_path, 'title.ttf')
            custom_regular_font = os.path.join(font_path, 'regular.ttf')
            custom_small_font = os.path.join(font_path, 'small.ttf')
            
            if os.path.exists(custom_title_font):
                self.title_font = pygame.font.Font(custom_title_font, 28)
            
            if os.path.exists(custom_regular_font):
                self.regular_font = pygame.font.Font(custom_regular_font, 20)
            
            if os.path.exists(custom_small_font):
                self.small_font = pygame.font.Font(custom_small_font, 14)
        
        except Exception as e:
            logger.warning(f"Could not load custom fonts: {e}")
    
    def create_renderer(self, module_id, width=None, height=None, theme=None, use_cached=True):
        """Create a renderer for a module.
        
        Args:
            module_id: ID of the module
            width: Screen width (optional)
            height: Screen height (optional)
            theme: Theme to use (optional)
            use_cached: Whether to use cached renderer (default: True)
            
        Returns:
            Renderer instance
        """
        # Use default dimensions if not provided
        width = width or self.default_width
        height = height or self.default_height
        
        # Check if we have a cached renderer for this module
        cache_key = f"{module_id}_{width}_{height}"
        if use_cached and cache_key in self.renderer_cache:
            renderer = self.renderer_cache[cache_key]
            
            # Apply theme if changed
            renderer.apply_theme(theme)
            
            return renderer
        
        # Ensure theme is set
        self._ensure_theme(theme)
        
        # Get theme-based colors
        theme = get_theme()
        colors = theme.colors if theme else None
        
        # Get renderer class for this module
        renderer_class = self._get_renderer_class(module_id)
        
        # Create renderer instance
        renderer = renderer_class(
            screen=self.screen,
            module_id=module_id,
            title_font=self.title_font,
            regular_font=self.regular_font,
            small_font=self.small_font,
            colors=colors,
            width=width,
            height=height
        )
        
        # Cache renderer for future use
        self.renderer_cache[cache_key] = renderer
        
        return renderer
    
    def _get_renderer_class(self, module_id):
        """Get the renderer class for a module.
        
        Args:
            module_id: ID of the module
            
        Returns:
            Renderer class
        """
        # Check for custom renderer
        if module_id in self.custom_renderers:
            return self.custom_renderers[module_id]
        
        # Check for specialized renderer in renderers package
        try:
            # Convert module_id to renderer name (e.g. "morph_matrix" -> "morph_matrix_renderer")
            renderer_name = f"{module_id}_renderer"
            module_path = f"MetaMindIQTrain.clients.pygame.renderers.{renderer_name}"
            
            # Try to import the module
            module = importlib.import_module(module_path)
            
            # Look for an appropriate renderer class
            for name, obj in inspect.getmembers(module, inspect.isclass):
                if issubclass(obj, BaseComponentRenderer) and obj != BaseComponentRenderer:
                    logger.info(f"Found specialized renderer for {module_id}: {name}")
                    return obj
        
        except (ImportError, AttributeError) as e:
            logger.debug(f"No specialized renderer found for {module_id}: {e}")
            pass
        
        # Fall back to OptimizedRenderer
        logger.info(f"Using generic optimized renderer for {module_id}")
        return OptimizedRenderer
    
    def register_renderer(self, module_id, renderer_class):
        """Register a custom renderer class for a module.
        
        Args:
            module_id: ID of the module
            renderer_class: Renderer class to use
        """
        self.custom_renderers[module_id] = renderer_class
        
        # Clear cache for this module
        for key in list(self.renderer_cache.keys()):
            if key.startswith(f"{module_id}_"):
                del self.renderer_cache[key]
    
    def _ensure_theme(self, theme=None):
        """Ensure a theme is set.
        
        Args:
            theme: Theme to use (optional)
        """
        if theme:
            # Use provided theme
            set_theme(theme)
        elif get_theme() is None:
            # Create default theme
            default_theme = Theme.default_theme(platform='pygame')
            set_theme(default_theme)
    
    def create_component_factory(self):
        """Create a component factory with current theme.
        
        Returns:
            ComponentFactory instance
        """
        # Ensure theme is set
        self._ensure_theme()
        
        # Create factory
        return ComponentFactory()
    
    def create_ui(self, width=None, height=None):
        """Create a UI instance.
        
        Args:
            width: UI width (optional)
            height: UI height (optional)
            
        Returns:
            UI instance
        """
        # Use default dimensions if not provided
        width = width or self.default_width
        height = height or self.default_height
        
        # Create UI
        return UI(width, height)
    
    def get_theme_colors(self):
        """Get the current theme colors.
        
        Returns:
            Dictionary of colors
        """
        theme = get_theme()
        return theme.colors if theme else {}
    
    def apply_theme_to_renderer(self, renderer, theme=None):
        """Apply a theme to a renderer.
        
        Args:
            renderer: Renderer to apply theme to
            theme: Theme to apply (optional)
        """
        # Ensure theme is set
        self._ensure_theme(theme)
        
        # Apply theme to renderer
        renderer.apply_theme(get_theme())
    
    def cleanup(self):
        """Clean up resources used by renderers."""
        # Clean up all cached renderers
        for renderer in self.renderer_cache.values():
            renderer.cleanup()
        
        # Clear cache
        self.renderer_cache.clear()

# Function to get a renderer for a module
def get_renderer(module_id: str, screen: pygame.Surface, **kwargs) -> Any:
    """Get a renderer for the specified module.
    
    Args:
        module_id: ID of the module
        screen: PyGame screen surface
        **kwargs: Additional arguments for the renderer
        
    Returns:
        Renderer instance
    """
    return RendererFactory(screen).create_renderer(module_id, **kwargs)

# Function to register a custom renderer
def register_renderer(module_id: str, renderer_class: Type) -> None:
    """Register a custom renderer for a module.
    
    Args:
        module_id: Module ID
        renderer_class: Renderer class
    """
    RendererFactory(None).register_renderer(module_id, renderer_class) 