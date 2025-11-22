#!/usr/bin/env python3
"""
Theme-aware Morph Matrix training module for MetaMindIQTrain.

This module implements pattern recognition challenges involving matrix manipulation with:
- Theme-aware rendering using the unified theme system
- Resolution-independent layout using ScalingHelper
- Cache-optimized rendering with state tracking
- Adaptive difficulty scaling
"""

import random
import math
import time
import logging
from typing import Dict, List, Tuple, Any, Optional, Union

from MetaMindIQTrain.core.training_module import TrainingModule
from MetaMindIQTrain.core.theme import Theme, ThemeProvider
from MetaMindIQTrain.core.scaling_helper import ScalingHelper
from MetaMindIQTrain.core.components import Component, UI

logger = logging.getLogger(__name__)

class ThemeAwareMorphMatrix(TrainingModule):
    """
    A pattern recognition training module with theme awareness.
    
    This module tests users' ability to recognize transformed patterns 
    (rotated, flipped, and mutated) in matrices.
    
    Features:
    - Theme-aware rendering using the unified theme system
    - Resolution-independent layout using ScalingHelper
    - State tracking optimization with delta encoding
    - Adaptive difficulty scaling
    """
    
    # Game states
    STATE_INITIAL = 0
    STATE_PATTERN_DISPLAY = 1
    STATE_SELECTION = 2
    STATE_FEEDBACK = 3
    
    # Difficulty levels
    DIFFICULTY_LEVELS = [
        {"matrix_size": 3, "options": 4, "transformations": 1, "mutations": 1},
        {"matrix_size": 4, "options": 5, "transformations": 1, "mutations": 1},
        {"matrix_size": 4, "options": 6, "transformations": 2, "mutations": 2},
        {"matrix_size": 5, "options": 6, "transformations": 2, "mutations": 2},
        {"matrix_size": 5, "options": 7, "transformations": 3, "mutations": 3}
    ]
    
    def __init__(self, difficulty=1, theme_provider=None, resolution=(1440, 1024)):
        """Initialize the ThemeAwareMorphMatrix module.
        
        Args:
            difficulty: Initial difficulty level (0-4)
            theme_provider: Theme provider for styling
            resolution: Display resolution as (width, height)
        """
        super().__init__()
        
        # Set resolution
        self.resolution = resolution
        
        # Set up difficulty
        self.difficulty = max(0, min(difficulty, len(self.DIFFICULTY_LEVELS) - 1))
        self.config = self.DIFFICULTY_LEVELS[self.difficulty]
        
        # Set up theme
        self.theme_provider = theme_provider or ThemeProvider()
        
        # Initialize scaling helper
        self.scaling_helper = ScalingHelper()
        self.scaling_helper.update_scale_factors(
            self.resolution[0], self.resolution[1], 1440, 1024
        )
        
        # Module settings
        self.name = "morph_matrix"
        self.display_name = "MorphMatrix"
        self.description = "Identify patterns that are exact rotations of the original pattern"
        
        # Game state
        self.state = self.STATE_INITIAL
        self.current_pattern = None
        self.transformed_pattern = None
        self.options = []
        self.correct_indices = []
        self.selected_indices = []
        
        # Score tracking
        self.score = 0
        self.rounds_played = 0
        
        # UI components
        self.ui = UI()
        
        # Option bounds for click detection
        self._option_bounds = []
        
        # Start the first round
        self._start_round()
    
    def update(self, delta_time):
        """Update the module state.
        
        Args:
            delta_time: Time elapsed since the last update in seconds
        """
        # No continuous updates needed for this module
        pass
    
    def handle_click(self, position):
        """Handle mouse click.
        
        Args:
            position: (x, y) position of the click
        """
        if self.state != self.STATE_SELECTION:
            return
        
        # Check if click is on an option
        for i, option_bounds in enumerate(self._option_bounds):
            if (option_bounds[0] <= position[0] <= option_bounds[2] and
                option_bounds[1] <= position[1] <= option_bounds[3]):
                
                # Don't allow selecting the original pattern (index 0)
                if i == 0:
                    return
                    
                # Toggle selection
                if i in self.selected_indices:
                    self.selected_indices.remove(i)
                else:
                    self.selected_indices.append(i)
                
                # Rebuild UI to reflect selection
                self.build_ui()
                break
    
    def handle_key_press(self, key):
        """Handle key press.
        
        Args:
            key: Key that was pressed
        """
        if self.state == self.STATE_SELECTION:
            if key == " ":  # Space bar to submit answer
                self._check_answer()
            elif key.isdigit():
                # Option selection by number keys
                option = int(key) - 1
                if 0 < option < len(self.options):  # Skip option 0 (original)
                    if option in self.selected_indices:
                        self.selected_indices.remove(option)
                    else:
                        self.selected_indices.append(option)
                    self.build_ui()
    
    def _generate_pattern(self):
        """Generate a random pattern matrix based on current difficulty.
        
        Returns:
            A 2D list representing the pattern matrix
        """
        size = self.config["matrix_size"]
        
        # Create empty matrix
        pattern = [[0 for _ in range(size)] for _ in range(size)]
        
        # Fill with random pattern (approximately 40% filled)
        for i in range(size):
            for j in range(size):
                if random.random() < 0.4:
                    pattern[i][j] = 1
                    
        return pattern
    
    def _transform_pattern(self, pattern, rotation):
        """Apply rotation transformation to a pattern.
        
        Args:
            pattern: The original pattern matrix
            rotation: Rotation value (0=none, 1=90°, 2=180°, 3=270°)
            
        Returns:
            A transformed version of the pattern
        """
        # Make a deep copy of the pattern
        size = len(pattern)
        transformed = [row[:] for row in pattern]
        
        # Apply rotation
        if rotation == 0:  # No rotation
            return transformed
        elif rotation == 1:  # 90° clockwise
            return [[transformed[size-1-j][i] for j in range(size)] for i in range(size)]
        elif rotation == 2:  # 180°
            return [[transformed[size-1-i][size-1-j] for j in range(size)] for i in range(size)]
        elif rotation == 3:  # 270° clockwise
            return [[transformed[j][size-1-i] for j in range(size)] for i in range(size)]
        
        return transformed  # Fallback
    
    def _mutate_pattern(self, pattern, mutations=1):
        """Apply mutations to a pattern by flipping random cells.
        
        Args:
            pattern: The pattern to mutate
            mutations: Number of mutations to apply
            
        Returns:
            Mutated pattern
        """
        # Make a deep copy of the pattern
        size = len(pattern)
        mutated = [row[:] for row in pattern]
        
        # Apply mutations
        for _ in range(mutations):
            i = random.randint(0, size-1)
            j = random.randint(0, size-1)
            mutated[i][j] = 1 - mutated[i][j]
        
        return mutated
    
    def _generate_options(self):
        """Generate answer options including pure rotations and mutations.
        
        Returns:
            List of pattern matrices as options and list of correct indices
        """
        num_options = self.config["options"]
        mutations = self.config["mutations"]
        
        # First option is always the original
        options = [self.current_pattern]
        correct_indices = []  # The original isn't selectable
        
        # Generate rotation options (these are correct answers)
        for i in range(1, 4):  # 1=90°, 2=180°, 3=270°
            rotated = self._transform_pattern(self.current_pattern, i)
            options.append(rotated)
            correct_indices.append(len(options) - 1)
        
        # Generate mutation options (these are incorrect answers)
        mutations_added = 0
        while len(options) < num_options and mutations_added < mutations:
            # Randomly select either a rotation or the original to mutate
            base_pattern = random.choice([
                self.current_pattern,
                self._transform_pattern(self.current_pattern, 1),
                self._transform_pattern(self.current_pattern, 2),
                self._transform_pattern(self.current_pattern, 3)
            ])
            
            # Apply mutations
            mutated = self._mutate_pattern(base_pattern, random.randint(1, 2))
            
            # Check if this mutation is unique
            is_unique = True
            for existing_option in options:
                if all(mutated[i][j] == existing_option[i][j] for i in range(len(mutated)) for j in range(len(mutated))):
                    is_unique = False
                    break
                    
            if is_unique:
                options.append(mutated)
                mutations_added += 1
        
        # Shuffle options except the original
        shuffled_options = [options[0]]  # Keep original first
        shuffled_indices = list(range(1, len(options)))
        random.shuffle(shuffled_indices)
        
        # Create shuffled options and update correct indices
        new_correct_indices = []
        for i, idx in enumerate(shuffled_indices, 1):
            shuffled_options.append(options[idx])
            if idx in correct_indices:
                new_correct_indices.append(i)
        
        return shuffled_options, new_correct_indices
    
    def _start_round(self):
        """Start a new round of the game."""
        # Generate pattern
        self.current_pattern = self._generate_pattern()
        
        # Generate options with rotation and mutations
        self.options, self.correct_indices = self._generate_options()
        
        # Reset selection
        self.selected_indices = []
        
        # Update state
        self.state = self.STATE_SELECTION
        
        # Build UI for the new round
        self.build_ui()
    
    def _check_answer(self):
        """Check if the selected options match the correct answers."""
        # Sort selections for comparison
        selected = sorted(self.selected_indices)
        correct = sorted(self.correct_indices)
        
        # Check if all correct options were selected
        all_correct = True
        for idx in self.correct_indices:
            if idx not in self.selected_indices:
                all_correct = False
                break
        
        # Check if any incorrect options were selected
        no_incorrect = True
        for idx in self.selected_indices:
            if idx not in self.correct_indices:
                no_incorrect = False
                break
        
        # Update score for perfect answers only
        if all_correct and no_incorrect:
            self.score += 1
        
        # Update state
        self.state = self.STATE_FEEDBACK
        
        # Build feedback UI
        self.build_ui()
        
        # Schedule next round
        self.rounds_played += 1
        self.schedule_event(self._start_round, 3.0)  # 3 seconds for feedback
    
    def build_ui(self):
        """Build the UI for the current state.
        
        Returns:
            UI object with components
        """
        # Clear existing UI
        self.ui = UI()
        
        # Get current theme
        theme = self.theme_provider.theme
        
        # Update scaling helper with current resolution
        self.scaling_helper.update_scale_factors(
            self.resolution[0], self.resolution[1], 1440, 1024
        )
        
        # Main container
        container = self._add_main_container()
        
        # Add options (both for selection and feedback states)
        self._add_options(container)
        
        # Add feedback if in feedback state
        if self.state == self.STATE_FEEDBACK:
            self._add_feedback(container)
        
        # Add score
        self._add_score(container)
        
        # Add instructions
        self._add_instructions(container)
        
        return self.ui
    
    def _add_main_container(self):
        """Add the main container to the UI.
        
        Returns:
            Container component
        """
        # Scale container dimensions
        width = self.scaling_helper.scale_value(900)
        height = self.scaling_helper.scale_value(700)
        x = (self.resolution[0] - width) / 2
        y = (self.resolution[1] - height) / 2
        
        # Create container with theme styling
        container = Component(
            type="rectangle",
            position=(x, y),
            width=width,
            height=height,
            style=self.theme_provider.theme.get_style("morph_matrix.container")
        )
        
        # Add to UI
        self.ui.add_component(container)
        
        # Add title
        title = Component(
            type="text",
            text="Morph Matrix",
            position=(x + width/2, y + self.scaling_helper.scale_value(30)),
            style=self.theme_provider.theme.get_style("morph_matrix.title"),
            align="center"
        )
        self.ui.add_component(title)
        
        return container
    
    def _add_instructions(self, container):
        """Add instructions text to the container.
        
        Args:
            container: Container component to add the instructions to
        """
        if self.state == self.STATE_SELECTION:
            text = "Select all patterns that are exact rotations of the original (top) pattern"
        elif self.state == self.STATE_FEEDBACK:
            text = "Green = correct selection, Red = incorrect selection"
        else:
            text = "Morph Matrix pattern recognition challenge"
        
        instruction = Component(
            type="text",
            text=text,
            position=(container.position[0] + container.width/2, container.position[1] + self.scaling_helper.scale_value(70)),
            style=self.theme_provider.theme.get_style("morph_matrix.instruction"),
            align="center"
        )
        self.ui.add_component(instruction)
        
        # Add controls text
        if self.state == self.STATE_SELECTION:
            controls = Component(
                type="text",
                text="Click to select/deselect a pattern, Press SPACE to submit",
                position=(container.position[0] + container.width/2, container.position[1] + container.height - self.scaling_helper.scale_value(30)),
                style=self.theme_provider.theme.get_style("morph_matrix.instruction"),
                align="center"
            )
            self.ui.add_component(controls)
    
    def _add_options(self, container):
        """Add pattern options grid to the container.
        
        Args:
            container: Container component to add the options to
        """
        # Calculate dimensions
        option_count = len(self.options)
        matrix_size = len(self.options[0])
        cell_size = self.scaling_helper.scale_value(30)
        option_width = matrix_size * cell_size
        option_height = matrix_size * cell_size
        
        # Calculate layout (3 per row)
        options_per_row = 3
        rows = (option_count + options_per_row - 1) // options_per_row
        
        # Track option bounds for click detection
        self._option_bounds = []
        
        # Start position
        start_y = container.position[1] + self.scaling_helper.scale_value(120)
        
        # Render options
        for row in range(rows):
            options_in_this_row = min(options_per_row, option_count - row * options_per_row)
            total_width = options_in_this_row * (option_width + self.scaling_helper.scale_value(40))
            start_x = container.position[0] + (container.width - total_width) / 2
            
            for col in range(options_in_this_row):
                option_index = row * options_per_row + col
                if option_index >= option_count:
                    break
                    
                option_x = start_x + col * (option_width + self.scaling_helper.scale_value(40))
                option_y = start_y + row * (option_height + self.scaling_helper.scale_value(60))
                
                # Track bounds for click detection
                self._option_bounds.append((
                    option_x, option_y, 
                    option_x + option_width, option_y + option_height
                ))
                
                # Option container style based on state
                option_style = self._get_option_style(option_index)
                
                # Add option container with border
                option_container = Component(
                    type="rectangle",
                    position=(
                        option_x - self.scaling_helper.scale_value(5), 
                        option_y - self.scaling_helper.scale_value(5)
                    ),
                    width=option_width + self.scaling_helper.scale_value(10),
                    height=option_height + self.scaling_helper.scale_value(10),
                    style=option_style
                )
                self.ui.add_component(option_container)
                
                # Add matrix cells
                for i in range(matrix_size):
                    for j in range(matrix_size):
                        cell_x = option_x + j * cell_size
                        cell_y = option_y + i * cell_size
                        
                        # Determine cell state and style
                        cell_state = "filled" if self.options[option_index][i][j] == 1 else "empty"
                        
                        cell = Component(
                            type="rectangle",
                            position=(cell_x, cell_y),
                            width=cell_size - 2,
                            height=cell_size - 2,
                            style=self.theme_provider.theme.get_style(f"morph_matrix.cell.{cell_state}")
                        )
                        self.ui.add_component(cell)
                
                # Add option number
                option_label = Component(
                    type="text",
                    text=str(option_index),
                    position=(option_x + option_width/2, option_y + option_height + self.scaling_helper.scale_value(15)),
                    style=self.theme_provider.theme.get_style("morph_matrix.option_label"),
                    align="center"
                )
                self.ui.add_component(option_label)
    
    def _get_option_style(self, option_index):
        """Get the appropriate style for an option based on state.
        
        Args:
            option_index: Index of the option
            
        Returns:
            Style dictionary for the option
        """
        # Original pattern always has a special style
        if option_index == 0:
            return self.theme_provider.theme.get_style("morph_matrix.matrix")
        
        if self.state == self.STATE_SELECTION:
            # Selected options
            if option_index in self.selected_indices:
                return self.theme_provider.theme.get_style("morph_matrix.option.selected")
            return self.theme_provider.theme.get_style("morph_matrix.option")
        
        # Feedback state
        if option_index in self.correct_indices and option_index in self.selected_indices:
            # Correctly selected
            return self.theme_provider.theme.get_style("morph_matrix.option.correct")
        elif option_index in self.correct_indices:
            # Correct but not selected
            return self.theme_provider.theme.get_style("morph_matrix.option.missed")
        elif option_index in self.selected_indices:
            # Incorrectly selected
            return self.theme_provider.theme.get_style("morph_matrix.option.incorrect")
        else:
            # Not selected, not correct
            return self.theme_provider.theme.get_style("morph_matrix.option")
    
    def _add_feedback(self, container):
        """Add feedback based on answer correctness.
        
        Args:
            container: Container component to add the feedback to
        """
        # Sort selections for comparison
        selected = sorted(self.selected_indices)
        correct = sorted(self.correct_indices)
        
        # Check if all correct options were selected and no incorrect ones
        all_correct = True
        for idx in self.correct_indices:
            if idx not in self.selected_indices:
                all_correct = False
                break
        
        no_incorrect = True
        for idx in self.selected_indices:
            if idx not in self.correct_indices:
                no_incorrect = False
                break
        
        # Overall feedback
        if all_correct and no_incorrect:
            feedback_text = "Perfect! You found all rotations!"
            style_key = "morph_matrix.feedback.correct"
        elif all_correct:
            feedback_text = "Good! You found all rotations, but some extra selections were wrong."
            style_key = "morph_matrix.feedback.partial"
        elif no_incorrect:
            feedback_text = "Almost! You missed some rotations."
            style_key = "morph_matrix.feedback.partial"
        else:
            feedback_text = "Try again! You missed some rotations and had incorrect selections."
            style_key = "morph_matrix.feedback.incorrect"
        
        # Add feedback component
        feedback = Component(
            type="text",
            text=feedback_text,
            position=(container.position[0] + container.width/2, container.position[1] + self.scaling_helper.scale_value(70)),
            style=self.theme_provider.theme.get_style(style_key),
            align="center"
        )
        self.ui.add_component(feedback)
    
    def _add_score(self, container):
        """Add score display to the container.
        
        Args:
            container: Container component to add the score to
        """
        score_text = f"Score: {self.score}/{self.rounds_played}" if self.rounds_played > 0 else "Score: 0/0"
        
        score = Component(
            type="text",
            text=score_text,
            position=(
                container.position[0] + container.width - self.scaling_helper.scale_value(20),
                container.position[1] + self.scaling_helper.scale_value(20)
            ),
            style=self.theme_provider.theme.get_style("morph_matrix.score"),
            align="right"
        )
        self.ui.add_component(score)
    
    def set_theme(self, theme_provider):
        """Set the theme provider for the module.
        
        Args:
            theme_provider: New theme provider
        """
        self.theme_provider = theme_provider
        self.build_ui() 