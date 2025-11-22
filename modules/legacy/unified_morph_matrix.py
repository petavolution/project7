#!/usr/bin/env python3
"""
Unified Morph Matrix Module

An optimized version of the MorphMatrix module using the unified component system.
This module tests pattern recognition by displaying matrix patterns in various
rotations and transformations.

Optimizations:
1. Uses component memoization and caching
2. Implements declarative UI with automatic diffing
3. Efficiently updates only changed components
4. Implements batch rendering for improved performance
5. Uses adaptive grid sizing for different screen resolutions
"""

import random
import time
import math
import logging
from typing import Dict, List, Any, Optional, Tuple, Set

# Try to import the unified component system
try:
    from MetaMindIQTrain.core.unified_component_system import (
        Component, ComponentFactory, UI
    )
except ImportError:
    # For direct execution or during development
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from core.unified_component_system import (
        Component, ComponentFactory, UI
    )

# Configure logging
logger = logging.getLogger(__name__)

# Module states
STATE_INTRO = "intro"
STATE_CHALLENGE = "challenge"
STATE_RESULT = "result"

class UnifiedMorphMatrix:
    """Pattern recognition training module using the unified component system."""
    
    def __init__(self):
        """Initialize the morph matrix module."""
        # Configuration
        self.level = 1
        self.matrix_size = 5  # Default size, will be adjusted based on level
        
        # State
        self.state = STATE_INTRO
        self.clusters = []
        self.original_matrix = None
        self.selected_clusters = []
        self.modified_indices = []
        self.answered = False
        self.score = 0
        self.high_score = 0
        self.total_patterns = 0
        self.selected_patterns = []
        self.correct_answers = []
        self.start_time = time.time()
        self.patterns_per_row = 3
        
        # UI components
        self.ui = None
        self.screen_width = 1440  # Default width
        self.screen_height = 1024  # Default height
        
        # Colors
        self.color1 = (240, 240, 240)  # Light color for 0 cells
        self.color2 = (50, 50, 200)    # Blue for 1 cells
        
        # Messages
        self.message = "Select patterns that are exact rotations of the original (blue outlined) pattern"
        
        # Optimization
        self.needs_redraw = True  # Force full redraw on first frame
        self.last_state = None  # Previous state for change detection
    
    def initialize(self):
        """Initialize the module."""
        logger.info("Initializing Morph Matrix module")
        # Reset state
        self.state = STATE_INTRO
        self.score = 0
        self.level = 1
        self.matrix_size = 5
        self.clusters = []
        self.selected_clusters = []
    
    def shutdown(self):
        """Clean up resources."""
        logger.info("Shutting down Morph Matrix module")
    
    def update(self):
        """Update module state."""
        pass  # No time-based updates needed for this module
    
    def build_ui(self) -> UI:
        """Build the user interface.
        
        Returns:
            UI object with the component hierarchy
        """
        # Create a new UI if not exists
        if not self.ui:
            self.ui = UI(self.screen_width, self.screen_height)
        
        # Clear existing components if we need a full redraw
        if self.needs_redraw:
            self.ui.clear()
            
            # Build UI based on current state
            if self.state == STATE_INTRO:
                self._build_intro_ui()
            elif self.state == STATE_CHALLENGE:
                self._build_challenge_ui()
            elif self.state == STATE_RESULT:
                self._build_result_ui()
            
            # Reset flag
            self.needs_redraw = False
            self.last_state = self.state
        
        return self.ui
    
    def get_state(self) -> Dict[str, Any]:
        """Get the current state for rendering.
        
        Returns:
            State dictionary
        """
        return {
            "ui": self.ui.to_dict() if self.ui else {},
            "state": self.state,
            "level": self.level,
            "score": self.score,
            "high_score": self.high_score
        }
    
    def handle_click(self, component_id: str, pos: Tuple[int, int]):
        """Handle a click event.
        
        Args:
            component_id: ID of the clicked component
            pos: Click position (x, y)
        """
        logger.debug(f"Click on component {component_id} at {pos}")
        
        if self.state == STATE_INTRO:
            if component_id == "start_button":
                self.start_challenge()
        
        elif self.state == STATE_CHALLENGE:
            # Check if it's a pattern click
            if component_id.startswith("pattern_"):
                try:
                    # Extract pattern index from ID (format: pattern_index)
                    parts = component_id.split("_")
                    pattern_index = int(parts[1])
                    
                    # Toggle pattern selection
                    self.toggle_pattern_selection(pattern_index)
                    
                    # Mark UI for update
                    self.needs_redraw = True
                    
                except (IndexError, ValueError) as e:
                    logger.error(f"Error parsing pattern ID: {e}")
            
            # Check if it's the submit button
            elif component_id == "submit_button":
                self.check_answers()
        
        elif self.state == STATE_RESULT:
            if component_id == "continue_button":
                self.start_challenge()
            elif component_id == "menu_button":
                self.state = STATE_INTRO
                self.needs_redraw = True
    
    def handle_key(self, key: int):
        """Handle a key press event.
        
        Args:
            key: Key code
        """
        logger.debug(f"Key press: {key}")
        
        # Handle specific keys depending on state
        if self.state == STATE_INTRO:
            # Start game on space or enter
            if key in (13, 32):  # Enter or Space
                self.start_challenge()
        
        elif self.state == STATE_CHALLENGE:
            # Submit on Enter
            if key == 13:  # Enter
                self.check_answers()
            
            # Cancel on Escape
            elif key == 27:  # Escape
                self.state = STATE_INTRO
                self.needs_redraw = True
    
    def start_challenge(self):
        """Start a new pattern recognition challenge."""
        logger.info(f"Starting new challenge at level {self.level}")
        
        # Adjust matrix size based on level
        if self.level <= 3:
            self.matrix_size = 5
        elif self.level <= 6:
            self.matrix_size = 6
        elif self.level <= 9:
            self.matrix_size = 7
        else:
            self.matrix_size = 8
        
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
        
        # Set game state
        self.state = STATE_CHALLENGE
        self.needs_redraw = True
    
    def toggle_pattern_selection(self, pattern_index: int):
        """Toggle selection state of a pattern.
        
        Args:
            pattern_index: Index of the pattern to toggle
        """
        if pattern_index in self.selected_patterns:
            self.selected_patterns.remove(pattern_index)
        else:
            self.selected_patterns.append(pattern_index)
    
    def check_answers(self):
        """Check answers and calculate score."""
        logger.info("Checking answers")
        
        # Count correct selections
        correct = 0
        incorrect = 0
        
        # Check each pattern
        for i in range(len(self.clusters)):
            is_selected = i in self.selected_patterns
            is_rotation = i not in self.modified_indices
            
            if is_selected and is_rotation:
                correct += 1
            elif is_selected and not is_rotation:
                incorrect += 1
            elif not is_selected and not is_rotation:
                correct += 1
            elif not is_selected and is_rotation:
                incorrect += 1
        
        # Calculate score
        total_points = len(self.clusters)
        score_add = int((correct / total_points) * 100)
        
        # Update score
        self.score += score_add
        
        # Update high score if needed
        if self.score > self.high_score:
            self.high_score = self.score
        
        # Level up if accuracy is high enough
        if correct == total_points:
            self.level += 1
        
        # Store correct answers for display
        self.correct_answers = [i for i in range(len(self.clusters)) if i not in self.modified_indices]
        
        # Transition to result state
        self.state = STATE_RESULT
        self.needs_redraw = True
    
    def _build_intro_ui(self):
        """Build the intro screen UI."""
        # Add a title
        title = ComponentFactory.text(
            text="Morph Matrix",
            x=0, y=100, width=self.screen_width, height=80,
            color=(255, 255, 255),
            fontSize=48,
            textAlign='center'
        )
        self.ui.add(title)
        
        # Add description
        description = ComponentFactory.text(
            text="Identify exact rotations of the original pattern.",
            x=0, y=200, width=self.screen_width, height=40,
            color=(220, 220, 220),
            fontSize=24,
            textAlign='center'
        )
        self.ui.add(description)
        
        # Add level and score info
        if self.level > 1 or self.score > 0:
            info = ComponentFactory.text(
                text=f"Level: {self.level}   Score: {self.score}   High Score: {self.high_score}",
                x=0, y=260, width=self.screen_width, height=30,
                color=(180, 180, 200),
                fontSize=20,
                textAlign='center'
            )
            self.ui.add(info)
        
        # Add start button
        start_button = ComponentFactory.button(
            id="start_button",
            text="Start Challenge",
            x=(self.screen_width - 200) // 2, 
            y=350,
            width=200, height=60,
            backgroundColor=(60, 120, 255),
            color=(255, 255, 255),
            borderRadius=10,
            fontSize=24
        )
        self.ui.add(start_button)
    
    def _build_challenge_ui(self):
        """Build the challenge screen UI."""
        # Add a title
        title = ComponentFactory.text(
            text="Morph Matrix Challenge",
            x=0, y=40, width=self.screen_width, height=40,
            color=(255, 255, 255),
            fontSize=32,
            textAlign='center'
        )
        self.ui.add(title)
        
        # Add instruction
        instruction = ComponentFactory.text(
            text=self.message,
            x=0, y=90, width=self.screen_width, height=30,
            color=(220, 220, 100),
            fontSize=20,
            textAlign='center'
        )
        self.ui.add(instruction)
        
        # Add patterns
        self._add_pattern_grid()
        
        # Add submit button
        submit_button = ComponentFactory.button(
            id="submit_button",
            text="Submit",
            x=(self.screen_width - 160) // 2,
            y=self.screen_height - 120,
            width=160, height=50,
            backgroundColor=(60, 200, 100),
            color=(255, 255, 255),
            borderRadius=8,
            fontSize=22
        )
        self.ui.add(submit_button)
    
    def _build_result_ui(self):
        """Build the result screen UI."""
        # Add a title
        title = ComponentFactory.text(
            text="Results",
            x=0, y=80, width=self.screen_width, height=60,
            color=(255, 255, 255),
            fontSize=36,
            textAlign='center'
        )
        self.ui.add(title)
        
        # Count correct answers
        correct = 0
        total = len(self.clusters)
        
        for i in range(total):
            is_selected = i in self.selected_patterns
            is_rotation = i not in self.modified_indices
            
            if (is_selected and is_rotation) or (not is_selected and not is_rotation):
                correct += 1
        
        # Add score info
        accuracy = correct / total
        score_text = f"Correct: {correct}/{total} ({accuracy*100:.1f}%)"
        
        score_info = ComponentFactory.text(
            text=score_text,
            x=0, y=160, width=self.screen_width, height=40,
            color=(220, 220, 100),
            fontSize=28,
            textAlign='center'
        )
        self.ui.add(score_info)
        
        # Add total score
        total_score = ComponentFactory.text(
            text=f"Total Score: {self.score}   High Score: {self.high_score}",
            x=0, y=220, width=self.screen_width, height=30,
            color=(200, 200, 220),
            fontSize=22,
            textAlign='center'
        )
        self.ui.add(total_score)
        
        # Show level change message
        level_text = ""
        if correct == total:
            level_text = f"Great job! Advancing to Level {self.level}"
        else:
            level_text = f"Keep practicing at Level {self.level}"
        
        level_info = ComponentFactory.text(
            text=level_text,
            x=0, y=280, width=self.screen_width, height=30,
            color=(180, 200, 255),
            fontSize=20,
            textAlign='center'
        )
        self.ui.add(level_info)
        
        # Add continue button
        continue_button = ComponentFactory.button(
            id="continue_button",
            text="Next Challenge",
            x=(self.screen_width - 300) // 2 - 80,
            y=self.screen_height - 120,
            width=160, height=50,
            backgroundColor=(60, 120, 255),
            color=(255, 255, 255),
            borderRadius=8,
            fontSize=20
        )
        self.ui.add(continue_button)
        
        # Add menu button
        menu_button = ComponentFactory.button(
            id="menu_button",
            text="Main Menu",
            x=(self.screen_width - 300) // 2 + 120,
            y=self.screen_height - 120,
            width=160, height=50,
            backgroundColor=(100, 100, 140),
            color=(255, 255, 255),
            borderRadius=8,
            fontSize=20
        )
        self.ui.add(menu_button)
    
    def _add_pattern_grid(self):
        """Add a grid of patterns to the UI."""
        # Calculate adaptive cell size based on screen size and matrix size
        min_dimension = min(self.screen_width, self.screen_height)
        cell_size = max(20, min(40, min_dimension // (self.matrix_size * self.patterns_per_row)))
        
        # Calculate pattern dimensions
        pattern_width = cell_size * self.matrix_size
        pattern_height = cell_size * self.matrix_size
        
        # Calculate grid layout
        patterns_per_row = self.patterns_per_row
        num_rows = math.ceil(len(self.clusters) / patterns_per_row)
        
        # Calculate horizontal spacing based on screen width
        total_patterns_width = patterns_per_row * pattern_width
        spacing_x = (self.screen_width - total_patterns_width) // (patterns_per_row + 1)
        
        # Add patterns
        for i, cluster in enumerate(self.clusters):
            row = i // patterns_per_row
            col = i % patterns_per_row
            
            x_pos = spacing_x + col * (pattern_width + spacing_x)
            y_pos = 150 + row * (pattern_height + 60)
            
            # Check if this is the original pattern
            is_original = i == 0
            is_selected = i in self.selected_patterns
            
            # Add container for pattern
            border_color = (50, 100, 255) if is_original else (180, 180, 180)
            bg_color = (80, 100, 120) if is_selected else (60, 60, 80)
            
            pattern_container = ComponentFactory.container(
                id=f"pattern_{i}" if not is_original else None,
                x=x_pos - 10, y=y_pos - 10,
                width=pattern_width + 20, height=pattern_height + 20,
                backgroundColor=bg_color,
                borderWidth=2,
                borderColor=border_color,
                borderRadius=5
            )
            self.ui.add(pattern_container)
            
            # Add cells for the pattern
            matrix = cluster['matrix']
            for r in range(len(matrix)):
                for c in range(len(matrix[r])):
                    cell_x = x_pos + c * cell_size
                    cell_y = y_pos + r * cell_size
                    
                    # Determine cell color based on value
                    cell_color = self.color2 if matrix[r][c] == 1 else self.color1
                    
                    cell = ComponentFactory.rect(
                        x=cell_x, y=cell_y,
                        width=cell_size, height=cell_size,
                        backgroundColor=cell_color,
                        borderWidth=1,
                        borderColor=(100, 100, 100, 50)
                    )
                    self.ui.add(cell)
            
            # Add label for original pattern
            if is_original:
                label = ComponentFactory.text(
                    text="Original",
                    x=x_pos, y=y_pos + pattern_height + 5,
                    width=pattern_width, height=20,
                    color=(180, 200, 255),
                    fontSize=14,
                    textAlign='center'
                )
                self.ui.add(label)
    
    def create_pattern_variations(self, num_patterns, num_modified):
        """Create variations of the original pattern.
        
        Args:
            num_patterns: Number of patterns to create
            num_modified: Number of patterns that should be modified
        """
        # Reset clusters and modified indices
        self.clusters = []
        self.modified_indices = []
        
        # Create original pattern
        self.clusters.append({
            'matrix': self.original_matrix,
            'rotation': 0,
            'index': 0
        })
        
        # Create rotations and modifications
        for i in range(1, num_patterns):
            # Randomly choose rotation (0=0°, 1=90°, 2=180°, 3=270°)
            rotation = random.randint(0, 3)
            
            cluster = {
                'matrix': self.rotate_matrix(self.original_matrix, rotation),
                'rotation': rotation,
                'index': i
            }
            
            self.clusters.append(cluster)
        
        # Modify a subset of patterns
        modified_indices = random.sample(range(1, num_patterns), num_modified)
        self.modified_indices = modified_indices
        
        for idx in modified_indices:
            self.mutate_pattern(self.clusters[idx])
    
    def mutate_pattern(self, cluster):
        """Modify a pattern by flipping some bits.
        
        Args:
            cluster: Pattern cluster to modify
        """
        matrix = cluster['matrix']
        
        # Number of pixels to modify based on level
        num_pixels = 1 if self.level <= 3 else 2
        
        # Randomly flip pixels
        for _ in range(num_pixels):
            row = random.randrange(len(matrix))
            col = random.randrange(len(matrix[0]))
            matrix[row][col] = 1 - matrix[row][col]  # Flip 0 to 1 or 1 to 0
    
    def generate_random_matrix(self, size):
        """Generate a random binary matrix.
        
        Args:
            size: Size of the matrix
            
        Returns:
            A random matrix of 0s and 1s
        """
        # Create empty matrix
        matrix = [[0 for _ in range(size)] for _ in range(size)]
        
        # Fill with random values, with a bias toward 0s to create clearer patterns
        for r in range(size):
            for c in range(size):
                matrix[r][c] = 1 if random.random() < 0.4 else 0
        
        return matrix
    
    def rotate_matrix(self, source_matrix, rotation):
        """Rotate a matrix by the specified amount.
        
        Args:
            source_matrix: Matrix to rotate
            rotation: Rotation value (0=none, 1=90°, 2=180°, 3=270°)
            
        Returns:
            Rotated matrix
        """
        # Create a deep copy of the source matrix
        matrix = [row[:] for row in source_matrix]
        size = len(matrix)
        
        # Apply rotation
        if rotation == 0:  # No rotation
            return matrix
        elif rotation == 1:  # 90° clockwise
            return [[matrix[size-1-j][i] for j in range(size)] for i in range(size)]
        elif rotation == 2:  # 180°
            return [[matrix[size-1-i][size-1-j] for j in range(size)] for i in range(size)]
        elif rotation == 3:  # 270° clockwise
            return [[matrix[j][size-1-i] for j in range(size)] for i in range(size)]
        
        return matrix  # Fallback 