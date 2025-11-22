#!/usr/bin/env python3
"""
Quantum Memory Controller Component

This module handles user interactions for the Quantum Memory module:
- Input processing
- Click detection
- Action handling
- State updates
"""

import sys
import math
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional

# Add the parent directory to sys.path for absolute imports when imported directly
if __name__ == "__main__" or not __package__:
    project_root = Path(__file__).parent.parent.parent.parent
    sys.path.insert(0, str(project_root))


class QuantumMemoryController:
    """Controller component for Quantum Memory module - handles user interactions."""
    
    def __init__(self, model, view):
        """Initialize the controller with references to model and view.
        
        Args:
            model: Quantum Memory Model instance
            view: Quantum Memory View instance
        """
        self.model = model
        self.view = view
        
        # Interaction state
        self.last_action_time = 0
        self.action_cooldown = 0.2  # Seconds between actions
    
    def handle_input(self, input_data):
        """Handle user input.
        
        Args:
            input_data: Dictionary containing input data
            
        Returns:
            Dictionary containing the response
        """
        # Only process inputs in recall phase
        if self.model.phase != "recall":
            return {"result": "ignored", "reason": f"not in recall phase (current: {self.model.phase})"}
        
        # Get input type
        input_type = input_data.get("type")
        
        # Handle click input
        if input_type == "click":
            x = input_data.get("x", 0)
            y = input_data.get("y", 0)
            
            return self._handle_click(x, y)
        
        # Handle action input
        elif input_type == "action":
            action = input_data.get("action")
            data = input_data.get("data", {})
            
            return self._handle_action(action, data)
        
        # Unknown input type
        return {"result": "error", "reason": "unknown input type"}
    
    def _handle_click(self, x, y):
        """Handle mouse click input.
        
        Args:
            x: X coordinate of the click
            y: Y coordinate of the click
            
        Returns:
            Dictionary containing the response
        """
        # Check if click is on a quantum state
        state_id = self._get_state_at_position(x, y)
        if state_id is not None:
            # Toggle the state selection
            return self.model.toggle_state_selection(state_id)
        
        # Check if click is on the submit button
        if self._is_click_on_submit_button(x, y):
            return self._handle_action("submit", {})
        
        return {"result": "no_hit"}
    
    def _get_state_at_position(self, x, y):
        """Get the ID of a quantum state at the given position.
        
        Args:
            x: X coordinate
            y: Y coordinate
            
        Returns:
            ID of the quantum state or None if not found
        """
        # Check all quantum states
        quantum_states = self.model.get_visible_quantum_states()
        for state in quantum_states:
            # Only interactable states
            if state["type"] == "collapsed":
                continue
                
            pos_x, pos_y = state["position"]
            # Use a radius check (35px is half the cell width)
            dist = math.sqrt((pos_x - x) ** 2 + (pos_y - y) ** 2)
            
            if dist <= 35:
                return state["id"]
        
        return None
    
    def _is_click_on_submit_button(self, x, y):
        """Check if click is on the submit button.
        
        Args:
            x: X coordinate
            y: Y coordinate
            
        Returns:
            True if click is on submit button, False otherwise
        """
        button_x = self.view.screen_width // 2
        button_y = self.view.screen_height - 80
        button_width = 100
        button_height = 40
        
        return (abs(x - button_x) <= button_width // 2 and 
                abs(y - button_y) <= button_height // 2)
    
    def _handle_action(self, action, data):
        """Handle action input.
        
        Args:
            action: Action to perform
            data: Additional data for the action
            
        Returns:
            Dictionary containing the response
        """
        return self.model.process_action(action, data)
    
    def update(self, delta_time):
        """Update the controller state.
        
        Args:
            delta_time: Time delta in seconds
        """
        # Update model state
        self.model.update(delta_time)
    
    def reset(self):
        """Reset the controller state."""
        self.last_action_time = 0
        
        # Reset model
        self.model.reset()
    
    def get_state(self):
        """Get the current state of the controller and model.
        
        Returns:
            Dictionary containing current state information
        """
        return self.model.get_state() 