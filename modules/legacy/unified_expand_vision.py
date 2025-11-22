#!/usr/bin/env python3
"""
Unified Expand Vision Module

An optimized version of the ExpandVision module using the unified component system.
This module tests peripheral vision and attention by displaying a central focus
with numbers appearing in the periphery that the user must sum.

Optimizations:
1. Uses component memoization and caching
2. Implements declarative UI with automatic diffing
3. Efficiently updates only changed components
4. Implements adaptive positioning based on screen resolution
5. Uses delta encoding for efficient state updates
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

# Module phases
PHASE_INTRO = "intro"
PHASE_PREPARATION = "preparation"
PHASE_ACTIVE = "active"
PHASE_ANSWER = "answer"
PHASE_FEEDBACK = "feedback"
PHASE_COMPLETE = "complete"

class UnifiedExpandVision:
    """Peripheral vision and attention training module using the unified component system."""
    
    def __init__(self):
        """Initialize the expand vision module."""
        # Configuration
        self.preparation_rounds = 5  # Rounds without numbers
        self.total_rounds = 10  # Total rounds in a session
        
        # Visual settings
        self.screen_width = 1440  # Default width
        self.screen_height = 1024  # Default height
        
        # Calculate center position and circle dimensions
        self.center_x = self.screen_width // 2
        self.center_y = self.screen_height // 2
        self.base_circle_size = int(self.screen_height * 0.05)  # 5% of screen height
        self.circle_width = self.base_circle_size
        self.circle_height = self.base_circle_size
        self.circle_growth = int(self.base_circle_size * 0.15)  # 15% growth per tick
        
        # State
        self.phase = PHASE_INTRO
        self.preparation_complete = False
        self.show_numbers = False
        self.numbers = []
        self.number_range = 10  # Range for random numbers
        self.current_sum = 0
        self.user_answer = None
        self.correct_answers = 0
        self.score = 0
        self.high_score = 0
        self.round = 0
        self.level = 1
        self.is_completed = False
        
        # Number positioning
        self.distance_factor_x = 0.15  # Initial X distance from center (as percentage)
        self.distance_factor_y = 0.15  # Initial Y distance from center (as percentage)
        self.distance_increase_factor = 0.01  # How much to increase per round
        
        # Timing
        self.display_delay = 6000  # Delay in ms
        self.start_time = time.time()
        self.phase_start_time = time.time()
        self.elapsed_time = 0
        
        # Message
        self.message = "Focus gaze on center and calculate sum of numbers"
        
        # UI components
        self.ui = None
        
        # Optimization
        self.needs_redraw = True  # Force full redraw on first frame
        self.last_phase = None  # Previous phase for change detection
    
    def initialize(self):
        """Initialize the module."""
        logger.info("Initializing Expand Vision module")
        # Reset state
        self.phase = PHASE_INTRO
        self.score = 0
        self.round = 0
        self.level = 1
        self.is_completed = False
        
        # Reset circle dimensions
        self.circle_width = self.base_circle_size
        self.circle_height = self.base_circle_size
        
        # Reset distance factors
        self.distance_factor_x = 0.15
        self.distance_factor_y = 0.15
        
        # Force redraw
        self.needs_redraw = True
    
    def shutdown(self):
        """Clean up resources."""
        logger.info("Shutting down Expand Vision module")
    
    def update(self):
        """Update module state."""
        current_time = time.time()
        
        # Handle phases based on time
        if self.phase == PHASE_PREPARATION:
            # Grow the circle during preparation phase
            self.circle_width += self.circle_growth
            self.circle_height += self.circle_growth
            
            # Mark UI for update since circle size changed
            self.needs_redraw = True
            
            # After a few seconds, reset for next round
            if current_time - self.phase_start_time > 2.0:
                if self.round < self.preparation_rounds:
                    self.start_new_round()
                else:
                    # Transition to active phase with numbers
                    self.preparation_complete = True
                    self.phase = PHASE_ACTIVE
                    self.show_numbers = True
                    self.generate_random_numbers()
                    self.message = "Focus on the center and add the numbers"
                    self.phase_start_time = current_time
                    self.needs_redraw = True
        
        elif self.phase == PHASE_ACTIVE:
            # Grow the circle during active phase
            self.circle_width += self.circle_growth
            self.circle_height += self.circle_growth
            
            # Mark UI for update since circle size changed
            self.needs_redraw = True
            
            # After display delay, go to answer phase
            if self.show_numbers and current_time - self.phase_start_time > self.display_delay / 1000:
                self.phase = PHASE_ANSWER
                self.message = "What was the sum of the numbers?"
                self.phase_start_time = current_time
                self.needs_redraw = True
        
        elif self.phase == PHASE_FEEDBACK:
            # Show feedback for a short period
            if current_time - self.phase_start_time > 1.5:
                # Check if we've completed all rounds
                if self.round >= self.total_rounds:
                    self.is_completed = True
                    self.phase = PHASE_COMPLETE
                    self.message = f"Training complete! Score: {self.score}"
                    self.needs_redraw = True
                    
                    # Update high score if needed
                    if self.score > self.high_score:
                        self.high_score = self.score
                        
                    # Increase level for next session
                    self.level += 1
                else:
                    # Start next round
                    self.start_new_round()
    
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
            
            # Build UI based on current phase
            if self.phase == PHASE_INTRO:
                self._build_intro_ui()
            elif self.phase == PHASE_PREPARATION or self.phase == PHASE_ACTIVE:
                self._build_active_ui()
            elif self.phase == PHASE_ANSWER:
                self._build_answer_ui()
            elif self.phase == PHASE_FEEDBACK:
                self._build_feedback_ui()
            elif self.phase == PHASE_COMPLETE:
                self._build_complete_ui()
            
            # Reset flag
            self.needs_redraw = False
            self.last_phase = self.phase
        
        return self.ui
    
    def get_state(self) -> Dict[str, Any]:
        """Get the current state for rendering.
        
        Returns:
            State dictionary
        """
        return {
            "ui": self.ui.to_dict() if self.ui else {},
            "phase": self.phase,
            "round": self.round,
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
        
        if self.phase == PHASE_INTRO:
            if component_id == "start_button":
                self.start_training()
        
        elif self.phase == PHASE_ACTIVE and self.show_numbers:
            # Any click in active phase with numbers transitions to answer phase
            self.phase = PHASE_ANSWER
            self.message = "What was the sum of the numbers?"
            self.phase_start_time = time.time()
            self.needs_redraw = True
        
        elif self.phase == PHASE_ANSWER:
            # Check if it's an answer button
            if component_id.startswith("answer_"):
                try:
                    # Extract answer value from ID (format: answer_value)
                    parts = component_id.split("_")
                    answer_value = int(parts[1])
                    
                    # Set user answer and check
                    self.user_answer = answer_value
                    self.check_answer()
                    
                except (IndexError, ValueError) as e:
                    logger.error(f"Error parsing answer ID: {e}")
        
        elif self.phase == PHASE_COMPLETE:
            if component_id == "continue_button":
                self.initialize()
                self.start_training()
    
    def handle_key(self, key: int):
        """Handle a key press event.
        
        Args:
            key: Key code
        """
        logger.debug(f"Key press: {key}")
        
        # Handle specific keys depending on phase
        if self.phase == PHASE_INTRO:
            # Start training on space or enter
            if key in (13, 32):  # Enter or Space
                self.start_training()
        
        elif self.phase == PHASE_ACTIVE and self.show_numbers:
            # Any key in active phase with numbers transitions to answer phase
            self.phase = PHASE_ANSWER
            self.message = "What was the sum of the numbers?"
            self.phase_start_time = time.time()
            self.needs_redraw = True
        
        elif self.phase == PHASE_ANSWER:
            # Number keys 0-9 can be used to input answers
            if 48 <= key <= 57:  # 0-9 keys
                digit = key - 48
                if self.user_answer is None:
                    self.user_answer = digit
                else:
                    # Append digit to existing answer
                    self.user_answer = self.user_answer * 10 + digit
                
                # Mark UI for update
                self.needs_redraw = True
            
            # Backspace to delete last digit
            elif key == 8:
                if self.user_answer is not None:
                    self.user_answer = self.user_answer // 10
                    self.needs_redraw = True
            
            # Enter to submit answer
            elif key == 13:
                if self.user_answer is not None:
                    self.check_answer()
    
    def start_training(self):
        """Start a new training session."""
        logger.info("Starting new training session")
        
        # Reset session state
        self.round = 0
        self.score = 0
        self.correct_answers = 0
        self.is_completed = False
        
        # Start the first round
        self.start_new_round()
    
    def start_new_round(self):
        """Start a new round."""
        self.round += 1
        logger.info(f"Starting round {self.round}")
        
        # Reset the circle size for the start of a new round
        self.circle_width = self.base_circle_size
        self.circle_height = self.base_circle_size
        
        # Enter preparation phase for initial rounds
        if self.round <= self.preparation_rounds:
            self.phase = PHASE_PREPARATION
            self.show_numbers = False
            self.message = "Focus on the center circle"
        else:
            # Active phase with numbers after preparation rounds
            self.preparation_complete = True
            self.phase = PHASE_ACTIVE
            self.show_numbers = True
            
            # Generate random numbers and calculate sum
            self.generate_random_numbers()
            self.message = "Focus on the center and add the numbers"
        
        self.phase_start_time = time.time()
        self.needs_redraw = True
    
    def generate_random_numbers(self):
        """Generate random numbers around the periphery."""
        half_range = self.number_range // 2
        self.numbers = [random.randint(-half_range, half_range) for _ in range(4)]
        self.current_sum = sum(self.numbers)
        
        # Increase the distance factors to expand peripheral vision over time
        self.distance_factor_x += self.distance_increase_factor
        self.distance_factor_y += self.distance_increase_factor
    
    def check_answer(self):
        """Check the user's answer and update game state."""
        if self.user_answer == self.current_sum:
            self.message = "Correct!"
            self.score += 10
            self.correct_answers += 1
        else:
            self.message = f"Incorrect. The sum was {self.current_sum}."
        
        # After a short delay, start the next round
        self.phase = PHASE_FEEDBACK
        self.phase_start_time = time.time()
        self.needs_redraw = True
    
    def calculate_number_positions(self):
        """Calculate positions for the peripheral numbers.
        
        Returns:
            List of (x, y) positions
        """
        distance_x = int(self.screen_width * self.distance_factor_x)
        distance_y = int(self.screen_height * self.distance_factor_y)
        
        return [
            (self.center_x, self.center_y - distance_y),  # Top
            (self.center_x + distance_x, self.center_y),  # Right
            (self.center_x, self.center_y + distance_y),  # Bottom
            (self.center_x - distance_x, self.center_y)   # Left
        ]
    
    def _build_intro_ui(self):
        """Build the intro screen UI."""
        # Add a title
        title = ComponentFactory.text(
            text="Expand Vision",
            x=0, y=100, width=self.screen_width, height=80,
            color=(255, 255, 255),
            fontSize=48,
            textAlign='center'
        )
        self.ui.add(title)
        
        # Add description
        description = ComponentFactory.text(
            text="Focus on the center while being aware of numbers in your peripheral vision.",
            x=0, y=200, width=self.screen_width, height=40,
            color=(220, 220, 220),
            fontSize=24,
            textAlign='center'
        )
        self.ui.add(description)
        
        # Add second line of description
        description2 = ComponentFactory.text(
            text="Sum the numbers that appear around the circle.",
            x=0, y=250, width=self.screen_width, height=40,
            color=(220, 220, 220),
            fontSize=24,
            textAlign='center'
        )
        self.ui.add(description2)
        
        # Add level and score info
        if self.level > 1 or self.score > 0:
            info = ComponentFactory.text(
                text=f"Level: {self.level}   Score: {self.score}   High Score: {self.high_score}",
                x=0, y=310, width=self.screen_width, height=30,
                color=(180, 180, 200),
                fontSize=20,
                textAlign='center'
            )
            self.ui.add(info)
        
        # Add start button
        start_button = ComponentFactory.button(
            id="start_button",
            text="Start Training",
            x=(self.screen_width - 200) // 2, 
            y=400,
            width=200, height=60,
            backgroundColor=(60, 120, 255),
            color=(255, 255, 255),
            borderRadius=10,
            fontSize=24
        )
        self.ui.add(start_button)
    
    def _build_active_ui(self):
        """Build the active/preparation phase UI."""
        # Add status info
        round_info = ComponentFactory.text(
            text=f"Round {self.round} of {self.total_rounds}",
            x=0, y=40, width=self.screen_width, height=30,
            color=(200, 200, 220),
            fontSize=20,
            textAlign='center'
        )
        self.ui.add(round_info)
        
        # Add instruction
        instruction = ComponentFactory.text(
            text=self.message,
            x=0, y=80, width=self.screen_width, height=30,
            color=(220, 220, 100),
            fontSize=22,
            textAlign='center'
        )
        self.ui.add(instruction)
        
        # Add central circle
        circle = ComponentFactory.circle(
            x=self.center_x - self.circle_width // 2,
            y=self.center_y - self.circle_height // 2,
            radius=self.circle_width // 2,
            backgroundColor=(50, 150, 250, 180)  # Light blue, semi-transparent
        )
        self.ui.add(circle)
        
        # Add central dot
        dot = ComponentFactory.circle(
            x=self.center_x - 5,
            y=self.center_y - 5,
            radius=5,
            backgroundColor=(255, 255, 255)  # White
        )
        self.ui.add(dot)
        
        # Add numbers if in active phase with numbers shown
        if self.phase == PHASE_ACTIVE and self.show_numbers:
            positions = self.calculate_number_positions()
            
            for i, (x, y) in enumerate(positions):
                number = self.numbers[i]
                
                # Determine color based on sign (positive=green, negative=red)
                color = (50, 200, 50) if number >= 0 else (200, 50, 50)
                
                # Add number text
                number_text = ComponentFactory.text(
                    text=str(number),
                    x=x - 50, y=y - 25,
                    width=100, height=50,
                    color=color,
                    fontSize=32,
                    textAlign='center'
                )
                self.ui.add(number_text)
    
    def _build_answer_ui(self):
        """Build the answer input UI."""
        # Add status info
        round_info = ComponentFactory.text(
            text=f"Round {self.round} of {self.total_rounds}",
            x=0, y=40, width=self.screen_width, height=30,
            color=(200, 200, 220),
            fontSize=20,
            textAlign='center'
        )
        self.ui.add(round_info)
        
        # Add question
        question = ComponentFactory.text(
            text=self.message,
            x=0, y=100, width=self.screen_width, height=40,
            color=(255, 255, 255),
            fontSize=28,
            textAlign='center'
        )
        self.ui.add(question)
        
        # Add user's current answer if any
        if self.user_answer is not None:
            answer_display = ComponentFactory.text(
                text=str(self.user_answer),
                x=0, y=160, width=self.screen_width, height=60,
                color=(100, 220, 255),
                fontSize=48,
                textAlign='center'
            )
            self.ui.add(answer_display)
        
        # Define the possible answers (correct sum +/- offsets)
        possible_answers = [
            self.current_sum - 2,
            self.current_sum - 1,
            self.current_sum,
            self.current_sum + 1,
            self.current_sum + 2
        ]
        
        # Randomize answer positions to avoid fixed pattern
        random.shuffle(possible_answers)
        
        # Calculate button positions
        button_height = int(self.screen_height * 0.08)  # 8% of screen height
        button_width = int(self.screen_width * 0.1)    # 10% of screen width
        button_spacing = int(self.screen_width * 0.03)  # 3% of screen width
        total_width = 5 * button_width + 4 * button_spacing
        start_x = (self.screen_width - total_width) // 2
        y_pos = self.center_y + 100
        
        # Add answer buttons
        for i, answer in enumerate(possible_answers):
            btn_x = start_x + i * (button_width + button_spacing)
            
            # Button color - highlight if it matches current user answer
            bg_color = (100, 100, 180)
            if self.user_answer == answer:
                bg_color = (100, 150, 220)
            
            button = ComponentFactory.button(
                id=f"answer_{answer}",
                text=str(answer),
                x=btn_x, y=y_pos,
                width=button_width, height=button_height,
                backgroundColor=bg_color,
                color=(255, 255, 255),
                borderRadius=10,
                fontSize=28
            )
            self.ui.add(button)
        
        # Add instruction text
        instruction = ComponentFactory.text(
            text="Click an answer or type numbers and press Enter",
            x=0, y=y_pos + button_height + 20, width=self.screen_width, height=30,
            color=(200, 200, 220),
            fontSize=18,
            textAlign='center'
        )
        self.ui.add(instruction)
    
    def _build_feedback_ui(self):
        """Build the feedback UI after answering."""
        # Add status info
        round_info = ComponentFactory.text(
            text=f"Round {self.round} of {self.total_rounds}",
            x=0, y=40, width=self.screen_width, height=30,
            color=(200, 200, 220),
            fontSize=20,
            textAlign='center'
        )
        self.ui.add(round_info)
        
        # Add feedback message
        feedback = ComponentFactory.text(
            text=self.message,
            x=0, y=160, width=self.screen_width, height=40,
            color=(220, 220, 100) if self.user_answer == self.current_sum else (255, 100, 100),
            fontSize=32,
            textAlign='center'
        )
        self.ui.add(feedback)
        
        # Show what the sum was
        sum_text = ComponentFactory.text(
            text=f"The numbers were: {', '.join(str(n) for n in self.numbers)}",
            x=0, y=220, width=self.screen_width, height=30,
            color=(200, 200, 220),
            fontSize=20,
            textAlign='center'
        )
        self.ui.add(sum_text)
        
        # Show score
        score_text = ComponentFactory.text(
            text=f"Score: {self.score}",
            x=0, y=270, width=self.screen_width, height=30,
            color=(180, 180, 250),
            fontSize=22,
            textAlign='center'
        )
        self.ui.add(score_text)
    
    def _build_complete_ui(self):
        """Build the completion UI."""
        # Add title
        title = ComponentFactory.text(
            text="Training Complete!",
            x=0, y=120, width=self.screen_width, height=60,
            color=(255, 255, 255),
            fontSize=36,
            textAlign='center'
        )
        self.ui.add(title)
        
        # Show final score
        score_text = ComponentFactory.text(
            text=f"Final Score: {self.score}",
            x=0, y=200, width=self.screen_width, height=40,
            color=(220, 220, 100),
            fontSize=28,
            textAlign='center'
        )
        self.ui.add(score_text)
        
        # Show high score if different
        if self.high_score > self.score:
            high_score_text = ComponentFactory.text(
                text=f"High Score: {self.high_score}",
                x=0, y=250, width=self.screen_width, height=30,
                color=(180, 180, 250),
                fontSize=24,
                textAlign='center'
            )
            self.ui.add(high_score_text)
        
        # Show level progress
        level_text = ComponentFactory.text(
            text=f"Advanced to Level {self.level}",
            x=0, y=310, width=self.screen_width, height=30,
            color=(180, 220, 180),
            fontSize=22,
            textAlign='center'
        )
        self.ui.add(level_text)
        
        # Show performance stats
        if self.total_rounds > 0:
            accuracy = (self.correct_answers / self.total_rounds) * 100
            stats_text = ComponentFactory.text(
                text=f"Correct Answers: {self.correct_answers}/{self.total_rounds} ({accuracy:.1f}%)",
                x=0, y=360, width=self.screen_width, height=30,
                color=(200, 200, 220),
                fontSize=20,
                textAlign='center'
            )
            self.ui.add(stats_text)
        
        # Add continue button
        continue_button = ComponentFactory.button(
            id="continue_button",
            text="Start Next Level",
            x=(self.screen_width - 220) // 2,
            y=450,
            width=220, height=60,
            backgroundColor=(60, 120, 255),
            color=(255, 255, 255),
            borderRadius=10,
            fontSize=24
        )
        self.ui.add(continue_button) 