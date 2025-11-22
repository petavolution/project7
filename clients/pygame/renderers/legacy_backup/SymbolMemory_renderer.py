#!/usr/bin/env python3
"""
Memory Renderer

This module provides a renderer for the SymbolMemory module of MetaMindIQTrain.
It handles displaying the Symbol Memory Training module and tests a user's ability to
remember sequences of symbols.
"""

import pygame
import time
from datetime import datetime

from MetaMindIQTrain.clients.pygame.renderers.base_renderer import BaseRenderer
from MetaMindIQTrain.config import calculate_sizes, DEFAULT_SYMBOL_SIZE

class MemoryRenderer(BaseRenderer):
    """Renderer for the SymbolMemory module."""
    
    def __init__(self, screen, title_font, regular_font, small_font):
        """Initialize the renderer with the screen and fonts."""
        super().__init__(screen, title_font, regular_font, small_font)
        
        # Calculate sizes based on screen dimensions
        self.screen_width = self.screen.get_width()
        self.screen_height = self.screen.get_height()
        self.sizes = calculate_sizes(self.screen_width, self.screen_height)
        
        # Dark theme colors
        self.BG_COLOR = (15, 25, 35)         # Very dark blue/black for background
        self.CONTENT_BG = (20, 30, 45)       # Slightly lighter for content areas
        self.DARK_BLUE = (30, 60, 120)       # Dark blue for UI elements
        self.LIGHT_BLUE = (80, 140, 255)     # Brighter blue for highlights and hover
        self.GREEN = (40, 180, 80)           # Vibrant green for positive feedback
        self.RED = (220, 60, 60)             # Vibrant red for negative feedback
        self.GRAY = (120, 120, 130)          # Dark gray for subtle elements
        self.GRAY_LIGHT = (180, 180, 200)    # Light gray for secondary text
        self.TEXT_PRIMARY = (240, 245, 255)  # Almost white for primary text
        self.TEXT_SECONDARY = (180, 190, 210)# Light blue-gray for secondary text
        self.TEXT_HIGHLIGHT = (255, 255, 255)# Pure white for highlighted text
        self.ACCENT = (100, 200, 255)        # Bright blue accent color
        
        # Symbol settings
        self.symbol_size = self.percent_x(0.06)  # 6% of screen width
        
        # Create buttons for memory test - dark theme style
        button_width = self.percent_x(0.15)  # 15% of screen width
        button_height = self.percent_y(0.06)  # 6% of screen height
        button_spacing = self.percent_x(0.05)  # 5% of screen width
        
        # Position buttons in the footer area
        footer_center_x = self.footer_rect.centerx
        footer_center_y = self.footer_rect.centery
        
        self.buttons = [
            {
                'text': 'YES',
                'action': 'yes',
                'rect': pygame.Rect(
                    footer_center_x - button_spacing - button_width,
                    footer_center_y - button_height // 2,
                    button_width,
                    button_height
                ),
                'color': self.GREEN,
                'hover_color': (80, 220, 120),
                'text_color': self.TEXT_HIGHLIGHT,
                'visible': False  # Will be shown during question phase
            },
            {
                'text': 'NO',
                'action': 'no',
                'rect': pygame.Rect(
                    footer_center_x + button_spacing,
                    footer_center_y - button_height // 2,
                    button_width,
                    button_height
                ),
                'color': self.RED,
                'hover_color': (255, 100, 100),
                'text_color': self.TEXT_HIGHLIGHT,
                'visible': False  # Will be shown during question phase
            },
            {
                'text': 'CONTINUE',
                'action': 'continue',
                'rect': pygame.Rect(
                    footer_center_x - button_width // 2,
                    footer_center_y - button_height // 2,
                    button_width,
                    button_height
                ),
                'color': self.DARK_BLUE,
                'hover_color': self.LIGHT_BLUE,
                'text_color': self.TEXT_HIGHLIGHT,
                'visible': False  # Will be shown during feedback phase
            },
            {
                'text': 'Start Challenge',
                'action': 'start_challenge',
                'rect': pygame.Rect(
                    footer_center_x - button_width * 1.5 - button_spacing,
                    footer_center_y - button_height // 2,
                    button_width * 1.5,
                    button_height
                ),
                'color': self.DARK_BLUE,
                'hover_color': self.LIGHT_BLUE,
                'text_color': self.TEXT_HIGHLIGHT,
                'visible': True  # Always visible
            },
            {
                'text': 'Reset Level',
                'action': 'reset_level',
                'rect': pygame.Rect(
                    footer_center_x + button_spacing,
                    footer_center_y - button_height // 2,
                    button_width,
                    button_height
                ),
                'color': self.DARK_BLUE,
                'hover_color': self.LIGHT_BLUE,
                'text_color': self.TEXT_HIGHLIGHT,
                'visible': True  # Always visible
            },
            {
                'text': 'Advance Level',
                'action': 'advance_level',
                'rect': pygame.Rect(
                    footer_center_x + button_spacing,
                    footer_center_y - button_height // 2,
                    button_width,
                    button_height
                ),
                'color': self.DARK_BLUE,
                'hover_color': self.LIGHT_BLUE,
                'text_color': self.TEXT_HIGHLIGHT,
                'visible': True  # Always visible
            }
        ]
    
    def render(self, state):
        """Render the memory training module."""
        # Fill the background first with our dark theme color
        self.screen.fill(self.BG_COLOR)
        
        # Draw the standard layout (clears screen, draws sections)
        self.draw_standard_layout(state)
        
        # Fill content area with slightly lighter background
        pygame.draw.rect(self.screen, self.CONTENT_BG, self.content_rect)
        
        # Update which buttons are visible based on current phase
        self._update_buttons_for_phase(state)
        
        # Draw the appropriate content based on the game phase
        game_state = state.get('game_state', 'memorize')
        
        if game_state == 'memorize':
            self._draw_memorize_phase(state)
        elif game_state == 'question':
            self._draw_question_phase(state)
        elif game_state == 'feedback':
            self._draw_feedback_phase(state)
    
    def _update_buttons_for_phase(self, state):
        """Update which buttons are visible based on the current phase."""
        showing_feedback = state.get('showing_feedback', False)
        showing_modified = state.get('showing_modified', False)
        
        for button in self.buttons:
            if button['action'] == 'continue':
                button['visible'] = showing_feedback
            elif button['action'] in ['yes', 'no']:
                button['visible'] = showing_modified
    
    def _draw_memorize_phase(self, state):
        """Draw the memorization phase."""
        # Draw phase indicator
        self._draw_phase_indicator("MEMORIZE", self.ACCENT)
        
        # Get remaining time for memorization if available
        remaining_time = None
        if 'phase_transition_time' in state:
            current_time = pygame.time.get_ticks()
            remaining_time = max(0, state['phase_transition_time'] - current_time)
            remaining_seconds = int(remaining_time / 1000) + 1  # Round up to nearest second
            
            # Draw countdown timer prominently
            timer_text = f"Time: {remaining_seconds}s"
            timer_surface = self.regular_font.render(timer_text, True, self.ACCENT)
            timer_rect = timer_surface.get_rect(center=(self.content_rect.centerx, self.content_rect.top + self.percent_y(0.08)))
            self.screen.blit(timer_surface, timer_rect)
        
        # Draw instructions
        instructions = "Memorize this pattern"
        instructions_surface = self.regular_font.render(instructions, True, self.TEXT_PRIMARY)
        instructions_rect = instructions_surface.get_rect(center=(self.content_rect.centerx, self.content_rect.top + self.percent_y(0.15)))
        self.screen.blit(instructions_surface, instructions_rect)
        
        # Draw the symbol pattern centered in the content area
        memorize_y = self.content_rect.centery
        
        # First draw a blue oval around where the symbols will appear
        symbols = state.get('symbols', [])
        if symbols:
            # Draw the symbol pattern first to get its dimensions
            text_dimensions = self._draw_symbol_pattern(state, position=(self.content_rect.centerx, memorize_y), phase="memorize")
            
            # Calculate the size of the oval based on the text dimensions
            oval_width = text_dimensions['width'] * 1.3
            oval_height = text_dimensions['height'] * 1.8
            
            # Create oval surface with transparency for a more modern look
            oval_surface = pygame.Surface((oval_width, oval_height), pygame.SRCALPHA)
            pygame.draw.ellipse(
                oval_surface,
                (80, 140, 255, 160),  # Light blue color with alpha
                pygame.Rect(0, 0, oval_width, oval_height),
                3  # Line width
            )
            
            # Position the oval
            oval_rect = oval_surface.get_rect(center=(self.content_rect.centerx, memorize_y))
            
            # Draw the oval
            self.screen.blit(oval_surface, oval_rect)
        
        # Draw level and trial info at the top corners
        if 'level' in state and 'current_trial' in state and 'trials_per_round' in state:
            level = state.get('level', 1)
            current_trial = state.get('current_trial', 0)
            trials_per_round = state.get('trials_per_round', 5)
            
            # Left corner - Level
            level_text = f"Level: {level}"
            level_surface = self.small_font.render(level_text, True, self.TEXT_SECONDARY)
            level_rect = level_surface.get_rect(left=self.content_rect.left + 20, top=self.content_rect.top + 10)
            self.screen.blit(level_surface, level_rect)
            
            # Right corner - Trial
            trial_text = f"Trial: {current_trial + 1}/{trials_per_round}"
            trial_surface = self.small_font.render(trial_text, True, self.TEXT_SECONDARY)
            trial_rect = trial_surface.get_rect(right=self.content_rect.right - 20, top=self.content_rect.top + 10)
            self.screen.blit(trial_surface, trial_rect)
    
    def _draw_question_phase(self, state):
        """Draw the question phase."""
        # Draw phase indicator
        self._draw_phase_indicator("QUESTION", self.ACCENT)
        
        # Draw instructions
        instructions = "Was the pattern modified?"
        instructions_surface = self.regular_font.render(instructions, True, self.TEXT_PRIMARY)
        instructions_rect = instructions_surface.get_rect(center=(self.content_rect.centerx, self.content_rect.top + self.percent_y(0.08)))
        self.screen.blit(instructions_surface, instructions_rect)
        
        # Draw additional instructions
        sub_instructions = "Compare with the pattern you memorized"
        sub_instructions_surface = self.small_font.render(sub_instructions, True, self.TEXT_SECONDARY)
        sub_instructions_rect = sub_instructions_surface.get_rect(center=(self.content_rect.centerx, self.content_rect.top + self.percent_y(0.15)))
        self.screen.blit(sub_instructions_surface, sub_instructions_rect)
        
        # Draw the symbol pattern (potentially modified) centered in the content area
        question_y = self.content_rect.centery
        
        # First draw a gray oval around where the symbols will appear
        symbols = state.get('symbols', [])
        if symbols:
            # Draw the symbol pattern first to get its dimensions
            text_dimensions = self._draw_symbol_pattern(state, position=(self.content_rect.centerx, question_y), phase="question")
            
            # Calculate the size of the oval based on the text dimensions
            oval_width = text_dimensions['width'] * 1.3
            oval_height = text_dimensions['height'] * 1.8
            
            # Create oval surface with transparency
            oval_surface = pygame.Surface((oval_width, oval_height), pygame.SRCALPHA)
            pygame.draw.ellipse(
                oval_surface,
                (140, 140, 160, 160),  # Light gray color with alpha
                pygame.Rect(0, 0, oval_width, oval_height),
                3  # Line width
            )
            
            # Position the oval
            oval_rect = oval_surface.get_rect(center=(self.content_rect.centerx, question_y))
            
            # Draw the oval
            self.screen.blit(oval_surface, oval_rect)
        
        # Draw YES and NO buttons with clear labels
        yes_button = next((b for b in self.buttons if b['action'] == 'yes'), None)
        no_button = next((b for b in self.buttons if b['action'] == 'no'), None)
        
        if yes_button and no_button:
            # Draw explanatory text above the buttons
            prompt_text = "Select your answer:"
            prompt_surface = self.small_font.render(prompt_text, True, self.TEXT_SECONDARY)
            prompt_rect = prompt_surface.get_rect(center=(self.footer_rect.centerx, self.footer_rect.centery - self.percent_y(0.05)))
            self.screen.blit(prompt_surface, prompt_rect)
            
            # Ensure buttons are visible
            yes_button['visible'] = True
            no_button['visible'] = True
            
            # Ensure button text is clear
            yes_button['text'] = 'MODIFIED (Y)'
            no_button['text'] = 'SAME (N)'
        
        # Draw level and trial info at the top corners (same as memorize phase)
        if 'level' in state and 'current_trial' in state and 'trials_per_round' in state:
            level = state.get('level', 1)
            current_trial = state.get('current_trial', 0)
            trials_per_round = state.get('trials_per_round', 5)
            
            # Left corner - Level
            level_text = f"Level: {level}"
            level_surface = self.small_font.render(level_text, True, self.TEXT_SECONDARY)
            level_rect = level_surface.get_rect(left=self.content_rect.left + 20, top=self.content_rect.top + 10)
            self.screen.blit(level_surface, level_rect)
            
            # Right corner - Trial
            trial_text = f"Trial: {current_trial + 1}/{trials_per_round}"
            trial_surface = self.small_font.render(trial_text, True, self.TEXT_SECONDARY)
            trial_rect = trial_surface.get_rect(right=self.content_rect.right - 20, top=self.content_rect.top + 10)
            self.screen.blit(trial_surface, trial_rect)
    
    def _draw_feedback_phase(self, state):
        """Draw the feedback phase with results."""
        # Draw phase indicator
        self._draw_phase_indicator("FEEDBACK", self.ACCENT)
        
        # Get result from state
        correct = state.get('last_correct', False)
        was_modified = state.get('was_modified', False)
        user_answer = state.get('user_answer', "")
        
        # Determine feedback text and color
        if correct:
            feedback_text = "Correct!"
            feedback_color = self.GREEN
        else:
            feedback_text = "Incorrect"
            feedback_color = self.RED
        
        # Draw main feedback text
        feedback_surface = self.title_font.render(feedback_text, True, feedback_color)
        feedback_rect = feedback_surface.get_rect(center=(self.content_rect.centerx, self.content_rect.top + self.percent_y(0.08)))
        self.screen.blit(feedback_surface, feedback_rect)
        
        # Draw explanation
        if was_modified:
            explanation = f"The pattern WAS modified. You answered: {user_answer.upper()}"
        else:
            explanation = f"The pattern was NOT modified. You answered: {user_answer.upper()}"
        
        explanation_surface = self.regular_font.render(explanation, True, self.TEXT_PRIMARY)
        explanation_rect = explanation_surface.get_rect(center=(self.content_rect.centerx, self.content_rect.top + self.percent_y(0.15)))
        self.screen.blit(explanation_surface, explanation_rect)
        
        # Draw the symbol patterns side by side for comparison
        original_pattern = state.get('original_pattern', [])
        modified_pattern = state.get('modified_pattern', [])
        
        # Calculate container sizes - make it slightly wider and with more visual contrast
        container_width = min(self.content_rect.width * 0.9, 800)
        container_height = self.content_rect.height * 0.65
        
        # Create container for the comparison
        comparison_rect = pygame.Rect(
            self.content_rect.centerx - container_width // 2,
            self.content_rect.centery - container_height // 2 + self.percent_y(0.05),
            container_width,
            container_height
        )
        
        # Draw background for comparison area with subtle gradient effect
        # Create a gradient surface
        gradient = pygame.Surface((comparison_rect.width, comparison_rect.height))
        for y in range(comparison_rect.height):
            # Create a subtle gradient from top to bottom
            alpha = 50 + int(y * 0.15)  # Gradually increase darkness
            gradient.fill((25, 35, 55))
            pygame.draw.line(gradient, (25, 35, 55, alpha), 
                            (0, y), (comparison_rect.width, y))
        
        # Apply the gradient with transparency
        self.screen.blit(gradient, comparison_rect)
        
        # Draw border for comparison area
        pygame.draw.rect(self.screen, self.DARK_BLUE, comparison_rect, 2)  # Blue border
        
        # Draw dividing line between original and modified patterns
        divider_x = comparison_rect.centerx
        pygame.draw.line(
            self.screen,
            self.GRAY,
            (divider_x, comparison_rect.top + 40),
            (divider_x, comparison_rect.bottom - 20),
            2
        )
        
        # Calculate positions for side-by-side display
        center_y = comparison_rect.centery + self.percent_y(0.02)
        spacing = container_width * 0.25  # Space between the two patterns
        
        # Draw original pattern on the left
        title_original = "Original Pattern:"
        title_original_surface = self.regular_font.render(title_original, True, self.ACCENT)  # Accent color
        title_original_rect = title_original_surface.get_rect(center=(comparison_rect.centerx - spacing, comparison_rect.top + 20))
        self.screen.blit(title_original_surface, title_original_rect)
        
        # Draw blue oval for original pattern
        if original_pattern:
            # Draw the pattern first to get dimensions
            orig_dimensions = self._draw_symbol_pattern(
                {'symbols': original_pattern}, 
                position=(comparison_rect.centerx - spacing, center_y),
                compact=True,
                phase="memorize"  # Use memorize styling with white text
            )
            
            # Draw blue oval based on text dimensions
            oval_width = orig_dimensions['width'] * 1.3
            oval_height = orig_dimensions['height'] * 1.8
            
            # Draw blue oval (slightly transparent)
            oval_surface = pygame.Surface((oval_width, oval_height), pygame.SRCALPHA)
            pygame.draw.ellipse(
                oval_surface,
                (80, 140, 255, 128),  # Light blue color with alpha
                pygame.Rect(0, 0, oval_width, oval_height),
                3  # Line width
            )
            oval_rect = oval_surface.get_rect(center=(comparison_rect.centerx - spacing, center_y))
            self.screen.blit(oval_surface, oval_rect)
        
        # Draw modified pattern on the right
        title_modified = "Shown Pattern:"
        title_modified_surface = self.regular_font.render(title_modified, True, self.GRAY_LIGHT)  # Light gray
        title_modified_rect = title_modified_surface.get_rect(center=(comparison_rect.centerx + spacing, comparison_rect.top + 20))
        self.screen.blit(title_modified_surface, title_modified_rect)
        
        # Draw gray oval for modified pattern
        if modified_pattern:
            # Draw the pattern first to get dimensions
            mod_dimensions = self._draw_symbol_pattern(
                {'symbols': modified_pattern}, 
                position=(comparison_rect.centerx + spacing, center_y),
                compact=True,
                phase="question"  # Use question styling with light gray text
            )
            
            # Draw gray oval based on text dimensions
            oval_width = mod_dimensions['width'] * 1.3
            oval_height = mod_dimensions['height'] * 1.8
            
            # Draw gray oval (slightly transparent)
            oval_surface = pygame.Surface((oval_width, oval_height), pygame.SRCALPHA)
            pygame.draw.ellipse(
                oval_surface,
                (140, 140, 160, 128),  # Light gray color with alpha
                pygame.Rect(0, 0, oval_width, oval_height),
                3  # Line width
            )
            oval_rect = oval_surface.get_rect(center=(comparison_rect.centerx + spacing, center_y))
            self.screen.blit(oval_surface, oval_rect)
        
        # Highlight the differences if we know which symbols were modified
        if 'modified_indices' in state and was_modified:
            modified_indices = state.get('modified_indices', [])
            self._highlight_string_differences(
                "".join(original_pattern), 
                "".join(modified_pattern), 
                comparison_rect.centerx - spacing,
                comparison_rect.centerx + spacing, 
                center_y,
                modified_indices
            )
        
        # Draw level stats if available
        if 'correct_count' in state and 'total_count' in state:
            stats_text = f"Level progress: {state['correct_count']}/{state['total_count']} correct"
            stats_surface = self.small_font.render(stats_text, True, self.TEXT_SECONDARY)
            stats_rect = stats_surface.get_rect(center=(self.content_rect.centerx, comparison_rect.bottom + self.percent_y(0.03)))
            self.screen.blit(stats_surface, stats_rect)
            
        # Add a continue prompt
        continue_text = "Click CONTINUE to proceed"
        continue_surface = self.small_font.render(continue_text, True, self.ACCENT)
        continue_rect = continue_surface.get_rect(center=(self.content_rect.centerx, comparison_rect.bottom + self.percent_y(0.08)))
        self.screen.blit(continue_surface, continue_rect)
        
        # Ensure the continue button is visible
        continue_button = next((b for b in self.buttons if b['action'] == 'continue'), None)
        if continue_button:
            continue_button['visible'] = True
    
    def _highlight_string_differences(self, original_str, modified_str, left_x, right_x, center_y, modified_indices):
        """Highlight differences between the original and modified strings.
        
        Args:
            original_str: Original string
            modified_str: Modified string
            left_x: X center position of the original string
            right_x: X center position of the modified string
            center_y: Y center position of both strings
            modified_indices: List of indices that were modified
        """
        if not modified_indices or not original_str or not modified_str:
            return
        
        # Create a custom font to match the compact string display
        font_size = self.percent_y(0.05)  # 5% of screen height for compact view
        try:
            font = pygame.font.SysFont('Arial', int(font_size), bold=True)
        except:
            font = self.title_font
        
        # Get the size of a single character (approximation)
        sample = font.render("X", True, self.TEXT_PRIMARY)
        char_width = sample.get_width()
        
        # Draw a connecting line between changed characters
        for index in modified_indices:
            if index < len(original_str) and index < len(modified_str):
                # Draw a red outline around the modified character in the modified string
                # First, render the entire string up to this character to find position
                if index > 0:
                    prefix = modified_str[:index]
                    prefix_surface = font.render(prefix, True, self.TEXT_PRIMARY)
                    prefix_width = prefix_surface.get_width()
                else:
                    prefix_width = 0
                
                # Get the width of the current character
                char = modified_str[index]
                char_surface = font.render(char, True, self.TEXT_PRIMARY)
                current_width = char_surface.get_width()
                
                # Calculate the positions
                orig_char_center_x = left_x - (font.render(original_str, True, self.TEXT_PRIMARY).get_width() / 2) + prefix_width + (current_width / 2)
                mod_char_center_x = right_x - (font.render(modified_str, True, self.TEXT_PRIMARY).get_width() / 2) + prefix_width + (current_width / 2)
                
                # Draw red outline around the modified character
                mod_char_rect = pygame.Rect(
                    mod_char_center_x - (current_width / 2) - 2,
                    center_y - (char_surface.get_height() / 2) - 2,
                    current_width + 4,
                    char_surface.get_height() + 4
                )
                pygame.draw.rect(self.screen, self.RED, mod_char_rect, 2)
                
                # Draw a dashed connecting line between the original and modified character
                dash_length = 5
                space_length = 3
                distance = mod_char_center_x - orig_char_center_x
                
                # Calculate number of dashes needed
                num_dashes = int(distance / (dash_length + space_length))
                
                for i in range(num_dashes):
                    start_x = orig_char_center_x + i * (dash_length + space_length)
                    end_x = start_x + dash_length
                    
                    # Ensure we don't exceed the distance
                    end_x = min(end_x, mod_char_center_x)
                    
                    if start_x < end_x:
                        pygame.draw.line(
                            self.screen,
                            self.RED,
                            (start_x, center_y),
                            (end_x, center_y),
                            1
                        )
    
    def _draw_symbol_pattern(self, state, position=None, compact=False, phase=None):
        """Draw a pattern of symbols as a simple string.
        
        Args:
            state: The state containing the symbols to draw
            position: Optional (x, y) position to center the pattern
            compact: If True, use a slightly smaller font
            phase: Optional current phase ("memorize", "question", or None for default)
        """
        symbols = state.get('symbols', [])
        if not symbols:
            return
        
        # Join symbols into a single string
        symbol_string = "".join(symbols)
        
        # Determine center position
        if position:
            center_x, center_y = position
        else:
            center_x = self.content_rect.centerx
            center_y = self.content_rect.centery
        
        # Determine colors based on phase
        if phase == "memorize":
            text_color = self.TEXT_HIGHLIGHT  # Pure white for memorize phase
            highlight_intensity = 255  # Full brightness
        elif phase == "question":
            text_color = self.TEXT_SECONDARY  # Light gray for question phase
            highlight_intensity = 200  # Slightly dimmed
        else:
            text_color = self.TEXT_PRIMARY  # Standard text color for other phases
            highlight_intensity = 220  # Near full brightness
        
        # Set font size based on compactness and screen size
        if compact:
            font_size = self.percent_y(0.05)  # 5% of screen height for compact view
        else:
            font_size = self.percent_y(0.08)  # 8% of screen height for normal view
        
        # Create a custom font of appropriate size
        try:
            font = pygame.font.SysFont('Arial', int(font_size), bold=True)
        except:
            # Fallback to the regular font if custom size is not available
            font = self.title_font
        
        # Draw symbol text with a glow effect for better visibility on dark background
        if phase == "memorize":
            # Add a subtle glow for better contrast
            # Create multiple layers with decreasing opacity for a glow effect
            for offset in [3, 2, 1]:
                glow_surface = font.render(symbol_string, True, (100, 160, 255, 50))
                glow_rect = glow_surface.get_rect(center=(center_x, center_y))
                glow_rect.inflate_ip(offset*2, offset*2)  # Make the rect slightly larger
                self.screen.blit(glow_surface, glow_rect)
        
        # Draw the symbol string
        symbol_surface = font.render(symbol_string, True, text_color)
        symbol_rect = symbol_surface.get_rect(center=(center_x, center_y))
        self.screen.blit(symbol_surface, symbol_rect)
        
        # Return the dimensions of the rendered text for reference (e.g., for the oval)
        width, height = symbol_surface.get_size()
        return {'width': width, 'height': height}
    
    def _draw_phase_indicator(self, phase_text, color):
        """Draw a phase indicator at the top of the content area."""
        # Draw phase text
        indicator_surface = self.regular_font.render(phase_text, True, color)
        indicator_rect = indicator_surface.get_rect(center=(self.content_rect.centerx, self.content_rect.top + self.percent_y(0.03)))
        self.screen.blit(indicator_surface, indicator_rect)
        
        # Create a more attractive underline with gradient
        underline_surface = pygame.Surface((indicator_rect.width + 10, 3), pygame.SRCALPHA)
        for x in range(underline_surface.get_width()):
            # Create a gradient that's brighter in the middle
            distance = abs(x - underline_surface.get_width() / 2)
            max_distance = underline_surface.get_width() / 2
            intensity = 1 - (distance / max_distance) * 0.5  # Fade to 50% at edges
            
            r, g, b = color
            pygame.draw.line(
                underline_surface,
                (r, g, b, int(255 * intensity)),
                (x, 0),
                (x, 2),
                1
            )
        
        # Position and draw the underline
        underline_rect = underline_surface.get_rect(centerx=indicator_rect.centerx, top=indicator_rect.bottom + 2)
        self.screen.blit(underline_surface, underline_rect) 