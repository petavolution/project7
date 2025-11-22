#!/usr/bin/env python3
"""
Neural Synthesis: A multi-modal cognitive training module.

This module integrates auditory and visual pattern recognition to enhance 
neural plasticity, cross-modal integration, and creative thinking by 
engaging users in a synesthetic experience that maps visual patterns 
to auditory sequences and requires pattern recognition across multiple
sensory domains.
"""

import random
import time
import math
from typing import Dict, Any, List, Tuple, Optional
from ..core.training_module import TrainingModule


class NeuralSynthesis(TrainingModule):
    """
    Neural Synthesis: Multi-modal cognitive training that bridges visual and auditory domains.
    
    Users must identify patterns that span both visual arrangements and sound sequences,
    training the brain to form connections between sensory modalities and enhance
    cognitive flexibility, processing speed, and creative thinking.
    """
    
    def __init__(self):
        super().__init__()
        # Module metadata
        self.name = "Neural Synthesis"
        self.description = "Train cross-modal integration between visual and auditory patterns"
        self.category = "Advanced Cognition"
        self.difficulty = "Medium"
        
        # Visual-auditory patterns
        self.patterns = []
        self.current_pattern = None
        self.user_sequence = []
        self.display_sequence = False
        self.sequence_complete = False
        self.comparison_active = False
        
        # Pattern cells
        self.grid_size = 4  # Start with 4x4 grid
        self.max_grid_size = 8
        self.cell_size = 60
        self.grid_position = (0, 0)  # Will be calculated in initialize()
        
        # Colors for cells (each with associated "tone")
        self.colors = [
            {"rgb": (255, 0, 0), "name": "red", "note": "C"},      # Red - C
            {"rgb": (255, 165, 0), "name": "orange", "note": "D"},  # Orange - D
            {"rgb": (255, 255, 0), "name": "yellow", "note": "E"},  # Yellow - E
            {"rgb": (0, 255, 0), "name": "green", "note": "F"},    # Green - F
            {"rgb": (0, 255, 255), "name": "cyan", "note": "G"},   # Cyan - G
            {"rgb": (0, 0, 255), "name": "blue", "note": "A"},     # Blue - A
            {"rgb": (128, 0, 128), "name": "purple", "note": "B"}  # Purple - B
        ]
        
        # Timing settings
        self.pattern_display_time = 4000  # ms
        self.pattern_start_time = 0
        self.feedback_time = 1500  # ms
        self.feedback_start_time = 0
        
        # Sequence settings
        self.sequence_length = 4  # Start with sequences of 4
        self.max_sequence_length = 12
        self.current_sequence = []
        self.user_sequence = []
        
        # Game flow
        self.phase = "observation"  # observation, reproduction, feedback
        self.trials_per_level = 3
        self.current_trial = 0
        self.correct_count = 0
        
        # Performance metrics
        self.response_times = []
        self.accuracy_history = []
        
        self.initialize()
        
    def initialize(self):
        """Initialize the module state."""
        # Calculate grid position (centered)
        grid_width = self.grid_size * self.cell_size
        grid_height = self.grid_size * self.cell_size
        self.grid_position = (
            (self.screen_width - grid_width) // 2,
            (self.screen_height - grid_height) // 2 + 20  # Offset for header
        )
        
        # Generate a pattern for the first trial
        self._generate_new_pattern()
        
    def _generate_new_pattern(self):
        """Generate a new pattern for the current level."""
        # Create a sequence of the current length
        self.current_sequence = []
        for _ in range(self.sequence_length):
            # Random position in the grid
            x = random.randint(0, self.grid_size - 1)
            y = random.randint(0, self.grid_size - 1)
            
            # Random color/tone
            color_idx = random.randint(0, len(self.colors) - 1)
            
            # Add to sequence
            self.current_sequence.append({
                "position": (x, y),
                "color_idx": color_idx
            })
        
        # Reset user sequence
        self.user_sequence = []
        
        # Set phase to observation
        self.phase = "observation"
        self.pattern_start_time = time.time() * 1000  # Convert to ms
        
    def handle_click(self, x, y):
        """Handle a click event.
        
        Args:
            x: The x-coordinate of the click.
            y: The y-coordinate of the click.
            
        Returns:
            dict: Result of the click operation.
        """
        # Ignore clicks during observation phase
        if self.phase == "observation":
            return {"success": False, "message": "Please observe the pattern"}
            
        # Ignore clicks during feedback phase
        if self.phase == "feedback":
            return {"success": False, "message": "Please wait for next trial"}
        
        # Check if click is in the grid
        grid_x, grid_y = self.grid_position
        grid_width = self.grid_size * self.cell_size
        grid_height = self.grid_size * self.cell_size
        
        if (grid_x <= x < grid_x + grid_width and 
            grid_y <= y < grid_y + grid_height):
            
            # Convert click to grid coordinates
            cell_x = (x - grid_x) // self.cell_size
            cell_y = (y - grid_y) // self.cell_size
            
            # Determine which color/tone was selected
            # For now, we'll just use the position to map to a color
            # In a real implementation, the displayed grid would show the colors
            color_idx = (cell_x + cell_y) % len(self.colors)
            
            # Add to user sequence
            self.user_sequence.append({
                "position": (cell_x, cell_y),
                "color_idx": color_idx,
                "time": time.time() * 1000  # Record timestamp for response time analysis
            })
            
            # Check if sequence is complete
            if len(self.user_sequence) == len(self.current_sequence):
                correct = self._check_sequence()
                self.phase = "feedback"
                self.feedback_start_time = time.time() * 1000
                
                if correct:
                    self.score += 10 * self.level
                    self.correct_count += 1
                    self.message = "Correct pattern!"
                    
                    # Track accuracy
                    self.accuracy_history.append(1)
                else:
                    self.message = "Incorrect pattern."
                    
                    # Track accuracy
                    self.accuracy_history.append(0)
                
                # Go to next trial or level
                self.current_trial += 1
                if self.current_trial >= self.trials_per_level:
                    self._advance_level()
                    
            return {"success": True}
        
        return {"success": False, "message": "Click outside the grid"}
        
    def _check_sequence(self):
        """Check if the user's sequence matches the generated pattern.
        
        Returns:
            bool: True if the sequences match, False otherwise.
        """
        if len(self.user_sequence) != len(self.current_sequence):
            return False
            
        for i, (user, target) in enumerate(zip(self.user_sequence, self.current_sequence)):
            if (user["position"] != target["position"] or 
                user["color_idx"] != target["color_idx"]):
                return False
                
        return True
        
    def _advance_level(self):
        """Advance to the next level."""
        # If user got at least 2/3 correct
        if self.correct_count >= 2:
            self.level += 1
            self.message = f"Advanced to level {self.level}!"
            
            # Increase difficulty
            if self.level % 2 == 0 and self.sequence_length < self.max_sequence_length:
                self.sequence_length += 1
                
            if self.level % 3 == 0 and self.grid_size < self.max_grid_size:
                self.grid_size += 1
                # Recalculate grid position
                grid_width = self.grid_size * self.cell_size
                grid_height = self.grid_size * self.cell_size
                self.grid_position = (
                    (self.screen_width - grid_width) // 2,
                    (self.screen_height - grid_height) // 2 + 20
                )
                
            # Decrease pattern display time (min 2000ms)
            self.pattern_display_time = max(2000, 4000 - (self.level - 1) * 200)
        else:
            self.message = "Try again to advance to the next level."
            
        # Reset for next level
        self.current_trial = 0
        self.correct_count = 0
        self._generate_new_pattern()
        
    def update(self, dt):
        """Update module state based on time.
        
        Args:
            dt: Time delta in seconds.
        """
        current_time = time.time() * 1000  # Convert to ms
        
        # Handle phase transitions
        if self.phase == "observation":
            elapsed = current_time - self.pattern_start_time
            if elapsed >= self.pattern_display_time:
                self.phase = "reproduction"
                self.message = "Reproduce the pattern by clicking the grid."
                
        elif self.phase == "feedback":
            elapsed = current_time - self.feedback_start_time
            if elapsed >= self.feedback_time:
                self._generate_new_pattern()
        
    def build_ui(self):
        """Build the UI components for the current state.
        
        Returns:
            UI: UI instance with components
        """
        # Start with base UI (score, level, etc.)
        ui = super().build_ui()
        
        # Add grid
        grid_x, grid_y = self.grid_position
        cell_size = self.cell_size
        
        # Draw grid background
        ui.add_component(ui.rectangle(
            position=self.grid_position,
            size=(self.grid_size * cell_size, self.grid_size * cell_size),
            color=(30, 30, 30),
            border_color=(100, 100, 100),
            border_width=2
        ))
        
        # Draw grid cells
        for y in range(self.grid_size):
            for x in range(self.grid_size):
                cell_x = grid_x + x * cell_size
                cell_y = grid_y + y * cell_size
                
                # Default cell color
                cell_color = (50, 50, 50)
                
                # If in observation phase, show the pattern
                if self.phase == "observation":
                    for item in self.current_sequence:
                        if item["position"] == (x, y):
                            cell_color = self.colors[item["color_idx"]]["rgb"]
                
                # If in feedback phase, show correct and user selections
                elif self.phase == "feedback":
                    # Show correct pattern
                    for item in self.current_sequence:
                        if item["position"] == (x, y):
                            cell_color = self.colors[item["color_idx"]]["rgb"]
                            
                    # Highlight user selections
                    for item in self.user_sequence:
                        if item["position"] == (x, y):
                            # If wrong selection, use a different visual indicator
                            if item not in self.current_sequence:
                                # Add 'X' overlay or some visual indicator
                                ui.add_component(ui.text(
                                    text="X",
                                    position=(cell_x + cell_size // 2, cell_y + cell_size // 2),
                                    font_size=24,
                                    color=(255, 0, 0),
                                    align="center"
                                ))
                
                # Draw the cell
                ui.add_component(ui.rectangle(
                    position=(cell_x, cell_y),
                    size=(cell_size - 2, cell_size - 2),
                    color=cell_color,
                    border_color=(80, 80, 80),
                    border_width=1
                ))
        
        # Add phase-specific instructions
        if self.phase == "observation":
            ui.add_component(ui.text(
                text="Memorize the pattern",
                position=(self.screen_width // 2, grid_y - 40),
                font_size=24,
                color=(255, 255, 255),
                align="center"
            ))
        elif self.phase == "reproduction":
            ui.add_component(ui.text(
                text="Reproduce the pattern",
                position=(self.screen_width // 2, grid_y - 40),
                font_size=24,
                color=(255, 255, 255),
                align="center"
            ))
            
            # Show sequence progress
            progress_text = f"Selected: {len(self.user_sequence)} / {len(self.current_sequence)}"
            ui.add_component(ui.text(
                text=progress_text,
                position=(self.screen_width // 2, grid_y + (self.grid_size * cell_size) + 30),
                font_size=18,
                color=(200, 200, 200),
                align="center"
            ))
        
        # Show current level information
        level_info = f"Level {self.level}: {self.grid_size}x{self.grid_size} grid, {self.sequence_length} items"
        ui.add_component(ui.text(
            text=level_info,
            position=(self.screen_width // 2, 70),
            font_size=16,
            color=(180, 180, 180),
            align="center"
        ))
        
        # Show trial progress
        trial_text = f"Trial {self.current_trial + 1} of {self.trials_per_level}"
        ui.add_component(ui.text(
            text=trial_text,
            position=(self.screen_width // 2, 95),
            font_size=16,
            color=(180, 180, 180),
            align="center"
        ))
        
        return ui
        
    def get_module_state(self):
        """Get module-specific state.
        
        Returns:
            dict: Module-specific state.
        """
        return {
            "neural_synthesis": {
                "grid_size": self.grid_size,
                "sequence_length": self.sequence_length,
                "phase": self.phase,
                "current_trial": self.current_trial,
                "trials_per_level": self.trials_per_level
            }
        } 