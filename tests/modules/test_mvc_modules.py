#!/usr/bin/env python3
"""
MVC Module Tests for MetaMindIQTrain.

This module tests that all MVC-based cognitive training modules
can be properly imported, instantiated, and run their basic functionality.
"""

import os
import sys
import unittest
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parents[2]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Try to import pygame without initializing it
os.environ["SDL_VIDEODRIVER"] = "dummy"

# Import the MVC modules
try:
    from MetaMindIQTrain.modules.symbol_memory_mvc import SymbolMemory as SymbolMemoryMVC
    from MetaMindIQTrain.modules.morph_matrix_mvc import MorphMatrix as MorphMatrixMVC
    from MetaMindIQTrain.modules.expand_vision_Grid_mvc import ExpandVision as ExpandVisionMVC
except ImportError as e:
    print(f"Error importing MVC modules: {e}")
    raise


class MVCModuleTests(unittest.TestCase):
    """Tests for loading and instantiating MVC-based training modules."""
    
    def test_symbol_memory_mvc_import(self):
        """Test that the SymbolMemory MVC module can be imported."""
        self.assertIsNotNone(SymbolMemoryMVC)
        
    def test_morph_matrix_mvc_import(self):
        """Test that the MorphMatrix MVC module can be imported."""
        self.assertIsNotNone(MorphMatrixMVC)
        
    def test_expand_vision_mvc_import(self):
        """Test that the ExpandVision MVC module can be imported."""
        self.assertIsNotNone(ExpandVisionMVC)
        
    def test_symbol_memory_mvc_instantiation(self):
        """Test that the SymbolMemory MVC module can be instantiated."""
        try:
            module = SymbolMemoryMVC(difficulty=1)
            self.assertIsNotNone(module, "Failed to instantiate SymbolMemory MVC module")
            # Check that the module has the required components
            self.assertIsNotNone(module.model, "SymbolMemory MVC module missing model component")
            self.assertIsNotNone(module.view, "SymbolMemory MVC module missing view component")
            self.assertIsNotNone(module.controller, "SymbolMemory MVC module missing controller component")
        except Exception as e:
            self.fail(f"SymbolMemory MVC instantiation failed with error: {e}")
        
    def test_morph_matrix_mvc_instantiation(self):
        """Test that the MorphMatrix MVC module can be instantiated."""
        try:
            module = MorphMatrixMVC(difficulty=1)
            self.assertIsNotNone(module, "Failed to instantiate MorphMatrix MVC module")
            # Check that the module has the required components
            self.assertIsNotNone(module.model, "MorphMatrix MVC module missing model component")
            self.assertIsNotNone(module.view, "MorphMatrix MVC module missing view component")
            self.assertIsNotNone(module.controller, "MorphMatrix MVC module missing controller component")
        except Exception as e:
            self.fail(f"MorphMatrix MVC instantiation failed with error: {e}")
        
    def test_expand_vision_mvc_instantiation(self):
        """Test that the ExpandVision MVC module can be instantiated."""
        try:
            # Note: ExpandVision requires screen dimensions
            screen_width, screen_height = 1024, 768
            module = ExpandVisionMVC(screen_width=screen_width, screen_height=screen_height)
            self.assertIsNotNone(module, "Failed to instantiate ExpandVision MVC module")
            # Check that the module has the required components
            self.assertIsNotNone(module.model, "ExpandVision MVC module missing model component")
            self.assertIsNotNone(module.view, "ExpandVision MVC module missing view component")
            self.assertIsNotNone(module.controller, "ExpandVision MVC module missing controller component")
        except Exception as e:
            self.fail(f"ExpandVision MVC instantiation failed with error: {e}")
    
    def test_symbol_memory_mvc_state(self):
        """Test that the SymbolMemory MVC module can generate a state."""
        module = SymbolMemoryMVC(difficulty=1)
        state = module.get_state()
        self.assertIsNotNone(state, "SymbolMemory MVC module returned None state")
        self.assertIn("components", state, "SymbolMemory MVC state missing components")
    
    def test_morph_matrix_mvc_state(self):
        """Test that the MorphMatrix MVC module can generate a state."""
        module = MorphMatrixMVC(difficulty=1)
        state = module.get_state()
        self.assertIsNotNone(state, "MorphMatrix MVC module returned None state")
        self.assertIn("components", state, "MorphMatrix MVC state missing components")
    
    def test_expand_vision_mvc_state(self):
        """Test that the ExpandVision MVC module can generate a state."""
        screen_width, screen_height = 1024, 768
        module = ExpandVisionMVC(screen_width=screen_width, screen_height=screen_height)
        state = module.get_state()
        self.assertIsNotNone(state, "ExpandVision MVC module returned None state")
        self.assertIn("components", state, "ExpandVision MVC state missing components")


if __name__ == "__main__":
    unittest.main() 