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

# Add the parent directory to sys.path for absolute imports when imported directly
if __name__ == "__main__" or not __package__:
    project_root = Path(__file__).parent.parent.parent.parent
    sys.path.insert(0, str(project_root))
    from MetaMindIQTrain.core.theme_manager import ThemeManager
else:
    # Use relative imports when imported as a module
    from ....core.theme_manager import ThemeManager


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