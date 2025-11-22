#!/usr/bin/env python3
"""
Neural Synthesis Controller Component

This module handles user interactions for the Neural Synthesis training module:
- Mouse click processing
- Phase transitions
- Game state updates
- User input validation
"""

import sys
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional

# Add the parent directory to sys.path for absolute imports when imported directly
if __name__ == "__main__" or not __package__:
    project_root = Path(__file__).parent.parent.parent.parent
    sys.path.insert(0, str(project_root))


class NeuralSynthesisController:
    """Controller component for Neural Synthesis module - handles user interactions."""
    
    def __init__(self, model, view):
        """Initialize the controller with references to model and view.
        
        Args:
            model: Neural Synthesis Model instance
            view: Neural Synthesis View instance
        """
        self.model = model
        self.view = view
        
        # Interaction state
        self.last_click_time = 0
        self.click_cooldown = 0.2  # Seconds between clicks
    
    def handle_click(self, pos):
        """Process a click at the given position.
        
        Args:
            pos: (x, y) coordinates of the click
            
        Returns:
            Dict with result information
        """
        x, y = pos
        # Pass click to model for processing
        result = self.model.process_click(x, y)
        return result
    
    def update(self, dt):
        """Update the controller state.
        
        Args:
            dt: Time delta in seconds
        """
        # Update model state
        self.model.update(dt)
    
    def reset(self):
        """Reset the controller state."""
        # Reset model
        self.model.reset()
    
    def get_state(self):
        """Get the current state of the controller.
        
        Returns:
            Dict containing current state information
        """
        return self.model.get_state() 