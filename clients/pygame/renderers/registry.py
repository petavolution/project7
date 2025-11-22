#!/usr/bin/env python3
"""
Renderer Registry for MetaMindIQTrain PyGame Client

This module manages the registration and discovery of renderers for
different module types. Each module should have a dedicated renderer
to handle its specific rendering needs.
"""

import importlib
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class RendererRegistry:
    """Registry for module renderers."""
    
    def __init__(self):
        """Initialize the renderer registry."""
        self.renderers = {}
        self._register_renderers()
        
    def _register_renderers(self):
        """Register available renderers."""
        # Import built-in renderers
        try:
            # Try relative import first
            from .default_renderer import register_renderer as register_default
            from .symbol_memory_renderer import register_renderer as register_symbol_memory
            from .morph_matrix_renderer import register_renderer as register_morph_matrix
            from .expand_vision_renderer import register_renderer as register_expand_vision
            from .music_theory_renderer import register_renderer as register_music_theory
            from .psychoacoustic_wizard_renderer import register_renderer as register_psychoacoustic_wizard
            from .theme_component_renderer import register_renderer as register_theme_component
            
            # Register renderers
            self._register_renderer(register_default())
            self._register_renderer(register_symbol_memory())
            self._register_renderer(register_morph_matrix())
            self._register_renderer(register_expand_vision())
            self._register_renderer(register_music_theory())
            self._register_renderer(register_psychoacoustic_wizard())
            self._register_renderer(register_theme_component())
            
        except ImportError as e:
            # Fall back to absolute imports
            try:
                from MetaMindIQTrain.clients.pygame.renderers.default_renderer import register_renderer as register_default
                from MetaMindIQTrain.clients.pygame.renderers.symbol_memory_renderer import register_renderer as register_symbol_memory
                from MetaMindIQTrain.clients.pygame.renderers.morph_matrix_renderer import register_renderer as register_morph_matrix
                from MetaMindIQTrain.clients.pygame.renderers.expand_vision_renderer import register_renderer as register_expand_vision
                from MetaMindIQTrain.clients.pygame.renderers.music_theory_renderer import register_renderer as register_music_theory
                from MetaMindIQTrain.clients.pygame.renderers.psychoacoustic_wizard_renderer import register_renderer as register_psychoacoustic_wizard
                from MetaMindIQTrain.clients.pygame.renderers.theme_component_renderer import register_renderer as register_theme_component
                
                # Register renderers
                self._register_renderer(register_default())
                self._register_renderer(register_symbol_memory())
                self._register_renderer(register_morph_matrix())
                self._register_renderer(register_expand_vision())
                self._register_renderer(register_music_theory())
                self._register_renderer(register_psychoacoustic_wizard())
                self._register_renderer(register_theme_component())
                
            except ImportError as e:
                logger.warning(f"Error importing renderers: {e}")
                logger.warning("Falling back to enhanced generic renderer")
                
                # Try to import theme component renderer first, if available
                try:
                    from .theme_component_renderer import ThemeComponentRenderer
                    
                    # Register theme renderer
                    self._register_renderer({
                        "id": "theme",
                        "name": "Theme Renderer",
                        "renderer_class": ThemeComponentRenderer,
                        "description": "Renders UI components using the theme system"
                    })
                    
                    # Use theme renderer as default
                    self._register_renderer({
                        "id": "default",
                        "name": "Default",
                        "renderer_class": ThemeComponentRenderer,
                        "description": "Theme-aware renderer for all modules"
                    })
                except ImportError:
                    # Fall back to the enhanced generic renderer
                    from .enhanced_generic_renderer import EnhancedGenericRenderer
                    
                    # Register a minimal set of renderers
                    self._register_renderer({
                        "id": "default",
                        "name": "Default",
                        "renderer_class": EnhancedGenericRenderer,
                        "description": "Generic renderer for all modules"
                    })
    
    def _register_renderer(self, renderer_info):
        """Register a renderer.
        
        Args:
            renderer_info: Dictionary with renderer information
        """
        if "id" not in renderer_info:
            logger.warning(f"Cannot register renderer without ID: {renderer_info}")
            return
            
        renderer_id = renderer_info["id"]
        self.renderers[renderer_id] = renderer_info
        logger.debug(f"Registered renderer: {renderer_id}")
    
    def get_renderer(self, module_id):
        """Get a renderer for a module.
        
        Args:
            module_id: Module ID
            
        Returns:
            Renderer information or None
        """
        # Look for a dedicated renderer
        if module_id in self.renderers:
            return self.renderers[module_id]
            
        # Fall back to default renderer
        if "default" in self.renderers:
            return self.renderers["default"]
            
        # No renderers available
        return None
    
    def create_renderer(self, module_id, screen, **kwargs):
        """Create a renderer instance.
        
        Args:
            module_id: Module ID
            screen: Pygame screen
            **kwargs: Additional arguments for the renderer
            
        Returns:
            Renderer instance
        """
        renderer_info = self.get_renderer(module_id)
        
        if not renderer_info:
            logger.warning(f"No renderer available for {module_id}")
            return None
            
        try:
            renderer_class = renderer_info["renderer_class"]
            renderer = renderer_class(screen, **kwargs)
            renderer.module_id = module_id
            return renderer
        except Exception as e:
            logger.error(f"Error creating renderer for {module_id}: {e}")
            return None
    
    def list_renderers(self):
        """List all available renderers.
        
        Returns:
            List of renderer IDs
        """
        return list(self.renderers.keys())

    def has_renderer(self, module_id):
        """Check if a renderer is available for a module.
        
        Args:
            module_id: Module ID
            
        Returns:
            True if a renderer is available, False otherwise
        """
        return module_id in self.renderers or "default" in self.renderers

# Singleton instance
_registry = None

def get_registry():
    """Get the renderer registry instance.
    
    Returns:
        RendererRegistry instance
    """
    global _registry
    if _registry is None:
        _registry = RendererRegistry()
    return _registry 