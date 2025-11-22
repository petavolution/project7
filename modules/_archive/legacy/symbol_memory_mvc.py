#!/usr/bin/env python3
"""
SymbolMemory Training Module with MVC Architecture

This module separates concerns using a Model-View-Controller pattern:
- Model: Core memory game logic 
- View: UI representation and component building
- Controller: User interaction and input handling

Key features:
1. Clean separation of game logic from presentation
2. Theme-aware styling
3. Responsive grid layout
4. Optimized state management
"""

import random
import time
import math
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional, Union, Set
import pygame

# Add the parent directory to sys.path for absolute imports when imported directly
if __name__ == "__main__" or not __package__:
    project_root = Path(__file__).parent.parent
    sys.path.insert(0, str(project_root))
    from MetaMindIQTrain.core.training_module import TrainingModule
    from MetaMindIQTrain.core.theme_manager import ThemeManager
    from MetaMindIQTrain.core.config import config
else:
    # Use relative imports when imported as a module
    from ..core.training_module import TrainingModule
    from ..core.theme_manager import ThemeManager
    from ..core.config import config


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
                
        elif modification_type == 4 and original_pattern["symbols"]:
            # Remove a symbol
            position_index = random.randint(0, len(original_pattern["positions"]) - 1)
            row, col = original_pattern["positions"][position_index]
            
            # Clear the position
            new_grid[row][col] = ""
        
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
            "user_answer": self.user_answer,
            "message": self.message,
            "timer_active": self.timer_active,
            "memorize_duration": self.memorize_duration,
            "hidden_duration": self.hidden_duration,
            "total_rounds": self.total_rounds,
            "correct_rounds": self.correct_rounds
        }


class SymbolMemoryView:
    """View component for SymbolMemory module - handles UI representation."""
    
    def __init__(self, model):
        """Initialize the view with reference to the model.
        
        Args:
            model: SymbolMemoryModel instance
        """
        self.model = model
        self.screen_width = 800  # Default width
        self.screen_height = 600  # Default height
        
        # Grid layout properties
        self.cell_size = 60  # Will be adjusted based on grid size
        self.grid_margin = 40
        self.grid_padding = 10
        
        # Button dimensions
        self.button_width = 120
        self.button_height = 50
        self.button_margin = 20
        
        # UI element references
        self.grid_rect = None  # Rectangle for the grid
        self.button_rects = {}  # Rectangles for buttons
    
    def set_dimensions(self, width, height):
        """Set the screen dimensions.
        
        Args:
            width: Screen width
            height: Screen height
        """
        self.screen_width = width
        self.screen_height = height
        self.calculate_layout()
    
    def calculate_layout(self):
        """Calculate layout based on screen dimensions and grid size."""
        # Get theme styling for symbol memory
        theme = config.UI_THEME
        symbol_layout = theme["layouts"]["symbol_memory"]
        
        # Get module-specific settings including scaling factor
        module_settings = config.MODULE_SETTINGS["symbol_memory"]
        visual_scale = module_settings.get("visual_scale", 1.0)  # Default to 1.0 if not specified
        
        # Calculate grid dimensions
        grid_size = self.model.current_grid_size
        
        # Get content area dimensions
        content_width = self.screen_width
        content_height = int(self.screen_height * 0.7)  # 70% of screen height
        content_y = int(self.screen_height * 0.15)  # 15% from top
        
        # Calculate grid margin and padding as percentage of screen
        self.grid_margin = int(min(content_width, content_height) * symbol_layout["grid_margin"] / 100)
        self.grid_padding = int(min(content_width, content_height) * symbol_layout["grid_padding"] / 100)
        
        # Calculate maximum grid size based on available space
        max_grid_width = content_width - (2 * self.grid_margin)
        max_grid_height = content_height - (2 * self.grid_margin)
        max_grid_size = min(max_grid_width, max_grid_height)
        
        # Apply visual scaling factor to the grid size
        max_grid_size = int(max_grid_size * visual_scale)
        
        # Calculate cell size including margin between cells
        cell_margin_percent = symbol_layout["cell_margin"]
        total_cell_margin = (grid_size - 1) * (max_grid_size * cell_margin_percent / 100)
        available_cell_space = max_grid_size - total_cell_margin
        self.cell_size = int(available_cell_space / grid_size)
        
        # Calculate total grid size including padding
        grid_width = grid_size * self.cell_size + total_cell_margin + 2 * self.grid_padding
        grid_height = grid_width  # Square grid
        
        # Center grid in content area
        grid_x = (content_width - grid_width) // 2
        grid_y = content_y + (content_height - grid_height) // 2
        
        self.grid_rect = (grid_x, grid_y, grid_width, grid_height)
        
        # Calculate button positions matching HTML layout
        self._calculate_button_positions()
    
    def _calculate_button_positions(self):
        """Calculate positions for buttons based on screen size and phase."""
        # Get module-specific settings including scaling factor
        module_settings = config.MODULE_SETTINGS["symbol_memory"]
        visual_scale = module_settings.get("visual_scale", 1.0)  # Default to 1.0 if not specified
        
        # Get footer area dimensions
        footer_y = int(self.screen_height * 0.85)  # 85% from top
        footer_height = int(self.screen_height * 0.15)  # 15% of screen height
        
        # Button dimensions based on percentage of screen
        self.button_width = int(self.screen_width * 0.15 * visual_scale)  # 15% of screen width * scale
        self.button_height = int(footer_height * 0.5 * visual_scale)  # 50% of footer height * scale
        self.button_margin = int(self.screen_width * 0.05)  # 5% of screen width (not scaled)
        
        # Calculate yes/no button positions (side by side in footer)
        yes_x = self.screen_width // 2 - self.button_width - self.button_margin // 2
        no_x = self.screen_width // 2 + self.button_margin // 2
        buttons_y = footer_y + (footer_height - self.button_height) // 2
        
        self.button_rects = {
            "yes": (yes_x, buttons_y, self.button_width, self.button_height),
            "no": (no_x, buttons_y, self.button_width, self.button_height),
            "continue": ((self.screen_width - self.button_width) // 2, buttons_y, self.button_width, self.button_height)
        }
    
    def get_cell_rect(self, row, col):
        """Get the rectangle for a grid cell.
        
        Args:
            row: Row index
            col: Column index
            
        Returns:
            Tuple of (x, y, width, height)
        """
        grid_x, grid_y, _, _ = self.grid_rect
        
        # Calculate cell position within grid
        cell_x = grid_x + self.grid_padding + col * self.cell_size
        cell_y = grid_y + self.grid_padding + row * self.cell_size
        
        return (cell_x, cell_y, self.cell_size, self.cell_size)
    
    def build_component_tree(self):
        """Build a component tree for rendering.
        
        Returns:
            Root component of the UI tree
        """
        # Root container
        root = {
            "type": "container",
            "id": "symbol_memory_root",
            "width": self.screen_width,
            "height": self.screen_height,
            "properties": {
                "style": {
                    "backgroundColor": ThemeManager.get_color("bg_color")
                }
            },
            "children": [
                # Header
                {
                    "type": "container",
                    "id": "header",
                    "x": 0,
                    "y": 0,
                    "width": self.screen_width,
                    "height": 50,
                    "properties": {
                        "style": {
                            "backgroundColor": ThemeManager.get_color("card_bg")
                        }
                    },
                    "children": [
                        # Title
                        {
                            "type": "text",
                            "id": "title",
                            "x": 20,
                            "y": 10,
                            "width": 300,
                            "height": 30,
                            "text": "Symbol Memory - Recall Challenge",
                            "properties": {
                                "style": {
                                    "color": ThemeManager.get_color("text_color"),
                                    "fontSize": 18
                                }
                            }
                        },
                        # Score
                        {
                            "type": "text",
                            "id": "score",
                            "x": self.screen_width - 150,
                            "y": 10,
                            "width": 130,
                            "height": 30,
                            "text": f"Score: {self.model.score}",
                            "properties": {
                                "style": {
                                    "color": ThemeManager.get_color("text_color"),
                                    "textAlign": "right",
                                    "fontSize": 18
                                }
                            }
                        }
                    ]
                },
                
                # Instructions/Message
                {
                    "type": "text",
                    "id": "instructions",
                    "x": 20,
                    "y": 60,
                    "width": self.screen_width - 40,
                    "height": 30,
                    "text": self.model.message,
                    "properties": {
                        "style": {
                            "color": ThemeManager.get_color("text_color"),
                            "textAlign": "center"
                        }
                    }
                },
                
                # Symbol grid
                {
                    "type": "container",
                    "id": "grid_container",
                    "x": self.grid_rect[0],
                    "y": self.grid_rect[1],
                    "width": self.grid_rect[2],
                    "height": self.grid_rect[3],
                    "properties": {
                        "style": {
                            "backgroundColor": ThemeManager.get_color("card_bg"),
                            "borderColor": ThemeManager.get_color("border_color"),
                            "borderWidth": 2,
                            "borderRadius": 5
                        }
                    },
                    "children": self._create_grid_components()
                },
                
                # Button container
                {
                    "type": "container",
                    "id": "button_container",
                    "x": 0,
                    "y": self.button_rects["yes"][1] - 10,
                    "width": self.screen_width,
                    "height": 70,
                    "children": self._create_button_components()
                }
            ]
        }
        
        return root
    
    def _create_grid_components(self):
        """Create component specs for grid cells.
        
        Returns:
            List of cell component specifications
        """
        cells = []
        
        # Get the current pattern based on phase
        pattern = None
        show_symbols = False
        
        if self.model.phase == self.model.PHASE_MEMORIZE:
            pattern = self.model.original_pattern
            show_symbols = True
        elif self.model.phase == self.model.PHASE_COMPARE:
            pattern = self.model.modified_pattern
            show_symbols = True
        
        if not pattern:
            return cells
            
        grid = pattern["grid"]
        grid_size = pattern["size"]
        
        # Calculate cell dimensions
        padding = self.grid_padding
        cell_size = self.cell_size
        
        for row in range(grid_size):
            for col in range(grid_size):
                cell_x = padding + col * cell_size
                cell_y = padding + row * cell_size
                
                symbol = grid[row][col] if show_symbols else ""
                
                # Cell background
                cell = {
                    "type": "container",
                    "id": f"cell_{row}_{col}",
                    "x": cell_x,
                    "y": cell_y,
                    "width": cell_size,
                    "height": cell_size,
                    "properties": {
                        "style": {
                            "backgroundColor": ThemeManager.get_color("card_hover"),
                            "borderColor": ThemeManager.get_color("border_color"),
                            "borderWidth": 1
                        }
                    }
                }
                
                cells.append(cell)
                
                # Symbol text (if visible)
                if show_symbols and symbol:
                    symbol_text = {
                        "type": "text",
                        "id": f"symbol_{row}_{col}",
                        "x": cell_x,
                        "y": cell_y,
                        "width": cell_size,
                        "height": cell_size,
                        "text": symbol,
                        "properties": {
                            "style": {
                                "color": self.get_symbol_color(symbol),
                                "fontSize": int(cell_size * 0.6),
                                "textAlign": "center"
                            }
                        }
                    }
                    
                    cells.append(symbol_text)
        
        return cells
    
    def _create_button_components(self):
        """Create component specs for buttons.
        
        Returns:
            List of button component specifications
        """
        buttons = []
        
        if self.model.phase == self.model.PHASE_ANSWER:
            # Yes button
            yes_rect = self.button_rects["yes"]
            yes_button = {
                "type": "button",
                "id": "yes_button",
                "x": yes_rect[0],
                "y": yes_rect[1],
                "width": yes_rect[2],
                "height": yes_rect[3],
                "text": "Yes",
                "properties": {
                    "style": {
                        "backgroundColor": ThemeManager.get_color("primary_color"),
                        "color": ThemeManager.get_color("text_color"),
                        "borderRadius": 5
                    }
                }
            }
            buttons.append(yes_button)
            
            # No button
            no_rect = self.button_rects["no"]
            no_button = {
                "type": "button",
                "id": "no_button",
                "x": no_rect[0],
                "y": no_rect[1],
                "width": no_rect[2],
                "height": no_rect[3],
                "text": "No",
                "properties": {
                    "style": {
                        "backgroundColor": ThemeManager.get_color("secondary_color"),
                        "color": ThemeManager.get_color("text_color"),
                        "borderRadius": 5
                    }
                }
            }
            buttons.append(no_button)
        
        elif self.model.phase == self.model.PHASE_FEEDBACK:
            # Continue button
            continue_rect = self.button_rects["continue"]
            continue_button = {
                "type": "button",
                "id": "continue_button",
                "x": continue_rect[0],
                "y": continue_rect[1],
                "width": continue_rect[2],
                "height": continue_rect[3],
                "text": "Continue",
                "properties": {
                    "style": {
                        "backgroundColor": ThemeManager.get_color("primary_color"),
                        "color": ThemeManager.get_color("text_color"),
                        "borderRadius": 5
                    }
                }
            }
            buttons.append(continue_button)
        
        return buttons

    def render_grid(self, renderer):
        """Render the symbol grid using enhanced styling to match HTML/CSS.
        
        Args:
            renderer: UIRenderer instance
        """
        # Get theme styling
        theme = config.UI_THEME
        
        # Get module-specific settings including scaling factor
        module_settings = config.MODULE_SETTINGS["symbol_memory"]
        visual_scale = module_settings.get("visual_scale", 1.0)  # Default to 1.0 if not specified
        preserve_font_size = module_settings.get("preserve_font_size", True)
        
        # Get grid dimensions
        grid_x, grid_y, grid_width, grid_height = self.grid_rect
        
        # Draw grid background
        bg_color = theme["colors"]["bg_dark"]
        pygame.draw.rect(
            renderer.screen, 
            bg_color, 
            self.grid_rect, 
            border_radius=10
        )
        
        # Get the current pattern based on phase
        pattern = None
        show_symbols = False
        
        if self.model.phase == self.model.PHASE_MEMORIZE:
            pattern = self.model.original_pattern
            show_symbols = True
            phase_text = "Memorize the pattern"
            phase_type = "memorize"
        elif self.model.phase == self.model.PHASE_COMPARE:
            pattern = self.model.modified_pattern
            show_symbols = True
            phase_text = "Was the pattern changed?"
            phase_type = "recall"
        elif self.model.phase == self.model.PHASE_ANSWER:
            pattern = self.model.modified_pattern
            show_symbols = True
            phase_text = "Was a symbol changed?"
            phase_type = "recall"
        elif self.model.phase == self.model.PHASE_FEEDBACK:
            pattern = self.model.modified_pattern
            show_symbols = True
            
            if self.model.was_modified:
                correct_answer = self.model.user_answer
            else:
                correct_answer = not self.model.user_answer
                
            if correct_answer:
                phase_text = "Correct!"
                phase_type = "feedback_correct"
            else:
                phase_text = "Incorrect!"
                phase_type = "feedback_incorrect"
        else:
            # Default for hidden phase
            pattern = self.model.original_pattern
            show_symbols = False
            phase_text = "Recall the pattern"
            phase_type = "recall"
        
        # Render phase indicator
        renderer.render_phase_indicator(phase_text, phase_type)
        
        if not pattern:
            return
            
        grid = pattern["grid"]
        grid_size = pattern["size"]
        
        # Calculate cell dimensions
        grid_inner_width = grid_width - 2 * self.grid_padding
        cell_margin = grid_inner_width * theme["layouts"]["symbol_memory"]["cell_margin"] / 100 / grid_size
        cell_size = (grid_inner_width - cell_margin * (grid_size - 1)) / grid_size
        
        # Render grid cells
        for row in range(grid_size):
            for col in range(grid_size):
                # Calculate cell position
                cell_x = grid_x + self.grid_padding + col * (cell_size + cell_margin)
                cell_y = grid_y + self.grid_padding + row * (cell_size + cell_margin)
                
                # Get symbol for this cell
                symbol = ""
                if row < len(grid) and col < len(grid[row]):
                    symbol = grid[row][col] if show_symbols else ""
                
                # Determine if cell is highlighted (for modified cell highlighting)
                is_highlighted = False
                if self.model.phase == self.model.PHASE_FEEDBACK and self.model.was_modified:
                    if self.model.modified_position:
                        mod_row, mod_col = self.model.modified_position
                        is_highlighted = (row == mod_row and col == mod_col)
                
                # Get symbol color if available
                symbol_color = None
                if symbol and hasattr(self.model, 'get_symbol_color'):
                    symbol_color = self.model.get_symbol_color(symbol)
                
                # Render cell with styled appearance
                cell_rect = (cell_x, cell_y, cell_size, cell_size)
                renderer.render_styled_grid_cell(
                    cell_rect, 
                    theme["colors"]["bg_light"], 
                    symbol if show_symbols else "", 
                    is_highlighted,
                    symbol_color=symbol_color
                )
    
    def render_buttons(self, renderer):
        """Render the interaction buttons using enhanced styling.
        
        Args:
            renderer: UIRenderer instance
        """
        # Get current phase
        phase = self.model.phase
        
        # Render the appropriate buttons based on phase
        if phase == self.model.PHASE_ANSWER:
            # Render yes/no buttons
            yes_rect = self.button_rects["yes"]
            no_rect = self.button_rects["no"]
            
            # Check for mouse hover
            mouse_pos = pygame.mouse.get_pos()
            is_yes_hover = pygame.Rect(*yes_rect).collidepoint(mouse_pos)
            is_no_hover = pygame.Rect(*no_rect).collidepoint(mouse_pos)
            
            # Render styled buttons
            renderer.render_styled_button("Yes", yes_rect, "yes", is_highlighted=is_yes_hover)
            renderer.render_styled_button("No", no_rect, "no", is_highlighted=is_no_hover)
            
        elif phase == self.model.PHASE_FEEDBACK:
            # Render continue button
            continue_rect = self.button_rects["continue"]
            
            # Check for mouse hover
            mouse_pos = pygame.mouse.get_pos()
            is_continue_hover = pygame.Rect(*continue_rect).collidepoint(mouse_pos)
            
            # Render styled button
            renderer.render_styled_button("Continue", continue_rect, "continue", is_highlighted=is_continue_hover)


class SymbolMemoryController:
    """Controller component for SymbolMemory module - handles user interaction."""
    
    def __init__(self, model, view):
        """Initialize the controller with references to model and view.
        
        Args:
            model: SymbolMemoryModel instance
            view: SymbolMemoryView instance
        """
        self.model = model
        self.view = view
    
    def handle_click(self, x, y):
        """Handle mouse click event.
        
        Args:
            x: X coordinate of click
            y: Y coordinate of click
            
        Returns:
            Dictionary with result and updated state
        """
        if self.model.phase == self.model.PHASE_ANSWER:
            # Check for clicks on YES button
            yes_rect = self.view.button_rects["yes"]
            if self._is_point_in_rect(x, y, yes_rect):
                is_correct, score_change = self.model.process_answer(True)
                return {"result": "answer_processed", "correct": is_correct, "score_change": score_change, "state": self.model.get_state()}
            
            # Check for clicks on NO button
            no_rect = self.view.button_rects["no"]
            if self._is_point_in_rect(x, y, no_rect):
                is_correct, score_change = self.model.process_answer(False)
                return {"result": "answer_processed", "correct": is_correct, "score_change": score_change, "state": self.model.get_state()}
            
        elif self.model.phase == self.model.PHASE_FEEDBACK:
            # Check for clicks on CONTINUE button
            continue_rect = self.view.button_rects["continue"]
            if self._is_point_in_rect(x, y, continue_rect):
                self.model.start_next_round()
                return {"result": "next_round", "state": self.model.get_state()}
        
        # Default: no action
        return {"result": "no_action", "state": self.model.get_state()}
    
    def update(self, dt, current_time):
        """Update controller state.
        
        Args:
            dt: Time delta in seconds
            current_time: Current time in seconds
            
        Returns:
            True if state changed, False otherwise
        """
        # Check for phase transitions
        return self.model.update_phase(current_time)
    
    def _is_point_in_rect(self, x, y, rect):
        """Check if a point is inside a rectangle.
        
        Args:
            x: X coordinate of point
            y: Y coordinate of point
            rect: Tuple of (rect_x, rect_y, rect_width, rect_height)
            
        Returns:
            True if the point is inside the rectangle
        """
        rect_x, rect_y, rect_width, rect_height = rect
        return (rect_x <= x <= rect_x + rect_width and
                rect_y <= y <= rect_y + rect_height)


class SymbolMemory(TrainingModule):
    """SymbolMemory training module with MVC architecture."""
    
    def __init__(self, difficulty=1):
        """Initialize the module.
        
        Args:
            difficulty: Initial difficulty level
        """
        super().__init__()
        
        # Module metadata
        self.name = "symbol_memory"
        self.display_name = "Symbol Memory"
        self.description = "Memorize symbols in a grid and identify changes"
        self.category = "Memory"
        
        # Screen dimensions from parent class
        self.screen_width = self.__class__.SCREEN_WIDTH
        self.screen_height = self.__class__.SCREEN_HEIGHT
        
        # Set up MVC components
        self.model = SymbolMemoryModel(difficulty)
        self.view = SymbolMemoryView(self.model)
        self.controller = SymbolMemoryController(self.model, self.view)
        
        # Configure view
        self.view.set_dimensions(self.screen_width, self.screen_height)
        
        # Track properties for efficient delta generation
        self._tracked_properties = self._tracked_properties.union({
            'phase', 'game_state', 'current_grid_size', 'original_pattern',
            'modified_pattern', 'was_modified', 'user_answer', 'timer_active', 
            'memorize_duration', 'hidden_duration', 'user_answer', 'round_score'
        })
    
    @staticmethod
    def get_name():
        """Get the name of the module."""
        return "Symbol Memory"
    
    @staticmethod
    def get_description():
        """Get the description of the module."""
        return "Memorize symbols in a grid and identify changes"
    
    def handle_click(self, x, y):
        """Handle mouse click events.
        
        Args:
            x: X coordinate of click
            y: Y coordinate of click
            
        Returns:
            Result dictionary
        """
        return self.controller.handle_click(x, y)
    
    def update(self, dt):
        """Update module state based on elapsed time.
        
        Args:
            dt: Time delta since last update in seconds
        """
        super().update(dt)
        
        # Update controller with current time
        self.controller.update(dt, time.time())
    
    def get_state(self):
        """Get the current module state.
        
        Returns:
            Dictionary with state information
        """
        # Start with base state
        state = super().get_state()
        
        # Add model state
        model_state = self.model.get_state()
        state.update(model_state)
        
        # Add module-specific properties
        state.update({
            "name": self.name,
            "display_name": self.display_name,
            "description": self.description,
            "category": self.category
        })
        
        return state
    
    def process_input(self, input_data):
        """Process input data.
        
        Args:
            input_data: Input data dictionary
            
        Returns:
            Result dictionary
        """
        action = input_data.get("action", "")
        
        if action == "answer_yes":
            is_correct, score_change = self.model.process_answer(True)
            return {"result": "answer_processed", "correct": is_correct, "score_change": score_change, "state": self.get_state()}
        
        elif action == "answer_no":
            is_correct, score_change = self.model.process_answer(False)
            return {"result": "answer_processed", "correct": is_correct, "score_change": score_change, "state": self.get_state()}
        
        elif action == "next_round":
            self.model.start_next_round()
            return {"result": "next_round", "state": self.get_state()}
        
        # Default: no action
        return {"result": "no_action", "state": self.get_state()}
    
    def build_ui(self):
        """Build the UI component tree.
        
        This is used by modern renderers that support component-based rendering.
        
        Returns:
            UI component tree specification
        """
        return self.view.build_component_tree() 