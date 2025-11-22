#!/usr/bin/env python3
"""
Unified Component System for MetaMindIQTrain

This module provides a flexible and optimized component system for building
user interfaces across different client implementations. It includes features
for efficient rendering, component reuse, and automatic layout calculation.

Key optimizations:
1. Component memoization and property caching
2. Automatic diffing to identify changed components
3. Hash-based rendering cache for improved performance
4. Component pooling to reduce object creation overhead
5. Declarative UI definition with automatic layout
"""

import uuid
import time
import json
import hashlib
import logging
from typing import Dict, List, Any, Optional, Tuple, Union, Set, Callable

# Configure logging
logger = logging.getLogger(__name__)

# Global cache and stats for optimization
_component_hash_cache = {}  # (component_id, props_hash) -> hash
_stats = {
    "created": 0,
    "reused": 0,
    "cached": 0,
    "render_hits": 0,
    "render_misses": 0
}

def reset_stats():
    """Reset component statistics."""
    global _stats
    _stats = {
        "created": 0,
        "reused": 0,
        "cached": 0,
        "render_hits": 0,
        "render_misses": 0
    }

def get_stats():
    """Get component statistics.
    
    Returns:
        Dictionary with component statistics
    """
    return _stats.copy()


class Component:
    """Base class for all UI components."""
    
    def __init__(self, component_type: str, id: Optional[str] = None, 
                 x: int = 0, y: int = 0, width: int = 0, height: int = 0, **kwargs):
        """Initialize a component.
        
        Args:
            component_type: Type of component
            id: Unique identifier (auto-generated if None)
            x: X coordinate
            y: Y coordinate
            width: Width
            height: Height
            **kwargs: Additional properties
        """
        global _stats
        _stats["created"] += 1
        
        self.type = component_type
        self.id = id if id is not None else str(uuid.uuid4())
        self.props = {}
        self.style = {}
        self.children = []
        self.parent = None
        self.dirty = True
        self.render_hash = None
        
        # Set initial layout
        self.layout = {
            "x": x,
            "y": y,
            "width": width,
            "height": height
        }
        
        # Process additional props
        for key, value in kwargs.items():
            # Style properties start with uppercase or have specific names
            if (key[0].isupper() or 
                key in ("color", "backgroundColor", "borderColor", "borderWidth", 
                       "borderRadius", "fontSize", "fontFamily", "textAlign")):
                self.style[key] = value
            else:
                self.props[key] = value
    
    def set_props(self, **props):
        """Set component properties.
        
        Args:
            **props: Properties to set
        """
        changed = False
        
        for key, value in props.items():
            if key in self.props and self.props[key] == value:
                continue
                
            self.props[key] = value
            changed = True
        
        if changed:
            self.mark_dirty()
        
        return self
    
    def set_style(self, **styles):
        """Set component styles.
        
        Args:
            **styles: Styles to set
        """
        changed = False
        
        for key, value in styles.items():
            if key in self.style and self.style[key] == value:
                continue
                
            self.style[key] = value
            changed = True
        
        if changed:
            self.mark_dirty()
        
        return self
    
    def set_layout(self, **layout):
        """Set component layout.
        
        Args:
            **layout: Layout properties to set
        """
        changed = False
        
        for key, value in layout.items():
            if key in self.layout and self.layout[key] == value:
                continue
                
            self.layout[key] = value
            changed = True
        
        if changed:
            self.mark_dirty()
        
        return self
    
    def add_child(self, child):
        """Add a child component.
        
        Args:
            child: Child component to add
        """
        self.children.append(child)
        child.parent = self
        self.mark_dirty()
        
        return self
    
    def remove_child(self, child):
        """Remove a child component.
        
        Args:
            child: Child component to remove
        """
        if child in self.children:
            self.children.remove(child)
            child.parent = None
            self.mark_dirty()
        
        return self
    
    def mark_dirty(self):
        """Mark the component as needing to be redrawn."""
        self.dirty = True
        self.render_hash = None
        
        # Mark parent as dirty
        if self.parent:
            self.parent.mark_dirty()
    
    def mark_clean(self):
        """Mark the component as clean (not needing to be redrawn)."""
        self.dirty = False
    
    def needs_render(self) -> bool:
        """Check if the component needs to be redrawn.
        
        Returns:
            True if the component needs to be redrawn, False otherwise
        """
        if self.dirty:
            return True
            
        # Check if any children need rendering
        for child in self.children:
            if child.needs_render():
                return True
                
        return False
    
    def hash_for_rendering(self) -> str:
        """Get a hash of the component for caching rendered surfaces.
        
        Returns:
            Hash string
        """
        global _component_hash_cache, _stats
        
        # Check cache first
        cache_key = (self.id, self._hash_props_and_style())
        if cache_key in _component_hash_cache:
            _stats["cached"] += 1
            return _component_hash_cache[cache_key]
        
        # Generate hash
        props_str = json.dumps(self.props, sort_keys=True)
        style_str = json.dumps(self.style, sort_keys=True)
        layout_str = json.dumps(self.layout, sort_keys=True)
        
        hash_str = hashlib.md5(
            f"{self.type}:{props_str}:{style_str}:{layout_str}".encode()
        ).hexdigest()
        
        # Cache the hash
        _component_hash_cache[cache_key] = hash_str
        
        return hash_str
    
    def _hash_props_and_style(self) -> str:
        """Get a hash of the component's props and style.
        
        Returns:
            Hash string
        """
        props_str = json.dumps(self.props, sort_keys=True)
        style_str = json.dumps(self.style, sort_keys=True)
        
        return hashlib.md5(f"{props_str}:{style_str}".encode()).hexdigest()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the component to a dictionary representation.
        
        Returns:
            Dictionary representation of the component
        """
        result = {
            "id": self.id,
            "type": self.type,
            "props": self.props,
            "style": self.style,
            "layout": self.layout
        }
        
        if self.children:
            result["children"] = [child.to_dict() for child in self.children]
            
        return result


# Try to import theme system
try:
    from . import theme
except ImportError:
    # For direct execution or during development
    import sys
    import os
    from pathlib import Path
    current_dir = Path(__file__).parent
    if str(current_dir) not in sys.path:
        sys.path.insert(0, str(current_dir))
    import theme


class ComponentFactory:
    """Factory for creating UI components."""
    
    @staticmethod
    def text(text="", x=0, y=0, width=100, height=30, **kwargs):
        """Create a text component with theme-aware styling.
        
        Args:
            text: Text content
            x: X coordinate
            y: Y coordinate
            width: Width
            height: Height
            **kwargs: Additional properties/style overrides
            
        Returns:
            Text component
        """
        # Get styles from theme with overrides
        styles = theme.get_theme().resolve_component_styles("text", **kwargs)
        
        # Create component with resolved styles
        return Component(
            component_type="text",
            x=x, y=y, width=width, height=height,
            text=text, **styles
        )
    
    @staticmethod
    def rect(x=0, y=0, width=100, height=100, **kwargs):
        """Create a rectangle component with theme-aware styling.
        
        Args:
            x: X coordinate
            y: Y coordinate
            width: Width
            height: Height
            **kwargs: Additional properties/style overrides
            
        Returns:
            Rectangle component
        """
        # Get styles from theme with overrides
        styles = theme.get_theme().resolve_component_styles("rect", **kwargs)
        
        # Create component with resolved styles
        return Component(
            component_type="rect",
            x=x, y=y, width=width, height=height,
            **styles
        )
    
    @staticmethod
    def circle(x=0, y=0, radius=50, **kwargs):
        """Create a circle component with theme-aware styling.
        
        Args:
            x: X coordinate
            y: Y coordinate
            radius: Circle radius
            **kwargs: Additional properties/style overrides
            
        Returns:
            Circle component
        """
        # Get styles from theme with overrides
        styles = theme.get_theme().resolve_component_styles("circle", **kwargs)
        
        # Ensure size is based on radius
        size = radius * 2
        
        # Create component with resolved styles
        return Component(
            component_type="circle",
            x=x, y=y, width=size, height=size,
            radius=radius, **styles
        )
    
    @staticmethod
    def image(src="", x=0, y=0, width=100, height=100, **kwargs):
        """Create an image component with theme-aware styling.
        
        Args:
            src: Image source path
            x: X coordinate
            y: Y coordinate
            width: Width
            height: Height
            **kwargs: Additional properties/style overrides
            
        Returns:
            Image component
        """
        # Get styles from theme with overrides
        styles = theme.get_theme().resolve_component_styles("image", **kwargs)
        
        # Create component with resolved styles
        return Component(
            component_type="image",
            x=x, y=y, width=width, height=height,
            src=src, **styles
        )
    
    @staticmethod
    def button(text="Button", x=0, y=0, width=100, height=40, **kwargs):
        """Create a button component with theme-aware styling.
        
        Args:
            text: Button text
            x: X coordinate
            y: Y coordinate
            width: Width
            height: Height
            **kwargs: Additional properties/style overrides
            
        Returns:
            Button component
        """
        # Get styles from theme with overrides
        styles = theme.get_theme().resolve_component_styles("button", **kwargs)
        
        # Create component with resolved styles
        return Component(
            component_type="button",
            x=x, y=y, width=width, height=height,
            text=text, **styles
        )
    
    @staticmethod
    def grid(rows=3, cols=3, x=0, y=0, width=300, height=300, **kwargs):
        """Create a grid component with theme-aware styling.
        
        Args:
            rows: Number of rows
            cols: Number of columns
            x: X coordinate
            y: Y coordinate
            width: Width
            height: Height
            **kwargs: Additional properties/style overrides
            
        Returns:
            Grid component
        """
        # Get styles from theme with overrides
        styles = theme.get_theme().resolve_component_styles("grid", **kwargs)
        
        # Create component with resolved styles
        return Component(
            component_type="grid",
            x=x, y=y, width=width, height=height,
            rows=rows, cols=cols, **styles
        )
    
    @staticmethod
    def container(x=0, y=0, width=400, height=300, **kwargs):
        """Create a container component with theme-aware styling.
        
        Args:
            x: X coordinate
            y: Y coordinate
            width: Width
            height: Height
            **kwargs: Additional properties/style overrides
            
        Returns:
            Container component
        """
        # Get styles from theme with overrides
        styles = theme.get_theme().resolve_component_styles("container", **kwargs)
        
        # Create component with resolved styles
        return Component(
            component_type="container",
            x=x, y=y, width=width, height=height,
            **styles
        )
    
    @staticmethod
    def symbol_cell(x=0, y=0, width=80, height=80, symbol="", **kwargs):
        """Create a symbol cell component with theme-aware styling.
        
        Args:
            x: X coordinate
            y: Y coordinate
            width: Width
            height: Height
            symbol: Symbol to display
            **kwargs: Additional properties/style overrides
            
        Returns:
            Symbol cell component
        """
        # Get styles from theme with overrides
        styles = theme.get_theme().resolve_component_styles("symbol_cell", **kwargs)
        
        # Create component with resolved styles
        return Component(
            component_type="symbol_cell",
            x=x, y=y, width=width, height=height,
            symbol=symbol, **styles
        )


class UI:
    """User interface with components."""
    
    def __init__(self, screen_width=800, screen_height=600):
        """Initialize the UI.
        
        Args:
            screen_width: Screen width
            screen_height: Screen height
        """
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.root = Component(component_type="root", x=0, y=0, width=screen_width, height=screen_height)
        self.components_by_id = {self.root.id: self.root}
        self.layout_calculated = False
    
    def add(self, component):
        """Add a component to the UI.
        
        Args:
            component: Component to add
        """
        self.root.add_child(component)
        self._register_component(component)
        self.layout_calculated = False
        
        return self
    
    def remove(self, component):
        """Remove a component from the UI.
        
        Args:
            component: Component to remove
        """
        self.root.remove_child(component)
        self._unregister_component(component)
        
        return self
    
    def clear(self):
        """Clear all components from the UI."""
        self.root.children.clear()
        self.components_by_id = {self.root.id: self.root}
        self.layout_calculated = False
        
        return self
    
    def find_component_by_id(self, component_id):
        """Find a component by ID.
        
        Args:
            component_id: Component ID
            
        Returns:
            Component with the specified ID or None if not found
        """
        return self.components_by_id.get(component_id)
    
    def find_component_at(self, x, y):
        """Find a component at the specified position.
        
        Args:
            x: X coordinate
            y: Y coordinate
            
        Returns:
            Component at the specified position or None if not found
        """
        # Start with the root component
        return self._find_component_at_recursive(self.root, x, y)
    
    def _find_component_at_recursive(self, component, x, y):
        """Recursively find a component at the specified position.
        
        Args:
            component: Component to check
            x: X coordinate
            y: Y coordinate
            
        Returns:
            Component at the specified position or None if not found
        """
        # Check if point is within component bounds
        if not self._is_point_in_component(component, x, y):
            return None
        
        # Search children first (in reverse order to check top-most first)
        for child in reversed(component.children):
            result = self._find_component_at_recursive(child, x, y)
            if result:
                return result
        
        # If no child contains the point, return this component
        return component
    
    def _is_point_in_component(self, component, x, y):
        """Check if a point is within a component's bounds.
        
        Args:
            component: Component to check
            x: X coordinate
            y: Y coordinate
            
        Returns:
            True if the point is within the component's bounds, False otherwise
        """
        layout = component.layout
        
        # Handle circle components differently
        if component.type == "circle":
            # Calculate center and radius
            center_x = layout["x"] + layout["width"] // 2
            center_y = layout["y"] + layout["height"] // 2
            radius = component.props.get("radius", min(layout["width"], layout["height"]) // 2)
            
            # Calculate distance from center
            dx = x - center_x
            dy = y - center_y
            distance = (dx * dx + dy * dy) ** 0.5
            
            return distance <= radius
        
        # Regular rectangular bounds check
        return (
            x >= layout["x"] and
            x < layout["x"] + layout["width"] and
            y >= layout["y"] and
            y < layout["y"] + layout["height"]
        )
    
    def calculate_layout(self):
        """Calculate the layout of all components."""
        # For now, we'll keep it simple and just use the explicitly set
        # positions and sizes. A more sophisticated system would calculate
        # layout based on parent/child relationships and constraints.
        self.layout_calculated = True
        
        return self
    
    def _register_component(self, component):
        """Register a component and its children.
        
        Args:
            component: Component to register
        """
        self.components_by_id[component.id] = component
        
        for child in component.children:
            self._register_component(child)
    
    def _unregister_component(self, component):
        """Unregister a component and its children.
        
        Args:
            component: Component to unregister
        """
        if component.id in self.components_by_id:
            del self.components_by_id[component.id]
        
        for child in component.children:
            self._unregister_component(child)
    
    def to_dict(self):
        """Convert the UI to a dictionary representation.
        
        Returns:
            Dictionary representation of the UI
        """
        components = []
        
        for child in self.root.children:
            components.append(child.to_dict())
        
        return {
            "screen_width": self.screen_width,
            "screen_height": self.screen_height,
            "components": components
        }


class DeltaCalculator:
    """Calculator for state deltas between updates."""
    
    @staticmethod
    def calculate_delta(old_state, new_state):
        """Calculate the delta between two states.
        
        Args:
            old_state: Old state
            new_state: New state
            
        Returns:
            Delta dictionary
        """
        if not old_state:
            return {"full": new_state}
        
        delta = {}
        paths = []
        
        # Find differences
        DeltaCalculator._find_differences(old_state, new_state, "", paths)
        
        # Generate delta
        for path in paths:
            parts = path.lstrip(".").split(".")
            value = new_state
            
            for part in parts:
                if part.isdigit():
                    part = int(part)
                value = value[part]
            
            DeltaCalculator._set_path_value(delta, path.lstrip("."), value)
        
        return {"delta": delta, "paths": paths}
    
    @staticmethod
    def _find_differences(old_value, new_value, path, paths):
        """Recursively find differences between two values.
        
        Args:
            old_value: Old value
            new_value: New value
            path: Current path
            paths: List of paths with differences
        """
        if type(old_value) != type(new_value):
            paths.append(path)
            return
        
        if isinstance(old_value, dict):
            # Check for removed keys
            for key in old_value:
                if key not in new_value:
                    paths.append(f"{path}.{key}")
            
            # Check for new or changed keys
            for key in new_value:
                if key not in old_value:
                    paths.append(f"{path}.{key}")
                else:
                    DeltaCalculator._find_differences(
                        old_value[key], new_value[key], f"{path}.{key}", paths
                    )
        
        elif isinstance(old_value, list):
            # For simplicity, if list length changes, consider the whole list changed
            if len(old_value) != len(new_value):
                paths.append(path)
            else:
                for i in range(len(old_value)):
                    DeltaCalculator._find_differences(
                        old_value[i], new_value[i], f"{path}.{i}", paths
                    )
        
        elif old_value != new_value:
            paths.append(path)
    
    @staticmethod
    def _set_path_value(obj, path, value):
        """Set a value at a specific path in an object.
        
        Args:
            obj: Object to modify
            path: Path to set
            value: Value to set
        """
        parts = path.split(".")
        current = obj
        
        for i, part in enumerate(parts[:-1]):
            if part.isdigit():
                part = int(part)
            
            if part not in current:
                # Determine if the next part is an integer (list index)
                next_part = parts[i + 1]
                if next_part.isdigit():
                    current[part] = []
                else:
                    current[part] = {}
            
            current = current[part]
        
        last_part = parts[-1]
        if last_part.isdigit():
            last_part = int(last_part)
        
        current[last_part] = value


# Helper functions

def create_component_tree(data):
    """Create a component tree from a dictionary representation.
    
    Args:
        data: Dictionary representation of a component
        
    Returns:
        Component tree
    """
    # Extract layout properties
    x = data.get("layout", {}).get("x", 0)
    y = data.get("layout", {}).get("y", 0)
    width = data.get("layout", {}).get("width", 0)
    height = data.get("layout", {}).get("height", 0)
    
    # Create component
    component = Component(
        component_type=data.get("type", "container"),
        id=data.get("id"),
        x=x, y=y, width=width, height=height
    )
    
    # Set properties
    for key, value in data.get("props", {}).items():
        component.props[key] = value
    
    # Set styles
    for key, value in data.get("style", {}).items():
        component.style[key] = value
    
    # Add children
    for child_data in data.get("children", []):
        child = create_component_tree(child_data)
        component.add_child(child)
    
    return component

def create_ui(width, height):
    """Create a new UI with the specified dimensions.
    
    Args:
        width: Screen width
        height: Screen height
        
    Returns:
        UI instance
    """
    return UI(width, height) 