#!/usr/bin/env python3
"""
Unified Symbol Memory Module

An optimized version of the Symbol Memory module using the unified component system.
This module tests memory by displaying symbols in a grid which the player must remember
and reproduce.

Optimizations:
1. Uses component memoization and caching
2. Implements declarative UI with automatic diffing
3. Uses adaptive grid sizing for different screen resolutions
4. Efficiently updates only changed components
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

# Default symbols for the memory game
DEFAULT_SYMBOLS = [
    "★", "♦", "♥", "♠", "♣", "▲", "●", "■",
    "◆", "▼", "△", "▽", "□", "◇", "○", "⬟",
    "⬤", "⬢", "⬡", "⬕", "⬖", "⬗", "⬘", "⬙"
]

# Module states
STATE_INTRO = "intro"
STATE_MEMORIZE = "memorize"
STATE_RECALL = "recall"
STATE_RESULT = "result"


class UnifiedSymbolMemory:
    """Symbol memory training module using the unified component system."""
    
    def __init__(self, renderer=None):
        """Initialize the symbol memory module.
        
        Args:
            renderer: Optional UnifiedRenderer instance for advanced visual effects
        """
        # Configuration
        self.grid_size = 3  # Default grid size (3x3)
        self.symbols = DEFAULT_SYMBOLS.copy()
        self.memorize_time = 5.0  # Time to memorize in seconds
        self.recall_time = 20.0  # Time to recall in seconds
        self.level = 1
        
        # State
        self.state = STATE_INTRO
        self.game_grid = []  # Symbols to memorize
        self.player_grid = []  # Player's selections
        self.selected_symbol_index = 0  # Currently selected symbol
        self.start_time = 0  # Timer start
        self.elapsed_time = 0  # Elapsed time
        self.score = 0  # Current score
        self.high_score = 0  # High score
        
        # UI components
        self.ui = None
        self.screen_width = 1440  # Default width
        self.screen_height = 1024  # Default height
        
        # Store renderer reference for transitions
        self.renderer = renderer
        
        # Optimization
        self.needs_redraw = True  # Force full redraw on first frame
        self.last_state = None  # Previous state for change detection
    
    def initialize(self):
        """Initialize the module."""
        logger.info("Initializing Symbol Memory module")
        # Reset state
        self.state = STATE_INTRO
        self.score = 0
        self.level = 1
        self.grid_size = 3
        self.game_grid = []
        self.player_grid = []
    
    def shutdown(self):
        """Clean up resources."""
        logger.info("Shutting down Symbol Memory module")
    
    def update(self, dt=None):
        """Update module state.
        
        Args:
            dt: Time delta since last update (seconds)
        """
        current_time = time.time()
        
        # Update timer for timed states
        if self.state in (STATE_MEMORIZE, STATE_RECALL) and self.start_time > 0:
            self.elapsed_time = current_time - self.start_time
            
            # Check for timer expiration
            if self.state == STATE_MEMORIZE and self.elapsed_time >= self.memorize_time:
                self.transition_to_recall()
            elif self.state == STATE_RECALL and self.elapsed_time >= self.recall_time:
                self.evaluate_result()
    
    def build_ui(self, ui=None) -> UI:
        """Build the user interface.
        
        Args:
            ui: Optional UI instance to use, a new one will be created if None
            
        Returns:
            UI object with the component hierarchy
        """
        # Use provided UI or create a new one if not exists
        if ui:
            self.ui = ui
        elif not self.ui:
            self.ui = UI(self.screen_width, self.screen_height)
        
        # Clear existing components if we need a full redraw
        if self.needs_redraw:
            self.ui.clear()
            
            # Build UI based on current state
            if self.state == STATE_INTRO:
                self._build_intro_ui()
            elif self.state == STATE_MEMORIZE:
                self._build_memorize_ui()
            elif self.state == STATE_RECALL:
                self._build_recall_ui()
            elif self.state == STATE_RESULT:
                self._build_result_ui()
            
            # Reset flag
            self.needs_redraw = False
            self.last_state = self.state
        
        # Only update dynamic elements if not doing a full redraw
        else:
            # Update timer if in a timed state
            if self.state in (STATE_MEMORIZE, STATE_RECALL):
                self._update_timer_ui()
        
        return self.ui
    
    def get_state(self) -> Dict[str, Any]:
        """Get the current state for rendering.
        
        Returns:
            State dictionary
        """
        return {
            "ui": self.ui.to_dict() if self.ui else {},
            "state": self.state,
            "level": self.level,
            "score": self.score,
            "high_score": self.high_score,
            "elapsed_time": self.elapsed_time
        }
    
    def handle_click(self, component_id: str, pos: Tuple[int, int]):
        """Handle a click event.
        
        Args:
            component_id: ID of the clicked component
            pos: Click position (x, y)
        """
        logger.debug(f"Click on component {component_id} at {pos}")
        
        if self.state == STATE_INTRO:
            if component_id == "start_button":
                self.start_game()
        
        elif self.state == STATE_RECALL:
            # Check if it's a grid cell click
            if component_id.startswith("cell_"):
                try:
                    # Extract row and column from cell ID (format: cell_row_col)
                    parts = component_id.split("_")
                    row = int(parts[1])
                    col = int(parts[2])
                    
                    # Toggle cell
                    self._toggle_cell(row, col)
                    
                    # Mark UI for update
                    self.needs_redraw = True
                    
                except (IndexError, ValueError) as e:
                    logger.error(f"Error parsing cell ID: {e}")
            
            # Check if it's a symbol selection
            elif component_id.startswith("symbol_"):
                try:
                    # Extract symbol index from ID (format: symbol_index)
                    parts = component_id.split("_")
                    index = int(parts[1])
                    
                    # Set selected symbol
                    self.selected_symbol_index = index
                    
                    # Mark UI for update
                    self.needs_redraw = True
                    
                except (IndexError, ValueError) as e:
                    logger.error(f"Error parsing symbol ID: {e}")
            
            # Check if it's the submit button
            elif component_id == "submit_button":
                self.evaluate_result()
        
        elif self.state == STATE_RESULT:
            if component_id == "continue_button":
                self.start_game()
            elif component_id == "menu_button":
                self.state = STATE_INTRO
                self.needs_redraw = True
    
    def handle_key(self, key: int):
        """Handle a key press event.
        
        Args:
            key: Key code
        """
        logger.debug(f"Key press: {key}")
        
        # Handle specific keys depending on state
        if self.state == STATE_INTRO:
            # Start game on space or enter
            if key in (13, 32):  # Enter or Space
                self.start_game()
        
        elif self.state == STATE_RECALL:
            # Submit on Enter
            if key == 13:  # Enter
                self.evaluate_result()
            
            # Cancel on Escape
            elif key == 27:  # Escape
                self.state = STATE_INTRO
                self.needs_redraw = True
            
            # Arrow keys to change selected symbol
            elif key in (273, 274, 275, 276):  # Up, Down, Right, Left
                direction = 1 if key in (275, 274) else -1  # Right/Down vs Left/Up
                self.selected_symbol_index = (self.selected_symbol_index + direction) % len(self.symbols)
                self.needs_redraw = True
    
    def start_game(self):
        """Start a new game."""
        logger.info(f"Starting new game at level {self.level}")
        
        # Calculate grid size based on level
        self.grid_size = min(3 + (self.level - 1) // 2, 8)
        
        # Generate random grid
        self._generate_game_grid()
        
        # Initialize player grid with empty cells
        self.player_grid = [["" for _ in range(self.grid_size)] for _ in range(self.grid_size)]
        
        # Set state to memorize
        self.state = STATE_MEMORIZE
        self.start_time = time.time()
        self.elapsed_time = 0
        
        # Force UI rebuild
        self.needs_redraw = True
    
    def transition_to_recall(self):
        """Transition from memorize to recall state with visual effect."""
        logger.info("Transitioning to recall state")
        
        # Signal renderer to start transition (if using UnifiedRenderer)
        # The renderer needs to be passed as a parameter during module initialization
        if hasattr(self, 'renderer') and self.renderer:
            self.renderer.start_transition(effect_type="fade", duration=0.8)
        
        # Change state
        self.state = STATE_RECALL
        self.start_time = time.time()
        self.elapsed_time = 0
        
        # Reset selected symbol
        self.selected_symbol_index = 0
        
        # Force UI rebuild
        self.needs_redraw = True
    
    def evaluate_result(self):
        """Evaluate the player's recall result with transition effect."""
        logger.info("Evaluating results")
        
        # Start transition if renderer is available
        if hasattr(self, 'renderer') and self.renderer:
            self.renderer.start_transition(effect_type="zoom_in", duration=0.6)
        
        # Count correct cells
        correct = 0
        total = self.grid_size * self.grid_size
        
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                if self.player_grid[row][col] == self.game_grid[row][col]:
                    correct += 1
        
        # Calculate score as percentage
        accuracy = correct / total
        round_score = int(accuracy * 100)
        
        # Add to total score
        self.score += round_score
        
        # Update high score if needed
        if self.score > self.high_score:
            self.high_score = self.score
        
        # Level up if accuracy is high enough
        if accuracy >= 0.8:
            self.level += 1
        
        # Transition to result state
        self.state = STATE_RESULT
        self.needs_redraw = True
    
    def _generate_game_grid(self):
        """Generate a random grid of symbols for the game."""
        # Determine how many different symbols to use based on level
        num_symbols = min(4 + self.level, len(self.symbols))
        symbols_to_use = random.sample(self.symbols, num_symbols)
        
        # Create the grid
        self.game_grid = []
        for _ in range(self.grid_size):
            row = []
            for _ in range(self.grid_size):
                row.append(random.choice(symbols_to_use))
            self.game_grid.append(row)
    
    def _toggle_cell(self, row: int, col: int):
        """Toggle a cell's symbol in the player grid.
        
        Args:
            row: Row index
            col: Column index
        """
        if 0 <= row < self.grid_size and 0 <= col < self.grid_size:
            # Set the cell to the currently selected symbol
            self.player_grid[row][col] = self.symbols[self.selected_symbol_index]
    
    def _build_intro_ui(self):
        """Build the intro screen UI."""
        # Add a title
        title = ComponentFactory.text(
            text="Symbol Memory",
            x=0, y=100, width=self.screen_width, height=80,
            color=(255, 255, 255),
            fontSize=48,
            textAlign='center'
        )
        self.ui.add(title)
        
        # Add description
        description = ComponentFactory.text(
            text="Memorize the symbols and their positions, then recall them.",
            x=0, y=200, width=self.screen_width, height=40,
            color=(220, 220, 220),
            fontSize=24,
            textAlign='center'
        )
        self.ui.add(description)
        
        # Add level and score info
        if self.level > 1 or self.score > 0:
            info = ComponentFactory.text(
                text=f"Level: {self.level}   Score: {self.score}   High Score: {self.high_score}",
                x=0, y=260, width=self.screen_width, height=30,
                color=(180, 180, 200),
                fontSize=20,
                textAlign='center'
            )
            self.ui.add(info)
        
        # Add start button
        start_button = ComponentFactory.button(
            id="start_button",
            text="Start Game",
            x=(self.screen_width - 200) // 2, 
            y=350,
            width=200, height=60,
            backgroundColor=(60, 120, 255),
            color=(255, 255, 255),
            borderRadius=10,
            fontSize=24
        )
        self.ui.add(start_button)
    
    def _build_memorize_ui(self):
        """Build the memorize screen UI."""
        # Add a title
        title = ComponentFactory.text(
            text="Memorize the Symbols",
            x=0, y=40, width=self.screen_width, height=40,
            color=(255, 255, 255),
            fontSize=32,
            textAlign='center'
        )
        self.ui.add(title)
        
        # Add timer
        timer = ComponentFactory.text(
            id="timer",
            text=f"Time: {self.memorize_time - self.elapsed_time:.1f}s",
            x=0, y=90, width=self.screen_width, height=30,
            color=(220, 220, 100),
            fontSize=20,
            textAlign='center'
        )
        self.ui.add(timer)
        
        # Calculate grid size and position
        self._add_symbol_grid(STATE_MEMORIZE)
    
    def _build_recall_ui(self):
        """Build the recall screen UI."""
        # Add a title
        title = ComponentFactory.text(
            text="Recall the Symbols",
            x=0, y=40, width=self.screen_width, height=40,
            color=(255, 255, 255),
            fontSize=32,
            textAlign='center'
        )
        self.ui.add(title)
        
        # Add timer
        timer = ComponentFactory.text(
            id="timer",
            text=f"Time: {self.recall_time - self.elapsed_time:.1f}s",
            x=0, y=90, width=self.screen_width, height=30,
            color=(220, 220, 100),
            fontSize=20,
            textAlign='center'
        )
        self.ui.add(timer)
        
        # Calculate grid size and position
        self._add_symbol_grid(STATE_RECALL)
        
        # Add symbol selection palette
        self._add_symbol_palette()
        
        # Add submit button
        submit_button = ComponentFactory.button(
            id="submit_button",
            text="Submit",
            x=(self.screen_width - 160) // 2,
            y=self.screen_height - 120,
            width=160, height=50,
            backgroundColor=(60, 200, 100),
            color=(255, 255, 255),
            borderRadius=8,
            fontSize=22
        )
        self.ui.add(submit_button)
    
    def _build_result_ui(self):
        """Build the result screen UI."""
        # Add a title
        title = ComponentFactory.text(
            text="Results",
            x=0, y=80, width=self.screen_width, height=60,
            color=(255, 255, 255),
            fontSize=36,
            textAlign='center'
        )
        self.ui.add(title)
        
        # Count correct answers
        correct = 0
        total = self.grid_size * self.grid_size
        
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                if self.player_grid[row][col] == self.game_grid[row][col]:
                    correct += 1
        
        # Add score info
        accuracy = correct / total
        score_text = f"Correct: {correct}/{total} ({accuracy*100:.1f}%)"
        
        score_info = ComponentFactory.text(
            text=score_text,
            x=0, y=160, width=self.screen_width, height=40,
            color=(220, 220, 100),
            fontSize=28,
            textAlign='center'
        )
        self.ui.add(score_info)
        
        # Add total score
        total_score = ComponentFactory.text(
            text=f"Total Score: {self.score}   High Score: {self.high_score}",
            x=0, y=220, width=self.screen_width, height=30,
            color=(200, 200, 220),
            fontSize=22,
            textAlign='center'
        )
        self.ui.add(total_score)
        
        # Show level change message
        level_text = ""
        if accuracy >= 0.8:
            level_text = f"Great job! Advancing to Level {self.level}"
        else:
            level_text = f"Keep practicing at Level {self.level}"
        
        level_info = ComponentFactory.text(
            text=level_text,
            x=0, y=280, width=self.screen_width, height=30,
            color=(180, 200, 255),
            fontSize=20,
            textAlign='center'
        )
        self.ui.add(level_info)
        
        # Show the correct grid
        # Calculate grid size and position - we'll use a smaller grid size
        cell_size = min(60, (self.screen_height - 450) // self.grid_size)
        grid_width = cell_size * self.grid_size
        grid_height = cell_size * self.grid_size
        
        grid_x = (self.screen_width - grid_width) // 2
        grid_y = 340
        
        grid_container = ComponentFactory.container(
            x=grid_x - 20, y=grid_y - 20,
            width=grid_width + 40, height=grid_height + 40,
            backgroundColor=(40, 40, 60, 180),
            borderWidth=2,
            borderColor=(100, 100, 200),
            borderRadius=10
        )
        self.ui.add(grid_container)
        
        # Add "Correct Solution" label
        solution_label = ComponentFactory.text(
            text="Correct Solution",
            x=grid_x, y=grid_y - 30, width=grid_width, height=20,
            color=(200, 200, 255),
            fontSize=16,
            textAlign='center'
        )
        self.ui.add(solution_label)
        
        # Add cells with the correct symbols
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                cell_x = grid_x + col * cell_size
                cell_y = grid_y + row * cell_size
                
                # Determine if this cell was correct
                is_correct = self.player_grid[row][col] == self.game_grid[row][col]
                
                # Create cell background with color indicating correctness
                cell_bg_color = (40, 100, 40) if is_correct else (100, 40, 40)
                
                cell_bg = ComponentFactory.rect(
                    x=cell_x, y=cell_y,
                    width=cell_size, height=cell_size,
                    backgroundColor=cell_bg_color,
                    borderWidth=1,
                    borderColor=(120, 120, 160)
                )
                self.ui.add(cell_bg)
                
                # Add the correct symbol
                symbol = ComponentFactory.text(
                    text=self.game_grid[row][col],
                    x=cell_x, y=cell_y,
                    width=cell_size, height=cell_size,
                    color=(255, 255, 255),
                    fontSize=cell_size // 2,
                    textAlign='center'
                )
                self.ui.add(symbol)
        
        # Add continue button
        continue_button = ComponentFactory.button(
            id="continue_button",
            text="Next Level",
            x=(self.screen_width - 300) // 2 - 80,
            y=self.screen_height - 120,
            width=160, height=50,
            backgroundColor=(60, 120, 255),
            color=(255, 255, 255),
            borderRadius=8,
            fontSize=20
        )
        self.ui.add(continue_button)
        
        # Add menu button
        menu_button = ComponentFactory.button(
            id="menu_button",
            text="Main Menu",
            x=(self.screen_width - 300) // 2 + 120,
            y=self.screen_height - 120,
            width=160, height=50,
            backgroundColor=(100, 100, 140),
            color=(255, 255, 255),
            borderRadius=8,
            fontSize=20
        )
        self.ui.add(menu_button)
    
    def _update_timer_ui(self):
        """Update the timer text in the UI."""
        if self.state == STATE_MEMORIZE:
            remaining = max(0, self.memorize_time - self.elapsed_time)
            # Find the timer component
            timer_component = self.ui.find_component_by_id("timer")
            if timer_component:
                timer_component.set_props(text=f"Time: {remaining:.1f}s")
        
        elif self.state == STATE_RECALL:
            remaining = max(0, self.recall_time - self.elapsed_time)
            # Find the timer component
            timer_component = self.ui.find_component_by_id("timer")
            if timer_component:
                timer_component.set_props(text=f"Time: {remaining:.1f}s")
    
    def _add_symbol_grid(self, grid_state):
        """Add a symbol grid to the UI.
        
        Args:
            grid_state: Current state (memorize or recall)
        """
        # Calculate adaptive cell size based on screen size and grid size
        min_dimension = min(self.screen_width, self.screen_height)
        max_cell_size = min(100, min_dimension // (self.grid_size + 2))
        
        # Ensure cell size is not too small
        cell_size = max(max_cell_size, 40)
        
        # Calculate grid dimensions
        grid_width = cell_size * self.grid_size
        grid_height = cell_size * self.grid_size
        
        # Center the grid on screen
        grid_x = (self.screen_width - grid_width) // 2
        grid_y = (self.screen_height - grid_height) // 2 - 50  # Offset upward
        
        # Add a container for the grid with a background
        grid_container = ComponentFactory.container(
            x=grid_x - 20, y=grid_y - 20,
            width=grid_width + 40, height=grid_height + 40,
            backgroundColor=(40, 40, 60, 180),
            borderWidth=2,
            borderColor=(100, 100, 200),
            borderRadius=10
        )
        self.ui.add(grid_container)
        
        # Add cells
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                cell_x = grid_x + col * cell_size
                cell_y = grid_y + row * cell_size
                
                # Create clickable cell with ID for recall state
                cell_id = f"cell_{row}_{col}" if grid_state == STATE_RECALL else None
                symbol_text = ""
                
                # Get the appropriate symbol for the cell
                if grid_state == STATE_MEMORIZE:
                    symbol_text = self.game_grid[row][col]
                elif grid_state == STATE_RECALL:
                    symbol_text = self.player_grid[row][col]
                
                # Use the optimized symbol cell component
                cell = ComponentFactory.symbol_cell(
                    id=cell_id,
                    x=cell_x, 
                    y=cell_y,
                    width=cell_size, 
                    height=cell_size,
                    symbol=symbol_text,
                    backgroundColor=(60, 60, 80),
                    borderColor=(120, 120, 160),
                    borderWidth=1,
                    borderRadius=8,
                    color=(255, 255, 255),
                    # Add cell state properties
                    highlighted=False,  # Will be set during interactions
                    active=(grid_state == STATE_RECALL),
                    correct=False,      # Will be set during result phase
                    incorrect=False     # Will be set during result phase
                )
                self.ui.add(cell)
    
    def _add_symbol_palette(self):
        """Add a palette of available symbols for selection."""
        # Calculate position and size
        palette_height = 80
        symbol_size = 50
        max_per_row = min(12, len(self.symbols))
        
        palette_width = max_per_row * symbol_size
        rows_needed = math.ceil(len(self.symbols) / max_per_row)
        
        palette_x = (self.screen_width - palette_width) // 2
        palette_y = self.screen_height - 220
        
        # Add palette background
        palette_bg = ComponentFactory.container(
            x=palette_x - 10, y=palette_y - 10,
            width=palette_width + 20, height=rows_needed * symbol_size + 20,
            backgroundColor=(40, 40, 60, 180),
            borderWidth=2,
            borderColor=(100, 100, 200),
            borderRadius=10
        )
        self.ui.add(palette_bg)
        
        # Add symbols
        for i, symbol in enumerate(self.symbols):
            row = i // max_per_row
            col = i % max_per_row
            
            symbol_x = palette_x + col * symbol_size
            symbol_y = palette_y + row * symbol_size
            
            # Determine if this symbol is selected
            is_selected = i == self.selected_symbol_index
            bg_color = (60, 120, 200) if is_selected else (60, 60, 80)
            
            # Create background
            symbol_bg = ComponentFactory.rect(
                id=f"symbol_{i}",
                x=symbol_x, y=symbol_y,
                width=symbol_size, height=symbol_size,
                backgroundColor=bg_color,
                borderWidth=1,
                borderColor=(140, 140, 180)
            )
            self.ui.add(symbol_bg)
            
            # Add symbol text
            symbol_text = ComponentFactory.text(
                text=symbol,
                x=symbol_x, y=symbol_y,
                width=symbol_size, height=symbol_size,
                color=(255, 255, 255),
                fontSize=symbol_size // 2,
                textAlign='center'
            )
            self.ui.add(symbol_text)
        
        # Add instruction text
        instruction = ComponentFactory.text(
            text="Select a symbol, then click on the grid to place it",
            x=0, y=palette_y - 40, width=self.screen_width, height=30,
            color=(200, 200, 220),
            fontSize=16,
            textAlign='center'
        )
        self.ui.add(instruction)
    
    def handle_event(self, event):
        """Handle an event from the renderer.
        
        Args:
            event: Event dictionary containing event data
        """
        # Handle click events
        if event["type"] == "mousedown":
            if "component_id" in event:
                self.handle_click(event["component_id"], (event["x"], event["y"]))
            else:
                # Handle raw click without component_id
                x, y = event["x"], event["y"]
                # Find component at position
                if self.ui:
                    component = self.ui.find_component_at(x, y)
                    if component:
                        self.handle_click(component.id, (x, y))
        
        # Handle key events
        elif event["type"] == "keydown":
            self.handle_key(event["key"])
        
        # Handle quit events
        elif event["type"] == "quit":
            self.shutdown() 