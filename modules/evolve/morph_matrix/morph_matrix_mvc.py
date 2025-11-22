#!/usr/bin/env python3
"""
MorphMatrix Training Module with MVC Architecture

This module provides a pattern recognition game that challenges users to identify
rotated versions of a pattern versus modified versions. It implements the
Model-View-Controller architecture by integrating separate components.

Key features:
1. Clean separation of game logic from presentation
2. Theme-aware styling
3. Responsive grid layout
4. Optimized state management
"""

import sys
from pathlib import Path
from typing import Dict, Any, Optional

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
        class TrainingModule:
            def __init__(self): pass

# Import local MVC components
from modules.evolve.morph_matrix.morph_matrix_model import MorphMatrixModel
from modules.evolve.morph_matrix.morph_matrix_view import MorphMatrixView
from modules.evolve.morph_matrix.morph_matrix_controller import MorphMatrixController


class MorphMatrix(TrainingModule):
    """MorphMatrix training module with MVC architecture."""
    
    def __init__(self, difficulty=1):
        """Initialize the module.
        
        Args:
            difficulty: Initial difficulty level
        """
        super().__init__()
        
        # Module metadata
        self.name = "morph_matrix"
        self.display_name = "MorphMatrix"
        self.description = "Identify patterns that are exact rotations of the original pattern"
        
        # Screen dimensions from parent class
        self.screen_width = self.__class__.SCREEN_WIDTH
        self.screen_height = self.__class__.SCREEN_HEIGHT
        
        # Set up MVC components
        self.model = MorphMatrixModel(difficulty)
        self.view = MorphMatrixView(self.model)
        self.controller = MorphMatrixController(self.model, self.view)
        
        # Configure view
        self.view.set_dimensions(self.screen_width, self.screen_height)
        
        # Track properties for efficient delta generation
        self._tracked_properties = self._tracked_properties.union({
            'difficulty', 'level', 'matrix_size', 'game_state', 
            'clusters', 'original_matrix', 'selected_clusters',
            'answered', 'correct_answer', 'score', 'modified_indices',
            'selected_patterns', 'total_patterns'
        })
    
    @staticmethod
    def get_name():
        """Get the name of the module."""
        return "Morph Matrix"
    
    @staticmethod
    def get_description():
        """Get the description of the module."""
        return "Identify rotated vs. mutated patterns"
    
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
        
        # No time-based updates needed for MorphMatrix
        pass
    
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
        
        if action == "select_pattern":
            pattern_index = input_data.get("pattern_index", -1)
            self.model.toggle_pattern_selection(pattern_index)
            return {"result": "pattern_toggled", "pattern": pattern_index, "state": self.get_state()}
        
        elif action == "submit":
            is_correct, score_change = self.model.check_answers()
            return {"result": "answer_submitted", "correct": is_correct, "score_change": score_change, "state": self.get_state()}
        
        elif action == "next_round":
            self.model.start_next_round()
            self.view.calculate_layout()
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

    def render(self, renderer):
        """Render the module using the provided renderer.

        This method renders the module's UI using the renderer abstraction,
        delegating to the view for the actual drawing.

        Args:
            renderer: The renderer instance to use for drawing.
        """
        # Update view dimensions
        self.view.set_dimensions(self.screen_width, self.screen_height)

        # Render using the view
        self.view.render_to_renderer(renderer, self.model)