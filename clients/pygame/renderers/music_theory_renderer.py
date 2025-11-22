#!/usr/bin/env python3
"""
Music Theory Renderer

This module provides a specialized renderer for the Music Theory training module.
It handles the display of musical challenges, playback controls, and user interface
for answering challenges.
"""

import pygame
import math
import time
import random
from typing import Dict, Any, List, Tuple
import numpy as np

# Import base renderer
try:
    from .music_components_renderer import MusicComponentsRenderer
except ImportError:
    # When running directly
    import sys
    from pathlib import Path
    project_root = Path(__file__).parents[3]
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    from MetaMindIQTrain.clients.pygame.renderers.music_components_renderer import MusicComponentsRenderer


class MusicTheoryRenderer(MusicComponentsRenderer):
    """Specialized renderer for the Music Theory module."""
    
    def __init__(self, screen, session_manager, module, config=None):
        """Initialize the renderer with screen and optional configuration."""
        super().__init__(screen, session_manager, module, config)
        
        # Module-specific colors
        self.colors.update({
            'bg': (30, 30, 40),
            'header': (40, 40, 60),
            'highlight': (100, 120, 220),
            'button': (60, 70, 100),
            'button_hover': (80, 90, 130),
            'button_active': (100, 110, 150),
            'button_text': (230, 230, 240),
            'option': (50, 60, 90),
            'option_hover': (70, 80, 110),
            'option_selected': (90, 100, 170),
        })
        
        # UI state
        self.state = {}
        self.selected_option = None
        self.hover_option = None
        self.hover_play_button = False
        
        # Audio visualization
        self.audio_playing = False
        self.audio_start_time = 0
        self.audio_duration = 0  # In seconds
        self.audio_visualization = []
        
        # Animation settings
        self.animation_time = 0
        self.feedback_animation = 0
    
    def register_module_specific_achievements(self):
        """Register music theory specific achievements."""
        # Register module-specific achievements
        # (these will be checked in the MusicComponentsRenderer)
        pass
    
    def render(self):
        """Render the current state of the Music Theory module."""
        if not hasattr(self.module, 'state'):
            return super().render()
            
        # Store the state for event handling
        self.state = self.module.state
        
        # Get screen dimensions
        width, height = self.screen.get_size()
        
        # Clear screen
        self.screen.fill(self.colors['bg'])
        
        # Draw header
        pygame.draw.rect(self.screen, self.colors['header'], 
                         (0, 0, width, 80))
        
        # Draw title
        title_text = f"Music Theory Training - Level {self.state.get('level', 1)}"
        title_surface = self.title_font.render(title_text, True, self.colors['text'])
        self.screen.blit(title_surface, (width // 2 - title_surface.get_width() // 2, 20))
        
        # Draw score
        score_text = f"Score: {self.state.get('score', 0)}"
        score_surface = self.small_font.render(score_text, True, self.colors['text'])
        self.screen.blit(score_surface, (width - score_surface.get_width() - 20, 20))
        
        # Draw progress
        progress_text = f"Challenge: {self.state.get('current_level_challenges', 0)}/{self.state.get('challenges_per_level', 10)}"
        progress_surface = self.small_font.render(progress_text, True, self.colors['text'])
        self.screen.blit(progress_surface, (20, 20))
        
        # Draw audio control/visualization
        self._draw_audio_section(width, height)
        
        # Draw challenge options
        self._draw_options(width, height)
        
        # Draw message
        self._draw_message(width, height)
        
        # Draw footer with instructions
        self._draw_footer(width, height)
        
        # Update animation timer
        self.animation_time += 0.02
        
        # Update audio visualization animation
        if self.audio_playing and time.time() - self.audio_start_time > self.audio_duration:
            self.audio_playing = False
        
        # Feedback animation
        if self.state.get('state') == 'feedback':
            self.feedback_animation = min(1.0, self.feedback_animation + 0.05)
        else:
            self.feedback_animation = max(0.0, self.feedback_animation - 0.05)
            
        # Render feedback and achievement notifications from base class
        self.render_feedback()
        self.render_achievement_notification()
    
    def _draw_audio_section(self, width, height):
        """Draw the audio playback control and visualization.
        
        Args:
            width: Screen width
            height: Screen height
        """
        # Draw audio control section background
        audio_section_rect = pygame.Rect(width // 2 - 150, 100, 300, 120)
        pygame.draw.rect(self.screen, self.colors['header'], audio_section_rect, 0, 10)
        
        # Draw play button
        play_button_rect = pygame.Rect(width // 2 - 40, 130, 80, 60)
        
        # Button color based on hover state
        button_color = self.colors['button_active'] if self.hover_play_button else self.colors['button']
        
        # Draw the button with rounded corners
        pygame.draw.rect(self.screen, button_color, play_button_rect, 0, 10)
        
        # Draw the play icon (triangle)
        play_icon_points = [
            (play_button_rect.left + 25, play_button_rect.top + 15),
            (play_button_rect.left + 25, play_button_rect.bottom - 15),
            (play_button_rect.right - 20, play_button_rect.centery)
        ]
        pygame.draw.polygon(self.screen, self.colors['button_text'], play_icon_points)
        
        # Draw "Play Audio" text
        play_text = self.note_font.render("Play Audio", True, self.colors['text'])
        self.screen.blit(play_text, (width // 2 - play_text.get_width() // 2, 200))
        
        # Audio visualization (waveform or spectrum)
        if self.audio_playing:
            # Number of bars in visualization
            num_bars = 20
            bar_width = 10
            bar_spacing = 5
            total_width = num_bars * (bar_width + bar_spacing) - bar_spacing
            
            # Calculate the starting position
            start_x = width // 2 - total_width // 2
            start_y = 240
            
            # Generate animation values based on time
            if not self.audio_visualization or len(self.audio_visualization) != num_bars:
                # Generate random heights for visualization bars
                self.audio_visualization = []
                challenge_type = self.state.get('challenge_type', '')
                
                if challenge_type == 'scales':
                    # Scales have multiple notes - create a pattern
                    for i in range(num_bars):
                        # Sine wave pattern with some randomness
                        height = 20 + 15 * math.sin(i / 2 + self.animation_time * 5) + random.randint(-5, 5)
                        self.audio_visualization.append(int(height))
                
                elif challenge_type == 'intervals':
                    # Intervals have two notes - create two clusters
                    for i in range(num_bars):
                        if i < num_bars // 2 - 2 or i > num_bars // 2 + 1:
                            height = random.randint(5, 15)
                        else:
                            height = random.randint(25, 35)
                        self.audio_visualization.append(height)
                
                elif challenge_type == 'chords':
                    # Chords have simultaneous notes - make bars more even
                    for i in range(num_bars):
                        height = 25 + random.randint(-5, 5)
                        self.audio_visualization.append(height)
            
            # Draw the bars
            for i in range(num_bars):
                bar_height = self.audio_visualization[i]
                
                # Animate the bars
                animated_height = bar_height * (0.7 + 0.3 * math.sin(self.animation_time * 10 + i / 2))
                
                # Calculate position
                x = start_x + i * (bar_width + bar_spacing)
                y = start_y
                
                # Draw the bar
                pygame.draw.rect(self.screen, self.colors['highlight'], 
                                (x, y, bar_width, animated_height))
    
    def _draw_options(self, width, height):
        """Draw the answer options for the challenge.
        
        Args:
            width: Screen width
            height: Screen height
        """
        if 'options' not in self.state:
            return
        
        options = self.state['options']
        
        # Calculate grid layout based on number of options
        num_options = len(options)
        rows = math.ceil(num_options / 2)
        
        # Option dimensions and spacing
        option_width = 300
        option_height = 60
        horizontal_spacing = 50
        vertical_spacing = 20
        
        # Calculate total grid dimensions
        grid_width = option_width * 2 + horizontal_spacing
        grid_height = rows * (option_height + vertical_spacing) - vertical_spacing
        
        # Calculate starting position (centered)
        start_x = width // 2 - grid_width // 2
        start_y = 300
        
        # Draw each option
        for i, option in enumerate(options):
            row = i // 2
            col = i % 2
            
            x = start_x + col * (option_width + horizontal_spacing)
            y = start_y + row * (option_height + vertical_spacing)
            
            # Determine option color based on state
            option_color = self.colors['option']
            
            # If this is the selected option
            if i == self.selected_option:
                option_color = self.colors['option_selected']
            # If this is the hovered option
            elif i == self.hover_option:
                option_color = self.colors['option_hover']
            
            # If in feedback state and this was the user's answer or correct answer
            if self.state.get('state') == 'feedback' and self.state.get('answered', False):
                if option == self.state.get('user_answer', ''):
                    # User's answer - red if wrong, green if correct
                    if option == self.state.get('correct_answer', ''):
                        option_color = self.colors['correct']
                    else:
                        option_color = self.colors['incorrect']
                elif option == self.state.get('correct_answer', ''):
                    # Highlight the correct answer
                    option_color = self.colors['correct']
            
            # Draw option box with rounded corners
            option_rect = pygame.Rect(x, y, option_width, option_height)
            pygame.draw.rect(self.screen, option_color, option_rect, 0, 10)
            
            # Draw option text
            option_text = self.note_font.render(option, True, self.colors['text'])
            text_x = x + option_width // 2 - option_text.get_width() // 2
            text_y = y + option_height // 2 - option_text.get_height() // 2
            self.screen.blit(option_text, (text_x, text_y))
    
    def _draw_message(self, width, height):
        """Draw feedback message.
        
        Args:
            width: Screen width
            height: Screen height
        """
        message = ""
        message_color = self.colors['text']
        
        # Determine message based on state
        if self.state.get('state') == 'intro':
            message = f"Level {self.state.get('level', 1)}: {self.state.get('challenge_type', 'Music Theory').capitalize()}"
        elif self.state.get('state') == 'challenge':
            message = self.state.get('challenge_text', 'Identify the musical element')
        elif self.state.get('state') == 'feedback':
            if self.state.get('answered', False) and self.state.get('is_correct', False):
                message = "Correct!"
                message_color = self.colors['correct']
            elif self.state.get('answered', False) and not self.state.get('is_correct', True):
                message = f"Incorrect. The answer was: {self.state.get('correct_answer', '')}"
                message_color = self.colors['incorrect']
        elif self.state.get('state') == 'level_complete':
            message = f"Level {self.state.get('level', 1)} Complete!"
        
        # Draw message if we have one
        if message:
            message_text = self.title_font.render(message, True, message_color)
            message_rect = pygame.Rect(
                width // 2 - 300, height // 2 - 150, 600, 60
            )
            
            # If we're in feedback state, apply animation
            if self.state.get('state') == 'feedback':
                # Scale based on animation progress
                scale = 1.0 + math.sin(self.feedback_animation * math.pi) * 0.1
                scaled_width = int(message_text.get_width() * scale)
                scaled_height = int(message_text.get_height() * scale)
                
                # Create scaled surface
                scaled_text = pygame.transform.scale(message_text, (scaled_width, scaled_height))
                
                # Position centered
                text_rect = scaled_text.get_rect(
                    center=(width // 2, message_rect.centery)
                )
                
                # Draw
                self.screen.blit(scaled_text, text_rect)
            else:
                # Normal drawing
                text_rect = message_text.get_rect(
                    center=(width // 2, message_rect.centery)
                )
                self.screen.blit(message_text, text_rect)
    
    def _draw_footer(self, width, height):
        """Draw footer with instructions.
        
        Args:
            width: Screen width
            height: Screen height
        """
        # Draw continue button in feedback state
        if self.state.get('state') == 'feedback':
            continue_rect = pygame.Rect(width // 2 - 100, height - 50, 200, 40)
            pygame.draw.rect(self.screen, self.colors['button'], continue_rect, 0, 5)
            
            continue_text = self.note_font.render("Continue", True, self.colors['button_text'])
            text_rect = continue_text.get_rect(center=continue_rect.center)
            self.screen.blit(continue_text, text_rect)
    
    def handle_event(self, event):
        """Handle PyGame events.
        
        Args:
            event: PyGame event object
            
        Returns:
            bool: True if the event was handled, False otherwise
        """
        # Get screen dimensions for hit testing
        width, height = self.screen.get_size()
        
        if event.type == pygame.MOUSEMOTION:
            # Update hover states
            mouse_x, mouse_y = event.pos
            
            # Check if hovering play button
            play_button_rect = pygame.Rect(width // 2 - 40, 130, 80, 60)
            self.hover_play_button = play_button_rect.collidepoint(mouse_x, mouse_y)
            
            # Check if hovering an option
            if 'state' in self.state and self.state['state'] == 'challenge' and 'options' in self.state:
                options = self.state['options']
                num_options = len(options)
                rows = math.ceil(num_options / 2)
                
                # Option dimensions and spacing
                option_width = 300
                option_height = 60
                horizontal_spacing = 50
                vertical_spacing = 20
                
                # Calculate grid dimensions
                grid_width = option_width * 2 + horizontal_spacing
                
                # Calculate starting position
                start_x = width // 2 - grid_width // 2
                start_y = 300
                
                # Check each option
                self.hover_option = None
                for i, option in enumerate(options):
                    row = i // 2
                    col = i % 2
                    
                    option_x = start_x + col * (option_width + horizontal_spacing)
                    option_y = start_y + row * (option_height + vertical_spacing)
                    
                    option_rect = pygame.Rect(option_x, option_y, option_width, option_height)
                    if option_rect.collidepoint(mouse_x, mouse_y):
                        self.hover_option = i
                        break
            
            return True
            
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button
                result = self._handle_click(event.pos)
                if result:
                    # Forward the input to the module
                    self.module.process_input(result)
                return True
                
        return super().handle_event(event)
    
    def _handle_click(self, pos: Tuple[int, int]) -> Dict[str, Any]:
        """Handle mouse click events, generating module input.
        
        Args:
            pos: Mouse position (x, y)
            
        Returns:
            Dict with module input or None if no input to send
        """
        x, y = pos
        width, height = self.screen.get_size()
        
        # Check if clicked play button
        play_button_rect = pygame.Rect(width // 2 - 40, 130, 80, 60)
        if play_button_rect.collidepoint(x, y):
            # Set audio playback animation state
            self.audio_playing = True
            self.audio_start_time = time.time()
            
            # Estimate duration based on challenge type
            challenge_type = self.state.get('challenge_type', '')
            if challenge_type == 'scales':
                self.audio_duration = 3.0  # Longer for melodies
            else:
                self.audio_duration = 2.0
            
            # Clear previous visualization
            self.audio_visualization = []
            
            # Return play audio action
            return {"action": "play_audio"}
        
        # Check if clicked an option
        if self.state.get('state') == 'challenge' and 'options' in self.state:
            options = self.state['options']
            num_options = len(options)
            rows = math.ceil(num_options / 2)
            
            # Option dimensions and spacing
            option_width = 300
            option_height = 60
            horizontal_spacing = 50
            vertical_spacing = 20
            
            # Calculate grid dimensions
            grid_width = option_width * 2 + horizontal_spacing
            
            # Calculate starting position
            start_x = width // 2 - grid_width // 2
            start_y = 300
            
            # Check each option
            for i, option in enumerate(options):
                row = i // 2
                col = i % 2
                
                option_x = start_x + col * (option_width + horizontal_spacing)
                option_y = start_y + row * (option_height + vertical_spacing)
                
                option_rect = pygame.Rect(option_x, option_y, option_width, option_height)
                if option_rect.collidepoint(x, y):
                    self.selected_option = i
                    
                    # Update the feedback message based on correctness
                    if option == self.state.get('correct_answer', ''):
                        self.show_feedback("Correct!", True)
                    else:
                        self.show_feedback(f"Incorrect. The answer was: {self.state.get('correct_answer', '')}", False)
                    
                    # Return the answer
                    return {"answer": option}
        
        # Check if clicked continue button
        if self.state.get('state') == 'feedback':
            continue_rect = pygame.Rect(width // 2 - 100, height - 50, 200, 40)
            if continue_rect.collidepoint(x, y):
                # Reset visualization
                self.audio_visualization = []
                
                # Reset feedback animation
                self.feedback_animation = 0
                
                # Return continue action
                return {"action": "continue"}
        
        return None

# Register renderer
def register_renderer():
    return {
        'id': 'music_theory',
        'renderer_class': MusicTheoryRenderer
    } 