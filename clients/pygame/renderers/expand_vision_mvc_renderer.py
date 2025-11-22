#!/usr/bin/env python3
"""
ExpandVision MVC Renderer for PyGame

This renderer works with the MVC implementation of the ExpandVision module,
using the new UI component system for consistent styling and layout.

Key features:
1. Component-based rendering with caching
2. Theme-aware styling using the central theme manager
3. Responsive layout that adapts to screen dimensions
4. Efficient rendering with animation effects
"""

import pygame
import logging
import math
import sys
import time
from pathlib import Path
from typing import Dict, List, Any, Tuple, Optional, Union

# Try to import from the package path
try:
    from MetaMindIQTrain.clients.pygame.renderers.base_renderer import BaseRenderer
    from MetaMindIQTrain.core.theme_manager import ThemeManager
    from MetaMindIQTrain.core.ui_component import (
        UIComponent, ContainerComponent, TextComponent, ButtonComponent,
        create_ui_hierarchy, LayoutManager
    )
except ImportError:
    # For direct execution during development
    sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
    from clients.pygame.renderers.base_renderer import BaseRenderer
    from core.theme_manager import ThemeManager
    from core.ui_component import (
        UIComponent, ContainerComponent, TextComponent, ButtonComponent,
        create_ui_hierarchy, LayoutManager
    )

# Configure logging
logger = logging.getLogger(__name__)

class ExpandVisionGridMVCRenderer(BaseRenderer):
    """Renderer for ExpandVision module using MVC pattern and component-based UI."""
    
    def __init__(self, screen, title_font=None, regular_font=None, small_font=None):
        """Initialize the renderer.
        
        Args:
            screen: Pygame screen surface
            title_font: Font for titles (optional)
            regular_font: Font for regular text (optional)
            small_font: Font for small text (optional)
        """
        super().__init__(screen, title_font, regular_font, small_font)
        
        # Screen dimensions
        self.screen_width = self.screen.get_width()
        self.screen_height = self.screen.get_height()
        
        # Set theme platform
        ThemeManager.set_platform("pygame")
        
        # Root component
        self.root_component = None
        
        # Animation properties
        self.animation_time = 0
        self.pulse_animation = 0  # 0-100 for pulsing effect
        self.pulse_direction = 1  # 1 for growing, -1 for shrinking
        
        # Event handlers
        self.on_select_answer = None
        
        # Words for central focus (matches web implementation)
        self.word_list = [
            "relaxing", "breathing", "focusing", "widening", 
            "brain", "energy", "power", "vision"
        ]
        self.current_word_index = 0
        self.word_change_interval = 3.0  # seconds
        self.last_word_change = time.time()
        
        # Debug mode
        self.show_debug = False
    
    def set_event_handlers(self, on_select_answer=None):
        """Set event handlers for UI interactions.
        
        Args:
            on_select_answer: Callback for answer button clicks
        """
        self.on_select_answer = on_select_answer
    
    def render(self, state: Dict[str, Any]):
        """Render the ExpandVision module.
        
        Args:
            state: Current module state
        """
        # Clear screen with background color
        bg_color = ThemeManager.get_color("vision_bg", "#0F141E")
        self.screen.fill(bg_color)
        
        # Update animation timing
        current_time = time.time()
        if current_time - self.last_word_change > self.word_change_interval:
            self.current_word_index = (self.current_word_index + 1) % len(self.word_list)
            self.last_word_change = current_time
        
        # Pulse animation
        self.pulse_animation += 0.5 * self.pulse_direction
        if self.pulse_animation >= 100:
            self.pulse_direction = -1
        elif self.pulse_animation <= 0:
            self.pulse_direction = 1
        
        # Ensure we have a root component
        if not self.root_component:
            self._create_root_component(state)
        
        # Update root component based on state
        self._update_components(state)
        
        # Render the component tree
        self.root_component.render(self.screen)
        
        # Draw debug info if enabled
        if self.show_debug:
            self._render_debug_info(state)
    
    def handle_event(self, event, state):
        """Handle pygame events.
        
        Args:
            event: Pygame event
            state: Current module state
            
        Returns:
            True if the event was handled
        """
        # Check for clicks on buttons during answer phase
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            phase = state.get("phase", "")
            
            # Handle click anywhere during active phase to show answer input
            if phase == "active" and state.get("show_numbers", False):
                # This will be handled by the module's click handler
                return False
        
        # Pass event to root component if available
        if self.root_component:
            return self.root_component.handle_event(event)
        
        return False
    
    def _create_root_component(self, state):
        """Create the root component tree.
        
        Args:
            state: Current module state
        """
        # Create the root container
        self.root_component = ContainerComponent(
            id="root",
            x=0,
            y=0,
            width=self.screen_width,
            height=self.screen_height,
            properties={
                "style": {
                    "backgroundColor": ThemeManager.get_color("vision_bg", "#0F141E")
                }
            }
        )
        
        # Header
        header = ContainerComponent(
            id="header",
            x=0,
            y=0,
            width=self.screen_width,
            height=60,
            properties={
                "style": {
                    "backgroundColor": ThemeManager.get_color("card_bg")
                }
            }
        )
        self.root_component.add_child(header)
        
        # Title
        title = TextComponent(
            id="title",
            x=20,
            y=15,
            width=300,
            height=30,
            text="Expand Vision",
            properties={
                "font": self.title_font,
                "style": {
                    "color": ThemeManager.get_color("text_color"),
                    "fontSize": 24,
                    "textAlign": "left"
                }
            }
        )
        header.add_child(title)
        
        # Score and round
        self.score_text = TextComponent(
            id="score",
            x=self.screen_width - 200,
            y=15,
            width=180,
            height=30,
            text=f"Score: {state.get('score', 0)} | Round: {state.get('round', 1)}/{state.get('total_rounds', 10)}",
            properties={
                "font": self.regular_font,
                "style": {
                    "color": ThemeManager.get_color("text_color"),
                    "fontSize": 18,
                    "textAlign": "right"
                }
            }
        )
        header.add_child(self.score_text)
        
        # Instructions
        self.instructions = TextComponent(
            id="instructions",
            x=20,
            y=70,
            width=self.screen_width - 40,
            height=30,
            text=state.get("message", "Focus on the center circle"),
            properties={
                "font": self.regular_font,
                "style": {
                    "color": ThemeManager.get_color("preparation_text", "#B4DCFA"),
                    "fontSize": 18,
                    "textAlign": "center"
                }
            }
        )
        self.root_component.add_child(self.instructions)
        
        # Game area container
        self.game_container = ContainerComponent(
            id="game_container",
            x=0,
            y=120,
            width=self.screen_width,
            height=self.screen_height - 180,
            properties={
                "style": {
                    "backgroundColor": ThemeManager.get_color("vision_bg", "#0F141E")
                }
            }
        )
        self.root_component.add_child(self.game_container)
        
        # Create the central circle and focus point
        self._create_game_components(state)
        
        # Button container for answer phase
        self.button_container = ContainerComponent(
            id="button_container",
            x=0,
            y=self.screen_height - 150,
            width=self.screen_width,
            height=100,
            properties={
                "style": {
                    "backgroundColor": ThemeManager.get_color("vision_bg", "#0F141E")
                }
            }
        )
        self.root_component.add_child(self.button_container)
    
    def _create_game_components(self, state):
        """Create the central game components (circle and numbers).
        
        Args:
            state: Current module state
        """
        # Clear existing game components
        self.game_container.clear_children()
        
        # Get center position
        center_x = state.get("center_x", self.screen_width // 2)
        center_y = state.get("center_y", self.screen_height // 2)
        
        # Get circle dimensions
        circle_width = state.get("circle_width", 50)
        
        # Get phase
        phase = state.get("phase", "preparation")
        
        # Circle color based on phase
        circle_color = ThemeManager.get_color(
            "vision_circle_active" if phase == "active" else "vision_circle", 
            "#0078FF"
        )
        
        # Apply pulse effect to active circle
        if phase in ["preparation", "active"]:
            # Calculate pulse factor (0.9 to 1.1)
            pulse_factor = 1.0 + (self.pulse_animation - 50) / 500
            circle_width = int(circle_width * pulse_factor)
        
        # Central circle
        circle = ContainerComponent(
            id="central_circle",
            x=center_x - circle_width // 2,
            y=center_y - circle_width // 2,
            width=circle_width,
            height=circle_width,
            properties={
                "style": {
                    "backgroundColor": circle_color,
                    "borderRadius": "50%"  # Make it round
                }
            }
        )
        self.game_container.add_child(circle)
        
        # Focus word in center (only in preparation phase)
        if phase == "preparation":
            focus_word = TextComponent(
                id="focus_word",
                x=center_x - 60,
                y=center_y - 15,
                width=120,
                height=30,
                text=self.word_list[self.current_word_index],
                properties={
                    "font": self.small_font,
                    "style": {
                        "color": ThemeManager.get_color("text_color"),
                        "fontSize": 16,
                        "textAlign": "center"
                    }
                }
            )
            self.game_container.add_child(focus_word)
        
        # Red focus point
        focus_point = ContainerComponent(
            id="focus_point",
            x=center_x - 2,
            y=center_y - 2,
            width=4,
            height=4,
            properties={
                "style": {
                    "backgroundColor": ThemeManager.get_color("focus_point", "#FF0000"),
                    "borderRadius": "50%"
                }
            }
        )
        self.game_container.add_child(focus_point)
        
        # Add peripheral numbers if they should be shown
        if state.get("show_numbers", False) and phase == "active":
            number_positions = state.get("number_positions", [])
            
            # Number colors
            number_colors = [
                ThemeManager.get_color("number_top", "#DCDCDC"),     # Top
                ThemeManager.get_color("number_right", "#FFFF78"),   # Right
                ThemeManager.get_color("number_bottom", "#78FF78"),  # Bottom
                ThemeManager.get_color("number_left", "#7878FF")     # Left
            ]
            
            for i, (x, y, number) in enumerate(number_positions):
                number_text = TextComponent(
                    id=f"number_{i}",
                    x=x - 15,  # Offset for centering
                    y=y - 15,  # Offset for centering
                    width=30,
                    height=30,
                    text=str(number),
                    properties={
                        "font": self.regular_font,
                        "style": {
                            "color": number_colors[i],
                            "fontSize": 22,
                            "textAlign": "center"
                        }
                    }
                )
                self.game_container.add_child(number_text)
    
    def _create_answer_buttons(self, state):
        """Create answer buttons when in answer phase.
        
        Args:
            state: Current module state
        """
        # Clear existing buttons
        self.button_container.clear_children()
        
        # Only create buttons in answer phase
        if state.get("phase") != "answer":
            return
        
        # Get center
        center_x = state.get("center_x", self.screen_width // 2)
        center_y = state.get("center_y", self.screen_height // 2)
        
        # Current sum
        current_sum = state.get("current_sum", 0)
        
        # Button dimensions
        button_height = int(self.screen_height * 0.06)  # 6% of screen height
        button_width = int(self.screen_width * 0.08)    # 8% of screen width
        button_spacing = int(self.screen_width * 0.02)  # 2% of screen width
        
        # Define the possible answers (correct sum +/- offsets)
        possible_answers = [
            current_sum - 2,
            current_sum - 1,
            current_sum,
            current_sum + 1,
            current_sum + 2
        ]
        
        # Calculate total width of all buttons with spacing
        total_width = 5 * button_width + 4 * button_spacing
        start_x = (self.screen_width - total_width) // 2
        button_y = center_y + int(self.screen_height * 0.05)  # Slightly below center
        
        # Create buttons
        for i, value in enumerate(possible_answers):
            btn_x = start_x + i * (button_width + button_spacing)
            
            answer_btn = ButtonComponent(
                id=f"answer_button_{i}",
                x=btn_x,
                y=button_y,
                width=button_width,
                height=button_height,
                text=str(value),
                properties={
                    "style": {
                        "backgroundColor": ThemeManager.get_color(
                            "primary_color" if value == current_sum else "secondary_color"
                        ),
                        "color": ThemeManager.get_color("text_color"),
                        "borderRadius": 5
                    },
                    "value": value,
                    "on_click": lambda comp, value=value: self._on_answer_click(value)
                }
            )
            self.button_container.add_child(answer_btn)
    
    def _update_components(self, state):
        """Update components based on the current state.
        
        Args:
            state: Current module state
        """
        # Update score and round
        if hasattr(self, "score_text"):
            self.score_text.set_text(f"Score: {state.get('score', 0)} | Round: {state.get('round', 1)}/{state.get('total_rounds', 10)}")
        
        # Update instructions
        if hasattr(self, "instructions"):
            self.instructions.set_text(state.get("message", "Focus on the center circle"))
        
        # Update game components (circle and numbers)
        if hasattr(self, "game_container"):
            self._create_game_components(state)
        
        # Update answer buttons
        if hasattr(self, "button_container"):
            self._create_answer_buttons(state)
    
    def _on_answer_click(self, value):
        """Handle answer button click.
        
        Args:
            value: Value of the clicked button
        """
        if self.on_select_answer:
            self.on_select_answer(value)
    
    def _render_debug_info(self, state):
        """Render debug information.
        
        Args:
            state: Current module state
        """
        # Create debug font if not exists
        if not hasattr(self, "debug_font"):
            self.debug_font = pygame.font.SysFont("monospace", 14)
        
        # FPS
        fps_text = f"FPS: {int(self.clock.get_fps())}"
        fps_surface = self.debug_font.render(fps_text, True, (255, 255, 255))
        self.screen.blit(fps_surface, (10, 10))
        
        # Phase
        phase_text = f"Phase: {state.get('phase', 'unknown')}"
        phase_surface = self.debug_font.render(phase_text, True, (255, 255, 255))
        self.screen.blit(phase_surface, (10, 30))
        
        # Circle size
        circle_text = f"Circle: {state.get('circle_width', 0)}x{state.get('circle_height', 0)}"
        circle_surface = self.debug_font.render(circle_text, True, (255, 255, 255))
        self.screen.blit(circle_surface, (10, 50))
        
        # Component count
        if self.root_component:
            component_count = self._count_components(self.root_component)
            count_text = f"Components: {component_count}"
            count_surface = self.debug_font.render(count_text, True, (255, 255, 255))
            self.screen.blit(count_surface, (10, 70))
    
    def _count_components(self, component):
        """Count total components in the tree.
        
        Args:
            component: Root component
            
        Returns:
            Total number of components
        """
        if not component:
            return 0
            
        count = 1  # Count this component
        for child in component.children:
            count += self._count_components(child)
            
        return count


def register_renderer():
    """Register this renderer with the system.
    
    Returns:
        Dictionary with registration info
    """
    return {
        "name": "expand_vision_mvc_renderer",
        "class": ExpandVisionGridMVCRenderer,
        "description": "MVC-based renderer for ExpandVision module",
        "module_types": ["expand_vision"]
    } 