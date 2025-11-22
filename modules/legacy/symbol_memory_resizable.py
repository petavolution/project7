"""
Symbol Memory Module (Resolution-Aware)

This module implements the Symbol Memory training module using the
BaseModule class with dynamic resolution support.
"""

import pygame
import sys
import random
import time
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from core.base_module import BaseModule
from core import config

class SymbolMemoryModule(BaseModule):
    """
    Symbol Memory training module with dynamic resolution support.
    
    This module tests working memory and pattern recognition by:
    1. Displaying a grid of symbols
    2. Hiding the symbols
    3. Asking the user to recall the pattern
    """
    
    def __init__(self, difficulty=3):
        """Initialize the Symbol Memory module."""
        super().__init__(
            title="Symbol Memory Training",
            description="Memorize the pattern, then recall it when the symbols are hidden.",
            difficulty=difficulty
        )
        
        # Module-specific state
        self.symbols = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J"]
        self.grid_size = 3 + self.difficulty // 2  # Grid size based on difficulty
        self.pattern = []
        self.user_pattern = []
        self.state = "intro"  # intro, memorize, recall, feedback
        self.score = 0
        self.current_level = self.difficulty
        
        # Timers
        self.memorize_duration = max(3, 10 - self.difficulty // 2)  # Seconds to memorize
        self.timer = 0
        
        # UI elements
        self.buttons = [
            {"text": "Start", "action": "start"},
            {"text": "Check", "action": "check", "active": False},
            {"text": "Quit", "action": "quit"}
        ]
    
    def setup(self):
        """Set up the module."""
        # Generate a new pattern
        self.generate_pattern()
        
        # Reset state
        self.state = "intro"
        self.user_pattern = [None] * (self.grid_size * self.grid_size)
        self.timer = 0
    
    def generate_pattern(self):
        """Generate a random pattern of symbols."""
        # Create a list of grid positions
        grid_positions = [(x, y) for x in range(self.grid_size) for y in range(self.grid_size)]
        
        # Determine number of symbols to place
        num_symbols = max(3, self.grid_size * self.grid_size // 3)
        
        # Select random positions
        selected_positions = random.sample(grid_positions, num_symbols)
        
        # Create pattern with symbols
        self.pattern = [None] * (self.grid_size * self.grid_size)
        for x, y in selected_positions:
            # Convert 2D position to 1D index
            index = y * self.grid_size + x
            # Assign random symbol
            self.pattern[index] = random.choice(self.symbols)
    
    def update(self, dt):
        """Update module state."""
        # Update timer in memorize state
        if self.state == "memorize":
            self.timer += dt
            
            # Transition to recall state when time is up
            if self.timer >= self.memorize_duration:
                self.state = "recall"
                self.timer = 0
                # Activate check button
                for btn in self.buttons:
                    if btn.get("action") == "check":
                        btn["active"] = True
    
    def render_content(self):
        """Render module content."""
        # Get content area dimensions
        x, y, width, height = config.get_content_rect(self.width, self.height)
        
        # Calculate grid dimensions (maintaining aspect ratio)
        grid_size_factor = config.MODULE_SETTINGS["symbol_memory"]["grid_size_factor"]
        grid_size = min(width, height) * grid_size_factor
        grid_x = x + (width - grid_size) // 2
        grid_y = y + (height - grid_size) // 2
        
        # Render grid
        self.render_grid(grid_x, grid_y, grid_size)
        
        # Render state-specific info
        if self.state == "intro":
            self.render_intro_message()
        elif self.state == "memorize":
            self.render_memorize_info()
        elif self.state == "recall":
            self.render_recall_info()
        elif self.state == "feedback":
            self.render_feedback()
    
    def render_grid(self, x, y, grid_size):
        """Render the symbol grid."""
        # Calculate cell size
        cell_size = grid_size / self.grid_size
        
        # Draw grid background
        self.ui.render_rect(
            (x, y, grid_size, grid_size),
            config.COLORS["grid_bg"],
            config.COLORS["grid_border"],
            2
        )
        
        # Draw grid lines
        for i in range(1, self.grid_size):
            # Vertical lines
            line_x = x + i * cell_size
            pygame.draw.line(
                self.screen,
                config.COLORS["grid_border"],
                (line_x, y),
                (line_x, y + grid_size),
                1
            )
            
            # Horizontal lines
            line_y = y + i * cell_size
            pygame.draw.line(
                self.screen,
                config.COLORS["grid_border"],
                (x, line_y),
                (x + grid_size, line_y),
                1
            )
        
        # Draw cell contents
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                # Calculate cell position
                cell_x = x + col * cell_size
                cell_y = y + row * cell_size
                
                # Convert 2D position to 1D index
                index = row * self.grid_size + col
                
                # Get cell content based on state
                cell_text = None
                if self.state == "memorize":
                    # Show pattern in memorize state
                    cell_text = self.pattern[index]
                elif self.state == "recall":
                    # Show user's selection in recall state
                    cell_text = self.user_pattern[index]
                elif self.state == "feedback":
                    # Show both patterns in feedback state
                    cell_text = self.pattern[index]
                
                # Draw cell content if it exists
                if cell_text:
                    # Calculate text position (center of cell)
                    text_x = cell_x + cell_size / 2
                    text_y = cell_y + cell_size / 2
                    
                    # Determine color based on feedback state
                    color = config.COLORS["text"]
                    if self.state == "feedback":
                        user_value = self.user_pattern[index]
                        # Green if correct, red if incorrect
                        if user_value == cell_text:
                            color = config.COLORS["success"]
                        elif user_value is not None:
                            color = config.COLORS["error"]
                    
                    # Draw text
                    self.ui.render_text(
                        cell_text,
                        (text_x, text_y),
                        font_key="regular",
                        color=color
                    )
    
    def render_intro_message(self):
        """Render introduction message."""
        # Get content area dimensions
        x, y, width, height = config.get_content_rect(self.width, self.height)
        
        # Render instruction message
        message = "Click 'Start' to begin. You'll have "
        message += f"{self.memorize_duration} seconds to memorize the pattern."
        
        self.ui.render_text(
            message,
            (x + width // 2, y + height // 4),
            font_key="regular",
            color=config.COLORS["text_secondary"]
        )
    
    def render_memorize_info(self):
        """Render memorize state information."""
        # Get content area dimensions
        x, y, width, height = config.get_content_rect(self.width, self.height)
        
        # Calculate remaining time
        remaining = max(0, self.memorize_duration - self.timer)
        
        # Render timer
        self.ui.render_text(
            f"Memorize! Time: {remaining:.1f}s",
            (x + width // 2, y + 30),
            font_key="regular",
            color=config.COLORS["primary"]
        )
    
    def render_recall_info(self):
        """Render recall state information."""
        # Get content area dimensions
        x, y, width, height = config.get_content_rect(self.width, self.height)
        
        # Render instruction
        self.ui.render_text(
            "Click cells to recreate the pattern, then press 'Check'",
            (x + width // 2, y + 30),
            font_key="regular",
            color=config.COLORS["primary"]
        )
    
    def render_feedback(self):
        """Render feedback after checking the pattern."""
        # Get content area dimensions
        x, y, width, height = config.get_content_rect(self.width, self.height)
        
        # Calculate score
        correct_count = sum(1 for p, u in zip(self.pattern, self.user_pattern) 
                            if p == u and p is not None)
        total_count = sum(1 for p in self.pattern if p is not None)
        
        # Determine feedback message
        if correct_count == total_count:
            message = "Perfect! All symbols correctly placed."
            color = config.COLORS["success"]
        else:
            message = f"Score: {correct_count}/{total_count} symbols correct."
            color = config.COLORS["text"]
        
        # Render message
        self.ui.render_text(
            message,
            (x + width // 2, y + 30),
            font_key="regular",
            color=color
        )
    
    def process_event(self, event):
        """Process pygame events."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Check if grid was clicked (in recall state only)
            if self.state == "recall":
                self.handle_grid_click(event.pos)
    
    def handle_grid_click(self, pos):
        """Handle a click on the grid."""
        # Get content area dimensions
        content_rect = config.get_content_rect(self.width, self.height)
        x, y, width, height = content_rect
        
        # Calculate grid dimensions
        grid_size_factor = config.MODULE_SETTINGS["symbol_memory"]["grid_size_factor"]
        grid_size = min(width, height) * grid_size_factor
        grid_x = x + (width - grid_size) // 2
        grid_y = y + (height - grid_size) // 2
        
        # Check if click is within grid
        if (grid_x <= pos[0] <= grid_x + grid_size and
            grid_y <= pos[1] <= grid_y + grid_size):
            
            # Calculate cell size
            cell_size = grid_size / self.grid_size
            
            # Calculate cell coordinates
            col = int((pos[0] - grid_x) / cell_size)
            row = int((pos[1] - grid_y) / cell_size)
            
            # Check bounds
            if 0 <= row < self.grid_size and 0 <= col < self.grid_size:
                # Convert 2D position to 1D index
                index = row * self.grid_size + col
                
                # Toggle selection
                if self.user_pattern[index] is None:
                    # Assign a random symbol when clicked
                    self.user_pattern[index] = random.choice(self.symbols)
                else:
                    # Clear if already set
                    self.user_pattern[index] = None
    
    def handle_button_action(self, action):
        """Handle button actions."""
        if action == "start":
            if self.state == "intro" or self.state == "feedback":
                # Start a new round
                self.setup()
                self.state = "memorize"
                self.timer = 0
            
            # Update buttons
            for btn in self.buttons:
                if btn.get("action") == "start":
                    btn["text"] = "Restart"
                elif btn.get("action") == "check":
                    btn["active"] = False
        
        elif action == "check":
            if self.state == "recall":
                # Check the pattern
                self.state = "feedback"
                
                # Enable start button for next round
                for btn in self.buttons:
                    if btn.get("action") == "start":
                        btn["text"] = "Next Level"
                        btn["active"] = True
                    elif btn.get("action") == "check":
                        btn["active"] = False
        
        elif action == "quit":
            self.running = False

# Run the module if executed directly
if __name__ == "__main__":
    module = SymbolMemoryModule(difficulty=3)
    module.run() 