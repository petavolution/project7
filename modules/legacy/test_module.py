#!/usr/bin/env python3
"""
Test training module

This module provides a simple test training module for the MetaMindIQTrain platform.
It displays a blue rectangle with text that the user can click on.
"""

import sys
import random
import time
from pathlib import Path

# Add the parent directory to sys.path for absolute imports when imported directly
if __name__ == "__main__" or not __package__:
    project_root = Path(__file__).parent.parent.parent
    sys.path.insert(0, str(project_root))
    from MetaMindIQTrain.core.training_module import TrainingModule
else:
    # Use relative imports when imported as a module
    from ..core.training_module import TrainingModule


class TestTrainingModule(TrainingModule):
    """
    A simple test training module.
    
    This module displays a blue rectangle with text that the user can click on.
    It's used for testing the platform and as a simple example.
    """
    
    def __init__(self):
        """Initialize the test training module."""
        super().__init__()
        
        # Module metadata
        self.name = "Test Module"
        self.description = "A simple test module that displays a blue rectangle with text."
        
        # Game state
        self.score = 0
        self.level = 1
        self.rectangle_x = 362
        self.rectangle_y = 309
        self.rectangle_width = 300
        self.rectangle_height = 150
        self.rectangle_color = (0, 0, 255)  # Blue
        self.text = "Click Me!"
        self.text_offset = 0
        self.message = "Click on the blue rectangle"
        
        # Game logic
        self.clicks = 0
        self.last_click_time = 0
        self.move_after_clicks = 3
    
    @staticmethod
    def get_name():
        """Get the name of the module."""
        return "Test Module"
    
    @staticmethod
    def get_description():
        """Get the description of the module."""
        return "A simple test module that displays a blue rectangle with text."
    
    def handle_click(self, x, y):
        """
        Handle a click event.
        
        Args:
            x: The x-coordinate of the click.
            y: The y-coordinate of the click.
            
        Returns:
            dict: A dictionary containing the result of the click.
        """
        # Check if click is within rectangle
        is_hit = (
            self.rectangle_x <= x <= self.rectangle_x + self.rectangle_width and
            self.rectangle_y <= y <= self.rectangle_y + self.rectangle_height
        )
        
        current_time = time.time()
        time_since_last_click = current_time - self.last_click_time
        self.last_click_time = current_time
        
        if is_hit:
            # Increment clicks
            self.clicks += 1
            
            # Calculate points based on speed
            points = 10
            if time_since_last_click < 1.0:
                speed_bonus = int((1.0 - time_since_last_click) * 10)
                points += speed_bonus
            
            # Update score
            self.score += points
            
            # Update message
            self.message = f"Great job! +{points} points"
            
            # Check if we should move the rectangle
            if self.clicks % self.move_after_clicks == 0:
                self._move_rectangle()
                self.level += 1
                self.message = f"Level {self.level}! Find the new rectangle"
            
            return {
                "success": True,
                "message": self.message,
                "points": points
            }
        else:
            # Miss
            self.message = "Missed! Try again."
            
            return {
                "success": False,
                "message": self.message,
                "points": 0
            }
    
    def _move_rectangle(self):
        """Move the rectangle to a new random position."""
        # Use the screen dimensions from the base class
        # (which are set by TrainingModule.configure_display)
        max_x = self.screen_width - self.rectangle_width
        max_y = self.screen_height - self.rectangle_height
        
        # Keep the rectangle within the visible area (accounting for margins)
        margin = int(min(self.screen_width, self.screen_height) * 0.05)  # 5% margin
        self.rectangle_x = random.randint(margin, max_x - margin)
        self.rectangle_y = random.randint(margin, max_y - margin)
        
        # Change color
        r = random.randint(0, 255)
        g = random.randint(0, 255)
        b = random.randint(0, 255)
        self.rectangle_color = (r, g, b)
        
        # Change text
        texts = ["Click Me!", "Focus!", "Concentrate", "Be Quick!", "Find Me!"]
        self.text = random.choice(texts)
        
        # Change text offset
        self.text_offset = random.randint(-20, 20)
    
    def get_state(self):
        """
        Get the current state of the module.
        
        Returns:
            dict: A dictionary containing the current state.
        """
        # Prepare UI components for the enhanced generic renderer
        ui_components = [
            {
                "type": "rectangle",
                "position": [self.rectangle_x, self.rectangle_y],
                "size": [self.rectangle_width, self.rectangle_height],
                "color": self.rectangle_color,
                "filled": True
            },
            {
                "type": "text",
                "text": self.text,
                "position": [
                    self.rectangle_x + self.rectangle_width // 2,
                    self.rectangle_y + self.rectangle_height // 2 + self.text_offset
                ],
                "font_size": 24,
                "color": [255, 255, 255] if sum(self.rectangle_color) < 380 else [0, 0, 0],
                "align": "center"
            },
            {
                "type": "text",
                "text": self.message,
                "position": [512, 700],
                "font_size": 20,
                "color": [0, 0, 0],
                "align": "center"
            }
        ]
        
        return {
            "module_id": "test_module",
            "module_name": self.name,
            "score": self.score,
            "level": self.level,
            "message": self.message,
            "rectangle_x": self.rectangle_x,
            "rectangle_y": self.rectangle_y,
            "rectangle_width": self.rectangle_width,
            "rectangle_height": self.rectangle_height,
            "rectangle_color": self.rectangle_color,
            "text": self.text,
            "text_offset": self.text_offset,
            "ui_components": ui_components
        } 