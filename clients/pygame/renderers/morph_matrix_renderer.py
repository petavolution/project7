#!/usr/bin/env python3
"""
MorphMatrix Renderer for PyGame

This module provides a specialized renderer for the MorphMatrix module,
ensuring visual consistency with the web implementation.

Key features:
1. Theme-aware styling that matches the web CSS
2. 3x2 grid layout matching the web UI
3. Consistent UI flow between platforms
4. Utilizes the unified component system for rendering
"""

import pygame
import logging
import math
from typing import Dict, List, Any, Tuple, Optional

# Try to import from the package first
try:
    from MetaMindIQTrain.clients.pygame.renderers.base_renderer import BaseRenderer
    from MetaMindIQTrain.core.theme import get_theme, set_theme, Theme
    from MetaMindIQTrain.core.unified_component_system import ComponentFactory, UI
except ImportError:
    # For direct execution during development
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
    from clients.pygame.renderers.base_renderer import BaseRenderer
    from core.theme import get_theme, set_theme, Theme
    from core.unified_component_system import ComponentFactory, UI

# Configure logging
logger = logging.getLogger(__name__)

class MorphMatrixRenderer(BaseRenderer):
    """Specialized renderer for the MorphMatrix module."""
    
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
        
        # Initialize colors from theme
        self.initialize_colors()
        
        # Cache for rendered patterns
        self.pattern_cache = {}
        
        # Current UI state
        self.ui = UI(self.screen_width, self.screen_height)
        
        # Track current screen state
        self.current_screen = "start"  # "start", "game", "results"
    
    def initialize_colors(self):
        """Initialize colors from theme system."""
        # Ensure we have a theme
        theme = get_theme()
        if not theme:
            # Create and set a theme that matches the web colors
            theme = Theme.default_theme(platform="pygame")
            
            # Update colors to match web version explicitly
            theme.colors.update({
                "background": (30, 36, 44),        # Dark background color
                "card_background": (40, 44, 52),   # Darker cell background
                "text_primary": (255, 255, 255),   # White text
                "primary": (0, 120, 255),          # Blue for primary actions
                "primary_hover": (30, 140, 255),   # Hover state
                "success": (75, 210, 75),          # Green for correct answers
                "error": (255, 75, 75),            # Red for incorrect answers
                "warning": (255, 220, 55),         # Yellow for warnings
                "border": (100, 100, 160),         # Border color
                "highlight": (255, 220, 115),      # Highlight color
                "cell_filled": (255, 50, 50),      # Bright red for filled cells
                "cell_empty": (50, 255, 50),       # Bright green for empty cells
                "cell_highlight": (80, 180, 255)   # Highlight color for cells
            })
            
            # Set component styles
            theme.component_styles.update({
                "pattern_container": {
                    "backgroundColor": theme.colors["card_background"],
                    "borderWidth": 1,
                    "borderColor": theme.colors["border"],
                    "borderRadius": 5,
                },
                "pattern_container_original": {
                    "backgroundColor": theme.colors["card_background"],
                    "borderWidth": 3,
                    "borderColor": theme.colors["primary"],
                    "borderRadius": 5,
                },
                "pattern_container_selected": {
                    "backgroundColor": theme.colors["card_background"],
                    "borderWidth": 2,
                    "borderColor": theme.colors["highlight"],
                    "borderRadius": 5,
                }
            })
            
            # Set the theme
            set_theme(theme)
        
        # Get colors from theme
        theme = get_theme()
        self.colors = theme.colors
    
    def render(self, state: Dict[str, Any]):
        """Render the MorphMatrix module.
        
        Args:
            state: Current module state
        """
        # Clear screen with background color
        self.screen.fill(self.colors["background"])
        
        # Determine which screen to show
        current_screen = state.get("game_state", "challenge_active")
        
        if current_screen == "intro" or current_screen == "module_intro":
            self.render_start_screen(state)
        elif current_screen == "challenge_active":
            self.render_game_screen(state)
        elif current_screen == "challenge_complete" or current_screen == "feedback":
            self.render_results_screen(state)
        else:
            # Fallback to game screen
            self.render_game_screen(state)
        
        # Draw UI chrome (module name, score, etc.)
        self.render_ui_chrome(state)
    
    def render_start_screen(self, state: Dict[str, Any]):
        """Render the start screen.
        
        Args:
            state: Current module state
        """
        # Draw title
        title_text = "Morph Matrix"
        title_surface = self.title_font.render(title_text, True, self.colors["text_primary"])
        title_rect = title_surface.get_rect(centerx=self.screen_width//2, top=100)
        self.screen.blit(title_surface, title_rect)
        
        # Draw instructions
        instructions = [
            "The ORIGINAL PATTERN is shown at the top center with a blue outline.",
            "Select all patterns that are EXACT ROTATIONS of the original pattern.",
            "Avoid patterns that have had cells changed.",
            "Click on a pattern to select/deselect it."
        ]
        
        y_pos = title_rect.bottom + 30
        for instruction in instructions:
            text_surface = self.regular_font.render(instruction, True, self.colors["text_primary"])
            text_rect = text_surface.get_rect(centerx=self.screen_width//2, top=y_pos)
            self.screen.blit(text_surface, text_rect)
            y_pos += 30
        
        # Draw start button
        button_width, button_height = 200, 50
        button_rect = pygame.Rect(
            (self.screen_width - button_width) // 2,
            y_pos + 40,
            button_width,
            button_height
        )
        self.draw_button(button_rect, "Start Challenge", "start_challenge")
    
    def render_game_screen(self, state: Dict[str, Any]):
        """Render the game screen with patterns.
        
        Args:
            state: Current module state
        """
        # Draw title and instructions
        title_text = "Morph Matrix"
        title_surface = self.title_font.render(title_text, True, self.colors["text_primary"])
        title_rect = title_surface.get_rect(centerx=self.screen_width//2, top=20)
        self.screen.blit(title_surface, title_rect)
        
        instruction = "Select all patterns that are exact rotations of the original pattern"
        instruction_surface = self.regular_font.render(instruction, True, self.colors["warning"])
        instruction_rect = instruction_surface.get_rect(centerx=self.screen_width//2, top=title_rect.bottom + 10)
        self.screen.blit(instruction_surface, instruction_rect)
        
        # Render patterns
        clusters = state.get("clusters", [])
        selected_patterns = state.get("selected_patterns", [])
        
        if clusters:
            self.render_pattern_grid(clusters, selected_patterns)
        
        # Draw check button
        button_width, button_height = 180, 50
        button_rect = pygame.Rect(
            (self.screen_width - button_width) // 2,
            self.screen_height - button_height - 40,
            button_width,
            button_height
        )
        self.draw_button(button_rect, "Check Answers", "check_answers")
    
    def render_results_screen(self, state: Dict[str, Any]):
        """Render the results screen.
        
        Args:
            state: Current module state
        """
        # Draw results title
        title_text = "Results"
        title_surface = self.title_font.render(title_text, True, self.colors["text_primary"])
        title_rect = title_surface.get_rect(centerx=self.screen_width//2, top=20)
        self.screen.blit(title_surface, title_rect)
        
        # Draw score
        score = state.get("score", 0)
        score_text = f"Score: {score}"
        score_surface = self.regular_font.render(score_text, True, self.colors["text_primary"])
        score_rect = score_surface.get_rect(centerx=self.screen_width//2, top=title_rect.bottom + 20)
        self.screen.blit(score_surface, score_rect)
        
        # Render patterns with feedback
        clusters = state.get("clusters", [])
        selected_patterns = state.get("selected_patterns", [])
        modified_indices = state.get("modified_indices", [])
        
        if clusters:
            self.render_pattern_grid(clusters, selected_patterns, show_feedback=True, modified_indices=modified_indices)
        
        # Draw next button
        button_width, button_height = 180, 50
        button_rect = pygame.Rect(
            (self.screen_width - button_width) // 2,
            self.screen_height - button_height - 40,
            button_width,
            button_height
        )
        self.draw_button(button_rect, "Next Challenge", "next_challenge")
    
    def render_pattern_grid(self, clusters, selected_patterns, show_feedback=False, modified_indices=None):
        """Render the 3x2 grid of patterns that matches the web layout.
        
        Args:
            clusters: List of pattern clusters
            selected_patterns: List of selected pattern indices
            show_feedback: Whether to show feedback on correct/incorrect answers
            modified_indices: List of indices that were modified
        """
        # Use consistent pattern dimensions matching web version
        pattern_size = clusters[0].get("size", 5)
        cell_size = 30  # Match web CSS
        pattern_width = pattern_size * cell_size
        pattern_height = pattern_size * cell_size
        
        # Calculate grid layout for 3x2 grid with original in center top
        grid_width = self.screen_width * 0.9
        grid_height = grid_width * 0.6  # Keep similar aspect ratio to web
        
        # Position grid to match web layout
        grid_x = (self.screen_width - grid_width) / 2
        grid_y = 100  # Place below instructions
        
        # Calculate padding between patterns
        padding_x = grid_width * 0.05
        padding_y = grid_height * 0.1
        
        # Calculate individual pattern positions in 3x2 grid
        # Top row: patterns 1, 0 (original), 2
        # Bottom row: patterns 3, 4, 5
        positions = [
            # Top row
            (grid_x + grid_width * 0.25 - pattern_width/2, grid_y),  # Index 1
            (grid_x + grid_width * 0.5 - pattern_width/2, grid_y),   # Original (index 0)
            (grid_x + grid_width * 0.75 - pattern_width/2, grid_y),  # Index 2
            # Bottom row
            (grid_x + grid_width * 0.16 - pattern_width/2, grid_y + pattern_height + padding_y),  # Index 3
            (grid_x + grid_width * 0.5 - pattern_width/2, grid_y + pattern_height + padding_y),   # Index 4
            (grid_x + grid_width * 0.84 - pattern_width/2, grid_y + pattern_height + padding_y)   # Index 5
        ]
        
        # Reorder to match web layout: original (0) goes in center top position
        reordered_positions = [positions[1]]  # Original position
        reordered_positions.extend([positions[0], positions[2]])  # Rest of top row
        reordered_positions.extend(positions[3:])  # Bottom row
        
        # Render each pattern
        for i, cluster in enumerate(clusters):
            if i >= len(reordered_positions):
                continue
                
            # Get position
            pos_x, pos_y = reordered_positions[i]
            
            # Determine if this pattern is selected or original
            is_original = i == 0
            is_selected = i in selected_patterns
            
            # Create rectangle for the pattern container
            pattern_rect = pygame.Rect(
                pos_x, pos_y, 
                pattern_width, pattern_height
            )
            
            # Draw pattern container with appropriate styling
            container_rect = pygame.Rect(
                pattern_rect.x - 10, pattern_rect.y - 10,
                pattern_rect.width + 20, pattern_rect.height + 20
            )
            
            # Choose styling based on state
            if is_original:
                # Blue border for original pattern
                border_color = self.colors["primary"]
                border_width = 3
            elif is_selected:
                # Highlight color for selected patterns
                border_color = self.colors["highlight"]
                border_width = 2
            else:
                # Default border for other patterns
                border_color = self.colors["border"]
                border_width = 1
            
            # Draw container background
            pygame.draw.rect(
                self.screen,
                self.colors["card_background"],
                container_rect,
                border_radius=5
            )
            
            # Draw container border
            pygame.draw.rect(
                self.screen,
                border_color,
                container_rect,
                width=border_width,
                border_radius=5
            )
            
            # Draw matrix
            matrix = cluster.get("matrix", [])
            for r in range(len(matrix)):
                for c in range(len(matrix[r])):
                    cell_x = pattern_rect.x + c * cell_size
                    cell_y = pattern_rect.y + r * cell_size
                    cell_rect = pygame.Rect(cell_x, cell_y, cell_size, cell_size)
                    
                    # Cell color based on value - match web colors
                    if matrix[r][c] == 1:
                        cell_color = self.colors["cell_filled"]
                    else:
                        cell_color = self.colors["cell_empty"]
                    
                    # Draw cell
                    pygame.draw.rect(
                        self.screen,
                        cell_color,
                        cell_rect,
                    )
                    
                    # Draw cell border
                    pygame.draw.rect(
                        self.screen,
                        (80, 80, 80),
                        cell_rect,
                        width=1
                    )
            
            # Draw label below pattern
            if is_original:
                label_text = "ORIGINAL PATTERN"
            else:
                label_text = f"PATTERN {i + 1}"
            
            label_surface = self.small_font.render(label_text, True, 
                self.colors["primary"] if is_original else self.colors["text_primary"])
            label_rect = label_surface.get_rect(
                centerx=pattern_rect.centerx,
                top=pattern_rect.bottom + 5
            )
            self.screen.blit(label_surface, label_rect)
            
            # Show feedback if requested
            if show_feedback and not is_original:
                is_modified = modified_indices and i in modified_indices
                is_correct_selection = (is_selected and not is_modified) or (not is_selected and is_modified)
                
                # Draw feedback label
                if is_modified:
                    feedback_text = "MODIFIED"
                else:
                    feedback_text = "EXACT ROTATION"
                
                feedback_color = self.colors["success"] if is_correct_selection else self.colors["error"]
                feedback_surface = self.small_font.render(feedback_text, True, feedback_color)
                feedback_rect = feedback_surface.get_rect(
                    centerx=pattern_rect.centerx,
                    top=label_rect.bottom + 5
                )
                self.screen.blit(feedback_surface, feedback_rect)
    
    def render_ui_chrome(self, state: Dict[str, Any]):
        """Render UI chrome elements.
        
        Args:
            state: Current module state
        """
        # Draw score and level in top corners
        score = state.get("score", 0)
        level = state.get("level", 1)
        
        # Score in top-left
        score_text = f"Score: {score}"
        score_surface = self.small_font.render(score_text, True, self.colors["text_primary"])
        score_rect = score_surface.get_rect(left=20, top=20)
        self.screen.blit(score_surface, score_rect)
        
        # Level in top-right
        level_text = f"Level: {level}"
        level_surface = self.small_font.render(level_text, True, self.colors["text_primary"])
        level_rect = level_surface.get_rect(right=self.screen_width-20, top=20)
        self.screen.blit(level_surface, level_rect)
    
    def draw_button(self, rect, text, action=None, hover=False):
        """Draw a button with text.
        
        Args:
            rect: Button rectangle
            text: Button text
            action: Button action
            hover: Whether the button is being hovered
        """
        # Draw button background
        bg_color = self.colors["primary_hover"] if hover else self.colors["primary"]
        pygame.draw.rect(
            self.screen,
            bg_color,
            rect,
            border_radius=8
        )
        
        # Draw button text
        text_surface = self.regular_font.render(text, True, self.colors["text_primary"])
        text_rect = text_surface.get_rect(center=rect.center)
        self.screen.blit(text_surface, text_rect)
    
    def handle_event(self, event, state):
        """Handle pygame events.
        
        Args:
            event: Pygame event
            state: Current module state
            
        Returns:
            Action dictionary or None
        """
        # Handle mouse clicks
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Check button clicks
            mouse_pos = pygame.mouse.get_pos()
            
            # Handle clicks based on current screen
            current_screen = state.get("game_state", "challenge_active")
            
            if current_screen == "intro" or current_screen == "module_intro":
                # Check start button
                button_width, button_height = 200, 50
                button_rect = pygame.Rect(
                    (self.screen_width - button_width) // 2,
                    240,
                    button_width,
                    button_height
                )
                if button_rect.collidepoint(mouse_pos):
                    return {"action": "start_challenge"}
            
            elif current_screen == "challenge_active":
                # Check for pattern clicks
                clusters = state.get("clusters", [])
                if clusters:
                    pattern_idx = self.get_clicked_pattern(mouse_pos, clusters)
                    if pattern_idx is not None and pattern_idx > 0:  # Original can't be selected
                        return {"action": "toggle_pattern", "pattern": pattern_idx}
                
                # Check check button
                button_width, button_height = 180, 50
                button_rect = pygame.Rect(
                    (self.screen_width - button_width) // 2,
                    self.screen_height - button_height - 40,
                    button_width,
                    button_height
                )
                if button_rect.collidepoint(mouse_pos):
                    return {"action": "check_answers"}
            
            elif current_screen == "challenge_complete" or current_screen == "feedback":
                # Check next button
                button_width, button_height = 180, 50
                button_rect = pygame.Rect(
                    (self.screen_width - button_width) // 2,
                    self.screen_height - button_height - 40,
                    button_width,
                    button_height
                )
                if button_rect.collidepoint(mouse_pos):
                    return {"action": "next_challenge"}
        
        return None
    
    def get_clicked_pattern(self, mouse_pos, clusters):
        """Determine which pattern was clicked.
        
        Args:
            mouse_pos: Mouse position (x, y)
            clusters: List of pattern clusters
            
        Returns:
            Pattern index or None if no pattern was clicked
        """
        # Use consistent pattern dimensions matching web version
        pattern_size = clusters[0].get("size", 5)
        cell_size = 30  # Match web CSS
        pattern_width = pattern_size * cell_size
        pattern_height = pattern_size * cell_size
        
        # Calculate grid layout for 3x2 grid with original in center top
        grid_width = self.screen_width * 0.9
        grid_height = grid_width * 0.6  # Keep similar aspect ratio to web
        
        # Position grid to match web layout
        grid_x = (self.screen_width - grid_width) / 2
        grid_y = 100  # Place below instructions
        
        # Calculate padding between patterns
        padding_x = grid_width * 0.05
        padding_y = grid_height * 0.1
        
        # Calculate individual pattern positions in 3x2 grid
        # Top row: patterns 1, 0 (original), 2
        # Bottom row: patterns 3, 4, 5
        positions = [
            # Top row
            (grid_x + grid_width * 0.25 - pattern_width/2, grid_y),  # Index 1
            (grid_x + grid_width * 0.5 - pattern_width/2, grid_y),   # Original (index 0)
            (grid_x + grid_width * 0.75 - pattern_width/2, grid_y),  # Index 2
            # Bottom row
            (grid_x + grid_width * 0.16 - pattern_width/2, grid_y + pattern_height + padding_y),  # Index 3
            (grid_x + grid_width * 0.5 - pattern_width/2, grid_y + pattern_height + padding_y),   # Index 4
            (grid_x + grid_width * 0.84 - pattern_width/2, grid_y + pattern_height + padding_y)   # Index 5
        ]
        
        # Reorder to match web layout: original (0) goes in center top position
        reordered_positions = [positions[1]]  # Original position
        reordered_positions.extend([positions[0], positions[2]])  # Rest of top row
        reordered_positions.extend(positions[3:])  # Bottom row
        
        # Check each pattern collision
        for i, pos in enumerate(reordered_positions):
            if i >= len(clusters):
                continue
                
            # Pattern container rectangle
            container_rect = pygame.Rect(
                pos[0] - 10, pos[1] - 10,
                pattern_width + 20, pattern_height + 20
            )
            
            if container_rect.collidepoint(mouse_pos):
                return i
        
        return None

def register_renderer():
    """Register this renderer with the system."""
    return {
        "id": "morph_matrix",
        "name": "MorphMatrix",
        "renderer_class": MorphMatrixRenderer,
        "description": "Pattern recognition challenge renderer"
    } 