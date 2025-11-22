#!/usr/bin/env python3
"""
Simplified UI Component System for MetaMindIQTrain

This module provides a streamlined component architecture for building
consistent user interfaces across PyGame and web clients.

Key features:
1. Base UIComponent class for all UI elements
2. Consistent properties and styling system
3. Event handling with bubbling
4. Layout management helpers
5. Component registry for dynamic instantiation
"""

import pygame
import time
import math
import logging
from typing import Dict, List, Tuple, Any, Optional, Union, Callable
from pathlib import Path

# Try to import theme manager
try:
    from .theme_manager import ThemeManager
except ImportError:
    # For direct execution during development
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from core.theme_manager import ThemeManager

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class UIComponent:
    """Base class for all UI components."""
    
    def __init__(self, id=None, x=0, y=0, width=100, height=100, properties=None):
        """Initialize the component.
        
        Args:
            id: Unique identifier for the component
            x: X coordinate
            y: Y coordinate
            width: Width of the component
            height: Height of the component
            properties: Additional properties dictionary
        """
        self.id = id or f"component_{id(self)}"
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.properties = properties or {}
        
        # State tracking
        self.visible = True
        self.hover = False
        self.active = False
        self.disabled = False
        self.is_dirty = True  # Initially dirty to force first render
        
        # Parent-child relationships
        self.parent = None
        self.children = []
        
        # Styling information
        self.style = self.properties.get("style", {})
        
        # Caching
        self.cached_surface = None
        self.cached_hash = None
        self.last_update_time = time.time()
    
    def get_rect(self):
        """Get the pygame Rect for this component.
        
        Returns:
            pygame.Rect object
        """
        return pygame.Rect(self.x, self.y, self.width, self.height)
    
    def contains_point(self, point):
        """Check if the component contains a point.
        
        Args:
            point: (x, y) tuple
            
        Returns:
            True if the point is within this component
        """
        return self.get_rect().collidepoint(point)
    
    def add_child(self, child):
        """Add a child component.
        
        Args:
            child: Child component to add
            
        Returns:
            The added child component
        """
        child.parent = self
        self.children.append(child)
        self.mark_dirty()
        return child
    
    def remove_child(self, child):
        """Remove a child component.
        
        Args:
            child: Child component to remove
            
        Returns:
            True if the child was removed
        """
        if child in self.children:
            child.parent = None
            self.children.remove(child)
            self.mark_dirty()
            return True
        return False
    
    def clear_children(self):
        """Remove all children."""
        for child in list(self.children):
            child.parent = None
        self.children.clear()
        self.mark_dirty()
    
    def mark_dirty(self):
        """Mark this component as needing to be redrawn."""
        self.is_dirty = True
        self.cached_surface = None
        self.cached_hash = None
        if self.parent:
            self.parent.mark_dirty()
    
    def update(self, dt):
        """Update component state based on time delta.
        
        Args:
            dt: Time delta in seconds
        """
        # Update all children
        for child in self.children:
            child.update(dt)
        
        # Check if enough time has passed to allow another render
        if time.time() - self.last_update_time > 0.016:  # ~60fps
            self.is_dirty = True
            self.last_update_time = time.time()
    
    def handle_event(self, event):
        """Handle a pygame event.
        
        Args:
            event: pygame event object
            
        Returns:
            True if the event was handled
        """
        # Handle mouse movement for hover state
        if event.type == pygame.MOUSEMOTION:
            was_hover = self.hover
            self.hover = self.contains_point(event.pos)
            if was_hover != self.hover:
                self.mark_dirty()
                return True
        
        # Handle mouse button for active state
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.contains_point(event.pos):
                self.active = True
                self.mark_dirty()
                return True
        elif event.type == pygame.MOUSEBUTTONUP:
            was_active = self.active
            self.active = False
            if was_active and self.contains_point(event.pos):
                # This was a click
                self.on_click()
                self.mark_dirty()
                return True
            elif was_active:
                self.mark_dirty()
                return True
        
        # Bubble event to children in reverse order (top to bottom)
        for child in reversed(self.children):
            if child.visible and child.handle_event(event):
                return True
        
        return False
    
    def on_click(self):
        """Handle click event. Override in subclasses."""
        pass
    
    def render(self, surface, force_render=False):
        """Render the component to a surface.
        
        Args:
            surface: Target pygame surface
            force_render: Whether to force rendering even if not dirty
            
        Returns:
            List of dirty rects that were updated
        """
        if not self.visible:
            return []
        
        # Check if we need to redraw
        if not self.is_dirty and not force_render and self.cached_surface:
            # Just blit the cached surface
            surface.blit(self.cached_surface, (self.x, self.y))
            return [self.get_rect()]
        
        # Create a new surface for this component
        component_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        component_surface.fill((0, 0, 0, 0))  # Transparent
        
        # Draw this component
        self._draw_component(component_surface)
        
        # Draw all children
        dirty_rects = []
        for child in self.children:
            if child.visible:
                # Translate child coordinates to local space
                child_surface = pygame.Surface((child.width, child.height), pygame.SRCALPHA)
                child_surface.fill((0, 0, 0, 0))  # Transparent
                child_dirty = child.render(child_surface, force_render)
                if child_dirty:
                    component_surface.blit(child_surface, (child.x - self.x, child.y - self.y))
                    dirty_rects.extend(child_dirty)
        
        # Cache the surface
        self.cached_surface = component_surface.copy()
        self.is_dirty = False
        
        # Blit to the target surface
        surface.blit(component_surface, (self.x, self.y))
        
        return [self.get_rect()] + dirty_rects
    
    def _draw_component(self, surface):
        """Draw the component itself (not children).
        
        Args:
            surface: Surface to draw on
        """
        # Base implementation does nothing - override in subclasses
        pass
    
    def get_property(self, name, default=None):
        """Get a property value.
        
        Args:
            name: Property name
            default: Default value if property doesn't exist
            
        Returns:
            Property value or default
        """
        return self.properties.get(name, default)
    
    def set_property(self, name, value):
        """Set a property value.
        
        Args:
            name: Property name
            value: Property value
        """
        self.properties[name] = value
        self.mark_dirty()
    
    def get_absolute_position(self):
        """Get absolute position including parent offsets.
        
        Returns:
            (x, y) tuple of absolute position
        """
        if self.parent:
            parent_x, parent_y = self.parent.get_absolute_position()
            return (parent_x + self.x, parent_y + self.y)
        return (self.x, self.y)
    
    def get_style(self, key, default=None):
        """Get a style value.
        
        Args:
            key: Style key
            default: Default value if style doesn't exist
            
        Returns:
            Style value or default
        """
        return self.style.get(key, default)


class ContainerComponent(UIComponent):
    """Container for other components with layout management."""
    
    def __init__(self, id=None, x=0, y=0, width=100, height=100, properties=None):
        """Initialize the container.
        
        Args:
            id: Unique identifier for the component
            x: X coordinate
            y: Y coordinate
            width: Width of the component
            height: Height of the component
            properties: Additional properties dictionary
        """
        super().__init__(id, x, y, width, height, properties)
        
        # Layout properties
        self.layout = self.properties.get("layout", "flow")  # flow, grid
        self.layout_props = self.properties.get("layout_props", {})
        
        # Background and border
        self.bg_color = self.get_style("backgroundColor", ThemeManager.get_color("card_bg"))
        self.border_width = self.get_style("borderWidth", 0)
        self.border_color = self.get_style("borderColor", ThemeManager.get_color("border_color"))
        self.border_radius = self.get_style("borderRadius", 0)
    
    def _draw_component(self, surface):
        """Draw the container.
        
        Args:
            surface: Surface to draw on
        """
        # Draw background with rounded corners if needed
        if self.border_radius > 0:
            pygame.draw.rect(
                surface, 
                self.bg_color, 
                (0, 0, self.width, self.height),
                border_radius=self.border_radius
            )
            
            # Draw border if needed
            if self.border_width > 0:
                pygame.draw.rect(
                    surface, 
                    self.border_color, 
                    (0, 0, self.width, self.height),
                    width=self.border_width,
                    border_radius=self.border_radius
                )
        else:
            # Regular rectangle
            pygame.draw.rect(
                surface, 
                self.bg_color, 
                (0, 0, self.width, self.height)
            )
            
            # Draw border if needed
            if self.border_width > 0:
                pygame.draw.rect(
                    surface, 
                    self.border_color, 
                    (0, 0, self.width, self.height),
                    width=self.border_width
                )
    
    def layout_children(self):
        """Layout child components based on layout type."""
        if self.layout == "flow":
            self._flow_layout()
        elif self.layout == "grid":
            self._grid_layout()
        
        self.mark_dirty()
    
    def _flow_layout(self):
        """Arrange children in a flow layout."""
        margin = self.layout_props.get("margin", 5)
        padding = self.layout_props.get("padding", 10)
        direction = self.layout_props.get("direction", "horizontal")
        
        x, y = padding, padding
        max_height = 0
        max_width = 0
        
        for child in self.children:
            if not child.visible:
                continue
                
            if direction == "horizontal":
                # Check if we need to wrap to next row
                if x + child.width > self.width - padding:
                    x = padding
                    y += max_height + margin
                    max_height = 0
                
                # Position the child
                child.x = x
                child.y = y
                
                # Update position for next child
                x += child.width + margin
                max_height = max(max_height, child.height)
            else:  # vertical
                # Position the child
                child.x = x
                child.y = y
                
                # Update position for next child
                y += child.height + margin
                max_width = max(max_width, child.width)
    
    def _grid_layout(self):
        """Arrange children in a grid layout."""
        columns = self.layout_props.get("columns", 3)
        margin = self.layout_props.get("margin", 5)
        padding = self.layout_props.get("padding", 10)
        
        # Calculate available width and cell width
        available_width = self.width - (2 * padding) - (margin * (columns - 1))
        cell_width = available_width // columns
        
        row, col = 0, 0
        
        for child in self.children:
            if not child.visible:
                continue
                
            # Position the child
            child.x = padding + (col * (cell_width + margin))
            child.y = padding + (row * (child.height + margin))
            
            # Update for next child
            col += 1
            if col >= columns:
                col = 0
                row += 1
            
            # Optional: resize child to fit grid
            if self.layout_props.get("resize_children", False):
                child.width = cell_width


class TextComponent(UIComponent):
    """Text component for displaying text."""
    
    def __init__(self, id=None, x=0, y=0, width=100, height=40, text="Text", properties=None):
        """Initialize the text component.
        
        Args:
            id: Unique identifier for the component
            x: X coordinate
            y: Y coordinate
            width: Width of the component
            height: Height of the component
            text: Text to display
            properties: Additional properties dictionary
        """
        properties = properties or {}
        properties["text"] = text
        super().__init__(id, x, y, width, height, properties)
        
        # Initialize fonts if not provided
        if "font" not in self.properties:
            font_size = self.get_style("fontSize", ThemeManager.get_theme()["text_size"])
            try:
                self.properties["font"] = pygame.font.SysFont(
                    ThemeManager.get_theme()["font_family"], 
                    font_size
                )
            except:
                # Fallback to default pygame font
                self.properties["font"] = pygame.font.Font(None, font_size)
        
        # Text properties
        self.text = text
        self.font = self.properties["font"]
        self.color = self.get_style("color", ThemeManager.get_color("text_color"))
        self.bg_color = self.get_style("backgroundColor", None)
        self.align = self.get_style("textAlign", "left")  # left, center, right
    
    def _draw_component(self, surface):
        """Draw the text.
        
        Args:
            surface: Surface to draw on
        """
        # Draw background if specified
        if self.bg_color:
            pygame.draw.rect(
                surface, 
                self.bg_color, 
                (0, 0, self.width, self.height)
            )
        
        # Render text
        text_surface = self.font.render(self.text, True, self.color)
        
        # Position based on alignment
        text_rect = text_surface.get_rect()
        if self.align == "left":
            text_rect.left = 0
            text_rect.centery = self.height // 2
        elif self.align == "center":
            text_rect.center = (self.width // 2, self.height // 2)
        else:  # right
            text_rect.right = self.width
            text_rect.centery = self.height // 2
        
        # Draw text
        surface.blit(text_surface, text_rect)
    
    def set_text(self, text):
        """Set the text.
        
        Args:
            text: New text
        """
        if self.text != text:
            self.text = text
            self.mark_dirty()


class ButtonComponent(ContainerComponent):
    """Interactive button component."""
    
    def __init__(self, id=None, x=0, y=0, width=120, height=40, text="Button", properties=None):
        """Initialize the button.
        
        Args:
            id: Unique identifier for the component
            x: X coordinate
            y: Y coordinate
            width: Width of the component
            height: Height of the component
            text: Button text
            properties: Additional properties dictionary
        """
        properties = properties or {}
        super().__init__(id, x, y, width, height, properties)
        
        # Button specific properties
        self.bg_color = self.get_style("backgroundColor", ThemeManager.get_color("button_bg"))
        self.bg_hover_color = self.get_style("hoverBackgroundColor", ThemeManager.get_color("button_hover"))
        self.bg_active_color = self.get_style("activeBackgroundColor", ThemeManager.get_color("button_hover"))
        self.border_radius = self.get_style("borderRadius", ThemeManager.get_theme()["border_radius"])
        
        # Add text component as child
        self.text_component = TextComponent(
            id=f"{self.id}_text",
            x=0,
            y=0,
            width=width,
            height=height,
            text=text,
            properties={
                "style": {
                    "color": self.get_style("color", ThemeManager.get_color("text_color")),
                    "textAlign": "center"
                }
            }
        )
        self.add_child(self.text_component)
        
        # Click handler
        self.on_click_handler = properties.get("on_click", None)
    
    def _draw_component(self, surface):
        """Draw the button.
        
        Args:
            surface: Surface to draw on
        """
        # Determine color based on state
        color = self.bg_color
        if self.active:
            color = self.bg_active_color
        elif self.hover:
            color = self.bg_hover_color
        
        # Draw rounded rectangle
        pygame.draw.rect(
            surface, 
            color, 
            (0, 0, self.width, self.height),
            border_radius=self.border_radius
        )
        
        # Draw border if needed
        if self.border_width > 0:
            pygame.draw.rect(
                surface, 
                self.border_color, 
                (0, 0, self.width, self.height),
                width=self.border_width,
                border_radius=self.border_radius
            )
    
    def on_click(self):
        """Handle click event."""
        if self.on_click_handler:
            self.on_click_handler(self)
    
    def set_text(self, text):
        """Set the button text.
        
        Args:
            text: New text
        """
        self.text_component.set_text(text)


class ComponentRegistry:
    """Registry for component types."""
    
    # Component mapping
    _components = {}
    
    @classmethod
    def register(cls, component_type, component_class):
        """Register a component type.
        
        Args:
            component_type: Component type name
            component_class: Component class
        """
        cls._components[component_type] = component_class
    
    @classmethod
    def create(cls, component_type, **kwargs):
        """Create a component by type.
        
        Args:
            component_type: Component type name
            **kwargs: Arguments to pass to the component constructor
            
        Returns:
            New component instance
        """
        if component_type not in cls._components:
            raise ValueError(f"Unknown component type: {component_type}")
        return cls._components[component_type](**kwargs)


# Register built-in components
ComponentRegistry.register("container", ContainerComponent)
ComponentRegistry.register("text", TextComponent)
ComponentRegistry.register("button", ButtonComponent)


class LayoutManager:
    """Helper for calculating responsive layouts."""
    
    @staticmethod
    def calculate_grid_positions(num_items, container_width, container_height, 
                                min_width=280, aspect_ratio=1.0, gap=20, padding=20):
        """Calculate positions for items in a responsive grid.
        
        Args:
            num_items: Number of items in the grid
            container_width: Width of the container
            container_height: Height of the container
            min_width: Minimum width for each item
            aspect_ratio: Width/height ratio for items
            gap: Gap between items
            padding: Padding around the grid
            
        Returns:
            List of (x, y, width, height) tuples for each item
        """
        # Calculate available width
        available_width = container_width - (2 * padding)
        
        # Calculate maximum number of columns based on min_width
        max_columns = max(1, int(available_width / (min_width + gap)))
        
        # Limit columns based on number of items
        columns = min(max_columns, num_items)
        
        # Calculate rows needed
        rows = math.ceil(num_items / columns)
        
        # Calculate actual item width
        item_width = (available_width - (columns - 1) * gap) / columns
        item_height = item_width / aspect_ratio
        
        # Calculate total grid height
        grid_height = rows * item_height + (rows - 1) * gap
        
        # Center grid vertically if container is taller
        start_y = padding
        if container_height > grid_height + (2 * padding):
            start_y = (container_height - grid_height) / 2
        
        # Calculate positions for each item
        positions = []
        for i in range(num_items):
            row = i // columns
            col = i % columns
            
            x = padding + col * (item_width + gap)
            y = start_y + row * (item_height + gap)
            
            positions.append((x, y, item_width, item_height))
        
        return positions


def create_ui_hierarchy(components_data, parent=None):
    """Create a UI hierarchy from component data.
    
    Args:
        components_data: List of component data dictionaries
        parent: Optional parent component
        
    Returns:
        List of created components
    """
    created_components = []
    
    for data in components_data:
        component_type = data.get("type", "container")
        properties = data.get("properties", {})
        
        # Create component
        component = ComponentRegistry.create(
            component_type,
            id=data.get("id"),
            x=data.get("x", 0),
            y=data.get("y", 0),
            width=data.get("width", 100),
            height=data.get("height", 100),
            properties=properties
        )
        
        # Add to parent if provided
        if parent:
            parent.add_child(component)
        
        # Process children
        if "children" in data and data["children"]:
            create_ui_hierarchy(data["children"], component)
        
        created_components.append(component)
    
    return created_components 