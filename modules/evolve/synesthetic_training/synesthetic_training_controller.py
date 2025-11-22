#!/usr/bin/env python3
"""
Synesthetic Training Controller Component

This module handles user interactions for the Synesthetic Training module:
- Mouse click processing and hit detection
- Action handling for associations
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


class SynestheticTrainingController:
    """Controller component for Synesthetic Training module - handles user interactions."""
    
    def __init__(self, model, view):
        """Initialize the controller with references to model and view.
        
        Args:
            model: Synesthetic Training Model instance
            view: Synesthetic Training View instance
        """
        self.model = model
        self.view = view
        
        # Interaction state
        self.selected_stimulus_index = None
        self.selected_response_index = None
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
        # Check if click is on a stimulus
        stimulus_index = self._get_stimulus_at_position(x, y)
        if stimulus_index is not None:
            self.selected_stimulus_index = stimulus_index
            
            # If a response is already selected, make the association
            if self.selected_response_index is not None:
                return self._make_association()
            
            return {
                "result": "select_stimulus",
                "stimulus_index": stimulus_index
            }
            
        # Check if click is on a response option
        response_index = self._get_response_at_position(x, y)
        if response_index is not None:
            self.selected_response_index = response_index
            
            # If a stimulus is already selected, make the association
            if self.selected_stimulus_index is not None:
                return self._make_association()
            
            return {
                "result": "select_response",
                "response_index": response_index
            }
        
        # Check if click is on the submit button
        if self._is_click_on_submit_button(x, y):
            return self._handle_action("submit", {})
        
        return {"result": "no_hit"}
    
    def _get_stimulus_at_position(self, x, y):
        """Get the index of a stimulus at the given position.
        
        Args:
            x: X coordinate
            y: Y coordinate
            
        Returns:
            Index of the stimulus or None if not found
        """
        # Calculate stimulus positions based on layout
        stimuli = self.model.current_stimuli
        num_items = len(stimuli)
        
        stimulus_x = self.view.screen_width // 4
        
        for i, _ in enumerate(stimuli):
            y_pos = 250 + i * (300 / max(1, num_items - 1)) if num_items > 1 else 300
            
            # Check if click is within the stimulus container
            if (abs(x - stimulus_x) <= 40 and abs(y - y_pos) <= 40):
                return i
        
        return None
    
    def _get_response_at_position(self, x, y):
        """Get the index of a response option at the given position.
        
        Args:
            x: X coordinate
            y: Y coordinate
            
        Returns:
            Index of the response or None if not found
        """
        # Calculate response positions based on layout
        associations = self.model.current_associations
        num_items = len(associations)
        
        response_x = 3 * self.view.screen_width // 4
        
        for i, _ in enumerate(associations):
            y_pos = 250 + i * (300 / max(1, num_items - 1)) if num_items > 1 else 300
            
            # Check if click is within the response container
            if (abs(x - response_x) <= 40 and abs(y - y_pos) <= 40):
                return i
        
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
    
    def _make_association(self):
        """Create an association between the selected stimulus and response.
        
        Returns:
            Dictionary containing the response
        """
        if self.selected_stimulus_index is None or self.selected_response_index is None:
            return {"result": "error", "reason": "no selection"}
        
        # Create association data
        data = {
            "stimulus_index": self.selected_stimulus_index,
            "response_index": self.selected_response_index
        }
        
        # Process the association action
        result = self.model.process_action("associate", data)
        
        # Reset selections
        self.selected_stimulus_index = None
        self.selected_response_index = None
        
        return result
    
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
        self.selected_stimulus_index = None
        self.selected_response_index = None
        self.last_action_time = 0
        
        # Reset model
        self.model.reset()
    
    def get_state(self):
        """Get the current state of the controller.
        
        Returns:
            Dictionary containing current state information
        """
        state = self.model.get_state()
        
        # Add controller-specific state
        if self.model.phase == "recall":
            state["selected_stimulus"] = self.selected_stimulus_index
            state["selected_response"] = self.selected_response_index
        
        return state 