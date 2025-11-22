#!/usr/bin/env python3
"""
MorphMatrix MVC Renderer for PyGame

This renderer works with the MVC implementation of the MorphMatrix module,
using the new UI component system for consistent styling and layout.

Key features:
1. Component-based rendering with caching
2. Theme-aware styling using the central theme manager
3. Responsive layout that adapts to screen dimensions
4. Efficient rendering with surface caching
"""

import pygame
import logging
import math
import sys
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

class MorphMatrixMVCRenderer(BaseRenderer):
    """Renderer for MorphMatrix module using MVC pattern and component-based UI."""
    
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
        
        # Pattern cache for efficient rendering
        self.pattern_cache = {}
        
        # Event handlers
        self.on_pattern_click = None
        self.on_submit_click = None
        self.on_next_click = None
    
    def set_event_handlers(self, on_pattern_click=None, on_submit_click=None, on_next_click=None):
        """Set event handlers for UI interactions.
        
        Args:
            on_pattern_click: Callback for pattern clicks (pattern_index)
            on_submit_click: Callback for submit button click
            on_next_click: Callback for next challenge button click
        """
        self.on_pattern_click = on_pattern_click
        self.on_submit_click = on_submit_click
        self.on_next_click = on_next_click
    
    def render(self, state: Dict[str, Any]):
        """Render the MorphMatrix module.
        
        Args:
            state: Current module state
        """
        # Clear screen with background color
        bg_color = ThemeManager.get_color("bg_color")
        self.screen.fill(bg_color)
        
        # Ensure we have a root component
        if not self.root_component:
            self._create_root_component(state)
        
        # Update root component based on state
        self._update_components(state)
        
        # Render the component tree
        self.root_component.render(self.screen)
        
        # Draw debug info if enabled
        if getattr(self, "show_debug", False):
            self._render_debug_info(state)
    
    def handle_event(self, event, state):
        """Handle pygame events.
        
        Args:
            event: Pygame event
            state: Current module state
            
        Returns:
            True if the event was handled
        """
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
                    "backgroundColor": ThemeManager.get_color("bg_color")
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
            text="MorphMatrix - Pattern Recognition",
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
        
        # Score
        self.score_text = TextComponent(
            id="score",
            x=self.screen_width - 150,
            y=15,
            width=130,
            height=30,
            text=f"Score: {state.get('score', 0)}",
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
            text="Select all patterns that are rotations of the original pattern (blue outline).",
            properties={
                "font": self.regular_font,
                "style": {
                    "color": ThemeManager.get_color("text_color"),
                    "fontSize": 16,
                    "textAlign": "center"
                }
            }
        )
        self.root_component.add_child(self.instructions)
        
        # Pattern container
        self.pattern_container = ContainerComponent(
            id="pattern_container",
            x=0,
            y=110,
            width=self.screen_width,
            height=self.screen_height - 180,
            properties={
                "style": {
                    "backgroundColor": ThemeManager.get_color("bg_color")
                }
            }
        )
        self.root_component.add_child(self.pattern_container)
        
        # Create pattern components
        self._create_pattern_components(state)
        
        # Button container
        self.button_container = ContainerComponent(
            id="button_container",
            x=0,
            y=self.screen_height - 70,
            width=self.screen_width,
            height=70,
            properties={
                "style": {
                    "backgroundColor": ThemeManager.get_color("bg_color")
                }
            }
        )
        self.root_component.add_child(self.button_container)
        
        # Create the appropriate button based on game state
        self._create_action_button(state)
    
    def _create_pattern_components(self, state):
        """Create UI components for pattern display.
        
        Args:
            state: Current module state
        """
        # Clear existing patterns
        self.pattern_container.clear_children()
        
        # Get clusters data
        clusters = state.get("clusters", [])
        if not clusters:
            return
        
        # Calculate layout
        layout = LayoutManager.calculate_grid_positions(
            num_items=len(clusters),
            container_width=self.pattern_container.width,
            container_height=self.pattern_container.height,
            min_width=150,  # Minimum pattern width
            aspect_ratio=1.0,  # Square patterns
            gap=20,  # Gap between patterns
            padding=30  # Padding around grid
        )
        
        # Track pattern components for interaction
        self.pattern_components = []
        
        # Create components for each pattern
        selected_patterns = state.get("selected_patterns", [])
        modified_indices = state.get("modified_indices", [])
        answered = state.get("answered", False)
        
        for i, (x, y, width, height) in enumerate(layout):
            cluster = clusters[i]
            is_selected = i in selected_patterns
            is_original = i == 0  # First pattern is the original
            is_modified = i in modified_indices
            
            # Create pattern container
            pattern = self._create_pattern_component(
                i, x, y, width, height, 
                cluster, is_selected, is_original, 
                is_modified, answered
            )
            
            # Store for reference
            self.pattern_components.append(pattern)
            
            # Add to container
            self.pattern_container.add_child(pattern)
    
    def _create_pattern_component(self, index, x, y, width, height, 
                                 cluster, is_selected, is_original, 
                                 is_modified, answered):
        """Create a pattern component.
        
        Args:
            index: Pattern index
            x, y: Position
            width, height: Dimensions
            cluster: Pattern cluster data
            is_selected: Whether this pattern is selected
            is_original: Whether this is the original pattern
            is_modified: Whether this pattern is modified
            answered: Whether the question has been answered
            
        Returns:
            Pattern component
        """
        # Determine styling
        bg_color = ThemeManager.get_color("card_bg")
        border_color = ThemeManager.get_color("primary_color") if is_original else ThemeManager.get_color("border_color")
        border_width = 3 if is_original else 1
        
        if is_selected:
            border_color = ThemeManager.get_color("accent_color")
            border_width = 2
        
        # If answered, show correct/incorrect styling
        if answered:
            if is_modified:
                # Should NOT be selected
                if is_selected:
                    bg_color = ThemeManager.get_color("error_color")
            else:
                # Should be selected
                if is_selected:
                    bg_color = ThemeManager.get_color("success_color")
                else:
                    bg_color = ThemeManager.get_color("error_color")
        
        # Create container
        pattern = ContainerComponent(
            id=f"pattern_{index}",
            x=x,
            y=y,
            width=width,
            height=height,
            properties={
                "index": index,  # Store index for click handling
                "style": {
                    "backgroundColor": bg_color,
                    "borderColor": border_color,
                    "borderWidth": border_width,
                    "borderRadius": 5
                },
                "on_click": self._on_pattern_click  # Click handler
            }
        )
        
        # Create cells
        matrix = cluster.get("matrix", [])
        if matrix:
            # Calculate cell dimensions
            matrix_size = len(matrix)
            padding = 10
            available_size = min(width, height) - (2 * padding)
            cell_size = available_size // matrix_size
            
            # Calculate start position (center matrix in pattern)
            start_x = (width - (matrix_size * cell_size)) // 2
            start_y = (height - (matrix_size * cell_size)) // 2
            
            # Create cells
            for row in range(matrix_size):
                for col in range(matrix_size):
                    cell_x = start_x + col * cell_size
                    cell_y = start_y + row * cell_size
                    filled = matrix[row][col] == 1
                    
                    cell = ContainerComponent(
                        id=f"cell_{index}_{row}_{col}",
                        x=cell_x,
                        y=cell_y,
                        width=cell_size,
                        height=cell_size,
                        properties={
                            "style": {
                                "backgroundColor": ThemeManager.get_color("accent_color") if filled else ThemeManager.get_color("card_hover"),
                                "borderColor": ThemeManager.get_color("border_color"),
                                "borderWidth": 1
                            }
                        }
                    )
                    pattern.add_child(cell)
        
        return pattern
    
    def _create_action_button(self, state):
        """Create action button based on game state.
        
        Args:
            state: Current module state
        """
        # Clear existing buttons
        self.button_container.clear_children()
        
        # Get game state
        game_state = state.get("game_state", "challenge_active")
        
        # Button properties
        button_width = 150
        button_height = 40
        button_x = (self.screen_width - button_width) // 2
        button_y = 15
        
        if game_state == "challenge_active":
            # Submit button
            submit_button = ButtonComponent(
                id="submit_button",
                x=button_x,
                y=button_y,
                width=button_width,
                height=button_height,
                text="Submit",
                properties={
                    "style": {
                        "backgroundColor": ThemeManager.get_color("primary_color"),
                        "color": ThemeManager.get_color("text_color"),
                        "borderRadius": 5
                    },
                    "on_click": self._on_submit_click
                }
            )
            self.button_container.add_child(submit_button)
        else:
            # Next challenge button
            next_button = ButtonComponent(
                id="next_button",
                x=button_x,
                y=button_y,
                width=button_width,
                height=button_height,
                text="Next Challenge",
                properties={
                    "style": {
                        "backgroundColor": ThemeManager.get_color("primary_color"),
                        "color": ThemeManager.get_color("text_color"),
                        "borderRadius": 5
                    },
                    "on_click": self._on_next_click
                }
            )
            self.button_container.add_child(next_button)
    
    def _update_components(self, state):
        """Update components based on the current state.
        
        Args:
            state: Current module state
        """
        # Update score
        if hasattr(self, "score_text"):
            self.score_text.set_text(f"Score: {state.get('score', 0)}")
        
        # Update instructions based on game state
        if hasattr(self, "instructions"):
            game_state = state.get("game_state", "challenge_active")
            if game_state == "challenge_active":
                self.instructions.set_text("Select all patterns that are rotations of the original pattern (blue outline).")
            elif game_state == "challenge_complete":
                correct = state.get("correct_answer", False)
                if correct:
                    self.instructions.set_text("Correct! Green patterns show rotations, red show modified patterns.")
                else:
                    self.instructions.set_text("Incorrect. Green patterns show rotations, red show modified patterns.")
        
        # Check if we need to recreate patterns (e.g., new challenge)
        clusters = state.get("clusters", [])
        if len(clusters) != len(getattr(self, "pattern_components", [])):
            self._create_pattern_components(state)
        
        # Update button based on game state
        game_state = state.get("game_state", "challenge_active")
        if not hasattr(self, "current_game_state") or self.current_game_state != game_state:
            self._create_action_button(state)
            self.current_game_state = game_state
    
    def _on_pattern_click(self, component):
        """Handle pattern click event.
        
        Args:
            component: Pattern component that was clicked
        """
        if self.on_pattern_click and "index" in component.properties:
            pattern_index = component.properties["index"]
            self.on_pattern_click(pattern_index)
    
    def _on_submit_click(self, component):
        """Handle submit button click.
        
        Args:
            component: Button component
        """
        if self.on_submit_click:
            self.on_submit_click()
    
    def _on_next_click(self, component):
        """Handle next challenge button click.
        
        Args:
            component: Button component
        """
        if self.on_next_click:
            self.on_next_click()
    
    def _render_debug_info(self, state):
        """Render debug information.
        
        Args:
            state: Current module state
        """
        # Render FPS and state info
        debug_font = pygame.font.SysFont("monospace", 14)
        
        # FPS
        fps_text = f"FPS: {int(self.clock.get_fps())}"
        fps_surface = debug_font.render(fps_text, True, (255, 255, 255))
        self.screen.blit(fps_surface, (10, 10))
        
        # Component count
        component_count = self._count_components(self.root_component)
        count_text = f"Components: {component_count}"
        count_surface = debug_font.render(count_text, True, (255, 255, 255))
        self.screen.blit(count_surface, (10, 30))
    
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
        "name": "morph_matrix_mvc_renderer",
        "class": MorphMatrixMVCRenderer,
        "description": "MVC-based renderer for MorphMatrix module",
        "module_types": ["morph_matrix"]
    } 