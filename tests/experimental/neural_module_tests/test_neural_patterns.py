#!/usr/bin/env python3
"""
Test Neural Patterns

This module tests the functionality of the neural pattern generation system.
"""

import unittest
import sys
from pathlib import Path
import numpy as np
import random
import time

# Add the parent directory to sys.path if needed
parent_dir = str(Path(__file__).parent.parent.parent)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from MetaMindIQTrain.core.neural_patterns import (
    PatternComplexity, DifficultyAxis, PatternType, 
    UserPerformanceModel, NeuralPattern
)


class TestUserPerformanceModel(unittest.TestCase):
    """Test the user performance model functionality."""
    
    def setUp(self):
        """Set up test fixture."""
        self.model = UserPerformanceModel(history_size=5)
        
    def test_update_and_get_optimal_difficulty(self):
        """Test updating performance data and getting optimal difficulty."""
        # Test with high accuracy
        for _ in range(3):
            self.model.update(0.95, 2.0, DifficultyAxis.SIZE)
        
        # High accuracy should suggest a more challenging difficulty
        difficulty = self.model.get_optimal_difficulty(DifficultyAxis.SIZE)
        self.assertIn(difficulty, [PatternComplexity.MEDIUM, PatternComplexity.CHALLENGING])
        
        # Reset the model
        self.model = UserPerformanceModel(history_size=5)
        
        # Test with low accuracy
        for _ in range(3):
            self.model.update(0.35, 2.0, DifficultyAxis.SIZE)
        
        # Low accuracy should suggest an easier difficulty
        difficulty = self.model.get_optimal_difficulty(DifficultyAxis.SIZE)
        self.assertEqual(difficulty, PatternComplexity.VERY_EASY)
        
    def test_learning_rate_adaptation(self):
        """Test that learning rate adapts based on performance consistency."""
        axis = DifficultyAxis.SIZE
        initial_rate = self.model.learning_rate[axis]
        
        # Consistent performance
        for _ in range(3):
            self.model.update(0.8, 2.0, axis)
        
        # Learning rate should adapt based on consistency
        self.assertNotEqual(initial_rate, self.model.learning_rate[axis], 
                         "Learning rate should adapt based on performance consistency")


class TestNeuralPattern(unittest.TestCase):
    """Test the neural pattern generation functionality."""
    
    def setUp(self):
        """Set up test fixture."""
        self.user_model = UserPerformanceModel()
        self.pattern_generators = {
            pattern_type: NeuralPattern(pattern_type, self.user_model)
            for pattern_type in PatternType
        }
        
    def test_generate_visual_grid_pattern(self):
        """Test generating visual grid patterns."""
        generator = self.pattern_generators[PatternType.VISUAL_GRID]
        
        # Test with default complexity
        pattern = generator.generate_pattern()
        
        # Check that the pattern has the expected structure
        self.assertEqual(pattern['type'], 'visual_grid')
        self.assertIn('grid', pattern)
        self.assertIn('grid_size', pattern)
        self.assertIn('num_elements', pattern)
        self.assertIn('display_time', pattern)
        self.assertIn('complexity', pattern)
        
        # Test with specific complexity
        complexity = {
            DifficultyAxis.SIZE: PatternComplexity.MEDIUM,
            DifficultyAxis.ELEMENTS: PatternComplexity.HARD,
            DifficultyAxis.SYMMETRY: PatternComplexity.EASY,
            DifficultyAxis.NOISE: PatternComplexity.VERY_EASY,
            DifficultyAxis.TIMING: PatternComplexity.CHALLENGING
        }
        
        pattern = generator.generate_pattern(complexity)
        
        # Check that the grid size matches the expected size for MEDIUM complexity
        self.assertEqual(pattern['grid_size'], 
                          generator.complexity_params[DifficultyAxis.SIZE][PatternComplexity.MEDIUM])
        
    def test_generate_multimodal_pattern(self):
        """Test generating multimodal patterns."""
        generator = self.pattern_generators[PatternType.MULTIMODAL]
        
        # Test with default complexity
        pattern = generator.generate_pattern()
        
        # Check that the pattern has the expected structure
        self.assertEqual(pattern['type'], 'multimodal')
        self.assertIn('sequence', pattern)
        self.assertIn('sequence_length', pattern)
        self.assertIn('num_visual_elements', pattern)
        self.assertIn('num_auditory_elements', pattern)
        
        # Check that the sequence contains the expected format (visual, auditory) pairs
        for visual, auditory in pattern['sequence']:
            self.assertIsInstance(visual, int)
            self.assertIsInstance(auditory, str)
            
    def test_evaluate_performance(self):
        """Test evaluating performance and adaptive difficulty."""
        generator = self.pattern_generators[PatternType.VISUAL_SEQUENCE]
        
        # Generate a pattern
        pattern = generator.generate_pattern()
        
        # Evaluate performance (simulate a user getting 80% correct)
        accuracy = 0.8
        response_time = 2.5
        
        eval_result = generator.evaluate_performance(
            accuracy, response_time, pattern['type'], pattern['complexity']
        )
        
        # Check that evaluation result contains expected fields
        self.assertIn('accuracy', eval_result)
        self.assertIn('response_time', eval_result)
        self.assertIn('overall_accuracy', eval_result)
        self.assertIn('overall_response_time', eval_result)
        self.assertIn('optimal_complexity', eval_result)
        
        # Check that optimal complexity was updated
        self.assertEqual(eval_result['accuracy'], accuracy)
        
        # Test with different performance levels
        accuracy = 0.4  # Poor performance
        
        eval_result = generator.evaluate_performance(
            accuracy, response_time, pattern['type'], pattern['complexity']
        )
        
        # Optimal complexity should now adapt to easier levels
        for axis, complexity in eval_result['optimal_complexity'].items():
            # Convert string to enum
            axis_enum = DifficultyAxis(axis)
            complexity_enum = PatternComplexity(complexity)
            
            # Check that poor performance leads to easier difficulty
            optimal = generator.user_model.get_optimal_difficulty(axis_enum)
            self.assertIn(optimal, [PatternComplexity.VERY_EASY, PatternComplexity.EASY])


if __name__ == '__main__':
    unittest.main() 