#!/usr/bin/env python3
"""
Enhanced Generic Module Renderer for the PyGame client.

This is a fully generic renderer that can display any training module
based solely on the state information provided by the server. It eliminates
the need for module-specific renderers by using a flexible component-based
approach to rendering with performance optimizations.
"""

import pygame
import logging
import math
import os
from typing import Dict, Any, List, Tuple, Optional, Union, Callable
from abc import ABC, abstractmethod
import time
import weakref

# Try to import module colors from config
try:
    from MetaMindIQTrain.config import (
        MODULE_COLORS, 
        scale_coordinates, 
        scale_for_resolution, 
        maintain_aspect_ratio,
        calculate_sizes
    )
    HAS_MODULE_COLORS = True
except ImportError:
    HAS_MODULE_COLORS = False
    
# Handle imports properly whether run as module or directly
if __name__ == "__main__":
    # When run directly
    import sys
    import os
    from pathlib import Path
    
    # Add the project root to the path
    project_root = Path(__file__).resolve().parent.parent.parent.parent
    sys.path.insert(0, str(project_root))
    
    # Now import from the absolute path
    from base_renderer import BaseRenderer
else:
    # When imported as a module
    from .base_renderer import BaseRenderer

logger = logging.getLogger(__name__)

class RenderCache:
    """Cache for rendered components to reduce redundant rendering."""
    
    def __init__(self, max_size=100, ttl=5.0):
        """Initialize the render cache.
        
        Args:
            max_size: Maximum number of cached items
            ttl: Time-to-live in seconds for cached items
        """
        self.cache = {}
        self.max_size = max_size
        self.ttl = ttl
        self.timestamps = {}
        self.hit_count = 0
        self.miss_count = 0
    
    def get(self, key):
        """Get a cached surface if available and not expired.
        
        Args:
            key: Cache key (hash of component data)
            
        Returns:
            Cached surface or None if not found or expired
        """
        now = time.time()
        if key in self.cache:
            if now - self.timestamps[key] < self.ttl:
                self.timestamps[key] = now  # Update access time
                self.hit_count += 1
                return self.cache[key]
            else:
                # Expired
                del self.cache[key]
                del self.timestamps[key]
        
        self.miss_count += 1
        return None
    
    def set(self, key, surface):
        """Add a surface to the cache.
        
        Args:
            key: Cache key (hash of component data)
            surface: Rendered surface to cache
        """
        # If cache is full, remove oldest entry
        if len(self.cache) >= self.max_size:
            oldest_key = min(self.timestamps, key=lambda k: self.timestamps[k])
            del self.cache[oldest_key]
            del self.timestamps[oldest_key]
        
        # Add to cache
        self.cache[key] = surface.copy()  # Store a copy to prevent modifications
        self.timestamps[key] = time.time()
    
    def clear(self):
        """Clear the cache."""
        self.cache.clear()
        self.timestamps.clear()
    
    def clean_expired(self):
        """Remove expired entries from the cache."""
        now = time.time()
        expired_keys = [k for k, t in self.timestamps.items() if now - t >= self.ttl]
        for key in expired_keys:
            del self.cache[key]
            del self.timestamps[key]
    
    def get_stats(self):
        """Get cache statistics.
        
        Returns:
            Dictionary with cache statistics
        """
        total = self.hit_count + self.miss_count
        hit_rate = self.hit_count / total if total > 0 else 0
        
        return {
            'size': len(self.cache),
            'max_size': self.max_size,
            'hit_count': self.hit_count,
            'miss_count': self.miss_count,
            'hit_rate': hit_rate
        }

class EnhancedGenericRenderer(BaseRenderer):
    """Enhanced generic renderer for any module type with optimized rendering."""
    
    def __init__(self, screen, module_id, config=None, colors=None, fonts=None, width=None, height=None):
        """Initialize the enhanced generic renderer.
        
        Args:
            screen: Pygame screen surface
            module_id: ID of the module to render
            config: Optional configuration dictionary
            colors: Optional color scheme dictionary
            fonts: Optional fonts dictionary
            width: Optional screen width (defaults to screen width)
            height: Optional screen height (defaults to screen height)
        """
        self.screen = screen
        self.module_id = module_id
        self.config = config or {}
        
        # Import config settings if not already provided
        if width is None or height is None:
            try:
                from MetaMindIQTrain.config import SCREEN_WIDTH, SCREEN_HEIGHT
                self.width = width or SCREEN_WIDTH
                self.height = height or SCREEN_HEIGHT
            except ImportError:
                # Fallback to screen dimensions if config import fails
                self.width = width or screen.get_width()
                self.height = height or screen.get_height()
        else:
            self.width = width
            self.height = height
            
        # Ensure UI elements respect the actual screen dimensions
        self.screen_rect = self.screen.get_rect()
        self.actual_width = self.screen_rect.width
        self.actual_height = self.screen_rect.height
        
        # Calculate scaling factors if render target is different from config dimensions
        self.scale_x = self.actual_width / self.width
        self.scale_y = self.actual_height / self.height
        
        # Initialize the base renderer
        self.title_font = fonts['title'] if fonts and 'title' in fonts else pygame.font.Font(None, 36)
        self.regular_font = fonts['regular'] if fonts and 'regular' in fonts else pygame.font.Font(None, 24)
        self.small_font = fonts['small'] if fonts and 'small' in fonts else pygame.font.Font(None, 18)
        
        super().__init__(screen, self.title_font, self.regular_font, self.small_font, colors)
        
        # Initialize component cache
        self.render_cache = RenderCache(max_size=200, ttl=2.0)
        
        # Initialize theme-aware component factory
        try:
            from MetaMindIQTrain.core.theme import ThemeProvider, get_theme, Theme
            from MetaMindIQTrain.core.components import ThemeAwareComponentFactory
            
            # Use existing theme or create a default one
            theme = get_theme() or Theme(name="Dark Theme", platform="pygame")
            theme_provider = ThemeProvider(theme)
            self.component_factory = ThemeAwareComponentFactory(theme_provider)
            self.has_theme_support = True
            logger.info("Using theme-aware component factory")
        except ImportError:
            # Fall back to direct imports if package import fails
            try:
                # Try relative imports
                sys.path.insert(0, str(Path(__file__).parent.parent.parent))
                from core.theme import ThemeProvider, get_theme, Theme
                from core.components import ThemeAwareComponentFactory
                
                # Use existing theme or create a default one
                theme = get_theme() or Theme(name="Dark Theme", platform="pygame")
                theme_provider = ThemeProvider(theme)
                self.component_factory = ThemeAwareComponentFactory(theme_provider)
                self.has_theme_support = True
                logger.info("Using theme-aware component factory (relative import)")
            except ImportError:
                # Fall back to basic component factory if theme system not available
                from MetaMindIQTrain.core.components import ComponentFactory
                self.component_factory = ComponentFactory()
                self.has_theme_support = False
                logger.warning("Theme system not available, using basic component factory")
        
        # Component render methods mapping
        self.component_renderers = {
            'text': self._draw_text_component,
            'rectangle': self._draw_rectangle_component,
            'circle': self._draw_circle_component,
            'shape': self._draw_shape_component,
            'grid': self._draw_grid_component,
            'container': self._draw_container_component,
            'button': self._draw_button_component,
            'progress': self._draw_progress_component,
            'timer': self._draw_timer_component,
            'image': self._draw_image_component,
            'symbol': self._draw_symbol_component
        }
        
        # Module-specific dispatch table
        self.module_renderers = {
            'expand_vision': self.render_expand_vision,
            'morph_matrix': self.render_morph_matrix,
            'symbol_memory': self.render_symbol_memory
        }
        
        # Track performance metrics
        self.render_time = 0
        self.component_count = 0
        self.frame_count = 0
        self.last_fps_update = time.time()
        self.current_fps = 0
        
        # Store the last state for incremental rendering
        self.last_state = None
        
        # Apply module-specific colors
        self._apply_module_colors(module_id)
        
        # Set up layout
        self._setup_layout()
        
        logger.info(f"Initialized EnhancedGenericRenderer for module {module_id}")
        
        # Load resolution scaling helpers from config
        try:
            from MetaMindIQTrain.config import scale_coordinates, scale_for_resolution, maintain_aspect_ratio
            self.scale_coordinates = scale_coordinates
            self.scale_for_resolution = scale_for_resolution
            self.maintain_aspect_ratio = maintain_aspect_ratio
        except ImportError:
            # Define fallback scaling methods
            self.scale_coordinates = lambda x, y, ow, oh, tw, th: (int(x * tw / ow), int(y * th / oh))
            self.scale_for_resolution = lambda val, old_dim, new_dim: int(val * new_dim / old_dim)
            self.maintain_aspect_ratio = lambda w, h, tw=None, th=None: (tw, int(tw * h / w)) if tw else (int(th * w / h), th)
    
    def _apply_module_colors(self, module_id):
        """Apply module-specific colors if available."""
        if not HAS_MODULE_COLORS:
            return
            
        if module_id in MODULE_COLORS:
            module_colors = MODULE_COLORS[module_id]
            # Update renderer colors with module-specific ones
            for key, value in module_colors.items():
                if isinstance(value, (list, tuple)) and not isinstance(value[0], (list, tuple)):
                    # It's a single color tuple, not a list of colors
                    if key not in self.colors:
                        self.colors[key] = value
    
    def _setup_layout(self):
        """Set up layout based on screen dimensions."""
        # Calculate sizes based on actual screen dimensions
        self.sizes = calculate_sizes(self.actual_width, self.actual_height)
        
        # Define standard layout sections based on calculated sizes
        self.header_rect = pygame.Rect(0, 0, self.actual_width, self.sizes['UI_HEADER_HEIGHT'])
        self.content_rect = pygame.Rect(
            0, 
            self.sizes['UI_CONTENT_TOP'], 
            self.actual_width, 
            self.sizes['UI_CONTENT_HEIGHT']
        )
        self.footer_rect = pygame.Rect(
            0, 
            self.sizes['UI_CONTENT_BOTTOM'], 
            self.actual_width, 
            self.sizes['UI_FOOTER_HEIGHT']
        )
    
    def scale_position(self, x, y):
        """Scale a position based on the current resolution.
        
        Args:
            x: X coordinate (in base resolution coordinates)
            y: Y coordinate (in base resolution coordinates)
            
        Returns:
            Tuple of scaled coordinates
        """
        return self.scale_coordinates(x, y, self.width, self.height, self.actual_width, self.actual_height)
    
    def scale_size(self, width, height):
        """Scale a size based on the current resolution.
        
        Args:
            width: Width (in base resolution)
            height: Height (in base resolution)
            
        Returns:
            Tuple of scaled dimensions
        """
        scaled_w = self.scale_for_resolution(width, self.width, self.actual_width)
        scaled_h = self.scale_for_resolution(height, self.height, self.actual_height)
        return (scaled_w, scaled_h)
    
    def scale_rect(self, rect):
        """Scale a rectangle based on the current resolution.
        
        Args:
            rect: Rectangle (pygame.Rect or tuple) in base resolution
            
        Returns:
            Scaled pygame.Rect
        """
        if isinstance(rect, pygame.Rect):
            x, y, w, h = rect.x, rect.y, rect.width, rect.height
        else:
            x, y, w, h = rect
            
        scaled_x, scaled_y = self.scale_position(x, y)
        scaled_w, scaled_h = self.scale_size(w, h)
        
        return pygame.Rect(scaled_x, scaled_y, scaled_w, scaled_h)
    
    def create_component(self, component_type, properties=None, children=None):
        """Create a new component with the theme-aware component factory.
        
        Args:
            component_type: Type of component to create
            properties: Component properties
            children: Child components
            
        Returns:
            The created component
        """
        return self.component_factory.create(
            component_type=component_type,
            properties=properties or {},
            children=children or []
        )
    
    def render(self, state):
        """Render the current state of the module.
        
        Args:
            state: Module state dictionary
            
        Returns:
            True if rendering was successful
        """
        # Record start time for performance measurement
        start_time = time.time()
        
        # Store current state
        self.current_state = state
        
        # Check if module_id is in state, if not add it
        if 'module_id' not in state and self.module_id:
            state['module_id'] = self.module_id
        
        # Draw standard layout
        self.draw_standard_layout(state)
        
        # Dispatch to module-specific renderer if available
        module_id = state.get('module_id', self.module_id)
        if module_id in self.module_renderers:
            self.module_renderers[module_id](state)
        else:
            # Fall back to generic rendering
            self._render_generic(state)
        
        # Update performance metrics
        self.render_time = time.time() - start_time
        self.frame_count += 1
        
        # Update FPS counter every second
        if time.time() - self.last_fps_update > 1.0:
            self.current_fps = self.frame_count
            self.frame_count = 0
            self.last_fps_update = time.time()
        
        # Store state for next frame
        self.last_state = state.copy()
        
        return True

    def _render_animated_components(self, state):
        """Render only components that need constant updates (animations, timers).
        
        Args:
            state: Current module state
        """
        # Extract components that might need constant updates
        components = state.get('ui', {}).get('components', [])
        animated_types = ['timer', 'progress']
        
        for component in components:
            component_type = component.get('type')
            if component_type in animated_types:
                self._render_component(component_type, component)

    def _render_component(self, component_type, component):
        """Render a component using the appropriate renderer.
        
        Args:
            component_type: Type of component to render
            component: Component data
            
        Returns:
            True if component was rendered, False otherwise
        """
        # Skip invalid components
        if not component or not isinstance(component, dict):
            return False
            
        # Extract common properties
        position = component.get('position', (0, 0))
        
        # Scale position to actual screen size
        scaled_position = self.scale_position(position[0], position[1])
        
        # Generate cache key for this component
        cache_key = str(hash(str(component)))
        
        # Check if we have a cached surface
        cached_surface = self.render_cache.get(cache_key)
        if cached_surface:
            # Use cached surface
            self.screen.blit(cached_surface, scaled_position)
            return True
            
        # Look up renderer for this component type
        renderer = self.component_renderers.get(component_type)
        if renderer:
            # Create a surface for this component
            # We create the surface at the original size and scale when blitting
            if 'width' in component and 'height' in component:
                width, height = component.get('width'), component.get('height')
                scaled_width, scaled_height = self.scale_size((width, height))
                component_surface = pygame.Surface((scaled_width, scaled_height), pygame.SRCALPHA)
            else:
                # For components without explicit dimensions, use a temporary surface
                component_surface = pygame.Surface((self.actual_width, self.actual_height), pygame.SRCALPHA)
                
            # Render the component to the surface
            result = renderer(component, component_surface, (0, 0))
            
            if result:
                # Blit the component surface to the screen
                self.screen.blit(component_surface, scaled_position)
                
                # Cache the component surface
                self.render_cache.set(cache_key, component_surface)
                
                return True
                
        # Component wasn't rendered
        return False

    def _render_components(self, components):
        """Render a list of components.
        
        Args:
            components: List of component data
            
        Returns:
            Number of components rendered
        """
        rendered_count = 0
        
        # Track component count for performance metrics
        self.component_count = len(components) if components else 0
        
        # Sort components by zIndex if available
        sorted_components = sorted(components, key=lambda c: c.get('zIndex', 0)) if components else []
        
        # Render each component
        for component in sorted_components:
            component_type = component.get('type')
            if self._render_component(component_type, component):
                rendered_count += 1
                
        return rendered_count
        
    def _draw_text_component(self, component, surface, offset):
        """Draw a text component.
        
        Args:
            component: Text component data
            surface: Surface to draw on
            offset: (x, y) offset to apply
            
        Returns:
            True if component was rendered, False otherwise
        """
        # Extract properties
        text = component.get('text', '')
        font_size = component.get('fontSize', 20)
        color = component.get('color', (255, 255, 255))
        align = component.get('align', 'left')
        
        # Scale font size
        scaled_font_size = self.scale_for_resolution(font_size, self.height, self.actual_height)
        
        # Choose font based on size
        if scaled_font_size >= 36:
            font = self.title_font
        elif scaled_font_size >= 24:
            font = self.regular_font
        else:
            font = self.small_font
            
        # Render text
        text_surface = font.render(str(text), True, color)
        
        # Position based on alignment
        if align == 'center':
            pos = (offset[0] + (surface.get_width() - text_surface.get_width()) // 2, offset[1])
        elif align == 'right':
            pos = (offset[0] + surface.get_width() - text_surface.get_width(), offset[1])
        else:  # left align
            pos = offset
            
        # Draw text
        surface.blit(text_surface, pos)
        return True

    def _draw_rectangle_component(self, component, surface, offset):
        """Draw a rectangle component.
        
        Args:
            component: Rectangle component data
            surface: Surface to draw on
            offset: (x, y) offset to apply
            
        Returns:
            True if component was rendered, False otherwise
        """
        # Extract properties
        width = component.get('width', 100)
        height = component.get('height', 100)
        bg_color = component.get('backgroundColor', (100, 100, 100))
        border_width = component.get('borderWidth', 0)
        border_color = component.get('borderColor', (0, 0, 0))
        border_radius = component.get('borderRadius', 0)
        
        # Scale to actual screen size
        scaled_width, scaled_height = self.scale_size((width, height))
        scaled_border_width = max(1, self.scale_for_resolution(border_width, self.height, self.actual_height))
        scaled_border_radius = self.scale_for_resolution(border_radius, self.height, self.actual_height)
        
        # Create rectangle
        rect = pygame.Rect(offset[0], offset[1], scaled_width, scaled_height)
        
        # Draw filled rectangle with border radius if supported
        if border_radius > 0 and pygame.version.vernum[0] >= 2:
            # Draw background
            pygame.draw.rect(surface, bg_color, rect, 0, scaled_border_radius)
            
            # Draw border if needed
            if border_width > 0:
                pygame.draw.rect(surface, border_color, rect, scaled_border_width, scaled_border_radius)
        else:
            # Draw background
            pygame.draw.rect(surface, bg_color, rect, 0)
            
            # Draw border if needed
            if border_width > 0:
                pygame.draw.rect(surface, border_color, rect, scaled_border_width)
                
        return True

    def _render_generic(self, state):
        """Render the module using the generic approach.
        
        Args:
            state: Current module state
        """
        # Render UI components
        if 'ui' in state and 'components' in state['ui']:
            self._render_components(state['ui']['components'])
        
        # Render module-specific UI elements
        content_rect = self.get_content_rect()
        
        # Draw basic module info if no components
        if 'ui' not in state or not state['ui'].get('components'):
            self._render_basic_info()
        
        # Draw UI chrome (header, footer)
        self._render_ui_chrome(state)

    def _render_basic_info(self):
        """Render basic module information when no components are available."""
        content_rect = self.get_content_rect()
        center_x = content_rect.left + content_rect.width // 2
        center_y = content_rect.top + content_rect.height // 2
        
        # Draw module ID
        module_text = f"Module: {self.module_id}"
        self.draw_text(
            module_text,
            center_x,
            center_y - 40,
            self.title_font,
            self.colors['text_primary'],
            centered=True
        )
        
        # Draw help text
        help_text = "No components to render. This module may not be fully implemented."
        self.draw_text(
            help_text,
            center_x,
            center_y,
            self.regular_font,
            self.colors['text_secondary'],
            centered=True
        )
        
        # Draw instructions
        instructions = "Check the module implementation to ensure it provides UI components."
        self.draw_text(
            instructions,
            center_x,
            center_y + 40,
            self.small_font,
            self.colors['text_secondary'],
            centered=True
        )

    def _render_ui_chrome(self, state):
        """Render UI chrome (header, footer, fps counter).
        
        Args:
            state: Current module state
        """
        # Draw performance metrics in corner if enabled
        if self.config.get('show_performance_metrics', True):
            metrics_text = f"FPS: {self.current_fps} | Render: {self.render_time*1000:.1f}ms | Components: {self.component_count}"
            self.draw_text(
                metrics_text,
                10,
                self.height - 15,
                self.small_font,
                self.colors['text_secondary'],
                centered=False
            )
        
        # Draw module name in header if available
        if 'module' in state and 'name' in state['module']:
            module_name = state['module']['name']
            self.draw_text(
                module_name,
                self.width // 2,
                self.layout['header']['height'] // 2,
                self.title_font,
                self.colors['text_highlight'],
                centered=True
            )

    def render_expand_vision(self, state):
        """Specialized rendering for the Expand Vision module using component-based approach.
        
        Args:
            state (dict): The current state of the module.
        
        Returns:
            None: Updates the screen in place.
        """
        # Set up the rendering area
        self._setup_rendering_area(state)
        
        # Extract components from state
        components = state.get('components', [])
        
        # Render all components
        self._render_components(components)
    
    def render_morph_matrix(self, state):
        """Specialized rendering for the Morph Matrix module using component-based approach.
        
        Args:
            state (dict): The current state of the module.
        
        Returns:
            None: Updates the screen in place.
        """
        # Set up the rendering area
        self._setup_rendering_area(state)
        
        # Extract components from state
        components = state.get('components', [])
        
        # Render all components
        self._render_components(components)
    
    def render_symbol_memory(self, state):
        """Specialized rendering for the Symbol Memory module using component-based approach.
        
        Args:
            state (dict): The current state of the module.
        
        Returns:
            None: Updates the screen in place.
        """
        # Set up the rendering area
        self._setup_rendering_area(state)
        
        # Extract components from state
        components = state.get('components', [])
        
        # Render all components
        self._render_components(components)
    
    def _setup_rendering_area(self, state):
        """Set up the rendering area for a module.
        
        Args:
            state (dict): The current state of the module.
        """
        # Clear the screen with the background color
        self.screen.fill(self.colors['background'])
        
        # Set up layout if not already done
        if not self.layout:
            self._setup_layout()
        
        # Apply module-specific colors
        self._apply_module_colors(self.module_id)
        
        # Check if we have a specialized renderer for this module
        # These are optimized renderers for specific modules
        if self.module_id == 'expand_vision':
            self.render_expand_vision(state)
        elif self.module_id == 'morph_matrix':
            self.render_morph_matrix(state)
        elif self.module_id == 'symbol_memory':
            self.render_symbol_memory(state)
            
        # If no specialized renderer, use the generic renderer
        # for any other module based on component system
        else:
            self._render_generic(state) 