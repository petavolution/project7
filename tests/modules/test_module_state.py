#!/usr/bin/env python3
"""
Module State Tests for MetaMindIQTrain.

This module tests state management and progression in the cognitive training modules.
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


class ModuleStateTests(unittest.TestCase):
    """Tests for module state management and progression."""
    
    def test_symbol_memory_state(self):
        """Test that the SymbolMemory module maintains proper state."""
        module = create_module_instance('symbol_memory')
        
        # Get initial state
        initial_state = module.get_state()
        
        # Verify initial state has expected properties
        self.assertEqual(initial_state['game_state'], 'memorize', "Initial state should be 'memorize'")
        self.assertEqual(initial_state['level'], 1, "Initial level should be 1")
        self.assertEqual(initial_state['score'], 0, "Initial score should be 0")
        
        # Process an input (simulate user response)
        result = module.process_input({"answer": "yes"})
        
        # Verify the state changes
        self.assertIn('state', result, "Result should include updated state")
    
    def test_morph_matrix_state(self):
        """Test that the MorphMatrix module maintains proper state."""
        module = create_module_instance('morph_matrix')
        
        # Get initial state
        initial_state = module.get_state()
        
        # Verify initial state has expected properties
        self.assertEqual(initial_state['level'], 1, "Initial level should be 1")
        self.assertEqual(initial_state['score'], 0, "Initial score should be 0")
        
        # Select a pattern
        cluster_index = 1  # Assuming there's at least one pattern besides the original
        module.select_pattern(cluster_index)
        
        # Get the updated state
        updated_state = module.get_state()
        
        # Verify the state reflects the selection
        self.assertIn(cluster_index, updated_state['selected_patterns'], 
                     "Selected pattern should be in selected_patterns list")
    
    def test_expand_vision_state(self):
        """Test that the ExpandVision module maintains proper state."""
        module = create_module_instance('expand_vision')
        
        # Get initial state
        initial_state = module.get_state()
        
        # Verify initial state has expected properties
        self.assertEqual(initial_state['level'], 1, "Initial level should be 1")
        self.assertEqual(initial_state['score'], 0, "Initial score should be 0")
        
        # Process an input (simulate user response)
        if initial_state['show_numbers']:
            # If numbers are showing, try to answer
            sum_value = sum(initial_state['numbers'])
            result = module.process_input({"sum": sum_value})
            
            # Verify the result
            self.assertIn('result', result, "Result should include 'result' field")
            self.assertEqual(result['result']['correct'], True, "Answer should be correct")
        else:
            # Skip the test if numbers aren't showing yet
            pass


if __name__ == "__main__":
    unittest.main() 