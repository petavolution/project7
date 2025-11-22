#!/usr/bin/env python3
"""
ExpandVision Grid Training Module - MVC Implementation

This module implements the ExpandVision Grid cognitive training exercise using the 
Model-View-Controller (MVC) architecture. ExpandVision Grid trains peripheral vision 
and numerical processing by briefly displaying numbers in a circular pattern and
asking the user to calculate their sum.

KEY FEATURES:
- Clean separation of game logic (Model) from presentation (View) and user interaction (Controller)
- Theme-aware styling for consistent presentation across the platform
- Responsive layout that adapts to different screen sizes
- Configurable difficulty levels that adapt to user performance
- Optimized state management for efficient updates

This module serves as the entry point for the ExpandVision Grid training module, integrating
the Model, View, and Controller components.
"""

import sys
import time
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional

# Add the parent directory to sys.path for absolute imports
if __name__ == "__main__" or not __package__:
    project_root = Path(__file__).parent.parent.parent.parent
    sys.path.insert(0, str(project_root))
    from MetaMindIQTrain.core.training_module import TrainingModule
else:
    # Use relative imports when imported as a module
    from ....core.training_module import TrainingModule

from .expand_vision_grid_model import ExpandVisionGridModel
from .expand_vision_grid_view import ExpandVisionGridView
from .expand_vision_grid_controller import ExpandVisionGridController

class ExpandVisionGrid(TrainingModule):
    """ExpandVision Grid Training Module - Enhances peripheral vision and numerical processing.
    
    This class serves as the main entry point for the ExpandVision Grid training module.
    It initializes the MVC components, handles the game loop, and provides 
    the interface for interaction with the rest of the platform.
    """
    
    def __init__(self, screen_width: int = None, screen_height: int = None):
        """Initialize the ExpandVision Grid training module.
        
        Args:
            screen_width: Width of the screen in pixels (optional)
            screen_height: Height of the screen in pixels (optional)
        """
        super().__init__()
        
        # Module metadata
        self.name = "expand_vision_grid"
        self.display_name = "Expand Vision Grid"
        self.description = "Focus gaze on center and calculate sum of numbers"
        self.category = "Visual Processing"
        
        # Use provided dimensions or get from parent class
        if screen_width is None or screen_height is None:
            screen_width = self.__class__.SCREEN_WIDTH
            screen_height = self.__class__.SCREEN_HEIGHT
        
        # Initialize MVC components
        self.model = ExpandVisionGridModel(screen_width, screen_height)
        self.view = ExpandVisionGridView(self.model)
        self.controller = ExpandVisionGridController(self.model, self.view)
        
        # Game timer
        self.last_update_time = time.time()
        
        # Track properties for efficient delta generation
        self._tracked_properties = self._tracked_properties.union({
            'phase', 'preparation_complete', 'circle_width', 'circle_height',
            'numbers', 'current_sum', 'user_answer', 'show_numbers', 'round',
            'correct_answers', 'total_rounds', 'distance_factor_x', 'distance_factor_y'
        })
    
    @staticmethod
    def get_name():
        """Get the name of the module."""
        return "Expand Vision Grid"
    
    @staticmethod
    def get_description():
        """Get the description of the module."""
        return "Focus gaze on center and calculate sum of numbers"
    
    def handle_click(self, x: int, y: int) -> Dict[str, Any]:
        """Handle mouse click events.
        
        Args:
            x: X coordinate of click
            y: Y coordinate of click
            
        Returns:
            Result dictionary
        """
        return self.controller.handle_click(x, y)
    
    def update(self, dt: float) -> bool:
        """Update module state based on elapsed time.
        
        Args:
            dt: Time delta since last update in seconds
            
        Returns:
            True if the state changed and an update is needed
        """
        super().update(dt)
        
        current_time = time.time()
        delta_time = current_time - self.last_update_time
        self.last_update_time = current_time
        
        # Update controller with current time
        return self.controller.update(delta_time, current_time)
    
    def get_state(self) -> Dict[str, Any]:
        """Get the current module state.
        
        Returns:
            Dictionary with state information
        """
        # Start with base state
        state = super().get_state()
        
        # Add model state
        model_state = self.model.get_state()
        state.update(model_state)
        
        # Add module-specific properties
        state.update({
            "name": self.name,
            "display_name": self.display_name,
            "description": self.description,
            "category": self.category
        })
        
        return state
    
    def process_input_data(self, input_data: Dict[str, Any]) -> None:
        """Process input data for the module.
        
        Args:
            input_data: Dict containing input data
        """
        # Handle screen resize if dimensions are provided
        if "screen_width" in input_data and "screen_height" in input_data:
            screen_width = input_data["screen_width"]
            screen_height = input_data["screen_height"]
            
            # Update model and view dimensions
            self.model.screen_width = screen_width
            self.model.screen_height = screen_height
            self.view.update_dimensions(screen_width, screen_height)
    
    def process_input(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process input data.
        
        Args:
            input_data: Input data dictionary
            
        Returns:
            Result dictionary
        """
        action = input_data.get("action", "")
        
        if action == "select_answer":
            value = input_data.get("value")
            if value is not None:
                is_correct, score_change = self.model.process_answer(value)
                return {
                    "result": "answer_processed", 
                    "correct": is_correct, 
                    "score_change": score_change, 
                    "state": self.get_state()
                }
        
        elif action == "reset":
            self.model.reset()
            self.controller.reset()
            return {"result": "reset", "state": self.get_state()}
        
        # Default: no action
        return {"result": "no_action", "state": self.get_state()}
    
    def build_component_tree(self) -> Dict[str, Any]:
        """Build the UI component tree.
        
        Returns:
            Root component of the UI tree
        """
        return self.view.build_component_tree()
    
    def reset(self) -> None:
        """Reset the module for a new session."""
        self.model.reset()
        self.controller.reset()
        self.last_update_time = time.time()


if __name__ == "__main__":
    # For standalone testing (simulated environment)
    import pygame
    
    # Initialize pygame
    pygame.init()
    screen_width, screen_height = 800, 600
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("ExpandVision Grid Test")
    
    # Create module
    expand_vision_grid = ExpandVisionGrid(screen_width, screen_height)
    
    # Main loop
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                expand_vision_grid.handle_click(x, y)
        
        # Update module
        needs_update = expand_vision_grid.update(0.016)  # ~60fps
        
        # Only redraw if something changed
        if needs_update:
            # Clear screen
            screen.fill((15, 20, 30))  # Dark blue background
            
            # Get UI tree and render it (simplified for testing)
            ui_tree = expand_vision_grid.build_component_tree()
            # Actual rendering would be done by the UI system
            
            # Update display
            pygame.display.flip()
        
        # Cap frame rate
        pygame.time.delay(10)
    
    pygame.quit() 