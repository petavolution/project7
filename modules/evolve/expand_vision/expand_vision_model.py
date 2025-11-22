#!/usr/bin/env python3
"""
ExpandVision Model - Core game logic for the ExpandVision module

This module implements the Model component in the MVC architecture for the
ExpandVision cognitive training exercise. It handles:
- Game state management
- Number generation
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

class ExpandVisionModel:
    """Model component for ExpandVision module - handles core game logic."""
    
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
        
        # Game settings
        self.show_numbers = False  # Only show numbers after several rounds
        self.numbers = []  # The four numbers at the periphery
        self.number_range = 10  # Range for random numbers (-range/2 to range/2)
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
        self.preparation_rounds = 5  # Number of rounds for preparation phase
        self.preparation_complete = False  # Flag for tracking phase transition
        
        # Number positioning - percentages of screen dimensions
        self.distance_factor_x = 0.15  # Initial X distance from center (as percentage)
        self.distance_factor_y = 0.15  # Initial Y distance from center (as percentage)
        self.distance_increase_factor = 0.01  # How much to increase per round
        
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
            
            # Generate random numbers and calculate sum
            self.generate_random_numbers()
            self.message = "Focus on the center and add the numbers"
        
        self.phase_start_time = time.time()
    
    def generate_random_numbers(self):
        """Generate random numbers around the periphery."""
        half_range = self.number_range // 2
        self.numbers = [random.randint(-half_range, half_range) for _ in range(4)]
        self.current_sum = sum(self.numbers)
        
        # Increase the distance factors to expand peripheral vision over time
        self.distance_factor_x += self.distance_increase_factor
        self.distance_factor_y += self.distance_increase_factor
    
    def calculate_number_positions(self):
        """Calculate positions for the peripheral numbers.
        
        Returns:
            List of tuples (x, y, number) for each peripheral number
        """
        positions = []
        
        # Only calculate if numbers should be shown
        if self.show_numbers:
            # Calculate positions based on distance factors
            offset_x = int(self.screen_width * self.distance_factor_x)
            offset_y = int(self.screen_height * self.distance_factor_y)
            
            # Create positions for all four sides (top, right, bottom, left)
            # Format: (x, y, number)
            positions = [
                (self.center_x, self.center_y - offset_y, self.numbers[0]),  # Top
                (self.center_x + offset_x, self.center_y, self.numbers[1]),  # Right
                (self.center_x, self.center_y + offset_y, self.numbers[2]),  # Bottom
                (self.center_x - offset_x, self.center_y, self.numbers[3])   # Left
            ]
        
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
            self.message = "Correct!"
            score_change = 10
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
                    self.message = "Focus on the center and add the numbers"
                    self.phase_start_time = time.time()
                    phase_changed = True
        
        elif self.phase == self.PHASE_ACTIVE:
            # Grow the circle during active phase
            self.circle_width += self.circle_growth
            self.circle_height += self.circle_growth
            
            # After display delay, go to answer phase
            if self.show_numbers and elapsed_time > self.display_delay / 1000:
                self.phase = self.PHASE_ANSWER
                self.message = "What was the sum of the numbers?"
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
        
        # Reset number positioning
        self.distance_factor_x = 0.15
        self.distance_factor_y = 0.15
        
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
            "distance_factor_x": self.distance_factor_x,
            "distance_factor_y": self.distance_factor_y,
            "phase_start_time": self.phase_start_time,
            "display_delay": self.display_delay,
            "number_positions": self.calculate_number_positions()
        } 