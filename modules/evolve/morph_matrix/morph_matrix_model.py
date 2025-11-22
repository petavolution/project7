#!/usr/bin/env python3
"""
MorphMatrix Model Component

This module handles the core game logic for the MorphMatrix training module:
- Pattern generation and manipulation
- Game state management
- Score calculation
- Difficulty progression

The model is responsible for all data and business logic, independent of the UI.
"""

import random
import time
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional, Union, Set

# Add the parent directory to sys.path for absolute imports when imported directly
if __name__ == "__main__" or not __package__:
    project_root = Path(__file__).parent.parent.parent.parent
    sys.path.insert(0, str(project_root))


class MorphMatrixModel:
    """Model component for MorphMatrix module - handles core game logic."""
    
    def __init__(self, difficulty=1):
        """Initialize the model with game state and business logic.
        
        Args:
            difficulty: Initial difficulty level (1-10)
        """
        # Game settings
        self.difficulty = max(1, min(10, difficulty))
        self.level = self.difficulty
        self.matrix_size = self._calculate_matrix_size()
        self.score = 0
        
        # Game state
        self.game_state = "challenge_active"  # challenge_active, challenge_complete, feedback
        self.clusters = []  # Matrix pattern clusters
        self.original_matrix = None  # Original pattern matrix
        self.selected_clusters = []  # User selections
        self.answered = False  # Whether the user has submitted an answer
        self.correct_answer = None  # Whether the last answer was correct
        self.modified_indices = []  # Indices of modified patterns
        self.selected_patterns = []  # Indices of user-selected patterns
        self.total_patterns = 0  # Total number of patterns in the challenge
        
        # Performance tracking
        self.round_start_time = time.time()
        self.challenge_time = 0
        
        # Create first challenge
        self.create_new_challenge()
    
    def create_new_challenge(self):
        """Create a new pattern recognition challenge."""
        # Adjust matrix size based on level
        self.matrix_size = self._calculate_matrix_size()
        
        # Reset state
        self.original_matrix = self.generate_random_matrix(self.matrix_size)
        self.selected_patterns = []
        self.answered = False
        self.correct_answer = None
        self.round_start_time = time.time()
        
        # Create pattern variations
        num_patterns = 6  # Default 6 patterns (3x2 grid)
        num_modified = random.randint(1, 4)  # 1-4 modified patterns
        
        self.create_pattern_variations(num_patterns, num_modified)
    
    def create_pattern_variations(self, num_patterns, num_modified):
        """Create pattern variations from the original matrix.
        
        Args:
            num_patterns: Total number of patterns to create
            num_modified: Number of patterns that should be modified
        """
        self.clusters = []
        self.modified_indices = []
        
        # Create all patterns as rotations initially
        for i in range(num_patterns):
            rotation = random.choice([0, 90, 180, 270])
            position = None  # Will be set by the View
            
            cluster = self.create_cluster(self.original_matrix, rotation, i, position)
            self.clusters.append(cluster)
        
        # Select random patterns to modify
        indices_to_modify = random.sample(range(num_patterns), num_modified)
        self.modified_indices = indices_to_modify
        
        # Modify the selected patterns
        for idx in indices_to_modify:
            self.mutate_pattern(self.clusters[idx])
        
        self.total_patterns = num_patterns
    
    def create_cluster(self, source_matrix, rotation, index, position=None):
        """Create a pattern cluster with metadata.
        
        Args:
            source_matrix: Source matrix to transform
            rotation: Rotation angle (0, 90, 180, 270)
            index: Pattern index
            position: Optional (x, y) position
            
        Returns:
            Cluster dictionary with pattern data
        """
        rotated = self.rotate_matrix(source_matrix, rotation)
        
        return {
            "matrix": rotated,
            "rotation": rotation,
            "source": source_matrix,
            "position": position,
            "index": index,
            "modified": False,
            "selected": False
        }
    
    def mutate_pattern(self, cluster):
        """Modify a pattern by changing random pixels.
        
        Args:
            cluster: Pattern cluster to modify
        """
        # Mark as modified
        cluster["modified"] = True
        
        # Deep copy the matrix
        matrix = [row[:] for row in cluster["matrix"]]
        
        # Modify 1-3 bits depending on matrix size
        num_changes = min(3, max(1, self.matrix_size // 2))
        size = len(matrix)
        
        for _ in range(num_changes):
            row = random.randint(0, size - 1)
            col = random.randint(0, size - 1)
            matrix[row][col] = 1 - matrix[row][col]  # Flip 0 to 1 or 1 to 0
        
        # Update the matrix
        cluster["matrix"] = matrix
    
    def toggle_pattern_selection(self, pattern_index):
        """Toggle selection state of a pattern.
        
        Args:
            pattern_index: Index of the pattern to toggle
            
        Returns:
            True if the selection state changed
        """
        if pattern_index < 0 or pattern_index >= len(self.clusters):
            return False
        
        # Toggle selected state
        if pattern_index in self.selected_patterns:
            self.selected_patterns.remove(pattern_index)
            self.clusters[pattern_index]["selected"] = False
        else:
            self.selected_patterns.append(pattern_index)
            self.clusters[pattern_index]["selected"] = True
        
        return True
    
    def check_answers(self):
        """Check if the user's selections are correct.
        
        Returns:
            Tuple of (is_correct, score_change)
        """
        self.answered = True
        
        # Check if user selected all unmodified patterns
        correct_selections = set(range(len(self.clusters))) - set(self.modified_indices)
        user_selections = set(self.selected_patterns)
        
        is_correct = (correct_selections == user_selections)
        
        # Calculate score
        challenge_time = time.time() - self.round_start_time
        self.challenge_time = challenge_time
        
        if is_correct:
            # Calculate score based on difficulty, matrix size, and time
            base_points = self.matrix_size * 10
            time_factor = max(0.5, min(1.0, 15.0 / max(1.0, challenge_time)))
            difficulty_bonus = self.difficulty * 5
            
            score_change = int(base_points * time_factor + difficulty_bonus)
            self.score += score_change
            
            # Potentially increase level
            if self.level < 10 and random.random() < 0.3:  # 30% chance to level up
                self.level += 1
        else:
            score_change = 0
        
        self.correct_answer = is_correct
        self.game_state = "challenge_complete"
        
        return (is_correct, score_change)
    
    def start_next_round(self):
        """Start the next round with a new challenge."""
        self.create_new_challenge()
        self.game_state = "challenge_active"
    
    def _calculate_matrix_size(self):
        """Calculate matrix size based on current level.
        
        Returns:
            Matrix size (width/height)
        """
        # Size increases with level
        if self.level <= 2:
            return 3  # 3x3 matrix for levels 1-2
        elif self.level <= 5:
            return 4  # 4x4 matrix for levels 3-5
        elif self.level <= 8:
            return 5  # 5x5 matrix for levels 6-8
        else:
            return 6  # 6x6 matrix for levels 9-10
    
    def generate_random_matrix(self, size):
        """Generate a random binary matrix.
        
        Args:
            size: Width/height of the matrix
            
        Returns:
            Random binary matrix
        """
        # Create a random binary matrix with approximately 40% filled cells
        matrix = []
        for _ in range(size):
            row = []
            for _ in range(size):
                cell = 1 if random.random() < 0.4 else 0
                row.append(cell)
            matrix.append(row)
        return matrix
    
    def rotate_matrix(self, source_matrix, rotation):
        """Rotate a matrix by the specified angle.
        
        Args:
            source_matrix: Source matrix to rotate
            rotation: Rotation angle (0, 90, 180, 270)
            
        Returns:
            Rotated matrix
        """
        if rotation == 0:
            # No rotation
            return [row[:] for row in source_matrix]  # Deep copy
        
        size = len(source_matrix)
        result = [[0 for _ in range(size)] for _ in range(size)]
        
        if rotation == 90:
            # 90 degree rotation
            for r in range(size):
                for c in range(size):
                    result[c][size - 1 - r] = source_matrix[r][c]
        elif rotation == 180:
            # 180 degree rotation
            for r in range(size):
                for c in range(size):
                    result[size - 1 - r][size - 1 - c] = source_matrix[r][c]
        elif rotation == 270:
            # 270 degree rotation
            for r in range(size):
                for c in range(size):
                    result[size - 1 - c][r] = source_matrix[r][c]
        
        return result
    
    def get_state(self):
        """Get the current model state.
        
        Returns:
            Dictionary with current game state
        """
        return {
            "game_state": self.game_state,
            "level": self.level,
            "difficulty": self.difficulty,
            "matrix_size": self.matrix_size,
            "score": self.score,
            "clusters": self.clusters,
            "selected_patterns": self.selected_patterns,
            "modified_indices": self.modified_indices,
            "answered": self.answered,
            "correct_answer": self.correct_answer,
            "challenge_time": self.challenge_time,
            "total_patterns": self.total_patterns
        } 