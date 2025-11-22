#!/usr/bin/env python3
"""
Unified Renderer Adapter for PyGame

This module provides an adapter between the old style renderers and the new
component-based rendering system. It allows existing code to use the new
rendering system without major refactoring.
"""

import pygame
import logging
from typing import Dict, Any, List, Tuple, Optional, Union

# Try to import from the package first
try:
    from MetaMindIQTrain.core.theme import Theme, get_theme, set_theme
    from MetaMindIQTrain.core.unified_component_system import ComponentFactory, UI
    from MetaMindIQTrain.clients.pygame.renderers.base_component_renderer import BaseComponentRenderer
    from MetaMindIQTrain.clients.pygame.optimized_renderer import OptimizedRenderer
    from MetaMindIQTrain.clients.pygame.renderer_factory import RendererFactory
except ImportError:
    # For direct execution during development
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))
    from core.theme import Theme, get_theme, set_theme
    from core.unified_component_system import ComponentFactory, UI
    from clients.pygame.renderers.base_component_renderer import BaseComponentRenderer
    from clients.pygame.optimized_renderer import OptimizedRenderer
    from clients.pygame.renderer_factory import RendererFactory

# Configure logging
logger = logging.getLogger(__name__)

class UnifiedRendererAdapter:
    """Adapter to bridge old renderer API to new component-based rendering system."""
    
    def __init__(self, screen, module_id=None, width=None, height=None):
        """Initialize the adapter.
        
        Args:
            screen: PyGame screen surface
            module_id: ID of the module (optional)
            width: Screen width (optional)
            height: Screen height (optional)
        """
        self.screen = screen
        self.module_id = module_id
        self.width = width or screen.get_width()
        self.height = height or screen.get_height()
        
        # Create renderer factory
        self.factory = RendererFactory(screen, default_width=self.width, default_height=self.height)
        
        # Create renderer
        self.renderer = self.factory.create_renderer(module_id)
        
        # Create component factory
        self.component_factory = self.factory.create_component_factory()
        
        # Initialize state
        self.state = {
            'components': [],
            'module_id': module_id,
            'screen_width': self.width,
            'screen_height': self.height
        }
        
        # Track added components
        self.component_map = {}
        
        # Legacy color definitions for backward compatibility
        self.colors = self.renderer.colors
    
    def _convert_legacy_component(self, component_data):
        """Convert a legacy component definition to a unified component.
        
        Args:
            component_data: Legacy component data
            
        Returns:
            Unified component instance
        """
        comp_type = component_data.get('type', 'rect')
        
        # Extract base properties
        props = {
            'x': component_data.get('x', 0),
            'y': component_data.get('y', 0),
            'width': component_data.get('w', 10),
            'height': component_data.get('h', 10),
        }
        
        # Extract style properties
        style = {}
        
        # Common style mappings
        if 'color' in component_data:
            if comp_type == 'text':
                style['color'] = component_data['color']
            else:
                style['backgroundColor'] = component_data['color']
                
        if 'border_width' in component_data:
            style['borderWidth'] = component_data['border_width']
            
        if 'border_color' in component_data:
            style['borderColor'] = component_data['border_color']
            
        if 'radius' in component_data:
            style['borderRadius'] = component_data['radius']
            
        # Type-specific conversions
        if comp_type == 'rect':
            # Add any rect-specific properties
            component = self.component_factory.rect(**props)
            
        elif comp_type == 'circle':
            component = self.component_factory.circle(**props)
            
        elif comp_type == 'text':
            # Add text-specific properties
            props['text'] = component_data.get('text', '')
            
            if 'font_size' in component_data:
                style['fontSize'] = component_data['font_size']
                
            if 'align' in component_data:
                style['textAlign'] = component_data['align']
                
            component = self.component_factory.text(**props)
            
        elif comp_type == 'image':
            # Add image-specific properties
            props['src'] = component_data.get('image_path', '')
            component = self.component_factory.image(**props)
            
        elif comp_type == 'grid':
            # Add grid-specific properties
            cells = component_data.get('cells', [])
            rows = len(cells)
            cols = len(cells[0]) if rows > 0 else 0
            
            props['rows'] = rows
            props['cols'] = cols
            
            component = self.component_factory.grid(**props)
            
            # Process cells if available
            if rows > 0 and cols > 0:
                for row in range(rows):
                    for col in range(cols):
                        if row < len(cells) and col < len(cells[row]):
                            cell_data = cells[row][col]
                            
                            # Create cell component
                            cell_props = {
                                'row': row,
                                'col': col,
                                'x': col * (props['width'] / cols),
                                'y': row * (props['height'] / rows),
                                'width': props['width'] / cols,
                                'height': props['height'] / rows
                            }
                            
                            # Add text if available
                            if 'text' in cell_data:
                                cell_props['symbol'] = cell_data['text']
                            
                            # Create cell component
                            cell = self.component_factory.symbol_cell(**cell_props)
                            
                            # Add cell-specific styles
                            if 'color' in cell_data:
                                cell.style['backgroundColor'] = cell_data['color']
                            
                            if 'text_color' in cell_data:
                                cell.style['symbolColor'] = cell_data['text_color']
                            
                            if 'border_width' in cell_data:
                                cell.style['borderWidth'] = cell_data['border_width']
                            
                            if 'border_color' in cell_data:
                                cell.style['borderColor'] = cell_data['border_color']
                            
                            # Add cell to grid
                            component.add_child(cell)
        else:
            # Default to container for unknown types
            component = self.component_factory.container(**props)
        
        # Apply styles
        component.style.update(style)
        
        # Add component ID if available
        if 'id' in component_data:
            component.props['id'] = component_data['id']
        
        # Add onClick handler if available
        if 'onClick' in component_data:
            component.props['onClick'] = component_data['onClick']
        
        return component
    
    def add_component(self, component_data):
        """Add a component to the renderer.
        
        Args:
            component_data: Component data in legacy format
            
        Returns:
            Component ID
        """
        # Convert to unified component
        component = self._convert_legacy_component(component_data)
        
        # Generate ID if not provided
        comp_id = component_data.get('id', f"comp_{len(self.component_map)}")
        
        # Store in component map
        self.component_map[comp_id] = component
        
        # Add to state
        self.state['components'].append(component)
        
        return comp_id
    
    def update_component(self, comp_id, updates):
        """Update a component.
        
        Args:
            comp_id: Component ID
            updates: Updates to apply
            
        Returns:
            True if successful, False otherwise
        """
        if comp_id not in self.component_map:
            logger.warning(f"Component {comp_id} not found")
            return False
        
        component = self.component_map[comp_id]
        
        # Update properties
        for key, value in updates.items():
            if key == 'x':
                component.layout['x'] = value
            elif key == 'y':
                component.layout['y'] = value
            elif key == 'w':
                component.layout['width'] = value
            elif key == 'h':
                component.layout['height'] = value
            elif key == 'color':
                if component.type == 'text':
                    component.style['color'] = value
                else:
                    component.style['backgroundColor'] = value
            elif key == 'text':
                component.props['text'] = value
            elif key == 'border_width':
                component.style['borderWidth'] = value
            elif key == 'border_color':
                component.style['borderColor'] = value
            elif key == 'radius':
                component.style['borderRadius'] = value
            elif key == 'onClick':
                component.props['onClick'] = value
        
        # Mark component for update
        self.renderer.register_component_update(comp_id, component)
        
        return True
    
    def remove_component(self, comp_id):
        """Remove a component.
        
        Args:
            comp_id: Component ID
            
        Returns:
            True if successful, False otherwise
        """
        if comp_id not in self.component_map:
            logger.warning(f"Component {comp_id} not found")
            return False
        
        # Remove from component map
        component = self.component_map.pop(comp_id)
        
        # Remove from state
        self.state['components'] = [c for c in self.state['components'] if c != component]
        
        # Force redraw
        self.renderer.force_full_redraw()
        
        return True
    
    def clear_components(self):
        """Clear all components."""
        self.component_map.clear()
        self.state['components'] = []
        
        # Force redraw
        self.renderer.force_full_redraw()
    
    def render(self):
        """Render the current state."""
        # Update the renderer
        self.renderer.render(self.state)
    
    def handle_event(self, event):
        """Handle a PyGame event.
        
        Args:
            event: PyGame event
            
        Returns:
            Updated state if event handled, None otherwise
        """
        return self.renderer.handle_event(event, self.state)
    
    def cleanup(self):
        """Clean up resources."""
        self.renderer.cleanup()
        self.factory.cleanup()
    
    # Legacy methods for backward compatibility
    
    def draw_rect(self, x, y, width, height, color, border_width=0, border_color=None, radius=0):
        """Draw a rectangle.
        
        Args:
            x: X position
            y: Y position
            width: Width
            height: Height
            color: Fill color
            border_width: Border width (optional)
            border_color: Border color (optional)
            radius: Border radius (optional)
            
        Returns:
            Component ID
        """
        component_data = {
            'type': 'rect',
            'x': x,
            'y': y,
            'w': width,
            'h': height,
            'color': color
        }
        
        if border_width > 0:
            component_data['border_width'] = border_width
            component_data['border_color'] = border_color or (0, 0, 0)
        
        if radius > 0:
            component_data['radius'] = radius
        
        return self.add_component(component_data)
    
    def draw_circle(self, x, y, radius, color, border_width=0, border_color=None):
        """Draw a circle.
        
        Args:
            x: X position (center)
            y: Y position (center)
            radius: Radius
            color: Fill color
            border_width: Border width (optional)
            border_color: Border color (optional)
            
        Returns:
            Component ID
        """
        component_data = {
            'type': 'circle',
            'x': x - radius,
            'y': y - radius,
            'w': radius * 2,
            'h': radius * 2,
            'color': color
        }
        
        if border_width > 0:
            component_data['border_width'] = border_width
            component_data['border_color'] = border_color or (0, 0, 0)
        
        return self.add_component(component_data)
    
    def draw_text(self, text, x, y, color, font_size=24, align='center', width=None, height=None):
        """Draw text.
        
        Args:
            text: Text to draw
            x: X position
            y: Y position
            color: Text color
            font_size: Font size (optional)
            align: Text alignment (optional)
            width: Width (optional)
            height: Height (optional)
            
        Returns:
            Component ID
        """
        # Estimate size if not provided
        if width is None or height is None:
            # Create temporary font to measure text
            font = pygame.font.SysFont(None, font_size)
            text_size = font.size(text)
            width = width or text_size[0] + 10
            height = height or text_size[1] + 10
        
        component_data = {
            'type': 'text',
            'x': x,
            'y': y,
            'w': width,
            'h': height,
            'text': text,
            'color': color,
            'font_size': font_size,
            'align': align
        }
        
        return self.add_component(component_data)
    
    def draw_image(self, image_path, x, y, width, height):
        """Draw an image.
        
        Args:
            image_path: Path to image
            x: X position
            y: Y position
            width: Width
            height: Height
            
        Returns:
            Component ID
        """
        component_data = {
            'type': 'image',
            'x': x,
            'y': y,
            'w': width,
            'h': height,
            'image_path': image_path
        }
        
        return self.add_component(component_data)
    
    def draw_grid(self, x, y, width, height, cells, cell_spacing=1):
        """Draw a grid.
        
        Args:
            x: X position
            y: Y position
            width: Width
            height: Height
            cells: Grid cell data
            cell_spacing: Spacing between cells (optional)
            
        Returns:
            Component ID
        """
        component_data = {
            'type': 'grid',
            'x': x,
            'y': y,
            'w': width,
            'h': height,
            'cells': cells
        }
        
        return self.add_component(component_data)
    
    def set_title(self, title):
        """Set the module title.
        
        Args:
            title: Title text
        """
        self.state['title'] = title
    
    def set_instructions(self, instructions):
        """Set the instructions text.
        
        Args:
            instructions: Instructions text
        """
        self.state['instructions'] = instructions 