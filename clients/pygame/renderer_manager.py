#!/usr/bin/env python3
"""
Renderer Manager for MetaMindIQTrain PyGame client

This module provides a central manager for all renderers used in the PyGame client.
It coordinates theme application, resolution scaling, and renderer lifecycle.
"""

import pygame
import time
import logging
import os
from typing import Dict, Any, Tuple, Optional, List, Union
from functools import lru_cache

# Try to import from the package first
try:
    from MetaMindIQTrain.core.theme import Theme, get_theme, set_theme, register_theme
    from MetaMindIQTrain.clients.pygame.renderers.registry import RendererRegistry
    from MetaMindIQTrain.clients.pygame.renderers.base_component_renderer import BaseComponentRenderer
    from MetaMindIQTrain.clients.pygame.renderers.optimized_renderer import OptimizedRenderer
    from MetaMindIQTrain.clients.pygame.renderers.unified_renderer_adapter import UnifiedRendererAdapter
except ImportError:
    # For direct execution during development
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))
    from core.theme import Theme, get_theme, set_theme, register_theme
    from clients.pygame.renderers.registry import RendererRegistry
    from clients.pygame.renderers.base_component_renderer import BaseComponentRenderer
    from clients.pygame.renderers.optimized_renderer import OptimizedRenderer
    from clients.pygame.renderers.unified_renderer_adapter import UnifiedRendererAdapter

# Configure logging
logger = logging.getLogger(__name__)

# Constants
DEFAULT_RESOLUTION = (1440, 1024)
DEFAULT_FPS = 60
MAX_CACHED_RENDERERS = 5
PERFORMANCE_WINDOW_SIZE = 60  # Number of frames to average for performance metrics

class RendererManager:
    """
    Central manager for all renderers in the PyGame client.
    
    This class is responsible for:
    1. Creating and caching renderers for modules
    2. Managing theme application
    3. Handling resolution scaling
    4. Providing performance metrics
    
    It uses the Singleton pattern to ensure only one instance exists.
    """
    
    # Singleton instance
    _instance = None
    
    @classmethod
    def get_instance(cls, screen=None, theme=None):
        """Get the singleton instance of the renderer manager.
        
        Args:
            screen: PyGame screen surface (only used when creating the instance)
            theme: Theme to use (only used when creating the instance)
            
        Returns:
            RendererManager: The singleton instance
        """
        if cls._instance is None:
            cls._instance = cls(screen, theme)
        elif screen is not None:
            # Update screen if provided
            cls._instance.screen = screen
            cls._instance.update_resolution(screen.get_width(), screen.get_height())
        return cls._instance
    
    def __init__(self, screen, theme=None):
        """Initialize the renderer manager.
        
        Args:
            screen: PyGame screen surface
            theme: Theme to use (optional)
        """
        # Ensure singleton pattern
        if RendererManager._instance is not None:
            raise RuntimeError("Use get_instance() instead of constructor")
        
        # Initialize properties
        self.screen = screen
        self.registry = RendererRegistry()
        self.resolution = DEFAULT_RESOLUTION
        self.actual_resolution = DEFAULT_RESOLUTION
        self.scaling_factor = (1.0, 1.0)
        
        # Set up theme
        self.theme = theme or self._create_default_theme()
        set_theme(self.theme)
        
        # Update resolution based on screen
        if screen:
            self.update_resolution(screen.get_width(), screen.get_height())
        
        # Initialize renderer cache
        self.renderer_cache = {}
        self.adapter_cache = {}
        
        # Initialize performance metrics
        self.frame_times = []
        self.render_times = []
        self.last_frame_time = time.time()
        self.current_fps = 0
        self.average_render_time = 0
        
        logger.info("Renderer manager initialized")
    
    def _create_default_theme(self) -> Theme:
        """Create a default theme for the application.
        
        Returns:
            Theme: The default theme
        """
        dark_theme = Theme(
            id="dark",
            name="Dark Theme",
            colors={
                "background": (15, 18, 28),          # Dark blue-black background
                "text": (220, 225, 235),             # Light blue-white text
                "text_secondary": (180, 180, 190),   # Light blue-gray for secondary text
                "header": (22, 26, 38),              # Slightly lighter dark blue for headers
                "content": (18, 22, 32),             # Mid dark blue for content areas
                "border": (60, 70, 100),             # Medium blue for borders
                "accent": (80, 120, 200),            # Vibrant blue accent
                "success": (70, 200, 120),           # Green for success/positive
                "warning": (240, 180, 60),           # Amber for warnings
                "error": (230, 70, 80),              # Red for errors/failures
                "highlight": (100, 160, 255),        # Lighter blue for highlights
                "button": (40, 50, 80),              # Dark blue buttons
                "button_hover": (50, 65, 100),       # Slightly lighter when hovered
                "button_text": (220, 225, 235),      # Light text on buttons
                "input": (25, 30, 45),               # Slightly lighter than background for input fields
                "selection": (60, 100, 180, 80),     # Semi-transparent selection color
            },
            fonts={
                "small": 18,
                "regular": 22,
                "large": 28,
                "title": 36,
                "header": 48
            },
            spacing={
                "xs": 5,
                "sm": 10,
                "md": 20,
                "lg": 30,
                "xl": 50
            },
            borders={
                "radius_sm": 3,
                "radius_md": 5,
                "radius_lg": 10,
                "width_thin": 1,
                "width_regular": 2,
                "width_thick": 3
            }
        )
        
        # Register the theme
        register_theme(dark_theme)
        
        return dark_theme
    
    def update_resolution(self, width: int, height: int):
        """Update the current resolution and scaling factors.
        
        Args:
            width: New screen width
            height: New screen height
        """
        # Update actual resolution
        self.actual_resolution = (width, height)
        
        # Calculate scaling factors
        self.scaling_factor = (
            width / DEFAULT_RESOLUTION[0],
            height / DEFAULT_RESOLUTION[1]
        )
        
        logger.info(f"Resolution updated to {width}x{height}, scaling: {self.scaling_factor}")
        
        # Apply resolution to theme scaling
        self._apply_theme_scaling()
    
    def _apply_theme_scaling(self):
        """Apply scaling to theme values based on the current resolution."""
        theme = get_theme()
        
        # Scale font sizes
        for key, size in theme.fonts.items():
            theme.fonts[key] = int(size * min(self.scaling_factor))
        
        # Scale spacing values
        for key, value in theme.spacing.items():
            theme.spacing[key] = int(value * min(self.scaling_factor))
        
        # Update the theme
        set_theme(theme)
        
        logger.debug("Applied theme scaling based on resolution")
    
    def get_renderer(self, module_id: str, screen: pygame.Surface = None) -> Any:
        """Get a renderer for the specified module.
        
        Args:
            module_id: ID of the module to get a renderer for
            screen: PyGame screen surface (uses the manager's screen if not provided)
            
        Returns:
            Any: The renderer for the module
        """
        # Use the manager's screen if not provided
        screen = screen or self.screen
        
        # Check if we have a cached renderer
        if module_id in self.renderer_cache:
            logger.debug(f"Using cached renderer for {module_id}")
            return self.renderer_cache[module_id]
        
        # Try to get a specialized renderer from the registry
        try:
            logger.info(f"Creating renderer for {module_id}")
            
            # First check if we have a specialized renderer
            if self.registry.has_renderer(module_id):
                renderer_class = self.registry.get_renderer(module_id)
                renderer = renderer_class(screen)
                logger.info(f"Created specialized renderer for {module_id}")
            else:
                # Fall back to the optimized renderer
                renderer = OptimizedRenderer(screen, module_id)
                logger.info(f"Created optimized renderer for {module_id}")
            
            # Cache the renderer (limiting cache size)
            if len(self.renderer_cache) >= MAX_CACHED_RENDERERS:
                # Remove the oldest entry
                oldest_key = next(iter(self.renderer_cache))
                del self.renderer_cache[oldest_key]
            
            self.renderer_cache[module_id] = renderer
            return renderer
            
        except Exception as e:
            logger.error(f"Error creating renderer for {module_id}: {e}")
            # Fall back to the base component renderer
            renderer = BaseComponentRenderer(screen, module_id)
            self.renderer_cache[module_id] = renderer
            return renderer
    
    def get_adapter(self, module_id: str, screen: pygame.Surface = None) -> Any:
        """Get a renderer adapter for the specified module.
        
        Args:
            module_id: ID of the module to get an adapter for
            screen: PyGame screen surface (uses the manager's screen if not provided)
            
        Returns:
            Any: The renderer adapter for the module
        """
        # Use the manager's screen if not provided
        screen = screen or self.screen
        
        # Check if we have a cached adapter
        if module_id in self.adapter_cache:
            logger.debug(f"Using cached adapter for {module_id}")
            return self.adapter_cache[module_id]
        
        # Create a new adapter
        try:
            logger.info(f"Creating adapter for {module_id}")
            adapter = UnifiedRendererAdapter(screen, module_id)
            
            # Cache the adapter (limiting cache size)
            if len(self.adapter_cache) >= MAX_CACHED_RENDERERS:
                # Remove the oldest entry
                oldest_key = next(iter(self.adapter_cache))
                del self.adapter_cache[oldest_key]
            
            self.adapter_cache[module_id] = adapter
            return adapter
            
        except Exception as e:
            logger.error(f"Error creating adapter for {module_id}: {e}")
            return None
    
    def handle_resize(self, width: int, height: int):
        """Handle window resize event.
        
        Args:
            width: New screen width
            height: New screen height
        """
        # Update resolution
        self.update_resolution(width, height)
        
        # Clear renderer cache to force recreation with new resolution
        self.renderer_cache.clear()
        self.adapter_cache.clear()
        
        logger.info(f"Handled resize to {width}x{height}, cleared renderer cache")
    
    def scale_position(self, x: float, y: float) -> Tuple[int, int]:
        """Scale a position according to the current resolution.
        
        Args:
            x: X coordinate in base resolution
            y: Y coordinate in base resolution
            
        Returns:
            Tuple[int, int]: Scaled coordinates
        """
        return (
            int(x * self.scaling_factor[0]),
            int(y * self.scaling_factor[1])
        )
    
    def scale_dimensions(self, width: float, height: float) -> Tuple[int, int]:
        """Scale dimensions according to the current resolution.
        
        Args:
            width: Width in base resolution
            height: Height in base resolution
            
        Returns:
            Tuple[int, int]: Scaled dimensions
        """
        return (
            int(width * self.scaling_factor[0]),
            int(height * self.scaling_factor[1])
        )
    
    def unscale_position(self, x: float, y: float) -> Tuple[int, int]:
        """Convert a scaled position back to base resolution.
        
        Args:
            x: X coordinate in current resolution
            y: Y coordinate in current resolution
            
        Returns:
            Tuple[int, int]: Position in base resolution
        """
        return (
            int(x / self.scaling_factor[0]),
            int(y / self.scaling_factor[1])
        )
    
    def update_performance_metrics(self):
        """Update performance metrics for the current frame."""
        current_time = time.time()
        frame_time = current_time - self.last_frame_time
        self.last_frame_time = current_time
        
        # Add frame time to history
        self.frame_times.append(frame_time)
        
        # Keep only the most recent frames
        if len(self.frame_times) > PERFORMANCE_WINDOW_SIZE:
            self.frame_times.pop(0)
        
        # Calculate current FPS (avoid division by zero)
        if frame_time > 0:
            self.current_fps = 1.0 / frame_time
        
        # Calculate average render time
        if self.render_times:
            self.average_render_time = sum(self.render_times) / len(self.render_times)
    
    def record_render_time(self, start_time: float):
        """Record the time taken to render a frame.
        
        Args:
            start_time: Time when rendering started
        """
        render_time = time.time() - start_time
        
        # Add render time to history
        self.render_times.append(render_time)
        
        # Keep only the most recent render times
        if len(self.render_times) > PERFORMANCE_WINDOW_SIZE:
            self.render_times.pop(0)
    
    def render_debug_overlay(self, show_fps: bool = True, show_render_time: bool = True):
        """Render debug information as an overlay.
        
        Args:
            show_fps: Whether to show FPS counter
            show_render_time: Whether to show render time
        """
        if not self.screen:
            return
        
        # Get theme colors
        theme = get_theme()
        text_color = theme.colors["text"]
        bg_color = (0, 0, 0, 128)  # Semi-transparent black
        
        # Create font
        try:
            debug_font = pygame.font.SysFont("monospace", 16)
        except:
            debug_font = pygame.font.Font(None, 16)
        
        # Prepare debug text
        debug_lines = []
        
        if show_fps:
            debug_lines.append(f"FPS: {self.current_fps:.1f}")
        
        if show_render_time:
            debug_lines.append(f"Render: {self.average_render_time * 1000:.2f}ms")
        
        # Add resolution info
        width, height = self.actual_resolution
        debug_lines.append(f"Res: {width}x{height}")
        
        # Create background rect
        line_height = 20
        overlay_height = len(debug_lines) * line_height + 10
        overlay_rect = pygame.Rect(
            10, 10, 
            150, overlay_height
        )
        
        # Draw semi-transparent background
        s = pygame.Surface((overlay_rect.width, overlay_rect.height), pygame.SRCALPHA)
        s.fill(bg_color)
        self.screen.blit(s, (overlay_rect.x, overlay_rect.y))
        
        # Draw debug text
        for i, line in enumerate(debug_lines):
            text_surface = debug_font.render(line, True, text_color)
            self.screen.blit(text_surface, (overlay_rect.x + 5, overlay_rect.y + 5 + i * line_height))
    
    def cleanup(self):
        """Clean up resources."""
        # Clear caches
        self.renderer_cache.clear()
        self.adapter_cache.clear()
        
        logger.info("Renderer manager cleaned up")

# Module-level functions for easier access

def get_renderer(module_id: str, screen: pygame.Surface = None) -> Any:
    """Get a renderer for the specified module.
    
    Args:
        module_id: ID of the module to get a renderer for
        screen: PyGame screen surface (uses the manager's screen if not provided)
        
    Returns:
        Any: The renderer for the module
    """
    return RendererManager.get_instance().get_renderer(module_id, screen)

def get_adapter(module_id: str, screen: pygame.Surface = None) -> Any:
    """Get a renderer adapter for the specified module.
    
    Args:
        module_id: ID of the module to get an adapter for
        screen: PyGame screen surface (uses the manager's screen if not provided)
        
    Returns:
        Any: The renderer adapter for the module
    """
    return RendererManager.get_instance().get_adapter(module_id, screen)

def scale_position(x: float, y: float) -> Tuple[int, int]:
    """Scale a position according to the current resolution.
    
    Args:
        x: X coordinate in base resolution
        y: Y coordinate in base resolution
        
    Returns:
        Tuple[int, int]: Scaled coordinates
    """
    return RendererManager.get_instance().scale_position(x, y)

def scale_dimensions(width: float, height: float) -> Tuple[int, int]:
    """Scale dimensions according to the current resolution.
    
    Args:
        width: Width in base resolution
        height: Height in base resolution
        
    Returns:
        Tuple[int, int]: Scaled dimensions
    """
    return RendererManager.get_instance().scale_dimensions(width, height)

def unscale_position(x: float, y: float) -> Tuple[int, int]:
    """Convert a scaled position back to base resolution.
    
    Args:
        x: X coordinate in current resolution
        y: Y coordinate in current resolution
        
    Returns:
        Tuple[int, int]: Position in base resolution
    """
    return RendererManager.get_instance().unscale_position(x, y)

def update_performance_metrics(screen: pygame.Surface = None):
    """Update performance metrics for the current frame.
    
    Args:
        screen: Screen to associate with the performance metrics
    """
    manager = RendererManager.get_instance(screen)
    manager.update_performance_metrics()

def render_debug_overlay(show_fps: bool = True, show_render_time: bool = True, screen: pygame.Surface = None):
    """Render debug information as an overlay.
    
    Args:
        show_fps: Whether to show FPS counter
        show_render_time: Whether to show render time
        screen: Screen to render debug overlay on
    """
    manager = RendererManager.get_instance(screen)
    manager.render_debug_overlay(show_fps, show_render_time) 