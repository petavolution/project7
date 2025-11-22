import random
import time
import math
from typing import Dict, Any, List, Tuple, Set
from ..core.training_module import TrainingModule


class ExpandVision(TrainingModule):
    """
    ExpandVision: A peripheral vision and attention training module.
    
    This module presents a central focus point with an expanding circle.
    After several rounds, random numbers appear around the periphery that
    the user must sum while maintaining central focus.
    
    Optimizations:
    - Resolution-independent layout using percentage-based calculations
    - State tracking for optimal delta encoding
    - Component-based rendering for improved performance
    - Adaptive difficulty scaling based on user performance
    """
    
    def __init__(self):
        super().__init__()
        # Module metadata
        self.name = "Expand Vision"
        self.description = "Focus gaze on center and calculate sum of numbers"
        
        # Track properties for efficient delta generation
        self._tracked_properties = self._tracked_properties.union({
            'phase', 'preparation_complete', 'circle_width', 'circle_height',
            'numbers', 'current_sum', 'user_answer', 'show_numbers', 'round',
            'correct_answers', 'total_rounds', 'distance_factor_x', 'distance_factor_y'
        })
        
        # Visual settings - use screen dimensions from base class
        self.screen_width = self.__class__.SCREEN_WIDTH
        self.screen_height = self.__class__.SCREEN_HEIGHT
        
        # Calculate center position based on screen dimensions
        self.center_x = self.screen_width // 2
        self.center_y = self.screen_height // 2
        
        # Calculate circle dimensions as percentage of screen height
        base_circle_size = self.screen_height * 0.05  # 5% of screen height
        self.circle_width = int(base_circle_size)
        self.circle_height = int(base_circle_size)
        self.circle_growth = int(base_circle_size * 0.15)  # Growth per round is 15% of base size
        
        # Number settings
        self.show_numbers = False  # Only show numbers after several rounds
        self.numbers = []  # The four numbers at the periphery
        self.number_range = 10  # Range for random numbers (-range/2 to range/2)
        self.current_sum = 0  # The sum of the current numbers
        self.user_answer = None  # User's submitted answer
        self.correct_answers = 0  # Count of correct answers
        self.round = 0  # Current round number
        self.total_rounds = 10  # Total rounds in a session
        
        # Phase settings
        self.phase = "preparation"  # Can be "preparation", "active", or "answer"
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
        
        # Performance tracking
        self.last_state_hash = None
        self.state_changes = 0
        
        # Initialize the first round
        self.start_new_round()
    
    def handle_click(self, x, y):
        """
        Handle mouse click events.
        
        Args:
            x: X coordinate of the click
            y: Y coordinate of the click
            
        Returns:
            Result dictionary with updated state
        """
        # During the active phase with numbers shown, clicking anywhere brings up answer input
        if self.phase == "active" and self.show_numbers:
            self.phase = "answer"
            self.state_changes += 1
            return {"result": "show_answer_input", "state": self.get_state()}
        
        # Check for clicks on number buttons during answer phase
        if self.phase == "answer":
            # Check if click is on an answer button
            button_height = int(self.screen_height * 0.06)  # 6% of screen height
            button_width = int(self.screen_width * 0.08)   # 8% of screen width
            
            # Define the possible answers (correct sum +/- offsets)
            possible_answers = [
                self.current_sum - 2,
                self.current_sum - 1,
                self.current_sum,
                self.current_sum + 1,
                self.current_sum + 2
            ]
            
            # Calculate button positions
            button_spacing = int(self.screen_width * 0.02)  # 2% of screen width
            total_width = 5 * button_width + 4 * button_spacing
            start_x = (self.screen_width - total_width) // 2
            
            for i in range(5):
                btn_x = start_x + i * (button_width + button_spacing)
                btn_y = self.center_y + int(self.screen_height * 0.05)  # Slightly below center
                
                # Check if click is within this button
                if btn_x <= x <= btn_x + button_width and btn_y <= y <= btn_y + button_height:
                    self.user_answer = possible_answers[i]
                    self.check_answer()
                    return {"result": "answer_selected", "state": self.get_state()}
        
        return {"result": "no_action", "state": self.get_state()}
    
    def check_answer(self):
        """Check the user's answer and update game state."""
        if self.user_answer == self.current_sum:
            self.message = "Correct!"
            self.score += 10
            self.correct_answers += 1
        else:
            self.message = f"Incorrect. The sum was {self.current_sum}."
        
        # After a short delay, start the next round
        self.phase = "feedback"
        self.phase_start_time = time.time()
        self.state_changes += 1
    
    def start_new_round(self):
        """Start a new round."""
        self.round += 1
        
        # Reset the circle size for the start of a new round
        base_circle_size = self.screen_height * 0.05
        self.circle_width = int(base_circle_size)
        self.circle_height = int(base_circle_size)
        
        # Enter preparation phase for initial rounds
        if self.round <= self.preparation_rounds:
            self.phase = "preparation"
            self.show_numbers = False
            self.message = "Focus on the center circle"
        else:
            # Active phase with numbers after preparation rounds
            self.preparation_complete = True
            self.phase = "active"
            self.show_numbers = True
            
            # Generate random numbers and calculate sum
            self.generate_random_numbers()
            self.message = "Focus on the center and add the numbers"
        
        self.phase_start_time = time.time()
        self.state_changes += 1
    
    def generate_random_numbers(self):
        """Generate random numbers around the periphery."""
        half_range = self.number_range // 2
        self.numbers = [random.randint(-half_range, half_range) for _ in range(4)]
        self.current_sum = sum(self.numbers)
        
        # Increase the distance factors to expand peripheral vision over time
        self.distance_factor_x += self.distance_increase_factor
        self.distance_factor_y += self.distance_increase_factor
    
    def update(self, dt):
        """
        Update module state based on elapsed time.
        
        Args:
            dt: Time delta since last update in seconds
        """
        super().update(dt)
        current_time = time.time()
        
        # Handle phases based on time
        if self.phase == "preparation":
            # Grow the circle during preparation phase
            self.circle_width += self.circle_growth
            self.circle_height += self.circle_growth
            
            # After a few seconds, reset for next round
            if current_time - self.phase_start_time > 2.0:
                if self.round < self.preparation_rounds:
                    self.start_new_round()
                else:
                    # Transition to active phase with numbers
                    self.preparation_complete = True
                    self.phase = "active"
                    self.show_numbers = True
                    self.generate_random_numbers()
                    self.message = "Focus on the center and add the numbers"
                    self.phase_start_time = current_time
                    self.state_changes += 1
        
        elif self.phase == "active":
            # Grow the circle during active phase
            self.circle_width += self.circle_growth
            self.circle_height += self.circle_growth
            
            # After display delay, either go to answer phase or next round
            if self.show_numbers and current_time - self.phase_start_time > self.display_delay / 1000:
                self.phase = "answer"
                self.message = "What was the sum of the numbers?"
                self.phase_start_time = current_time
                self.state_changes += 1
        
        elif self.phase == "feedback":
            # Show feedback for a short period
            if current_time - self.phase_start_time > 1.5:
                # Check if we've completed all rounds
                if self.round >= self.total_rounds:
                    self.is_completed = True
                    self.message = f"Training complete! Score: {self.score}"
                    self.level = 1  # Reset level for next session
                    self.state_changes += 1
                else:
                    # Start next round
                    self.start_new_round()
    
    def build_ui(self):
        """Build UI components for the current state."""
        self.ui.clear()
        
        # Always show the central circle
        circle_color = (50, 150, 250)  # Light blue
        self.ui.add_component(self.ui.circle(
            center=(self.center_x, self.center_y),
            radius=self.circle_width // 2,
            color=circle_color
        ))
        
        # Add module name
        self.ui.add_component(self.ui.text(
            text=self.name,
            position=(self.screen_width // 2, int(self.screen_height * 0.05)),
            font_size=int(self.screen_height * 0.03),
            color=(255, 255, 255),
            align="center"
        ))
        
        # Add score indicator
        self.ui.add_component(self.ui.text(
            text=f"Score: {self.score}",
            position=(int(self.screen_width * 0.9), int(self.screen_height * 0.05)),
            font_size=int(self.screen_height * 0.025),
            color=(200, 200, 200),
            align="right"
        ))
        
        # Add round indicator
        self.ui.add_component(self.ui.text(
            text=f"Round: {self.round}/{self.total_rounds}",
            position=(int(self.screen_width * 0.1), int(self.screen_height * 0.05)),
            font_size=int(self.screen_height * 0.025),
            color=(200, 200, 200),
            align="left"
        ))
        
        # Show peripheral numbers during active phase with numbers
        if self.phase == "active" and self.show_numbers:
            # Calculate positions for four numbers around the center
            number_positions = self.calculate_number_positions()
            number_font_size = int(self.screen_height * 0.05)  # 5% of screen height
            
            # Add the number components
            for i, number in enumerate(self.numbers):
                pos_x, pos_y = number_positions[i]
                self.ui.add_component(self.ui.text(
                    text=str(number),
                    position=(pos_x, pos_y),
                    font_size=number_font_size,
                    color=(255, 255, 255),
                    align="center"
                ))
        
        # Show answer input during answer phase
        if self.phase == "answer":
            self.build_answer_ui()
        
        # Show status message
        self.ui.add_component(self.ui.text(
            text=self.message,
            position=(self.screen_width // 2, int(self.screen_height * 0.9)),
            font_size=int(self.screen_height * 0.025),
            color=(255, 255, 0),
            align="center"
        ))
        
        return self.ui
    
    def build_answer_ui(self):
        """Build UI for answer selection."""
        # Create a set of buttons with possible answers
        possible_answers = [
            self.current_sum - 2,
            self.current_sum - 1,
            self.current_sum,
            self.current_sum + 1,
            self.current_sum + 2
        ]
        
        # Shuffle the answers to avoid having correct answer always in the middle
        shuffled_indices = list(range(5))
        random.shuffle(shuffled_indices)
        shuffled_answers = [possible_answers[i] for i in shuffled_indices]
        
        # Calculate button dimensions
        button_height = int(self.screen_height * 0.06)  # 6% of screen height
        button_width = int(self.screen_width * 0.08)   # 8% of screen width
        button_spacing = int(self.screen_width * 0.02)  # 2% of screen width
        
        # Calculate total width of all buttons
        total_width = 5 * button_width + 4 * button_spacing
        start_x = (self.screen_width - total_width) // 2
        btn_y = self.center_y + int(self.screen_height * 0.15)  # Below center
        
        # Create buttons for each possible answer
        for i, answer in enumerate(shuffled_answers):
            btn_x = start_x + i * (button_width + button_spacing)
            
            # Add the button component
            self.ui.add_component(self.ui.button(
                text=str(answer),
                position=(btn_x, btn_y),
                size=(button_width, button_height),
                color=(60, 70, 120),
                text_color=(255, 255, 255),
                border_radius=int(self.screen_height * 0.01)
            ))
    
    def calculate_number_positions(self):
        """Calculate positions for peripheral numbers based on current settings.
        
        Returns:
            List of (x, y) positions for the four numbers
        """
        # Calculate distances based on screen dimensions and current factors
        dist_x = int(self.screen_width * self.distance_factor_x)
        dist_y = int(self.screen_height * self.distance_factor_y)
        
        # Four positions in clockwise order starting from top
        positions = [
            (self.center_x, self.center_y - dist_y),  # Top
            (self.center_x + dist_x, self.center_y),  # Right
            (self.center_x, self.center_y + dist_y),  # Bottom
            (self.center_x - dist_x, self.center_y),  # Left
        ]
        
        return positions
    
    def get_module_state(self) -> Dict[str, Any]:
        """Get module-specific state.
        
        Returns:
            Dictionary with module-specific state
        """
        return {
            'expand_vision': {
                'phase': self.phase,
                'round': self.round,
                'total_rounds': self.total_rounds,
                'circle_size': (self.circle_width, self.circle_height),
                'show_numbers': self.show_numbers,
                'numbers': self.numbers if self.show_numbers else [],
                'current_sum': self.current_sum if self.phase == "answer" else None,
                'correct_answers': self.correct_answers,
                'preparation_complete': self.preparation_complete,
                'state_changes': self.state_changes
            }
        }
    
    def reset(self):
        """Reset the module to its initial state."""
        super().reset()
        
        # Reset visual settings
        base_circle_size = self.screen_height * 0.05
        self.circle_width = int(base_circle_size)
        self.circle_height = int(base_circle_size)
        
        # Reset game state
        self.show_numbers = False
        self.numbers = []
        self.current_sum = 0
        self.user_answer = None
        self.correct_answers = 0
        self.round = 0
        
        # Reset phase
        self.phase = "preparation"
        self.preparation_complete = False
        
        # Reset positioning
        self.distance_factor_x = 0.15
        self.distance_factor_y = 0.15
        
        # Reset timing
        self.start_time = time.time()
        self.phase_start_time = time.time()
        
        # Reset performance tracking
        self.last_state_hash = None
        self.state_changes = 0
        
        # Start first round
        self.start_new_round() 