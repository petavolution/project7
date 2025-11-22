#!/usr/bin/env python3
"""
Theme-aware Expand Vision training module for MetaMindIQTrain.

This module implements peripheral vision and attention training with:
- Theme-aware rendering using the unified theme system
- Resolution-independent layout using ScalingHelper
- Cache-optimized rendering with state tracking
- Adaptive difficulty scaling
"""

import random
import math
import logging
from typing import Dict, List, Tuple, Any, Optional, Union

from MetaMindIQTrain.core.training_module import TrainingModule
from MetaMindIQTrain.core.theme import Theme, ThemeProvider
from MetaMindIQTrain.core.scaling_helper import ScalingHelper
from MetaMindIQTrain.core.components import Component, UI

logger = logging.getLogger(__name__)

class ThemeAwareExpandVision(TrainingModule):
    """
    A peripheral vision and attention training module with theme awareness.
    
    This module presents a central focus point with an expanding circle and
    requires users to sum random numbers appearing around the periphery
    while maintaining focus on the central point.
    
    Features:
    - Theme-aware rendering using the unified theme system
    - Resolution-independent layout using ScalingHelper
    - State tracking optimization with delta encoding
    - Adaptive difficulty scaling
    """
    
    # Game phases
    PHASE_INTRO = 0
    PHASE_TRAINING = 1
    PHASE_ANSWER = 2
    PHASE_FEEDBACK = 3
    
    # Difficulty levels
    DIFFICULTY_LEVELS = [
        {"num_elements": 3, "duration": 5.0, "circle_expansion_rate": 0.8},
        {"num_elements": 4, "duration": 4.5, "circle_expansion_rate": 0.9},
        {"num_elements": 5, "duration": 4.0, "circle_expansion_rate": 1.0},
        {"num_elements": 6, "duration": 3.5, "circle_expansion_rate": 1.1},
        {"num_elements": 7, "duration": 3.0, "circle_expansion_rate": 1.2}
    ]
    
    def __init__(self, difficulty=1, theme_provider=None, **kwargs):
        """Initialize the ThemeAwareExpandVision module.
        
        Args:
            difficulty: Initial difficulty level (0-4)
            theme_provider: Theme provider for styling
            **kwargs: Additional arguments for the base class
        """
        super().__init__(**kwargs)
        
        # Set up difficulty
        self.difficulty = max(0, min(difficulty, len(self.DIFFICULTY_LEVELS) - 1))
        self.config = self.DIFFICULTY_LEVELS[self.difficulty]
        
        # Set up theme
        self.theme_provider = theme_provider or ThemeProvider()
        
        # Initialize scaling helper
        self.scaling_helper = ScalingHelper()
        
        # Game state
        self.phase = self.PHASE_INTRO
        self.timer = 0
        self.max_time = self.config["duration"]
        self.circle_radius = 30  # Starting radius, will be scaled
        self.max_circle_radius = 300  # Max radius, will be scaled
        
        # Elements (numbers on the periphery)
        self.elements = []
        self.correct_sum = 0
        self.user_answer = ""
        
        # Performance tracking
        self.score = 0
        self.rounds_played = 0
        
        # UI components
        self.ui = None
        
        # Start the first round
        self._start_intro_phase()
    
    def update(self, delta_time):
        """Update the module state.
        
        Args:
            delta_time: Time elapsed since the last update in seconds
        """
        if self.phase == self.PHASE_TRAINING:
            # Update timer
            self.timer += delta_time
            if self.timer >= self.max_time:
                self._transition_to_answer_phase()
            
            # Update expanding circle
            expansion_rate = self.config["circle_expansion_rate"]
            self.circle_radius = min(
                self.circle_radius + expansion_rate * delta_time * 60,
                self.max_circle_radius
            )
            
            # Rebuild UI with updated state
            self.build_ui()
    
    def handle_key_press(self, key):
        """Handle keyboard input.
        
        Args:
            key: The key that was pressed
        """
        if self.phase == self.PHASE_ANSWER:
            if key.isdigit() and len(self.user_answer) < 3:
                # Add digit to answer
                self.user_answer += key
                self.build_ui()
            elif key == "\b" and self.user_answer:  # Backspace
                # Remove last digit
                self.user_answer = self.user_answer[:-1]
                self.build_ui()
            elif key == "\r":  # Enter
                # Submit answer
                self._check_answer()
        elif self.phase == self.PHASE_INTRO and key == "\r":
            # Start training phase
            self._start_training_phase()
        elif self.phase == self.PHASE_FEEDBACK and key == "\r":
            # Start next round
            self._start_intro_phase()
    
    def handle_click(self, position):
        """Handle mouse click.
        
        Args:
            position: (x, y) position of the click
        """
        # Scale position based on resolution
        scaled_pos = self.scaling_helper.scale_pos(position)
        
        # Start button handling for intro phase
        if self.phase == self.PHASE_INTRO:
            start_button_rect = self._get_start_button_rect()
            if self._is_point_in_rect(scaled_pos, start_button_rect):
                self._start_training_phase()
        
        # Submit button handling for answer phase
        elif self.phase == self.PHASE_ANSWER:
            submit_button_rect = self._get_submit_button_rect()
            if self._is_point_in_rect(scaled_pos, submit_button_rect):
                self._check_answer()
        
        # Next round button handling for feedback phase
        elif self.phase == self.PHASE_FEEDBACK:
            next_button_rect = self._get_next_button_rect()
            if self._is_point_in_rect(scaled_pos, next_button_rect):
                self._start_intro_phase()
    
    def _is_point_in_rect(self, point, rect):
        """Check if a point is inside a rectangle.
        
        Args:
            point: (x, y) point
            rect: (x, y, width, height) rectangle
            
        Returns:
            True if the point is inside the rectangle, False otherwise
        """
        x, y = point
        rx, ry, rw, rh = rect
        return rx <= x <= rx + rw and ry <= y <= ry + rh
    
    def _get_start_button_rect(self):
        """Get the bounds of the start button.
        
        Returns:
            (x, y, width, height) rectangle
        """
        button_width = self.scaling_helper.scale_value(200)
        button_height = self.scaling_helper.scale_value(50)
        button_x = (self.resolution[0] - button_width) / 2
        button_y = self.resolution[1] / 2 + self.scaling_helper.scale_value(100)
        return (button_x, button_y, button_width, button_height)
    
    def _get_submit_button_rect(self):
        """Get the bounds of the submit button.
        
        Returns:
            (x, y, width, height) rectangle
        """
        button_width = self.scaling_helper.scale_value(200)
        button_height = self.scaling_helper.scale_value(50)
        button_x = (self.resolution[0] - button_width) / 2
        button_y = self.resolution[1] / 2 + self.scaling_helper.scale_value(100)
        return (button_x, button_y, button_width, button_height)
    
    def _get_next_button_rect(self):
        """Get the bounds of the next round button.
        
        Returns:
            (x, y, width, height) rectangle
        """
        button_width = self.scaling_helper.scale_value(200)
        button_height = self.scaling_helper.scale_value(50)
        button_x = (self.resolution[0] - button_width) / 2
        button_y = self.resolution[1] / 2 + self.scaling_helper.scale_value(100)
        return (button_x, button_y, button_width, button_height)
    
    def _start_intro_phase(self):
        """Start the introduction phase with instructions."""
        self.phase = self.PHASE_INTRO
        self.build_ui()
    
    def _start_training_phase(self):
        """Start the actual training with expanding circle and peripheral elements."""
        self.phase = self.PHASE_TRAINING
        self.timer = 0
        self.circle_radius = self.scaling_helper.scale_value(30)
        self.max_circle_radius = self.scaling_helper.scale_value(300)
        
        # Generate random elements (numbers)
        self._generate_elements()
        
        # Build initial UI
        self.build_ui()
    
    def _transition_to_answer_phase(self):
        """Transition to the answer input phase."""
        self.phase = self.PHASE_ANSWER
        self.user_answer = ""
        self.build_ui()
    
    def _check_answer(self):
        """Check the user's answer against the correct sum."""
        if not self.user_answer:
            return
        
        user_value = int(self.user_answer)
        is_correct = user_value == self.correct_sum
        
        # Update score
        if is_correct:
            self.score += 1
        
        # Update rounds played
        self.rounds_played += 1
        
        # Transition to feedback phase
        self.phase = self.PHASE_FEEDBACK
        self.build_ui()
    
    def _generate_elements(self):
        """Generate random number elements placed around the periphery."""
        # Clear previous elements
        self.elements = []
        
        # Get number of elements based on difficulty
        num_elements = self.config["num_elements"]
        
        # Calculate placement radius (bigger than the max circle radius)
        placement_radius = self.scaling_helper.scale_value(350)
        
        # Generate numbers between 1 and 9
        numbers = [random.randint(1, 9) for _ in range(num_elements)]
        self.correct_sum = sum(numbers)
        
        # Place elements around the circle
        center_x = self.resolution[0] / 2
        center_y = self.resolution[1] / 2
        
        for i in range(num_elements):
            # Calculate position on the periphery
            angle = (2 * math.pi * i / num_elements) + random.uniform(-0.2, 0.2)
            x = center_x + placement_radius * math.cos(angle)
            y = center_y + placement_radius * math.sin(angle)
            
            # Add element
            self.elements.append({
                "position": (x, y),
                "value": numbers[i],
                "size": self.scaling_helper.scale_value(40)
            })
    
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
        
        # Build phase-specific UI
        if self.phase == self.PHASE_INTRO:
            self._build_intro_ui()
        elif self.phase == self.PHASE_TRAINING:
            self._build_training_ui()
        elif self.phase == self.PHASE_ANSWER:
            self._build_answer_ui()
        elif self.phase == self.PHASE_FEEDBACK:
            self._build_feedback_ui()
        
        return self.ui
    
    def _build_intro_ui(self):
        """Build the intro phase UI with instructions."""
        # Main container
        container = self._add_main_container()
        
        # Title
        title = Component(
            type="text",
            text="Expand Vision",
            position=(self.resolution[0]/2, self.scaling_helper.scale_value(80)),
            style=self.theme_provider.theme.get_style("expand_vision.title"),
            align="center"
        )
        self.ui.add_component(title)
        
        # Instructions
        instructions = [
            "Focus on the center circle as it expands",
            "Notice the numbers appearing in your peripheral vision",
            "Add up all the numbers you see",
            "Enter the sum when prompted"
        ]
        
        y_offset = self.scaling_helper.scale_value(150)
        line_height = self.scaling_helper.scale_value(40)
        
        for instruction in instructions:
            text = Component(
                type="text",
                text=instruction,
                position=(self.resolution[0]/2, y_offset),
                style=self.theme_provider.theme.get_style("expand_vision.instruction"),
                align="center"
            )
            self.ui.add_component(text)
            y_offset += line_height
        
        # Difficulty info
        difficulty_text = f"Difficulty: {self.difficulty + 1}/5"
        difficulty = Component(
            type="text",
            text=difficulty_text,
            position=(self.resolution[0]/2, y_offset + line_height),
            style=self.theme_provider.theme.get_style("expand_vision.info"),
            align="center"
        )
        self.ui.add_component(difficulty)
        
        # Start button
        button_rect = self._get_start_button_rect()
        start_button = Component(
            type="rectangle",
            position=(button_rect[0], button_rect[1]),
            width=button_rect[2],
            height=button_rect[3],
            style=self.theme_provider.theme.get_style("expand_vision.button")
        )
        self.ui.add_component(start_button)
        
        # Button text
        button_text = Component(
            type="text",
            text="Start",
            position=(button_rect[0] + button_rect[2]/2, button_rect[1] + button_rect[3]/2),
            style=self.theme_provider.theme.get_style("expand_vision.button_text"),
            align="center"
        )
        self.ui.add_component(button_text)
        
        # Score display if there are previous rounds
        if self.rounds_played > 0:
            score_text = f"Score: {self.score}/{self.rounds_played}"
            score = Component(
                type="text",
                text=score_text,
                position=(self.resolution[0] - self.scaling_helper.scale_value(20), self.scaling_helper.scale_value(20)),
                style=self.theme_provider.theme.get_style("expand_vision.score"),
                align="right"
            )
            self.ui.add_component(score)
    
    def _build_training_ui(self):
        """Build the training phase UI with expanding circle and peripheral elements."""
        # Main container
        container = self._add_main_container()
        
        # Center point - outer circle (expanding)
        center_x = self.resolution[0] / 2
        center_y = self.resolution[1] / 2
        
        expanding_circle = Component(
            type="circle",
            position=(center_x, center_y),
            radius=self.circle_radius,
            style=self.theme_provider.theme.get_style("expand_vision.expanding_circle")
        )
        self.ui.add_component(expanding_circle)
        
        # Center point - inner circle (fixed)
        center_circle = Component(
            type="circle",
            position=(center_x, center_y),
            radius=self.scaling_helper.scale_value(15),
            style=self.theme_provider.theme.get_style("expand_vision.center_circle")
        )
        self.ui.add_component(center_circle)
        
        # Render number elements
        for element in self.elements:
            # Element circle
            circle = Component(
                type="circle",
                position=element["position"],
                radius=element["size"] / 2,
                style=self.theme_provider.theme.get_style("expand_vision.element")
            )
            self.ui.add_component(circle)
            
            # Element text (number)
            text = Component(
                type="text",
                text=str(element["value"]),
                position=element["position"],
                style=self.theme_provider.theme.get_style("expand_vision.element_text"),
                align="center"
            )
            self.ui.add_component(text)
        
        # Timer progress bar
        progress_width = self.scaling_helper.scale_value(300)
        progress_height = self.scaling_helper.scale_value(15)
        progress_x = (self.resolution[0] - progress_width) / 2
        progress_y = self.scaling_helper.scale_value(30)
        
        # Background
        timer_bg = Component(
            type="rectangle",
            position=(progress_x, progress_y),
            width=progress_width,
            height=progress_height,
            style=self.theme_provider.theme.get_style("expand_vision.timer_bg")
        )
        self.ui.add_component(timer_bg)
        
        # Progress fill
        progress_value = min(1.0, self.timer / self.max_time)
        timer_fill = Component(
            type="rectangle",
            position=(progress_x, progress_y),
            width=progress_width * progress_value,
            height=progress_height,
            style=self.theme_provider.theme.get_style("expand_vision.timer_fill")
        )
        self.ui.add_component(timer_fill)
    
    def _build_answer_ui(self):
        """Build the answer input UI."""
        # Main container
        container = self._add_main_container()
        
        # Title
        title = Component(
            type="text",
            text="What is the sum of all numbers?",
            position=(self.resolution[0]/2, self.scaling_helper.scale_value(150)),
            style=self.theme_provider.theme.get_style("expand_vision.question"),
            align="center"
        )
        self.ui.add_component(title)
        
        # User answer display
        answer_text = self.user_answer if self.user_answer else "_"
        answer = Component(
            type="text",
            text=answer_text,
            position=(self.resolution[0]/2, self.resolution[1]/2),
            style=self.theme_provider.theme.get_style("expand_vision.answer"),
            align="center"
        )
        self.ui.add_component(answer)
        
        # Submit button
        button_rect = self._get_submit_button_rect()
        submit_button = Component(
            type="rectangle",
            position=(button_rect[0], button_rect[1]),
            width=button_rect[2],
            height=button_rect[3],
            style=self.theme_provider.theme.get_style("expand_vision.button")
        )
        self.ui.add_component(submit_button)
        
        # Button text
        button_text = Component(
            type="text",
            text="Submit",
            position=(button_rect[0] + button_rect[2]/2, button_rect[1] + button_rect[3]/2),
            style=self.theme_provider.theme.get_style("expand_vision.button_text"),
            align="center"
        )
        self.ui.add_component(button_text)
        
        # Instructions for keyboard input
        instructions = Component(
            type="text",
            text="Type numbers using keyboard, press Enter to submit",
            position=(self.resolution[0]/2, self.resolution[1] - self.scaling_helper.scale_value(50)),
            style=self.theme_provider.theme.get_style("expand_vision.instruction"),
            align="center"
        )
        self.ui.add_component(instructions)
    
    def _build_feedback_ui(self):
        """Build the feedback UI showing whether the answer was correct."""
        # Main container
        container = self._add_main_container()
        
        # Determine if answer was correct
        user_value = int(self.user_answer) if self.user_answer else 0
        is_correct = user_value == self.correct_sum
        
        # Feedback message
        message = "Correct!" if is_correct else "Incorrect!"
        result = Component(
            type="text",
            text=message,
            position=(self.resolution[0]/2, self.scaling_helper.scale_value(150)),
            style=self.theme_provider.theme.get_style(
                "expand_vision.feedback.correct" if is_correct else "expand_vision.feedback.incorrect"
            ),
            align="center"
        )
        self.ui.add_component(result)
        
        # Show correct answer if wrong
        if not is_correct:
            correct_answer = Component(
                type="text",
                text=f"The correct sum was {self.correct_sum}",
                position=(self.resolution[0]/2, self.scaling_helper.scale_value(220)),
                style=self.theme_provider.theme.get_style("expand_vision.answer"),
                align="center"
            )
            self.ui.add_component(correct_answer)
        
        # Your answer
        your_answer = Component(
            type="text",
            text=f"Your answer: {self.user_answer}",
            position=(self.resolution[0]/2, self.scaling_helper.scale_value(290)),
            style=self.theme_provider.theme.get_style("expand_vision.info"),
            align="center"
        )
        self.ui.add_component(your_answer)
        
        # Score update
        new_score = Component(
            type="text",
            text=f"Score: {self.score}/{self.rounds_played}",
            position=(self.resolution[0]/2, self.scaling_helper.scale_value(360)),
            style=self.theme_provider.theme.get_style("expand_vision.score"),
            align="center"
        )
        self.ui.add_component(new_score)
        
        # Next round button
        button_rect = self._get_next_button_rect()
        next_button = Component(
            type="rectangle",
            position=(button_rect[0], button_rect[1]),
            width=button_rect[2],
            height=button_rect[3],
            style=self.theme_provider.theme.get_style("expand_vision.button")
        )
        self.ui.add_component(next_button)
        
        # Button text
        button_text = Component(
            type="text",
            text="Next Round",
            position=(button_rect[0] + button_rect[2]/2, button_rect[1] + button_rect[3]/2),
            style=self.theme_provider.theme.get_style("expand_vision.button_text"),
            align="center"
        )
        self.ui.add_component(button_text)
    
    def _add_main_container(self):
        """Add the main container to the UI.
        
        Returns:
            Container component
        """
        # Create full-screen container with theme styling
        container = Component(
            type="rectangle",
            position=(0, 0),
            width=self.resolution[0],
            height=self.resolution[1],
            style=self.theme_provider.theme.get_style("expand_vision.container")
        )
        
        # Add to UI
        self.ui.add_component(container)
        
        return container 