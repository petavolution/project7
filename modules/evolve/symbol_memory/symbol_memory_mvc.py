#!/usr/bin/env python3
"""
Symbol Memory Training Module with MVC Architecture

This module provides a memory challenge game that tests users' ability to
memorize symbol patterns and detect changes. It implements the Model-View-Controller
architecture by integrating separate components.

Key features:
1. Clean separation of game logic from presentation
2. Theme-aware styling
3. Responsive grid layout
4. Optimized state management
5. Multi-phase memory training
"""

import time
import sys
from pathlib import Path
from typing import Dict, Any, Optional

# Add the parent directory to sys.path for absolute imports when imported directly
if __name__ == "__main__" or not __package__:
    project_root = Path(__file__).parent.parent.parent.parent
    sys.path.insert(0, str(project_root))
    from MetaMindIQTrain.core.training_module import TrainingModule
    from MetaMindIQTrain.modules.evolve.symbol_memory.symbol_memory_model import SymbolMemoryModel
    from MetaMindIQTrain.modules.evolve.symbol_memory.symbol_memory_view import SymbolMemoryView
    from MetaMindIQTrain.modules.evolve.symbol_memory.symbol_memory_controller import SymbolMemoryController
else:
    # Use relative imports when imported as a module
    from ....core.training_module import TrainingModule
    from .symbol_memory_model import SymbolMemoryModel
    from .symbol_memory_view import SymbolMemoryView
    from .symbol_memory_controller import SymbolMemoryController


class SymbolMemory(TrainingModule):
    """SymbolMemory training module with MVC architecture."""
    
    def __init__(self, difficulty=1):
        """Initialize the module.
        
        Args:
            difficulty: Initial difficulty level
        """
        super().__init__()
        
        # Module metadata
        self.name = "symbol_memory"
        self.display_name = "Symbol Memory"
        self.description = "Memorize symbols in a grid and identify changes"
        self.category = "Memory"
        
        # Screen dimensions from parent class
        self.screen_width = self.__class__.SCREEN_WIDTH
        self.screen_height = self.__class__.SCREEN_HEIGHT
        
        # Set up MVC components
        self.model = SymbolMemoryModel(difficulty)
        self.view = SymbolMemoryView(self.model)
        self.controller = SymbolMemoryController(self.model, self.view)
        
        # Configure view
        self.view.set_dimensions(self.screen_width, self.screen_height)
        
        # Track properties for efficient delta generation
        self._tracked_properties = self._tracked_properties.union({
            'phase', 'game_state', 'current_grid_size', 'original_pattern',
            'modified_pattern', 'was_modified', 'user_answer', 'timer_active', 
            'memorize_duration', 'hidden_duration', 'user_answer', 'round_score'
        })
    
    @staticmethod
    def get_name():
        """Get the name of the module."""
        return "Symbol Memory"
    
    @staticmethod
    def get_description():
        """Get the description of the module."""
        return "Memorize symbols in a grid and identify changes"
    
    def handle_click(self, x, y):
        """Handle mouse click events.
        
        Args:
            x: X coordinate of click
            y: Y coordinate of click
            
        Returns:
            Result dictionary
        """
        return self.controller.handle_click(x, y)
    
    def update(self, dt):
        """Update module state based on elapsed time.
        
        Args:
            dt: Time delta since last update in seconds
        """
        super().update(dt)
        
        # Update controller with current time
        self.controller.update(dt, time.time())
    
    def get_state(self):
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
    
    def process_input(self, input_data):
        """Process input data.
        
        Args:
            input_data: Input data dictionary
            
        Returns:
            Result dictionary
        """
        action = input_data.get("action", "")
        
        if action == "answer_yes":
            is_correct, score_change = self.model.process_answer(True)
            return {"result": "answer_processed", "correct": is_correct, "score_change": score_change, "state": self.get_state()}
        
        elif action == "answer_no":
            is_correct, score_change = self.model.process_answer(False)
            return {"result": "answer_processed", "correct": is_correct, "score_change": score_change, "state": self.get_state()}
        
        elif action == "next_round":
            self.model.start_next_round()
            return {"result": "next_round", "state": self.get_state()}
        
        # Default: no action
        return {"result": "no_action", "state": self.get_state()}
    
    def build_ui(self):
        """Build the UI component tree.
        
        This is used by modern renderers that support component-based rendering.
        
        Returns:
            UI component tree specification
        """
        return self.view.build_component_tree() 