#!/usr/bin/env python3
"""
Base Component Renderer for MetaMindIQTrain

This module provides a base class for rendering components from the unified component system
in the PyGame client. It handles theme application, component caching, and efficient rendering.
"""

import pygame
import time
import logging
from typing import Dict, Any, List, Tuple, Optional, Set, Union
import os
import json
from functools import lru_cache

# Try to import from the package first
try:
    from MetaMindIQTrain.core.theme import Theme, get_theme
    from MetaMindIQTrain.core.unified_component_system import (
        Component, Container, Text, Image, Button, 
        Rectangle, Circle, Line, Grid, FlexContainer
    )
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

# Configure logging
logger = logging.getLogger(__name__)

# Constants
DEFAULT_CACHE_SIZE = 100
DEFAULT_MAX_COMPONENT_INSTANCES = 1000

class BaseComponentRenderer:
    """
    Base renderer for components using the unified component system.
    
    This renderer provides a bridge between the unified component system
    and PyGame rendering. It includes optimizations such as:
    
    1. Component caching - Rendered components are cached for reuse
    2. Dirty region tracking - Only redraw what changed
    3. Theme integration - Automatic theme application
    4. Component pooling - Reuse component instances
    5. Automatic scaling - Scale components based on screen size
    """
    
    def __init__(self, screen: pygame.Surface, module_id: str):
        """Initialize the base component renderer.
        
        Args:
            screen: PyGame screen surface
            module_id: ID of the module this renderer is for
        """
        self.screen = screen
        self.module_id = module_id
        self.width = screen.get_width()
        self.height = screen.get_height()
        
        # Component caching
        self.component_cache = {}
        self.dirty_regions = []
        self.dirty_state_keys = set()
        self.needs_full_redraw = True
        
        # State tracking
        self.last_state = {}
        self.current_state = {}
        
        # Theme
        self.theme = get_theme()
        self.theme_version = id(self.theme)
        
        # Font cache
        self.font_cache = {}
        
        # Surface cache
        self.surface_cache = {}
        
        # Component pool
        self.component_pool = {}
        self.component_pool_size = 0
        
        # Performance metrics
        self.render_count = 0
        self.last_render_time = 0
        self.render_times = []
        
        # Debug flags
        self.debug_mode = False
        self.show_dirty_regions = False
        
        # Initialize resources
        self._init_resources()
        
        logger.info(f"Base component renderer initialized for {module_id}")
    
    def _init_resources(self):
        """Initialize resources for the renderer."""
        # Set up component pools
        component_classes = [Container, Text, Image, Button, Rectangle, Circle, Line, Grid, FlexContainer]
        for cls in component_classes:
            self.component_pool[cls.__name__] = []
    
    def get_component(self, component_type: str, **props) -> Component:
        """Get a component from the pool or create a new one.
        
        Args:
            component_type: Type of component to get
            **props: Properties to set on the component
            
        Returns:
            Component: The component instance
        """
        # Check if we've reached the pool size limit
        if self.component_pool_size >= DEFAULT_MAX_COMPONENT_INSTANCES:
            # Create a temporary component (not pooled)
            cls = globals()[component_type]
            return cls(**props)
        
        # Get from pool or create new
        pool = self.component_pool.get(component_type, [])
        
        if pool:
            # Reuse existing component
            component = pool.pop()
            # Reset and update props
            for key, value in props.items():
                setattr(component, key, value)
            return component
        else:
            # Create new component
            cls = globals()[component_type]
            component = cls(**props)
            self.component_pool_size += 1
            return component
    
    def release_component(self, component: Component):
        """Release a component back to the pool.
        
        Args:
            component: Component to release
        """
        if self.component_pool_size < DEFAULT_MAX_COMPONENT_INSTANCES:
            component_type = component.__class__.__name__
            if component_type not in self.component_pool:
                self.component_pool[component_type] = []
            self.component_pool[component_type].append(component)
    
    @lru_cache(maxsize=DEFAULT_CACHE_SIZE)
    def get_font(self, size: int, bold: bool = False, italic: bool = False) -> pygame.font.Font:
        """Get or create a PyGame font.
        
        Args:
            size: Font size
            bold: Whether the font should be bold
            italic: Whether the font should be italic
            
        Returns:
            pygame.font.Font: The font instance
        """
        # Use system default font
        try:
            # Try to use a nicer default font if available
            default_font = pygame.font.get_default_font()
            return pygame.font.Font(default_font, size)
        except:
            # Fall back to basic font
            return pygame.font.Font(None, size)
    
    def register_dirty_region(self, rect: pygame.Rect):
        """Register a region that needs to be redrawn.
        
        Args:
            rect: Rectangle defining the dirty region
        """
        self.dirty_regions.append(rect)
    
    def mark_state_key_dirty(self, key: str):
        """Mark a state key as dirty, requiring component updates.
        
        Args:
            key: State key that has changed
        """
        self.dirty_state_keys.add(key)
    
    def clear_dirty_regions(self):
        """Clear all dirty regions."""
        self.dirty_regions.clear()
        self.dirty_state_keys.clear()
    
    def detect_state_changes(self, new_state: Dict[str, Any]) -> Set[str]:
        """Detect which keys have changed in the state.
        
        Args:
            new_state: New state to compare with current state
            
        Returns:
            Set[str]: Set of keys that changed
        """
        if not self.current_state:
            # First time, everything is dirty
            return set(new_state.keys())
        
        # Compare states and detect changes
        changed_keys = set()
        
        # Check for changed or added keys
        for key, value in new_state.items():
            if key not in self.current_state or self.current_state[key] != value:
                changed_keys.add(key)
        
        # Check for removed keys
        for key in self.current_state:
            if key not in new_state:
                changed_keys.add(key)
        
        return changed_keys
    
    def check_theme_changed(self) -> bool:
        """Check if the theme has changed.
        
        Returns:
            bool: True if the theme has changed, False otherwise
        """
        current_theme = get_theme()
        current_theme_id = id(current_theme)
        
        if current_theme_id != self.theme_version:
            self.theme = current_theme
            self.theme_version = current_theme_id
            return True
        
        return False
    
    def create_root_component(self, state: Dict[str, Any]) -> Container:
        """Create the root component for the current state.
        
        This method should be overridden by subclasses to create
        the appropriate component tree for the module.
        
        Args:
            state: Current module state
            
        Returns:
            Container: Root container component
        """
        # Create a default root component
        root = Container(
            id="root",
            width=self.width,
            height=self.height,
            color=self.theme.colors.get("background", (0, 0, 0)),
            children=[
                Text(
                    id="default_text",
                    text=f"Default renderer for {self.module_id}",
                    x=self.width/2,
                    y=self.height/2,
                    color=self.theme.colors.get("text", (255, 255, 255)),
                    align="center",
                    font_size=24
                )
            ]
        )
        
        return root
    
    def render_component(self, component: Component, parent_surface: pygame.Surface) -> List[pygame.Rect]:
        """Render a component and its children to the parent surface.
        
        Args:
            component: Component to render
            parent_surface: Surface to render onto
            
        Returns:
            List[pygame.Rect]: List of dirty rectangles
        """
        # Refactored implementation using helper functions
        if isinstance(component, Container):
            dirty_rects = self._draw_container(component, parent_surface, int(component.x) if hasattr(component, 'x') else 0, int(component.y) if hasattr(component, 'y') else 0, int(component.width) if hasattr(component, 'width') else parent_surface.get_width(), int(component.height) if hasattr(component, 'height') else parent_surface.get_height())
            if hasattr(component, 'children'):
                for child in component.children:
                    if getattr(component, 'clip_children', False):
                        child_surface = parent_surface.subsurface(pygame.Rect(int(component.x) if hasattr(component, 'x') else 0, int(component.y) if hasattr(component, 'y') else 0, int(component.width) if hasattr(component, 'width') else parent_surface.get_width(), int(component.height) if hasattr(component, 'height') else parent_surface.get_height()))
                        child_dirty = self.render_component(child, child_surface)
                        for r in child_dirty:
                            r.move_ip(int(component.x) if hasattr(component, 'x') else 0, int(component.y) if hasattr(component, 'y') else 0)
                        dirty_rects.extend(child_dirty)
                    else:
                        dirty_rects.extend(self.render_component(child, parent_surface))
        elif isinstance(component, Text):
            dirty_rects = self._draw_text(component, parent_surface, int(component.x) if hasattr(component, 'x') else 0, int(component.y) if hasattr(component, 'y') else 0, int(component.width) if hasattr(component, 'width') else parent_surface.get_width(), int(component.height) if hasattr(component, 'height') else parent_surface.get_height())
        elif isinstance(component, Rectangle):
            dirty_rects = self._draw_rectangle(component, parent_surface, int(component.x) if hasattr(component, 'x') else 0, int(component.y) if hasattr(component, 'y') else 0, int(component.width) if hasattr(component, 'width') else parent_surface.get_width(), int(component.height) if hasattr(component, 'height') else parent_surface.get_height())
        elif isinstance(component, Circle):
            dirty_rects = self._draw_circle(component, parent_surface, int(component.x) if hasattr(component, 'x') else 0, int(component.y) if hasattr(component, 'y') else 0, int(component.width) if hasattr(component, 'width') else parent_surface.get_width(), int(component.height) if hasattr(component, 'height') else parent_surface.get_height())
        elif isinstance(component, Line):
            dirty_rects = self._draw_line(component, parent_surface, int(component.start_x) if hasattr(component, 'start_x') else 0, int(component.start_y) if hasattr(component, 'start_y') else 0, int(component.end_x) if hasattr(component, 'end_x') else 0, int(component.end_y) if hasattr(component, 'end_y') else 0)
        elif isinstance(component, Image):
            dirty_rects = self._draw_image(component, parent_surface, int(component.x) if hasattr(component, 'x') else 0, int(component.y) if hasattr(component, 'y') else 0, int(component.width) if hasattr(component, 'width') else parent_surface.get_width(), int(component.height) if hasattr(component, 'height') else parent_surface.get_height())
        else:
            dirty_rects = [pygame.Rect(int(component.x) if hasattr(component, 'x') else 0, int(component.y) if hasattr(component, 'y') else 0, int(component.width) if hasattr(component, 'width') else parent_surface.get_width(), int(component.height) if hasattr(component, 'height') else parent_surface.get_height())]
        
        return dirty_rects
    
    def render(self, state: Dict[str, Any]) -> bool:
        """Render the current state to the screen.
        
        Args:
            state: Current module state
            
        Returns:
            bool: True if rendering was successful
        """
        # Record render start time
        start_time = time.time()
        
        # Update state
        self.last_state = self.current_state.copy()
        self.current_state = state.copy()
        
        # Check if theme has changed
        if self.check_theme_changed():
            self.needs_full_redraw = True
            # Clear font cache since font sizes might depend on theme
            self.font_cache.clear()
        
        # Detect state changes
        changed_keys = self.detect_state_changes(state)
        for key in changed_keys:
            self.mark_state_key_dirty(key)
        
        # Create root component
        root = self.create_root_component(state)
        
        # Check if we need a full redraw
        if self.needs_full_redraw:
            # Clear screen
            self.screen.fill(self.theme.colors.get("background", (0, 0, 0)))
            
            # Render entire component tree
            self.render_component(root, self.screen)
            
            # Clear dirty flags
            self.clear_dirty_regions()
            self.needs_full_redraw = False
        else:
            # Only render dirty regions
            for rect in self.dirty_regions:
                # Clear the dirty region
                bg_color = self.theme.colors.get("background", (0, 0, 0))
                pygame.draw.rect(self.screen, bg_color, rect)
            
            # Render component tree
            self.render_component(root, self.screen)
            
            # Debug: Draw dirty region rectangles
            if self.debug_mode and self.show_dirty_regions:
                for rect in self.dirty_regions:
                    pygame.draw.rect(self.screen, (255, 0, 0), rect, 1)
            
            # Clear dirty flags
            self.clear_dirty_regions()
        
        # Update performance metrics
        self.render_count += 1
        self.last_render_time = time.time() - start_time
        self.render_times.append(self.last_render_time)
        
        # Limit render_times list size
        if len(self.render_times) > 60:
            self.render_times.pop(0)
        
        return True
    
    def handle_event(self, event: pygame.event.Event) -> Optional[Dict[str, Any]]:
        """Handle a PyGame event.
        
        Args:
            event: PyGame event to handle
            
        Returns:
            Optional[Dict[str, Any]]: Event data if handled, None otherwise
        """
        # Default implementation returns None
        return None
    
    def get_render_stats(self) -> Dict[str, Any]:
        """Get rendering statistics.
        
        Returns:
            Dict[str, Any]: Dictionary of rendering statistics
        """
        avg_render_time = sum(self.render_times) / len(self.render_times) if self.render_times else 0
        
        return {
            'render_count': self.render_count,
            'last_render_time': self.last_render_time * 1000,  # ms
            'avg_render_time': avg_render_time * 1000,  # ms
            'component_pool_size': self.component_pool_size,
            'surface_cache_size': len(self.surface_cache),
        }
    
    def cleanup(self):
        """Clean up resources.
        
        This method releases all resources held by the renderer, including
        component caches, surface caches, font caches, and component pools.
        """
        # Clear caches
        self.component_cache.clear()
        self.surface_cache.clear()
        self.font_cache.clear()
        
        # Clear component pools
        for pool in self.component_pool.values():
            pool.clear()
        self.component_pool_size = 0
        
        logger.info(f"Base component renderer cleaned up for {self.module_id}")

    def _draw_container(self, component: Container, parent_surface: pygame.Surface, x: int, y: int, width: int, height: int) -> List[pygame.Rect]:
        dirty_rects = []
        if hasattr(component, 'color') and component.color is not None:
            if len(component.color) == 4:  # RGBA
                temp_surface = pygame.Surface((width, height), pygame.SRCALPHA)
                temp_surface.fill(component.color)
                parent_surface.blit(temp_surface, (x, y))
            else:
                pygame.draw.rect(parent_surface, component.color, pygame.Rect(x, y, width, height))
        if hasattr(component, 'border_width') and component.border_width and hasattr(component, 'border_color'):
            pygame.draw.rect(parent_surface, component.border_color, pygame.Rect(x, y, width, height), component.border_width)
        dirty_rects.append(pygame.Rect(x, y, width, height))
        return dirty_rects

    def _draw_text(self, component: Text, parent_surface: pygame.Surface, x: int, y: int, width: int, height: int) -> List[pygame.Rect]:
        dirty_rects = []
        font = self.get_font(component.font_size, getattr(component, 'bold', False))
        text_surface = font.render(str(component.text), True, component.color)
        text_rect = text_surface.get_rect()
        if hasattr(component, 'align'):
            if component.align == 'center':
                text_rect.center = (x, y)
            elif component.align == 'right':
                text_rect.right = x
                text_rect.centery = y
            else:
                text_rect.topleft = (x, y)
        else:
            text_rect.topleft = (x, y)
        parent_surface.blit(text_surface, text_rect)
        dirty_rects.append(text_rect)
        return dirty_rects

    def _draw_rectangle(self, component: Rectangle, parent_surface: pygame.Surface, x: int, y: int, width: int, height: int) -> List[pygame.Rect]:
        dirty_rects = []
        if len(component.color) == 4:
            temp_surface = pygame.Surface((width, height), pygame.SRCALPHA)
            temp_surface.fill(component.color)
            parent_surface.blit(temp_surface, (x, y))
        else:
            pygame.draw.rect(parent_surface, component.color, pygame.Rect(x, y, width, height))
        if getattr(component, 'border_width', 0) > 0 and hasattr(component, 'border_color'):
            pygame.draw.rect(parent_surface, component.border_color, pygame.Rect(x, y, width, height), component.border_width)
        dirty_rects.append(pygame.Rect(x, y, width, height))
        return dirty_rects

    def _draw_circle(self, component: Circle, parent_surface: pygame.Surface, x: int, y: int, width: int, height: int) -> List[pygame.Rect]:
        dirty_rects = []
        radius = int(component.radius)
        center = (x + width // 2, y + height // 2)
        if len(component.color) == 4:
            temp_surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(temp_surface, component.color, (radius, radius), radius)
            parent_surface.blit(temp_surface, (center[0] - radius, center[1] - radius))
        else:
            pygame.draw.circle(parent_surface, component.color, center, radius)
        if getattr(component, 'border_width', 0) > 0 and hasattr(component, 'border_color'):
            pygame.draw.circle(parent_surface, component.border_color, center, radius, component.border_width)
        circle_rect = pygame.Rect(center[0] - radius, center[1] - radius, radius * 2, radius * 2)
        dirty_rects.append(circle_rect)
        return dirty_rects

    def _draw_line(self, component: Line, parent_surface: pygame.Surface, x: int, y: int, width: int, height: int) -> List[pygame.Rect]:
        dirty_rects = []
        start_pos = (int(component.start_x), int(component.start_y))
        end_pos = (int(component.end_x), int(component.end_y))
        line_width = int(getattr(component, 'width', 1))
        pygame.draw.line(parent_surface, component.color, start_pos, end_pos, line_width)
        line_rect = pygame.Rect(min(start_pos[0], end_pos[0]), min(start_pos[1], end_pos[1]), abs(end_pos[0] - start_pos[0]) + line_width, abs(end_pos[1] - start_pos[1]) + line_width)
        dirty_rects.append(line_rect)
        return dirty_rects

    def _draw_image(self, component: Image, parent_surface: pygame.Surface, x: int, y: int, width: int, height: int) -> List[pygame.Rect]:
        dirty_rects = []
        image_path = component.src
        if image_path not in self.surface_cache:
            try:
                if image_path.startswith('data:'):
                    pass
                else:
                    image = pygame.image.load(image_path)
                    self.surface_cache[image_path] = image
            except Exception as e:
                placeholder = pygame.Surface((width, height))
                placeholder.fill((255, 0, 255))
                self.surface_cache[image_path] = placeholder
        image = self.surface_cache[image_path]
        if hasattr(component, 'width') and hasattr(component, 'height'):
            image = pygame.transform.scale(image, (width, height))
        parent_surface.blit(image, (x, y))
        dirty_rects.append(pygame.Rect(x, y, image.get_width(), image.get_height()))
        return dirty_rects