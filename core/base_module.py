"""
Base Module

This module defines the BaseModule class, which serves as the foundation
for all training modules. It handles common functionality like UI rendering,
window management, and event processing.
"""

import pygame
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from core import config
from core.ui_renderer import UIRenderer

class BaseModule:
    """
    Base class for all training modules in MetaMindIQTrain.
    
    This class handles:
    - Window creation and management
    - Common UI rendering (header, content area, footer)
    - Event processing
    - Game loop
    """
    
    def __init__(self, title, description=None, difficulty=3):
        """
        Initialize the base module.
        
        Args:
            title: Module title
            description: Module description
            difficulty: Initial difficulty level (1-10)
        """
        self.title = title
        self.description = description
        self.difficulty = max(1, min(10, difficulty))
        
        # Initialize pygame if not already initialized
        if not pygame.get_init():
            pygame.init()
        
        # Create window based on config
        self.width, self.height = config.get_resolution()
        
        # Create window
        self.screen = pygame.display.set_mode(
            (self.width, self.height),
            pygame.RESIZABLE if not config.DISPLAY_CONFIG["fullscreen"] else pygame.FULLSCREEN
        )
        pygame.display.set_caption(f"MetaMindIQTrain - {title}")
        
        # Create UI renderer
        self.ui = UIRenderer(self.screen, self.width, self.height)
        
        # Game state
        self.running = False
        self.clock = pygame.time.Clock()
        self.fps_limit = config.DISPLAY_CONFIG["fps_limit"]
        self.show_debug = False
        
        # Default buttons
        self.buttons = [
            {"text": "Start", "action": "start"},
            {"text": "Reset", "action": "reset", "active": False},
            {"text": "Quit", "action": "quit"}
        ]
    
    def setup(self):
        """
        Set up the module. Override this in subclasses to initialize
        module-specific components.
        """
        pass
    
    def update(self, dt):
        """
        Update module state.
        
        Args:
            dt: Time elapsed since last frame (in seconds)
        """
        pass
    
    def render(self):
        """Render the module UI."""
        # Render basic layout (header, content, footer)
        self.ui.render_layout()
        
        # Render header with title and description
        self.ui.render_header(self.title, self.description)
        
        # Render footer buttons
        self.ui.render_footer_buttons(self.buttons)
        
        # Render debug info if enabled
        if self.show_debug:
            self._render_debug_info()
    
    def _render_debug_info(self):
        """Render debug information overlay."""
        # Get current FPS
        fps = int(self.clock.get_fps())
        
        # Render FPS counter
        self.ui.render_text(
            f"FPS: {fps}",
            (10, 10),
            font_key="small",
            color=config.COLORS["text"],
            align="left"
        )
        
        # Render resolution info
        self.ui.render_text(
            f"Resolution: {self.width}x{self.height}",
            (10, 30),
            font_key="small",
            color=config.COLORS["text"],
            align="left"
        )
        
        # Render mouse position
        mouse_x, mouse_y = pygame.mouse.get_pos()
        self.ui.render_text(
            f"Mouse: ({mouse_x}, {mouse_y})",
            (10, 50),
            font_key="small",
            color=config.COLORS["text"],
            align="left"
        )
    
    def handle_event(self, event):
        """
        Handle a pygame event.
        
        Args:
            event: pygame event to handle
            
        Returns:
            True if event was handled, False otherwise
        """
        if event.type == pygame.QUIT:
            self.running = False
            return True
        
        elif event.type == pygame.KEYDOWN:
            # Toggle debug info with F3
            if event.key == pygame.K_F3:
                self.show_debug = not self.show_debug
                return True
            
            # ESC key exits
            elif event.key == pygame.K_ESCAPE:
                self.running = False
                return True
        
        elif event.type == pygame.VIDEORESIZE:
            # Handle window resize
            if not config.DISPLAY_CONFIG["fullscreen"]:
                self.width, self.height = event.size
                self.screen = pygame.display.set_mode(
                    (self.width, self.height),
                    pygame.RESIZABLE
                )
                # Recreate UI renderer with new dimensions
                self.ui = UIRenderer(self.screen, self.width, self.height)
                return True
        
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Handle button clicks in footer
            clicked_button = self.ui.handle_button_click(self.buttons, event.pos)
            if clicked_button:
                self.handle_button_action(clicked_button.get("action"))
                return True
        
        return False
    
    def handle_button_action(self, action):
        """
        Handle a button action.
        
        Args:
            action: Action identifier
        """
        if action == "start":
            # Enable reset button when started
            for btn in self.buttons:
                if btn.get("action") == "reset":
                    btn["active"] = True
                if btn.get("action") == "start":
                    btn["text"] = "Restart"
        
        elif action == "reset":
            # Reset module state
            self.setup()
        
        elif action == "quit":
            self.running = False
    
    def run(self):
        """Run the module game loop."""
        self.setup()
        self.running = True
        last_time = pygame.time.get_ticks() / 1000  # Convert to seconds
        
        while self.running:
            # Calculate delta time
            current_time = pygame.time.get_ticks() / 1000
            dt = current_time - last_time
            last_time = current_time
            
            # Process events
            for event in pygame.event.get():
                if not self.handle_event(event):
                    # Event wasn't handled by base class, give subclass a chance
                    self.process_event(event)
            
            # Update module state
            self.update(dt)
            
            # Render
            self.render()
            
            # Render module content (implemented by subclasses)
            self.render_content()
            
            # Update display
            pygame.display.flip()
            
            # Cap FPS
            self.clock.tick(self.fps_limit)
        
        # Clean up
        pygame.quit()
    
    def process_event(self, event):
        """
        Process a pygame event not handled by the base class.
        Override this in subclasses to handle module-specific events.
        
        Args:
            event: pygame event to process
        """
        pass
    
    def render_content(self):
        """
        Render module-specific content.
        Override this in subclasses to render module content.
        """
        # Get content area dimensions
        content_rect = config.get_content_rect(self.width, self.height)
        
        # Render placeholder text
        self.ui.render_text(
            "Module content goes here",
            (self.width // 2, self.height // 2),
            font_key="regular",
            color=config.COLORS["text_secondary"]
        ) 