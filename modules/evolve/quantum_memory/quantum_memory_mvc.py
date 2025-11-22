#!/usr/bin/env python3
"""
Quantum Memory MVC Module

This module integrates the Model, View, and Controller components for the
Quantum Memory module, which enhances working memory, cognitive flexibility,
and strategic thinking through quantum-inspired memory challenges.
"""

import sys
import os
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional

# Add the parent directory to sys.path for absolute imports when imported directly
if __name__ == "__main__" or not __package__:
    project_root = Path(__file__).parent.parent.parent.parent
    sys.path.insert(0, str(project_root))

from MetaMindIQTrain.modules.base_module import BaseModule
from MetaMindIQTrain.modules.evolve.quantum_memory.quantum_memory_model import QuantumMemoryModel
from MetaMindIQTrain.modules.evolve.quantum_memory.quantum_memory_view import QuantumMemoryView
from MetaMindIQTrain.modules.evolve.quantum_memory.quantum_memory_controller import QuantumMemoryController

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class QuantumMemory(BaseModule):
    """Main Quantum Memory module that integrates MVC components."""
    
    def __init__(self, config=None):
        """Initialize Quantum Memory module.
        
        Args:
            config: Optional configuration dictionary to override defaults
        """
        super().__init__(config)
        
        # Initialize MVC components
        self.model = QuantumMemoryModel()
        self.view = QuantumMemoryView(self.model)
        self.controller = QuantumMemoryController(self.model, self.view)
        
        # Apply custom configuration if provided
        if config:
            self.configure(config)
    
    def configure(self, config):
        """Configure the module with custom settings.
        
        Args:
            config: Configuration dictionary
        """
        # Apply configuration to model
        if hasattr(self.model, 'config'):
            self.model.config.update(config)
            
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
        return "Quantum Memory"
    
    @classmethod
    def get_module_description(cls):
        """Get the module description.
        
        Returns:
            String containing the module description
        """
        return (
            "Enhance your working memory and cognitive flexibility through quantum-inspired "
            "challenges. Memorize quantum states that exist in superposition and make strategic "
            "choices to collapse them correctly. Boost your mental adaptability and processing power."
        )


# If run directly, create and run the module
if __name__ == "__main__":
    # Simple test
    module = QuantumMemory()
    state = module.get_state()
    print(f"Module initialized with state: {state}")
    print(f"Component tree: {module.get_component_tree()}") 