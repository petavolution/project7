#!/usr/bin/env python3
"""
Neural Flow Controller Component

This module handles user interactions and game flow for the Neural Flow training module:
- Mouse click processing
- Phase transitions
- Game state updates
- User input validation
"""

import sys
import math
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional

# Add the parent directory to sys.path for absolute imports when imported directly
if __name__ == "__main__" or not __package__:
    project_root = Path(__file__).parent.parent.parent.parent
    sys.path.insert(0, str(project_root))
else:
    # Use relative imports when imported as a module
    pass


class NeuralFlowController:
    """Controller component for NeuralFlow module - handles user interactions and game flow."""
    
    def __init__(self, model, view):
        """Initialize the controller with references to model and view.
        
        Args:
            model: NeuralFlowModel instance
            view: NeuralFlowView instance
        """
        self.model = model
        self.view = view
        
        # Interaction state
        self.last_click_time = 0
        self.click_cooldown = 0.5  # Seconds between clicks
    
    def handle_click(self, pos: Tuple[int, int]) -> bool:
        """Process a mouse click at the given position.
        
        Args:
            pos: (x, y) coordinates of the click
            
        Returns:
            bool: True if click was processed, False otherwise
        """
        # Check if we're in the active phase
        if self.model.phase != self.model.PHASE_ACTIVE:
            return False
        
        # Check click cooldown
        current_time = self.model.get_state()["time"]
        if current_time - self.last_click_time < self.click_cooldown:
            return False
        
        # Process click
        success = self.model.process_click(pos)
        if success:
            self.last_click_time = current_time
            return True
        
        return False
    
    def update(self, delta_time: float):
        """Update the controller state.
        
        Args:
            delta_time: Time elapsed since last update
        """
        # Update model
        self.model.update(delta_time)
        
        # Check for phase transitions
        if self.model.phase == self.model.PHASE_ACTIVE:
            # Check if all nodes have been activated
            if self.model.targets_found >= len(self.model.target_nodes):
                self.model.phase = self.model.PHASE_FEEDBACK
                self.model.message = "Round complete! Preparing for next level..."
        elif self.model.phase == self.model.PHASE_FEEDBACK:
            # Check if feedback phase is complete
            if self.model.get_state()["time"] - self.model.last_phase_change > self.model.config["feedback_duration"]:
                self.model.start_new_round()
    
    def reset(self):
        """Reset the controller state."""
        self.last_click_time = 0
        self.model.reset()
    
    def get_state(self) -> Dict[str, Any]:
        """Get the current state of the controller.
        
        Returns:
            Dict containing current state information
        """
        return {
            "phase": self.model.phase,
            "score": self.model.score,
            "level": self.model.level,
            "targets_found": self.model.targets_found,
            "accuracy": self.model.accuracy,
            "time": self.model.get_state()["time"]
        } 