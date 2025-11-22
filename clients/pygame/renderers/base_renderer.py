#!/usr/bin/env python3
"""
Base renderer for all PyGame renderers in MetaMindIQTrain.

This module provides a base class that all specific renderers inherit from,
ensuring a consistent interface and eliminating duplication.
"""

import pygame
from MetaMindIQTrain.config import (
    SECTION_DIVIDER_COLOR, SECTION_DIVIDER_THICKNESS,
    HEADER_BG_COLOR, FOOTER_BG_COLOR, CONTENT_BG_COLOR,
    calculate_sizes, DEFAULT_SIZES
)


class BaseRenderer:
    """Base class for all PyGame renderers."""
    
    def __init__(self, screen, title_font, regular_font, small_font, colors=None):
        """Initialize the renderer with common elements.
        
        Args:
            screen: PyGame screen surface
            title_font: Font for titles
            regular_font: Font for regular text
            small_font: Font for small text
            colors: Dictionary of colors (optional)
        """
        self.screen = screen
        self.title_font = title_font
        self.regular_font = regular_font
        self.small_font = small_font
        
        # Get screen dimensions
        self.width, self.height = screen.get_size()
        
        # Calculate sizes based on actual screen dimensions
        self.sizes = calculate_sizes(self.width, self.height)
        
        # Dark theme colors that match the SymbolMemory implementation
        self.colors = {
            'background': (15, 25, 35),       # Very dark blue/black for background
            'content_bg': (20, 30, 45),       # Slightly lighter for content areas
            'header_bg': (25, 35, 55),        # Dark blue for header
            'footer_bg': (25, 35, 55),        # Dark blue for footer
            'text_primary': (240, 245, 255),  # Almost white for primary text
            'text_secondary': (180, 190, 210),# Light blue-gray for secondary text
            'text_highlight': (255, 255, 255),# Pure white for highlighted text
            'accent': (100, 200, 255),        # Bright blue accent color
            'dark_blue': (30, 60, 120),       # Dark blue for UI elements
            'light_blue': (80, 140, 255),     # Brighter blue for highlights and hover
            'button': (30, 60, 120),          # Button background
            'button_hover': (80, 140, 255),   # Button hover state
            'button_text': (255, 255, 255),   # Button text color
            'correct': (40, 180, 80),         # Success/correct color
            'incorrect': (220, 60, 60),       # Error/incorrect color
            'section_divider': (40, 60, 100), # Section divider lines
            'highlight': (100, 200, 255),     # Highlight color for selections
            'selected': (60, 180, 100),       # Selected item color
            'gray': (120, 120, 130),          # Dark gray for subtle elements
            'gray_light': (180, 180, 200)     # Light gray for secondary elements
        }
        
        # Override with provided colors if any
        if colors:
            self.colors.update(colors)
        
        # Track UI elements
        self.buttons = []
        
        # Define standard layout sections based on calculated sizes
        self.header_rect = pygame.Rect(0, 0, self.width, self.sizes['UI_HEADER_HEIGHT'])
        self.content_rect = pygame.Rect(
            0, 
            self.sizes['UI_CONTENT_TOP'], 
            self.width, 
            self.sizes['UI_CONTENT_HEIGHT']
        )
        self.footer_rect = pygame.Rect(
            0, 
            self.sizes['UI_CONTENT_BOTTOM'], 
            self.width, 
            self.sizes['UI_FOOTER_HEIGHT']
        )
    
    def render(self, state):
        """Render the current state of the module.
        
        Args:
            state: Module state dictionary
        
        This method should be implemented by subclasses.
        """
        raise NotImplementedError("Subclasses must implement the render method")
    
    def draw_standard_layout(self, state):
        """Draw the standard layout with header, content area, and footer.
        
        Args:
            state: Module state dictionary
        """
        # Clear screen with background color
        self.screen.fill(self.colors['background'])
        
        # Reset buttons for this frame
        self.buttons = []
        
        # Draw colored section backgrounds with subtle gradients
        self._draw_gradient_rect(self.header_rect, self.colors['header_bg'], is_vertical=True, darken_bottom=True)
        self._draw_gradient_rect(self.content_rect, self.colors['content_bg'], is_vertical=False)
        self._draw_gradient_rect(self.footer_rect, self.colors['footer_bg'], is_vertical=True, darken_bottom=False)
        
        # Draw header section
        self._draw_header_section(state)
        
        # Draw section divider between header and content - glowing effect
        self._draw_glowing_divider(
            (0, self.sizes['UI_HEADER_HEIGHT']), 
            (self.width, self.sizes['UI_HEADER_HEIGHT']),
            self.colors['section_divider']
        )
        
        # Content area is drawn by subclasses
        
        # Draw another section divider between content and footer - glowing effect
        self._draw_glowing_divider(
            (0, self.sizes['UI_CONTENT_BOTTOM']), 
            (self.width, self.sizes['UI_CONTENT_BOTTOM']),
            self.colors['section_divider']
        )
        
        # Draw footer section
        self._draw_footer_section(state)
    
    def _draw_gradient_rect(self, rect, base_color, is_vertical=True, darken_bottom=True):
        """Draw a rectangle with a subtle gradient for a more attractive look.
        
        Args:
            rect: Pygame Rect to fill
            base_color: Base color (r,g,b) tuple for the gradient
            is_vertical: Whether gradient should be vertical (True) or horizontal (False)
            darken_bottom: If True, gradient darkens toward bottom/right, otherwise top/left
        """
        gradient_surface = pygame.Surface((rect.width, rect.height))
        
        # Unpack the base color
        r, g, b = base_color
        
        # Determine gradient direction and size
        if is_vertical:
            size = rect.height
        else:
            size = rect.width
        
        # Draw the gradient
        for i in range(size):
            # Calculate position in gradient (0.0 to 1.0)
            pos = i / size
            
            # Adjust direction if needed
            if not darken_bottom:
                pos = 1.0 - pos
                
            # Create a subtle gradient (±15%)
            intensity = 1.0 - (pos * 0.15)
            
            # Calculate color with proper intensity
            color = (min(255, int(r * intensity)), 
                    min(255, int(g * intensity)), 
                    min(255, int(b * intensity)))
            
            # Draw the line
            if is_vertical:
                pygame.draw.line(gradient_surface, color, (0, i), (rect.width, i))
            else:
                pygame.draw.line(gradient_surface, color, (i, 0), (i, rect.height))
        
        # Draw the surface to the screen
        self.screen.blit(gradient_surface, rect)
    
    def _draw_glowing_divider(self, start_pos, end_pos, color, thickness=2):
        """Draw a divider line with a subtle glow effect.
        
        Args:
            start_pos: Starting position (x, y) tuple
            end_pos: Ending position (x, y) tuple
            color: Base color for the divider
            thickness: Line thickness
        """
        # Unpack the color
        r, g, b = color
        
        # Create a surface for the glow effect
        glow_width = abs(end_pos[0] - start_pos[0])
        glow_height = max(thickness * 3, 6)  # At least 6 pixels high
        
        glow_surface = pygame.Surface((glow_width, glow_height), pygame.SRCALPHA)
        
        # Draw several lines with decreasing opacity for the glow
        for i in range(glow_height):
            # Calculate distance from center
            distance = abs(i - glow_height // 2)
            max_distance = glow_height // 2
            
            # Calculate alpha based on distance from center
            alpha = 255 * (1.0 - (distance / max_distance))
            
            if i == glow_height // 2:
                # Main line is full color
                line_color = (r, g, b)
            else:
                # Glow lines have alpha
                line_color = (r, g, b, int(alpha * 0.5))
            
            # Draw the line
            pygame.draw.line(
                glow_surface, 
                line_color,
                (0, i), 
                (glow_width, i),
                1
            )
        
        # Position and draw the glow
        y_offset = start_pos[1] - glow_height // 2
        self.screen.blit(glow_surface, (start_pos[0], y_offset))
    
    def _draw_header_section(self, state):
        """Draw the header section with title and description.
        
        Args:
            state: Module state dictionary
        """
        # Draw title
        title = state.get('module_name', state.get('name', "Training Module"))
        self.draw_text(
            title, 
            self.width // 2, 
            self.header_rect.height * 0.3, 
            self.title_font, 
            self.colors['text_highlight']
        )
        
        # Draw module description
        description = state.get('description', "")
        if description:
            self.draw_text(
                description, 
                self.width // 2, 
                self.header_rect.height * 0.65,
                self.regular_font, 
                self.colors['text_primary']
            )
        
        # Draw score in top right corner
        score = state.get('score', 0)
        self.draw_text(
            f"Score: {score}", 
            self.width - self.sizes['UI_PADDING'], 
            self.sizes['UI_PADDING'] + 10, 
            self.regular_font, 
            self.colors['text_secondary'], 
            centered=False
        )
        
        # Draw level in top left corner
        level = state.get('level', 1)
        self.draw_text(
            f"Level: {level}", 
            self.sizes['UI_PADDING'], 
            self.sizes['UI_PADDING'] + 10, 
            self.regular_font, 
            self.colors['text_secondary'], 
            centered=False
        )
    
    def _draw_footer_section(self, state):
        """Draw the footer section with navigation buttons.
        
        Args:
            state: Module state dictionary
        """
        # Draw standard navigation buttons in the footer
        footer_center_y = self.sizes['UI_CONTENT_BOTTOM'] + (self.sizes['UI_FOOTER_HEIGHT'] // 2)
        
        # Create standard buttons based on common module actions
        # Center the buttons horizontally
        button_width = self.sizes['BUTTON_WIDTH']
        button_height = self.sizes['BUTTON_HEIGHT']
        button_spacing = self.sizes['BUTTON_SPACING']
        
        total_width = (button_width * 3) + (button_spacing * 2)
        start_x = (self.width - total_width) // 2
        
        # New Challenge Button
        new_challenge_rect = pygame.Rect(
            start_x, 
            footer_center_y - button_height // 2, 
            button_width, 
            button_height
        )
        self.draw_button(new_challenge_rect, "New Challenge", "start_challenge")
        
        # Reset Level Button
        reset_level_rect = pygame.Rect(
            start_x + button_width + button_spacing, 
            footer_center_y - button_height // 2,
            button_width, 
            button_height
        )
        self.draw_button(reset_level_rect, "Reset Level", "reset_level")
        
        # Next Level Button
        next_level_rect = pygame.Rect(
            start_x + (button_width + button_spacing) * 2, 
            footer_center_y - button_height // 2,
            button_width, 
            button_height
        )
        self.draw_button(next_level_rect, "Next Level", "advance_level")
        
        # Add any module-specific buttons here
        
        # Draw help text if provided
        help_text = state.get('help_text', "")
        if help_text:
            self.draw_text(
                help_text, 
                self.width // 2, 
                self.height - self.sizes['UI_PADDING'],
                self.small_font, 
                self.colors['text_primary']
            )
    
    def draw_text(self, text, x, y, font, color, centered=True, background=None):
        """Draw text on the screen with optional background.
        
        Args:
            text: Text to display
            x, y: Coordinates
            font: PyGame font object
            color: Text color
            centered: Whether to center text at coordinates
            background: Optional background color
        """
        surface = font.render(text, True, color, background)
        rect = surface.get_rect()
        
        if centered:
            rect.center = (x, y)
        else:
            rect.topleft = (x, y)
            
        self.screen.blit(surface, rect)
    
    def draw_button(self, rect, text, action, hover=False, color=None, text_color=None):
        """Draw a button and add it to the button tracking list.
        
        Args:
            rect: Pygame Rect for the button
            text: Button text
            action: Action identifier for this button
            hover: Whether the button is being hovered over
            color: Button color (default: self.colors['button'])
            text_color: Text color (default: self.colors['button_text'])
        """
        color = color or (self.colors['button_hover'] if hover else self.colors['button'])
        text_color = text_color or self.colors['button_text']
        
        # Draw button
        pygame.draw.rect(self.screen, color, rect)
        pygame.draw.rect(self.screen, self.colors['text_highlight'], rect, 2)
        
        # Draw text
        self.draw_text(text, rect.centerx, rect.centery, font=self.regular_font, color=text_color)
        
        # Add to button list for tracking
        self.buttons.append({
            'rect': rect,
            'action': action,
            'actual_rect': rect
        })
    
    def percent_to_pixels(self, percent_w, percent_h):
        """Convert percentage values to pixel values based on screen dimensions.
        
        Args:
            percent_w: Width as percentage of screen width (0.0 to 1.0)
            percent_h: Height as percentage of screen height (0.0 to 1.0)
            
        Returns:
            Tuple of (pixel_width, pixel_height)
        """
        return (int(percent_w * self.width), int(percent_h * self.height))
    
    def percent_x(self, percent):
        """Convert percentage of screen width to pixels.
        
        Args:
            percent: Percentage of screen width (0.0 to 1.0)
            
        Returns:
            Pixels value
        """
        return int(percent * self.width)
    
    def percent_y(self, percent):
        """Convert percentage of screen height to pixels.
        
        Args:
            percent: Percentage of screen height (0.0 to 1.0)
            
        Returns:
            Pixels value
        """
        return int(percent * self.height)
    
    def percent_rect(self, x_percent, y_percent, width_percent, height_percent):
        """Create a pygame.Rect using percentage values.
        
        Args:
            x_percent: X position as percentage of screen width (0.0 to 1.0)
            y_percent: Y position as percentage of screen height (0.0 to 1.0)
            width_percent: Width as percentage of screen width (0.0 to 1.0)
            height_percent: Height as percentage of screen height (0.0 to 1.0)
            
        Returns:
            pygame.Rect with pixel values
        """
        return pygame.Rect(
            self.percent_x(x_percent),
            self.percent_y(y_percent),
            self.percent_x(width_percent),
            self.percent_y(height_percent)
        )
    
    def get_content_rect(self):
        """Get a rect representing the content area (between header and footer).
        
        Returns:
            pygame.Rect for the content area
        """
        return self.content_rect.copy()
        
    def adjust_mouse_position(self, x, y):
        """Adjust mouse position if needed for special scaling.
        
        This is a hook for renderers that implement special scaling.
        
        Args:
            x: Original x coordinate
            y: Original y coordinate
            
        Returns:
            Tuple of (adjusted_x, adjusted_y)
        """
        # Default implementation returns original coordinates
        return x, y
    
    # For backward compatibility
    def draw(self, state):
        """Alias for render method to maintain backward compatibility."""
        return self.render(state) 