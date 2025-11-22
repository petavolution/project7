#!/usr/bin/env python3
"""
SymbolMemory MVC Renderer for PyGame

This renderer works with the MVC implementation of the SymbolMemory module,
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

class SymbolMemoryMVCRenderer(BaseRenderer):
    """Renderer for SymbolMemory module using MVC pattern and component-based UI."""
    
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
        
        # Symbol cache for efficient rendering
        self.symbol_cache = {}
        
        # Event handlers
        self.on_yes_click = None
        self.on_no_click = None
        self.on_continue_click = None
        
        # Debug mode
        self.show_debug = False
    
    def set_event_handlers(self, on_yes_click=None, on_no_click=None, on_continue_click=None):
        """Set event handlers for UI interactions.
        
        Args:
            on_yes_click: Callback for Yes button clicks
            on_no_click: Callback for No button clicks
            on_continue_click: Callback for Continue button clicks
        """
        self.on_yes_click = on_yes_click
        self.on_no_click = on_no_click
        self.on_continue_click = on_continue_click
    
    def render(self, state: Dict[str, Any]):
        """Render the SymbolMemory module.
        
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
            text="Symbol Memory - Recall Challenge",
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
            text=state.get("message", "Memorize the pattern"),
            properties={
                "font": self.regular_font,
                "style": {
                    "color": ThemeManager.get_color("text_color"),
                    "fontSize": 18,
                    "textAlign": "center"
                }
            }
        )
        self.root_component.add_child(self.instructions)
        
        # Create grid container
        grid_size = state.get("current_grid_size", 3)
        
        # Calculate grid dimensions
        grid_margin = 40
        max_grid_width = self.screen_width - (2 * grid_margin)
        max_grid_height = self.screen_height - 200  # Leave space for UI elements
        
        cell_size = min(
            max_grid_width / grid_size,
            max_grid_height / grid_size
        )
        
        grid_padding = 10
        grid_width = grid_size * cell_size + 2 * grid_padding
        grid_height = grid_width  # Square grid
        
        grid_x = (self.screen_width - grid_width) // 2
        grid_y = 120  # Position from top
        
        self.grid_container = ContainerComponent(
            id="grid_container",
            x=grid_x,
            y=grid_y,
            width=grid_width,
            height=grid_height,
            properties={
                "style": {
                    "backgroundColor": ThemeManager.get_color("card_bg"),
                    "borderColor": ThemeManager.get_color("border_color"),
                    "borderWidth": 2,
                    "borderRadius": 5
                },
                "grid_padding": grid_padding,
                "cell_size": cell_size,
                "grid_size": grid_size
            }
        )
        self.root_component.add_child(self.grid_container)
        
        # Create the cells
        self._create_grid_cells(state)
        
        # Button container
        button_y = grid_y + grid_height + 30
        self.button_container = ContainerComponent(
            id="button_container",
            x=0,
            y=button_y,
            width=self.screen_width,
            height=70,
            properties={
                "style": {
                    "backgroundColor": ThemeManager.get_color("bg_color")
                }
            }
        )
        self.root_component.add_child(self.button_container)
        
        # Create the appropriate buttons based on phase
        self._create_phase_buttons(state)
    
    def _create_grid_cells(self, state):
        """Create grid cells based on current state.
        
        Args:
            state: Current module state
        """
        # Clear existing cells
        self.grid_container.clear_children()
        
        # Get pattern data
        phase = state.get("phase", "memorize")
        grid_size = state.get("current_grid_size", 3)
        
        # Determine which pattern to show
        pattern = None
        show_symbols = False
        
        if phase == "memorize":
            pattern = state.get("original_pattern", None)
            show_symbols = True
        elif phase == "compare":
            pattern = state.get("modified_pattern", None)
            show_symbols = True
        
        if not pattern:
            return
        
        grid = pattern.get("grid", [])
        if not grid:
            return
        
        # Get layout properties
        grid_padding = self.grid_container.get_property("grid_padding", 10)
        cell_size = self.grid_container.get_property("cell_size", 50)
        
        # Create cells
        for row in range(grid_size):
            for col in range(grid_size):
                cell_x = grid_padding + col * cell_size
                cell_y = grid_padding + row * cell_size
                
                # Cell background
                cell = ContainerComponent(
                    id=f"cell_{row}_{col}",
                    x=cell_x,
                    y=cell_y,
                    width=cell_size,
                    height=cell_size,
                    properties={
                        "style": {
                            "backgroundColor": ThemeManager.get_color("card_hover"),
                            "borderColor": ThemeManager.get_color("border_color"),
                            "borderWidth": 1
                        }
                    }
                )
                self.grid_container.add_child(cell)
                
                # Add symbol if visible
                symbol = grid[row][col] if row < len(grid) and col < len(grid[row]) else ""
                if show_symbols and symbol:
                    symbol_text = TextComponent(
                        id=f"symbol_{row}_{col}",
                        x=cell_x,
                        y=cell_y,
                        width=cell_size,
                        height=cell_size,
                        text=symbol,
                        properties={
                            "font": self.regular_font,
                            "style": {
                                "color": ThemeManager.get_color("primary_color"),
                                "fontSize": int(cell_size * 0.6),
                                "textAlign": "center"
                            }
                        }
                    )
                    self.grid_container.add_child(symbol_text)
    
    def _create_phase_buttons(self, state):
        """Create buttons based on the current phase.
        
        Args:
            state: Current module state
        """
        # Clear existing buttons
        self.button_container.clear_children()
        
        # Get phase
        phase = state.get("phase", "memorize")
        
        # Button dimensions
        button_width = 120
        button_height = 50
        button_margin = 20
        
        if phase == "answer":
            # Yes button
            yes_x = self.screen_width // 2 - button_width - button_margin
            yes_button = ButtonComponent(
                id="yes_button",
                x=yes_x,
                y=10,
                width=button_width,
                height=button_height,
                text="Yes",
                properties={
                    "style": {
                        "backgroundColor": ThemeManager.get_color("primary_color"),
                        "color": ThemeManager.get_color("text_color"),
                        "borderRadius": 5
                    },
                    "on_click": self._on_yes_click
                }
            )
            self.button_container.add_child(yes_button)
            
            # No button
            no_x = self.screen_width // 2 + button_margin
            no_button = ButtonComponent(
                id="no_button",
                x=no_x,
                y=10,
                width=button_width,
                height=button_height,
                text="No",
                properties={
                    "style": {
                        "backgroundColor": ThemeManager.get_color("secondary_color"),
                        "color": ThemeManager.get_color("text_color"),
                        "borderRadius": 5
                    },
                    "on_click": self._on_no_click
                }
            )
            self.button_container.add_child(no_button)
            
        elif phase == "feedback":
            # Continue button
            continue_x = (self.screen_width - button_width) // 2
            continue_button = ButtonComponent(
                id="continue_button",
                x=continue_x,
                y=10,
                width=button_width,
                height=button_height,
                text="Continue",
                properties={
                    "style": {
                        "backgroundColor": ThemeManager.get_color("primary_color"),
                        "color": ThemeManager.get_color("text_color"),
                        "borderRadius": 5
                    },
                    "on_click": self._on_continue_click
                }
            )
            self.button_container.add_child(continue_button)
    
    def _update_components(self, state):
        """Update components based on the current state.
        
        Args:
            state: Current module state
        """
        # Update score
        if hasattr(self, "score_text"):
            self.score_text.set_text(f"Score: {state.get('score', 0)}")
        
        # Update instructions
        if hasattr(self, "instructions"):
            self.instructions.set_text(state.get("message", "Memorize the pattern"))
        
        # Check if grid has changed
        current_grid_size = state.get("current_grid_size", 3)
        if hasattr(self, "grid_container"):
            grid_size = self.grid_container.get_property("grid_size", 0)
            if grid_size != current_grid_size:
                # Recalculate grid dimensions
                grid_margin = 40
                max_grid_width = self.screen_width - (2 * grid_margin)
                max_grid_height = self.screen_height - 200
                
                cell_size = min(
                    max_grid_width / current_grid_size,
                    max_grid_height / current_grid_size
                )
                
                grid_padding = 10
                grid_width = current_grid_size * cell_size + 2 * grid_padding
                grid_height = grid_width
                
                grid_x = (self.screen_width - grid_width) // 2
                grid_y = 120
                
                # Update grid container
                self.grid_container.x = grid_x
                self.grid_container.y = grid_y
                self.grid_container.width = grid_width
                self.grid_container.height = grid_height
                self.grid_container.set_property("grid_size", current_grid_size)
                self.grid_container.set_property("cell_size", cell_size)
                
                # Position button container
                if hasattr(self, "button_container"):
                    self.button_container.y = grid_y + grid_height + 30
                
                # Force update
                self.grid_container.mark_dirty()
        
        # Update grid cells for current phase
        self._create_grid_cells(state)
        
        # Update buttons for current phase
        phase = state.get("phase", "memorize")
        if not hasattr(self, "current_phase") or self.current_phase != phase:
            self._create_phase_buttons(state)
            self.current_phase = phase
    
    def _on_yes_click(self, component):
        """Handle Yes button click.
        
        Args:
            component: Button component
        """
        if self.on_yes_click:
            self.on_yes_click()
    
    def _on_no_click(self, component):
        """Handle No button click.
        
        Args:
            component: Button component
        """
        if self.on_no_click:
            self.on_no_click()
    
    def _on_continue_click(self, component):
        """Handle Continue button click.
        
        Args:
            component: Button component
        """
        if self.on_continue_click:
            self.on_continue_click()
    
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
        
        # Component count
        if self.root_component:
            component_count = self._count_components(self.root_component)
            count_text = f"Components: {component_count}"
            count_surface = self.debug_font.render(count_text, True, (255, 255, 255))
            self.screen.blit(count_surface, (10, 50))
    
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
        "name": "symbol_memory_mvc_renderer",
        "class": SymbolMemoryMVCRenderer,
        "description": "MVC-based renderer for SymbolMemory module",
        "module_types": ["symbol_memory"]
    } 