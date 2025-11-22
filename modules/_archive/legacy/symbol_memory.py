#!/usr/bin/env python3
"""
Symbol Memory Training Module for MetaMindIQTrain

This module tests the user's ability to memorize and recall
patterns of symbols in a grid. Supports adaptive difficulty
and various grid sizes.

Optimizations:
- State caching for improved delta encoding
- Component-based rendering for flexibility
- Dynamic grid generation for any screen resolution
- Adaptive difficulty with level progression
"""

import random
import time
import uuid
import json
import math
from typing import Dict, Any, List, Tuple, Set, Optional, Union

from ..core.training_module import TrainingModule
from ..config import SCREEN_WIDTH, SCREEN_HEIGHT


class SymbolMemory(TrainingModule):
    """
    Symbol Memory training module.
    
    This module displays a grid of symbols that the user must memorize.
    After a brief period, the symbols are hidden and then optionally modified,
    and the user must determine if the pattern was modified.
    """
    
    # Available symbols
    SYMBOLS = ["■", "●", "▲", "◆", "★", "♦", "♥", "♣", "♠", "⬡", "⬢", "⌘"]
    
    # Game phases
    PHASE_MEMORIZE = "memorize"
    PHASE_HIDDEN = "hidden"
    PHASE_COMPARE = "compare"
    PHASE_ANSWER = "answer"
    PHASE_FEEDBACK = "feedback"
    
    # Game states
    STATE_ACTIVE = "active"
    STATE_COMPLETED = "completed"
    
    def __init__(self, difficulty=1):
        """Initialize the Symbol Memory module.
        
        Args:
            difficulty: Initial difficulty level (1-10)
        """
        super().__init__()
        
        # Module metadata
        self.name = "Symbol Memory"
        self.description = "Memorize symbols in a grid and identify changes"
        self.category = "Memory"
        self.difficulty = max(1, min(10, difficulty))  # Clamp difficulty between 1-10
        self.level = self.difficulty
        
        # Grid properties
        self.min_grid_size = 2  # Minimum grid size
        self.max_grid_size = 6  # Maximum grid size
        self.current_grid_size = self._calculate_grid_size()  # Current grid size based on level
        
        # Track properties for efficient delta generation
        self._tracked_properties = self._tracked_properties.union({
            'phase', 'game_state', 'current_grid_size', 'original_pattern',
            'modified_pattern', 'was_modified', 'user_answer', 'timer_active', 
            'memorize_duration', 'hidden_duration', 'user_answer', 'round_score'
        })
        
        # Game state
        self.phase = self.PHASE_MEMORIZE
        self.game_state = self.STATE_ACTIVE
        self.original_pattern = None
        self.modified_pattern = None
        self.was_modified = False
        self.user_answer = None
        self.timer_active = True
        self.round_score = 0
        self.total_rounds = 0
        self.correct_rounds = 0
        
        # Timing settings (in seconds)
        self.phase_start_time = time.time()
        self.memorize_duration = self._calculate_memorize_duration()
        self.hidden_duration = 1.0  # Fixed duration for hidden phase
        
        # Performance tracking
        self.last_state_hash = None
        self.state_changes = 0
        
        # Screen dimensions from parent class
        self.screen_width = self.__class__.SCREEN_WIDTH
        self.screen_height = self.__class__.SCREEN_HEIGHT
        
        # Initialize first round
        self._generate_pattern()
    
    def handle_click(self, x, y):
        """Handle mouse click events.
        
        Args:
            x: X coordinate of click
            y: Y coordinate of click
            
        Returns:
            Dictionary with result and updated state
        """
        # Only handle clicks during the answer phase
        if self.phase == self.PHASE_ANSWER:
            # Check for clicks on YES button
            yes_rect = self._get_button_rect("yes")
            if self._is_point_in_rect(x, y, yes_rect):
                self.user_answer = True
                return self._process_answer()
            
            # Check for clicks on NO button
            no_rect = self._get_button_rect("no")
            if self._is_point_in_rect(x, y, no_rect):
                self.user_answer = False
                return self._process_answer()
            
            # No button was clicked
            return {"result": "no_action", "state": self.get_state()}
        
        elif self.phase == self.PHASE_FEEDBACK:
            # Check for clicks on CONTINUE button
            continue_rect = self._get_button_rect("continue")
            if self._is_point_in_rect(x, y, continue_rect):
                self._start_next_round()
                return {"result": "next_round", "state": self.get_state()}
        
        # Default response for clicks in other phases
        return {"result": "no_action", "state": self.get_state()}
    
    def update(self, dt):
        """Update module state based on elapsed time.
        
        Args:
            dt: Time delta since last update in seconds
        """
        super().update(dt)
        
        current_time = time.time()
        elapsed_since_phase = current_time - self.phase_start_time
        
        # Handle automatic phase transitions based on timers
        if self.timer_active:
            if self.phase == self.PHASE_MEMORIZE and elapsed_since_phase >= self.memorize_duration:
                self.phase = self.PHASE_HIDDEN
                self.phase_start_time = current_time
                self.state_changes += 1
            
            elif self.phase == self.PHASE_HIDDEN and elapsed_since_phase >= self.hidden_duration:
                self.phase = self.PHASE_COMPARE
                self.phase_start_time = current_time
                self.state_changes += 1
            
            elif self.phase == self.PHASE_COMPARE and elapsed_since_phase >= self.memorize_duration:
                self.phase = self.PHASE_ANSWER
                self.phase_start_time = current_time
                self.message = "Was the pattern modified?"
                self.state_changes += 1
        
        # Update UI message based on the current phase
        self._update_message()
    
    def _process_answer(self):
        """Process the user's answer and update game state.
        
        Returns:
            Dictionary with result and updated state
        """
        # Check if the answer is correct
        is_correct = (self.user_answer == self.was_modified)
        
        # Update score and statistics
        if is_correct:
            # Calculate score based on grid size and timing
            base_points = self.current_grid_size * 5
            time_bonus = max(0, int((self.memorize_duration * 1.5 - (time.time() - self.phase_start_time)) * 10))
            self.round_score = base_points + time_bonus
            self.score += self.round_score
            self.correct_rounds += 1
            self.message = f"Correct! +{self.round_score} points"
        else:
            self.round_score = 0
            self.message = "Incorrect. Try again."
        
        # Update total rounds
        self.total_rounds += 1
        
        # Transition to feedback phase
        self.phase = self.PHASE_FEEDBACK
        self.phase_start_time = time.time()
        self.state_changes += 1
        
        # Check if level should increase
        if self.correct_rounds >= 3 and self.correct_rounds % 3 == 0:
            self._increase_level()
        
        return {"result": "answer_processed", "correct": is_correct, "state": self.get_state()}
    
    def _start_next_round(self):
        """Start the next round with new patterns."""
        # Generate a new pattern
        self._generate_pattern()
        
        # Reset phase to memorize
        self.phase = self.PHASE_MEMORIZE
        self.phase_start_time = time.time()
        self.user_answer = None
        self.round_score = 0
        
        # Update message
        self.message = "Memorize the pattern"
        self.state_changes += 1
    
    def _increase_level(self):
        """Increase the difficulty level."""
        self.level += 1
        self.current_grid_size = self._calculate_grid_size()
        self.memorize_duration = self._calculate_memorize_duration()
        self.message = f"Level increased to {self.level}!"
    
    def _calculate_grid_size(self):
        """Calculate grid size based on current level.
        
        Returns:
            Grid size (width/height) in cells
        """
        # Grid size increases with level
        if self.level <= 2:
            return 2  # 2x2 grid for levels 1-2
        elif self.level <= 4:
            return 3  # 3x3 grid for levels 3-4
        elif self.level <= 6:
            return 4  # 4x4 grid for levels 5-6
        elif self.level <= 8:
            return 5  # 5x5 grid for levels 7-8
        else:
            return 6  # 6x6 grid for levels 9+
    
    def _calculate_memorize_duration(self):
        """Calculate memorization duration based on grid size and level.
        
        Returns:
            Duration in seconds
        """
        # Base duration depends on grid size
        base_duration = self.current_grid_size * 0.7  # 0.7 seconds per cell
        
        # Adjust for level difficulty (higher levels get less time)
        level_factor = max(0.6, 1.0 - (self.level * 0.02))  # Reduce by 2% per level, min 60%
        
        # Ensure minimum viewing time
        return max(2.0, base_duration * level_factor)
    
    def _generate_pattern(self):
        """Generate a new pattern to memorize."""
        # Create a new random pattern
        grid_size = self.current_grid_size
        pattern = []
        
        # Choose a subset of symbols to use for this pattern
        available_symbols = random.sample(self.SYMBOLS, min(grid_size * 2, len(self.SYMBOLS)))
        
        # Generate the grid with random symbols
        for row in range(grid_size):
            pattern_row = []
            for col in range(grid_size):
                # Each cell has a 70% chance of having a symbol
                if random.random() < 0.7:
                    symbol = random.choice(available_symbols)
                    pattern_row.append(symbol)
                else:
                    pattern_row.append(None)  # Empty cell
            pattern.append(pattern_row)
        
        self.original_pattern = pattern
        
        # Decide whether to modify the pattern
        self.was_modified = random.choice([True, False])
        
        if self.was_modified:
            # Create a modified copy of the pattern
            self.modified_pattern = self._create_modified_pattern(pattern)
        else:
            # Use the same pattern (no modification)
            self.modified_pattern = [row[:] for row in pattern]
        
        # Reset phase and timing
        self.phase = self.PHASE_MEMORIZE
        self.phase_start_time = time.time()
        self.state_changes += 1
    
    def _create_modified_pattern(self, original_pattern):
        """Create a modified version of the pattern.
        
        Args:
            original_pattern: Original pattern to modify
            
        Returns:
            Modified pattern
        """
        # Create a deep copy of the original pattern
        modified = [row[:] for row in original_pattern]
        grid_size = self.current_grid_size
        
        # The number of modifications increases with level
        num_modifications = 1 + (self.level // 3)
        
        # Apply random modifications
        for _ in range(num_modifications):
            # Choose a random modification type
            mod_type = random.choice(['change', 'add', 'remove'])
            
            if mod_type == 'change':
                # Change an existing symbol to a different one
                # Find cells with symbols
                filled_cells = []
                for row in range(grid_size):
                    for col in range(grid_size):
                        if modified[row][col] is not None:
                            filled_cells.append((row, col))
                
                if filled_cells:
                    # Choose a random filled cell
                    row, col = random.choice(filled_cells)
                    current_symbol = modified[row][col]
                    
                    # Get a different symbol
                    new_symbols = [s for s in self.SYMBOLS if s != current_symbol]
                    new_symbol = random.choice(new_symbols)
                    modified[row][col] = new_symbol
            
            elif mod_type == 'add':
                # Add a symbol to an empty cell
                # Find empty cells
                empty_cells = []
                for row in range(grid_size):
                    for col in range(grid_size):
                        if modified[row][col] is None:
                            empty_cells.append((row, col))
                
                if empty_cells:
                    # Choose a random empty cell
                    row, col = random.choice(empty_cells)
                    modified[row][col] = random.choice(self.SYMBOLS)
            
            elif mod_type == 'remove':
                # Remove a symbol
                # Find cells with symbols
                filled_cells = []
                for row in range(grid_size):
                    for col in range(grid_size):
                        if modified[row][col] is not None:
                            filled_cells.append((row, col))
                
                if filled_cells:
                    # Choose a random filled cell
                    row, col = random.choice(filled_cells)
                    modified[row][col] = None
        
        return modified
    
    def _update_message(self):
        """Update the message based on the current phase."""
        if self.phase == self.PHASE_MEMORIZE:
            self.message = "Memorize the pattern"
        elif self.phase == self.PHASE_HIDDEN:
            self.message = "..."
        elif self.phase == self.PHASE_COMPARE:
            self.message = "Compare with the original pattern"
        elif self.phase == self.PHASE_ANSWER:
            self.message = "Was the pattern modified?"
    
    def _get_button_rect(self, button_type):
        """Get the rectangle for a button.
        
        Args:
            button_type: Type of button ('yes', 'no', or 'continue')
            
        Returns:
            Dictionary with button rectangle properties
        """
        button_width = int(self.screen_width * 0.15)
        button_height = int(self.screen_height * 0.06)
        
        if button_type == "yes":
            x = int(self.screen_width * 0.35)
            y = int(self.screen_height * 0.75)
        elif button_type == "no":
            x = int(self.screen_width * 0.65)
            y = int(self.screen_height * 0.75)
        elif button_type == "continue":
            x = int(self.screen_width * 0.5) - button_width // 2
            y = int(self.screen_height * 0.75)
        else:
            # Default fallback
            x = 0
            y = 0
        
        return {
            'x': x,
            'y': y,
            'width': button_width,
            'height': button_height
        }
    
    def _is_point_in_rect(self, x, y, rect):
        """Check if a point is inside a rectangle.
        
        Args:
            x: X coordinate of point
            y: Y coordinate of point
            rect: Rectangle definition
            
        Returns:
            True if point is inside rectangle, False otherwise
        """
        return (rect['x'] <= x <= rect['x'] + rect['width'] and 
                rect['y'] <= y <= rect['y'] + rect['height'])
    
    def _calculate_cell_size(self) -> int:
        """Calculate the cell size based on grid size and screen dimensions.
        
        Returns:
            Cell size in pixels
        """
        # Leave some margin around the grid
        available_width = self.screen_width * 0.8
        available_height = self.screen_height * 0.6
        
        # Scale margins based on ui_sizes if available
        if hasattr(self, 'ui_sizes') and self.ui_sizes:
            # Use UI_MARGIN from ui_sizes if available
            margin_percent = self.ui_sizes.get('UI_MARGIN_PERCENT', 0.01)
            content_height_percent = self.ui_sizes.get('UI_CONTENT_HEIGHT_PERCENT', 0.6)
            
            # Adjust available space based on calculated UI layout
            available_width = self.screen_width * (1 - 2 * margin_percent)
            available_height = self.screen_height * content_height_percent
        
        # Choose the smaller dimension to fit the grid
        max_cell_width = available_width / self.current_grid_size
        max_cell_height = available_height / self.current_grid_size
        
        cell_size = min(max_cell_width, max_cell_height)
        
        # Ensure cell size is not too small but scales with resolution
        min_size = int(self.screen_height * 0.03)  # 3% of screen height as minimum
        
        # Scale cell size based on screen resolution to ensure it looks good at all resolutions
        if self.screen_width >= 1920:  # 4K and higher resolutions
            # Scale up for very high resolutions
            cell_size = cell_size * 1.2
        elif self.screen_width <= 800:  # Small screens
            # Scale down for very small screens
            cell_size = cell_size * 0.9
        
        # Ensure cell size is an integer
        return max(min_size, int(cell_size))
    
    def get_module_state(self) -> Dict[str, Any]:
        """Get module-specific state.
        
        Returns:
            Dictionary with module-specific state
        """
        return {
            'symbol_memory': {
                'phase': self.phase,
                'game_state': self.game_state,
                'grid_size': self.current_grid_size,
                'level': self.level,
                'total_rounds': self.total_rounds,
                'correct_rounds': self.correct_rounds,
                'memorize_duration': self.memorize_duration,
                'elapsed_time': time.time() - self.phase_start_time,
                'was_modified': self.was_modified if self.phase == self.PHASE_FEEDBACK else None,
                'user_answer': self.user_answer if self.phase in [self.PHASE_FEEDBACK] else None,
                'round_score': self.round_score if self.phase == self.PHASE_FEEDBACK else 0
            }
        }
    
    def build_ui(self):
        """Build UI components based on current state.
        
        Returns:
            UI object with components
        """
        self.ui.clear()
        
        # Add module title
        self.ui.add_component(self.ui.text(
            text=self.name,
            position=(self.screen_width // 2, int(self.screen_height * 0.05)),
            font_size=int(self.screen_height * 0.03),
            color=(255, 255, 255),
            align="center"
        ))
        
        # Add level and score indicators
        self.ui.add_component(self.ui.text(
            text=f"Level: {self.level}",
            position=(int(self.screen_width * 0.1), int(self.screen_height * 0.05)),
            font_size=int(self.screen_height * 0.025),
            color=(200, 200, 200),
            align="left"
        ))
        
        self.ui.add_component(self.ui.text(
            text=f"Score: {self.score}",
            position=(int(self.screen_width * 0.9), int(self.screen_height * 0.05)),
            font_size=int(self.screen_height * 0.025),
            color=(200, 200, 200),
            align="right"
        ))
        
        # Add the symbol grid
        self._add_symbol_grid()
        
        # Add UI elements based on the current phase
        if self.phase == self.PHASE_ANSWER:
            self._add_answer_buttons()
        elif self.phase == self.PHASE_FEEDBACK:
            self._add_feedback_ui()
        
        # Add message
        self.ui.add_component(self.ui.text(
            text=self.message,
            position=(self.screen_width // 2, int(self.screen_height * 0.9)),
            font_size=int(self.screen_height * 0.025),
            color=(255, 255, 0),
            align="center"
        ))
        
        return self.ui
    
    def _add_symbol_grid(self):
        """Add the symbol grid to the UI based on current phase."""
        # Calculate grid position and cell size
        cell_size = self._calculate_cell_size()
        grid_size = self.current_grid_size
        grid_width = grid_size * cell_size
        grid_height = grid_size * cell_size
        
        # Center the grid on screen
        grid_x = (self.screen_width - grid_width) // 2
        grid_y = (self.screen_height - grid_height) // 2
        
        # Calculate border size based on screen resolution
        border_width = max(2, int(self.screen_height * 0.003))  # Scale with resolution
        border_color = (100, 100, 150)
        
        # Create grid borders with adaptive sizing
        self.ui.add_component(self.ui.rectangle(
            position=(grid_x - border_width * 2, grid_y - border_width * 2),
            size=(grid_width + border_width * 4, grid_height + border_width * 4),
            color=(0, 0, 0),
            border_width=border_width,
            border_color=border_color
        ))
        
        # Determine which pattern to display based on phase
        if self.phase == self.PHASE_MEMORIZE:
            display_pattern = self.original_pattern
        elif self.phase in [self.PHASE_COMPARE, self.PHASE_ANSWER, self.PHASE_FEEDBACK]:
            display_pattern = self.modified_pattern
        else:
            # During hidden phase, don't display symbols
            display_pattern = [[None for _ in range(grid_size)] for _ in range(grid_size)]
        
        # Add cells and symbols
        font_size = int(cell_size * 0.7)
        cell_border = max(1, int(self.screen_height * 0.001))  # Scale cell border with resolution
        
        for row in range(grid_size):
            for col in range(grid_size):
                # Calculate cell position
                cell_x = grid_x + col * cell_size
                cell_y = grid_y + row * cell_size
                
                # Add cell background
                self.ui.add_component(self.ui.rectangle(
                    position=(cell_x, cell_y),
                    size=(cell_size, cell_size),
                    color=(30, 30, 50),
                    border_width=cell_border,
                    border_color=(70, 70, 100)
                ))
                
                # Add symbol if present
                if display_pattern and row < len(display_pattern) and col < len(display_pattern[row]):
                    symbol = display_pattern[row][col]
                    if symbol:
                        self.ui.add_component(self.ui.text(
                            text=symbol,
                            position=(cell_x + cell_size // 2, cell_y + cell_size // 2),
                            font_size=font_size,
                            color=(255, 255, 255),
                            align="center"
                        ))
    
    def _add_answer_buttons(self):
        """Add yes/no answer buttons to the UI."""
        # Get button dimensions
        yes_rect = self._get_button_rect('yes')
        no_rect = self._get_button_rect('no')
        
        # Add YES button
        self.ui.add_component(self.ui.button(
            text="Yes",
            position=(yes_rect['x'], yes_rect['y']),
            size=(yes_rect['width'], yes_rect['height']),
            color=(50, 120, 50),
            text_color=(255, 255, 255),
            border_radius=int(self.screen_height * 0.01)
        ))
        
        # Add NO button
        self.ui.add_component(self.ui.button(
            text="No",
            position=(no_rect['x'], no_rect['y']),
            size=(no_rect['width'], no_rect['height']),
            color=(120, 50, 50),
            text_color=(255, 255, 255),
            border_radius=int(self.screen_height * 0.01)
        ))
    
    def _add_feedback_ui(self):
        """Add feedback UI elements during the feedback phase."""
        # Get continue button dimensions
        continue_rect = self._get_button_rect('continue')
        
        # Add feedback text
        if self.user_answer == self.was_modified:
            # Correct answer
            feedback_color = (100, 255, 100)
            if self.was_modified:
                feedback_text = "Correct! The pattern was modified."
            else:
                feedback_text = "Correct! The pattern was not modified."
        else:
            # Incorrect answer
            feedback_color = (255, 100, 100)
            if self.was_modified:
                feedback_text = "Incorrect. The pattern was modified."
            else:
                feedback_text = "Incorrect. The pattern was not modified."
        
        # Add feedback text
        self.ui.add_component(self.ui.text(
            text=feedback_text,
            position=(self.screen_width // 2, int(self.screen_height * 0.65)),
            font_size=int(self.screen_height * 0.025),
            color=feedback_color,
            align="center"
        ))
        
        # Add continue button
        self.ui.add_component(self.ui.button(
            text="Continue",
            position=(continue_rect['x'], continue_rect['y']),
            size=(continue_rect['width'], continue_rect['height']),
            color=(60, 60, 120),
            text_color=(255, 255, 255),
            border_radius=int(self.screen_height * 0.01)
        ))
    
    def reset(self):
        """Reset the module to its initial state."""
        super().reset()
        
        # Reset game state
        self.phase = self.PHASE_MEMORIZE
        self.game_state = self.STATE_ACTIVE
        self.original_pattern = None
        self.modified_pattern = None
        self.was_modified = False
        self.user_answer = None
        self.round_score = 0
        self.total_rounds = 0
        self.correct_rounds = 0
        
        # Reset difficulty settings
        self.level = self.difficulty
        self.current_grid_size = self._calculate_grid_size()
        self.memorize_duration = self._calculate_memorize_duration()
        
        # Reset timing
        self.phase_start_time = time.time()
        
        # Reset performance tracking
        self.last_state_hash = None
        self.state_changes = 0
        
        # Generate first pattern
        self._generate_pattern()
        
        # Reset message
        self.message = "Memorize the pattern"
    
    def cleanup(self):
        """Clean up resources."""
        super().cleanup()
        self.symbol_colors.clear()
        self.needs_full_update = True 