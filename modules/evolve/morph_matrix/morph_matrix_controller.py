#!/usr/bin/env python3
"""
MorphMatrix Controller Component

This module handles user interactions for the MorphMatrix training module:
- Click event handling
- Game state transitions
- User input processing
- Communication between model and view
"""

import sys
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional, Union

# Add the parent directory to sys.path for absolute imports when imported directly
if __name__ == "__main__" or not __package__:
    project_root = Path(__file__).parent.parent.parent.parent
    sys.path.insert(0, str(project_root))


class MorphMatrixController:
    """Controller component for MorphMatrix module - handles user interaction."""
    
    def __init__(self, model, view):
        """Initialize the controller with references to model and view.
        
        Args:
            model: MorphMatrixModel instance
            view: MorphMatrixView instance
        """
        self.model = model
        self.view = view
    
    def handle_click(self, x, y):
        """Handle mouse click event.
        
        Args:
            x: X coordinate of click
            y: Y coordinate of click
            
        Returns:
            Dictionary with result and updated state
        """
        if self.model.game_state == "challenge_active":
            # Check for pattern clicks
            pattern_index = self._get_clicked_pattern(x, y)
            if pattern_index >= 0:
                # Toggle pattern selection
                self.model.toggle_pattern_selection(pattern_index)
                return {"result": "pattern_toggled", "pattern": pattern_index, "state": self.model.get_state()}
            
            # Check for submit button
            submit_button_rect = self._get_submit_button_rect()
            if self._is_point_in_rect(x, y, submit_button_rect):
                # Check answers
                is_correct, score_change = self.model.check_answers()
                return {"result": "answer_submitted", "correct": is_correct, "score_change": score_change, "state": self.model.get_state()}
        
        elif self.model.game_state == "challenge_complete":
            # Check for next button
            next_button_rect = self._get_next_button_rect()
            if self._is_point_in_rect(x, y, next_button_rect):
                # Start next round
                self.model.start_next_round()
                # Recalculate view layout
                self.view.calculate_layout()
                return {"result": "next_round", "state": self.model.get_state()}
        
        # Default: no action
        return {"result": "no_action", "state": self.model.get_state()}
    
    def _get_clicked_pattern(self, x, y):
        """Get the index of the pattern clicked.
        
        Args:
            x: X coordinate of click
            y: Y coordinate of click
            
        Returns:
            Pattern index or -1 if no pattern was clicked
        """
        for rect in self.view.pattern_rects:
            rect_x, rect_y, rect_width, rect_height, pattern_index = rect
            if self._is_point_in_rect(x, y, (rect_x, rect_y, rect_width, rect_height)):
                return pattern_index
        
        return -1
    
    def _get_submit_button_rect(self):
        """Get the rect for the submit button.
        
        Returns:
            Tuple of (x, y, width, height)
        """
        x = (self.view.screen_width - 120) // 2
        y = self.view.screen_height - 45
        width = 120
        height = 40
        return (x, y, width, height)
    
    def _get_next_button_rect(self):
        """Get the rect for the next button.
        
        Returns:
            Tuple of (x, y, width, height)
        """
        x = (self.view.screen_width - 120) // 2
        y = self.view.screen_height - 45
        width = 120
        height = 40
        return (x, y, width, height)
    
    def _is_point_in_rect(self, x, y, rect):
        """Check if a point is inside a rectangle.
        
        Args:
            x: X coordinate of point
            y: Y coordinate of point
            rect: Tuple of (rect_x, rect_y, rect_width, rect_height)
            
        Returns:
            True if the point is inside the rectangle
        """
        rect_x, rect_y, rect_width, rect_height = rect
        return (rect_x <= x <= rect_x + rect_width and
                rect_y <= y <= rect_y + rect_height) 