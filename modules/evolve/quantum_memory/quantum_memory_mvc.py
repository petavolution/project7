#!/usr/bin/env python3
"""
Quantum Memory MVC Module

This module integrates the Model, View, and Controller components for the
Quantum Memory module, which enhances working memory, cognitive flexibility,
and strategic thinking through quantum-inspired memory challenges.
"""

import sys
import logging
from pathlib import Path
from typing import Dict, Any

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
            SCREEN_WIDTH = 1024
            SCREEN_HEIGHT = 768
            def __init__(self): pass

# Import local MVC components
from modules.evolve.quantum_memory.quantum_memory_model import QuantumMemoryModel
from modules.evolve.quantum_memory.quantum_memory_view import QuantumMemoryView
from modules.evolve.quantum_memory.quantum_memory_controller import QuantumMemoryController

logger = logging.getLogger(__name__)


class QuantumMemory(TrainingModule):
    """Main Quantum Memory module that integrates MVC components."""

    def __init__(self, difficulty=1):
        """Initialize Quantum Memory module.

        Args:
            difficulty: Initial difficulty level
        """
        super().__init__()

        # Module metadata
        self.name = "quantum_memory"
        self.display_name = "Quantum Memory"
        self.description = "Quantum-inspired memory challenges for cognitive flexibility"
        self.category = "Advanced Memory"

        # Screen dimensions from parent class
        self.screen_width = self.__class__.SCREEN_WIDTH
        self.screen_height = self.__class__.SCREEN_HEIGHT

        # Initialize MVC components
        self.model = QuantumMemoryModel()
        self.view = QuantumMemoryView(self.model)
        self.controller = QuantumMemoryController(self.model, self.view)

        # Set view dimensions
        if hasattr(self.view, 'set_dimensions'):
            self.view.set_dimensions(self.screen_width, self.screen_height)

    def handle_click(self, pos):
        """Handle a mouse click event.

        Args:
            pos: (x, y) coordinates of click

        Returns:
            Result dictionary from controller
        """
        if hasattr(self.controller, 'handle_click'):
            return self.controller.handle_click(pos)
        elif hasattr(self.controller, 'handle_input'):
            return self.controller.handle_input({'type': 'click', 'pos': pos})
        return {}

    def update(self, delta_time):
        """Update the module state.

        Args:
            delta_time: Time delta in seconds
        """
        if hasattr(self.controller, 'update'):
            self.controller.update(delta_time)

    def render(self, renderer):
        """Render the module using the provided renderer.

        Args:
            renderer: Renderer instance
        """
        # Update view dimensions
        if hasattr(self.view, 'set_dimensions'):
            self.view.set_dimensions(self.screen_width, self.screen_height)

        # Render using the view's renderer abstraction
        if hasattr(self.view, 'render_to_renderer'):
            self.view.render_to_renderer(renderer, self.model)
        else:
            # Fallback to base class render
            super().render(renderer)

    def get_state(self) -> Dict[str, Any]:
        """Get the current state of the module.

        Returns:
            Dictionary containing current state information
        """
        if hasattr(self.controller, 'get_state'):
            return self.controller.get_state()
        return {'score': self.score, 'level': self.level}

    def reset(self):
        """Reset the module state."""
        super().reset()
        if hasattr(self.controller, 'reset'):
            self.controller.reset()

    def build_component_tree(self) -> Dict[str, Any]:
        """Build the UI component tree.

        Returns:
            Dictionary containing the component tree
        """
        if hasattr(self.view, 'build_component_tree'):
            return self.view.build_component_tree()
        return {} 