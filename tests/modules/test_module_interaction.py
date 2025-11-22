#!/usr/bin/env python3
"""
Module Interaction Tests for MetaMindIQTrain.

This module tests that all the core cognitive training modules
can properly handle user interactions like clicks.
"""

import os
import sys
import unittest
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parents[2]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Import the module registry
from MetaMindIQTrain.module_registry import create_module_instance


class ModuleInteractionTests(unittest.TestCase):
    """Tests for module interactions like handling clicks."""
    
    def test_symbol_memory_click(self):
        """Test that the SymbolMemory module can handle clicks."""
        module = create_module_instance('symbol_memory')
        result = module.handle_click(400, 300)  # Click in the middle of the screen
        
        # Verify the click response has the expected structure
        self.assertIsInstance(result, dict, "Click handler should return a dictionary")
        self.assertIn('success', result, "Click result should have a 'success' key")
        
    def test_morph_matrix_click(self):
        """Test that the MorphMatrix module can handle clicks."""
        module = create_module_instance('morph_matrix')
        result = module.handle_click(400, 300)  # Click in the middle of the screen
        
        # Verify the click response has the expected structure
        self.assertIsInstance(result, dict, "Click handler should return a dictionary")
        
    def test_expand_vision_click(self):
        """Test that the ExpandVision module can handle clicks."""
        module = create_module_instance('expand_vision')
        result = module.handle_click(400, 300)  # Click in the middle of the screen
        
        # Verify the click response has the expected structure
        self.assertIsInstance(result, dict, "Click handler should return a dictionary")
        self.assertIn('success', result, "Click result should have a 'success' key")
        
    def test_module_state_retrieval(self):
        """Test that all modules can return their state."""
        for module_id in ['symbol_memory', 'morph_matrix', 'expand_vision']:
            module = create_module_instance(module_id)
            state = module.get_state()
            
            # Verify the state has the expected structure
            self.assertIsInstance(state, dict, f"{module_id} state should be a dictionary")
            self.assertIn('score', state, f"{module_id} state should have a 'score' key")
            self.assertIn('level', state, f"{module_id} state should have a 'level' key")


if __name__ == "__main__":
    unittest.main() 