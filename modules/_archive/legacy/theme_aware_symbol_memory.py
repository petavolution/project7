#!/usr/bin/env python3
"""
Theme-Aware Symbol Memory Training Module for MetaMindIQTrain

This module tests the user's ability to memorize and recall
patterns of symbols in a grid, with enhanced theme support
and resolution scaling.

Features:
- Theme-aware rendering for consistent visual styling
- Resolution-independent layout with proper scaling
- Cache-optimized rendering for improved performance
- Adaptive difficulty with level progression
"""

import random
import time
import math
from typing import Dict, Any, List, Tuple, Set, Optional, Union

# Try to import from the package
try:
    from ..core.training_module import TrainingModule
    from ..core.theme import Theme, get_theme, ThemeProvider
    from ..core.scaling_helper import ScalingHelper
    from ..core.module_theme_styles import register_cognitive_module_styles
except ImportError:
    # For direct execution during development
    import sys
    import os
    from pathlib import Path
    
    # Add the project root to the path
    project_root = Path(__file__).resolve().parent.parent
    sys.path.insert(0, str(project_root))
    
    # Now import from the absolute path
    from MetaMindIQTrain.core.training_module import TrainingModule
    from MetaMindIQTrain.core.theme import Theme, get_theme, ThemeProvider
    from MetaMindIQTrain.core.scaling_helper import ScalingHelper
    from MetaMindIQTrain.core.module_theme_styles import register_cognitive_module_styles


class ThemeAwareSymbolMemory(TrainingModule):
    """
    Theme-aware Symbol Memory training module.
    
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
    
    def __init__(self, difficulty=1, theme_provider=None):
        """Initialize the Symbol Memory module with theme support.
        
        Args:
            difficulty: Initial difficulty level (1-10)
            theme_provider: Optional ThemeProvider instance
        """
        super().__init__()
        
        # Module metadata
        self.name = "Symbol Memory"
        self.description = "Memorize symbols in a grid and identify changes"
        self.category = "Memory"
        self.difficulty = max(1, min(10, difficulty))  # Clamp difficulty between 1-10
        self.level = self.difficulty
        
        # Set up theme provider
        self.theme_provider = theme_provider or ThemeProvider()
        if not self.theme_provider.get_theme():
            # Set a default theme if none is provided
            from ..core.theme import create_dark_theme
            theme = create_dark_theme()
            register_cognitive_module_styles(theme)
            self.theme_provider.set_theme(theme)
        
        # Initialize the scaling helper
        self.scaling = ScalingHelper()
        
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
        
        # Initialize first round
        self._generate_pattern()
    
    def handle_click(self, x, y):
        """Handle mouse click events with proper scaling.
        
        Args:
            x: X coordinate of click
            y: Y coordinate of click
            
        Returns:
            Dictionary with result and updated state
        """
        # Convert screen coordinates to logical coordinates
        logical_x, logical_y = x / self.scaling.scale_x, y / self.scaling.scale_y
        
        # Only handle clicks during the answer phase
        if self.phase == self.PHASE_ANSWER:
            # Check for clicks on YES button
            yes_rect = self._get_button_rect("yes")
            if self._is_point_in_rect(logical_x, logical_y, yes_rect):
                self.user_answer = True
                return self._process_answer()
            
            # Check for clicks on NO button
            no_rect = self._get_button_rect("no")
            if self._is_point_in_rect(logical_x, logical_y, no_rect):
                self.user_answer = False
                return self._process_answer()
            
            # No button was clicked
            return {"result": "no_action", "state": self.get_state()}
        
        elif self.phase == self.PHASE_FEEDBACK:
            # Check for clicks on CONTINUE button
            continue_rect = self._get_button_rect("continue")
            if self._is_point_in_rect(logical_x, logical_y, continue_rect):
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
        """Calculate memorization duration based on level and grid size.
        
        Returns:
            Duration in seconds
        """
        # Base duration decreases with level
        base_duration = max(3.0, 10.0 - (self.level * 0.5))
        
        # Add time based on grid size
        size_factor = (self.current_grid_size ** 2) / 8  # Squared for exponential increase
        
        return base_duration + size_factor
    
    def _generate_pattern(self):
        """Generate a new pattern for memorization."""
        # Create original pattern
        size = self.current_grid_size
        self.original_pattern = []
        
        # Available symbol subset (reduce options for lower levels)
        available_symbols = self.SYMBOLS[:min(len(self.SYMBOLS), 4 + self.level)]
        
        # Generate a random pattern of symbols
        for _ in range(size * size):
            symbol = random.choice(available_symbols)
            self.original_pattern.append(symbol)
        
        # Decide whether to modify the pattern for comparison
        self.was_modified = random.choice([True, False])
        
        if self.was_modified:
            # Create modified pattern by changing a few symbols
            self.modified_pattern = self._create_modified_pattern(self.original_pattern)
        else:
            # Use the same pattern
            self.modified_pattern = self.original_pattern.copy()
    
    def _create_modified_pattern(self, original_pattern):
        """Create a modified version of the pattern.
        
        Args:
            original_pattern: The original pattern to modify
            
        Returns:
            Modified pattern list
        """
        # Copy the original pattern
        modified = original_pattern.copy()
        
        # Calculate number of changes based on difficulty
        total_symbols = len(original_pattern)
        num_changes = max(1, min(3, total_symbols // 8))  # At least 1, at most 3 changes
        
        # Make changes
        for _ in range(num_changes):
            # Choose a random position
            position = random.randint(0, total_symbols - 1)
            
            # Get current symbol
            current_symbol = modified[position]
            
            # Choose a different symbol
            available_symbols = self.SYMBOLS[:min(len(self.SYMBOLS), 4 + self.level)]
            available_symbols = [s for s in available_symbols if s != current_symbol]
            
            # Change the symbol
            modified[position] = random.choice(available_symbols)
        
        return modified
    
    def _update_message(self):
        """Update the UI message based on the current phase."""
        if self.phase == self.PHASE_MEMORIZE:
            self.message = "Memorize the pattern"
        elif self.phase == self.PHASE_HIDDEN:
            self.message = "Waiting..."
        elif self.phase == self.PHASE_COMPARE:
            self.message = "Is this the same pattern?"
        elif self.phase == self.PHASE_ANSWER:
            self.message = "Was the pattern modified?"
    
    def _get_button_rect(self, button_type):
        """Get the rectangle for a button.
        
        Args:
            button_type: Type of button ("yes", "no", or "continue")
            
        Returns:
            Button rectangle as (x, y, width, height)
        """
        # Calculate button dimensions
        button_width = 150
        button_height = 50
        spacing = 20
        
        # Calculate base position
        screen_width = self.screen_width
        screen_height = self.screen_height
        
        if button_type == "yes":
            x = (screen_width / 2) - button_width - (spacing / 2)
            y = screen_height * 0.7
            return (x, y, button_width, button_height)
        
        elif button_type == "no":
            x = (screen_width / 2) + (spacing / 2)
            y = screen_height * 0.7
            return (x, y, button_width, button_height)
        
        elif button_type == "continue":
            x = (screen_width / 2) - (button_width / 2)
            y = screen_height * 0.7
            return (x, y, button_width, button_height)
        
        # Default empty rect
        return (0, 0, 0, 0)
    
    def _is_point_in_rect(self, x, y, rect):
        """Check if a point is inside a rectangle.
        
        Args:
            x: X coordinate of point
            y: Y coordinate of point
            rect: Rectangle as (x, y, width, height)
            
        Returns:
            True if point is inside rectangle, False otherwise
        """
        rx, ry, rw, rh = rect
        return (rx <= x <= rx + rw) and (ry <= y <= ry + rh)
    
    def _calculate_cell_size(self) -> int:
        """Calculate the size of grid cells.
        
        Returns:
            Cell size in pixels
        """
        # Base size with scaling
        base_size = 60
        
        # Adjust based on grid size to ensure it fits on screen
        max_grid_dimension = max(self.min_grid_size, self.current_grid_size)
        available_space = min(self.screen_width, self.screen_height) * 0.6
        
        # Calculate cell size to fit the grid
        cell_size = min(base_size, available_space / max_grid_dimension)
        
        # Scale for current resolution
        return self.scaling.scale_size(int(cell_size))
    
    def build_ui(self, renderer):
        """Build the UI using the provided renderer.
        
        Args:
            renderer: The renderer to use for building UI components
            
        Returns:
            Dictionary of UI components
        """
        theme = self.theme_provider.get_theme()
        ui_components = {}
        
        # Update scaling from current renderer if possible
        try:
            info = pygame.display.Info()
            self.scaling.update_scale_factors(info.current_w, info.current_h)
        except (NameError, AttributeError):
            pass
        
        # Add appropriate UI components based on current phase
        if self.phase == self.PHASE_MEMORIZE:
            # Show original pattern
            ui_components.update(self._add_symbol_grid(renderer, self.original_pattern))
            
            # Add timer bar
            elapsed = time.time() - self.phase_start_time
            progress = min(1.0, elapsed / self.memorize_duration)
            
            timer_pos = self.scaling.scale_pos((self.screen_width * 0.25, self.screen_height * 0.9))
            timer_size = self.scaling.scale_size((self.screen_width * 0.5, 20))
            
            # Use themed timer bar
            ui_components["timer"] = renderer.render_progress(
                timer_pos,
                timer_size,
                progress,
                variant="timer"
            )
            
        elif self.phase == self.PHASE_HIDDEN:
            # Show placeholder grid
            empty_pattern = [""] * (self.current_grid_size * self.current_grid_size)
            ui_components.update(self._add_symbol_grid(renderer, empty_pattern))
            
        elif self.phase == self.PHASE_COMPARE:
            # Show modified pattern
            ui_components.update(self._add_symbol_grid(renderer, self.modified_pattern))
            
            # Add timer bar
            elapsed = time.time() - self.phase_start_time
            progress = min(1.0, elapsed / self.memorize_duration)
            
            timer_pos = self.scaling.scale_pos((self.screen_width * 0.25, self.screen_height * 0.9))
            timer_size = self.scaling.scale_size((self.screen_width * 0.5, 20))
            
            # Use themed timer bar
            ui_components["timer"] = renderer.render_progress(
                timer_pos,
                timer_size,
                progress,
                variant="timer"
            )
            
        elif self.phase == self.PHASE_ANSWER:
            # Show answer buttons
            ui_components.update(self._add_answer_buttons(renderer))
            
        elif self.phase == self.PHASE_FEEDBACK:
            # Show feedback UI
            ui_components.update(self._add_feedback_ui(renderer))
        
        # Add common elements
        
        # Add message
        message_pos = self.scaling.scale_pos((self.screen_width / 2, self.screen_height * 0.1))
        ui_components["message"] = renderer.render_text(
            self.message,
            message_pos,
            variant="heading",
            textAlign="center"
        )
        
        # Add score
        score_pos = self.scaling.scale_pos((self.screen_width * 0.9, self.screen_height * 0.05))
        ui_components["score"] = renderer.render_text(
            f"Score: {self.score}",
            score_pos,
            variant="label",
            textAlign="right"
        )
        
        # Add level
        level_pos = self.scaling.scale_pos((self.screen_width * 0.1, self.screen_height * 0.05))
        ui_components["level"] = renderer.render_text(
            f"Level: {self.level}",
            level_pos,
            variant="label",
            textAlign="left"
        )
        
        return ui_components
    
    def _add_symbol_grid(self, renderer, pattern):
        """Add a grid of symbols to the UI.
        
        Args:
            renderer: The renderer to use
            pattern: List of symbols to display
            
        Returns:
            Dictionary of UI components for the grid
        """
        components = {}
        
        # Calculate grid layout
        cell_size = self._calculate_cell_size()
        grid_size = self.current_grid_size
        
        # Calculate total grid size
        grid_width = grid_size * cell_size
        grid_height = grid_size * cell_size
        
        # Center the grid on screen
        start_x = (self.screen_width - grid_width) / 2
        start_y = (self.screen_height - grid_height) / 2
        
        # Create container for grid
        grid_pos = self.scaling.scale_pos((start_x, start_y))
        grid_size = self.scaling.scale_size((grid_width, grid_height))
        
        components["grid_container"] = renderer.render_container(
            grid_pos,
            grid_size,
            variant="card"
        )
        
        # Add symbols to grid
        for i, symbol in enumerate(pattern):
            row = i // grid_size
            col = i % grid_size
            
            # Calculate position
            x = start_x + (col * cell_size) + (cell_size / 2)
            y = start_y + (row * cell_size) + (cell_size / 2)
            
            # Scale position
            pos = self.scaling.scale_pos((x, y))
            
            # Determine state
            state = None
            if self.phase == self.PHASE_HIDDEN:
                state = "hidden"
            
            # Add symbol
            symbol_key = f"symbol_{row}_{col}"
            
            if symbol:  # Only render if there's a symbol to show
                components[symbol_key] = renderer.render_circle(
                    pos,
                    self.scaling.scale_size(cell_size * 0.4),  # Symbol size is 80% of cell size
                    variant="symbol",
                    state=state
                )
                
                # Add text for symbol
                components[f"symbol_text_{row}_{col}"] = renderer.render_text(
                    symbol,
                    pos,
                    variant="symbol_text",
                    state=state,
                    textAlign="center"
                )
        
        return components
    
    def _add_answer_buttons(self, renderer):
        """Add YES/NO answer buttons to the UI.
        
        Args:
            renderer: The renderer to use
            
        Returns:
            Dictionary of UI components for the buttons
        """
        components = {}
        
        # Get button rectangles
        yes_rect = self._get_button_rect("yes")
        no_rect = self._get_button_rect("no")
        
        # Scale button positions and sizes
        yes_pos = self.scaling.scale_pos((yes_rect[0], yes_rect[1]))
        yes_size = self.scaling.scale_size((yes_rect[2], yes_rect[3]))
        
        no_pos = self.scaling.scale_pos((no_rect[0], no_rect[1]))
        no_size = self.scaling.scale_size((no_rect[2], no_rect[3]))
        
        # Add YES button
        components["yes_button"] = renderer.render_button(
            "YES",
            yes_pos,
            yes_size,
            variant="success"
        )
        
        # Add NO button
        components["no_button"] = renderer.render_button(
            "NO",
            no_pos,
            no_size,
            variant="danger"
        )
        
        return components
    
    def _add_feedback_ui(self, renderer):
        """Add feedback UI components.
        
        Args:
            renderer: The renderer to use
            
        Returns:
            Dictionary of UI components for feedback
        """
        components = {}
        
        # Determine feedback type
        is_correct = (self.user_answer == self.was_modified)
        feedback_variant = "correct" if is_correct else "incorrect"
        
        # Create feedback container
        container_width = self.screen_width * 0.8
        container_height = self.screen_height * 0.3
        
        container_x = (self.screen_width - container_width) / 2
        container_y = (self.screen_height - container_height) / 2
        
        # Scale position and size
        container_pos = self.scaling.scale_pos((container_x, container_y))
        container_size = self.scaling.scale_size((container_width, container_height))
        
        # Create feedback rectangle with appropriate styling
        components["feedback_container"] = renderer.render_rectangle(
            container_pos,
            container_size,
            variant="feedback",
            state=feedback_variant
        )
        
        # Add feedback message
        message_pos = self.scaling.scale_pos((self.screen_width / 2, container_y + container_height * 0.3))
        
        if is_correct:
            message = f"Correct! +{self.round_score} points"
        else:
            modified_text = "was" if self.was_modified else "was not"
            message = f"Incorrect. The pattern {modified_text} modified."
        
        components["feedback_message"] = renderer.render_text(
            message,
            message_pos,
            variant="heading",
            textAlign="center"
        )
        
        # Add continue button
        continue_rect = self._get_button_rect("continue")
        button_pos = self.scaling.scale_pos((continue_rect[0], continue_rect[1]))
        button_size = self.scaling.scale_size((continue_rect[2], continue_rect[3]))
        
        components["continue_button"] = renderer.render_button(
            "Continue",
            button_pos,
            button_size,
            variant="primary"
        )
        
        return components
    
    def render(self, renderer):
        """Render the module using the provided renderer.
        
        Args:
            renderer: Renderer to use for drawing
        """
        # Build and render UI components
        ui_components = self.build_ui(renderer)
        
        # The components are already rendered in build_ui
        pass
    
    def reset(self):
        """Reset the module to its initial state."""
        # Reset game state
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
        self.score = 0
        
        # Reset timing
        self.phase_start_time = time.time()
        
        # Generate first pattern
        self._generate_pattern()
    
    def cleanup(self):
        """Clean up resources used by the module."""
        # Nothing to clean up for this module
        pass
    
    def get_state(self):
        """Get the current state of the module.
        
        Returns:
            Dictionary with current state
        """
        # Get base state from parent class
        state = super().get_state()
        
        # Add module-specific state
        module_state = {
            "phase": self.phase,
            "game_state": self.game_state,
            "grid_size": self.current_grid_size,
            "memorize_duration": self.memorize_duration,
            "level": self.level,
            "round_score": self.round_score,
            "total_rounds": self.total_rounds,
            "correct_rounds": self.correct_rounds
        }
        
        # Merge states
        state.update(module_state)
        
        return state

# For direct module testing
if __name__ == "__main__":
    import pygame
    
    # Initialize pygame
    pygame.init()
    
    # Create display
    screen = pygame.display.set_mode((1024, 768))
    pygame.display.set_caption("Symbol Memory Test")
    
    # Create module
    module = ThemeAwareSymbolMemory()
    
    # Main loop
    running = True
    clock = pygame.time.Clock()
    
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                module.handle_click(*event.pos)
        
        # Update module
        module.update(1/60)  # 60 FPS
        
        # Clear screen
        screen.fill((0, 0, 0))
        
        # Render module (would need an actual renderer here)
        # module.render(renderer)
        
        # Update display
        pygame.display.flip()
        clock.tick(60)
    
    # Quit pygame
    pygame.quit() 