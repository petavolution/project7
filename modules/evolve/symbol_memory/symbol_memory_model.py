#!/usr/bin/env python3
"""
Symbol Memory Model Component

This module handles the core game logic for the Symbol Memory training module:
- Symbol and grid generation
- Game state management
- Phase transitions
- Score calculation
- Difficulty progression

The model is responsible for all data and business logic, independent of the UI.
"""

import random
import time
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional, Union, Set

# Add the parent directory to sys.path for absolute imports when imported directly
if __name__ == "__main__" or not __package__:
    project_root = Path(__file__).parent.parent.parent.parent
    sys.path.insert(0, str(project_root))


class SymbolMemoryModel:
    """Model component for SymbolMemory module - handles core game logic."""
    
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
        """Initialize the model with game state and business logic.
        
        Args:
            difficulty: Initial difficulty level (1-10)
        """
        # Game settings
        self.difficulty = max(1, min(10, difficulty))  # Clamp difficulty between 1-10
        self.level = self.difficulty
        self.current_grid_size = self._calculate_grid_size()
        self.score = 0
        
        # Game state
        self.phase = self.PHASE_MEMORIZE
        self.game_state = self.STATE_ACTIVE
        self.original_pattern = None
        self.modified_pattern = None
        self.was_modified = False
        self.modified_position = None  # Track the position that was modified
        self.user_answer = None
        self.timer_active = True
        self.round_score = 0
        self.total_rounds = 0
        self.correct_rounds = 0
        self.message = "Memorize the pattern"
        
        # Timing settings (in seconds)
        self.phase_start_time = time.time()
        self.memorize_duration = self._calculate_memorize_duration()
        self.hidden_duration = 1.0  # Fixed duration for hidden phase
        
        # Bright colors for multi-modal cognitive enhancement
        self.bright_colors = [
            (255, 0, 0),      # Bright Red
            (0, 255, 0),      # Bright Green
            (0, 0, 255),      # Bright Blue
            (255, 255, 0),    # Yellow
            (255, 0, 255),    # Magenta
            (0, 255, 255),    # Cyan
            (255, 128, 0),    # Orange
            (128, 0, 255),    # Purple
            (255, 0, 128),    # Pink
            (0, 255, 128),    # Mint
            (128, 255, 0),    # Lime
            (0, 128, 255)     # Sky Blue
        ]
        
        # Dictionary to store symbol colors
        self.symbol_colors = {}
        self.assign_symbol_colors()
        
        # Initialize first round
        self._generate_pattern()
    
    def assign_symbol_colors(self):
        """Assign a random bright color to each symbol for enhanced perception."""
        # Shuffle the bright colors
        available_colors = self.bright_colors.copy()
        random.shuffle(available_colors)
        
        # Assign a color to each symbol
        for i, symbol in enumerate(self.SYMBOLS):
            color_index = i % len(available_colors)
            self.symbol_colors[symbol] = available_colors[color_index]
    
    def get_symbol_color(self, symbol):
        """Get the color assigned to a symbol."""
        return self.symbol_colors.get(symbol, (255, 255, 255))  # Default to white if not found
    
    def _generate_pattern(self):
        """Generate a new random pattern for the current grid size."""
        grid_size = self.current_grid_size
        
        # Calculate the number of symbols to place based on difficulty
        # Higher levels have more symbols
        max_symbols = grid_size * grid_size
        num_symbols = min(max_symbols, max(3, int(max_symbols * (0.3 + 0.05 * self.difficulty))))
        
        # Create empty grid
        empty_grid = [["" for _ in range(grid_size)] for _ in range(grid_size)]
        
        # Place symbols randomly
        symbols = []
        positions = []
        
        for _ in range(num_symbols):
            # Select random symbol
            symbol = random.choice(self.SYMBOLS)
            
            # Find an empty position
            while True:
                row = random.randint(0, grid_size - 1)
                col = random.randint(0, grid_size - 1)
                
                if empty_grid[row][col] == "":
                    empty_grid[row][col] = symbol
                    symbols.append(symbol)
                    positions.append((row, col))
                    break
        
        self.original_pattern = {
            "grid": empty_grid,
            "symbols": symbols,
            "positions": positions,
            "size": grid_size
        }
        
        # Create a modified pattern (50% chance of modification)
        self.modified_pattern = self._create_modified_pattern(self.original_pattern)
        self.was_modified = (self.original_pattern["grid"] != self.modified_pattern["grid"])
    
    def _create_modified_pattern(self, original_pattern):
        """Create a potentially modified version of the original pattern.
        
        Args:
            original_pattern: Original pattern dictionary
            
        Returns:
            Modified pattern dictionary
        """
        grid_size = original_pattern["size"]
        original_grid = original_pattern["grid"]
        
        # Deep copy the original grid
        new_grid = [row[:] for row in original_grid]
        
        # Decide if we should modify the pattern (50% chance)
        if random.random() < 0.5:
            # No modification - return a copy of the original
            return {
                "grid": new_grid,
                "symbols": original_pattern["symbols"][:],
                "positions": original_pattern["positions"][:],
                "size": grid_size
            }
        
        # Modification types:
        # 1. Change a symbol
        # 2. Move a symbol to a new position
        # 3. Add a new symbol
        # 4. Remove a symbol
        
        modification_type = random.randint(1, 4)
        self.modified_position = None  # Reset the modified position
        
        if modification_type == 1 and original_pattern["symbols"]:
            # Change a symbol
            position_index = random.randint(0, len(original_pattern["positions"]) - 1)
            row, col = original_pattern["positions"][position_index]
            
            # Select a new different symbol
            current_symbol = original_grid[row][col]
            available_symbols = [s for s in self.SYMBOLS if s != current_symbol]
            new_symbol = random.choice(available_symbols)
            
            # Update the grid
            new_grid[row][col] = new_symbol
            self.modified_position = (row, col)
            
        elif modification_type == 2 and original_pattern["symbols"]:
            # Move a symbol to a new position
            position_index = random.randint(0, len(original_pattern["positions"]) - 1)
            row, col = original_pattern["positions"][position_index]
            symbol = original_grid[row][col]
            
            # Find an empty position
            empty_positions = []
            for r in range(grid_size):
                for c in range(grid_size):
                    if original_grid[r][c] == "" and (r, c) != (row, col):
                        empty_positions.append((r, c))
            
            if empty_positions:
                # Clear the old position
                new_grid[row][col] = ""
                self.modified_position = (row, col)
                
                # Place at new position
                new_row, new_col = random.choice(empty_positions)
                new_grid[new_row][new_col] = symbol
                
        elif modification_type == 3:
            # Add a new symbol (if there's space)
            empty_positions = []
            for r in range(grid_size):
                for c in range(grid_size):
                    if original_grid[r][c] == "":
                        empty_positions.append((r, c))
            
            if empty_positions:
                new_row, new_col = random.choice(empty_positions)
                new_symbol = random.choice(self.SYMBOLS)
                new_grid[new_row][new_col] = new_symbol
                self.modified_position = (new_row, new_col)
                
        elif modification_type == 4 and original_pattern["symbols"]:
            # Remove a symbol
            position_index = random.randint(0, len(original_pattern["positions"]) - 1)
            row, col = original_pattern["positions"][position_index]
            
            # Clear the position
            new_grid[row][col] = ""
            self.modified_position = (row, col)
        
        # Rebuild symbols and positions lists
        symbols = []
        positions = []
        
        for r in range(grid_size):
            for c in range(grid_size):
                if new_grid[r][c] != "":
                    symbols.append(new_grid[r][c])
                    positions.append((r, c))
        
        return {
            "grid": new_grid,
            "symbols": symbols,
            "positions": positions,
            "size": grid_size
        }
    
    def process_answer(self, user_answer):
        """Process the user's answer.
        
        Args:
            user_answer: True if user thinks pattern was modified, False otherwise
            
        Returns:
            Tuple of (is_correct, score_change)
        """
        self.user_answer = user_answer
        
        # Check if the answer is correct
        is_correct = (user_answer == self.was_modified)
        
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
        
        # Check if level should increase
        if self.correct_rounds >= 3 and self.correct_rounds % 3 == 0:
            self._increase_level()
        
        return (is_correct, self.round_score)
    
    def start_next_round(self):
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
    
    def update_phase(self, current_time):
        """Update the game phase based on elapsed time.
        
        Args:
            current_time: Current time in seconds
            
        Returns:
            True if the phase changed, False otherwise
        """
        if not self.timer_active:
            return False
            
        elapsed_since_phase = current_time - self.phase_start_time
        phase_changed = False
        
        if self.phase == self.PHASE_MEMORIZE and elapsed_since_phase >= self.memorize_duration:
            self.phase = self.PHASE_HIDDEN
            self.phase_start_time = current_time
            self.message = "Remembering..."
            phase_changed = True
        
        elif self.phase == self.PHASE_HIDDEN and elapsed_since_phase >= self.hidden_duration:
            self.phase = self.PHASE_COMPARE
            self.phase_start_time = current_time
            self.message = "Compare with the original pattern"
            phase_changed = True
        
        elif self.phase == self.PHASE_COMPARE and elapsed_since_phase >= self.memorize_duration:
            self.phase = self.PHASE_ANSWER
            self.phase_start_time = current_time
            self.message = "Was the pattern modified?"
            phase_changed = True
            
        return phase_changed
    
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
        # Base duration is longer for larger grids
        base_duration = 1.0 + (self.current_grid_size * 0.5)
        
        # Reduce time as level increases (but keep a minimum)
        level_factor = max(0.6, 1.0 - (self.level * 0.04))
        
        return base_duration * level_factor
    
    def get_state(self):
        """Get the current model state.
        
        Returns:
            Dictionary with current game state
        """
        return {
            "phase": self.phase,
            "game_state": self.game_state,
            "level": self.level,
            "difficulty": self.difficulty,
            "score": self.score,
            "round_score": self.round_score,
            "current_grid_size": self.current_grid_size,
            "original_pattern": self.original_pattern,
            "modified_pattern": self.modified_pattern,
            "was_modified": self.was_modified,
            "modified_position": self.modified_position,
            "user_answer": self.user_answer,
            "message": self.message,
            "timer_active": self.timer_active,
            "memorize_duration": self.memorize_duration,
            "hidden_duration": self.hidden_duration,
            "total_rounds": self.total_rounds,
            "correct_rounds": self.correct_rounds
        } 