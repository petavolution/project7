#!/usr/bin/env python3
"""
Module Loading Tests for MetaMindIQTrain.

This module tests that all the core cognitive training modules
can be properly imported and instantiated.
"""

import os
import sys
import unittest
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parents[2]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Import the module registry and base class
from MetaMindIQTrain.core.training_module import TrainingModule
from MetaMindIQTrain.module_registry import get_available_modules, create_module_instance


class ModuleLoadingTests(unittest.TestCase):
    """Tests for loading and instantiating training modules."""
    
    def test_base_module_import(self):
        """Test that the base TrainingModule class can be imported."""
        self.assertIsNotNone(TrainingModule)
        
    def test_all_modules_available(self):
        """Test that the expected modules are available in the registry."""
        # Get the available modules
        modules = get_available_modules()
        
        # Check that the key modules are in the registry
        expected_modules = ['symbol_memory', 'morph_matrix', 'expand_vision', 'music_theory']
        for module_id in expected_modules:
            self.assertIn(module_id, modules.keys(), f"Module '{module_id}' not found in registry")
            
    def test_symbol_memory_instantiation(self):
        """Test that the SymbolMemory module can be instantiated."""
        module = create_module_instance('symbol_memory')
        self.assertIsNotNone(module, "Failed to instantiate SymbolMemory module")
        self.assertIsInstance(module, TrainingModule, "SymbolMemory module does not inherit from TrainingModule")
        
    def test_morph_matrix_instantiation(self):
        """Test that the MorphMatrix module can be instantiated."""
        module = create_module_instance('morph_matrix')
        self.assertIsNotNone(module, "Failed to instantiate MorphMatrix module")
        self.assertIsInstance(module, TrainingModule, "MorphMatrix module does not inherit from TrainingModule")
        
    def test_expand_vision_instantiation(self):
        """Test that the ExpandVision module can be instantiated."""
        module = create_module_instance('expand_vision')
        self.assertIsNotNone(module, "Failed to instantiate ExpandVision module")
        self.assertIsInstance(module, TrainingModule, "ExpandVision module does not inherit from TrainingModule")
        
    def test_music_theory_instantiation(self):
        """Test that the MusicTheory module can be instantiated."""
        module = create_module_instance('music_theory')
        self.assertIsNotNone(module, "Failed to instantiate MusicTheory module")
        self.assertIsInstance(module, TrainingModule, "MusicTheory module does not inherit from TrainingModule")


if __name__ == "__main__":
    unittest.main() 