#!/usr/bin/env python3
"""
Neural Synthesis View Component

This module handles the UI representation for the Neural Synthesis training module:
- Layout calculations based on screen dimensions
- Component tree building for rendering
- Visual representation of the pattern grid
- Theme-aware styling
"""

import sys
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional

# Ensure project root is in path
_project_root = Path(__file__).resolve().parent.parent.parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

# Import theme manager - try multiple approaches
try:
    from core.theme_manager import ThemeManager
except ImportError:
    try:
        from core.theme import Theme as ThemeManager
    except ImportError:
        ThemeManager = None


class NeuralSynthesisView:
    """View component for Neural Synthesis module - handles UI representation."""
    
    def __init__(self, model):
        """Initialize the view with reference to the model.
        
        Args:
            model: Neural Synthesis Model instance
        """
        self.model = model
        self.screen_width = model.screen_width
        self.screen_height = model.screen_height
        
    def set_dimensions(self, width, height):
        """Set the screen dimensions.
        
        Args:
            width: Screen width
            height: Screen height
        """
        self.screen_width = width
        self.screen_height = height
        
        # Update model's dimensions and recalculate layout
        self.model.screen_width = width
        self.model.screen_height = height
        
        # Recalculate grid position
        grid_width = self.model.grid_size * self.model.cell_size
        grid_height = self.model.grid_size * self.model.cell_size
        self.model.grid_position = (
            (width - grid_width) // 2,
            (height - grid_height) // 2 + 20  # Offset for header
        )
    
    def build_component_tree(self):
        """Build a component tree for rendering.
        
        Returns:
            Dict containing the UI component tree
        """
        # Root container
        root = {
            "type": "container",
            "id": "neural_synthesis_root",
            "width": self.screen_width,
            "height": self.screen_height,
            "properties": {
                "style": {
                    "backgroundColor": ThemeManager.get_color("bg_color")
                }
            },
            "children": [
                # Header
                self._build_header(),
                
                # Game info
                self._build_game_info(),
                
                # Grid
                self._build_grid(),
                
                # Instructions
                self._build_instructions()
            ]
        }
        
        return root
    
    def _build_header(self):
        """Build the header component.
        
        Returns:
            Dict representing the header component
        """
        return {
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
                    "text": "Neural Synthesis - Cross-Modal Training",
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
        }
    
    def _build_game_info(self):
        """Build the game info component.
        
        Returns:
            Dict representing the game info component
        """
        # Game info container
        level_info = f"Level {self.model.level}: {self.model.grid_size}x{self.model.grid_size} grid, {self.model.sequence_length} items"
        trial_text = f"Trial {self.model.current_trial + 1} of {self.model.trials_per_level}"
        
        return {
            "type": "container",
            "id": "game_info",
            "x": 0,
            "y": 50,
            "width": self.screen_width,
            "height": 50,
            "properties": {
                "style": {
                    "backgroundColor": ThemeManager.get_color("bg_color")
                }
            },
            "children": [
                # Level info
                {
                    "type": "text",
                    "id": "level_info",
                    "x": self.screen_width // 2,
                    "y": 70,
                    "width": self.screen_width - 40,
                    "height": 20,
                    "text": level_info,
                    "properties": {
                        "style": {
                            "color": ThemeManager.get_color("text_color"),
                            "textAlign": "center",
                            "fontSize": 16
                        }
                    }
                },
                # Trial progress
                {
                    "type": "text",
                    "id": "trial_progress",
                    "x": self.screen_width // 2,
                    "y": 95,
                    "width": self.screen_width - 40,
                    "height": 20,
                    "text": trial_text,
                    "properties": {
                        "style": {
                            "color": ThemeManager.get_color("text_color"),
                            "textAlign": "center",
                            "fontSize": 16
                        }
                    }
                }
            ]
        }
    
    def _build_grid(self):
        """Build the pattern grid component.
        
        Returns:
            Dict representing the grid component
        """
        # Grid dimensions
        grid_x, grid_y = self.model.grid_position
        cell_size = self.model.cell_size
        grid_width = self.model.grid_size * cell_size
        grid_height = self.model.grid_size * cell_size
        
        # Grid container
        grid_container = {
            "type": "container",
            "id": "grid_container",
            "x": grid_x,
            "y": grid_y,
            "width": grid_width,
            "height": grid_height,
            "properties": {
                "style": {
                    "backgroundColor": ThemeManager.get_color("card_bg"),
                    "borderColor": ThemeManager.get_color("border_color"),
                    "borderWidth": 2,
                    "borderRadius": 5
                }
            },
            "children": []
        }
        
        # Add cells to grid
        children = []
        for y in range(self.model.grid_size):
            for x in range(self.model.grid_size):
                cell_x = x * cell_size
                cell_y = y * cell_size
                
                # Default cell color
                cell_color = ThemeManager.get_color("card_bg_dark")
                
                # If in observation phase, show the pattern
                if self.model.phase == "observation":
                    for item in self.model.current_sequence:
                        if item["position"] == (x, y):
                            color_rgb = self.model.colors[item["color_idx"]]["rgb"]
                            cell_color = f"rgb({color_rgb[0]}, {color_rgb[1]}, {color_rgb[2]})"
                
                # Add cell component
                cell = {
                    "type": "rectangle",
                    "id": f"cell_{x}_{y}",
                    "x": cell_x,
                    "y": cell_y,
                    "width": cell_size - 2,
                    "height": cell_size - 2,
                    "properties": {
                        "style": {
                            "fillColor": cell_color,
                            "borderColor": ThemeManager.get_color("border_color"),
                            "borderWidth": 1
                        }
                    }
                }
                children.append(cell)
                
                # In feedback phase, show correct/incorrect indicators
                if self.model.phase == "feedback":
                    for item in self.model.current_sequence:
                        if item["position"] == (x, y):
                            # Show target pattern
                            color_rgb = self.model.colors[item["color_idx"]]["rgb"]
                            cell["properties"]["style"]["fillColor"] = f"rgb({color_rgb[0]}, {color_rgb[1]}, {color_rgb[2]})"
                    
                    # Check if this cell was in user's sequence
                    for item in self.model.user_sequence:
                        if item["position"] == (x, y):
                            # If it wasn't in the target sequence, mark as error
                            is_correct = False
                            for target in self.model.current_sequence:
                                if target["position"] == (x, y) and target["color_idx"] == item["color_idx"]:
                                    is_correct = True
                                    break
                            
                            if not is_correct:
                                # Add 'X' overlay
                                error_mark = {
                                    "type": "text",
                                    "id": f"error_{x}_{y}",
                                    "x": cell_x + cell_size // 2,
                                    "y": cell_y + cell_size // 2,
                                    "width": cell_size,
                                    "height": cell_size,
                                    "text": "X",
                                    "properties": {
                                        "style": {
                                            "color": ThemeManager.get_color("error_color"),
                                            "fontSize": 24,
                                            "textAlign": "center",
                                            "verticalAlign": "middle"
                                        }
                                    }
                                }
                                children.append(error_mark)
        
        grid_container["children"] = children
        return grid_container
    
    def _build_instructions(self):
        """Build the instructions component.
        
        Returns:
            Dict representing the instructions component
        """
        grid_x, grid_y = self.model.grid_position
        grid_height = self.model.grid_size * self.model.cell_size
        
        # Instructions text based on phase
        instruction_text = ""
        if self.model.phase == "observation":
            instruction_text = "Memorize the pattern"
        elif self.model.phase == "reproduction":
            instruction_text = "Reproduce the pattern"
        elif self.model.phase == "feedback":
            instruction_text = self.model.message
        
        # Progress text for reproduction phase
        progress_text = ""
        if self.model.phase == "reproduction":
            progress_text = f"Selected: {len(self.model.user_sequence)} / {len(self.model.current_sequence)}"
        
        # Instructions container
        instructions = {
            "type": "container",
            "id": "instructions",
            "x": 0,
            "y": grid_y + grid_height + 10,
            "width": self.screen_width,
            "height": 70,
            "properties": {
                "style": {
                    "backgroundColor": ThemeManager.get_color("bg_color")
                }
            },
            "children": [
                # Phase-specific instructions
                {
                    "type": "text",
                    "id": "instruction_text",
                    "x": self.screen_width // 2,
                    "y": grid_y + grid_height + 20,
                    "width": self.screen_width - 40,
                    "height": 30,
                    "text": instruction_text,
                    "properties": {
                        "style": {
                            "color": ThemeManager.get_color("text_color"),
                            "textAlign": "center",
                            "fontSize": 18
                        }
                    }
                }
            ]
        }
        
        # Add progress text for reproduction phase
        if self.model.phase == "reproduction":
            instructions["children"].append({
                "type": "text",
                "id": "progress_text",
                "x": self.screen_width // 2,
                "y": grid_y + grid_height + 50,
                "width": self.screen_width - 40,
                "height": 20,
                "text": progress_text,
                "properties": {
                    "style": {
                        "color": ThemeManager.get_color("text_color"),
                        "textAlign": "center",
                        "fontSize": 16
                    }
                }
            })
        
        return instructions
    
    def render(self, renderer):
        """Render the module using the pygame renderer.

        Args:
            renderer: Renderer instance
        """
        # This method is used if the module needs to render directly with pygame
        # instead of using the component tree
        pass

    def render_to_renderer(self, renderer, model):
        """Render the view using the renderer abstraction.

        This method uses the renderer's drawing API instead of pygame directly,
        allowing for headless rendering and different backend support.

        Args:
            renderer: The renderer instance with drawing methods
            model: The model containing game state
        """
        # Get theme colors
        bg_color = (20, 25, 31)
        card_bg = (30, 36, 44)
        text_color = (240, 240, 240)
        primary_color = (0, 120, 255)
        success_color = (50, 255, 80)
        error_color = (255, 50, 50)
        border_color = (60, 70, 80)

        if ThemeManager:
            bg_color = ThemeManager.get_color("bg_color")
            card_bg = ThemeManager.get_color("card_bg")
            text_color = ThemeManager.get_color("text_color")
            primary_color = ThemeManager.get_color("primary_color")
            success_color = ThemeManager.get_color("success_color")
            error_color = ThemeManager.get_color("error_color")
            border_color = ThemeManager.get_color("border_color")

        # Clear with background color
        renderer.clear((*bg_color, 255))

        # Draw header background
        header_height = 50
        renderer.draw_rectangle(0, 0, self.screen_width, header_height, (*card_bg, 255))

        # Draw title
        renderer.draw_text(
            self.screen_width // 2, 15,
            "Neural Synthesis - Cross-Modal Training",
            font_size=18,
            color=(*text_color, 255),
            align="center"
        )

        # Draw score
        score = model.score if hasattr(model, 'score') else 0
        renderer.draw_text(
            self.screen_width - 30, 15,
            f"Score: {score}",
            font_size=18,
            color=(*text_color, 255),
            align="right"
        )

        # Draw level and trial info
        level = model.level if hasattr(model, 'level') else 1
        grid_size = model.grid_size if hasattr(model, 'grid_size') else 4
        seq_length = model.sequence_length if hasattr(model, 'sequence_length') else 3
        current_trial = model.current_trial if hasattr(model, 'current_trial') else 0
        trials_per_level = model.trials_per_level if hasattr(model, 'trials_per_level') else 5

        level_info = f"Level {level}: {grid_size}x{grid_size} grid, {seq_length} items"
        renderer.draw_text(
            self.screen_width // 2, 60,
            level_info,
            font_size=16,
            color=(*text_color, 255),
            align="center"
        )

        trial_text = f"Trial {current_trial + 1} of {trials_per_level}"
        renderer.draw_text(
            self.screen_width // 2, 85,
            trial_text,
            font_size=16,
            color=(*text_color, 255),
            align="center"
        )

        # Draw the grid
        self._render_grid(renderer, model, card_bg, border_color, success_color, error_color)

        # Draw instructions based on phase
        self._render_instructions(renderer, model, text_color, primary_color, success_color, error_color)

    def _render_grid(self, renderer, model, card_bg, border_color, success_color, error_color):
        """Render the pattern grid.

        Args:
            renderer: The renderer instance
            model: The model containing grid data
            card_bg: Card background color
            border_color: Border color
            success_color: Color for correct answers
            error_color: Color for incorrect answers
        """
        grid_x, grid_y = model.grid_position if hasattr(model, 'grid_position') else (100, 120)
        cell_size = model.cell_size if hasattr(model, 'cell_size') else 60
        grid_size = model.grid_size if hasattr(model, 'grid_size') else 4
        grid_width = grid_size * cell_size
        grid_height = grid_size * cell_size

        # Draw grid background
        renderer.draw_rectangle(
            grid_x - 5, grid_y - 5,
            grid_width + 10, grid_height + 10,
            (*card_bg, 255)
        )

        # Get colors list
        colors = model.colors if hasattr(model, 'colors') else []
        current_sequence = model.current_sequence if hasattr(model, 'current_sequence') else []
        user_sequence = model.user_sequence if hasattr(model, 'user_sequence') else []
        phase = model.phase if hasattr(model, 'phase') else 'observation'

        # Draw cells
        for y in range(grid_size):
            for x in range(grid_size):
                cell_x = grid_x + x * cell_size
                cell_y = grid_y + y * cell_size

                # Default cell color (darker background)
                cell_color = (20, 24, 32)

                # In observation phase, show the pattern
                if phase == "observation":
                    for item in current_sequence:
                        if item.get("position") == (x, y):
                            color_idx = item.get("color_idx", 0)
                            if color_idx < len(colors):
                                rgb = colors[color_idx].get("rgb", (100, 100, 100))
                                cell_color = rgb

                # In feedback phase, show correct and user selections
                elif phase == "feedback":
                    # First check if it's a target
                    is_target = False
                    for item in current_sequence:
                        if item.get("position") == (x, y):
                            is_target = True
                            color_idx = item.get("color_idx", 0)
                            if color_idx < len(colors):
                                rgb = colors[color_idx].get("rgb", (100, 100, 100))
                                cell_color = rgb

                    # Check if user selected this cell incorrectly
                    for item in user_sequence:
                        if item.get("position") == (x, y):
                            if not is_target:
                                # User selected wrong cell - show error
                                cell_color = error_color

                # Draw the cell
                renderer.draw_rectangle(
                    cell_x + 1, cell_y + 1,
                    cell_size - 2, cell_size - 2,
                    (*cell_color, 255)
                )

                # Draw cell border
                renderer.draw_rectangle(
                    cell_x, cell_y,
                    cell_size, cell_size,
                    (*border_color, 255),
                    filled=False
                )

    def _render_instructions(self, renderer, model, text_color, primary_color, success_color, error_color):
        """Render instructions and buttons based on phase.

        Args:
            renderer: The renderer instance
            model: The model containing state
            text_color: Text color
            primary_color: Button color
            success_color: Success message color
            error_color: Error message color
        """
        phase = model.phase if hasattr(model, 'phase') else 'observation'
        grid_x, grid_y = model.grid_position if hasattr(model, 'grid_position') else (100, 120)
        cell_size = model.cell_size if hasattr(model, 'cell_size') else 60
        grid_size = model.grid_size if hasattr(model, 'grid_size') else 4
        grid_height = grid_size * cell_size

        instruction_y = grid_y + grid_height + 30
        message = model.message if hasattr(model, 'message') else ""

        if phase == "observation":
            renderer.draw_text(
                self.screen_width // 2, instruction_y,
                "Observe the pattern carefully!",
                font_size=18,
                color=(*text_color, 255),
                align="center"
            )
        elif phase == "reproduction":
            renderer.draw_text(
                self.screen_width // 2, instruction_y,
                "Reproduce the pattern by clicking cells",
                font_size=18,
                color=(*text_color, 255),
                align="center"
            )
            # Show progress
            seq_length = model.sequence_length if hasattr(model, 'sequence_length') else 3
            user_sequence = model.user_sequence if hasattr(model, 'user_sequence') else []
            progress_text = f"Selected: {len(user_sequence)} / {seq_length}"
            renderer.draw_text(
                self.screen_width // 2, instruction_y + 30,
                progress_text,
                font_size=16,
                color=(*text_color, 255),
                align="center"
            )
        elif phase == "feedback":
            # Show result message
            last_correct = model.last_trial_correct if hasattr(model, 'last_trial_correct') else False
            msg_color = success_color if last_correct else error_color
            result_text = "Correct!" if last_correct else "Incorrect"

            renderer.draw_text(
                self.screen_width // 2, instruction_y,
                result_text,
                font_size=24,
                color=(*msg_color, 255),
                align="center"
            )

            # Show continue button
            btn_width = 150
            btn_height = 40
            btn_x = (self.screen_width - btn_width) // 2
            btn_y = instruction_y + 50

            renderer.draw_rounded_rectangle(
                btn_x, btn_y, btn_width, btn_height,
                (*primary_color, 255),
                radius=5
            )
            renderer.draw_text(
                self.screen_width // 2, btn_y + btn_height // 2,
                "Continue",
                font_size=16,
                color=(255, 255, 255, 255),
                align="center",
                center_vertically=True
            )

        # Show any message from model
        if message:
            renderer.draw_text(
                self.screen_width // 2, self.screen_height - 40,
                message,
                font_size=14,
                color=(*text_color, 255),
                align="center"
            ) 