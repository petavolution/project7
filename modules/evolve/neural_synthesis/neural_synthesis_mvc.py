#!/usr/bin/env python3
"""
Neural Synthesis MVC Module

This module integrates the Model, View, and Controller components for the Neural Synthesis training module:
- NeuralSynthesisModel: Core game logic and state management
- NeuralSynthesisView: UI representation and rendering
- NeuralSynthesisController: User interaction and game flow

Neural Synthesis is a multi-modal cognitive training module that integrates auditory and visual
pattern recognition to enhance neural plasticity, cross-modal integration, and creative thinking.
"""

import sys
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional

# Ensure project root is in path for imports
_project_root = Path(__file__).resolve().parent.parent.parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

# Import local MVC components
from modules.evolve.neural_synthesis.neural_synthesis_model import NeuralSynthesisModel
from modules.evolve.neural_synthesis.neural_synthesis_view import NeuralSynthesisView
from modules.evolve.neural_synthesis.neural_synthesis_controller import NeuralSynthesisController


class NeuralSynthesis:
    """Main entry point for the Neural Synthesis training module."""
    
    def __init__(self, screen_width=800, screen_height=600):
        """Initialize the Neural Synthesis module.
        
        Args:
            screen_width: Width of the game screen
            screen_height: Height of the game screen
        """
        # Initialize MVC components
        self.model = NeuralSynthesisModel(screen_width, screen_height)
        self.view = NeuralSynthesisView(self.model)
        self.controller = NeuralSynthesisController(self.model, self.view)
        
        # Set initial dimensions
        self.view.set_dimensions(screen_width, screen_height)
    
    def handle_click(self, pos):
        """Process a mouse click at the given position.
        
        Args:
            pos: (x, y) coordinates of the click
            
        Returns:
            Dict with result information
        """
        return self.controller.handle_click(pos)
    
    def update(self, dt):
        """Update the module state.
        
        Args:
            dt: Time delta in seconds.
        """
        self.controller.update(dt)
    
    def reset(self):
        """Reset the module for a new session."""
        self.controller.reset()
    
    def get_state(self):
        """Get the current state of the module.
        
        Returns:
            Dict containing current state information
        """
        return self.controller.get_state()
    
    def process_input_data(self, data):
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
    
    def build_component_tree(self):
        """Build the UI component tree.
        
        Returns:
            Dict containing the UI component tree
        """
        return self.view.build_component_tree()
    
    def render(self, renderer):
        """Render the module using the provided renderer.
        
        Args:
            renderer: Renderer instance
        """
        self.view.render(renderer) 