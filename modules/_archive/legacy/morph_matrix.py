#!/usr/bin/env python3
"""
MorphMatrix Training Module

An integrated pattern recognition module that combines binary matrix manipulation
with visual pattern recognition challenges. This module tests users' ability to:
1. Recognize rotated patterns
2. Identify patterns that have been mutated (with changed pixels)
3. Understand spatial transformations

The module builds on the RectCluster pattern matrix foundation.

Optimizations:
- Dynamic resolution handling for any screen size
- State tracking for optimal delta encoding
- Component-based rendering for flexible UI
- Adaptive difficulty scaling
"""

import sys
import random
import time
from pathlib import Path
from typing import List, Tuple, Dict, Any, Set

# Add the parent directory to sys.path for absolute imports when imported directly
if __name__ == "__main__" or not __package__:
    project_root = Path(__file__).parent.parent
    sys.path.insert(0, str(project_root))
    from MetaMindIQTrain.core.training_module import TrainingModule
else:
    # Use relative imports when imported as a module
    from ..core.training_module import TrainingModule

# Conditionally import pygame - allows core logic to work without UI
try:
    import pygame
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False
    print("Warning: pygame not available, using headless mode for MorphMatrix")


class MorphMatrix(TrainingModule):
    """
    MorphMatrix training module with pattern recognition challenges.
    
    This module presents pattern matrices in various orientations and transformations.
    Users must identify which patterns are pure rotations vs. which ones have been
    modified with pixel changes.
    """
    
    # Static cell dimensions
    CELL_WIDTH = 30
    CELL_HEIGHT = 30
    
    def __init__(self, difficulty=1):
        """Initialize the MorphMatrix module.
        
        Args:
            difficulty: Initial difficulty level
        """
        # Initialize base class
        super().__init__()
        
        # Module settings
        self.name = "morph_matrix"
        self.display_name = "MorphMatrix"
        self.description = "Identify patterns that are exact rotations of the original pattern"
        self.difficulty = difficulty
        self.level = difficulty
        self.matrix_size = 5  # Default size, will be adjusted based on level
        
        # Track properties for efficient delta generation
        self._tracked_properties = self._tracked_properties.union({
            'difficulty', 'level', 'matrix_size', 'game_state', 
            'clusters', 'original_matrix', 'selected_clusters',
            'answered', 'correct_answer', 'score', 'modified_indices',
            'selected_patterns', 'total_patterns'
        })
        
        # State
        self.clusters = []
        self.original_matrix = None
        self.selected_clusters = []
        self.answered = False
        self.correct_answer = None
        self.score = 0
        self.game_state = "challenge_active"
        self.modified_indices = []
        self.selected_patterns = []
        self.total_patterns = 0
        self.start_time = time.time()
        self.challenge_time = 0
        
        # Grid layout settings
        self.patterns_per_row = 3  # Default value for grid layout
        
        # Performance tracking
        self.last_state_hash = None
        self.state_changes = 0
        
        # Screen dimensions - will be used for scaling
        self.screen_width = self.__class__.SCREEN_WIDTH
        self.screen_height = self.__class__.SCREEN_HEIGHT
        
        # Calculate cell dimensions based on screen size
        # This ensures proper scaling on all resolutions
        self.calculate_cell_dimensions()
        
        # Default colors for rendering
        self.color1 = (240, 240, 240)  # Light color for 0 cells
        self.color2 = (50, 50, 200)    # Blue for 1 cells
        
        # UI elements - only initialize if pygame is available
        self.font = None
        if PYGAME_AVAILABLE:
            try:
                self.font = pygame.font.SysFont('Arial', int(self.screen_height * 0.022))
            except:
                pass  # Fail silently if font can't be loaded
        
        self.message = "Select patterns that are exact rotations of the original (blue outlined) pattern"
        
        # Initialize the first challenge
        self.create_new_challenge()
    
    @staticmethod
    def get_name():
        """Get the name of the module."""
        return "Morph Matrix"
    
    @staticmethod
    def get_description():
        """Get the description of the module."""
        return "Identify rotated vs. mutated patterns"
    
    def start_challenge(self):
        """Start a new pattern recognition challenge.
        
        This is an alias for create_new_challenge for consistency with other modules.
        """
        self.create_new_challenge()
    
    def create_new_challenge(self):
        """Create a new pattern recognition challenge.
        
        This creates a new original pattern and several variations,
        some that are pure rotations and some that are modified.
        """
        # Adjust matrix size based on level
        # More advanced levels have larger matrices
        if self.level <= 3:
            self.matrix_size = 5
        elif self.level <= 6:
            self.matrix_size = 6
        elif self.level <= 9:
            self.matrix_size = 7
        else:
            self.matrix_size = 8
        
        # Recalculate cell dimensions for the new matrix size
        self.calculate_cell_dimensions()
        
        # Reset state
        self.clusters = []
        self.selected_clusters = []
        self.selected_patterns = []
        self.answered = False
        
        # Create the original pattern
        self.original_matrix = self.generate_random_matrix(self.matrix_size)
        
        # Number of patterns to display depends on level
        if self.level <= 2:
            num_patterns = 4
            self.patterns_per_row = 2
        elif self.level <= 5:
            num_patterns = 6
            self.patterns_per_row = 3
        else:
            num_patterns = 9
            self.patterns_per_row = 3
        
        # Number of modified patterns (harder as level increases)
        if self.level <= 3:
            num_modified = 1
        elif self.level <= 6:
            num_modified = 2
        else:
            num_modified = 3
            
        self.total_patterns = num_patterns
        
        # Create pattern variations
        self.create_pattern_variations(num_patterns, num_modified)
        
        # Record challenge start time
        self.challenge_time = time.time()
        
        # Reset game state
        self.game_state = "challenge_active"
        self.message = "Select patterns that are exact rotations of the original (blue outlined) pattern"
        
        # Update state change counter for delta tracking
        self.state_changes += 1
    
    def generate_random_matrix(self, size: int) -> List[List[int]]:
        """Generate a random binary matrix.
        
        Args:
            size: Size of the matrix (size x size)
            
        Returns:
            A 2D matrix of 0s and 1s
        """
        # Create empty matrix
        matrix = [[0 for _ in range(size)] for _ in range(size)]
        
        # Fill with random values, with a bias toward 0s to create clearer patterns
        for r in range(size):
            for c in range(size):
                matrix[r][c] = 1 if random.random() < 0.4 else 0
        
        return matrix
    
    def create_cluster(self, source_matrix: List[List[int]], rotation: int, index: int, position: Tuple[int, int] = None) -> Dict[str, Any]:
        """Create a cluster with the provided matrix and rotation.
        
        Args:
            source_matrix: The source binary matrix
            rotation: Rotation value (0=none, 1=90°, 2=180°, 3=270°)
            index: Index of this cluster in the grid
            position: Optional tuple (x, y) for explicit positioning
            
        Returns:
            A dictionary with cluster data
        """
        # Create a deep copy of the source matrix
        matrix = [row[:] for row in source_matrix]
        
        # Apply rotation
        if rotation == 1:  # 90° clockwise
            matrix = [[matrix[self.matrix_size-1-j][i] for j in range(self.matrix_size)] for i in range(self.matrix_size)]
        elif rotation == 2:  # 180°
            matrix = [[matrix[self.matrix_size-1-i][self.matrix_size-1-j] for j in range(self.matrix_size)] for i in range(self.matrix_size)]
        elif rotation == 3:  # 270° clockwise
            matrix = [[matrix[j][self.matrix_size-1-i] for j in range(self.matrix_size)] for i in range(self.matrix_size)]
        
        # Create cluster dict - position will be calculated during rendering
        cluster = {
            'matrix': matrix,
            'size': self.matrix_size,
            'rotation': rotation,
            'index': index,
            'is_selected': False,
            'is_original': index == 0
        }
        
        # Add position if provided
        if position:
            cluster['position'] = position
        
        return cluster
    
    def mutate_pattern(self, cluster: Dict[str, Any]):
        """Toggle a random cell in the pattern matrix.
        
        Args:
            cluster: The cluster to mutate
        """
        matrix = cluster["matrix"]
        size = cluster["size"]
        
        # Select a random cell
        r1 = random.randint(0, size - 1)
        r2 = random.randint(0, size - 1)
        
        # Toggle the cell (0 to 1, or 1 to 0)
        matrix[r1][r2] = 1 - matrix[r1][r2]
    
    def toggle_pattern_selection(self, pattern_index: int):
        """Toggle the selection state of a pattern.
        
        Args:
            pattern_index: Index of the pattern to toggle
            
        Returns:
            True if the pattern was selected, False if deselected
        """
        # Check if valid index
        if pattern_index < 0 or pattern_index >= len(self.clusters):
            return False
            
        # Don't allow selecting the original pattern
        if self.clusters[pattern_index].get('is_original', False):
            return False
            
        # Toggle selected state in the cluster data structure
        self.clusters[pattern_index]['is_selected'] = not self.clusters[pattern_index].get('is_selected', False)
        
        # Update selected_patterns list to stay in sync
        is_selected = self.clusters[pattern_index]['is_selected']
        
        if is_selected and pattern_index not in self.selected_patterns:
            self.selected_patterns.append(pattern_index)
            return True
        elif not is_selected and pattern_index in self.selected_patterns:
            self.selected_patterns.remove(pattern_index)
            return False
            
        return is_selected
    
    def check_answers(self):
        """Check if the selected patterns match the correct answers.
        
        Returns:
            Dict with results including score and feedback
        """
        # Calculate how many answers are correct
        correct_answers = 0
        total_correct = self.total_patterns - len(self.modified_indices)
        
        # Check each pattern
        for i in range(self.total_patterns):
            is_modified = i in self.modified_indices
            is_selected = i in self.selected_patterns
            
            # If not modified and selected, or modified and not selected, it's correct
            if (not is_modified and is_selected) or (is_modified and not is_selected):
                correct_answers += 1
        
        # Calculate score for this round
        round_score = correct_answers * 10
        
        # Perfect score bonus
        if correct_answers == self.total_patterns:
            round_score += 20 * self.level  # More bonus for higher levels
        
        # Time bonus (faster completion = more points)
        time_taken = time.time() - self.start_time
        if time_taken < 30:  # If completed in less than 30 seconds
            time_bonus = int((30 - time_taken) / 2)
            round_score += time_bonus
        
        # Update total score
        self.score += round_score
        
        # Update game state
        self.game_state = "results"
        self.end_time = time.time()
        
        # Prepare results
        results = {
            "correct_answers": correct_answers,
            "total_correct": total_correct,
            "total_patterns": self.total_patterns,
            "round_score": round_score,
            "total_score": self.score,
            "time_taken": time_taken
        }
        
        # Set appropriate message based on performance
        if correct_answers == self.total_patterns:
            self.message = f"Perfect! {correct_answers}/{self.total_patterns} correct. +{round_score} points!"
        elif correct_answers >= total_correct:
            self.message = f"Good job! {correct_answers}/{self.total_patterns} correct. +{round_score} points!"
        else:
            self.message = f"Try again! {correct_answers}/{self.total_patterns} correct. +{round_score} points!"
        
        # Return both the results dictionary and the updated state
        return {
            "result": results,
            "state": self.get_state()
        }
    
    def advance_level(self):
        """Advance to the next level and create a new challenge."""
        self.difficulty += 1
        self.level = self.difficulty
        self.game_state = "challenge_active"
        self.create_new_challenge()
        
        # Make game harder as levels progress
        if self.level > 5:
            # Make matrices more similar with fewer mutations
            pass
    
    def handle_mouse_click(self, pos):
        """Handle mouse click event.
        
        Args:
            pos: Mouse position tuple (x, y)
        """
        if self.answered:
            # If already answered, clicking just moves to next challenge
            self.create_new_challenge()
            return
        
        x, y = pos
        
        # Check if any pattern was clicked
        for i, cluster in enumerate(self.clusters):
            pattern_pos = cluster["position"]
            pattern_width = cluster["size"] * self.CELL_WIDTH + 2
            pattern_height = cluster["size"] * self.CELL_HEIGHT + 2
            
            # Skip the original pattern (index 0)
            if i == 0:
                continue
                
            # Create a rectangle for hit testing
            if PYGAME_AVAILABLE:
                pattern_rect = pygame.Rect(pattern_pos[0], pattern_pos[1], pattern_width, pattern_height)
                if pattern_rect.collidepoint(x, y):
                    self.toggle_pattern_selection(i)
                    break
            else:
                # Simple collision detection without pygame
                px, py = pattern_pos
                if (px <= x <= px + pattern_width) and (py <= y <= py + pattern_height):
                    self.toggle_pattern_selection(i)
                    break
    
    def check_answer(self):
        """Check if the selected patterns match the correct rotations.
        
        Returns:
            dict: Result with success status and details
        """
        self.answered = True
        
        # In our layout, index 1 is always the original pattern at the top center
        # We need to identify which patterns are NOT modified (exact rotations)
        # and which ones the user selected
        selected_indices = [i for i, cluster in enumerate(self.clusters) if cluster.get('is_selected', False)]
        
        # All non-modified patterns except the original are correct answers
        correct_indices = [i for i, cluster in enumerate(self.clusters) 
                          if not cluster.get('is_modified', False) and not cluster.get('is_original', False)]
        
        # Calculate score
        correct_count = len([i for i in selected_indices if i in correct_indices])
        incorrect_count = len([i for i in selected_indices if i not in correct_indices])
        missed_count = len([i for i in correct_indices if i not in selected_indices])
        
        # Calculate the total score percentage
        total_possible = len(correct_indices)
        score_percentage = 0
        if total_possible > 0:
            score_percentage = int((correct_count / total_possible) * 100)
            # Penalize incorrect selections
            score_percentage = max(0, score_percentage - (incorrect_count * 20))
        
        # Determine success (need at least 70% for success)
        success = score_percentage >= 70
        
        # Generate a detailed result message
        message = f"You selected {correct_count} correct and {incorrect_count} incorrect patterns."
        if missed_count > 0:
            message += f" You missed {missed_count} correct patterns."
        
        # Update the state based on result
        if success:
            self.difficulty += 1
            self.level = self.difficulty
            result_message = f"Good job! Score: {score_percentage}%. Advancing to level {self.level}."
        else:
            result_message = f"Try again. Score: {score_percentage}%. Need at least 70% to advance."
        
        # Store the correct answer for reference
        self.correct_answer = correct_indices
        
        # Create result object
        result = {
            "success": success,
            "score": score_percentage,
            "message": result_message,
            "details": message,
            "level": self.level,
            "correct_indices": correct_indices,
            "selected_indices": selected_indices
        }
        
        return result
    
    def get_state(self):
        """Get the current state of the module.
        
        Returns:
            dict: Current state
        """
        # Return all relevant state
        return {
            'level': self.level,
            'score': self.difficulty * 10,  # Just an example score based on difficulty
            'message': self.message,
            'clusters': self.clusters,
            'matrix_size': self.matrix_size,
            'selected_patterns': [i for i, cluster in enumerate(self.clusters) if cluster.get('is_selected', False)],
            'answered': self.answered,
            'correct_answer': self.correct_answer,
            'help_text': self._get_help_text(),
            'game_state': 'challenge_active' if not self.answered else 'results'
        }
    
    def _get_help_text(self):
        """Get the help text for the module.
        
        Returns:
            str: Help text
        """
        help_text = [
            "MORPH MATRIX - PATTERN RECOGNITION",
            "-----------------------------------",
            "The ORIGINAL PATTERN is shown at the top center with a blue double outline.",
            "Your task is to select all patterns that are EXACT ROTATIONS of the original pattern.",
            "Some patterns have had one or more pixels changed - avoid selecting these.",
            "",
            "Controls:",
            "- Click on a pattern to select/deselect it",
            "- Press SPACE to check your answer",
            "- Press R to reset the level",
            "- Press A to advance to the next level",
            "- Press ESC to exit"
        ]
        return "\n".join(help_text)
    
    def reset_level(self):
        """Reset the current level."""
        self.create_new_challenge()
        
    def process_input(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process input from the user.
        
        Args:
            input_data: Dictionary with input data
            
        Returns:
            Response dictionary
        """
        result = {"success": False, "message": "Invalid input"}
        
        # Handle mouse clicks
        if "click_position" in input_data:
            x, y = input_data["click_position"]
            self.handle_mouse_click((x, y))
            result = {
                "success": True,
                "message": "Pattern selection updated"
            }
        
        # Handle explicit action commands
        elif "action" in input_data:
            action = input_data["action"]
            
            if action == "check_answer":
                result = self.check_answer()
            
            elif action == "next_level" or action == "advance_level":
                self.advance_level()
                result = {
                    "success": True,
                    "message": f"Advanced to level {self.level}",
                    "level": self.level
                }
            
            elif action == "reset_level":
                self.reset_level()
                result = {
                    "success": True,
                    "message": f"Reset to level {self.level}"
                }
        
        return {"result": result, "state": self.get_state()}

    def calculate_cell_dimensions(self):
        """Calculate cell dimensions based on screen size and matrix complexity.
        
        This ensures the module scales properly across different resolutions.
        """
        # Calculate the maximum number of matrices that might be displayed
        max_matrices = 9  # Maximum number of matrices we might show
        
        # Calculate the available area for matrices
        content_height = self.screen_height * 0.7  # Use 70% of screen height for matrices
        content_width = self.screen_width * 0.9   # Use 90% of screen width
        
        # Calculate how many matrices we can fit per row
        matrices_per_row = min(3, max_matrices)  # Maximum 3 per row
        
        # Calculate how many rows we need
        rows_needed = max(1, (max_matrices + matrices_per_row - 1) // matrices_per_row)
        
        # Calculate the maximum matrix size that will fit
        max_matrix_height = content_height / rows_needed
        max_matrix_width = content_width / matrices_per_row
        
        # Determine maximum cell size based on matrix size and available space
        max_cell_height = max_matrix_height / (self.matrix_size + 2)  # +2 for padding
        max_cell_width = max_matrix_width / (self.matrix_size + 2)   # +2 for padding
        
        # Take the smaller dimension to ensure square cells that fit
        cell_size = min(max_cell_height, max_cell_width)
        
        # Ensure minimum cell size for visibility but scale with resolution
        min_size = self.screen_height * 0.015  # 1.5% of screen height minimum
        
        # Set cell dimensions
        self.CELL_WIDTH = max(min_size, cell_size)
        self.CELL_HEIGHT = max(min_size, cell_size)
        
        # Round to integer pixels
        self.CELL_WIDTH = int(self.CELL_WIDTH)
        self.CELL_HEIGHT = int(self.CELL_HEIGHT)
        
        # Ensure minimum size
        self.CELL_WIDTH = max(5, self.CELL_WIDTH)
        self.CELL_HEIGHT = max(5, self.CELL_HEIGHT)

    def create_pattern_variations(self, num_patterns, num_modified):
        """Create pattern variations based on the given parameters.
        
        Args:
            num_patterns: Total number of patterns to create
            num_modified: Number of modified patterns
        """
        # Create the original pattern
        original_pattern = self.original_matrix
        
        # Create the modified patterns
        modified_patterns = []
        for _ in range(num_modified):
            modified_pattern = self.mutate_matrix(original_pattern)
            modified_patterns.append(modified_pattern)
        
        # Create the pure rotation patterns
        rotation_patterns = []
        for _ in range(num_patterns - num_modified):
            rotation_pattern = self.rotate_matrix(original_pattern, random.choice([90, 180, 270]))
            rotation_patterns.append(rotation_pattern)
        
        # Combine all patterns
        self.clusters = [
            self.create_cluster(original_pattern, 0, 0),
            *[self.create_cluster(pattern, rotation, i) for i, pattern in enumerate(modified_patterns)],
            *[self.create_cluster(pattern, rotation, i + num_modified) for i, pattern in enumerate(rotation_patterns)]
        ]
    
    def generate_random_matrix(self, size):
        """Generate a random binary matrix of the given size.
        
        Args:
            size: Size of the matrix (size x size)
            
        Returns:
            A 2D matrix of 0s and 1s
        """
        # Create a random binary matrix with roughly 50% filled cells
        return [[random.randint(0, 1) for _ in range(size)] for _ in range(size)]
    
    def mutate_matrix(self, matrix):
        """Apply random mutations to the matrix.
        
        Args:
            matrix: The matrix to mutate
            
        Returns:
            Mutated matrix
        """
        # Clone the matrix to avoid modifying the original
        matrix_copy = [row[:] for row in matrix]
        size = len(matrix_copy)
        
        # Apply mutations
        for _ in range(random.randint(1, 3)):
            row = random.randint(0, size - 1)
            col = random.randint(0, size - 1)
            matrix_copy[row][col] = 1 - matrix_copy[row][col]
        
        return matrix_copy
    
    def rotate_matrix(self, source_matrix: List[List[int]], rotation: int) -> List[List[int]]:
        """Rotate a matrix by the specified amount.
        
        Args:
            source_matrix: Original matrix to rotate
            rotation: Rotation value (1=90°, 2=180°, 3=270°)
            
        Returns:
            Rotated matrix
        """
        size = len(source_matrix)
        rotated = [[0 for _ in range(size)] for _ in range(size)]
        
        if rotation == 1:  # 90° clockwise
            for i in range(size):
                for j in range(size):
                    rotated[i][j] = source_matrix[size - 1 - j][i]
        elif rotation == 2:  # 180°
            for i in range(size):
                for j in range(size):
                    rotated[i][j] = source_matrix[size - 1 - i][size - 1 - j]
        elif rotation == 3:  # 270° clockwise
            for i in range(size):
                for j in range(size):
                    rotated[i][j] = source_matrix[j][size - 1 - i]
        
        return rotated

    def handle_click(self, x, y):
        """Handle a click at the specified coordinates.
        
        This is an abstract method required by the TrainingModule base class.
        
        Args:
            x: X coordinate of the click
            y: Y coordinate of the click
            
        Returns:
            dict: Result of the click operation
        """
        # Delegate to our more specific implementation
        self.handle_mouse_click((x, y))
        
        # Return a result dictionary as expected by the framework
        selected_count = len([c for c in self.clusters if c.get('is_selected', False)])
        
        return {
            "success": True,
            "message": f"Selected {selected_count} patterns",
            "selected_indices": [i for i, c in enumerate(self.clusters) if c.get('is_selected', False)]
        }


# Helper function to paint a cluster using a graphics adapter (for renderer integration)
def paint_cluster(cluster: Dict[str, Any], gfx) -> None:
    """Render a pattern cluster to a graphics context.
    
    This helper function implements the exact logic needed to render a pattern cluster
    using the provided graphics context. It can be used by renderers to display clusters.
    
    Args:
        cluster: Cluster data including matrix and position
        gfx: Graphics context with set_color() and draw_rect() methods
    """
    # Only attempt to paint if pygame is available
    if not PYGAME_AVAILABLE:
        return
        
    matrix = cluster["matrix"]
    x_pos, y_pos = cluster["position"]
    size = cluster["size"]
    color1 = cluster["color1"]
    color2 = cluster["color2"]
    cell_width = MorphMatrix.CELL_WIDTH
    cell_height = MorphMatrix.CELL_HEIGHT
    
    # Draw each cell
    for row in range(size):
        for col in range(size):
            # Calculate position for this cell
            cell_x = x_pos + 1 + col * cell_width
            cell_y = y_pos + 1 + row * cell_height
            
            # Set color based on cell value
            if matrix[row][col] == 0:
                gfx.set_color(color1)
            else:
                gfx.set_color(color2)
            
            # Draw the cell
            gfx.draw_rect(cell_x, cell_y, cell_width, cell_height)


# Example usage when run directly
if __name__ == "__main__":
    module = MorphMatrix()
    print(f"Created {module.get_name()} module")
    print(f"Description: {module.get_description()}")
    print(f"Initial state: level={module.level}, score={module.score}")
    
    # Create a new challenge
    module.create_new_challenge()
    print(f"Generated challenge with {len(module.clusters)} patterns")
    print(f"Modified patterns: {len(module.modified_indices)}")
    
    # Simulate some user interaction
    print("\nSimulating user selections...")
    for i in range(module.total_patterns):
        if i not in module.modified_indices:
            module.toggle_pattern_selection(i)
            print(f"Selected pattern {i+1} (correct)")
    
    # Check answers
    results = module.check_answers()
    print(f"\nResults: {module.message}")
    print(f"Score: {module.score}")
    
    # Advance to next level
    module.advance_level()
    print(f"\nAdvanced to level {module.level}") 