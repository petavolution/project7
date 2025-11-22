#!/usr/bin/env python3
"""
Symbol Memory Controller Component

This module handles user interactions for the Symbol Memory training module:
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


class SymbolMemoryController:
    """Controller component for SymbolMemory module - handles user interaction."""
    
    def __init__(self, model, view):
        """Initialize the controller with references to model and view.
        
        Args:
            model: SymbolMemoryModel instance
            view: SymbolMemoryView instance
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
        if self.model.phase == self.model.PHASE_ANSWER:
            # Check for clicks on YES button
            yes_rect = self.view.button_rects["yes"]
            if self._is_point_in_rect(x, y, yes_rect):
                is_correct, score_change = self.model.process_answer(True)
                return {"result": "answer_processed", "correct": is_correct, "score_change": score_change, "state": self.model.get_state()}
            
            # Check for clicks on NO button
            no_rect = self.view.button_rects["no"]
            if self._is_point_in_rect(x, y, no_rect):
                is_correct, score_change = self.model.process_answer(False)
                return {"result": "answer_processed", "correct": is_correct, "score_change": score_change, "state": self.model.get_state()}
            
        elif self.model.phase == self.model.PHASE_FEEDBACK:
            # Check for clicks on CONTINUE button
            continue_rect = self.view.button_rects["continue"]
            if self._is_point_in_rect(x, y, continue_rect):
                self.model.start_next_round()
                self.view.calculate_layout()  # Recalculate layout for new grid size
                return {"result": "next_round", "state": self.model.get_state()}
        
        # Default: no action
        return {"result": "no_action", "state": self.model.get_state()}
    
    def update(self, dt, current_time):
        """Update controller state.
        
        Args:
            dt: Time delta in seconds
            current_time: Current time in seconds
            
        Returns:
            True if state changed, False otherwise
        """
        # Check for phase transitions
        phase_changed = self.model.update_phase(current_time)
        
        # If phase changed, recalculate layout if needed
        if phase_changed and (self.model.phase == self.model.PHASE_COMPARE or 
                             self.model.phase == self.model.PHASE_ANSWER):
            self.view.calculate_layout()
            
        return phase_changed
    
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