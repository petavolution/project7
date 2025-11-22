#!/usr/bin/env python3
"""
ExpandVision Grid Controller - User interaction handling for the ExpandVision Grid module

This module implements the Controller component in the MVC architecture for the
ExpandVision Grid cognitive training exercise. It handles:
- User input processing
- Game flow management
- State transitions between game phases
"""

import sys
import time
from pathlib import Path
from typing import Dict, Tuple, Any, Optional

# Add the parent directory to sys.path for absolute imports
if __name__ == "__main__" or not __package__:
    project_root = Path(__file__).parent.parent.parent.parent
    sys.path.insert(0, str(project_root))
else:
    # Use relative imports when imported as a module
    pass

from .expand_vision_grid_model import ExpandVisionGridModel
from .expand_vision_grid_view import ExpandVisionGridView

class ExpandVisionGridController:
    """Controller component for ExpandVision Grid module - handles user interaction."""
    
    def __init__(self, model: ExpandVisionGridModel, view: ExpandVisionGridView):
        """Initialize controller with references to model and view.
        
        Args:
            model: ExpandVisionGridModel instance
            view: ExpandVisionGridView instance
        """
        self.model = model
        self.view = view
        
        # Timestamp to track when phases started
        self.phase_start_time = time.time()
        
        # Flag to indicate if an update is needed
        self.update_needed = True
    
    def handle_click(self, x: int, y: int) -> Dict[str, Any]:
        """Handle mouse click event.
        
        Args:
            x: X coordinate of click
            y: Y coordinate of click
            
        Returns:
            Dictionary with result and updated state
        """
        # During the active phase with numbers shown, clicking anywhere brings up answer input
        if self.model.phase == self.model.PHASE_ACTIVE and self.model.show_numbers:
            self.model.phase = self.model.PHASE_ANSWER
            self.update_needed = True
            return {"result": "show_answer_input", "state": self.model.get_state()}
        
        # Check for clicks on answer buttons during answer phase
        if self.model.phase == self.model.PHASE_ANSWER:
            for button in self.view.answer_buttons:
                rect = button["rect"]
                if self._point_in_rect(x, y, rect):
                    is_correct, score_change = self.model.process_answer(button["value"])
                    self.update_needed = True
                    return {
                        "result": "answer_selected", 
                        "correct": is_correct,
                        "score_change": score_change,
                        "state": self.model.get_state()
                    }
        
        # Default: no action
        return {"result": "no_action", "state": self.model.get_state()}
    
    def update(self, delta_time: float, current_time: float) -> bool:
        """Update controller state, check for phase transitions.
        
        Args:
            delta_time: Time delta since last update in seconds
            current_time: Current time in seconds
            
        Returns:
            True if the state changed and an update is needed
        """
        # Calculate elapsed time since phase started
        elapsed = current_time - self.phase_start_time
        
        # Check if we need to transition to the next phase
        if self.model.update_phase(elapsed):
            # Phase changed, update the timestamp
            self.phase_start_time = current_time
            self.update_needed = True
            return True
        
        # Check if we have a pending update flag
        if self.update_needed:
            self.update_needed = False
            return True
        
        # No state change
        return False
    
    def _point_in_rect(self, x: int, y: int, rect: Tuple[int, int, int, int]) -> bool:
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
    
    def reset(self):
        """Reset the controller state for a new session."""
        self.phase_start_time = time.time()
        self.update_needed = True 