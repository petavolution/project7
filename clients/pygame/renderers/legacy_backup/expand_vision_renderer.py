#!/usr/bin/env python3
"""
Expand Vision Renderer

This module provides a renderer for the ExpandVision module of MetaMindIQTrain.
It handles displaying and animating expanding ovals with numbers for peripheral
vision training.
"""

import pygame
import math
import random
import os
import time
from pygame import gfxdraw

from MetaMindIQTrain.clients.pygame.renderers.base_renderer import BaseRenderer
from MetaMindIQTrain.config import calculate_sizes

class ExpandVisionRenderer(BaseRenderer):
    """Renderer for the ExpandVision module."""
    
    def __init__(self, screen, title_font, regular_font, small_font):
        """Initialize the renderer with screen and fonts."""
        super().__init__(screen, title_font, regular_font, small_font)
        
        # Calculate sizes based on screen dimensions
        self.screen_width = self.screen.get_width()
        self.screen_height = self.screen.get_height()
        self.sizes = calculate_sizes(self.screen_width, self.screen_height)
        
        # Colors
        self.DARK_BLUE = (20, 60, 120)
        self.BLUE = (0, 120, 255)  # Oval color to match example
        self.LIGHT_BLUE = (100, 160, 255)
        self.GREEN = (50, 180, 50)
        self.RED = (255, 0, 0)  # Center dot color to match example
        self.GRAY = (200, 200, 200)
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.BG_COLOR = (40, 40, 60)  # Dark blue background like in example
        self.TEXT_COLOR = (220, 220, 220)  # Light gray text like in example
        
        # Oval settings
        self.max_oval_width = self.content_rect.width * 0.8
        self.max_oval_height = self.content_rect.height * 0.8
        self.focus_dot_radius = 3  # Match example: 3 pixels
        
        # Word list for center display
        self.wordlist = ["relaxing", "breathing", "focusing", "widening", 
                         "brain", "energy", "power", "vision"]
        self.current_word = random.choice(self.wordlist)
        self.word_display_chance = 0.2  # 20% chance to display word
        
        # Load the pentagram image
        self.pentagram_image = None
        self.load_pentagram_image()
        
        # Button dimensions based on screen size
        button_width = self.percent_x(0.15)  # 15% of screen width
        button_height = self.percent_y(0.06)  # 6% of screen height
        button_spacing = self.percent_x(0.05)  # 5% of screen width
        
        # Position buttons in the footer area
        footer_center_x = self.footer_rect.centerx
        footer_center_y = self.footer_rect.centery
        
        # Create buttons
        self.buttons = [
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
                'text_color': self.WHITE,
                'visible': True
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
                'text_color': self.WHITE,
                'visible': True
            },
            {
                'text': 'Advance Level',
                'action': 'advance_level',
                'rect': pygame.Rect(
                    footer_center_x + button_width + button_spacing * 2,
                    footer_center_y - button_height // 2,
                    button_width,
                    button_height
                ),
                'color': self.DARK_BLUE,
                'hover_color': self.LIGHT_BLUE,
                'text_color': self.WHITE,
                'visible': True
            }
        ]
    
    def load_pentagram_image(self):
        """Load the pentagram image used for focus."""
        try:
            # Try different possible paths for the pentagram image
            possible_paths = [
                "MetaMindIQTrain/assets/pentagram.png",
                "MetaMindIQTrain/assets/pentagram.svg",
                "assets/pentagram.png",
                "assets/pentagram.svg"
            ]
            
            for path in possible_paths:
                if os.path.exists(path):
                    self.pentagram_image = pygame.image.load(path)
                    # Scale the image to a reasonable size (80x80 to match example)
                    self.pentagram_image = pygame.transform.scale(
                        self.pentagram_image, 
                        (80, 80)
                    )
                    return
            
            # If no image is found, create a fallback pentagram
            self._create_fallback_pentagram()
                
        except Exception as e:
            print(f"Error loading pentagram image: {e}")
            self._create_fallback_pentagram()
    
    def _create_fallback_pentagram(self):
        """Create a fallback pentagram if image loading fails."""
        # Create a surface for the pentagram (80x80 to match example)
        size = 80
        self.pentagram_image = pygame.Surface((size, size), pygame.SRCALPHA)
        
        # Draw a simple pentagram
        radius = size // 2 - 5
        center = (size / 2, size / 2)
        points = []
        
        # Calculate the 5 outer points of a regular pentagram
        for i in range(5):
            # Calculate angle in radians (starts at top, moves clockwise)
            angle = (90 - i * 144) * math.pi / 180
            x = center[0] + radius * -1 * math.sin(angle)
            y = center[1] + radius * -1 * math.cos(angle)
            points.append((x, y))
        
        # Connect points in pentagram pattern (0->2->4->1->3->0)
        pentagram_indices = [0, 2, 4, 1, 3, 0]
        
        # Draw the pentagram
        pygame.draw.polygon(
            self.pentagram_image, 
            self.WHITE, 
            [points[i] for i in pentagram_indices], 
            2
        )
    
    def render(self, state):
        """Render the expand vision training module."""
        # Fill the screen with the dark background
        self.screen.fill(self.BG_COLOR)
        
        # Draw the standard layout
        self.draw_standard_layout(state)
        
        # Fill content area with specific background color
        pygame.draw.rect(self.screen, self.BG_COLOR, self.content_rect)
        
        # Get necessary data from state
        oval_width = state.get('circle_width', 30)  # Using legacy 'circle_width' for compatibility
        oval_height = state.get('circle_height', 30)  # Using legacy 'circle_height' for compatibility
        numbers = state.get('numbers', [])
        show_numbers = state.get('show_numbers', False)
        user_input = state.get('user_input', "")
        feedback = state.get('feedback', {})
        show_feedback = state.get('show_feedback', False)
        rounds = state.get('total_rounds', 0)
        level = state.get('level', 1)
        
        # Calculate center coordinates
        center_x = self.content_rect.centerx
        center_y = self.content_rect.centery
        
        # Get timing information
        current_time = pygame.time.get_ticks()
        phase_time = state.get('phase_transition_time', 0)
        display_delay = state.get('display_delay', 6000)
        
        # Calculate remaining time if in numbers phase
        remaining_time = 0
        if show_numbers and phase_time > 0:
            remaining_time = max(0, (phase_time + display_delay - current_time) // 1000)
        
        # Draw title
        title_text = "ExpandVision Training"
        title_surface = self.title_font.render(title_text, True, self.TEXT_COLOR)
        title_rect = title_surface.get_rect(center=(center_x, self.header_rect.centery))
        self.screen.blit(title_surface, title_rect)
        
        # Draw round information
        round_text = f"Round: {rounds}/{state.get('max_rounds', 25)}"
        round_surface = self.regular_font.render(round_text, True, self.TEXT_COLOR)
        round_rect = round_surface.get_rect(center=(center_x, self.content_rect.top + 30))
        self.screen.blit(round_surface, round_rect)
        
        # Draw level information
        level_text = f"Level: {level}"
        level_surface = self.small_font.render(level_text, True, self.TEXT_COLOR)
        level_rect = level_surface.get_rect(left=self.content_rect.left + 20, top=self.content_rect.top + 20)
        self.screen.blit(level_surface, level_rect)
        
        # Draw instructions, different based on phase
        if show_feedback:
            # Display feedback
            self._draw_feedback(feedback)
        else:
            # Draw current phase instructions
            instruction_text = ""
            if show_numbers:
                if rounds % 5 == 0:  # Every 5th round, prompt to calculate
                    instruction_text = "Calculate the sum of all numbers"
                else:
                    instruction_text = "Notice the numbers in your peripheral vision"
            else:
                instruction_text = "Focus on the center" if rounds < 5 else "Keep your focus on the center"
            
            instruction_surface = self.regular_font.render(instruction_text, True, self.TEXT_COLOR)
            instruction_rect = instruction_surface.get_rect(center=(center_x, self.content_rect.top + 70))
            self.screen.blit(instruction_surface, instruction_rect)
            
            # Draw expanding oval
            self._draw_oval(oval_width, oval_height)
            
            # Draw center content - either pentagram or random word
            should_show_word = state.get('show_word', False)
            
            if should_show_word:
                # Draw the central word
                word = state.get('current_word', random.choice(self.wordlist))
                word_surface = self.regular_font.render(word, True, self.TEXT_COLOR)
                word_rect = word_surface.get_rect(center=(center_x, center_y))
                self.screen.blit(word_surface, word_rect)
            else:
                # Draw pentagram image in center
                if self.pentagram_image:
                    pentagram_rect = self.pentagram_image.get_rect(center=(center_x, center_y))
                    self.screen.blit(self.pentagram_image, pentagram_rect)
            
            # Draw focus dot in center only when showing numbers (after warmup rounds)
            if rounds > 20:  # After warmup rounds
                pygame.draw.circle(
                    self.screen, 
                    self.RED, 
                    (center_x, center_y), 
                    self.focus_dot_radius,
                    0  # Filled circle
                )
                
                # Draw numbers if they should be visible
                if show_numbers and numbers:
                    self._draw_numbers(numbers, oval_width, oval_height)
                    
                    # Show remaining time
                    if remaining_time > 0:
                        time_text = f"Time: {remaining_time}s"
                        time_surface = self.small_font.render(time_text, True, self.TEXT_COLOR)
                        time_rect = time_surface.get_rect(center=(center_x, self.content_rect.bottom - 30))
                        self.screen.blit(time_surface, time_rect)
                    
                    # In every 5th round, show the sum after 3 seconds
                    if rounds % 5 == 0 and current_time - phase_time > 3000:
                        sum_value = sum(numbers)
                        sum_text = f"Sum: {sum_value}"
                        sum_surface = self.regular_font.render(sum_text, True, self.TEXT_COLOR)
                        sum_rect = sum_surface.get_rect(center=(center_x, self.content_rect.bottom - 60))
                        self.screen.blit(sum_surface, sum_rect)
            
            # Draw user input if available
            if user_input:
                self._draw_user_input(user_input)
        
        # Draw the navigation buttons
        # No need to call a separate method - the buttons are drawn by the base renderer

    def _draw_oval(self, width, height):
        """Draw the expanding oval."""
        # Scale dimensions based on content area
        scaled_width = int(width * self.max_oval_width / 300)  # Assuming max width would be around 300
        scaled_height = int(height * self.max_oval_height / 300)  # Assuming max height would be around 300
        
        # Create oval rect
        oval_rect = pygame.Rect(
            self.content_rect.centerx - scaled_width // 2,
            self.content_rect.centery - scaled_height // 2,
            scaled_width,
            scaled_height
        )
        
        # Draw oval outline - blue like in the example
        pygame.draw.ellipse(
            self.screen, 
            self.BLUE, 
            oval_rect,
            2  # Line thickness
        )
    
    def _draw_numbers(self, numbers, oval_width, oval_height):
        """Draw numbers around the expanding oval."""
        # Center coordinates
        center_x = self.content_rect.centerx
        center_y = self.content_rect.centery
        
        # Scale dimensions based on content area
        scaled_width = int(oval_width * self.max_oval_width / 300)
        scaled_height = int(oval_height * self.max_oval_height / 300)
        
        # Position four numbers around the oval exactly like in the example
        number_positions = [
            # (x, y, horizontal_align)
            (center_x - scaled_width // 2 - 20, center_y - scaled_height // 2 - 10, 'right'),  # Left-top
            (center_x + scaled_width // 2 + 20, center_y - scaled_height // 2 - 10, 'left'),   # Right-top
            (center_x - scaled_width // 2 - 20, center_y + scaled_height // 2 + 10, 'right'),  # Left-bottom
            (center_x + scaled_width // 2 + 20, center_y + scaled_height // 2 + 10, 'left')    # Right-bottom
        ]
        
        # Draw each number
        for i, num in enumerate(numbers):
            if i < len(number_positions):
                x, y, align = number_positions[i]
                
                # Draw number
                num_surface = self.regular_font.render(str(num), True, self.TEXT_COLOR)
                
                # Adjust position based on alignment
                if align == 'right':
                    num_rect = num_surface.get_rect(right=x, centery=y)
                else:  # 'left'
                    num_rect = num_surface.get_rect(left=x, centery=y)
                
                self.screen.blit(num_surface, num_rect)
    
    def _draw_user_input(self, user_input):
        """Draw the user's input at the bottom of the content area."""
        # Draw input prompt
        prompt_text = "Enter sum: "
        prompt_surface = self.regular_font.render(prompt_text, True, self.TEXT_COLOR)
        input_surface = self.regular_font.render(user_input, True, self.TEXT_COLOR)
        
        # Calculate positions
        prompt_width = prompt_surface.get_width()
        total_width = prompt_width + input_surface.get_width()
        
        prompt_x = self.content_rect.centerx - total_width/2
        input_x = prompt_x + prompt_width
        y = self.content_rect.bottom - self.percent_y(0.08)
        
        # Draw text
        self.screen.blit(prompt_surface, (prompt_x, y - prompt_surface.get_height()/2))
        self.screen.blit(input_surface, (input_x, y - input_surface.get_height()/2))
        
        # Draw cursor blink
        cursor_x = input_x + input_surface.get_width() + 2
        cursor_height = input_surface.get_height()
        
        # Blink cursor based on current time
        if pygame.time.get_ticks() % 1000 < 500:  # Blink every half second
            pygame.draw.line(
                self.screen,
                self.TEXT_COLOR,
                (cursor_x, y - cursor_height/2),
                (cursor_x, y + cursor_height/2),
                2
            )
    
    def _draw_feedback(self, feedback):
        """Draw feedback about the user's answer."""
        # Get feedback data
        correct = feedback.get('correct', False)
        user_sum = feedback.get('user_sum', 0)
        actual_sum = feedback.get('actual_sum', 0)
        numbers = feedback.get('numbers', [])
        
        # Determine feedback text and color
        if correct:
            result_text = "Correct!"
            result_color = self.GREEN
        else:
            result_text = "Incorrect"
            result_color = self.RED
        
        # Draw main result
        result_surface = self.title_font.render(result_text, True, result_color)
        result_rect = result_surface.get_rect(center=(self.content_rect.centerx, self.content_rect.top + self.percent_y(0.15)))
        self.screen.blit(result_surface, result_rect)
        
        # Draw details
        details_text = f"Your answer: {user_sum}"
        details_surface = self.regular_font.render(details_text, True, self.TEXT_COLOR)
        details_rect = details_surface.get_rect(center=(self.content_rect.centerx, self.content_rect.top + self.percent_y(0.25)))
        self.screen.blit(details_surface, details_rect)
        
        if not correct:
            correct_text = f"Correct answer: {actual_sum}"
            correct_surface = self.regular_font.render(correct_text, True, self.TEXT_COLOR)
            correct_rect = correct_surface.get_rect(center=(self.content_rect.centerx, self.content_rect.top + self.percent_y(0.32)))
            self.screen.blit(correct_surface, correct_rect)
        
        # Draw the numbers used
        if numbers:
            numbers_text = "Numbers: " + ", ".join(str(n) for n in numbers)
            numbers_surface = self.regular_font.render(numbers_text, True, self.TEXT_COLOR)
            numbers_rect = numbers_surface.get_rect(center=(self.content_rect.centerx, self.content_rect.top + self.percent_y(0.40)))
            self.screen.blit(numbers_surface, numbers_rect)
            
            # Show the calculation
            calc_text = " + ".join(str(n) for n in numbers) + f" = {actual_sum}"
            calc_surface = self.regular_font.render(calc_text, True, self.TEXT_COLOR)
            calc_rect = calc_surface.get_rect(center=(self.content_rect.centerx, self.content_rect.top + self.percent_y(0.48)))
            self.screen.blit(calc_surface, calc_rect)
            
        # Add instructions to continue
        continue_text = "Press any key to continue"
        continue_surface = self.small_font.render(continue_text, True, self.TEXT_COLOR)
        continue_rect = continue_surface.get_rect(center=(self.content_rect.centerx, self.content_rect.bottom - self.percent_y(0.10)))
        self.screen.blit(continue_surface, continue_rect) 