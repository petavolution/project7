#!/usr/bin/env python3
"""
ExpandVision Training Module - MVC Implementation

This module implements the ExpandVision cognitive training exercise using the 
Model-View-Controller (MVC) architecture. ExpandVision trains peripheral vision 
and numerical processing by briefly displaying numbers in a circular pattern and
asking the user to calculate their sum.

KEY FEATURES:
- Clean separation of game logic (Model) from presentation (View) and user interaction (Controller)
- Theme-aware styling for consistent presentation across the platform
- Responsive layout that adapts to different screen sizes
- Configurable difficulty levels that adapt to user performance
- Optimized state management for efficient updates

This module serves as the entry point for the ExpandVision training module, integrating
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

from .expand_vision_model import ExpandVisionModel
from .expand_vision_view import ExpandVisionView
from .expand_vision_controller import ExpandVisionController

class ExpandVision(TrainingModule):
    """ExpandVision Training Module - Enhances peripheral vision and numerical processing.
    
    This class serves as the main entry point for the ExpandVision training module.
    It initializes the MVC components, handles the game loop, and provides 
    the interface for interaction with the rest of the platform.
    """
    
    def __init__(self, screen_width: int, screen_height: int):
        """Initialize the ExpandVision training module.
        
        Args:
            screen_width: Width of the screen in pixels
            screen_height: Height of the screen in pixels
        """
        super().__init__()
        
        # Initialize MVC components
        self.model = ExpandVisionModel(screen_width, screen_height)
        self.view = ExpandVisionView(self.model)
        self.controller = ExpandVisionController(self.model, self.view)
        
        # Game timer
        self.last_update_time = time.time()
    
    def handle_click(self, x: int, y: int) -> bool:
        """Handle a mouse click event.
        
        Args:
            x: X-coordinate of click
            y: Y-coordinate of click
            
        Returns:
            True if the state changed and an update is needed
        """
        return self.controller.handle_click(x, y)
    
    def update(self) -> bool:
        """Update the module state.
        
        Returns:
            True if the state changed and an update is needed
        """
        current_time = time.time()
        delta_time = current_time - self.last_update_time
        self.last_update_time = current_time
        
        # Update controller and check if state changed
        return self.controller.update(delta_time)
    
    def get_state(self) -> Dict[str, Any]:
        """Get the current state of the module.
        
        Returns:
            Dict containing the current state
        """
        return self.model.get_state()
    
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
    pygame.display.set_caption("ExpandVision Test")
    
    # Create module
    expand_vision = ExpandVision(screen_width, screen_height)
    
    # Main loop
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                expand_vision.handle_click(x, y)
        
        # Update module
        needs_update = expand_vision.update()
        
        # Only redraw if something changed
        if needs_update:
            # Clear screen
            screen.fill((15, 20, 30))  # Dark blue background
            
            # Get UI tree and render it (simplified for testing)
            ui_tree = expand_vision.build_component_tree()
            # Actual rendering would be done by the UI system
            
            # Update display
            pygame.display.flip()
        
        # Cap frame rate
        pygame.time.delay(10)
    
    pygame.quit() 