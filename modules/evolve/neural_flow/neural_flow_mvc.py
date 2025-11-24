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

# Ensure project root is in path for imports
_project_root = Path(__file__).resolve().parent.parent.parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

# Import TrainingModule - try multiple approaches for robustness
try:
    from core.training_module import TrainingModule
except ImportError:
    try:
        from MetaMindIQTrain.core.training_module import TrainingModule
    except ImportError:
        # Minimal fallback
        class TrainingModule:
            SCREEN_WIDTH = 1024
            SCREEN_HEIGHT = 768
            def __init__(self): pass

# Import local MVC components
from modules.evolve.neural_flow.neural_flow_model import NeuralFlowModel
from modules.evolve.neural_flow.neural_flow_view import NeuralFlowView
from modules.evolve.neural_flow.neural_flow_controller import NeuralFlowController


class NeuralFlow(TrainingModule):
    """Main entry point for the Neural Flow training module."""

    def __init__(self, difficulty=1):
        """Initialize the Neural Flow module.

        Args:
            difficulty: Initial difficulty level
        """
        super().__init__()

        # Module metadata
        self.name = "neural_flow"
        self.display_name = "Neural Flow"
        self.description = "Train neural pathways through node connection exercises"
        self.category = "Evolve"

        # Screen dimensions from parent class
        self.screen_width = self.__class__.SCREEN_WIDTH
        self.screen_height = self.__class__.SCREEN_HEIGHT

        # Initialize MVC components
        self.model = NeuralFlowModel()
        self.model.screen_width = self.screen_width
        self.model.screen_height = self.screen_height
        self.view = NeuralFlowView(self.model)
        self.controller = NeuralFlowController(self.model, self.view)

        # Set initial dimensions
        self.view.set_dimensions(self.screen_width, self.screen_height)
    
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
        """Render the module using the provided renderer.

        Args:
            renderer: Renderer instance
        """
        # Update view dimensions
        self.view.set_dimensions(self.screen_width, self.screen_height)

        # Render using the view's renderer abstraction
        if hasattr(self.view, 'render_to_renderer'):
            self.view.render_to_renderer(renderer, self.model)
        else:
            # Fallback to base class render
            super().render(renderer) 