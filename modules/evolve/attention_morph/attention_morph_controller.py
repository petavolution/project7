#!/usr/bin/env python3
"""
Attention Morph Controller - User interaction handler for the Attention Morph module

This module implements the Controller component in the MVC architecture for the
Attention Morph cognitive training exercise. It handles:
- User input processing
- Game state management and transitions
- Performance tracking and metrics
- Difficulty adaptation
"""

import pygame
import time
import sys
import random
from pathlib import Path
from typing import Tuple, Dict, List, Optional, Any, Union, Set

# Add the parent directory to sys.path for absolute imports
if __name__ == "__main__" or not __package__:
    project_root = Path(__file__).parent.parent.parent
    sys.path.insert(0, str(project_root))
    from MetaMindIQTrain.core.theme_manager import ThemeManager
else:
    # Use relative imports when imported as a module
    from ...core.theme_manager import ThemeManager

# Import local module components
from .attention_morph_model import AttentionMorphModel
from .attention_morph_view import AttentionMorphView
from .adaptive_difficulty_engine import AdaptiveDifficultyEngine

class AttentionMorphController:
    """Controller for the Attention Morph module handling user input and game flow.
    
    This class manages user interactions, game state transitions, and performance
    tracking for the Attention Morph cognitive training exercise. It implements
    the controller component of the MVC pattern.
    """

    # Game states
    STATE_INTRO = 0      # Introduction/instructions
    STATE_PLAYING = 1    # Active gameplay
    STATE_GAME_OVER = 2  # Game completed
    
    # Performance constants
    MIN_REACTION_TIME = 0.2  # Minimum valid reaction time in seconds
    MAX_REACTION_TIME = 5.0  # Maximum valid reaction time in seconds
    SESSION_DURATION = 60.0  # Default game session duration in seconds
    
    def __init__(self, model: AttentionMorphModel, view: AttentionMorphView, adaptive_engine: AdaptiveDifficultyEngine):
        """Initialize controller with model, view, and adaptive difficulty engine.
        
        Args:
            model: The AttentionMorphModel containing game logic
            view: The AttentionMorphView for rendering
            adaptive_engine: The AdaptiveDifficultyEngine for dynamic difficulty
        """
        # Core components
        self.model = model
        self.view = view
        self.adaptive_engine = adaptive_engine
        
        # Game state
        self.state = self.STATE_INTRO
        self.game_timer = self.SESSION_DURATION  # 60 seconds for a game round
        self.last_time = time.time()
        self.last_transform_time = 0
        self.transform_interval = 1.0  # Time between random transformations
        
        # Selection tracking
        self.last_selection_time = 0
        self.selected_cells = set()
        
        # Performance metrics
        self.performance_metrics = {
            "correct_selections": 0,
            "incorrect_selections": 0,
            "reaction_times": [],
            "total_targets_found": 0,
            "targets_missed": 0,
            "false_positives": 0,
            "accuracy": 0.0,
            "average_reaction_time": 0.0,
            "targets_per_minute": 0.0
        }
        
        # Theme
        self.theme = ThemeManager.get_theme()

    def handle_user_input(self, event: pygame.event.Event) -> None:
        """Process user input events.
        
        Args:
            event: Pygame event to handle
        """
        # Handle different event types
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Mouse click handling
            if event.button == 1:  # Left click
                if self.state == self.STATE_INTRO:
                    # Transition from intro to gameplay
                    self.state = self.STATE_PLAYING
                    self._reset_game()
                elif self.state == self.STATE_GAME_OVER:
                    # Restart game
                    self.state = self.STATE_PLAYING
                    self._reset_game()
                elif self.state == self.STATE_PLAYING:
                    # Process gameplay selection
                    pos = event.pos
                    grid_coords = self._pixel_to_grid_coords(pos)
                    if grid_coords:
                        row, col = grid_coords
                        # Track reaction time
                        current_time = time.time()
                        if self.last_selection_time == 0:
                            self.last_selection_time = current_time
                        reaction_time = current_time - self.last_selection_time
                        self.last_selection_time = current_time
                        
                        # Process the selection
                        self._process_selection(row, col, reaction_time)
        
        elif event.type == pygame.KEYDOWN:
            # Keyboard input handling
            if event.key == pygame.K_ESCAPE:
                # ESC key to exit or reset
                if self.state == self.STATE_PLAYING:
                    self.state = self.STATE_GAME_OVER
                elif self.state == self.STATE_GAME_OVER:
                    self.state = self.STATE_INTRO
            elif event.key == pygame.K_SPACE:
                # Space to start or restart
                if self.state == self.STATE_INTRO:
                    self.state = self.STATE_PLAYING
                    self._reset_game()
                elif self.state == self.STATE_GAME_OVER:
                    self.state = self.STATE_PLAYING
                    self._reset_game()

    def _pixel_to_grid_coords(self, pixel_pos: Tuple[int, int]) -> Optional[Tuple[int, int]]:
        """Convert screen coordinates to grid coordinates.
        
        Args:
            pixel_pos: (x, y) screen position
            
        Returns:
            Tuple of (row, col) if click is within grid, None otherwise
        """
        # Extract grid bounds from view
        if not hasattr(self.view, 'grid_bounds'):
            return None
            
        grid_x, grid_y, grid_right, grid_bottom = self.view.grid_bounds
        x, y = pixel_pos
        
        # Check if click is outside grid bounds
        if x < grid_x or x >= grid_right or y < grid_y or y >= grid_bottom:
            return None
        
        # Calculate grid cell size
        rows = len(self.model.grid)
        cols = len(self.model.grid[0]) if rows > 0 else 0
        
        if rows == 0 or cols == 0:
            return None
            
        # View's cell size may be different from model's grid dimensions
        cell_width = (grid_right - grid_x) / cols
        cell_height = (grid_bottom - grid_y) / rows
        
        # Calculate grid coordinates
        col = int((x - grid_x) / cell_width)
        row = int((y - grid_y) / cell_height)
        
        # Ensure within bounds
        if 0 <= row < rows and 0 <= col < cols:
            return (row, col)
            
        return None

    def _process_selection(self, row: int, col: int, reaction_time: float = 0.0) -> None:
        """Process user selection of a grid cell.
        
        Args:
            row: Selected row
            col: Selected column
            reaction_time: Time taken to make the selection
        """
        # Check if this cell has already been selected
        if (row, col) in self.selected_cells:
            # Already selected, provide feedback
            self.view.provide_visual_feedback((False, "Already selected"))
            return
            
        # Add to selected cells
        self.selected_cells.add((row, col))
        
        # Check if selection is correct (target)
        is_correct = self.model.process_selection(row, col)
        
        if is_correct:
            # Update performance metrics
            self.performance_metrics["correct_selections"] += 1
            self.performance_metrics["total_targets_found"] += 1
            
            # Record valid reaction time
            if self.MIN_REACTION_TIME <= reaction_time <= self.MAX_REACTION_TIME:
                self.performance_metrics["reaction_times"].append(reaction_time)
            
            # Update score
            # Score is based on reaction time: faster = higher score
            max_points = 100 * self.model.difficulty_level
            if reaction_time > 0:
                speed_factor = max(0.1, min(1.0, 1.0 / reaction_time))
                points = int(max_points * speed_factor)
                self.model.score += points
            else:
                self.model.score += int(max_points * 0.5)  # Default points if no reaction time
                
            # Provide feedback
            self.view.provide_visual_feedback((True, f"+{points} points"))
        else:
            # Update performance metrics for incorrect selection
            self.performance_metrics["incorrect_selections"] += 1
            self.performance_metrics["false_positives"] += 1
            
            # Penalty for incorrect selection
            penalty = 50 * self.model.difficulty_level
            self.model.score = max(0, self.model.score - penalty)
            
            # Provide feedback
            self.view.provide_visual_feedback((False, f"-{penalty} points"))

    def _reset_game(self) -> None:
        """Reset game state for a new session."""
        # Reset model
        self.model.reset()
        
        # Regenerate grid with appropriate difficulty
        self.model.generate_shape_grid(5, 5, self.model.difficulty_level)
        self.model.define_transformation_rules()
        
        # Set number of targets based on difficulty
        num_targets = max(3, min(10, 3 + self.model.difficulty_level))
        self.model.place_target_stimuli(num_targets)
        
        # Reset timer and state
        self.game_timer = self.SESSION_DURATION
        self.last_time = time.time()
        self.last_transform_time = 0
        self.last_selection_time = 0
        self.selected_cells.clear()
        
        # Reset performance metrics
        self.performance_metrics = {
            "correct_selections": 0,
            "incorrect_selections": 0,
            "reaction_times": [],
            "total_targets_found": 0,
            "targets_missed": 0,
            "false_positives": 0,
            "accuracy": 0.0,
            "average_reaction_time": 0.0,
            "targets_per_minute": 0.0
        }

    def track_performance_metrics(self) -> None:
        """Update and calculate performance metrics."""
        # Update game timer
        current_time = time.time()
        elapsed = current_time - self.last_time
        
        if self.state == self.STATE_PLAYING:
            self.game_timer -= elapsed
            
            # Check for game over condition
            if self.game_timer <= 0:
                self.game_timer = 0
                self.state = self.STATE_GAME_OVER
                
                # Calculate final targets missed
                total_targets = self.model.count_targets()
                self.performance_metrics["targets_missed"] = total_targets - self.performance_metrics["total_targets_found"]
        
        self.last_time = current_time
        
        # Calculate derived metrics
        total_selections = self.performance_metrics["correct_selections"] + self.performance_metrics["incorrect_selections"]
        if total_selections > 0:
            self.performance_metrics["accuracy"] = self.performance_metrics["correct_selections"] / total_selections
        
        # Calculate average reaction time
        if self.performance_metrics["reaction_times"]:
            self.performance_metrics["average_reaction_time"] = sum(self.performance_metrics["reaction_times"]) / len(self.performance_metrics["reaction_times"])
        
        # Calculate targets per minute (scaled to a full minute)
        elapsed_minutes = (self.SESSION_DURATION - self.game_timer) / 60.0
        if elapsed_minutes > 0:
            self.performance_metrics["targets_per_minute"] = self.performance_metrics["total_targets_found"] / elapsed_minutes

    def update_grid_state(self) -> None:
        """Update the grid state with transformations and animations."""
        if self.state != self.STATE_PLAYING:
            return
            
        # Update model state
        dt = time.time() - self.last_time
        self.model.update_grid(dt)
        
        # Periodically trigger random transformations
        current_time = time.time()
        if current_time - self.last_transform_time > self.transform_interval:
            # Number of transformations scales with difficulty
            transform_count = max(1, min(5, self.model.difficulty_level // 2))
            self.model.start_random_transformations(transform_count)
            
            # Adapt transform interval based on difficulty
            self.transform_interval = max(0.5, 2.0 - (self.model.difficulty_level * 0.1))
            self.last_transform_time = current_time

    def trigger_visual_feedback(self, selection: Tuple[bool, str]) -> None:
        """Trigger visual feedback for a selection.
        
        Args:
            selection: Tuple of (is_correct, message)
        """
        self.view.provide_visual_feedback(selection)

    def get_game_data_for_view(self) -> Dict[str, Any]:
        """Get current game data for the view.
        
        Returns:
            Dictionary with current game state data
        """
        return {
            "grid": self.model.grid,
            "score": self.model.score,
            "level": self.model.difficulty_level,
            "time_left": max(0, self.game_timer),
            "targets_found": self.performance_metrics["total_targets_found"],
            "targets_missed": self.performance_metrics["targets_missed"],
            "accuracy": self.performance_metrics["accuracy"] * 100,  # as percentage
            "average_reaction_time": self.performance_metrics["average_reaction_time"]
        } 