#!/usr/bin/env python3
"""
ExpandVision Controller - User interaction handling for the ExpandVision module

This module implements the Controller component in the MVC architecture for the
ExpandVision cognitive training exercise. It handles:
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

from .expand_vision_model import ExpandVisionModel
from .expand_vision_view import ExpandVisionView

class ExpandVisionController:
    """Controller component for ExpandVision module - handles user interaction."""
    
    def __init__(self, model: ExpandVisionModel, view: ExpandVisionView):
        """Initialize controller with references to model and view.
        
        Args:
            model: ExpandVisionModel instance
            view: ExpandVisionView instance
        """
        self.model = model
        self.view = view
        
        # Timestamp to track when phases started
        self.phase_start_time = time.time()
        
        # Flag to indicate if an update is needed
        self.update_needed = True
    
    def handle_click(self, x: int, y: int) -> bool:
        """Handle a mouse click event.
        
        Args:
            x: X-coordinate of click
            y: Y-coordinate of click
            
        Returns:
            True if the state changed and an update is needed
        """
        # Only process clicks in the answer phase
        if self.model.phase == self.model.PHASE_ANSWER:
            # Check if any answer button was clicked
            for button in self.view.answer_buttons:
                rect = button["rect"]
                if self._point_in_rect(x, y, rect):
                    # Process the answer
                    answer_value = button["value"]
                    correct = self.model.process_answer(answer_value)
                    self.update_needed = True
                    return True
        
        # No state change
        return False
    
    def update(self, delta_time: float) -> bool:
        """Update controller state, check for phase transitions.
        
        Args:
            delta_time: Time elapsed since last update in seconds
            
        Returns:
            True if the state changed and an update is needed
        """
        current_time = time.time()
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
        """Check if a point is within a rectangle.
        
        Args:
            x: X-coordinate of the point
            y: Y-coordinate of the point
            rect: Rectangle as (x, y, width, height)
            
        Returns:
            True if the point is within the rectangle
        """
        rx, ry, rw, rh = rect
        return (rx <= x <= rx + rw) and (ry <= y <= ry + rh)
    
    def reset(self):
        """Reset the controller state for a new session."""
        self.phase_start_time = time.time()
        self.update_needed = True 