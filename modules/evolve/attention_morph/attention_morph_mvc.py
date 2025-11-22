#!/usr/bin/env python3
"""
AttentionMorph Training Module with MVC Architecture

This module implements a cognitive training exercise focused on selective attention,
visual scanning speed, and inhibition control. It's based on a classic attention test
paradigm adapted for interactive cognitive training.

The module separates concerns using a Model-View-Controller pattern:
- Model: Core attention training game logic with shape management and transformations
- View: UI representation with responsive layout and theme-aware styling
- Controller: User interaction, input handling, and adaptive difficulty adjustments

Key features:
1. Clean separation of game logic from presentation
2. Theme-aware styling through ThemeManager integration
3. Responsive grid layout
4. Optimized state management
5. Adaptive difficulty based on performance metrics
6. Multi-modal cognitive engagement
"""

import random
import time
import math
import sys
import os
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional, Union, Set
import pygame

# Add the parent directory to sys.path for absolute imports
if __name__ == "__main__" or not __package__:
    project_root = Path(__file__).parent.parent.parent
    sys.path.insert(0, str(project_root))
    from MetaMindIQTrain.core.training_module import TrainingModule
    from MetaMindIQTrain.core.theme_manager import ThemeManager
    from MetaMindIQTrain.core.config import config
else:
    # Use relative imports when imported as a module
    from ...core.training_module import TrainingModule
    from ...core.theme_manager import ThemeManager
    from ...core.config import config

# Import local module components
from .attention_morph_model import AttentionMorphModel, Shape
from .attention_morph_view import AttentionMorphView
from .attention_morph_controller import AttentionMorphController
from .adaptive_difficulty_engine import AdaptiveDifficultyEngine


class AttentionMorph(TrainingModule):
    """Main training module that implements the AttentionMorph cognitive training exercise.
    
    This module enhances selective attention and visual scanning speed by requiring users
    to identify target shapes while ignoring distractors. The module demonstrates principles
    of inhibition control and focused attention, which are critical executive functions.
    """
    
    MODULE_NAME = "Attention Morph"
    MODULE_DESCRIPTION = "Find and select targets while ignoring distractors. " \
                        "Enhances selective attention, visual scanning speed, and cognitive inhibition."
    
    def __init__(self, difficulty=1):
        """Initialize the AttentionMorph training module.
        
        Args:
            difficulty: Initial difficulty level (1-10)
        """
        super().__init__()
        
        # Initialize model with appropriate difficulty
        self.model = AttentionMorphModel(rows=5, cols=5)
        self.model.difficulty_level = max(1, min(10, difficulty))
        
        # Initialize adaptive difficulty engine for performance-based adjustments
        self.adaptive_engine = AdaptiveDifficultyEngine()
        
        # View and controller will be initialized in build_ui
        self.view = None
        self.controller = None
        
        # Module state tracking
        self.last_time = time.time()
        self.fps_stats = []
        self.module_ready = False
        
        # Initialize theme
        self.theme = ThemeManager.get_theme()

    @staticmethod
    def get_name():
        """Get the display name of the module."""
        return AttentionMorph.MODULE_NAME
    
    @staticmethod
    def get_description():
        """Get the description of the module."""
        return AttentionMorph.MODULE_DESCRIPTION

    def handle_click(self, x, y):
        """Handle mouse click events in the module.
        
        Args:
            x: X coordinate of the click
            y: Y coordinate of the click
        """
        if self.controller:
            event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {'pos': (x, y), 'button': 1})
            self.controller.handle_user_input(event)
            
        # Track the property to optimize state updates
        self.track_property('state')

    def update(self, dt):
        """Update the module state.
        
        Args:
            dt: Time delta in seconds
        """
        if not self.module_ready:
            return
            
        # Update controller state
        current_time = time.time()
        
        if self.controller:
            self.controller.track_performance_metrics()
            self.controller.update_grid_state()
            
            # Apply difficulty adjustments every 10 seconds
            if int(current_time) % 10 == 0 and int(self.last_time) % 10 != 0:
                metrics = self.controller.performance_metrics
                difficulty_adjustment = self.adaptive_engine.compute_difficulty_adjustment(
                    metrics["accuracy"],
                    metrics["average_reaction_time"],
                    metrics["targets_per_minute"]
                )
                
                # Apply the difficulty adjustment
                new_level = max(1, min(10, self.model.difficulty_level + difficulty_adjustment))
                if new_level != self.model.difficulty_level:
                    self.model.update_difficulty(new_level)
                    
            self.last_time = current_time
            
        # Track FPS for performance monitoring
        if dt > 0:
            self.fps_stats.append(1.0 / dt)
            if len(self.fps_stats) > 60:
                self.fps_stats.pop(0)

    def get_state(self):
        """Get the current state of the module for UI rendering.
        
        Returns:
            Dict containing the current state
        """
        if not self.module_ready:
            return {}
            
        if self.controller:
            game_data = self.controller.get_game_data_for_view()
            
            return {
                'phase': self.controller.state,
                'grid': self.model.get_grid_data(),
                'targets_found': self.controller.performance_metrics["total_targets_found"],
                'targets_missed': self.controller.performance_metrics["targets_missed"],
                'score': self.model.score,
                'level': self.model.difficulty_level,
                'time_left': max(0, self.controller.game_timer),
                'accuracy': self.model.get_accuracy() * 100,  # As percentage
                'fps': sum(self.fps_stats) / len(self.fps_stats) if self.fps_stats else 0,
            }
        return {}

    def process_input(self, input_data):
        """Process external input data.
        
        Args:
            input_data: Input data dictionary
            
        Returns:
            Result of the input processing
        """
        if not self.module_ready:
            return {"status": "error", "message": "Module not ready"}
        
        action = input_data.get("action")
        
        if action == "select":
            x = input_data.get("x", 0)
            y = input_data.get("y", 0)
            self.handle_click(x, y)
            return {"status": "success", "action": "select"}
        elif action == "start":
            if self.controller and self.controller.state == self.controller.STATE_INTRO:
                self.controller.state = self.controller.STATE_PLAYING
                self.controller._reset_game()
                return {"status": "success", "action": "start"}
        elif action == "reset":
            if self.controller:
                self.controller._reset_game()
                return {"status": "success", "action": "reset"}
            
        return {"status": "error", "message": "Unknown action"}

    def build_ui(self):
        """Build the UI components for the module.
        
        Returns:
            Dictionary of UI components
        """
        # Initialize view with current screen dimensions
        screen_width = self.SCREEN_WIDTH or 800
        screen_height = self.SCREEN_HEIGHT or 600
        
        window_surface = pygame.Surface((screen_width, screen_height))
        self.view = AttentionMorphView(window_surface)
        
        # Initialize controller
        self.controller = AttentionMorphController(self.model, self.view, self.adaptive_engine)
        
        # Mark module as ready
        self.module_ready = True
        
        # Return empty component dictionary (UI handled internally)
        return {"root": None}


def main():
    """Main function to run the module independently for testing."""
    pygame.init()
    
    # Set up display with reasonable default size
    width, height = 800, 600
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Attention Morph Module")
    
    # Initialize the module
    module = AttentionMorph(difficulty=3)
    module.SCREEN_WIDTH = width
    module.SCREEN_HEIGHT = height
    module.build_ui()
    
    clock = pygame.time.Clock()
    running = True
    
    # Main game loop
    while running:
        dt = clock.tick(60) / 1000.0  # Convert to seconds
        
        # Process events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                else:
                    # Handle other key events by passing to controller
                    if module.controller:
                        module.controller.handle_user_input(event)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Handle mouse clicks
                module.handle_click(*event.pos)
        
        # Update module
        module.update(dt)
        
        # Clear screen 
        screen.fill(module.theme["bg_color"])
        
        # Render the current state
        if module.controller:
            game_data = module.get_state()
            
            if module.controller.state == module.controller.STATE_INTRO:
                _render_intro_screen(screen, width, height, module.theme)
            elif module.controller.state == module.controller.STATE_GAME_OVER:
                _render_game_over_screen(screen, width, height, game_data, module.theme)
            else:
                # Render active gameplay
                if module.view:
                    module.view.render_shape_grid(module.model.grid)
        
        # Update display
        pygame.display.flip()
    
    pygame.quit()
    sys.exit()


def _render_intro_screen(screen, width, height, theme):
    """Render introduction screen with instructions."""
    # Use theme colors for consistent styling
    bg_color = theme["bg_color"]
    text_color = theme["text_color"]
    accent_color = theme["accent_color"]
    
    # Fill background
    screen.fill(bg_color)
    
    # Load fonts
    title_font = pygame.font.SysFont(theme["font_family"], int(height * 0.07))
    instruction_font = pygame.font.SysFont(theme["font_family"], int(height * 0.04))
    
    # Render title
    title = title_font.render("Attention Morph", True, accent_color)
    title_rect = title.get_rect(center=(width // 2, height * 0.2))
    screen.blit(title, title_rect)
    
    # Render instructions
    instructions = [
        "Find and select all 'd' shapes with exactly 2 marks",
        "Ignore all other shapes",
        "Work quickly but accurately",
        "",
        "Click anywhere to begin"
    ]
    
    y_pos = height * 0.4
    for line in instructions:
        text = instruction_font.render(line, True, text_color)
        text_rect = text.get_rect(center=(width // 2, y_pos))
        screen.blit(text, text_rect)
        y_pos += height * 0.07


def _render_game_over_screen(screen, width, height, game_data, theme):
    """Render game over screen with results."""
    # Use theme colors for consistent styling
    bg_color = theme["bg_color"]
    text_color = theme["text_color"]
    accent_color = theme["accent_color"]
    success_color = theme["success_color"]
    
    # Fill background
    screen.fill(bg_color)
    
    # Load fonts
    title_font = pygame.font.SysFont(theme["font_family"], int(height * 0.07))
    stats_font = pygame.font.SysFont(theme["font_family"], int(height * 0.05))
    instruction_font = pygame.font.SysFont(theme["font_family"], int(height * 0.04))
    
    # Render title
    title = title_font.render("Training Complete!", True, accent_color)
    title_rect = title.get_rect(center=(width // 2, height * 0.2))
    screen.blit(title, title_rect)
    
    # Render statistics
    stats = [
        f"Score: {game_data.get('score', 0)}",
        f"Targets Found: {game_data.get('targets_found', 0)}",
        f"Accuracy: {game_data.get('accuracy', 0):.1f}%",
        f"Level Reached: {game_data.get('level', 1)}"
    ]
    
    y_pos = height * 0.4
    for line in stats:
        text = stats_font.render(line, True, text_color)
        text_rect = text.get_rect(center=(width // 2, y_pos))
        screen.blit(text, text_rect)
        y_pos += height * 0.07
    
    # Render restart instruction
    restart_text = instruction_font.render("Click anywhere to play again", True, success_color)
    restart_rect = restart_text.get_rect(center=(width // 2, height * 0.8))
    screen.blit(restart_text, restart_rect)


if __name__ == "__main__":
    main() 