#!/usr/bin/env python3
"""
Component system for MetaMindIQTrain

This module provides a unified component system for building UIs across different
client implementations (pygame, web, terminal, etc).

Optimizations:
- Component pooling to reduce object creation/destruction overhead
- Automatic type conversion for consistent serialization
- Serialization/deserialization caching for frequently used components
- Factory methods for common UI elements
"""

import time
import logging
import json
import uuid
from typing import Dict, List, Any, Tuple, Optional, Union, Set

logger = logging.getLogger(__name__)

class ComponentPool:
    """Object pool for efficient component reuse."""
    
    def __init__(self, max_size=1000):
        """Initialize the component pool.
        
        Args:
            max_size: Maximum number of pooled components
        """
        self.pool = {}
        self.max_size = max_size
        self.stats = {
            'created': 0,
            'reused': 0,
            'returned': 0
        }
    
    def get(self, component_type):
        """Get a component from the pool.
        
        Args:
            component_type: Type of component to get
            
        Returns:
            Component of the requested type
        """
        if component_type not in self.pool or not self.pool[component_type]:
            # Create new component
            self.stats['created'] += 1
            return Component(component_type)
        
        # Reuse existing component
        self.stats['reused'] += 1
        return self.pool[component_type].pop()
    
    def release(self, component):
        """Return a component to the pool.
        
        Args:
            component: Component to return to pool
        """
        component_type = component.type
        
        # Reset the component for reuse
        component.reset()
        
        # Initialize pool for this type if needed
        if component_type not in self.pool:
            self.pool[component_type] = []
            
        # Add to pool if not full
        if len(self.pool[component_type]) < self.max_size:
            self.pool[component_type].append(component)
            self.stats['returned'] += 1
    
    def clear(self):
        """Clear the pool."""
        self.pool.clear()
        self.stats = {
            'created': 0,
            'reused': 0,
            'returned': 0
        }
    
    def get_stats(self):
        """Get pool statistics.
        
        Returns:
            Dictionary with pool statistics
        """
        total = self.stats['created']
        reuse_rate = self.stats['reused'] / total if total > 0 else 0
        return {
            'size': sum(len(items) for items in self.pool.values()),
            'max_size': self.max_size,
            'created': self.stats['created'],
            'reused': self.stats['reused'],
            'returned': self.stats['returned'],
            'reuse_rate': reuse_rate
        }

# Create global component pool
_component_pool = ComponentPool()

def reset_component_stats():
    """Reset component pool statistics."""
    _component_pool.stats = {
        'created': 0,
        'reused': 0,
        'returned': 0
    }

def get_component_stats():
    """Get component pool statistics.
    
    Returns:
        Dictionary with pool statistics
    """
    return _component_pool.get_stats()

class Component:
    """Base component class for UI elements."""
    
    # Cache for serialized components
    _serialization_cache = {}
    _cache_hits = 0
    _cache_misses = 0
    
    def __init__(self, component_type):
        """Initialize the component.
        
        Args:
            component_type: Type of component
        """
        self.id = str(uuid.uuid4())
        self.type = component_type
        self.properties = {}
        self.position = (0, 0)
        self.created_at = time.time()
        self.parent = None
        self.children = []
        
        # Track whether component has changed since last serialization
        self._has_changed = True
        self._cached_dict = None
    
    def __del__(self):
        """Return component to pool when deleted."""
        try:
            _component_pool.release(self)
        except:
            pass
    
    def reset(self):
        """Reset the component for reuse."""
        self.id = str(uuid.uuid4())
        self.properties = {}
        self.position = (0, 0)
        self.created_at = time.time()
        self.parent = None
        self.children = []
        self._has_changed = True
        self._cached_dict = None
    
    def set_property(self, name, value):
        """Set a component property.
        
        Args:
            name: Property name
            value: Property value
            
        Returns:
            Self for method chaining
        """
        self.properties[name] = value
        self._has_changed = True
        return self
    
    def set_position(self, x, y):
        """Set component position.
        
        Args:
            x: X coordinate
            y: Y coordinate
            
        Returns:
            Self for method chaining
        """
        self.position = (x, y)
        self._has_changed = True
        return self
    
    def add_child(self, child):
        """Add a child component.
        
        Args:
            child: Child component
            
        Returns:
            Self for method chaining
        """
        self.children.append(child)
        child.parent = self
        self._has_changed = True
        return self
    
    def to_dict(self):
        """Convert component to dictionary.
        
        Returns:
            Dictionary representation of component
        """
        # Return cached version if available and unchanged
        if not self._has_changed and self._cached_dict:
            return self._cached_dict
        
        # Convert properties to JSON-serializable types
        serialized_props = self._convert_properties_to_json(self.properties)
        
        # Create base component dict
        result = {
            'id': self.id,
            'type': self.type,
            'position': self.position,
            'properties': serialized_props,
            'created_at': self.created_at
        }
        
        # Add children if any
        if self.children:
            result['children'] = [child.to_dict() for child in self.children]
        
        # Cache result
        self._cached_dict = result
        self._has_changed = False
        
        return result
    
    def _convert_properties_to_json(self, props):
        """Convert properties to JSON-serializable types.
        
        Args:
            props: Properties dictionary
            
        Returns:
            Dictionary with JSON-serializable values
        """
        result = {}
        
        for key, value in props.items():
            if isinstance(value, tuple):
                # Convert tuples to lists
                result[key] = list(value)
            elif isinstance(value, (int, float, str, bool, type(None))):
                # Basic types can be used as-is
                result[key] = value
            elif isinstance(value, list):
                # Process list items
                result[key] = [
                    self._convert_value_to_json(item) for item in value
                ]
            elif isinstance(value, dict):
                # Process nested dictionaries
                result[key] = self._convert_properties_to_json(value)
            else:
                # Convert other types to string
                result[key] = str(value)
        
        return result
    
    def _convert_value_to_json(self, value):
        """Convert a single value to JSON-serializable type.
        
        Args:
            value: Value to convert
            
        Returns:
            JSON-serializable value
        """
        if isinstance(value, tuple):
            return list(value)
        elif isinstance(value, (int, float, str, bool, type(None))):
            return value
        elif isinstance(value, list):
            return [self._convert_value_to_json(item) for item in value]
        elif isinstance(value, dict):
            return self._convert_properties_to_json(value)
        else:
            return str(value)
    
    @classmethod
    def from_dict(cls, data):
        """Create component from dictionary.
        
        Args:
            data: Dictionary representation of component
            
        Returns:
            Component instance
        """
        # Check if component already exists in cache
        component_id = data.get('id')
        cache_key = (component_id, str(data))
        
        if cache_key in cls._serialization_cache:
            cls._cache_hits += 1
            return cls._serialization_cache[cache_key]
        
        cls._cache_misses += 1
        
        # Get component from pool
        component = _component_pool.get(data.get('type', 'unknown'))
        
        # Set properties
        component.id = data.get('id', str(uuid.uuid4()))
        component.type = data.get('type', 'unknown')
        
        # Set position
        pos = data.get('position', (0, 0))
        component.position = tuple(pos) if isinstance(pos, list) else pos
        
        # Set creation time
        component.created_at = data.get('created_at', time.time())
        
        # Set properties
        component.properties = data.get('properties', {})
        
        # Add children if any
        if 'children' in data:
            for child_data in data['children']:
                child = cls.from_dict(child_data)
                component.add_child(child)
        
        # Cache component
        cls._serialization_cache[cache_key] = component
        
        # Clean cache if it gets too large
        if len(cls._serialization_cache) > 1000:
            # Remove oldest entries
            keys = list(cls._serialization_cache.keys())[:100]
            for key in keys:
                del cls._serialization_cache[key]
        
        return component

class UI:
    """User interface container for collections of components."""
    
    def __init__(self):
        """Initialize the UI."""
        self.components = []
        self.component_factory = ComponentFactory()
    
    def add_component(self, component):
        """Add a component to the UI.
        
        Args:
            component: Component to add
            
        Returns:
            Self for method chaining
        """
        self.components.append(component)
        return self
    
    def clear(self):
        """Clear all components."""
        self.components = []
    
    def to_dict(self):
        """Convert UI to dictionary.
        
        Returns:
            Dictionary representation of UI
        """
        return {
            'components': [component.to_dict() for component in self.components]
        }
    
    # Factory methods for creating components
    
    def text(self, text, position, font_size=20, color=(255, 255, 255), align="left"):
        """Create a text component.
        
        Args:
            text: Text content
            position: Position (x, y)
            font_size: Font size
            color: Text color
            align: Text alignment
            
        Returns:
            Text component
        """
        return self.component_factory.create_text(text, position, font_size, color, align)
    
    def rectangle(self, position, size, color=(100, 100, 100), border_width=0, 
                 border_color=(0, 0, 0), border_radius=0):
        """Create a rectangle component.
        
        Args:
            position: Position (x, y)
            size: Size (width, height)
            color: Fill color
            border_width: Border width
            border_color: Border color
            border_radius: Border radius
            
        Returns:
            Rectangle component
        """
        return self.component_factory.create_rectangle(
            position, size, color, border_width, border_color, border_radius
        )
    
    def circle(self, center, radius, color=(100, 100, 100), width=0):
        """Create a circle component.
        
        Args:
            center: Center position (x, y)
            radius: Circle radius
            color: Fill color
            width: Line width (0 for filled)
            
        Returns:
            Circle component
        """
        return self.component_factory.create_circle(center, radius, color, width)
    
    def image(self, path, position, size=None):
        """Create an image component.
        
        Args:
            path: Image path
            position: Position (x, y)
            size: Optional size (width, height)
            
        Returns:
            Image component
        """
        return self.component_factory.create_image(path, position, size)
    
    def button(self, text, position, size, color=(100, 100, 100), text_color=(255, 255, 255),
              border_radius=0, border_width=0, border_color=(0, 0, 0)):
        """Create a button component.
        
        Args:
            text: Button text
            position: Position (x, y)
            size: Size (width, height)
            color: Button color
            text_color: Text color
            border_radius: Border radius
            border_width: Border width
            border_color: Border color
            
        Returns:
            Button component
        """
        return self.component_factory.create_button(
            text, position, size, color, text_color, border_radius, border_width, border_color
        )
    
    def grid(self, position, rows, cols, cell_size, line_color=(100, 100, 100), line_width=1):
        """Create a grid component.
        
        Args:
            position: Position (x, y)
            rows: Number of rows
            cols: Number of columns
            cell_size: Size of each cell
            line_color: Line color
            line_width: Line width
            
        Returns:
            Grid component
        """
        return self.component_factory.create_grid(
            position, rows, cols, cell_size, line_color, line_width
        )
    
    def container(self, position, size, color=(0, 0, 0, 0), border_width=0, 
                 border_color=(0, 0, 0), border_radius=0):
        """Create a container component.
        
        Args:
            position: Position (x, y)
            size: Size (width, height)
            color: Background color
            border_width: Border width
            border_color: Border color
            border_radius: Border radius
            
        Returns:
            Container component
        """
        return self.component_factory.create_container(
            position, size, color, border_width, border_color, border_radius
        )
    
    def progress(self, position, size, value, color=(0, 255, 0), 
                background_color=(50, 50, 50), border_radius=0):
        """Create a progress bar component.
        
        Args:
            position: Position (x, y)
            size: Size (width, height)
            value: Progress value (0.0 - 1.0)
            color: Progress bar color
            background_color: Background color
            border_radius: Border radius
            
        Returns:
            Progress bar component
        """
        return self.component_factory.create_progress(
            position, size, value, color, background_color, border_radius
        )
    
    def timer(self, position, size, duration, elapsed, color=(0, 255, 0), 
             background_color=(50, 50, 50), border_radius=0):
        """Create a timer component.
        
        Args:
            position: Position (x, y)
            size: Size (width, height)
            duration: Timer duration in seconds
            elapsed: Elapsed time in seconds
            color: Timer color
            background_color: Background color
            border_radius: Border radius
            
        Returns:
            Timer component
        """
        return self.component_factory.create_timer(
            position, size, duration, elapsed, color, background_color, border_radius
        )
    
    def shape(self, position, points, color=(100, 100, 100), width=0):
        """Create a shape component.
        
        Args:
            position: Position (x, y)
            points: List of points
            color: Fill color
            width: Line width (0 for filled)
            
        Returns:
            Shape component
        """
        return self.component_factory.create_shape(position, points, color, width)
    
    def symbol(self, symbol, position, font_size=30, color=(255, 255, 255)):
        """Create a symbol component.
        
        Args:
            symbol: Symbol character
            position: Position (x, y)
            font_size: Font size
            color: Symbol color
            
        Returns:
            Symbol component
        """
        return self.component_factory.create_symbol(symbol, position, font_size, color)

class ComponentFactory:
    """Factory class for creating UI components."""
    
    def create_text(self, text, position, font_size=20, color=(255, 255, 255), align="left"):
        """Create a text component.
        
        Args:
            text: Text content
            position: (x, y) position
            font_size: Font size in pixels
            color: Text color
            align: Alignment (left, center, right)
            
        Returns:
            Text component
        """
        component = _component_pool.get("text")
        component.set_position(*position)
        component.set_property("text", text)
        component.set_property("fontSize", font_size)
        component.set_property("color", color)
        component.set_property("align", align)
        return component
    
    def create_rectangle(self, position, size, color=(100, 100, 100), border_width=0, 
                    border_color=(0, 0, 0), border_radius=0):
        """Create a rectangle component.
        
        Args:
            position: (x, y) position
            size: (width, height) size
            color: Fill color
            border_width: Border width in pixels
            border_color: Border color
            border_radius: Border radius in pixels
            
        Returns:
            Rectangle component
        """
        component = _component_pool.get("rectangle")
        component.set_position(*position)
        component.set_property("width", size[0])
        component.set_property("height", size[1])
        component.set_property("backgroundColor", color)
        component.set_property("borderWidth", border_width)
        component.set_property("borderColor", border_color)
        component.set_property("borderRadius", border_radius)
        return component
    
    def create_circle(self, center, radius, color=(100, 100, 100), width=0):
        """Create a circle component.
        
        Args:
            center: (x, y) center position
            radius: Circle radius
            color: Fill color
            width: Line width (0 = filled)
            
        Returns:
            Circle component
        """
        component = _component_pool.get("circle")
        component.set_position(*center)
        component.set_property("radius", radius)
        component.set_property("backgroundColor", color)
        component.set_property("borderWidth", width)
        return component
    
    def create_image(self, path, position, size=None):
        """Create an image component.
        
        Args:
            path: Image file path
            position: (x, y) position
            size: (width, height) size or None for original size
            
        Returns:
            Image component
        """
        component = _component_pool.get("image")
        component.set_position(*position)
        component.set_property("src", path)
        if size:
            component.set_property("width", size[0])
            component.set_property("height", size[1])
        return component
    
    def create_button(self, text, position, size, color=(100, 100, 100), text_color=(255, 255, 255),
                 border_radius=0, border_width=0, border_color=(0, 0, 0)):
        """Create a button component.
        
        Args:
            text: Button text
            position: (x, y) position
            size: (width, height) size
            color: Background color
            text_color: Text color
            border_radius: Border radius in pixels
            border_width: Border width in pixels
            border_color: Border color
            
        Returns:
            Button component
        """
        component = _component_pool.get("button")
        component.set_position(*position)
        component.set_property("text", text)
        component.set_property("width", size[0])
        component.set_property("height", size[1])
        component.set_property("backgroundColor", color)
        component.set_property("color", text_color)
        component.set_property("borderRadius", border_radius)
        component.set_property("borderWidth", border_width)
        component.set_property("borderColor", border_color)
        return component
    
    def create_grid(self, position, rows, cols, cell_size, line_color=(100, 100, 100), line_width=1):
        """Create a grid component.
        
        Args:
            position: (x, y) position
            rows: Number of rows
            cols: Number of columns
            cell_size: Cell size in pixels
            line_color: Line color
            line_width: Line width in pixels
            
        Returns:
            Grid component
        """
        component = _component_pool.get("grid")
        component.set_position(*position)
        component.set_property("rows", rows)
        component.set_property("cols", cols)
        component.set_property("cellSize", cell_size)
        component.set_property("borderColor", line_color)
        component.set_property("borderWidth", line_width)
        return component
    
    def create_container(self, position, size, color=(0, 0, 0, 0), border_width=0, 
                    border_color=(0, 0, 0), border_radius=0):
        """Create a container component.
        
        Args:
            position: (x, y) position
            size: (width, height) size
            color: Background color
            border_width: Border width in pixels
            border_color: Border color
            border_radius: Border radius in pixels
            
        Returns:
            Container component
        """
        component = _component_pool.get("container")
        component.set_position(*position)
        component.set_property("width", size[0])
        component.set_property("height", size[1])
        component.set_property("backgroundColor", color)
        component.set_property("borderWidth", border_width)
        component.set_property("borderColor", border_color)
        component.set_property("borderRadius", border_radius)
        return component
    
    def create_progress(self, position, size, value, color=(0, 255, 0), 
                   background_color=(50, 50, 50), border_radius=0):
        """Create a progress bar component.
        
        Args:
            position: (x, y) position
            size: (width, height) size
            value: Progress value (0.0-1.0)
            color: Fill color
            background_color: Background color
            border_radius: Border radius in pixels
            
        Returns:
            Progress bar component
        """
        component = _component_pool.get("progress")
        component.set_position(*position)
        component.set_property("width", size[0])
        component.set_property("height", size[1])
        component.set_property("value", value)
        component.set_property("fillColor", color)
        component.set_property("backgroundColor", background_color)
        component.set_property("borderRadius", border_radius)
        return component
    
    def create_timer(self, position, size, duration, elapsed, color=(0, 255, 0), 
                background_color=(50, 50, 50), border_radius=0):
        """Create a timer component.
        
        Args:
            position: (x, y) position
            size: (width, height) size
            duration: Timer duration in seconds
            elapsed: Elapsed time in seconds
            color: Fill color
            background_color: Background color
            border_radius: Border radius in pixels
            
        Returns:
            Timer component
        """
        component = _component_pool.get("timer")
        component.set_position(*position)
        component.set_property("width", size[0])
        component.set_property("height", size[1])
        component.set_property("duration", duration)
        component.set_property("elapsed", elapsed)
        component.set_property("fillColor", color)
        component.set_property("backgroundColor", background_color)
        component.set_property("borderRadius", border_radius)
        return component
    
    def create_shape(self, position, points, color=(100, 100, 100), width=0):
        """Create a shape component.
        
        Args:
            position: (x, y) position
            points: List of (x, y) points
            color: Fill color
            width: Line width (0 = filled)
            
        Returns:
            Shape component
        """
        component = _component_pool.get("shape")
        component.set_position(*position)
        component.set_property("points", points)
        component.set_property("color", color)
        component.set_property("width", width)
        return component
    
    def create_symbol(self, symbol, position, font_size=30, color=(255, 255, 255)):
        """Create a symbol component.
        
        Args:
            symbol: Symbol character
            position: (x, y) position
            font_size: Font size in pixels
            color: Symbol color
            
        Returns:
            Symbol component
        """
        component = _component_pool.get("symbol")
        component.set_position(*position)
        component.set_property("symbol", symbol)
        component.set_property("fontSize", font_size)
        component.set_property("color", color)
        return component

class ThemeAwareComponentFactory:
    """Theme-aware factory for creating styled UI components.
    
    This factory uses the theme system to apply consistent styling
    to UI components based on their type, variant, and state.
    """
    
    def __init__(self, theme_provider=None):
        """Initialize the theme-aware component factory.
        
        Args:
            theme_provider: Optional theme provider instance
        """
        # Import theme only when needed to avoid circular imports
        from .theme import ThemeProvider, get_theme
        
        self.theme_provider = theme_provider or ThemeProvider(get_theme())
        self.base_factory = ComponentFactory()
    
    def create_text(self, text, position, variant=None, state=None, **kwargs):
        """Create a themed text component.
        
        Args:
            text: Text content
            position: (x, y) position
            variant: Optional variant name (title, subtitle, caption, label)
            state: Optional state name (disabled, highlighted, error)
            **kwargs: Additional style overrides
            
        Returns:
            Text component with themed styling
        """
        # Get style from theme
        style = self.theme_provider.get_style("text", variant, state, **kwargs)
        
        # Create component with base factory
        component = self.base_factory.create_text(
            text, 
            position, 
            font_size=style.get("fontSize", 20),
            color=style.get("color", (255, 255, 255)),
            align=style.get("textAlign", "left")
        )
        
        # Apply additional style properties
        if "fontWeight" in style:
            component.set_property("fontWeight", style["fontWeight"])
            
        if "lineHeight" in style:
            component.set_property("lineHeight", style["lineHeight"])
            
        if "opacity" in style:
            component.set_property("opacity", style["opacity"])
        
        return component
    
    def create_rectangle(self, position, size, variant=None, state=None, **kwargs):
        """Create a themed rectangle component.
        
        Args:
            position: (x, y) position
            size: (width, height) size
            variant: Optional variant name (card, panel)
            state: Optional state name (disabled, highlighted)
            **kwargs: Additional style overrides
            
        Returns:
            Rectangle component with themed styling
        """
        # Get style from theme
        style = self.theme_provider.get_style("rect", variant, state, **kwargs)
        
        # Create component with base factory
        component = self.base_factory.create_rectangle(
            position, 
            size, 
            color=style.get("backgroundColor", (100, 100, 100)),
            border_width=style.get("borderWidth", 0),
            border_color=style.get("borderColor", (0, 0, 0)),
            border_radius=style.get("borderRadius", 0)
        )
        
        # Apply additional style properties
        if "opacity" in style:
            component.set_property("opacity", style["opacity"])
        
        return component
    
    def create_circle(self, center, radius=None, variant=None, state=None, **kwargs):
        """Create a themed circle component.
        
        Args:
            center: (x, y) center position
            radius: Circle radius (overrides theme size if provided)
            variant: Optional variant name (indicator, status)
            state: Optional state name (active, success, error)
            **kwargs: Additional style overrides
            
        Returns:
            Circle component with themed styling
        """
        # Get style from theme
        style = self.theme_provider.get_style("circle", variant, state, **kwargs)
        
        # Use provided radius or get from style
        if radius is None and "size" in style:
            radius = style["size"] // 2
        elif radius is None:
            radius = 10  # Default fallback
        
        # Create component with base factory
        component = self.base_factory.create_circle(
            center, 
            radius, 
            color=style.get("backgroundColor", (100, 100, 100)),
            width=style.get("borderWidth", 0)
        )
        
        # Apply additional style properties
        if "borderColor" in style:
            component.set_property("borderColor", style["borderColor"])
            
        if "opacity" in style:
            component.set_property("opacity", style["opacity"])
        
        return component
    
    def create_button(self, text, position, size, variant=None, state=None, **kwargs):
        """Create a themed button component.
        
        Args:
            text: Button text
            position: (x, y) position
            size: (width, height) size
            variant: Optional variant name (primary, secondary, outline, text)
            state: Optional state name (hover, active, disabled)
            **kwargs: Additional style overrides
            
        Returns:
            Button component with themed styling
        """
        # Get style from theme
        style = self.theme_provider.get_style("button", variant, state, **kwargs)
        
        # Create component with base factory
        component = self.base_factory.create_button(
            text, 
            position, 
            size, 
            color=style.get("backgroundColor", (100, 100, 100)),
            text_color=style.get("color", (255, 255, 255)),
            border_radius=style.get("borderRadius", 0),
            border_width=style.get("borderWidth", 0),
            border_color=style.get("borderColor", (0, 0, 0))
        )
        
        # Apply additional style properties
        if "fontSize" in style:
            component.set_property("fontSize", style["fontSize"])
            
        if "fontWeight" in style:
            component.set_property("fontWeight", style["fontWeight"])
            
        if "opacity" in style:
            component.set_property("opacity", style["opacity"])
            
        if "padding" in style:
            component.set_property("padding", style["padding"])
        
        return component
    
    def create_grid(self, position, rows, cols, cell_size=None, variant=None, **kwargs):
        """Create a themed grid component.
        
        Args:
            position: (x, y) position
            rows: Number of rows
            cols: Number of columns
            cell_size: Cell size in pixels (overrides theme if provided)
            variant: Optional variant name (matrix, game_board)
            **kwargs: Additional style overrides
            
        Returns:
            Grid component with themed styling
        """
        # Get style from theme
        style = self.theme_provider.get_style("grid", variant, None, **kwargs)
        
        # Use provided cell_size or get from style
        if cell_size is None and "cellSize" in style:
            cell_size = style["cellSize"]
        elif cell_size is None:
            cell_size = 30  # Default fallback
        
        # Create component with base factory
        component = self.base_factory.create_grid(
            position, 
            rows, 
            cols, 
            cell_size, 
            line_color=style.get("borderColor", (100, 100, 100)),
            line_width=style.get("borderWidth", 1)
        )
        
        # Apply additional style properties
        if "backgroundColor" in style:
            component.set_property("backgroundColor", style["backgroundColor"])
            
        if "cellPadding" in style:
            component.set_property("cellPadding", style["cellPadding"])
            
        if "gapSize" in style:
            component.set_property("gapSize", style["gapSize"])
        
        return component
    
    def create_container(self, position, size, variant=None, **kwargs):
        """Create a themed container component.
        
        Args:
            position: (x, y) position
            size: (width, height) size
            variant: Optional variant name (modal, panel)
            **kwargs: Additional style overrides
            
        Returns:
            Container component with themed styling
        """
        # Get style from theme
        style = self.theme_provider.get_style("container", variant, None, **kwargs)
        
        # Determine background color, handle None/transparent case
        bg_color = style.get("backgroundColor", (0, 0, 0, 0))
        
        # Create component with base factory
        component = self.base_factory.create_container(
            position, 
            size, 
            color=bg_color,
            border_width=style.get("borderWidth", 0),
            border_color=style.get("borderColor", (0, 0, 0)),
            border_radius=style.get("borderRadius", 0)
        )
        
        # Apply additional style properties
        if "padding" in style:
            component.set_property("padding", style["padding"])
        
        return component
    
    def create_progress(self, position, size, value, variant=None, **kwargs):
        """Create a themed progress bar component.
        
        Args:
            position: (x, y) position
            size: (width, height) size or None to use theme height
            value: Progress value (0.0-1.0)
            variant: Optional variant name (success, warning, error)
            **kwargs: Additional style overrides
            
        Returns:
            Progress bar component with themed styling
        """
        # Get style from theme
        style = self.theme_provider.get_style("progress", variant, None, **kwargs)
        
        # Use provided height or get from style
        if size[1] is None and "height" in style:
            size = (size[0], style["height"])
        elif size[1] is None:
            size = (size[0], 10)  # Default fallback
        
        # Create component with base factory
        component = self.base_factory.create_progress(
            position, 
            size, 
            value, 
            color=style.get("fillColor", (0, 255, 0)),
            background_color=style.get("backgroundColor", (50, 50, 50)),
            border_radius=style.get("borderRadius", 0)
        )
        
        return component
    
    def create_symbol_cell(self, symbol, position, size, state=None, **kwargs):
        """Create a themed symbol cell component.
        
        Args:
            symbol: Symbol character
            position: (x, y) position
            size: (width, height) size
            state: Optional state name (highlighted, active, correct, incorrect)
            **kwargs: Additional style overrides
            
        Returns:
            Styled symbol cell component (actually a container with a symbol)
        """
        # Get style from theme
        style = self.theme_provider.get_style("symbol_cell", None, state, **kwargs)
        
        # Create container component
        container = self.base_factory.create_container(
            position,
            size,
            color=style.get("backgroundColor", (40, 44, 52)),
            border_width=style.get("borderWidth", 1),
            border_color=style.get("borderColor", (60, 70, 80)),
            border_radius=style.get("borderRadius", 4)
        )
        
        # Create symbol component
        symbol_comp = self.base_factory.create_symbol(
            symbol,
            (position[0] + size[0] // 2, position[1] + size[1] // 2),
            font_size=style.get("fontSize", 30),
            color=style.get("color", (255, 255, 255))
        )
        
        # Add symbol as child component
        container.add_child(symbol_comp)
        
        # Additional styling
        if "padding" in style:
            container.set_property("padding", style["padding"])
            
        return container
    
    def apply_theme(self, component, component_type, variant=None, state=None, **kwargs):
        """Apply theme styling to an existing component.
        
        Args:
            component: Component to style
            component_type: Component type
            variant: Optional variant name
            state: Optional state name
            **kwargs: Additional style overrides
            
        Returns:
            The styled component
        """
        # Get style from theme
        style = self.theme_provider.get_style(component_type, variant, state, **kwargs)
        
        # Apply common style properties
        if "backgroundColor" in style:
            component.set_property("backgroundColor", style["backgroundColor"])
            
        if "color" in style:
            component.set_property("color", style["color"])
            
        if "borderWidth" in style:
            component.set_property("borderWidth", style["borderWidth"])
            
        if "borderColor" in style:
            component.set_property("borderColor", style["borderColor"])
            
        if "borderRadius" in style:
            component.set_property("borderRadius", style["borderRadius"])
            
        # Type-specific properties
        if component_type == "text":
            if "fontSize" in style:
                component.set_property("fontSize", style["fontSize"])
                
            if "fontWeight" in style:
                component.set_property("fontWeight", style["fontWeight"])
                
            if "textAlign" in style:
                component.set_property("textAlign", style["textAlign"])
        
        # Apply any remaining style properties
        for key, value in style.items():
            if key not in ["backgroundColor", "color", "borderWidth", "borderColor", 
                          "borderRadius", "fontSize", "fontWeight", "textAlign"]:
                component.set_property(key, value)
        
        return component 