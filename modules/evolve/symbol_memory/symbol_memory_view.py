#!/usr/bin/env python3
"""
Symbol Memory View Component

This module handles the UI representation for the Symbol Memory training module:
- Layout calculations based on screen dimensions
- Component tree building for rendering
- Visual representation of the symbol grid
- Theme-aware styling
"""

import math
import sys
import pygame
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional

# Add the parent directory to sys.path for absolute imports when imported directly
if __name__ == "__main__" or not __package__:
    project_root = Path(__file__).parent.parent.parent.parent
    sys.path.insert(0, str(project_root))
    from MetaMindIQTrain.core.theme_manager import ThemeManager
    from MetaMindIQTrain.core.config import config
else:
    # Use relative imports when imported as a module
    from ....core.theme_manager import ThemeManager
    from ....core.config import config


class SymbolMemoryView:
    """View component for SymbolMemory module - handles UI representation."""
    
    def __init__(self, model):
        """Initialize the view with reference to the model.
        
        Args:
            model: SymbolMemoryModel instance
        """
        self.model = model
        self.screen_width = 800  # Default width
        self.screen_height = 600  # Default height
        
        # Grid layout properties
        self.cell_size = 60  # Will be adjusted based on grid size
        self.grid_margin = 40
        self.grid_padding = 10
        
        # Button dimensions
        self.button_width = 120
        self.button_height = 50
        self.button_margin = 20
        
        # UI element references
        self.grid_rect = None  # Rectangle for the grid
        self.button_rects = {}  # Rectangles for buttons
    
    def set_dimensions(self, width, height):
        """Set the screen dimensions.
        
        Args:
            width: Screen width
            height: Screen height
        """
        self.screen_width = width
        self.screen_height = height
        self.calculate_layout()
    
    def calculate_layout(self):
        """Calculate layout based on screen dimensions and grid size."""
        # Get theme styling for symbol memory
        theme = config.UI_THEME
        symbol_layout = theme["layouts"]["symbol_memory"]
        
        # Get module-specific settings including scaling factor
        module_settings = config.MODULE_SETTINGS["symbol_memory"]
        visual_scale = module_settings.get("visual_scale", 1.0)  # Default to 1.0 if not specified
        
        # Calculate grid dimensions
        grid_size = self.model.current_grid_size
        
        # Get content area dimensions
        content_width = self.screen_width
        content_height = int(self.screen_height * 0.7)  # 70% of screen height
        content_y = int(self.screen_height * 0.15)  # 15% from top
        
        # Calculate grid margin and padding as percentage of screen
        self.grid_margin = int(min(content_width, content_height) * symbol_layout["grid_margin"] / 100)
        self.grid_padding = int(min(content_width, content_height) * symbol_layout["grid_padding"] / 100)
        
        # Calculate maximum grid size based on available space
        max_grid_width = content_width - (2 * self.grid_margin)
        max_grid_height = content_height - (2 * self.grid_margin)
        max_grid_size = min(max_grid_width, max_grid_height)
        
        # Apply visual scaling factor to the grid size
        max_grid_size = int(max_grid_size * visual_scale)
        
        # Calculate cell size including margin between cells
        cell_margin_percent = symbol_layout["cell_margin"]
        total_cell_margin = (grid_size - 1) * (max_grid_size * cell_margin_percent / 100)
        available_cell_space = max_grid_size - total_cell_margin
        self.cell_size = int(available_cell_space / grid_size)
        
        # Calculate total grid size including padding
        grid_width = grid_size * self.cell_size + total_cell_margin + 2 * self.grid_padding
        grid_height = grid_width  # Square grid
        
        # Center grid in content area
        grid_x = (content_width - grid_width) // 2
        grid_y = content_y + (content_height - grid_height) // 2
        
        self.grid_rect = (grid_x, grid_y, grid_width, grid_height)
        
        # Calculate button positions matching HTML layout
        self._calculate_button_positions()
    
    def _calculate_button_positions(self):
        """Calculate positions for buttons based on screen size and phase."""
        # Get module-specific settings including scaling factor
        module_settings = config.MODULE_SETTINGS["symbol_memory"]
        visual_scale = module_settings.get("visual_scale", 1.0)  # Default to 1.0 if not specified
        
        # Get footer area dimensions
        footer_y = int(self.screen_height * 0.85)  # 85% from top
        footer_height = int(self.screen_height * 0.15)  # 15% of screen height
        
        # Button dimensions based on percentage of screen
        self.button_width = int(self.screen_width * 0.15 * visual_scale)  # 15% of screen width * scale
        self.button_height = int(footer_height * 0.5 * visual_scale)  # 50% of footer height * scale
        self.button_margin = int(self.screen_width * 0.05)  # 5% of screen width (not scaled)
        
        # Calculate yes/no button positions (side by side in footer)
        yes_x = self.screen_width // 2 - self.button_width - self.button_margin // 2
        no_x = self.screen_width // 2 + self.button_margin // 2
        buttons_y = footer_y + (footer_height - self.button_height) // 2
        
        self.button_rects = {
            "yes": (yes_x, buttons_y, self.button_width, self.button_height),
            "no": (no_x, buttons_y, self.button_width, self.button_height),
            "continue": ((self.screen_width - self.button_width) // 2, buttons_y, self.button_width, self.button_height)
        }
    
    def get_cell_rect(self, row, col):
        """Get the rectangle for a grid cell.
        
        Args:
            row: Row index
            col: Column index
            
        Returns:
            Tuple of (x, y, width, height)
        """
        grid_x, grid_y, _, _ = self.grid_rect
        
        # Calculate cell position within grid
        cell_x = grid_x + self.grid_padding + col * self.cell_size
        cell_y = grid_y + self.grid_padding + row * self.cell_size
        
        return (cell_x, cell_y, self.cell_size, self.cell_size)
    
    def build_component_tree(self):
        """Build a component tree for rendering.
        
        Returns:
            Root component of the UI tree
        """
        # Root container
        root = {
            "type": "container",
            "id": "symbol_memory_root",
            "width": self.screen_width,
            "height": self.screen_height,
            "properties": {
                "style": {
                    "backgroundColor": ThemeManager.get_color("bg_color")
                }
            },
            "children": [
                # Header
                {
                    "type": "container",
                    "id": "header",
                    "x": 0,
                    "y": 0,
                    "width": self.screen_width,
                    "height": 50,
                    "properties": {
                        "style": {
                            "backgroundColor": ThemeManager.get_color("card_bg")
                        }
                    },
                    "children": [
                        # Title
                        {
                            "type": "text",
                            "id": "title",
                            "x": 20,
                            "y": 10,
                            "width": 300,
                            "height": 30,
                            "text": "Symbol Memory - Recall Challenge",
                            "properties": {
                                "style": {
                                    "color": ThemeManager.get_color("text_color"),
                                    "fontSize": 18
                                }
                            }
                        },
                        # Score
                        {
                            "type": "text",
                            "id": "score",
                            "x": self.screen_width - 150,
                            "y": 10,
                            "width": 130,
                            "height": 30,
                            "text": f"Score: {self.model.score}",
                            "properties": {
                                "style": {
                                    "color": ThemeManager.get_color("text_color"),
                                    "textAlign": "right",
                                    "fontSize": 18
                                }
                            }
                        }
                    ]
                },
                
                # Instructions/Message
                {
                    "type": "text",
                    "id": "instructions",
                    "x": 20,
                    "y": 60,
                    "width": self.screen_width - 40,
                    "height": 30,
                    "text": self.model.message,
                    "properties": {
                        "style": {
                            "color": ThemeManager.get_color("text_color"),
                            "textAlign": "center"
                        }
                    }
                },
                
                # Symbol grid
                {
                    "type": "container",
                    "id": "grid_container",
                    "x": self.grid_rect[0],
                    "y": self.grid_rect[1],
                    "width": self.grid_rect[2],
                    "height": self.grid_rect[3],
                    "properties": {
                        "style": {
                            "backgroundColor": ThemeManager.get_color("card_bg"),
                            "borderColor": ThemeManager.get_color("border_color"),
                            "borderWidth": 2,
                            "borderRadius": 5
                        }
                    },
                    "children": self._create_grid_components()
                },
                
                # Button container
                {
                    "type": "container",
                    "id": "button_container",
                    "x": 0,
                    "y": self.button_rects["yes"][1] - 10,
                    "width": self.screen_width,
                    "height": 70,
                    "children": self._create_button_components()
                }
            ]
        }
        
        return root
    
    def _create_grid_components(self):
        """Create component specs for grid cells.
        
        Returns:
            List of cell component specifications
        """
        cells = []
        
        # Get the current pattern based on phase
        pattern = None
        show_symbols = False
        
        if self.model.phase == self.model.PHASE_MEMORIZE:
            pattern = self.model.original_pattern
            show_symbols = True
        elif self.model.phase == self.model.PHASE_COMPARE:
            pattern = self.model.modified_pattern
            show_symbols = True
        elif self.model.phase in [self.model.PHASE_ANSWER, self.model.PHASE_FEEDBACK]:
            pattern = self.model.modified_pattern
            show_symbols = True
        
        if not pattern:
            return cells
            
        grid = pattern["grid"]
        grid_size = pattern["size"]
        
        # Calculate cell dimensions
        padding = self.grid_padding
        cell_size = self.cell_size
        
        for row in range(grid_size):
            for col in range(grid_size):
                cell_x = padding + col * cell_size
                cell_y = padding + row * cell_size
                
                symbol = grid[row][col] if show_symbols else ""
                
                # Cell background
                cell = {
                    "type": "container",
                    "id": f"cell_{row}_{col}",
                    "x": cell_x,
                    "y": cell_y,
                    "width": cell_size,
                    "height": cell_size,
                    "properties": {
                        "style": {
                            "backgroundColor": ThemeManager.get_color("card_hover"),
                            "borderColor": ThemeManager.get_color("border_color"),
                            "borderWidth": 1
                        }
                    }
                }
                
                cells.append(cell)
                
                # Symbol text (if visible)
                if show_symbols and symbol:
                    # Check if this cell is the one that was modified (for feedback highlight)
                    is_highlighted = False
                    if self.model.phase == self.model.PHASE_FEEDBACK and self.model.was_modified:
                        if self.model.modified_position and (row, col) == self.model.modified_position:
                            is_highlighted = True
                    
                    # Get symbol color
                    color = self.model.get_symbol_color(symbol)
                    color_str = f"rgb({color[0]}, {color[1]}, {color[2]})"
                    
                    symbol_text = {
                        "type": "text",
                        "id": f"symbol_{row}_{col}",
                        "x": cell_x,
                        "y": cell_y,
                        "width": cell_size,
                        "height": cell_size,
                        "text": symbol,
                        "properties": {
                            "style": {
                                "color": color_str,
                                "fontSize": int(cell_size * 0.6),
                                "textAlign": "center",
                                "fontWeight": "bold" if is_highlighted else "normal"
                            }
                        }
                    }
                    
                    cells.append(symbol_text)
        
        return cells
    
    def _create_button_components(self):
        """Create component specs for buttons.
        
        Returns:
            List of button component specifications
        """
        buttons = []
        
        if self.model.phase == self.model.PHASE_ANSWER:
            # Yes button
            yes_rect = self.button_rects["yes"]
            yes_button = {
                "type": "button",
                "id": "yes_button",
                "x": yes_rect[0],
                "y": yes_rect[1],
                "width": yes_rect[2],
                "height": yes_rect[3],
                "text": "Yes",
                "properties": {
                    "style": {
                        "backgroundColor": ThemeManager.get_color("primary_color"),
                        "color": ThemeManager.get_color("text_color"),
                        "borderRadius": 5
                    }
                }
            }
            buttons.append(yes_button)
            
            # No button
            no_rect = self.button_rects["no"]
            no_button = {
                "type": "button",
                "id": "no_button",
                "x": no_rect[0],
                "y": no_rect[1],
                "width": no_rect[2],
                "height": no_rect[3],
                "text": "No",
                "properties": {
                    "style": {
                        "backgroundColor": ThemeManager.get_color("secondary_color"),
                        "color": ThemeManager.get_color("text_color"),
                        "borderRadius": 5
                    }
                }
            }
            buttons.append(no_button)
        
        elif self.model.phase == self.model.PHASE_FEEDBACK:
            # Continue button
            continue_rect = self.button_rects["continue"]
            continue_button = {
                "type": "button",
                "id": "continue_button",
                "x": continue_rect[0],
                "y": continue_rect[1],
                "width": continue_rect[2],
                "height": continue_rect[3],
                "text": "Continue",
                "properties": {
                    "style": {
                        "backgroundColor": ThemeManager.get_color("primary_color"),
                        "color": ThemeManager.get_color("text_color"),
                        "borderRadius": 5
                    }
                }
            }
            buttons.append(continue_button)
        
        return buttons

    def render_grid(self, renderer):
        """Render the symbol grid using enhanced styling to match HTML/CSS.
        
        Args:
            renderer: UIRenderer instance
        """
        # Get theme styling
        theme = config.UI_THEME
        
        # Get module-specific settings including scaling factor
        module_settings = config.MODULE_SETTINGS["symbol_memory"]
        visual_scale = module_settings.get("visual_scale", 1.0)  # Default to 1.0 if not specified
        preserve_font_size = module_settings.get("preserve_font_size", True)
        
        # Get grid dimensions
        grid_x, grid_y, grid_width, grid_height = self.grid_rect
        
        # Draw grid background
        bg_color = theme["colors"]["bg_dark"]
        pygame.draw.rect(
            renderer.screen, 
            bg_color, 
            self.grid_rect, 
            border_radius=10
        )
        
        # Get the current pattern based on phase
        pattern = None
        show_symbols = False
        
        if self.model.phase == self.model.PHASE_MEMORIZE:
            pattern = self.model.original_pattern
            show_symbols = True
            phase_text = "Memorize the pattern"
            phase_type = "memorize"
        elif self.model.phase == self.model.PHASE_COMPARE:
            pattern = self.model.modified_pattern
            show_symbols = True
            phase_text = "Was the pattern changed?"
            phase_type = "recall"
        elif self.model.phase == self.model.PHASE_ANSWER:
            pattern = self.model.modified_pattern
            show_symbols = True
            phase_text = "Was a symbol changed?"
            phase_type = "recall"
        elif self.model.phase == self.model.PHASE_FEEDBACK:
            pattern = self.model.modified_pattern
            show_symbols = True
            
            if self.model.user_answer == self.model.was_modified:
                phase_text = "Correct!"
                phase_type = "feedback_correct"
            else:
                phase_text = "Incorrect!"
                phase_type = "feedback_incorrect"
        else:
            # Default for hidden phase
            pattern = self.model.original_pattern
            show_symbols = False
            phase_text = "Recall the pattern"
            phase_type = "recall"
        
        # Render phase indicator
        if hasattr(renderer, 'render_phase_indicator'):
            renderer.render_phase_indicator(phase_text, phase_type)
        
        if not pattern:
            return
            
        grid = pattern["grid"]
        grid_size = pattern["size"]
        
        # Calculate cell dimensions
        grid_inner_width = grid_width - 2 * self.grid_padding
        cell_margin = grid_inner_width * theme["layouts"]["symbol_memory"]["cell_margin"] / 100 / grid_size
        cell_size = (grid_inner_width - cell_margin * (grid_size - 1)) / grid_size
        
        # Render grid cells
        for row in range(grid_size):
            for col in range(grid_size):
                # Calculate cell position
                cell_x = grid_x + self.grid_padding + col * (cell_size + cell_margin)
                cell_y = grid_y + self.grid_padding + row * (cell_size + cell_margin)
                
                # Get symbol for this cell
                symbol = ""
                if row < len(grid) and col < len(grid[row]):
                    symbol = grid[row][col] if show_symbols else ""
                
                # Determine if cell is highlighted (for modified cell highlighting)
                is_highlighted = False
                if self.model.phase == self.model.PHASE_FEEDBACK and self.model.was_modified:
                    if self.model.modified_position:
                        mod_row, mod_col = self.model.modified_position
                        is_highlighted = (row == mod_row and col == mod_col)
                
                # Get symbol color if available
                symbol_color = None
                if symbol and hasattr(self.model, 'get_symbol_color'):
                    symbol_color = self.model.get_symbol_color(symbol)
                
                # Render cell with styled appearance
                cell_rect = (cell_x, cell_y, cell_size, cell_size)
                if hasattr(renderer, 'render_styled_grid_cell'):
                    renderer.render_styled_grid_cell(
                        cell_rect, 
                        theme["colors"]["bg_light"], 
                        symbol if show_symbols else "", 
                        is_highlighted,
                        symbol_color=symbol_color
                    )
                else:
                    # Fallback rendering if specialized method doesn't exist
                    # Draw cell background
                    pygame.draw.rect(
                        renderer.screen,
                        theme["colors"]["bg_light"],
                        cell_rect,
                        border_radius=5
                    )
                    
                    # Draw symbol if visible
                    if show_symbols and symbol:
                        font_size = int(cell_size * 0.6)
                        if hasattr(renderer, 'fonts') and font_size in renderer.fonts:
                            font = renderer.fonts[font_size]
                        else:
                            font = pygame.font.SysFont(None, font_size)
                        
                        text_color = symbol_color if symbol_color else (255, 255, 255)
                        text_surf = font.render(symbol, True, text_color)
                        text_rect = text_surf.get_rect(center=(
                            cell_x + cell_size/2,
                            cell_y + cell_size/2
                        ))
                        renderer.screen.blit(text_surf, text_rect)
    
    def render_buttons(self, renderer):
        """Render the interaction buttons using enhanced styling.
        
        Args:
            renderer: UIRenderer instance
        """
        # Get current phase
        phase = self.model.phase
        
        # Render the appropriate buttons based on phase
        if phase == self.model.PHASE_ANSWER:
            # Render yes/no buttons
            yes_rect = self.button_rects["yes"]
            no_rect = self.button_rects["no"]
            
            # Check for mouse hover
            mouse_pos = pygame.mouse.get_pos()
            is_yes_hover = pygame.Rect(*yes_rect).collidepoint(mouse_pos)
            is_no_hover = pygame.Rect(*no_rect).collidepoint(mouse_pos)
            
            # Render styled buttons
            if hasattr(renderer, 'render_styled_button'):
                renderer.render_styled_button("Yes", yes_rect, "yes", is_highlighted=is_yes_hover)
                renderer.render_styled_button("No", no_rect, "no", is_highlighted=is_no_hover)
            else:
                # Fallback rendering if specialized method doesn't exist
                self._fallback_render_button(renderer, "Yes", yes_rect, is_yes_hover)
                self._fallback_render_button(renderer, "No", no_rect, is_no_hover)
            
        elif phase == self.model.PHASE_FEEDBACK:
            # Render continue button
            continue_rect = self.button_rects["continue"]
            
            # Check for mouse hover
            mouse_pos = pygame.mouse.get_pos()
            is_continue_hover = pygame.Rect(*continue_rect).collidepoint(mouse_pos)
            
            # Render styled button
            if hasattr(renderer, 'render_styled_button'):
                renderer.render_styled_button("Continue", continue_rect, "continue", is_highlighted=is_continue_hover)
            else:
                # Fallback rendering if specialized method doesn't exist
                self._fallback_render_button(renderer, "Continue", continue_rect, is_continue_hover)
    
    def _fallback_render_button(self, renderer, text, rect, is_hover):
        """Fallback method to render a button if the renderer doesn't have specialized methods.
        
        Args:
            renderer: Renderer instance
            text: Button text
            rect: Button rectangle (x, y, width, height)
            is_hover: Whether the mouse is hovering over the button
        """
        # Get colors from theme manager
        bg_color = ThemeManager.get_color("primary_color")
        if is_hover:
            # Brighten the color for hover effect
            bg_color = tuple(min(255, c + 30) for c in bg_color)
        text_color = ThemeManager.get_color("text_color")
        
        # Draw button background
        pygame.draw.rect(
            renderer.screen,
            bg_color,
            rect,
            border_radius=5
        )
        
        # Draw button text
        font_size = int(rect[3] * 0.6)
        if hasattr(renderer, 'fonts') and font_size in renderer.fonts:
            font = renderer.fonts[font_size]
        else:
            font = pygame.font.SysFont(None, font_size)
        
        text_surf = font.render(text, True, text_color)
        text_rect = text_surf.get_rect(center=(
            rect[0] + rect[2]/2,
            rect[1] + rect[3]/2
        ))
        renderer.screen.blit(text_surf, text_rect) 