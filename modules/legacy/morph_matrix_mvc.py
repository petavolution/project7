#!/usr/bin/env python3
"""
MorphMatrix Training Module with MVC Architecture

This module separates concerns using a Model-View-Controller pattern:
- Model: Core pattern recognition game logic
- View: UI representation and component building
- Controller: User interaction and input handling

Key features:
1. Clean separation of game logic from presentation
2. Theme-aware styling
3. Responsive grid layout
4. Optimized state management
"""

import random
import time
import math
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional, Union, Set

# Add the parent directory to sys.path for absolute imports when imported directly
if __name__ == "__main__" or not __package__:
    project_root = Path(__file__).parent.parent
    sys.path.insert(0, str(project_root))
    from MetaMindIQTrain.core.training_module import TrainingModule
    from MetaMindIQTrain.core.theme_manager import ThemeManager
else:
    # Use relative imports when imported as a module
    from ..core.training_module import TrainingModule
    from ..core.theme_manager import ThemeManager


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


class MorphMatrixView:
    """View component for MorphMatrix module - handles UI representation."""
    
    def __init__(self, model):
        """Initialize the view with reference to the model.
        
        Args:
            model: MorphMatrixModel instance
        """
        self.model = model
        self.screen_width = 800  # Default width
        self.screen_height = 600  # Default height
        
        # Grid layout properties
        self.grid_columns = 3
        self.grid_rows = 2
        self.cell_size = 30  # Will be adjusted based on matrix size
        self.pattern_margin = 20
        self.pattern_padding = 10
        
        # UI element references
        self.pattern_rects = []  # Rectangles for hit testing
        self.ui_components = []  # For component-based rendering
    
    def set_dimensions(self, width, height):
        """Set the screen dimensions.
        
        Args:
            width: Screen width
            height: Screen height
        """
        self.screen_width = width
        self.screen_height = height
        self.calculate_layout()
    
    def calculate_layout(self):
        """Calculate layout based on screen dimensions and matrix size."""
        # Calculate optimal cell size based on screen and matrix size
        matrix_size = self.model.matrix_size
        
        # Calculate pattern dimensions (each pattern is a container with a matrix)
        max_patterns_per_row = 3
        pattern_width = min(
            (self.screen_width - (max_patterns_per_row + 1) * self.pattern_margin) // max_patterns_per_row,
            (self.screen_height - 200) // 2  # Allow space for UI elements
        )
        
        # Max width 1/3 of screen, maintaining square aspect ratio
        pattern_width = min(pattern_width, self.screen_width // 3)
        pattern_height = pattern_width
        
        # Calculate cell size based on pattern size and matrix size
        available_size = pattern_width - 2 * self.pattern_padding
        self.cell_size = available_size // matrix_size
        
        # Calculate positions for patterns
        self.pattern_rects = []
        patterns_per_row = min(max_patterns_per_row, len(self.model.clusters))
        rows = math.ceil(len(self.model.clusters) / patterns_per_row)
        
        # Center the grid
        grid_width = patterns_per_row * pattern_width + (patterns_per_row - 1) * self.pattern_margin
        grid_height = rows * pattern_height + (rows - 1) * self.pattern_margin
        start_x = (self.screen_width - grid_width) // 2
        start_y = (self.screen_height - grid_height - 100) // 2 + 50  # Space for header
        
        # Calculate positions for each pattern
        for i, cluster in enumerate(self.model.clusters):
            row = i // patterns_per_row
            col = i % patterns_per_row
            
            x = start_x + col * (pattern_width + self.pattern_margin)
            y = start_y + row * (pattern_height + self.pattern_margin)
            
            # Store position in cluster
            cluster["position"] = (x, y)
            self.pattern_rects.append((x, y, pattern_width, pattern_height, i))
    
    def build_component_tree(self):
        """Build a component tree for rendering.
        
        This example uses a component-based approach with a hypothetical UI
        component system. Implement according to your actual UI component system.
        
        Returns:
            Root component of the UI tree
        """
        # Assuming a UI component system like described in ui_component.py
        # Depending on the actual implementation, you would create the
        # specific component instances here
        
        # For now, this is a placeholder that returns component specs
        # that would be used to create actual components
        
        # Root container
        root = {
            "type": "container",
            "id": "morph_matrix_root",
            "width": self.screen_width,
            "height": self.screen_height,
            "properties": {
                "style": {
                    "backgroundColor": ThemeManager.get_color("bg_color")
                }
            },
            "children": [
                # Header
                {
                    "type": "container",
                    "id": "header",
                    "x": 0,
                    "y": 0,
                    "width": self.screen_width,
                    "height": 50,
                    "properties": {
                        "style": {
                            "backgroundColor": ThemeManager.get_color("card_bg")
                        }
                    },
                    "children": [
                        # Title
                        {
                            "type": "text",
                            "id": "title",
                            "x": 20,
                            "y": 10,
                            "width": 300,
                            "height": 30,
                            "text": "MorphMatrix - Pattern Recognition",
                            "properties": {
                                "style": {
                                    "color": ThemeManager.get_color("text_color"),
                                    "fontSize": 18
                                }
                            }
                        },
                        # Score
                        {
                            "type": "text",
                            "id": "score",
                            "x": self.screen_width - 150,
                            "y": 10,
                            "width": 130,
                            "height": 30,
                            "text": f"Score: {self.model.score}",
                            "properties": {
                                "style": {
                                    "color": ThemeManager.get_color("text_color"),
                                    "textAlign": "right",
                                    "fontSize": 18
                                }
                            }
                        }
                    ]
                },
                
                # Instructions
                {
                    "type": "text",
                    "id": "instructions",
                    "x": 20,
                    "y": 60,
                    "width": self.screen_width - 40,
                    "height": 30,
                    "text": "Select all patterns that are rotations of the original pattern (blue outline).",
                    "properties": {
                        "style": {
                            "color": ThemeManager.get_color("text_color"),
                            "textAlign": "center"
                        }
                    }
                },
                
                # Pattern grid
                {
                    "type": "container",
                    "id": "pattern_grid",
                    "x": 0,
                    "y": 100,
                    "width": self.screen_width,
                    "height": self.screen_height - 150,
                    "children": self._create_pattern_components()
                },
                
                # Button container
                {
                    "type": "container",
                    "id": "button_container",
                    "x": 0,
                    "y": self.screen_height - 50,
                    "width": self.screen_width,
                    "height": 50,
                    "children": [
                        # Submit button
                        {
                            "type": "button",
                            "id": "submit_button",
                            "x": (self.screen_width - 120) // 2,
                            "y": 5,
                            "width": 120,
                            "height": 40,
                            "text": "Submit",
                            "properties": {
                                "style": {
                                    "backgroundColor": ThemeManager.get_color("primary_color"),
                                    "color": ThemeManager.get_color("text_color"),
                                    "borderRadius": 5
                                }
                            }
                        }
                    ] if self.model.game_state == "challenge_active" else [
                        # Next button (for challenge_complete state)
                        {
                            "type": "button",
                            "id": "next_button",
                            "x": (self.screen_width - 120) // 2,
                            "y": 5,
                            "width": 120,
                            "height": 40,
                            "text": "Next Challenge",
                            "properties": {
                                "style": {
                                    "backgroundColor": ThemeManager.get_color("primary_color"),
                                    "color": ThemeManager.get_color("text_color"),
                                    "borderRadius": 5
                                }
                            }
                        }
                    ]
                }
            ]
        }
        
        return root
    
    def _create_pattern_components(self):
        """Create component specs for patterns.
        
        Returns:
            List of pattern component specifications
        """
        patterns = []
        
        for i, cluster in enumerate(self.model.clusters):
            x, y = cluster["position"]
            width = height = self.pattern_rects[i][2]  # Use width from rect
            
            # Determine border color and width
            border_color = ThemeManager.get_color("primary_color") if i == 0 else ThemeManager.get_color("border_color")
            border_width = 3 if i == 0 else 1
            
            if cluster["selected"]:
                border_color = ThemeManager.get_color("accent_color")
                border_width = 2
            
            # Background color based on state
            bg_color = ThemeManager.get_color("card_bg")
            if self.model.answered:
                if i in self.model.modified_indices:
                    # Should not have been selected
                    bg_color = ThemeManager.get_color("error_color") if i in self.model.selected_patterns else bg_color
                else:
                    # Should have been selected
                    bg_color = ThemeManager.get_color("success_color") if i in self.model.selected_patterns else ThemeManager.get_color("error_color")
            
            # Create pattern container
            pattern = {
                "type": "container",
                "id": f"pattern_{i}",
                "x": x,
                "y": y,
                "width": width,
                "height": height,
                "properties": {
                    "style": {
                        "backgroundColor": bg_color,
                        "borderColor": border_color,
                        "borderWidth": border_width,
                        "borderRadius": 5
                    }
                },
                "children": self._create_matrix_cells(cluster["matrix"], x, y, width, height)
            }
            
            patterns.append(pattern)
        
        return patterns
    
    def _create_matrix_cells(self, matrix, pattern_x, pattern_y, pattern_width, pattern_height):
        """Create component specs for matrix cells.
        
        Args:
            matrix: Binary matrix data
            pattern_x: Pattern container X position
            pattern_y: Pattern container Y position
            pattern_width: Pattern container width
            pattern_height: Pattern container height
            
        Returns:
            List of cell component specifications
        """
        cells = []
        matrix_size = len(matrix)
        
        # Calculate cell size from pattern dimensions
        available_size = min(pattern_width, pattern_height) - 2 * self.pattern_padding
        cell_size = available_size // matrix_size
        
        # Calculate start position (center matrix in pattern)
        start_x = (pattern_width - (matrix_size * cell_size)) // 2
        start_y = (pattern_height - (matrix_size * cell_size)) // 2
        
        for row in range(matrix_size):
            for col in range(matrix_size):
                cell_x = start_x + col * cell_size
                cell_y = start_y + row * cell_size
                
                # Filled or empty?
                filled = matrix[row][col] == 1
                
                cell = {
                    "type": "container",
                    "id": f"cell_{row}_{col}",
                    "x": cell_x,
                    "y": cell_y,
                    "width": cell_size,
                    "height": cell_size,
                    "properties": {
                        "style": {
                            "backgroundColor": ThemeManager.get_color("accent_color") if filled else ThemeManager.get_color("card_hover"),
                            "borderColor": ThemeManager.get_color("border_color"),
                            "borderWidth": 1
                        }
                    }
                }
                
                cells.append(cell)
        
        return cells


class MorphMatrixController:
    """Controller component for MorphMatrix module - handles user interaction."""
    
    def __init__(self, model, view):
        """Initialize the controller with references to model and view.
        
        Args:
            model: MorphMatrixModel instance
            view: MorphMatrixView instance
        """
        self.model = model
        self.view = view
    
    def handle_click(self, x, y):
        """Handle mouse click event.
        
        Args:
            x: X coordinate of click
            y: Y coordinate of click
            
        Returns:
            Dictionary with result and updated state
        """
        if self.model.game_state == "challenge_active":
            # Check for pattern clicks
            pattern_index = self._get_clicked_pattern(x, y)
            if pattern_index >= 0:
                # Toggle pattern selection
                self.model.toggle_pattern_selection(pattern_index)
                return {"result": "pattern_toggled", "pattern": pattern_index, "state": self.model.get_state()}
            
            # Check for submit button
            submit_button_rect = self._get_submit_button_rect()
            if self._is_point_in_rect(x, y, submit_button_rect):
                # Check answers
                is_correct, score_change = self.model.check_answers()
                return {"result": "answer_submitted", "correct": is_correct, "score_change": score_change, "state": self.model.get_state()}
        
        elif self.model.game_state == "challenge_complete":
            # Check for next button
            next_button_rect = self._get_next_button_rect()
            if self._is_point_in_rect(x, y, next_button_rect):
                # Start next round
                self.model.start_next_round()
                # Recalculate view layout
                self.view.calculate_layout()
                return {"result": "next_round", "state": self.model.get_state()}
        
        # Default: no action
        return {"result": "no_action", "state": self.model.get_state()}
    
    def _get_clicked_pattern(self, x, y):
        """Get the index of the pattern clicked.
        
        Args:
            x: X coordinate of click
            y: Y coordinate of click
            
        Returns:
            Pattern index or -1 if no pattern was clicked
        """
        for rect in self.view.pattern_rects:
            rect_x, rect_y, rect_width, rect_height, pattern_index = rect
            if self._is_point_in_rect(x, y, (rect_x, rect_y, rect_width, rect_height)):
                return pattern_index
        
        return -1
    
    def _get_submit_button_rect(self):
        """Get the rect for the submit button.
        
        Returns:
            Tuple of (x, y, width, height)
        """
        x = (self.view.screen_width - 120) // 2
        y = self.view.screen_height - 45
        width = 120
        height = 40
        return (x, y, width, height)
    
    def _get_next_button_rect(self):
        """Get the rect for the next button.
        
        Returns:
            Tuple of (x, y, width, height)
        """
        x = (self.view.screen_width - 120) // 2
        y = self.view.screen_height - 45
        width = 120
        height = 40
        return (x, y, width, height)
    
    def _is_point_in_rect(self, x, y, rect):
        """Check if a point is inside a rectangle.
        
        Args:
            x: X coordinate of point
            y: Y coordinate of point
            rect: Tuple of (rect_x, rect_y, rect_width, rect_height)
            
        Returns:
            True if the point is inside the rectangle
        """
        rect_x, rect_y, rect_width, rect_height = rect
        return (rect_x <= x <= rect_x + rect_width and
                rect_y <= y <= rect_y + rect_height)


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