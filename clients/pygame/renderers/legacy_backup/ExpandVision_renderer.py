#!/usr/bin/env python3
"""
ExpandVision module renderer for the PyGame client.

This renderer handles displaying the ExpandVision training module,
which trains a user's peripheral vision and ability to process information.
"""

import pygame
import math
from .base_renderer import BaseRenderer
from MetaMindIQTrain.config import (
    UI_CONTENT_TOP, UI_CONTENT_BOTTOM, UI_PADDING, 
    UI_MARGIN, BUTTON_WIDTH, BUTTON_HEIGHT
)


class ExpandVisionRenderer(BaseRenderer):
    """Renderer for the ExpandVision module."""
    
    def __init__(self, screen, title_font, regular_font, small_font, colors=None):
        """Initialize the ExpandVision renderer.
        
        Args:
            screen: PyGame screen surface
            title_font: Font for titles
            regular_font: Font for regular text
            small_font: Font for small text
            colors: Dictionary of colors (optional)
        """
        # Initialize the base renderer
        super().__init__(screen, title_font, regular_font, small_font, colors)
        
        # Add ExpandVision-specific colors
        ev_colors = {
            'background': (40, 40, 60),  # Darker blue background like the demo
            'text': (220, 220, 220),
            'highlight': (255, 255, 255),
            'circle': (0, 120, 255),  # Blue circle like the demo
            'focus_point': (255, 0, 0),  # Red center dot
            'number': (240, 240, 10),  # Yellow numbers
            'instructions': (180, 180, 210),
            'input': (255, 255, 255),
            'input_box': (60, 60, 100),
            'input_active': (80, 80, 120)  # Highlighted when active
        }
        
        # Update colors
        self.colors.update(ev_colors)
        
        # Override with provided colors if any
        if colors:
            self.colors.update(colors)
        
        # Create a custom input font
        self.input_font = pygame.font.SysFont('Arial', 36, bold=True)
        self.number_font = pygame.font.SysFont('Arial', 42, bold=True)  # Increased for visibility
        
    def render(self, state):
        """Render the current state of the module.
        
        Args:
            state: Module state dictionary
        """
        # Use the standard layout structure
        self.draw_standard_layout(state)
        
        # Extract state variables for easier access
        self._extract_state_variables(state)
        
        # Draw the main exercise content in the content area
        self._draw_expanding_circle()
        
        # Draw instructions in the content area
        self._draw_instructions()
        
        # Draw numbers and input field if active
        if self.show_numbers and self.numbers:
            self._draw_peripheral_numbers()
            self._draw_input_field()
    
    def _extract_state_variables(self, state):
        """Extract and store state variables as instance attributes."""
        # Layout variables - use the center of the content area
        self.content_center_x = self.width // 2
        self.content_center_y = UI_CONTENT_TOP + (UI_CONTENT_BOTTOM - UI_CONTENT_TOP) // 2
        
        # State variables
        self.circle_width = state.get('circle_width', 30)
        self.circle_height = state.get('circle_height', 30)
        self.show_numbers = state.get('show_numbers', False)
        self.numbers = state.get('numbers', [])
        self.message = state.get('message', "")
        self.user_input = state.get('user_input', "")
    
    def _draw_expanding_circle(self):
        """Draw the expanding circle and focus point."""
        # Draw expanding circle
        pygame.draw.ellipse(
            self.screen,
            self.colors['circle'],
            (self.content_center_x - self.circle_width // 2,
             self.content_center_y - self.circle_height // 2,
             self.circle_width,
             self.circle_height),
            2
        )
        
        # Draw center focus point
        pygame.draw.circle(
            self.screen,
            self.colors['focus_point'],
            (self.content_center_x, self.content_center_y),
            6  # Slightly larger for better visibility
        )
    
    def _draw_peripheral_numbers(self):
        """Draw the numbers in the periphery."""
        # Calculate positions for numbers around the outer edge
        # Scale these positions based on screen dimensions
        circle_radius = max(self.circle_width, self.circle_height) // 2
        number_distance = circle_radius + 100  # Position numbers outside the circle
        
        # Calculate positions for numbers at top, right, bottom, left
        angle_offset = 0  # Start from top (0 degrees)
        num_positions = []
        
        for i in range(4):  # 4 positions around the circle
            angle = math.radians(angle_offset + (i * 90))  # Convert to radians
            pos_x = self.content_center_x + math.sin(angle) * number_distance
            pos_y = self.content_center_y - math.cos(angle) * number_distance
            num_positions.append((pos_x, pos_y))
        
        # Draw each number with a background circle for better visibility
        for i, num in enumerate(self.numbers[:4]):  # Ensure we only use up to 4 numbers
            if i < len(num_positions):
                pos_x, pos_y = num_positions[i]
                
                # Draw background circle (like in the demo)
                circle_radius = 35  # Slightly larger for better visibility
                pygame.draw.circle(
                    self.screen,
                    (50, 50, 80),  # Dark background
                    (int(pos_x), int(pos_y)),
                    circle_radius
                )
                
                # Draw circle border
                pygame.draw.circle(
                    self.screen,
                    self.colors['highlight'],
                    (int(pos_x), int(pos_y)),
                    circle_radius,
                    2  # Border width
                )
                
                # Draw number
                self.draw_text(str(num), int(pos_x), int(pos_y), 
                              self.number_font, self.colors['number'])
    
    def _draw_input_field(self):
        """Draw the input field for the user's answer."""
        # Center the input field at the bottom of the content area
        input_width = 200
        input_height = 50
        input_x = (self.width - input_width) // 2
        input_y = UI_CONTENT_BOTTOM - input_height - UI_PADDING * 2
        
        # Create input box rect
        input_rect = pygame.Rect(input_x, input_y, input_width, input_height)
        
        # Draw input box
        pygame.draw.rect(
            self.screen, 
            self.colors['input_box'], 
            input_rect
        )
        pygame.draw.rect(
            self.screen, 
            self.colors['highlight'], 
            input_rect, 
            2  # Border width
        )
        
        # Draw input text or placeholder
        input_text = self.user_input if self.user_input else "Enter sum"
        text_color = self.colors['input'] if self.user_input else (150, 150, 150)
        
        self.draw_text(input_text, input_rect.centerx, input_rect.centery, 
                      self.input_font, text_color)
        
        # Add a label above the input box
        label_y = input_y - 30
        self.draw_text("Enter the sum of all numbers:", 
                      self.width // 2, label_y, 
                      self.regular_font, self.colors['instructions'])
    
    def _draw_instructions(self):
        """Draw the main instructions for the module."""
        # Draw instructions near the top of the content area
        instruction_y = UI_CONTENT_TOP + UI_PADDING
        
        self._draw_instruction("Focus on the center red dot", instruction_y)
        
        if self.show_numbers:
            instruction_y += 30
            self._draw_instruction("Notice the numbers in your peripheral vision", instruction_y)
            instruction_y += 30
            self._draw_instruction("Calculate the sum: " + "+".join(str(n) for n in self.numbers), instruction_y)
            
    def _draw_instruction(self, text, y):
        """Draw an instruction with proper formatting."""
        self.draw_text(text, self.width // 2, y, self.regular_font, self.colors['instructions'])
        
    # For backward compatibility
    def draw(self, state):
        """Alias for render for backward compatibility."""
        self.render(state) 