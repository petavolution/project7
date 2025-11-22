#!/usr/bin/env python3
"""
Terminal Renderer for MetaMindIQTrain

This renderer provides a text-based interface for the MetaMindIQTrain platform,
allowing modules to run in terminal environments without requiring pygame.

Key features:
1. ASCII/Unicode rendering of components
2. Support for colors using ANSI escape codes
3. Keyboard input handling
4. Compatible with the unified component system
"""

import os
import sys
import time
import json
import logging
import curses
import threading
from typing import Dict, List, Any, Optional, Tuple, Union, Set

# Add project root to path for imports when run directly
if __name__ == "__main__":
    import sys
    from pathlib import Path
    project_root = Path(__file__).parent.parent.parent
    sys.path.insert(0, str(project_root))

# Try to import the unified component system
try:
    from MetaMindIQTrain.core.unified_component_system import (
        Component, UI, ComponentFactory, get_stats, reset_stats
    )
except ImportError:
    # For direct execution or during development
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))
    from core.unified_component_system import (
        Component, UI, ComponentFactory, get_stats, reset_stats
    )

# Configure logging
logger = logging.getLogger(__name__)

# ANSI color codes
COLORS = {
    "black": "\033[30m",
    "red": "\033[31m",
    "green": "\033[32m",
    "yellow": "\033[33m",
    "blue": "\033[34m",
    "magenta": "\033[35m",
    "cyan": "\033[36m",
    "white": "\033[37m",
    "reset": "\033[0m",
    "bg_black": "\033[40m",
    "bg_red": "\033[41m",
    "bg_green": "\033[42m",
    "bg_yellow": "\033[43m",
    "bg_blue": "\033[44m",
    "bg_magenta": "\033[45m",
    "bg_cyan": "\033[46m",
    "bg_white": "\033[47m",
}

# Symbol mappings for components
SYMBOLS = {
    "rect": "█",
    "circle": "●",
    "button": "▒",
    "container": "░",
    "grid_h": "─",
    "grid_v": "│",
    "grid_cross": "┼",
    "arrow_up": "↑",
    "arrow_down": "↓",
    "arrow_left": "←",
    "arrow_right": "→",
}

class TerminalRenderer:
    """Terminal renderer for the MetaMindIQTrain platform."""
    
    def __init__(self, width=80, height=24):
        """Initialize the terminal renderer.
        
        Args:
            width: Terminal width
            height: Terminal height
        """
        self.width = width
        self.height = height
        self.ui = None
        self.screen = None
        self.running = False
        self.buffer = []
        self.fps = 15  # Lower FPS for terminal
        self.last_render_time = 0
        self.frame_count = 0
        self.start_time = 0
        
        # Stats
        self.render_time = 0
    
    def initialize(self) -> bool:
        """Initialize the terminal renderer.
        
        Returns:
            True if initialization was successful, False otherwise
        """
        try:
            # Start curses
            self.screen = curses.initscr()
            curses.start_color()
            curses.use_default_colors()
            curses.curs_set(0)  # Hide cursor
            curses.noecho()
            curses.cbreak()
            self.screen.keypad(True)
            self.screen.timeout(100)  # Non-blocking input
            
            # Get terminal size
            height, width = self.screen.getmaxyx()
            self.width = width
            self.height = height
            
            # Initialize color pairs
            curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
            curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_WHITE)
            curses.init_pair(3, curses.COLOR_RED, curses.COLOR_BLACK)
            curses.init_pair(4, curses.COLOR_GREEN, curses.COLOR_BLACK)
            curses.init_pair(5, curses.COLOR_BLUE, curses.COLOR_BLACK)
            curses.init_pair(6, curses.COLOR_YELLOW, curses.COLOR_BLACK)
            curses.init_pair(7, curses.COLOR_CYAN, curses.COLOR_BLACK)
            curses.init_pair(8, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
            
            # Initialize buffer
            self.buffer = [[" " for _ in range(width)] for _ in range(height)]
            
            # Create UI
            self.ui = UI(width, height)
            
            # Set running flag
            self.running = True
            self.start_time = time.time()
            
            logger.info(f"Terminal renderer initialized with resolution {width}x{height}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize terminal renderer: {e}")
            self.shutdown()
            return False
    
    def shutdown(self) -> None:
        """Shut down the renderer."""
        try:
            if self.screen:
                # Restore terminal settings
                curses.nocbreak()
                self.screen.keypad(False)
                curses.echo()
                curses.endwin()
                
            logger.info("Terminal renderer shut down")
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")
    
    def process_events(self) -> List[Dict[str, Any]]:
        """Process terminal events.
        
        Returns:
            List of event dictionaries
        """
        events = []
        
        try:
            key = self.screen.getch()
            
            if key != -1:
                if key == 27:  # ESC
                    events.append({"type": "quit"})
                    self.running = False
                elif key == curses.KEY_ENTER or key == 10 or key == 13:
                    events.append({"type": "keydown", "key": 13, "unicode": "\n"})
                elif key == curses.KEY_UP:
                    events.append({"type": "keydown", "key": 273, "unicode": ""})
                elif key == curses.KEY_DOWN:
                    events.append({"type": "keydown", "key": 274, "unicode": ""})
                elif key == curses.KEY_RIGHT:
                    events.append({"type": "keydown", "key": 275, "unicode": ""})
                elif key == curses.KEY_LEFT:
                    events.append({"type": "keydown", "key": 276, "unicode": ""})
                elif key == 32:  # Space
                    events.append({"type": "keydown", "key": 32, "unicode": " "})
                elif key < 256:
                    events.append({
                        "type": "keydown",
                        "key": key,
                        "unicode": chr(key)
                    })
        except Exception as e:
            logger.error(f"Error processing events: {e}")
        
        return events
    
    def is_running(self) -> bool:
        """Check if the renderer is still running.
        
        Returns:
            True if running, False otherwise
        """
        return self.running
    
    def render(self, state: Dict[str, Any]) -> None:
        """Render the current state.
        
        Args:
            state: Current state dictionary
        """
        start_time = time.time()
        
        # Check if enough time has passed since last render
        if start_time - self.last_render_time < 1.0 / self.fps:
            return
            
        self.last_render_time = start_time
        
        try:
            # Clear buffer
            self.buffer = [[" " for _ in range(self.width)] for _ in range(self.height)]
            
            # Update UI from state if needed
            if "ui" in state:
                self.update_ui_from_state(state["ui"])
            
            # Calculate layout if needed
            if not self.ui.layout_calculated:
                self.ui.calculate_layout()
            
            # Render components
            self.render_component_tree(self.ui.root)
            
            # Draw buffer to screen
            self._draw_buffer()
            
            # Update stats
            self.frame_count += 1
            self.render_time = time.time() - start_time
            
        except Exception as e:
            logger.error(f"Error rendering: {e}")
    
    def update_ui_from_state(self, ui_state: Dict[str, Any]) -> None:
        """Update the UI from a state dictionary.
        
        Args:
            ui_state: UI state dictionary
        """
        # For now, just recreate the UI from scratch
        self.ui.clear()
        
        if "components" in ui_state:
            for component_data in ui_state["components"]:
                component = create_component_tree(component_data)
                self.ui.add(component)
    
    def render_component_tree(self, component: Component) -> None:
        """Render a component and its children.
        
        Args:
            component: Root component to render
        """
        if not component.needs_render():
            return
            
        # Render the component
        self.render_component(component)
        
        # Render children
        for child in component.children:
            self.render_component_tree(child)
        
        # Mark component as clean
        component.mark_clean()
    
    def render_component(self, component: Component) -> None:
        """Render a single component.
        
        Args:
            component: Component to render
        """
        # Skip root component
        if component.type == "root":
            return
            
        # Handle different component types
        if component.type == "rect":
            self._render_rect(component)
        elif component.type == "circle":
            self._render_circle(component)
        elif component.type == "text":
            self._render_text(component)
        elif component.type == "button":
            self._render_button(component)
        elif component.type == "grid":
            self._render_grid(component)
        elif component.type == "container":
            self._render_container(component)
    
    def _render_rect(self, component: Component) -> None:
        """Render a rectangle component.
        
        Args:
            component: Rectangle component
        """
        layout = component.layout
        x, y = layout["x"], layout["y"]
        width, height = layout["width"], layout["height"]
        
        symbol = SYMBOLS["rect"]
        
        # Draw rectangle
        for row in range(max(0, y), min(y + height, self.height)):
            for col in range(max(0, x), min(x + width, self.width)):
                self.buffer[row][col] = symbol
    
    def _render_circle(self, component: Component) -> None:
        """Render a circle component.
        
        Args:
            component: Circle component
        """
        layout = component.layout
        center_x = layout["x"] + layout["width"] // 2
        center_y = layout["y"] + layout["height"] // 2
        radius = component.props.get("radius", min(layout["width"], layout["height"]) // 2)
        
        # Approximate circle with terminal characters
        # Using a simpler approach for terminal renderer
        symbol = SYMBOLS["circle"]
        
        # Set the center point
        if 0 <= center_y < self.height and 0 <= center_x < self.width:
            self.buffer[center_y][center_x] = symbol
    
    def _render_text(self, component: Component) -> None:
        """Render a text component.
        
        Args:
            component: Text component
        """
        layout = component.layout
        x, y = layout["x"], layout["y"]
        width = layout["width"]
        text = component.props.get("text", "")
        align = component.style.get("textAlign", "left")
        
        # Skip if outside bounds
        if y < 0 or y >= self.height:
            return
        
        # Truncate text if needed
        if len(text) > width:
            text = text[:width-3] + "..."
        
        # Handle alignment
        if align == "center":
            x_offset = max(0, (width - len(text)) // 2)
        elif align == "right":
            x_offset = max(0, width - len(text))
        else:  # left
            x_offset = 0
        
        # Draw text
        for i, char in enumerate(text):
            col = x + x_offset + i
            if 0 <= col < self.width:
                self.buffer[y][col] = char
    
    def _render_button(self, component: Component) -> None:
        """Render a button component.
        
        Args:
            component: Button component
        """
        layout = component.layout
        x, y = layout["x"], layout["y"]
        width, height = layout["width"], layout["height"]
        text = component.props.get("text", "")
        
        # Draw button frame
        for row in range(max(0, y), min(y + height, self.height)):
            for col in range(max(0, x), min(x + width, self.width)):
                # Use different symbols for border vs. interior
                if (row == y or row == y + height - 1 or 
                    col == x or col == x + width - 1):
                    self.buffer[row][col] = "+"
                else:
                    self.buffer[row][col] = SYMBOLS["button"]
        
        # Draw button text
        text_y = y + height // 2
        if 0 <= text_y < self.height:
            # Center text
            text_x = x + (width - len(text)) // 2
            for i, char in enumerate(text):
                col = text_x + i
                if 0 <= col < self.width:
                    self.buffer[text_y][col] = char
    
    def _render_grid(self, component: Component) -> None:
        """Render a grid component.
        
        Args:
            component: Grid component
        """
        layout = component.layout
        x, y = layout["x"], layout["y"]
        width, height = layout["width"], layout["height"]
        rows = component.props.get("rows", 1)
        cols = component.props.get("cols", 1)
        
        # Calculate cell size
        cell_width = width / cols
        cell_height = height / rows
        
        # Draw horizontal lines
        for i in range(rows + 1):
            row = y + int(i * cell_height)
            if 0 <= row < self.height:
                for col in range(max(0, x), min(x + width, self.width)):
                    self.buffer[row][col] = SYMBOLS["grid_h"]
        
        # Draw vertical lines
        for i in range(cols + 1):
            col = x + int(i * cell_width)
            if 0 <= col < self.width:
                for row in range(max(0, y), min(y + height, self.height)):
                    self.buffer[row][col] = SYMBOLS["grid_v"]
        
        # Draw intersections
        for i in range(rows + 1):
            row = y + int(i * cell_height)
            if 0 <= row < self.height:
                for j in range(cols + 1):
                    col = x + int(j * cell_width)
                    if 0 <= col < self.width:
                        self.buffer[row][col] = SYMBOLS["grid_cross"]
    
    def _render_container(self, component: Component) -> None:
        """Render a container component.
        
        Args:
            component: Container component
        """
        layout = component.layout
        x, y = layout["x"], layout["y"]
        width, height = layout["width"], layout["height"]
        
        # Draw container border
        for row in range(max(0, y), min(y + height, self.height)):
            for col in range(max(0, x), min(x + width, self.width)):
                if (row == y or row == y + height - 1 or 
                    col == x or col == x + width - 1):
                    self.buffer[row][col] = "."
    
    def _draw_buffer(self) -> None:
        """Draw the buffer to the screen."""
        self.screen.clear()
        
        for y in range(min(self.height, self.screen.getmaxyx()[0] - 1)):
            line = "".join(self.buffer[y][:self.width])
            try:
                self.screen.addstr(y, 0, line)
            except curses.error:
                # This can happen when writing to the bottom-right corner
                pass
        
        # Add stats at the bottom if there's space
        if self.screen.getmaxyx()[0] > 2:
            try:
                fps = self.frame_count / (time.time() - self.start_time) if time.time() > self.start_time else 0
                stats = f"FPS: {fps:.1f} | Render: {self.render_time*1000:.1f}ms"
                self.screen.addstr(self.screen.getmaxyx()[0]-1, 0, stats[:self.width])
            except curses.error:
                pass
        
        self.screen.refresh()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get renderer statistics.
        
        Returns:
            Dictionary with renderer statistics
        """
        current_time = time.time()
        elapsed = current_time - self.start_time
        fps = self.frame_count / elapsed if elapsed > 0 else 0
        
        return {
            'fps': fps,
            'frame_count': self.frame_count,
            'render_time': self.render_time,
            'uptime': elapsed,
            'terminal_size': (self.width, self.height),
            'component_stats': get_stats()
        }


# Helper function for easy initialization
def create_renderer(width=80, height=24) -> TerminalRenderer:
    """Create and initialize a terminal renderer.
    
    Args:
        width: Terminal width
        height: Terminal height
        
    Returns:
        Initialized TerminalRenderer instance
    """
    renderer = TerminalRenderer(width, height)
    renderer.initialize()
    return renderer


# Example usage when run directly
if __name__ == "__main__":
    try:
        # Create and initialize the renderer
        renderer = create_renderer()
        
        # Create a test UI
        ui = UI(renderer.width, renderer.height)
        
        # Add some components
        title = ComponentFactory.text(
            text="Terminal Renderer Test",
            x=10, y=5, width=30, height=1,
            fontSize=12,
            textAlign='center'
        )
        ui.add(title)
        
        button = ComponentFactory.button(
            text="Press Enter",
            x=15, y=10, width=20, height=3
        )
        ui.add(button)
        
        # Use the UI in the renderer
        renderer.ui = ui
        
        # Main loop
        while renderer.is_running():
            # Process events
            events = renderer.process_events()
            
            # Handle events
            for event in events:
                if event["type"] == "quit":
                    break
            
            # Render the UI
            renderer.render({})
            
            # Delay to limit FPS
            time.sleep(0.1)
        
    finally:
        # Ensure terminal is restored
        if 'renderer' in locals():
            renderer.shutdown() 