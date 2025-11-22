#!/usr/bin/env python3
"""
ExpandVision Grid Model - Core game logic for the ExpandVision Grid module

This module implements the Model component in the MVC architecture for the
ExpandVision Grid cognitive training exercise. It handles:
- Game state management
- Grid-based number generation
- Score tracking
- Difficulty progression
- Phase transitions
"""

import random
import time
import math
import sys
from pathlib import Path
from typing import List, Dict, Tuple, Any, Optional, Union

# Add the parent directory to sys.path for absolute imports
if __name__ == "__main__" or not __package__:
    project_root = Path(__file__).parent.parent.parent.parent
    sys.path.insert(0, str(project_root))
else:
    # Use relative imports when imported as a module
    pass

class ExpandVisionGridModel:
    """Model component for ExpandVision Grid module - handles core game logic."""
    
    # Game phases
    PHASE_PREPARATION = "preparation"
    PHASE_ACTIVE = "active"
    PHASE_ANSWER = "answer"
    PHASE_FEEDBACK = "feedback"
    PHASE_COMPLETED = "completed"
    
    def __init__(self, screen_width: int, screen_height: int):
        """Initialize the model with game state and business logic.
        
        Args:
            screen_width: Width of the screen
            screen_height: Height of the screen
        """
        # Store screen dimensions for calculations
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Calculate center position
        self.center_x = self.screen_width // 2
        self.center_y = self.screen_height // 2
        
        # Circle dimensions as percentage of screen height
        base_circle_size = self.screen_height * 0.05  # 5% of screen height
        self.circle_width = int(base_circle_size)
        self.circle_height = int(base_circle_size)
        self.circle_growth = int(base_circle_size * 0.15)  # Growth per round is 15% of base size
        
        # Grid settings
        self.grid_size = 3  # Start with a 3x3 grid
        self.grid_spacing_x = int(self.screen_width * 0.15)  # Initial spacing as % of screen
        self.grid_spacing_y = int(self.screen_height * 0.15)
        self.spacing_increase_factor = 0.01  # How much to increase spacing per round
        
        # Game settings
        self.show_numbers = False  # Only show numbers after several rounds
        self.numbers = []  # The grid of numbers
        self.grid_positions = []  # Store calculated positions
        self.number_range = 5  # Range for random numbers (-range/2 to range/2)
        self.current_sum = 0  # The sum of the current numbers
        self.user_answer = None  # User's submitted answer
        self.score = 0  # User's score
        
        # Game progress
        self.message = "Focus on the center circle"
        self.round = 0  # Current round number
        self.total_rounds = 10  # Total rounds in a session
        self.correct_answers = 0  # Count of correct answers
        
        # Phase settings
        self.phase = self.PHASE_PREPARATION  # Initial phase
        self.preparation_rounds = 3  # Number of rounds for preparation phase
        self.preparation_complete = False  # Flag for tracking phase transition
        
        # Timing
        self.display_delay = 6000  # Starting delay in ms when showing numbers
        self.start_time = time.time()
        self.phase_start_time = time.time()
        
        # Flag for tracking game completion
        self.is_completed = False
        
        # Initialize the first round
        self.start_new_round()
    
    def start_new_round(self):
        """Start a new round, resetting necessary parameters."""
        self.round += 1
        
        # Reset the circle size for the start of a new round
        base_circle_size = self.screen_height * 0.05
        self.circle_width = int(base_circle_size)
        self.circle_height = int(base_circle_size)
        
        # Reset user answer
        self.user_answer = None
        
        # Enter preparation phase for initial rounds
        if self.round <= self.preparation_rounds:
            self.phase = self.PHASE_PREPARATION
            self.show_numbers = False
            self.message = "Focus on the center circle"
        else:
            # Active phase with numbers after preparation rounds
            self.preparation_complete = True
            self.phase = self.PHASE_ACTIVE
            self.show_numbers = True
            
            # Increase grid size as the game progresses
            if self.round > 6:
                self.grid_size = 5  # Increase to 5x5 grid for harder levels
            elif self.round > 3:
                self.grid_size = 4  # Increase to 4x4 grid after a few rounds
            
            # Generate random numbers and calculate sum
            self.generate_random_numbers()
            self.message = "Focus on the center and add all numbers in the grid"
        
        self.phase_start_time = time.time()
    
    def generate_random_numbers(self):
        """Generate random numbers in a grid layout."""
        half_range = self.number_range // 2
        
        # Create a grid of random numbers
        self.numbers = []
        for _ in range(self.grid_size * self.grid_size):
            self.numbers.append(random.randint(-half_range, half_range))
        
        # Calculate the sum of all numbers
        self.current_sum = sum(self.numbers)
        
        # Increase the grid spacing over time to expand peripheral vision
        self.grid_spacing_x += int(self.screen_width * self.spacing_increase_factor)
        self.grid_spacing_y += int(self.screen_height * self.spacing_increase_factor)
        
        # Pre-calculate positions
        self.grid_positions = self.calculate_number_positions()
    
    def calculate_number_positions(self):
        """Calculate positions for the grid of numbers.
        
        Returns:
            List of tuples (x, y, number) for each number in the grid
        """
        positions = []
        
        # Only calculate if numbers should be shown
        if self.show_numbers:
            # Calculate the starting position for the top-left corner of the grid
            grid_width = (self.grid_size - 1) * self.grid_spacing_x
            grid_height = (self.grid_size - 1) * self.grid_spacing_y
            start_x = self.center_x - grid_width // 2
            start_y = self.center_y - grid_height // 2
            
            # Create positions for each number in the grid
            index = 0
            for row in range(self.grid_size):
                for col in range(self.grid_size):
                    # Skip the center position (where the focus point is)
                    is_center = (row == self.grid_size // 2 and col == self.grid_size // 2)
                    
                    if not is_center and index < len(self.numbers):
                        x = start_x + col * self.grid_spacing_x
                        y = start_y + row * self.grid_spacing_y
                        positions.append((x, y, self.numbers[index]))
                        index += 1
        
        return positions
    
    def process_answer(self, answer):
        """Process the user's answer.
        
        Args:
            answer: User's answer (an integer)
            
        Returns:
            Tuple of (is_correct, score_change)
        """
        self.user_answer = answer
        is_correct = (answer == self.current_sum)
        score_change = 0
        
        if is_correct:
            # Higher score for larger grids
            base_score = 10
            grid_bonus = (self.grid_size - 2) * 5  # +5 points per size above 3x3
            score_change = base_score + grid_bonus
            
            self.message = "Correct!"
            self.score += score_change
            self.correct_answers += 1
        else:
            self.message = f"Incorrect. The sum was {self.current_sum}."
        
        # Transition to feedback phase
        self.phase = self.PHASE_FEEDBACK
        self.phase_start_time = time.time()
        
        return (is_correct, score_change)
    
    def update_phase(self, elapsed_time):
        """Update the game phase based on elapsed time.
        
        Args:
            elapsed_time: Time elapsed since phase started (in seconds)
            
        Returns:
            True if the phase changed, False otherwise
        """
        phase_changed = False
        
        # Handle phases based on time
        if self.phase == self.PHASE_PREPARATION:
            # Grow the circle during preparation phase
            self.circle_width += self.circle_growth
            self.circle_height += self.circle_growth
            
            # After a few seconds, reset for next round
            if elapsed_time > 2.0:
                if self.round < self.preparation_rounds:
                    self.start_new_round()
                    phase_changed = True
                else:
                    # Transition to active phase with numbers
                    self.preparation_complete = True
                    self.phase = self.PHASE_ACTIVE
                    self.show_numbers = True
                    self.generate_random_numbers()
                    self.message = "Focus on the center and add all numbers in the grid"
                    self.phase_start_time = time.time()
                    phase_changed = True
        
        elif self.phase == self.PHASE_ACTIVE:
            # Grow the circle during active phase
            self.circle_width += self.circle_growth
            self.circle_height += self.circle_growth
            
            # Adjust display time based on grid size (more time for larger grids)
            adjusted_delay = self.display_delay * (1 + (self.grid_size - 3) * 0.3)
            
            # After display delay, go to answer phase
            if self.show_numbers and elapsed_time > adjusted_delay / 1000:
                self.phase = self.PHASE_ANSWER
                self.message = "What was the sum of all the numbers?"
                self.phase_start_time = time.time()
                phase_changed = True
        
        elif self.phase == self.PHASE_FEEDBACK:
            # Show feedback for a short period
            if elapsed_time > 1.5:
                # Check if we've completed all rounds
                if self.round >= self.total_rounds:
                    self.is_completed = True
                    self.phase = self.PHASE_COMPLETED
                    self.message = f"Training complete! Score: {self.score}"
                    phase_changed = True
                else:
                    # Start next round
                    self.start_new_round()
                    phase_changed = True
        
        return phase_changed
    
    def reset(self):
        """Reset the module for a new session."""
        self.score = 0
        self.round = 0
        self.correct_answers = 0
        self.total_rounds = 10
        self.phase = self.PHASE_PREPARATION
        self.preparation_complete = False
        self.show_numbers = False
        self.user_answer = None
        self.message = "Focus on the center circle"
        self.is_completed = False
        
        # Reset grid settings
        self.grid_size = 3
        self.grid_spacing_x = int(self.screen_width * 0.15)
        self.grid_spacing_y = int(self.screen_height * 0.15)
        
        # Reset timing
        self.start_time = time.time()
        self.phase_start_time = time.time()
        
        # Start first round
        self.start_new_round()
    
    def get_state(self):
        """Get the current model state.
        
        Returns:
            Dictionary with current game state
        """
        return {
            "phase": self.phase,
            "round": self.round,
            "total_rounds": self.total_rounds,
            "score": self.score,
            "correct_answers": self.correct_answers,
            "circle_width": self.circle_width,
            "circle_height": self.circle_height,
            "center_x": self.center_x,
            "center_y": self.center_y,
            "show_numbers": self.show_numbers,
            "numbers": self.numbers if self.show_numbers else [],
            "current_sum": self.current_sum,
            "user_answer": self.user_answer,
            "message": self.message,
            "preparation_complete": self.preparation_complete,
            "is_completed": self.is_completed,
            "grid_size": self.grid_size,
            "grid_spacing_x": self.grid_spacing_x,
            "grid_spacing_y": self.grid_spacing_y,
            "grid_positions": self.grid_positions
        } 