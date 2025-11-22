#!/usr/bin/env python3
"""
Neural Pattern Generation System.

This module provides advanced pattern generation capabilities using
neural network principles to create personalized, adaptive challenges 
that optimize cognitive development based on user performance.
"""

import numpy as np
import random
import math
import logging
from typing import Dict, List, Tuple, Any, Optional, Union, Callable
from enum import Enum

logger = logging.getLogger(__name__)

class PatternComplexity(Enum):
    """Enum for pattern complexity levels."""
    VERY_EASY = 1
    EASY = 2
    MEDIUM = 3
    CHALLENGING = 4
    HARD = 5
    VERY_HARD = 6
    EXPERT = 7

class DifficultyAxis(Enum):
    """Enum for different axes of difficulty."""
    SIZE = "size"              # Pattern size/length
    ELEMENTS = "elements"      # Number of distinct elements
    SYMMETRY = "symmetry"      # Degree of symmetry
    REPETITION = "repetition"  # Pattern repetitiveness
    NOISE = "noise"            # Random noise/interference
    TIMING = "timing"          # Time available for perception/recall
    DISTRACTION = "distraction"  # Distractions/interference

class PatternType(Enum):
    """Enum for different pattern types."""
    VISUAL_GRID = "visual_grid"
    VISUAL_SEQUENCE = "visual_sequence"
    AUDITORY_SEQUENCE = "auditory_sequence"
    MULTIMODAL = "multimodal"
    SPATIAL = "spatial"

class UserPerformanceModel:
    """Model tracking user performance to adapt pattern difficulty."""
    
    def __init__(self, history_size: int = 10):
        """Initialize the user performance model.
        
        Args:
            history_size: Number of past performances to track
        """
        # Track accuracy history per difficulty axis
        self.accuracy_history: Dict[DifficultyAxis, List[float]] = {
            axis: [] for axis in DifficultyAxis
        }
        
        # Track response times
        self.response_times: List[float] = []
        
        # Overall performance metrics
        self.overall_accuracy: float = 0.5  # Start at 50%
        self.overall_response_time: float = 0.0
        
        # Learning rate
        self.learning_rate: Dict[DifficultyAxis, float] = {
            axis: 0.1 for axis in DifficultyAxis
        }
        
        # Maximum history size
        self.history_size = history_size
        
        # Difficulty weights
        self.difficulty_weights = {
            PatternComplexity.VERY_EASY: 0.5,
            PatternComplexity.EASY: 0.75,
            PatternComplexity.MEDIUM: 1.0,
            PatternComplexity.CHALLENGING: 1.25,
            PatternComplexity.HARD: 1.5,
            PatternComplexity.VERY_HARD: 1.75,
            PatternComplexity.EXPERT: 2.0
        }
    
    def update(self, 
               accuracy: float, 
               response_time: float, 
               axis: DifficultyAxis):
        """Update the model with a new performance data point.
        
        Args:
            accuracy: Performance accuracy (0.0 to 1.0)
            response_time: Response time in seconds
            axis: Difficulty axis relevant to this performance
        """
        # Append to axis-specific history (limited to history_size)
        self.accuracy_history[axis].append(accuracy)
        if len(self.accuracy_history[axis]) > self.history_size:
            self.accuracy_history[axis].pop(0)
        
        # Update response times
        self.response_times.append(response_time)
        if len(self.response_times) > self.history_size:
            self.response_times.pop(0)
        
        # Update overall metrics with exponential moving average
        self.overall_accuracy = 0.8 * self.overall_accuracy + 0.2 * accuracy
        
        if self.overall_response_time == 0.0:
            self.overall_response_time = response_time
        else:
            self.overall_response_time = 0.8 * self.overall_response_time + 0.2 * response_time
        
        # Update learning rate based on consistency of performance
        if len(self.accuracy_history[axis]) >= 3:
            variance = np.var(self.accuracy_history[axis][-3:])
            # Lower variance = more consistent performance = faster learning rate
            self.learning_rate[axis] = min(0.3, max(0.05, 0.2 - variance))
    
    def get_optimal_difficulty(self, axis: DifficultyAxis) -> PatternComplexity:
        """Get the optimal difficulty level for a given axis.
        
        Args:
            axis: The difficulty axis to get optimal level for
            
        Returns:
            The optimal difficulty level
        """
        if not self.accuracy_history[axis]:
            return PatternComplexity.EASY  # Default starting point
        
        # Get recent performance for this axis
        recent_performance = self.accuracy_history[axis][-min(3, len(self.accuracy_history[axis])):]
        avg_performance = sum(recent_performance) / len(recent_performance)
        
        # Target 75-85% success rate for optimal learning
        if avg_performance > 0.9:
            return PatternComplexity.CHALLENGING  # Too easy, increase difficulty
        elif avg_performance > 0.85:
            return PatternComplexity.MEDIUM  # Slightly too easy
        elif avg_performance >= 0.75:
            return PatternComplexity.EASY  # Optimal learning zone
        elif avg_performance >= 0.6:
            return PatternComplexity.VERY_EASY  # Slightly too hard
        else:
            return PatternComplexity.VERY_EASY  # Too hard, decrease difficulty
    
    def get_difficulty_score(self, complexity: PatternComplexity) -> float:
        """Get a numerical difficulty score for a complexity level.
        
        Args:
            complexity: The pattern complexity level
            
        Returns:
            Numerical difficulty score (higher = more difficult)
        """
        return self.difficulty_weights.get(complexity, 1.0)


class NeuralPattern:
    """Neural network-inspired pattern generator."""
    
    def __init__(self, 
                 pattern_type: PatternType,
                 user_model: Optional[UserPerformanceModel] = None):
        """Initialize the neural pattern generator.
        
        Args:
            pattern_type: Type of pattern to generate
            user_model: User performance model for adaptive patterns
        """
        self.pattern_type = pattern_type
        self.user_model = user_model or UserPerformanceModel()
        
        # Default dimensionality for each pattern type
        self.default_dimensions = {
            PatternType.VISUAL_GRID: (4, 4),    # 4x4 grid
            PatternType.VISUAL_SEQUENCE: (8,),  # 8 elements in sequence
            PatternType.AUDITORY_SEQUENCE: (6,),  # 6 elements in sequence
            PatternType.MULTIMODAL: (5,),       # 5 elements in sequence
            PatternType.SPATIAL: (3, 3)         # 3x3 grid
        }
        
        # Mapping from complexity to actual parameter values
        self.complexity_params = {
            # Mapping from complexity to grid size
            DifficultyAxis.SIZE: {
                PatternComplexity.VERY_EASY: 3,
                PatternComplexity.EASY: 4,
                PatternComplexity.MEDIUM: 5,
                PatternComplexity.CHALLENGING: 6,
                PatternComplexity.HARD: 7,
                PatternComplexity.VERY_HARD: 8,
                PatternComplexity.EXPERT: 9
            },
            # Mapping from complexity to number of elements
            DifficultyAxis.ELEMENTS: {
                PatternComplexity.VERY_EASY: 3,
                PatternComplexity.EASY: 5,
                PatternComplexity.MEDIUM: 7,
                PatternComplexity.CHALLENGING: 9,
                PatternComplexity.HARD: 12,
                PatternComplexity.VERY_HARD: 15,
                PatternComplexity.EXPERT: 20
            },
            # Mapping from complexity to entropy (lower = more symmetry)
            DifficultyAxis.SYMMETRY: {
                PatternComplexity.VERY_EASY: 0.2,
                PatternComplexity.EASY: 0.3,
                PatternComplexity.MEDIUM: 0.4,
                PatternComplexity.CHALLENGING: 0.6,
                PatternComplexity.HARD: 0.7,
                PatternComplexity.VERY_HARD: 0.8,
                PatternComplexity.EXPERT: 0.9
            },
            # Mapping from complexity to repetition (higher = less repetition)
            DifficultyAxis.REPETITION: {
                PatternComplexity.VERY_EASY: 0.2,
                PatternComplexity.EASY: 0.3,
                PatternComplexity.MEDIUM: 0.5,
                PatternComplexity.CHALLENGING: 0.6,
                PatternComplexity.HARD: 0.7,
                PatternComplexity.VERY_HARD: 0.85,
                PatternComplexity.EXPERT: 0.95
            },
            # Mapping from complexity to noise level
            DifficultyAxis.NOISE: {
                PatternComplexity.VERY_EASY: 0.0,
                PatternComplexity.EASY: 0.05,
                PatternComplexity.MEDIUM: 0.1,
                PatternComplexity.CHALLENGING: 0.15,
                PatternComplexity.HARD: 0.2,
                PatternComplexity.VERY_HARD: 0.25,
                PatternComplexity.EXPERT: 0.3
            },
            # Mapping from complexity to timing (in seconds)
            DifficultyAxis.TIMING: {
                PatternComplexity.VERY_EASY: 5.0,
                PatternComplexity.EASY: 4.0,
                PatternComplexity.MEDIUM: 3.0,
                PatternComplexity.CHALLENGING: 2.5,
                PatternComplexity.HARD: 2.0,
                PatternComplexity.VERY_HARD: 1.5,
                PatternComplexity.EXPERT: 1.0
            },
            # Mapping from complexity to distraction level
            DifficultyAxis.DISTRACTION: {
                PatternComplexity.VERY_EASY: 0.0,
                PatternComplexity.EASY: 0.1,
                PatternComplexity.MEDIUM: 0.2,
                PatternComplexity.CHALLENGING: 0.3,
                PatternComplexity.HARD: 0.4,
                PatternComplexity.VERY_HARD: 0.5,
                PatternComplexity.EXPERT: 0.6
            }
        }
        
        # Initialize pattern memory
        self.pattern_memory = []
    
    def generate_pattern(self, 
                         complexity: Optional[Dict[DifficultyAxis, PatternComplexity]] = None) -> Dict[str, Any]:
        """Generate a pattern with the given complexity.
        
        Args:
            complexity: Dictionary mapping difficulty axes to complexity levels
            
        Returns:
            Generated pattern as a dictionary
        """
        # Use default complexity if not provided
        if complexity is None:
            complexity = {
                DifficultyAxis.SIZE: PatternComplexity.EASY,
                DifficultyAxis.ELEMENTS: PatternComplexity.EASY,
                DifficultyAxis.SYMMETRY: PatternComplexity.EASY,
                DifficultyAxis.REPETITION: PatternComplexity.EASY,
                DifficultyAxis.NOISE: PatternComplexity.EASY,
                DifficultyAxis.TIMING: PatternComplexity.EASY,
                DifficultyAxis.DISTRACTION: PatternComplexity.EASY
            }
        
        # Dispatch to the appropriate pattern generator
        if self.pattern_type == PatternType.VISUAL_GRID:
            pattern = self._generate_visual_grid(complexity)
        elif self.pattern_type == PatternType.VISUAL_SEQUENCE:
            pattern = self._generate_visual_sequence(complexity)
        elif self.pattern_type == PatternType.AUDITORY_SEQUENCE:
            pattern = self._generate_auditory_sequence(complexity)
        elif self.pattern_type == PatternType.MULTIMODAL:
            pattern = self._generate_multimodal(complexity)
        elif self.pattern_type == PatternType.SPATIAL:
            pattern = self._generate_spatial(complexity)
        else:
            raise ValueError(f"Unknown pattern type: {self.pattern_type}")
        
        # Store in pattern memory
        self.pattern_memory.append(pattern)
        
        return pattern
    
    def generate_optimal_pattern(self) -> Dict[str, Any]:
        """Generate a pattern with optimal complexity based on user model.
        
        Returns:
            Generated pattern as a dictionary
        """
        optimal_complexity = {
            axis: self.user_model.get_optimal_difficulty(axis)
            for axis in DifficultyAxis
        }
        
        return self.generate_pattern(optimal_complexity)
    
    def _generate_visual_grid(self, 
                             complexity: Dict[DifficultyAxis, PatternComplexity]) -> Dict[str, Any]:
        """Generate a visual grid pattern.
        
        Args:
            complexity: Complexity settings for each difficulty axis
            
        Returns:
            Visual grid pattern as a dictionary
        """
        # Determine grid size based on SIZE complexity
        size_complexity = complexity.get(DifficultyAxis.SIZE, PatternComplexity.EASY)
        grid_size = self.complexity_params[DifficultyAxis.SIZE][size_complexity]
        
        # Determine number of elements (colors) based on ELEMENTS complexity
        elements_complexity = complexity.get(DifficultyAxis.ELEMENTS, PatternComplexity.EASY)
        num_elements = self.complexity_params[DifficultyAxis.ELEMENTS][elements_complexity]
        
        # Generate elements (colors)
        elements = list(range(num_elements))
        
        # Get symmetry parameter
        symmetry_complexity = complexity.get(DifficultyAxis.SYMMETRY, PatternComplexity.EASY)
        symmetry = self.complexity_params[DifficultyAxis.SYMMETRY][symmetry_complexity]
        
        # Get noise parameter
        noise_complexity = complexity.get(DifficultyAxis.NOISE, PatternComplexity.EASY)
        noise = self.complexity_params[DifficultyAxis.NOISE][noise_complexity]
        
        # Create grid with symmetry and noise
        grid = np.zeros((grid_size, grid_size), dtype=int)
        
        if symmetry < 0.5:
            # Generate symmetric pattern
            # Fill half the grid randomly
            for i in range(grid_size):
                for j in range(grid_size // 2 + grid_size % 2):
                    grid[i, j] = random.choice(elements)
            
            # Mirror the pattern for symmetry
            for i in range(grid_size):
                for j in range(grid_size // 2):
                    grid[i, grid_size - j - 1] = grid[i, j]
        else:
            # Generate asymmetric pattern
            for i in range(grid_size):
                for j in range(grid_size):
                    grid[i, j] = random.choice(elements)
        
        # Add noise
        if noise > 0:
            noise_mask = np.random.random((grid_size, grid_size)) < noise
            for i in range(grid_size):
                for j in range(grid_size):
                    if noise_mask[i, j]:
                        grid[i, j] = random.choice(elements)
        
        # Get timing parameter
        timing_complexity = complexity.get(DifficultyAxis.TIMING, PatternComplexity.EASY)
        display_time = self.complexity_params[DifficultyAxis.TIMING][timing_complexity] * 1000  # Convert to ms
        
        return {
            'type': 'visual_grid',
            'grid': grid.tolist(),
            'grid_size': grid_size,
            'num_elements': num_elements,
            'display_time': display_time,
            'complexity': {k.value: v.value for k, v in complexity.items()}
        }
    
    def _generate_visual_sequence(self, 
                                 complexity: Dict[DifficultyAxis, PatternComplexity]) -> Dict[str, Any]:
        """Generate a visual sequence pattern.
        
        Args:
            complexity: Complexity settings for each difficulty axis
            
        Returns:
            Visual sequence pattern as a dictionary
        """
        # Determine sequence length based on SIZE complexity
        size_complexity = complexity.get(DifficultyAxis.SIZE, PatternComplexity.EASY)
        seq_length = self.complexity_params[DifficultyAxis.SIZE][size_complexity]
        
        # Determine number of elements (colors/shapes) based on ELEMENTS complexity
        elements_complexity = complexity.get(DifficultyAxis.ELEMENTS, PatternComplexity.EASY)
        num_elements = self.complexity_params[DifficultyAxis.ELEMENTS][elements_complexity]
        
        # Get repetition parameter (higher = less repetition)
        repetition_complexity = complexity.get(DifficultyAxis.REPETITION, PatternComplexity.EASY)
        repetition = self.complexity_params[DifficultyAxis.REPETITION][repetition_complexity]
        
        # Generate elements
        elements = list(range(num_elements))
        
        # Generate sequence with controlled repetition
        sequence = []
        for i in range(seq_length):
            if random.random() < repetition or len(sequence) < 2:
                # Generate a new random element
                element = random.choice(elements)
                # Try to avoid the same element appearing twice in a row
                while len(sequence) > 0 and element == sequence[-1]:
                    element = random.choice(elements)
                sequence.append(element)
            else:
                # Repeat a pattern from earlier in the sequence
                pattern_length = random.randint(1, min(3, len(sequence)))
                start_idx = random.randint(0, len(sequence) - pattern_length)
                sequence.append(sequence[start_idx:start_idx + pattern_length][0])
        
        # Get timing parameter
        timing_complexity = complexity.get(DifficultyAxis.TIMING, PatternComplexity.EASY)
        display_time = self.complexity_params[DifficultyAxis.TIMING][timing_complexity] * 1000  # Convert to ms
        element_time = display_time / seq_length
        
        return {
            'type': 'visual_sequence',
            'sequence': sequence,
            'sequence_length': seq_length,
            'num_elements': num_elements,
            'display_time': display_time,
            'element_time': element_time,
            'complexity': {k.value: v.value for k, v in complexity.items()}
        }
    
    def _generate_auditory_sequence(self, 
                                   complexity: Dict[DifficultyAxis, PatternComplexity]) -> Dict[str, Any]:
        """Generate an auditory sequence pattern.
        
        Args:
            complexity: Complexity settings for each difficulty axis
            
        Returns:
            Auditory sequence pattern as a dictionary
        """
        # Determine sequence length based on SIZE complexity
        size_complexity = complexity.get(DifficultyAxis.SIZE, PatternComplexity.EASY)
        seq_length = self.complexity_params[DifficultyAxis.SIZE][size_complexity]
        
        # Determine number of elements (notes) based on ELEMENTS complexity
        elements_complexity = complexity.get(DifficultyAxis.ELEMENTS, PatternComplexity.EASY)
        num_elements = min(7, self.complexity_params[DifficultyAxis.ELEMENTS][elements_complexity])  # Limit to 7 notes
        
        # Get repetition parameter (higher = less repetition)
        repetition_complexity = complexity.get(DifficultyAxis.REPETITION, PatternComplexity.EASY)
        repetition = self.complexity_params[DifficultyAxis.REPETITION][repetition_complexity]
        
        # Define musical notes (C, D, E, F, G, A, B)
        notes = ['C', 'D', 'E', 'F', 'G', 'A', 'B'][:num_elements]
        
        # Generate sequence with controlled repetition and musicality
        sequence = []
        for i in range(seq_length):
            if random.random() < repetition or len(sequence) < 2:
                # Generate a new random note
                # Use musical theory to prefer certain intervals for musicality
                if len(sequence) > 0:
                    last_note_idx = notes.index(sequence[-1])
                    # Prefer smaller intervals (thirds and seconds)
                    interval = random.choice([-2, -1, 1, 2, 3])
                    new_idx = (last_note_idx + interval) % len(notes)
                    sequence.append(notes[new_idx])
                else:
                    sequence.append(random.choice(notes))
            else:
                # Repeat a pattern from earlier in the sequence
                pattern_length = random.randint(1, min(3, len(sequence)))
                start_idx = random.randint(0, len(sequence) - pattern_length)
                sequence.append(sequence[start_idx:start_idx + pattern_length][0])
        
        # Get timing parameter
        timing_complexity = complexity.get(DifficultyAxis.TIMING, PatternComplexity.EASY)
        display_time = self.complexity_params[DifficultyAxis.TIMING][timing_complexity] * 1000  # Convert to ms
        note_time = display_time / seq_length
        
        return {
            'type': 'auditory_sequence',
            'sequence': sequence,
            'sequence_length': seq_length,
            'num_elements': num_elements,
            'display_time': display_time,
            'note_time': note_time,
            'complexity': {k.value: v.value for k, v in complexity.items()}
        }
    
    def _generate_multimodal(self, 
                            complexity: Dict[DifficultyAxis, PatternComplexity]) -> Dict[str, Any]:
        """Generate a multimodal pattern combining visual and auditory elements.
        
        Args:
            complexity: Complexity settings for each difficulty axis
            
        Returns:
            Multimodal pattern as a dictionary
        """
        # Determine sequence length based on SIZE complexity
        size_complexity = complexity.get(DifficultyAxis.SIZE, PatternComplexity.EASY)
        seq_length = self.complexity_params[DifficultyAxis.SIZE][size_complexity]
        
        # Determine number of visual elements
        elements_complexity = complexity.get(DifficultyAxis.ELEMENTS, PatternComplexity.EASY)
        num_visual_elements = self.complexity_params[DifficultyAxis.ELEMENTS][elements_complexity]
        
        # Determine number of auditory elements (notes)
        num_auditory_elements = min(7, self.complexity_params[DifficultyAxis.ELEMENTS][elements_complexity])
        
        # Generate visual elements (colors)
        visual_elements = list(range(num_visual_elements))
        
        # Define musical notes
        auditory_elements = ['C', 'D', 'E', 'F', 'G', 'A', 'B'][:num_auditory_elements]
        
        # Generate combined sequence
        sequence = []
        for i in range(seq_length):
            visual = random.choice(visual_elements)
            auditory = random.choice(auditory_elements)
            sequence.append((visual, auditory))
        
        # Get timing parameter
        timing_complexity = complexity.get(DifficultyAxis.TIMING, PatternComplexity.EASY)
        display_time = self.complexity_params[DifficultyAxis.TIMING][timing_complexity] * 1000  # Convert to ms
        element_time = display_time / seq_length
        
        return {
            'type': 'multimodal',
            'sequence': sequence,
            'sequence_length': seq_length,
            'num_visual_elements': num_visual_elements,
            'num_auditory_elements': num_auditory_elements,
            'display_time': display_time,
            'element_time': element_time,
            'complexity': {k.value: v.value for k, v in complexity.items()}
        }
    
    def _generate_spatial(self, 
                         complexity: Dict[DifficultyAxis, PatternComplexity]) -> Dict[str, Any]:
        """Generate a spatial pattern.
        
        Args:
            complexity: Complexity settings for each difficulty axis
            
        Returns:
            Spatial pattern as a dictionary
        """
        # Determine grid size based on SIZE complexity
        size_complexity = complexity.get(DifficultyAxis.SIZE, PatternComplexity.EASY)
        grid_size = self.complexity_params[DifficultyAxis.SIZE][size_complexity]
        
        # Determine number of active cells
        elements_complexity = complexity.get(DifficultyAxis.ELEMENTS, PatternComplexity.EASY)
        num_elements = min(grid_size * grid_size, self.complexity_params[DifficultyAxis.ELEMENTS][elements_complexity])
        
        # Create grid
        grid = np.zeros((grid_size, grid_size), dtype=int)
        
        # Generate positions for active cells
        positions = []
        for i in range(grid_size):
            for j in range(grid_size):
                positions.append((i, j))
        
        # Randomly select positions for active cells
        active_positions = random.sample(positions, num_elements)
        
        # Set active cells
        for i, j in active_positions:
            grid[i, j] = 1
        
        # Get timing parameter
        timing_complexity = complexity.get(DifficultyAxis.TIMING, PatternComplexity.EASY)
        display_time = self.complexity_params[DifficultyAxis.TIMING][timing_complexity] * 1000  # Convert to ms
        
        return {
            'type': 'spatial',
            'grid': grid.tolist(),
            'grid_size': grid_size,
            'num_elements': num_elements,
            'display_time': display_time,
            'complexity': {k.value: v.value for k, v in complexity.items()}
        }
    
    def evaluate_performance(self,
                           accuracy: float,
                           response_time: float,
                           pattern_type: str,
                           complexity: Dict[str, int]) -> Dict[str, Any]:
        """Evaluate user performance on a pattern.
        
        Args:
            accuracy: Performance accuracy (0.0 to 1.0)
            response_time: Response time in seconds
            pattern_type: Type of pattern
            complexity: Complexity settings used
            
        Returns:
            Dictionary with performance assessment
        """
        # Convert complexity string keys to enum keys
        enum_complexity = {
            DifficultyAxis(k): PatternComplexity(v) 
            for k, v in complexity.items()
        }
        
        # Update user model for all relevant axes
        for axis in enum_complexity:
            self.user_model.update(accuracy, response_time, axis)
        
        # Get new optimal complexities
        optimal_complexity = {
            axis: self.user_model.get_optimal_difficulty(axis)
            for axis in DifficultyAxis
        }
        
        return {
            'accuracy': accuracy,
            'response_time': response_time,
            'overall_accuracy': self.user_model.overall_accuracy,
            'overall_response_time': self.user_model.overall_response_time,
            'optimal_complexity': {k.value: v.value for k, v in optimal_complexity.items()}
        }
    
    def get_adaptive_parameters(self) -> Dict[str, Any]:
        """Get adaptive parameters based on user model.
        
        Returns:
            Dictionary with adaptive parameters
        """
        # Get optimal complexities
        optimal_complexity = {
            axis: self.user_model.get_optimal_difficulty(axis)
            for axis in DifficultyAxis
        }
        
        # Convert to actual parameter values
        params = {}
        for axis, complexity in optimal_complexity.items():
            params[axis.value] = self.complexity_params[axis][complexity]
        
        return {
            'optimal_complexity': {k.value: v.value for k, v in optimal_complexity.items()},
            'parameters': params
        } 