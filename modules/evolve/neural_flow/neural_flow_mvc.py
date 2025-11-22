#!/usr/bin/env python3
"""
Neural Flow MVC Module

This module integrates the Model, View, and Controller components for the Neural Flow training module:
- NeuralFlowModel: Core game logic and state management
- NeuralFlowView: UI representation and rendering
- NeuralFlowController: User interaction and game flow
"""

import sys
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional

# Add the parent directory to sys.path for absolute imports when imported directly
if __name__ == "__main__" or not __package__:
    project_root = Path(__file__).parent.parent.parent.parent
    sys.path.insert(0, str(project_root))
    from .neural_flow_model import NeuralFlowModel
    from .neural_flow_view import NeuralFlowView
    from .neural_flow_controller import NeuralFlowController
else:
    # Use relative imports when imported as a module
    from .neural_flow_model import NeuralFlowModel
    from .neural_flow_view import NeuralFlowView
    from .neural_flow_controller import NeuralFlowController


class NeuralFlow:
    """Main entry point for the Neural Flow training module."""
    
    def __init__(self, screen_width: int = 800, screen_height: int = 600):
        """Initialize the Neural Flow module.
        
        Args:
            screen_width: Width of the game screen
            screen_height: Height of the game screen
        """
        # Initialize MVC components
        self.model = NeuralFlowModel(screen_width, screen_height)
        self.view = NeuralFlowView(self.model)
        self.controller = NeuralFlowController(self.model, self.view)
        
        # Set initial dimensions
        self.view.set_dimensions(screen_width, screen_height)
    
    def handle_click(self, pos: Tuple[int, int]) -> bool:
        """Process a mouse click at the given position.
        
        Args:
            pos: (x, y) coordinates of the click
            
        Returns:
            bool: True if click was processed, False otherwise
        """
        return self.controller.handle_click(pos)
    
    def update(self, delta_time: float):
        """Update the module state.
        
        Args:
            delta_time: Time elapsed since last update
        """
        self.controller.update(delta_time)
    
    def reset(self):
        """Reset the module for a new session."""
        self.controller.reset()
    
    def get_state(self) -> Dict[str, Any]:
        """Get the current state of the module.
        
        Returns:
            Dict containing current state information
        """
        return self.controller.get_state()
    
    def process_input_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process input data for the module.
        
        Args:
            data: Input data dictionary
            
        Returns:
            Dict containing processed data
        """
        # Extract relevant data
        screen_width = data.get("screen_width", 800)
        screen_height = data.get("screen_height", 600)
        
        # Update view dimensions if needed
        if screen_width != self.view.screen_width or screen_height != self.view.screen_height:
            self.view.set_dimensions(screen_width, screen_height)
        
        return {
            "screen_width": screen_width,
            "screen_height": screen_height
        }
    
    def build_component_tree(self) -> Dict[str, Any]:
        """Build the UI component tree.
        
        Returns:
            Root component of the UI tree
        """
        return self.view.build_component_tree()
    
    def render(self, renderer):
        """Render the module.
        
        Args:
            renderer: UIRenderer instance
        """
        self.view.render(renderer)
        self.view.render_status(renderer) 