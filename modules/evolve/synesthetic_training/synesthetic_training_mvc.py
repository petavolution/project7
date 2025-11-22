#!/usr/bin/env python3
"""
Synesthetic Training MVC Module

This module integrates the Model, View, and Controller components for the 
Synesthetic Training module, which trains cross-modal sensory associations.
"""

import sys
import os
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional

# Ensure project root is in path for imports
_project_root = Path(__file__).resolve().parent.parent.parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

# Import BaseModule - try multiple approaches
try:
    from modules.base_module import BaseModule
except ImportError:
    try:
        from core.training_module import TrainingModule as BaseModule
    except ImportError:
        class BaseModule:
            def __init__(self, config=None): pass

# Import local MVC components
from modules.evolve.synesthetic_training.synesthetic_training_model import SynestheticTrainingModel
from modules.evolve.synesthetic_training.synesthetic_training_view import SynestheticTrainingView
from modules.evolve.synesthetic_training.synesthetic_training_controller import SynestheticTrainingController

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SynestheticTraining(BaseModule):
    """Main Synesthetic Training module that integrates MVC components."""
    
    def __init__(self, config=None):
        """Initialize Synesthetic Training module.
        
        Args:
            config: Optional configuration dictionary to override defaults
        """
        super().__init__(config)
        
        # Initialize MVC components
        self.model = SynestheticTrainingModel()
        self.view = SynestheticTrainingView(self.model)
        self.controller = SynestheticTrainingController(self.model, self.view)
        
        # Apply custom configuration if provided
        if config:
            self.configure(config)
            
        # Initialize the game
        self.init_game()
    
    def configure(self, config):
        """Configure the module with custom settings.
        
        Args:
            config: Configuration dictionary
        """
        # Apply configuration to model
        if hasattr(self.model, 'configure'):
            self.model.configure(config)
            
        # Apply view configuration if present
        if 'screen_width' in config and 'screen_height' in config:
            self.view.set_dimensions(config['screen_width'], config['screen_height'])
    
    def init_game(self):
        """Initialize the game state."""
        self.model.init_game()
        self.controller.reset()
    
    def get_component_tree(self):
        """Get the UI component tree.
        
        Returns:
            Dictionary containing the component tree
        """
        return self.view.build_component_tree()
    
    def update(self, delta_time):
        """Update the module state.
        
        Args:
            delta_time: Time delta in seconds
            
        Returns:
            Dictionary containing update status
        """
        # Update controller (which updates model)
        self.controller.update(delta_time)
        
        # Return current game state
        return self.get_state()
    
    def handle_input(self, input_data):
        """Handle user input.
        
        Args:
            input_data: Dictionary containing input data
            
        Returns:
            Dictionary containing the response
        """
        # Let controller handle input
        response = self.controller.handle_input(input_data)
        
        # Update component tree if state changed
        if response.get("result") != "ignored":
            # Return updated component tree
            response["component_tree"] = self.get_component_tree()
        
        return response
    
    def get_state(self):
        """Get the current state of the module.
        
        Returns:
            Dictionary containing current state information
        """
        return self.controller.get_state()
    
    def reset(self):
        """Reset the module state."""
        self.controller.reset()
    
    def get_default_config(self):
        """Get the default configuration.
        
        Returns:
            Dictionary containing default configuration
        """
        return self.model.get_default_config()
    
    @classmethod
    def get_module_name(cls):
        """Get the module name.
        
        Returns:
            String containing the module name
        """
        return "Synesthetic Training"
    
    @classmethod
    def get_module_description(cls):
        """Get the module description.
        
        Returns:
            String containing the module description
        """
        return (
            "Trains cross-modal sensory associations through pattern recognition "
            "between different sensory inputs (visual, auditory, spatial, numeric). "
            "Enhances perceptual binding and multisensory integration capabilities."
        )


# If run directly, create and run the module
if __name__ == "__main__":
    # Simple test
    module = SynestheticTraining()
    state = module.get_state()
    print(f"Module initialized with state: {state}")
    print(f"Component tree: {module.get_component_tree()}") 