#!/usr/bin/env python3
"""
Theme-Aware Component Renderer for PyGame

This module provides a renderer that draws UI components according to the theme system,
ensuring consistent styling across the application.
"""

import pygame
import logging
import math
import time
from typing import Dict, Any, List, Tuple, Optional, Union, Callable
import hashlib

# Try to import from the package
try:
    from MetaMindIQTrain.core.theme import Theme, get_theme, ThemeProvider
    from MetaMindIQTrain.core.components import ThemeAwareComponentFactory, Component
    from MetaMindIQTrain.clients.pygame.renderers.enhanced_generic_renderer import EnhancedGenericRenderer
    from MetaMindIQTrain.config import (
        scale_coordinates, 
        scale_for_resolution, 
        maintain_aspect_ratio,
        calculate_sizes
    )
except ImportError:
    # For direct execution during development
    import sys
    import os
    from pathlib import Path
    
    # Add the project root to the path
    project_root = Path(__file__).resolve().parent.parent.parent.parent
    sys.path.insert(0, str(project_root))
    
    # Now import from the absolute path
    from MetaMindIQTrain.core.theme import Theme, get_theme, ThemeProvider
    from MetaMindIQTrain.core.components import ThemeAwareComponentFactory, Component
    from MetaMindIQTrain.clients.pygame.renderers.enhanced_generic_renderer import EnhancedGenericRenderer
    from MetaMindIQTrain.config import (
        scale_coordinates, 
        scale_for_resolution, 
        maintain_aspect_ratio,
        calculate_sizes
    )

logger = logging.getLogger(__name__)

class ThemeComponentRenderer(EnhancedGenericRenderer):
    """Theme-aware component renderer for PyGame that uses the theme system."""
    
    def __init__(self, screen, module_id=None, config=None, **kwargs):
        """Initialize the theme component renderer.
        
        Args:
            screen: PyGame screen surface
            module_id: ID of the module to render
            config: Optional configuration dictionary
            **kwargs: Additional arguments passed to EnhancedGenericRenderer
        """
        # Call the parent class constructor
        super().__init__(screen, module_id, config, **kwargs)
        
        # Initialize theme system
        self.theme = get_theme()
        if not self.theme:
            from MetaMindIQTrain.core.theme import create_dark_theme
            self.theme = create_dark_theme()
            logger.info("Created default dark theme")
        
        self.theme_provider = ThemeProvider(self.theme)
        self.component_factory = ThemeAwareComponentFactory(self.theme_provider)
        
        # Component render cache for improved performance
        self.component_render_cache = {}
        self.cache_max_size = 200
        self.cache_ttl = 5.0  # 5 seconds time-to-live
        self.cache_timestamps = {}
        
        logger.info(f"Initialized ThemeComponentRenderer with theme: {self.theme.name}")
    
    def _generate_cache_key(self, component_type, properties, variant, state):
        """Generate a cache key for the component.
        
        Args:
            component_type: Type of component
            properties: Component properties
            variant: Component variant
            state: Component state
            
        Returns:
            Cache key string
        """
        # Convert properties to a sorted list of items
        props_list = []
        for key, value in sorted(properties.items()):
            if isinstance(value, (list, tuple)):
                # Convert lists/tuples to strings
                props_list.append(f"{key}:{','.join(map(str, value))}")
            else:
                props_list.append(f"{key}:{value}")
        
        # Create a string with all information
        cache_str = f"{component_type}:{variant or 'default'}:{state or 'default'}:{','.join(props_list)}"
        
        # Use MD5 hash for a fixed-length cache key
        return hashlib.md5(cache_str.encode()).hexdigest()
    
    def _get_cached_component(self, key):
        """Get a cached component if available and not expired.
        
        Args:
            key: Cache key
            
        Returns:
            Cached surface or None
        """
        if key in self.component_render_cache:
            # Check if the cached item has expired
            now = time.time()
            if now - self.cache_timestamps.get(key, 0) < self.cache_ttl:
                self.cache_timestamps[key] = now  # Update access time
                return self.component_render_cache[key]
            else:
                # Remove expired item
                del self.component_render_cache[key]
                if key in self.cache_timestamps:
                    del self.cache_timestamps[key]
        
        return None
    
    def _cache_component(self, key, surface):
        """Cache a rendered component.
        
        Args:
            key: Cache key
            surface: Rendered surface
        """
        # Clean up cache if it's too large
        if len(self.component_render_cache) >= self.cache_max_size:
            # Remove the oldest item
            oldest_key = min(self.cache_timestamps, key=lambda k: self.cache_timestamps[k])
            del self.component_render_cache[oldest_key]
            del self.cache_timestamps[oldest_key]
        
        # Add the new item to the cache
        self.component_render_cache[key] = surface.copy()
        self.cache_timestamps[key] = time.time()
    
    def render_text(self, text, position, variant=None, state=None, **kwargs):
        """Render themed text.
        
        Args:
            text: Text content
            position: (x, y) position
            variant: Optional variant name (title, subtitle, caption, label)
            state: Optional state name (disabled, highlighted, error)
            **kwargs: Additional style overrides
            
        Returns:
            Rendered surface and rect
        """
        # Get style from theme
        style = self.theme_provider.get_style("text", variant, state, **kwargs)
        
        # Scale position to actual screen size
        scaled_position = self.scale_position(*position)
        
        # Create component properties
        properties = {
            "text": text,
            "fontSize": style.get("fontSize", 20),
            "color": style.get("color", (255, 255, 255)),
            "textAlign": style.get("textAlign", "left"),
            "fontWeight": style.get("fontWeight", "normal"),
            "opacity": style.get("opacity", 1.0)
        }
        
        # Override with any provided properties
        properties.update(kwargs)
        
        # Generate cache key
        cache_key = self._generate_cache_key("text", properties, variant, state)
        
        # Check cache first
        cached_surface = self._get_cached_component(cache_key)
        if cached_surface:
            # Calculate position based on alignment
            rect = cached_surface.get_rect()
            align = properties.get("textAlign", "left")
            
            if align == "center":
                rect.centerx = scaled_position[0]
                rect.y = scaled_position[1]
            elif align == "right":
                rect.right = scaled_position[0]
                rect.y = scaled_position[1]
            else:  # left
                rect.x = scaled_position[0]
                rect.y = scaled_position[1]
                
            # Draw to screen
            self.screen.blit(cached_surface, rect)
            return cached_surface, rect
        
        # Get font
        font_size = self.scale_for_resolution(properties["fontSize"], self.height, self.actual_height)
        font = pygame.font.Font(None, font_size)
        
        # Apply font weight if supported
        if pygame.font.get_init():
            font_weight = properties.get("fontWeight", "normal")
            if font_weight == "bold":
                try:
                    font.set_bold(True)
                except:
                    pass
            
        # Render text
        color = properties["color"]
        opacity = properties["opacity"]
        
        # Apply opacity to color if needed
        if opacity < 1.0 and len(color) == 3:
            color = (*color, int(255 * opacity))
        
        # Render text
        text_surface = font.render(text, True, color)
        
        # Calculate position based on alignment
        rect = text_surface.get_rect()
        align = properties.get("textAlign", "left")
        
        if align == "center":
            rect.centerx = scaled_position[0]
            rect.y = scaled_position[1]
        elif align == "right":
            rect.right = scaled_position[0]
            rect.y = scaled_position[1]
        else:  # left
            rect.x = scaled_position[0]
            rect.y = scaled_position[1]
        
        # Cache the rendered surface
        self._cache_component(cache_key, text_surface)
        
        # Draw to screen
        self.screen.blit(text_surface, rect)
        
        return text_surface, rect
    
    def render_rectangle(self, position, size, variant=None, state=None, **kwargs):
        """Render themed rectangle.
        
        Args:
            position: (x, y) position
            size: (width, height) size
            variant: Optional variant name (card, panel)
            state: Optional state name (disabled, highlighted)
            **kwargs: Additional style overrides
            
        Returns:
            Rendered surface and rect
        """
        # Get style from theme
        style = self.theme_provider.get_style("rect", variant, state, **kwargs)
        
        # Scale position and size to actual screen dimensions
        scaled_position = self.scale_position(*position)
        scaled_size = self.scale_size(*size)
        
        # Create properties
        properties = {
            "width": scaled_size[0],
            "height": scaled_size[1],
            "backgroundColor": style.get("backgroundColor", (100, 100, 100)),
            "borderWidth": self.scale_for_resolution(
                style.get("borderWidth", 0), 
                self.height, 
                self.actual_height
            ),
            "borderColor": style.get("borderColor", (0, 0, 0)),
            "borderRadius": self.scale_for_resolution(
                style.get("borderRadius", 0), 
                self.height, 
                self.actual_height
            ),
            "opacity": style.get("opacity", 1.0)
        }
        
        # Override with any provided properties
        properties.update(kwargs)
        
        # Generate cache key
        cache_key = self._generate_cache_key("rectangle", properties, variant, state)
        
        # Check cache first
        cached_surface = self._get_cached_component(cache_key)
        if cached_surface:
            rect = pygame.Rect(scaled_position, scaled_size)
            self.screen.blit(cached_surface, rect)
            return cached_surface, rect
        
        # Create surface
        surface = pygame.Surface(scaled_size, pygame.SRCALPHA)
        
        # Get properties
        bg_color = properties["backgroundColor"]
        border_width = properties["borderWidth"]
        border_color = properties["borderColor"]
        border_radius = properties["borderRadius"]
        opacity = properties["opacity"]
        
        # Apply opacity to colors if needed
        if opacity < 1.0:
            if len(bg_color) == 3:
                bg_color = (*bg_color, int(255 * opacity))
            elif len(bg_color) == 4:
                bg_color = (*bg_color[:3], int(bg_color[3] * opacity))
                
            if len(border_color) == 3:
                border_color = (*border_color, int(255 * opacity))
            elif len(border_color) == 4:
                border_color = (*border_color[:3], int(border_color[3] * opacity))
        
        # Draw rectangle
        rect = pygame.Rect(0, 0, scaled_size[0], scaled_size[1])
        
        if border_radius > 0:
            # Draw with rounded corners
            if border_width > 0:
                # Draw border
                pygame.draw.rect(surface, border_color, rect, border_radius=border_radius)
                
                # Draw inner rectangle (content)
                inner_rect = rect.inflate(-border_width*2, -border_width*2)
                pygame.draw.rect(surface, bg_color, inner_rect, border_radius=max(0, border_radius-border_width))
            else:
                # Draw filled rectangle
                pygame.draw.rect(surface, bg_color, rect, border_radius=border_radius)
        else:
            # Draw regular rectangle
            if border_width > 0:
                # Draw filled rectangle
                pygame.draw.rect(surface, bg_color, rect)
                
                # Draw border
                pygame.draw.rect(surface, border_color, rect, border_width)
            else:
                # Draw filled rectangle
                pygame.draw.rect(surface, bg_color, rect)
        
        # Cache the rendered surface
        self._cache_component(cache_key, surface)
        
        # Draw to screen
        screen_rect = pygame.Rect(scaled_position, scaled_size)
        self.screen.blit(surface, screen_rect)
        
        return surface, screen_rect
    
    def render_circle(self, center, radius, variant=None, state=None, **kwargs):
        """Render themed circle.
        
        Args:
            center: (x, y) center position
            radius: Circle radius
            variant: Optional variant name (indicator, status)
            state: Optional state name (active, success, error)
            **kwargs: Additional style overrides
            
        Returns:
            Rendered surface and rect
        """
        # Get style from theme
        style = self.theme_provider.get_style("circle", variant, state, **kwargs)
        
        # Scale center and radius to actual screen dimensions
        scaled_center = self.scale_position(*center)
        scaled_radius = self.scale_for_resolution(radius, self.height, self.actual_height)
        
        # Create properties
        properties = {
            "radius": scaled_radius,
            "backgroundColor": style.get("backgroundColor", (100, 100, 100)),
            "borderWidth": self.scale_for_resolution(
                style.get("borderWidth", 0), 
                self.height, 
                self.actual_height
            ),
            "borderColor": style.get("borderColor", (0, 0, 0)),
            "opacity": style.get("opacity", 1.0)
        }
        
        # Override with any provided properties
        properties.update(kwargs)
        
        # Generate cache key
        cache_key = self._generate_cache_key("circle", properties, variant, state)
        
        # Check cache first
        cached_surface = self._get_cached_component(cache_key)
        if cached_surface:
            rect = cached_surface.get_rect(center=scaled_center)
            self.screen.blit(cached_surface, rect)
            return cached_surface, rect
        
        # Get properties
        radius = properties["radius"]
        bg_color = properties["backgroundColor"]
        border_width = properties["borderWidth"]
        border_color = properties["borderColor"]
        opacity = properties["opacity"]
        
        # Apply opacity to colors if needed
        if opacity < 1.0:
            if len(bg_color) == 3:
                bg_color = (*bg_color, int(255 * opacity))
            elif len(bg_color) == 4:
                bg_color = (*bg_color[:3], int(bg_color[3] * opacity))
                
            if len(border_color) == 3:
                border_color = (*border_color, int(255 * opacity))
            elif len(border_color) == 4:
                border_color = (*border_color[:3], int(border_color[3] * opacity))
        
        # Create surface
        size = (radius * 2, radius * 2)
        surface = pygame.Surface(size, pygame.SRCALPHA)
        
        # Draw circle
        center_pos = (radius, radius)
        
        if border_width > 0:
            # Draw filled circle
            pygame.draw.circle(surface, bg_color, center_pos, radius - border_width)
            
            # Draw border
            pygame.draw.circle(surface, border_color, center_pos, radius, border_width)
        else:
            # Draw filled circle
            pygame.draw.circle(surface, bg_color, center_pos, radius)
        
        # Cache the rendered surface
        self._cache_component(cache_key, surface)
        
        # Draw to screen
        rect = surface.get_rect(center=scaled_center)
        self.screen.blit(surface, rect)
        
        return surface, rect
    
    def render_button(self, text, position, size, variant=None, state=None, **kwargs):
        """Render themed button.
        
        Args:
            text: Button text
            position: (x, y) position
            size: (width, height) size
            variant: Optional variant name (primary, secondary, outline, text)
            state: Optional state name (hover, active, disabled)
            **kwargs: Additional style overrides
            
        Returns:
            Rendered surface and rect
        """
        # Get style from theme
        style = self.theme_provider.get_style("button", variant, state, **kwargs)
        
        # Scale position and size to actual screen dimensions
        scaled_position = self.scale_position(*position)
        scaled_size = self.scale_size(*size)
        
        # Create properties
        properties = {
            "text": text,
            "width": scaled_size[0],
            "height": scaled_size[1],
            "backgroundColor": style.get("backgroundColor", (100, 100, 100)),
            "color": style.get("color", (255, 255, 255)),
            "borderWidth": self.scale_for_resolution(
                style.get("borderWidth", 0), 
                self.height, 
                self.actual_height
            ),
            "borderColor": style.get("borderColor", (0, 0, 0)),
            "borderRadius": self.scale_for_resolution(
                style.get("borderRadius", 0), 
                self.height, 
                self.actual_height
            ),
            "fontSize": style.get("fontSize", 20),
            "fontWeight": style.get("fontWeight", "normal"),
            "padding": self.scale_for_resolution(
                style.get("padding", 0), 
                self.height, 
                self.actual_height
            ),
            "textAlign": "center",
            "opacity": style.get("opacity", 1.0)
        }
        
        # Override with any provided properties
        properties.update(kwargs)
        
        # Generate cache key
        cache_key = self._generate_cache_key("button", properties, variant, state)
        
        # Check cache first
        cached_surface = self._get_cached_component(cache_key)
        if cached_surface:
            rect = pygame.Rect(scaled_position, scaled_size)
            self.screen.blit(cached_surface, rect)
            return cached_surface, rect
        
        # Create button surface
        surface = pygame.Surface(scaled_size, pygame.SRCALPHA)
        
        # Get properties
        bg_color = properties["backgroundColor"]
        text_color = properties["color"]
        border_width = properties["borderWidth"]
        border_color = properties["borderColor"]
        border_radius = properties["borderRadius"]
        opacity = properties["opacity"]
        
        # Apply opacity to colors if needed
        if opacity < 1.0:
            if len(bg_color) == 3:
                bg_color = (*bg_color, int(255 * opacity))
            elif len(bg_color) == 4:
                bg_color = (*bg_color[:3], int(bg_color[3] * opacity))
                
            if len(border_color) == 3:
                border_color = (*border_color, int(255 * opacity))
            elif len(border_color) == 4:
                border_color = (*border_color[:3], int(border_color[3] * opacity))
                
            if len(text_color) == 3:
                text_color = (*text_color, int(255 * opacity))
            elif len(text_color) == 4:
                text_color = (*text_color[:3], int(text_color[3] * opacity))
        
        # Draw button background
        rect = pygame.Rect(0, 0, scaled_size[0], scaled_size[1])
        
        if border_radius > 0:
            # Draw with rounded corners
            if border_width > 0:
                # Draw border
                pygame.draw.rect(surface, border_color, rect, border_radius=border_radius)
                
                # Draw inner rectangle (content)
                inner_rect = rect.inflate(-border_width*2, -border_width*2)
                pygame.draw.rect(surface, bg_color, inner_rect, border_radius=max(0, border_radius-border_width))
            else:
                # Draw filled rectangle
                pygame.draw.rect(surface, bg_color, rect, border_radius=border_radius)
        else:
            # Draw regular rectangle
            if border_width > 0:
                # Draw filled rectangle
                pygame.draw.rect(surface, bg_color, rect)
                
                # Draw border
                pygame.draw.rect(surface, border_color, rect, border_width)
            else:
                # Draw filled rectangle
                pygame.draw.rect(surface, bg_color, rect)
        
        # Draw text
        font_size = self.scale_for_resolution(properties["fontSize"], self.height, self.actual_height)
        font = pygame.font.Font(None, font_size)
        
        # Apply font weight if supported
        if pygame.font.get_init():
            font_weight = properties.get("fontWeight", "normal")
            if font_weight == "bold":
                try:
                    font.set_bold(True)
                except:
                    pass
        
        # Render text
        text_surface = font.render(text, True, text_color)
        
        # Position text in center of button
        text_rect = text_surface.get_rect(center=(scaled_size[0]//2, scaled_size[1]//2))
        surface.blit(text_surface, text_rect)
        
        # Cache the rendered surface
        self._cache_component(cache_key, surface)
        
        # Draw to screen
        screen_rect = pygame.Rect(scaled_position, scaled_size)
        self.screen.blit(surface, screen_rect)
        
        return surface, screen_rect
    
    def render_progress(self, position, size, value, variant=None, state=None, **kwargs):
        """Render themed progress bar.
        
        Args:
            position: (x, y) position
            size: (width, height) size
            value: Progress value (0.0-1.0)
            variant: Optional variant name (success, warning, error)
            state: Optional state name
            **kwargs: Additional style overrides
            
        Returns:
            Rendered surface and rect
        """
        # Get style from theme
        style = self.theme_provider.get_style("progress", variant, state, **kwargs)
        
        # Scale position and size to actual screen dimensions
        scaled_position = self.scale_position(*position)
        scaled_size = self.scale_size(*size)
        
        # Create properties
        properties = {
            "width": scaled_size[0],
            "height": scaled_size[1],
            "backgroundColor": style.get("backgroundColor", (50, 50, 50)),
            "fillColor": style.get("fillColor", (0, 255, 0)),
            "borderRadius": self.scale_for_resolution(
                style.get("borderRadius", 0), 
                self.height, 
                self.actual_height
            ),
            "value": max(0.0, min(1.0, value)),  # Clamp to 0.0-1.0
            "opacity": style.get("opacity", 1.0)
        }
        
        # Override with any provided properties
        properties.update(kwargs)
        
        # Generate cache key
        cache_key = self._generate_cache_key("progress", {**properties, "value": int(value * 100)}, variant, state)
        
        # Check cache first
        cached_surface = self._get_cached_component(cache_key)
        if cached_surface:
            rect = pygame.Rect(scaled_position, scaled_size)
            self.screen.blit(cached_surface, rect)
            return cached_surface, rect
        
        # Create progress bar surface
        surface = pygame.Surface(scaled_size, pygame.SRCALPHA)
        
        # Get properties
        width = properties["width"]
        height = properties["height"]
        bg_color = properties["backgroundColor"]
        fill_color = properties["fillColor"]
        border_radius = properties["borderRadius"]
        value = properties["value"]
        opacity = properties["opacity"]
        
        # Apply opacity to colors if needed
        if opacity < 1.0:
            if len(bg_color) == 3:
                bg_color = (*bg_color, int(255 * opacity))
            elif len(bg_color) == 4:
                bg_color = (*bg_color[:3], int(bg_color[3] * opacity))
                
            if len(fill_color) == 3:
                fill_color = (*fill_color, int(255 * opacity))
            elif len(fill_color) == 4:
                fill_color = (*fill_color[:3], int(fill_color[3] * opacity))
        
        # Draw background
        bg_rect = pygame.Rect(0, 0, width, height)
        
        if border_radius > 0:
            pygame.draw.rect(surface, bg_color, bg_rect, border_radius=border_radius)
        else:
            pygame.draw.rect(surface, bg_color, bg_rect)
        
        # Draw fill if value > 0
        if value > 0:
            fill_width = int(width * value)
            fill_rect = pygame.Rect(0, 0, fill_width, height)
            
            if border_radius > 0:
                # Clip the fill rectangle to stay within the background
                fill_surf = pygame.Surface((fill_width, height), pygame.SRCALPHA)
                pygame.draw.rect(fill_surf, fill_color, pygame.Rect(0, 0, fill_width, height), border_radius=border_radius)
                surface.blit(fill_surf, (0, 0))
            else:
                pygame.draw.rect(surface, fill_color, fill_rect)
        
        # Cache the rendered surface
        self._cache_component(cache_key, surface)
        
        # Draw to screen
        screen_rect = pygame.Rect(scaled_position, scaled_size)
        self.screen.blit(surface, screen_rect)
        
        return surface, screen_rect
    
    def render_container(self, position, size, children=None, variant=None, state=None, **kwargs):
        """Render themed container with optional child components.
        
        Args:
            position: (x, y) position
            size: (width, height) size
            children: Optional list of child components to render
            variant: Optional variant name (modal, panel)
            state: Optional state name
            **kwargs: Additional style overrides
            
        Returns:
            Rendered surface and rect
        """
        # First render the container background
        surface, rect = self.render_rectangle(position, size, variant, state, **kwargs)
        
        # Render children if provided
        if children:
            for child in children:
                # Child positions are relative to container
                child_pos = (position[0] + child.position[0], position[1] + child.position[1])
                
                # Render based on child type
                if child.type == "text":
                    self.render_text(
                        child.properties.get("text", ""), 
                        child_pos,
                        variant=child.properties.get("variant"),
                        state=child.properties.get("state"),
                        **child.properties
                    )
                elif child.type == "rectangle":
                    self.render_rectangle(
                        child_pos,
                        (child.properties.get("width", 10), child.properties.get("height", 10)),
                        variant=child.properties.get("variant"),
                        state=child.properties.get("state"),
                        **child.properties
                    )
                elif child.type == "circle":
                    self.render_circle(
                        child_pos,
                        child.properties.get("radius", 5),
                        variant=child.properties.get("variant"),
                        state=child.properties.get("state"),
                        **child.properties
                    )
                elif child.type == "button":
                    self.render_button(
                        child.properties.get("text", ""),
                        child_pos,
                        (child.properties.get("width", 100), child.properties.get("height", 30)),
                        variant=child.properties.get("variant"),
                        state=child.properties.get("state"),
                        **child.properties
                    )
                elif child.type == "progress":
                    self.render_progress(
                        child_pos,
                        (child.properties.get("width", 100), child.properties.get("height", 10)),
                        child.properties.get("value", 0.5),
                        variant=child.properties.get("variant"),
                        state=child.properties.get("state"),
                        **child.properties
                    )
        
        return surface, rect

# Register the renderer
def register_renderer():
    """Register the theme component renderer."""
    return {
        "id": "theme",
        "name": "Theme Renderer",
        "renderer_class": ThemeComponentRenderer,
        "description": "Renders UI components using the theme system"
    } 