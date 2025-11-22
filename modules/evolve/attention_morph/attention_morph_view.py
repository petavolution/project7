#!/usr/bin/env python3
"""
Attention Morph View - UI rendering component for the Attention Morph module

This module implements the View component in the MVC architecture for the 
Attention Morph cognitive training exercise. It handles:
- Rendering of shape grid and UI elements
- Layout calculations for responsive UI
- Visual feedback for user interactions
- Theme-aware styling using ThemeManager
"""

import pygame
import math
import sys
from pathlib import Path
from typing import List, Dict, Tuple, Optional, Union, Any, Set

# Add the parent directory to sys.path for absolute imports
if __name__ == "__main__" or not __package__:
    project_root = Path(__file__).parent.parent.parent
    sys.path.insert(0, str(project_root))
    from MetaMindIQTrain.core.theme_manager import ThemeManager
else:
    # Use relative imports when imported as a module
    from ...core.theme_manager import ThemeManager

from .attention_morph_model import Shape

class AttentionMorphView:
    """View for the Attention Morph module handling rendering and user interface.
    
    This class is responsible for all presentation aspects of the Attention Morph
    training module, including shape rendering, UI elements, and visual feedback.
    The view follows a responsive design pattern that adapts to different screen sizes.
    """

    # UI constants
    HEADER_HEIGHT_PCT = 0.12  # 12% of screen height
    FOOTER_HEIGHT_PCT = 0.10  # 10% of screen height
    GRID_PADDING_PCT = 0.05   # 5% padding around grid
    
    def __init__(self, screen: pygame.Surface):
        """Initialize the view with the screen surface and UI components.
        
        Args:
            screen: Pygame surface to render on
        """
        # Initialize view state and UI components
        self.screen = screen
        self.width, self.height = screen.get_size()
        
        # Theme settings
        self.theme = ThemeManager.get_theme()
        self.bg_color = self.theme["bg_color"]
        self.text_color = self.theme["text_color"]
        self.primary_color = self.theme["primary_color"]
        self.accent_color = self.theme["accent_color"]
        self.success_color = self.theme["success_color"]
        self.error_color = self.theme["error_color"]
        self.card_bg = self.theme["card_bg"]
        
        # Shape colors
        self.shape_colors = {
            "circle": self.theme["primary_color"],
            "square": (30, 180, 30),  # Green
            "triangle": (180, 30, 30),  # Red
            "diamond": (30, 30, 180),  # Blue
            "star": (180, 180, 30),    # Yellow
            "d": (180, 30, 180),       # Magenta
            "p": (30, 180, 180)        # Cyan
        }
        
        # Load fonts
        pygame.font.init()
        self.title_font = pygame.font.SysFont(self.theme["font_family"], int(self.height * 0.05))
        self.score_font = pygame.font.SysFont(self.theme["font_family"], int(self.height * 0.035))
        self.instruction_font = pygame.font.SysFont(self.theme["font_family"], int(self.height * 0.025))
        
        # Animation and feedback state
        self.feedback_timer = 0
        self.feedback_message = ""
        self.feedback_color = self.text_color
        
        # Calculate layout
        self.calculate_layout()

    def calculate_layout(self):
        """Calculate UI layout based on screen dimensions."""
        # Set header and footer heights
        self.header_height = int(self.height * self.HEADER_HEIGHT_PCT)
        self.footer_height = int(self.height * self.FOOTER_HEIGHT_PCT)
        
        # Calculate grid area dimensions
        grid_area_height = self.height - self.header_height - self.footer_height
        grid_area_width = self.width
        
        # Apply padding to grid area
        padding = int(min(grid_area_width, grid_area_height) * self.GRID_PADDING_PCT)
        grid_width = grid_area_width - (2 * padding)
        grid_height = grid_area_height - (2 * padding)
        
        # Ensure grid is square
        self.grid_size = min(grid_width, grid_height)
        
        # Calculate grid position
        self.grid_x = (self.width - self.grid_size) // 2
        self.grid_y = self.header_height + (grid_area_height - self.grid_size) // 2
        
        # Calculate cell size for a 5x5 grid (default)
        self.cell_size = self.grid_size // 5
        
        # Store grid bounds for hit detection
        self.grid_bounds = (
            self.grid_x,
            self.grid_y,
            self.grid_x + self.grid_size,
            self.grid_y + self.grid_size
        )

    def set_dimensions(self, width: int, height: int):
        """Update dimensions when screen size changes.
        
        Args:
            width: New screen width
            height: New screen height
        """
        self.width = width
        self.height = height
        
        # Recalculate UI layout
        self.calculate_layout()
        
        # Update font sizes
        self.title_font = pygame.font.SysFont(self.theme["font_family"], int(self.height * 0.05))
        self.score_font = pygame.font.SysFont(self.theme["font_family"], int(self.height * 0.035))
        self.instruction_font = pygame.font.SysFont(self.theme["font_family"], int(self.height * 0.025))

    def render_shape_grid(self, grid: List[List[Shape]]) -> None:
        """Render the grid of shapes.
        
        Args:
            grid: 2D grid of Shape objects
        """
        # Clear the screen with background color
        self.screen.fill(self.bg_color)
        
        # Get grid dimensions
        rows = len(grid)
        cols = len(grid[0]) if rows > 0 else 0
        
        # Adjust cell size for actual grid dimensions
        self.cell_size = self.grid_size // max(rows, cols)
        
        # Calculate grid position to center it
        grid_width = cols * self.cell_size
        grid_height = rows * self.cell_size
        
        grid_x = (self.width - grid_width) // 2
        grid_y = self.header_height + ((self.height - self.header_height - self.footer_height - grid_height) // 2)
        
        # Draw grid background
        grid_rect = pygame.Rect(grid_x - 2, grid_y - 2, grid_width + 4, grid_height + 4)
        pygame.draw.rect(self.screen, self.card_bg, grid_rect)
        pygame.draw.rect(self.screen, self.primary_color, grid_rect, 2)
        
        # Draw each cell
        for row in range(rows):
            for col in range(cols):
                # Calculate cell position
                cell_x = grid_x + (col * self.cell_size)
                cell_y = grid_y + (row * self.cell_size)
                
                # Get the shape at this position
                shape = grid[row][col]
                
                # Draw the shape
                if shape and shape.shape_type:
                    center_pos = (
                        cell_x + (self.cell_size // 2),
                        cell_y + (self.cell_size // 2)
                    )
                    shape_size = int(self.cell_size * 0.7)
                    
                    self._draw_shape(shape, center_pos)

        # Draw UI elements
        self._draw_header("Attention Morph", "Find all 'd' shapes with exactly 2 marks")
        self._draw_footer("Score: 0", "Level: 1")
        
        # Draw feedback message if active
        if self.feedback_message:
            self._draw_feedback()

    def _draw_shape(self, shape: Shape, position: Tuple[int, int]) -> None:
        """Draw an individual shape with its attributes.
        
        Args:
            shape: Shape object to draw
            position: Center position (x, y) to draw at
        """
        # Extract shape properties
        shape_type = shape.shape_type
        center_x, center_y = position
        size = int(shape.size * 0.7)  # Scale size for better appearance
        
        # Get shape color (use shape's color if available, otherwise use default)
        color = shape.color if hasattr(shape, "color") else self.shape_colors.get(shape_type, self.text_color)
        
        # Adjust brightness if shape is a target
        if shape.is_target:
            # Make color brighter for targets
            r, g, b = color
            color = (min(255, r + 40), min(255, g + 40), min(255, b + 40))
        
        # Draw different shapes based on shape_type
        if shape_type == "circle":
            pygame.draw.circle(self.screen, color, (center_x, center_y), size // 2)
            
        elif shape_type == "square":
            rect = pygame.Rect(
                center_x - size // 2,
                center_y - size // 2,
                size,
                size
            )
            pygame.draw.rect(self.screen, color, rect)
            
        elif shape_type == "triangle":
            points = [
                (center_x, center_y - size // 2),
                (center_x - size // 2, center_y + size // 2),
                (center_x + size // 2, center_y + size // 2)
            ]
            pygame.draw.polygon(self.screen, color, points)
            
        elif shape_type == "diamond":
            points = [
                (center_x, center_y - size // 2),
                (center_x + size // 2, center_y),
                (center_x, center_y + size // 2),
                (center_x - size // 2, center_y)
            ]
            pygame.draw.polygon(self.screen, color, points)
            
        elif shape_type == "star":
            points = []
            for i in range(10):
                angle = math.pi * 2 * i / 10 - math.pi / 2
                radius = size // 2 if i % 2 == 0 else size // 4
                x = center_x + int(radius * math.cos(angle))
                y = center_y + int(radius * math.sin(angle))
                points.append((x, y))
            pygame.draw.polygon(self.screen, color, points)
            
        elif shape_type == "d" or shape_type == "p":
            # Draw a circle for the letter
            pygame.draw.circle(self.screen, color, (center_x, center_y), size // 2)
            
            # Add a black rectangle to create 'd' or 'p' shape
            rect_x = center_x - size // 4 if shape_type == "d" else center_x - size // 4
            rect_width = size // 2
            rect_height = size
            
            # Position the rectangle to create 'd' or 'p'
            if shape_type == "d":
                rect_x = center_x
            else:  # p
                rect_x = center_x - size // 2
                
            rect = pygame.Rect(rect_x - rect_width // 2, center_y - size // 2, rect_width, rect_height)
            pygame.draw.rect(self.screen, self.bg_color, rect)
            
            # Draw letter using a font for better appearance
            font = pygame.font.SysFont(self.theme["font_family"], size)
            text = font.render(shape_type, True, color)
            text_rect = text.get_rect(center=(center_x, center_y))
            self.screen.blit(text, text_rect)
        
        # Draw marks (if any)
        if hasattr(shape, "marks"):
            marks = getattr(shape, "marks", 0)
            mark_radius = size // 10
            
            for i in range(marks):
                mark_x = center_x - size // 4 + (i * size // 4)
                mark_y = center_y - size // 2 - mark_radius * 2
                pygame.draw.circle(self.screen, color, (mark_x, mark_y), mark_radius)

    def highlight_target_stimuli(self, targets: List[Tuple[int, int]]) -> None:
        """Highlight target stimuli on the grid.
        
        Args:
            targets: List of (row, col) positions of targets
        """
        for row, col in targets:
            # Calculate cell position
            cell_x = self.grid_x + (col * self.cell_size)
            cell_y = self.grid_y + (row * self.cell_size)
            
            # Draw highlight rect
            highlight_rect = pygame.Rect(cell_x, cell_y, self.cell_size, self.cell_size)
            pygame.draw.rect(self.screen, self.accent_color, highlight_rect, 3)

    def provide_visual_feedback(self, selection: Tuple[bool, str]) -> None:
        """Provide visual feedback for user selection.
        
        Args:
            selection: Tuple of (correct, message)
        """
        is_correct, message = selection
        self.feedback_message = message
        self.feedback_color = self.success_color if is_correct else self.error_color
        self.feedback_timer = 60  # Display for ~1 second at 60 FPS

    def _draw_feedback(self) -> None:
        """Draw feedback message on screen."""
        if self.feedback_timer > 0:
            text = self.score_font.render(self.feedback_message, True, self.feedback_color)
            text_rect = text.get_rect(center=(self.width // 2, self.height // 2))
            
            # Add background for better readability
            bg_rect = text_rect.copy()
            bg_rect.inflate_ip(20, 10)
            pygame.draw.rect(self.screen, self.bg_color, bg_rect)
            pygame.draw.rect(self.screen, self.feedback_color, bg_rect, 2)
            
            self.screen.blit(text, text_rect)
            self.feedback_timer -= 1

    def _draw_header(self, title: str, instructions: str) -> None:
        """Draw header with title and instructions.
        
        Args:
            title: Title text
            instructions: Instruction text
        """
        # Draw header background
        header_rect = pygame.Rect(0, 0, self.width, self.header_height)
        pygame.draw.rect(self.screen, self.card_bg, header_rect)
        
        # Draw header bottom border
        pygame.draw.line(
            self.screen,
            self.primary_color,
            (0, self.header_height - 1),
            (self.width, self.header_height - 1),
            2
        )
        
        # Draw title
        title_text = self.title_font.render(title, True, self.accent_color)
        title_rect = title_text.get_rect(
            center=(self.width // 2, self.header_height // 3)
        )
        self.screen.blit(title_text, title_rect)
        
        # Draw instructions
        instruction_text = self.instruction_font.render(instructions, True, self.text_color)
        instruction_rect = instruction_text.get_rect(
            center=(self.width // 2, self.header_height * 2 // 3)
        )
        self.screen.blit(instruction_text, instruction_rect)

    def _draw_footer(self, score_text: str, level_text: str) -> None:
        """Draw footer with score and level information.
        
        Args:
            score_text: Score display text
            level_text: Level display text
        """
        # Draw footer background
        footer_rect = pygame.Rect(0, self.height - self.footer_height, self.width, self.footer_height)
        pygame.draw.rect(self.screen, self.card_bg, footer_rect)
        
        # Draw footer top border
        pygame.draw.line(
            self.screen,
            self.primary_color,
            (0, self.height - self.footer_height),
            (self.width, self.height - self.footer_height),
            2
        )
        
        # Draw score
        score_surface = self.score_font.render(score_text, True, self.text_color)
        score_rect = score_surface.get_rect(
            center=(self.width // 4, self.height - self.footer_height // 2)
        )
        self.screen.blit(score_surface, score_rect)
        
        # Draw level
        level_surface = self.score_font.render(level_text, True, self.text_color)
        level_rect = level_surface.get_rect(
            center=(self.width * 3 // 4, self.height - self.footer_height // 2)
        )
        self.screen.blit(level_surface, level_rect)

    def update_ui_design(self) -> None:
        """Update UI design with current theme settings."""
        # Refresh theme
        self.theme = ThemeManager.get_theme()
        
        # Update color settings
        self.bg_color = self.theme["bg_color"]
        self.text_color = self.theme["text_color"]
        self.primary_color = self.theme["primary_color"]
        self.accent_color = self.theme["accent_color"]
        self.success_color = self.theme["success_color"]
        self.error_color = self.theme["error_color"]
        self.card_bg = self.theme["card_bg"]
        
        # Recalculate layout
        self.calculate_layout()