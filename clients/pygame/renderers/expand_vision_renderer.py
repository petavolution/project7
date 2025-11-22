#!/usr/bin/env python3
"""
Specialized renderer for the Expand Vision module.

This renderer extends the enhanced generic renderer with specialized
visualization for the Expand Vision training module, supporting features
like preparation phase and dynamic number positioning.
"""

import pygame
import logging
import math
from typing import Dict, Any, List, Tuple, Optional

# Import the enhanced generic renderer
from .enhanced_generic_renderer import EnhancedGenericRenderer

logger = logging.getLogger(__name__)

class ExpandVisionRenderer(EnhancedGenericRenderer):
    """Specialized renderer for the Expand Vision module."""
    
    def __init__(self, screen, module_id="expand_vision", config=None, colors=None, fonts=None, width=None, height=None):
        """Initialize the Expand Vision renderer.
        
        Args:
            screen: Pygame screen surface
            module_id: ID of the module (default: 'expand_vision')
            config: Optional configuration dictionary
            colors: Optional color scheme dictionary
            fonts: Optional fonts dictionary
            width: Optional screen width
            height: Optional screen height
        """
        # Call parent constructor
        super().__init__(screen, module_id, config, colors, fonts, width, height)
        
        # Apply Expand Vision specific colors
        self._apply_expand_vision_colors()
        
        # Track animation time
        self.last_time = pygame.time.get_ticks()
        self.pulse_animation = 0  # 0-100 for pulsing effect
        self.pulse_direction = 1  # 1 for growing, -1 for shrinking
        
        # Cache for text surfaces
        self.text_cache = {}
        
        # Word list for central display (matches web implementation)
        self.word_list = [
            "relaxing", "breathing", "focusing", "widening", 
            "brain", "energy", "power", "vision"
        ]
        self.current_word_index = 0
        
    def _apply_expand_vision_colors(self):
        """Apply color scheme specific to Expand Vision module that matches web implementation."""
        vision_colors = {
            'vision_bg': (15, 20, 30),  # Darker background for better contrast
            'vision_circle': (0, 120, 255, 200),  # Blue circle matching web CSS var(--primary-color)
            'vision_circle_active': (0, 180, 100, 200),  # Green circle for active phase
            'vision_radius': (80, 100, 180, 100),  # Semi-transparent blue
            'number_default': (220, 220, 220),  # Top number - white (CSS: rgba(220, 220, 220, 1))
            'number_right': (255, 255, 120),  # Right number - yellow (CSS: rgba(255, 255, 120, 1))
            'number_bottom': (120, 255, 120),  # Bottom number - green (CSS: rgba(120, 255, 120, 1))
            'number_left': (120, 120, 255),  # Left number - blue (CSS: rgba(120, 120, 255, 1))
            'focus_point': (255, 0, 0),  # Red focus point (CSS: red)
            'preparation_text': (180, 220, 250),  # Light blue for preparation phase text
            'sum_prompt': (220, 220, 220),  # White text for sum prompt
            'sum_result': (100, 200, 100),  # Green text for sum result (CSS: var(--success-color))
            'phase_text': (180, 180, 180),  # Light gray text (CSS: var(--text-secondary))
        }
        
        # Update the colors dictionary
        self.colors.update(vision_colors)
        
        # Store these colors for future reference
        self.expand_vision_colors = vision_colors
    
    def render(self, state):
        """Render the Expand Vision module based on its state.
        
        Args:
            state: Current module state containing the circle dimensions,
                  phase information, and number positions
                  
        Returns:
            List of rendered components for potential interaction
        """
        # Clear the screen with the background color
        self.screen.fill(self.colors['vision_bg'])
        
        # Set up layout if not already done
        if not self.layout:
            self._setup_layout()
        
        # Apply module-specific colors
        self._apply_expand_vision_colors()
        
        # Get content area dimensions
        content_rect = self.layout.get('content_rect')
        if content_rect:
            content_width = content_rect.width
            content_height = content_rect.height
            center_x = content_rect.centerx
            center_y = content_rect.centery
        else:
            content_width = self.width * 0.8
            content_height = self.height * 0.8
            center_x = self.width // 2
            center_y = self.height // 2
        
        # Extract state information
        circle_width = state.get('circle_width', 30)
        circle_height = state.get('circle_height', 30)
        numbers = state.get('numbers', [])
        show_numbers = state.get('show_numbers', False)
        phase = state.get('phase', 'preparation')
        distance_factor_x = state.get('distance_factor_x', 0.15)
        distance_factor_y = state.get('distance_factor_y', 0.15)
        phase_message = state.get('message', 'Focus on the center')
        round_num = state.get('round', 0)
        total_rounds = state.get('total_rounds', 25)
        user_answer = state.get('user_answer', None)
        current_sum = state.get('current_sum', 0)
        
        # Update pulse animation for preparation phase
        if phase == 'preparation':
            # Calculate time delta
            current_time = pygame.time.get_ticks()
            dt = (current_time - self.last_time) / 1000.0  # Convert to seconds
            self.last_time = current_time
            
            # Update pulse animation (0-100)
            self.pulse_animation += self.pulse_direction * 50 * dt
            if self.pulse_animation > 100:
                self.pulse_animation = 100
                self.pulse_direction = -1
            elif self.pulse_animation < 0:
                self.pulse_animation = 0
                self.pulse_direction = 1
                
            # Apply pulse to circle size (5% variation)
            pulse_factor = 1.0 + (self.pulse_animation / 100.0) * 0.05
            circle_radius = min(circle_width, circle_height) // 2
            circle_radius = int(circle_radius * pulse_factor)
        else:
            circle_radius = min(circle_width, circle_height) // 2
        
        # Draw module title
        title_font = self.fonts['large']
        title_surf = title_font.render("Expand Vision Training", True, self.colors['text'])
        title_rect = title_surf.get_rect(centerx=center_x, top=20)
        self.screen.blit(title_surf, title_rect)
        
        # Draw round and time information
        stats_y = title_rect.bottom + 10
        round_font = self.fonts['medium']
        round_text = f"Round: {round_num}/{total_rounds}"
        round_surf = round_font.render(round_text, True, self.colors['text'])
        round_rect = round_surf.get_rect(centerx=center_x, top=stats_y)
        self.screen.blit(round_surf, round_rect)
        
        # Draw phase message (matches web CSS .phase-text)
        phase_font = self.fonts['medium']
        if phase == 'preparation':
            phase_text = 'Focus on the center'
        elif phase == 'active':
            phase_text = f"Round {round_num}: Calculate the numbers"
        elif phase == 'feedback':
            phase_text = "Calculating sum..."
        else:
            phase_text = phase_message
            
        phase_surf = phase_font.render(phase_text, True, self.colors['phase_text'])
        phase_rect = phase_surf.get_rect(centerx=center_x, top=round_rect.bottom + 15)
        self.screen.blit(phase_surf, phase_rect)
        
        # Calculate oval position (centered)
        oval_top = center_y - circle_radius
        oval_left = center_x - circle_radius
        oval_rect = pygame.Rect(oval_left, oval_top, circle_radius * 2, circle_radius * 2)
        
        # Draw expanding circle with glow effect (matches web CSS .oval)
        # Choose color based on phase like web implementation
        if phase == 'preparation':
            circle_color = self.colors['vision_circle']
            # Add glow effect matching CSS box-shadow
            # Draw multiple circles with decreasing opacity
            for i in range(5, 0, -1):
                glow_radius = circle_radius + i * 3
                glow_alpha = 80 - i * 15  # Decreasing alpha
                glow_surf = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
                pygame.draw.circle(
                    glow_surf,
                    (0, 120, 255, glow_alpha),  # Blue with alpha
                    (glow_radius, glow_radius),
                    glow_radius
                )
                glow_rect = glow_surf.get_rect(center=(center_x, center_y))
                self.screen.blit(glow_surf, glow_rect)
        else:
            circle_color = self.colors['vision_circle_active']
            # Add green glow for active phase
            for i in range(5, 0, -1):
                glow_radius = circle_radius + i * 3
                glow_alpha = 80 - i * 15  # Decreasing alpha
                glow_surf = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
                pygame.draw.circle(
                    glow_surf,
                    (0, 180, 100, glow_alpha),  # Green with alpha
                    (glow_radius, glow_radius),
                    glow_radius
                )
                glow_rect = glow_surf.get_rect(center=(center_x, center_y))
                self.screen.blit(glow_surf, glow_rect)
                
        # Draw the main circle (matches CSS .oval)
        pygame.draw.circle(
            self.screen,
            circle_color,
            (center_x, center_y),
            circle_radius,
            2  # Border width of 2px matching CSS border: 2px solid
        )
        
        # Draw focus point (red dot - matches CSS #focus-point)
        pygame.draw.circle(
            self.screen,
            self.colors['focus_point'],
            (center_x, center_y),
            3  # Matches CSS width: 6px (half for radius)
        )
        
        # Add central word if applicable (matches CSS #central-content)
        if phase == 'preparation':
            # Use the word_list like web implementation
            current_word = self.word_list[self.current_word_index % len(self.word_list)]
            word_font = self.fonts['medium']
            word_surf = word_font.render(current_word, True, self.colors['preparation_text'])
            word_rect = word_surf.get_rect(center=(center_x, center_y))
            self.screen.blit(word_surf, word_rect)
        
        # Add numbers if in active phase and showing numbers (matches CSS .peripheral-number)
        if show_numbers and numbers and len(numbers) >= 4:
            # Calculate dynamic positions based on distance factors - matches web updateNumberPositions()
            distance_x = content_width * distance_factor_x
            distance_y = content_height * distance_factor_y
            
            # Positions for the four numbers (top, right, bottom, left)
            # Matching the CSS positions with translateX/Y
            positions = [
                (center_x, center_y - distance_y),  # Top
                (center_x + distance_x, center_y),  # Right
                (center_x, center_y + distance_y),  # Bottom
                (center_x - distance_x, center_y)   # Left
            ]
            
            # Colors for each position - matching CSS
            number_colors = [
                self.colors['number_default'],  # Top
                self.colors['number_right'],    # Right
                self.colors['number_bottom'],   # Bottom
                self.colors['number_left']      # Left
            ]
            
            # Draw numbers with corresponding colors
            for i, num in enumerate(numbers[:4]):
                if i < len(positions):
                    num_font = self.fonts['large']
                    num_surf = num_font.render(str(num), True, number_colors[i])
                    num_rect = num_surf.get_rect(center=positions[i])
                    self.screen.blit(num_surf, num_rect)
        
        # Draw sum prompt if in answer phase (matches CSS .sum-container)
        if phase == 'answer':
            prompt_y = center_y + circle_radius + 50
            prompt_font = self.fonts['medium']
            prompt_surf = prompt_font.render("Calculate the sum of all numbers", True, self.colors['sum_prompt'])
            prompt_rect = prompt_surf.get_rect(centerx=center_x, top=prompt_y)
            self.screen.blit(prompt_surf, prompt_rect)
            
            # Draw possible answers as buttons (matching the web layout)
            button_height = int(self.height * 0.06)  # 6% of screen height
            button_width = int(self.width * 0.08)    # 8% of screen width
            button_spacing = int(self.width * 0.02)  # 2% of screen width
            
            # Define the possible answers (correct sum +/- offsets)
            possible_answers = [
                current_sum - 2,
                current_sum - 1,
                current_sum,
                current_sum + 1,
                current_sum + 2
            ]
            
            # Calculate button positions
            total_width = 5 * button_width + 4 * button_spacing
            start_x = (self.width - total_width) // 2
            button_y = prompt_rect.bottom + 20
            
            # Create interactive components list for possible clicks
            components = []
            
            # Draw each answer button
            for i, answer in enumerate(possible_answers):
                btn_x = start_x + i * (button_width + button_spacing)
                btn_rect = pygame.Rect(btn_x, button_y, button_width, button_height)
                
                # Highlight selected answer
                if user_answer == answer:
                    btn_color = self.colors['highlight']
                elif user_answer is not None and answer == current_sum:
                    btn_color = self.colors['success']
                else:
                    btn_color = self.colors['primary']
                
                # Draw button background
                pygame.draw.rect(
                    self.screen,
                    btn_color,
                    btn_rect,
                    border_radius=8
                )
                
                # Draw button text
                btn_font = self.fonts['medium']
                btn_surf = btn_font.render(str(answer), True, self.colors['text'])
                btn_text_rect = btn_surf.get_rect(center=btn_rect.center)
                self.screen.blit(btn_surf, btn_text_rect)
                
                # Add to interactive components
                components.append({
                    'type': 'button',
                    'rect': btn_rect,
                    'action': 'select_answer',
                    'value': answer
                })
            
            # Show feedback if answer has been selected
            if user_answer is not None:
                result_y = button_y + button_height + 20
                result_text = "Correct!" if user_answer == current_sum else f"Incorrect. The sum was {current_sum}."
                result_color = self.colors['success'] if user_answer == current_sum else self.colors['error']
                
                result_font = self.fonts['medium']
                result_surf = result_font.render(result_text, True, result_color)
                result_rect = result_surf.get_rect(centerx=center_x, top=result_y)
                self.screen.blit(result_surf, result_rect)
            
            # Return components for interaction
            return components
        
        # Draw controls hint - matching CSS .controls
        controls_font = self.fonts['small']
        controls_text = "Press SPACE to restart the exercise"
        controls_surf = controls_font.render(controls_text, True, (180, 180, 180, 180))
        controls_rect = controls_surf.get_rect(centerx=center_x, bottom=self.height - 20)
        self.screen.blit(controls_surf, controls_rect)
        
        # Return empty components list for non-answer phases
        return []
        
    def handle_event(self, event, state):
        """Handle pygame events.
        
        Args:
            event: Pygame event
            state: Current module state
            
        Returns:
            Action dictionary or None
        """
        # Handle keyboard events
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                # Restart exercise on space bar
                return {"action": "restart"}
                
        # Handle mouse clicks
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Get mouse position
            mouse_pos = pygame.mouse.get_pos()
            
            # Get components
            components = self.render(state)
            
            # Check for clicks on interactive components
            for component in components:
                if component['rect'].collidepoint(mouse_pos):
                    # Return action based on component
                    if component['action'] == 'select_answer':
                        return {
                            "action": "select_answer",
                            "value": component['value']
                        }
            
            # If no component was clicked and we're in active phase, switch to answer phase
            if state.get('phase') == 'active' and state.get('show_numbers', False):
                return {"action": "show_answer_input"}
                
        return None
    
def register_renderer():
    """Register the renderer with the system."""
    return {
        "id": "expand_vision",
        "name": "ExpandVision",
        "renderer_class": ExpandVisionRenderer,
        "description": "Specialized renderer for Expand Vision module"
    } 