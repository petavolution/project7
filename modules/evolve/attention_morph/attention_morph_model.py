#!/usr/bin/env python3
"""
Attention Morph Model - Core game logic for the Attention Morph training module

This module defines the Model component in the MVC architecture for the
Attention Morph cognitive training exercise. It handles the game's business logic:
- Shape management and transformation
- Target placement and validation
- Difficulty progression and scoring
- Grid state management

The model implements a selective attention training task where users must
identify target shapes among distractors, with difficulty that adapts to
user performance.
"""

import random
import pygame
import time
import math
import sys
from pathlib import Path
from typing import List, Dict, Tuple, Set, Optional, Any, Union

class Shape:
    """Represents a single shape in the attention morph grid.
    
    Shapes are the core visual elements in the Attention Morph exercise.
    Each shape can have various attributes such as type (circle, square, etc.),
    color, size, and transformation properties. Some shapes are designated as
    targets that users need to identify.
    """
    
    def __init__(self, shape_type: str, position: Tuple[int, int], size: int, color: Tuple[int, int, int]):
        """Initialize a shape with its attributes.
        
        Args:
            shape_type: Type of shape (circle, square, triangle, etc.)
            position: (x, y) center position of the shape
            size: Size of the shape in pixels
            color: (r, g, b) color tuple
        """
        self.shape_type = shape_type
        self.position = position
        self.size = size
        self.color = color
        self.is_target = False
        self.is_transforming = False
        self.transform_progress = 0.0
        self.transform_target = None
        self.creation_time = time.time()
        self.marks = 0  # Number of marks (used for target criteria)
        
    def update(self, dt: float) -> None:
        """Update shape transformation if active.
        
        Args:
            dt: Time delta in seconds
        """
        if self.is_transforming and self.transform_target:
            self.transform_progress += dt * 2  # Speed factor
            
            if self.transform_progress >= 1.0:
                # Complete transformation
                self.shape_type = self.transform_target
                self.is_transforming = False
                self.transform_progress = 0.0
                self.transform_target = None

    def make_target(self) -> None:
        """Mark this shape as a target by setting required attributes."""
        self.is_target = True
        self.marks = 2  # Target criteria: 'd' shape with 2 marks
        
    def get_data(self) -> Dict[str, Any]:
        """Get serializable data representing the shape.
        
        Returns:
            Dictionary with shape data
        """
        return {
            "type": self.shape_type,
            "is_target": self.is_target,
            "marks": self.marks,
            "transforming": self.is_transforming,
            "transform_progress": self.transform_progress
        }


class AttentionMorphModel:
    """Model for attention morph module handling shape transformations and difficulty progression.
    
    This class manages the core game logic for the Attention Morph cognitive training
    exercise, including grid generation, difficulty adjustment, and score tracking.
    It implements the model component of the MVC pattern.
    """

    # Available shapes and target definitions
    SHAPE_TYPES = ["circle", "square", "triangle", "diamond", "star", "d", "p"]
    TARGET_TYPE = "d"  # The letter d is our target when it has two marks
    TARGET_MARKS = 2  # Number of marks that make a shape a target
    
    # Game states
    STATE_ACTIVE = "active"
    STATE_COMPLETED = "completed"
    
    # Base colors for shapes
    BASE_COLORS = [
        (220, 50, 50),    # Red
        (50, 220, 50),    # Green
        (50, 50, 220),    # Blue
        (220, 220, 50),   # Yellow
        (220, 50, 220),   # Magenta
        (50, 220, 220),   # Cyan
        (220, 150, 50)    # Orange
    ]
    
    def __init__(self, rows: int = 5, cols: int = 5, difficulty: int = 1):
        """Initialize the model with game state and grid.
        
        Args:
            rows: Number of grid rows
            cols: Number of grid columns
            difficulty: Initial difficulty level (1-10)
        """
        # Grid dimensions
        self.rows = rows
        self.cols = cols
        self.grid = []  # 2D grid of Shape objects
        
        # Game state
        self.state = self.STATE_ACTIVE
        self.score = 0
        self.difficulty_level = max(1, min(10, difficulty))
        self.complexity = self._calculate_complexity()
        self.transformation_rules = {}
        self.targets = set()  # Set of (row, col) positions of target shapes
        
        # Shape transformation settings
        self.transformation_speed = 1.0
        self.transformation_probability = 0.1 * self.difficulty_level
        
        # Performance tracking
        self.selections = []  # List of (row, col, is_correct) tuples
        
        # Generate initial grid
        self.generate_shape_grid(rows, cols, self.complexity)
        self.define_transformation_rules()
    
    def _calculate_complexity(self) -> int:
        """Calculate grid complexity based on difficulty level.
        
        Returns:
            Complexity value
        """
        # Map difficulty (1-10) to complexity (1-5)
        return max(1, min(5, int(self.difficulty_level / 2) + 1))
        
    def generate_shape_grid(self, rows: int, cols: int, complexity: int) -> None:
        """Generate a grid of shapes with varying types.
        
        Args:
            rows: Number of grid rows
            cols: Number of grid columns
            complexity: Complexity level (1-5)
        """
        self.rows = rows
        self.cols = cols
        self.grid = []
        
        # Determine shape distribution based on complexity
        # Higher complexity = more variety of shapes
        available_shapes = self.SHAPE_TYPES[:2 + complexity]
        
        # Generate grid with random shapes
        for row in range(rows):
            grid_row = []
            for col in range(cols):
                # Calculate position
                position = (col, row)
                
                # Determine shape type with weighted probability
                # Make target shape type less common
                if self.TARGET_TYPE in available_shapes and random.random() < 0.1:
                    shape_type = self.TARGET_TYPE
                else:
                    # Exclude target type from random selection
                    non_target_shapes = [s for s in available_shapes if s != self.TARGET_TYPE]
                    shape_type = random.choice(non_target_shapes)
                
                # Random size based on difficulty (higher difficulty = smaller shapes)
                base_size = 50 - (self.difficulty_level * 2)
                size = max(20, base_size + random.randint(-5, 5))
                
                # Random color from base colors
                color = random.choice(self.BASE_COLORS)
                
                # Create shape
                shape = Shape(shape_type, position, size, color)
                grid_row.append(shape)
            
            self.grid.append(grid_row)

    def define_transformation_rules(self) -> Dict:
        """Define rules for how shapes can transform.
        
        Returns:
            Dictionary of transformation rules
        """
        # Reset rules
        self.transformation_rules = {}
        
        # Create rules for each shape type
        for shape_type in self.SHAPE_TYPES:
            # Each shape can transform into 2-3 other shapes
            possible_targets = [s for s in self.SHAPE_TYPES if s != shape_type]
            
            # For target shapes, make them less likely to transform
            if shape_type == self.TARGET_TYPE:
                num_targets = min(2, len(possible_targets))
            else:
                num_targets = min(3, len(possible_targets))
                
            # Randomly select transformation targets
            targets = random.sample(possible_targets, num_targets)
            
            # Store rule
            self.transformation_rules[shape_type] = targets
        
        return self.transformation_rules

    def place_target_stimuli(self, num_targets: int) -> None:
        """Place target stimuli randomly on the grid.
        
        Args:
            num_targets: Number of targets to place
        """
        # Clear existing targets
        self.targets.clear()
        
        # Reset existing target flags
        for row in range(self.rows):
            for col in range(self.cols):
                self.grid[row][col].is_target = False
        
        # Place new targets
        available_positions = [(row, col) for row in range(self.rows) for col in range(self.cols)]
        random.shuffle(available_positions)
        
        # Cap targets based on grid size
        max_possible = min(num_targets, len(available_positions))
        
        for i in range(max_possible):
            row, col = available_positions[i]
            
            # Set target properties
            self.grid[row][col].shape_type = self.TARGET_TYPE
            self.grid[row][col].make_target()
            
            # Add to target set
            self.targets.add((row, col))

    def update_grid(self, dt: float) -> None:
        """Update all shapes in the grid.
        
        Args:
            dt: Time delta in seconds
        """
        for row in range(self.rows):
            for col in range(self.cols):
                self.grid[row][col].update(dt)

    def start_random_transformations(self, count: int) -> None:
        """Start random transformations on the grid.
        
        Args:
            count: Number of transformations to start
        """
        # Get list of non-transforming cells
        available_cells = []
        for row in range(self.rows):
            for col in range(self.cols):
                if not self.grid[row][col].is_transforming:
                    available_cells.append((row, col))
        
        if not available_cells:
            return
            
        # Cap count to available cells
        count = min(count, len(available_cells))
        
        # Randomly select cells to transform
        cells_to_transform = random.sample(available_cells, count)
        
        for row, col in cells_to_transform:
            shape = self.grid[row][col]
            
            # Skip targets - they should remain stable
            if shape.is_target:
                continue
                
            # Get valid transformation targets
            if shape.shape_type in self.transformation_rules:
                possible_targets = self.transformation_rules[shape.shape_type]
                if possible_targets:
                    # Start transformation
                    shape.is_transforming = True
                    shape.transform_progress = 0.0
                    shape.transform_target = random.choice(possible_targets)

    def check_selection(self, row: int, col: int) -> bool:
        """Check if a selected cell contains a target.
        
        Args:
            row: Selected row
            col: Selected column
            
        Returns:
            True if selection is a target, False otherwise
        """
        # Validate indices
        if not (0 <= row < self.rows and 0 <= col < self.cols):
            return False
            
        # Check if shape at this position is a target
        return self.grid[row][col].is_target

    def process_selection(self, row: int, col: int) -> bool:
        """Process user selection of a cell.
        
        Args:
            row: Selected row
            col: Selected column
            
        Returns:
            True if selection was correct, False otherwise
        """
        result = self.check_selection(row, col)
        
        # Record selection
        self.selections.append((row, col, result))
        
        # If correct, remove from targets
        if result and (row, col) in self.targets:
            self.targets.remove((row, col))
        
        return result

    def update_difficulty(self, level: int) -> None:
        """Update difficulty level and adjust game parameters.
        
        Args:
            level: New difficulty level (1-10)
        """
        # Clamp difficulty to valid range
        self.difficulty_level = max(1, min(10, level))
        
        # Update derived parameters
        self.complexity = self._calculate_complexity()
        self.transformation_speed = 1.0 + (self.difficulty_level * 0.1)
        self.transformation_probability = 0.1 * self.difficulty_level

    def get_accuracy(self) -> float:
        """Calculate the current selection accuracy.
        
        Returns:
            Accuracy as a float between 0 and 1
        """
        if not self.selections:
            return 0.0
            
        correct = sum(1 for _, _, result in self.selections if result)
        return correct / len(self.selections)

    def get_score_rate(self) -> float:
        """Calculate score rate (points per second).
        
        Returns:
            Score rate
        """
        elapsed = time.time() - self.grid[0][0].creation_time if self.grid else 0
        if elapsed <= 0:
            return 0.0
            
        return self.score / elapsed

    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the current game state.
        
        Returns:
            Dictionary of statistics
        """
        return {
            "score": self.score,
            "difficulty": self.difficulty_level,
            "complexity": self.complexity,
            "accuracy": self.get_accuracy(),
            "score_rate": self.get_score_rate(),
            "targets_remaining": len(self.targets),
            "selections_made": len(self.selections)
        }
    
    def get_grid_data(self) -> List[List[Dict[str, Any]]]:
        """Get serializable grid data.
        
        Returns:
            2D list of shape data
        """
        return [[cell.get_data() for cell in row] for row in self.grid]
    
    def count_targets(self) -> int:
        """Count the total number of targets on the grid.
        
        Returns:
            Number of targets
        """
        return len(self.targets)

    def reset(self) -> None:
        """Reset model to initial state."""
        self.score = 0
        self.state = self.STATE_ACTIVE
        self.selections.clear()
        self.targets.clear()
        
        # Regenerate grid
        self.generate_shape_grid(self.rows, self.cols, self.complexity)
        self.define_transformation_rules() 