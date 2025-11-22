#!/usr/bin/env python3
"""
PyGame Adapter

This module provides a PyGame implementation of the PlatformAdapter interface
for the unified renderer, handling PyGame-specific rendering functionality.
"""

import logging
import pygame
from typing import Dict, Any, Tuple, Optional
from .renderer import PlatformAdapter

logger = logging.getLogger(__name__)

class PyGameAdapter(PlatformAdapter):
    """PyGame implementation of the platform adapter."""
    
    def __init__(self, fullscreen: bool = False):
        """Initialize the PyGame adapter.
        
        Args:
            fullscreen: Whether to run in fullscreen mode
        """
        self.fullscreen = fullscreen
        self.screen = None
        self.width = 1024
        self.height = 768
        self.clock = None
        self.fps = 60
        
        # Font cache
        self.fonts = {}
        
        # Component renderers
        self.component_renderers = {
            'text': self._render_text,
            'rect': self._render_rect,
            'circle': self._render_circle,
            'button': self._render_button,
            'image': self._render_image,
            'grid': self._render_grid,
            'quantum_state': self._render_quantum_state,
            'neural_node': self._render_neural_node,
            'neural_connection': self._render_neural_connection,
        }
        
    def initialize(self, width: int, height: int) -> None:
        """Initialize PyGame and create the window.
        
        Args:
            width: Screen width in pixels
            height: Screen height in pixels
        """
        pygame.init()
        self.width = width
        self.height = height
        
        # Create the window
        if self.fullscreen:
            self.screen = pygame.display.set_mode((width, height), pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode((width, height))
            
        # Create clock for framerate control
        self.clock = pygame.time.Clock()
        
        # Initialize fonts
        self._initialize_fonts()
        
        logger.info(f"Initialized PyGame adapter: {width}x{height}, fullscreen={self.fullscreen}")
        
    def render_component(self, component_type: str, component_id: str, component_data: Dict[str, Any]) -> None:
        """Render a component using PyGame.
        
        Args:
            component_type: Type of component to render
            component_id: ID of the component
            component_data: Component state data
        """
        if component_type in self.component_renderers:
            self.component_renderers[component_type](component_id, component_data)
        else:
            logger.warning(f"Unknown component type: {component_type}")
        
    def clear(self) -> None:
        """Clear the screen with background color."""
        if self.screen:
            self.screen.fill((20, 20, 30))  # Dark blue-gray background
        
    def update(self) -> None:
        """Update the display and maintain framerate."""
        pygame.display.flip()
        if self.clock:
            self.clock.tick(self.fps)
        
    def shutdown(self) -> None:
        """Shutdown PyGame."""
        pygame.quit()
        logger.info("PyGame adapter shut down")
        
    def _initialize_fonts(self) -> None:
        """Initialize font cache with common sizes."""
        font_name = 'Arial'
        sizes = [16, 20, 24, 32, 48, 64]
        
        for size in sizes:
            self.fonts[size] = pygame.font.SysFont(font_name, size)
            
        # Add special fonts
        self.fonts['title'] = pygame.font.SysFont(font_name, 48, bold=True)
        self.fonts['heading'] = pygame.font.SysFont(font_name, 32, bold=True)
        self.fonts['small'] = pygame.font.SysFont(font_name, 16)
        
        logger.debug("Initialized font cache")
    
    def _parse_color(self, color: Any) -> Tuple[int, int, int, int]:
        """Parse color value from various formats.
        
        Args:
            color: Color value (name, RGB tuple, or RGBA tuple)
            
        Returns:
            RGBA color tuple
        """
        # Color name lookup
        color_map = {
            'red': (255, 0, 0, 255),
            'green': (0, 255, 0, 255),
            'blue': (0, 0, 255, 255),
            'white': (255, 255, 255, 255),
            'black': (0, 0, 0, 255),
            'gray': (128, 128, 128, 255),
            'yellow': (255, 255, 0, 255),
            'cyan': (0, 255, 255, 255),
            'magenta': (255, 0, 255, 255),
            'transparent': (0, 0, 0, 0),
        }
        
        if isinstance(color, str) and color in color_map:
            return color_map[color]
        elif isinstance(color, (list, tuple)):
            if len(color) == 3:
                r, g, b = color
                return (r, g, b, 255)
            elif len(color) == 4:
                return tuple(color)
                
        # Default to white
        logger.warning(f"Unknown color format: {color}, using white")
        return (255, 255, 255, 255)
    
    def _get_font(self, font_spec: Any) -> pygame.font.Font:
        """Get a font from the cache or create a new one.
        
        Args:
            font_spec: Font specification (name, size, or size as int)
            
        Returns:
            PyGame font object
        """
        if isinstance(font_spec, str) and font_spec in self.fonts:
            return self.fonts[font_spec]
        elif isinstance(font_spec, int) and font_spec in self.fonts:
            return self.fonts[font_spec]
        elif isinstance(font_spec, int):
            # Create a new font if not in cache
            self.fonts[font_spec] = pygame.font.SysFont('Arial', font_spec)
            return self.fonts[font_spec]
            
        # Default to small font
        return self.fonts['small']
        
    def _render_text(self, component_id: str, component_data: Dict[str, Any]) -> None:
        """Render a text component.
        
        Args:
            component_id: ID of the component
            component_data: Component data
        """
        text = component_data.get('text', '')
        position = component_data.get('position', [self.width // 2, self.height // 2])
        color = self._parse_color(component_data.get('color', 'white'))
        font_size = component_data.get('font_size', 20)
        font = self._get_font(font_size)
        align = component_data.get('align', 'center')
        
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        
        # Position based on alignment
        if align == 'center':
            text_rect.center = position
        elif align == 'left':
            text_rect.midleft = position
        elif align == 'right':
            text_rect.midright = position
        else:
            text_rect.topleft = position
            
        self.screen.blit(text_surface, text_rect)
        
    def _render_rect(self, component_id: str, component_data: Dict[str, Any]) -> None:
        """Render a rectangle component.
        
        Args:
            component_id: ID of the component
            component_data: Component data
        """
        position = component_data.get('position', [self.width // 2, self.height // 2])
        width = component_data.get('width', 100)
        height = component_data.get('height', 100)
        color = self._parse_color(component_data.get('color', 'white'))
        filled = component_data.get('filled', True)
        border_radius = component_data.get('border_radius', 0)
        
        rect = pygame.Rect(0, 0, width, height)
        rect.center = position
        
        if filled:
            pygame.draw.rect(self.screen, color, rect, border_radius=border_radius)
        else:
            pygame.draw.rect(self.screen, color, rect, 2, border_radius=border_radius)
            
    def _render_circle(self, component_id: str, component_data: Dict[str, Any]) -> None:
        """Render a circle component.
        
        Args:
            component_id: ID of the component
            component_data: Component data
        """
        position = component_data.get('position', [self.width // 2, self.height // 2])
        radius = component_data.get('radius', 50)
        color = self._parse_color(component_data.get('color', 'white'))
        filled = component_data.get('filled', True)
        
        if filled:
            pygame.draw.circle(self.screen, color, position, radius)
        else:
            pygame.draw.circle(self.screen, color, position, radius, 2)
            
    def _render_button(self, component_id: str, component_data: Dict[str, Any]) -> None:
        """Render a button component.
        
        Args:
            component_id: ID of the component
            component_data: Component data
        """
        position = component_data.get('position', [self.width // 2, self.height // 2])
        width = component_data.get('width', 200)
        height = component_data.get('height', 50)
        color = self._parse_color(component_data.get('color', 'blue'))
        hover_color = self._parse_color(component_data.get('hover_color', 'blue'))
        text_color = self._parse_color(component_data.get('text_color', 'white'))
        text = component_data.get('text', 'Button')
        font_size = component_data.get('font_size', 20)
        font = self._get_font(font_size)
        is_hovered = component_data.get('is_hovered', False)
        
        # Create rectangle
        rect = pygame.Rect(0, 0, width, height)
        rect.center = position
        
        # Draw button with appropriate color
        if is_hovered:
            pygame.draw.rect(self.screen, hover_color, rect, border_radius=5)
        else:
            pygame.draw.rect(self.screen, color, rect, border_radius=5)
            
        # Add border
        pygame.draw.rect(self.screen, text_color, rect, 2, border_radius=5)
        
        # Draw text
        text_surface = font.render(text, True, text_color)
        text_rect = text_surface.get_rect(center=rect.center)
        self.screen.blit(text_surface, text_rect)
        
    def _render_image(self, component_id: str, component_data: Dict[str, Any]) -> None:
        """Render an image component.
        
        Args:
            component_id: ID of the component
            component_data: Component data
        """
        position = component_data.get('position', [self.width // 2, self.height // 2])
        path = component_data.get('path', '')
        scale = component_data.get('scale', 1.0)
        rotation = component_data.get('rotation', 0)
        
        if not path:
            logger.warning(f"No image path specified for component {component_id}")
            return
            
        try:
            # Load image (use caching in a real implementation)
            image = pygame.image.load(path)
            
            # Apply scaling
            if scale != 1.0:
                original_size = image.get_size()
                new_size = (int(original_size[0] * scale), int(original_size[1] * scale))
                image = pygame.transform.scale(image, new_size)
                
            # Apply rotation
            if rotation != 0:
                image = pygame.transform.rotate(image, rotation)
                
            # Get rect and position
            rect = image.get_rect()
            rect.center = position
            
            # Draw image
            self.screen.blit(image, rect)
        except Exception as e:
            logger.error(f"Error rendering image {path}: {e}")
            
    def _render_grid(self, component_id: str, component_data: Dict[str, Any]) -> None:
        """Render a grid component.
        
        Args:
            component_id: ID of the component
            component_data: Component data
        """
        position = component_data.get('position', [self.width // 2, self.height // 2])
        grid_size = component_data.get('grid_size', 3)
        cell_size = component_data.get('cell_size', 50)
        color = self._parse_color(component_data.get('color', 'white'))
        cells = component_data.get('cells', [])
        
        # Calculate grid dimensions
        grid_width = grid_size * cell_size
        grid_height = grid_size * cell_size
        grid_left = position[0] - grid_width // 2
        grid_top = position[1] - grid_height // 2
        
        # Draw grid lines
        for i in range(grid_size + 1):
            # Vertical line
            start_pos = (grid_left + i * cell_size, grid_top)
            end_pos = (grid_left + i * cell_size, grid_top + grid_height)
            pygame.draw.line(self.screen, color, start_pos, end_pos, 2)
            
            # Horizontal line
            start_pos = (grid_left, grid_top + i * cell_size)
            end_pos = (grid_left + grid_width, grid_top + i * cell_size)
            pygame.draw.line(self.screen, color, start_pos, end_pos, 2)
            
        # Draw cell contents
        for cell in cells:
            cell_x = cell.get('x', 0)
            cell_y = cell.get('y', 0)
            cell_type = cell.get('type', 'empty')
            cell_color = self._parse_color(cell.get('color', 'white'))
            cell_text = cell.get('text', '')
            
            # Calculate cell position
            cell_left = grid_left + cell_x * cell_size
            cell_top = grid_top + cell_y * cell_size
            cell_center = (cell_left + cell_size // 2, cell_top + cell_size // 2)
            
            if cell_type == 'filled':
                rect = pygame.Rect(cell_left + 2, cell_top + 2, cell_size - 4, cell_size - 4)
                pygame.draw.rect(self.screen, cell_color, rect)
            elif cell_type == 'circle':
                pygame.draw.circle(self.screen, cell_color, cell_center, cell_size // 3)
            elif cell_type == 'text':
                font = self._get_font(cell_size // 2)
                text_surface = font.render(cell_text, True, cell_color)
                text_rect = text_surface.get_rect(center=cell_center)
                self.screen.blit(text_surface, text_rect)
                
    def _render_quantum_state(self, component_id: str, component_data: Dict[str, Any]) -> None:
        """Render a quantum state component.
        
        Args:
            component_id: ID of the component
            component_data: Component data
        """
        position = component_data.get('position', [self.width // 2, self.height // 2])
        radius = component_data.get('radius', 30)
        state_value = component_data.get('state_value', 0)
        probability = component_data.get('probability', 1.0)
        
        # Choose color based on state value
        if state_value == 0:
            primary_color = (50, 100, 200)  # Blue for |0⟩
        else:
            primary_color = (200, 100, 50)  # Orange for |1⟩
            
        # Draw probability ring
        if probability < 1.0:
            # Outer ring shows uncertainty
            pygame.draw.circle(self.screen, (100, 100, 100), position, radius, 2)
            
            # Inner circle size based on probability
            inner_radius = int(radius * probability)
            pygame.draw.circle(self.screen, primary_color, position, inner_radius)
        else:
            # Full certainty
            pygame.draw.circle(self.screen, primary_color, position, radius)
            
        # Draw state label
        font = self._get_font(radius // 2)
        label = f"|{state_value}⟩"
        label_surface = font.render(label, True, (255, 255, 255))
        label_rect = label_surface.get_rect(center=position)
        self.screen.blit(label_surface, label_rect)
        
    def _render_neural_node(self, component_id: str, component_data: Dict[str, Any]) -> None:
        """Render a neural node component.
        
        Args:
            component_id: ID of the component
            component_data: Component data
        """
        position = component_data.get('position', [self.width // 2, self.height // 2])
        radius = component_data.get('radius', 20)
        strength = component_data.get('strength', 1.0)
        is_active = component_data.get('is_active', False)
        is_selected = component_data.get('is_selected', False)
        
        # Calculate color based on strength
        if is_active:
            color = (int(255 * strength), int(200 * strength), 50)
        else:
            color = (50, int(100 * strength), int(200 * strength))
            
        # Draw node
        pygame.draw.circle(self.screen, color, position, radius)
        
        # Draw selection indicator if selected
        if is_selected:
            pygame.draw.circle(self.screen, (255, 255, 255), position, radius + 4, 2)
            
    def _render_neural_connection(self, component_id: str, component_data: Dict[str, Any]) -> None:
        """Render a neural connection component.
        
        Args:
            component_id: ID of the component
            component_data: Component data
        """
        source = component_data.get('source', [self.width // 4, self.height // 2])
        target = component_data.get('target', [self.width * 3 // 4, self.height // 2])
        strength = component_data.get('strength', 1.0)
        is_active = component_data.get('is_active', False)
        pulse_position = component_data.get('pulse_position', None)
        
        # Calculate color and width based on strength and activation
        if is_active:
            color = (int(200 * strength), int(255 * strength), 50)
            width = max(1, int(4 * strength))
        else:
            color = (50, int(100 * strength), int(200 * strength))
            width = max(1, int(2 * strength))
            
        # Draw connection
        pygame.draw.line(self.screen, color, source, target, width)
        
        # Draw pulse if active
        if is_active and pulse_position is not None:
            # Calculate position along the line
            dx = target[0] - source[0]
            dy = target[1] - source[1]
            pulse_x = source[0] + dx * pulse_position
            pulse_y = source[1] + dy * pulse_position
            
            # Draw pulse
            pygame.draw.circle(self.screen, (255, 255, 255), (int(pulse_x), int(pulse_y)), 5) 