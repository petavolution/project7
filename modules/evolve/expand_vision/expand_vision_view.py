#!/usr/bin/env python3
"""
ExpandVision View - UI rendering component for the ExpandVision module

This module implements the View component in the MVC architecture for the
ExpandVision cognitive training exercise. It handles:
- UI component building and rendering
- Layout calculations for responsive UI
- Theme-aware styling
- Answer button positioning
"""

import sys
from pathlib import Path
from typing import List, Dict, Tuple, Any, Optional, Union, Set

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

from modules.evolve.expand_vision.expand_vision_model import ExpandVisionModel

class ExpandVisionView:
    """View component for ExpandVision module - handles UI representation."""
    
    def __init__(self, model: ExpandVisionModel):
        """Initialize the view with reference to the model.
        
        Args:
            model: ExpandVisionModel instance
        """
        self.model = model
        self.screen_width = model.screen_width
        self.screen_height = model.screen_height
        
        # Precompute some dimensions for layout
        self.center_x = self.screen_width // 2
        self.center_y = self.screen_height // 2
        
        # Button dimensions as percentage of screen
        self.button_height = int(self.screen_height * 0.06)  # 6% of screen height
        self.button_width = int(self.screen_width * 0.08)    # 8% of screen width
        self.button_spacing = int(self.screen_width * 0.02)  # 2% of screen width
        
        # Calculate positions for answer buttons
        self.answer_buttons = self._calculate_answer_button_positions()
        
        # Styling
        self.number_colors = [
            ThemeManager.get_color("number_top", "#DCDCDC"),     # Top
            ThemeManager.get_color("number_right", "#FFFF78"),   # Right
            ThemeManager.get_color("number_bottom", "#78FF78"),  # Bottom
            ThemeManager.get_color("number_left", "#7878FF")     # Left
        ]
    
    def _calculate_answer_button_positions(self):
        """Calculate positions for answer buttons.
        
        Returns:
            List of button rectangles
        """
        # Define the possible answers (correct sum +/- offsets)
        possible_answers = [
            self.model.current_sum - 2,
            self.model.current_sum - 1,
            self.model.current_sum,
            self.model.current_sum + 1,
            self.model.current_sum + 2
        ]
        
        # Calculate total width of all buttons with spacing
        total_width = 5 * self.button_width + 4 * self.button_spacing
        start_x = (self.screen_width - total_width) // 2
        button_y = self.center_y + int(self.screen_height * 0.05)  # Slightly below center
        
        # Create button rectangles and store with their values
        buttons = []
        for i, value in enumerate(possible_answers):
            btn_x = start_x + i * (self.button_width + self.button_spacing)
            buttons.append({
                "rect": (btn_x, button_y, self.button_width, self.button_height),
                "value": value
            })
        
        return buttons
    
    def update_dimensions(self, screen_width, screen_height):
        """Update dimensions when screen size changes.
        
        Args:
            screen_width: New screen width
            screen_height: New screen height
        """
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Update center position
        self.center_x = screen_width // 2
        self.center_y = screen_height // 2
        
        # Update button dimensions
        self.button_height = int(screen_height * 0.06)
        self.button_width = int(screen_width * 0.08)
        self.button_spacing = int(screen_width * 0.02)
        
        # Recalculate button positions
        self.answer_buttons = self._calculate_answer_button_positions()
    
    def build_component_tree(self):
        """Build a component tree for rendering.
        
        Returns:
            Root component of the UI tree
        """
        # Root container
        root = {
            "type": "container",
            "id": "expand_vision_root",
            "width": self.screen_width,
            "height": self.screen_height,
            "properties": {
                "style": {
                    "backgroundColor": ThemeManager.get_color("vision_bg", "#0F141E")
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
                            "text": "Expand Vision",
                            "properties": {
                                "style": {
                                    "color": ThemeManager.get_color("text_color"),
                                    "fontSize": 18
                                }
                            }
                        },
                        # Score and round
                        {
                            "type": "text",
                            "id": "score",
                            "x": self.screen_width - 200,
                            "y": 10,
                            "width": 180,
                            "height": 30,
                            "text": f"Score: {self.model.score} | Round: {self.model.round}/{self.model.total_rounds}",
                            "properties": {
                                "style": {
                                    "color": ThemeManager.get_color("text_color"),
                                    "textAlign": "right",
                                    "fontSize": 16
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
                            "color": ThemeManager.get_color("preparation_text", "#B4DCFA"),
                            "textAlign": "center"
                        }
                    }
                },
                
                # Main game area with circle and numbers
                self._build_game_area(),
                
                # Answer buttons (only in answer phase)
                self._build_answer_buttons()
            ]
        }
        
        return root
    
    def _build_game_area(self):
        """Build the main game area with circle and numbers.
        
        Returns:
            Container component for the game area
        """
        # Container for the game area
        game_area = {
            "type": "container",
            "id": "game_area",
            "x": 0,
            "y": 100,
            "width": self.screen_width,
            "height": self.screen_height - 150,
            "children": [
                # Central circle
                {
                    "type": "circle",
                    "id": "central_circle",
                    "x": self.center_x,
                    "y": self.center_y,
                    "radius": self.model.circle_width // 2,
                    "properties": {
                        "style": {
                            "fillColor": ThemeManager.get_color(
                                "vision_circle_active" if self.model.phase == self.model.PHASE_ACTIVE else "vision_circle", 
                                "#0078FF"
                            )
                        }
                    }
                },
                
                # Focus point (small red dot in center)
                {
                    "type": "circle",
                    "id": "focus_point",
                    "x": self.center_x,
                    "y": self.center_y,
                    "radius": 2,
                    "properties": {
                        "style": {
                            "fillColor": ThemeManager.get_color("focus_point", "#FF0000")
                        }
                    }
                }
            ]
        }
        
        # Add peripheral numbers if they should be shown
        if self.model.show_numbers and self.model.phase == self.model.PHASE_ACTIVE:
            number_positions = self.model.calculate_number_positions()
            
            for i, (x, y, number) in enumerate(number_positions):
                number_comp = {
                    "type": "text",
                    "id": f"number_{i}",
                    "x": x - 15,  # Offset for centering
                    "y": y - 15,  # Offset for centering
                    "width": 30,
                    "height": 30,
                    "text": str(number),
                    "properties": {
                        "style": {
                            "color": self.number_colors[i],
                            "fontSize": 22,
                            "textAlign": "center"
                        }
                    }
                }
                
                game_area["children"].append(number_comp)
        
        return game_area
    
    def _build_answer_buttons(self):
        """Build answer buttons when in answer phase.
        
        Returns:
            Container component for answer buttons
        """
        if self.model.phase != self.model.PHASE_ANSWER:
            # Return empty container if not in answer phase
            return {
                "type": "container",
                "id": "empty_answer_container",
                "x": 0,
                "y": 0,
                "width": 0,
                "height": 0
            }
        
        # Update button positions with current sum
        self.answer_buttons = self._calculate_answer_button_positions()
        
        # Container for answer buttons
        answer_container = {
            "type": "container",
            "id": "answer_container",
            "x": 0,
            "y": self.center_y + int(self.screen_height * 0.05) - 10,
            "width": self.screen_width,
            "height": self.button_height + 20,
            "children": []
        }
        
        # Add each answer button
        for i, button in enumerate(self.answer_buttons):
            rect = button["rect"]
            answer_btn = {
                "type": "button",
                "id": f"answer_button_{i}",
                "x": rect[0],
                "y": rect[1],
                "width": rect[2],
                "height": rect[3],
                "text": str(button["value"]),
                "properties": {
                    "style": {
                        "backgroundColor": ThemeManager.get_color("primary_color"),
                        "color": ThemeManager.get_color("text_color"),
                        "borderRadius": 5
                    },
                    "value": button["value"]
                }
            }
            answer_container["children"].append(answer_btn)
        
        return answer_container 