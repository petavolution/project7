#!/usr/bin/env python3
"""
Specialized renderer for the Quantum Memory module.

This renderer extends the enhanced generic renderer with specialized
visualization for the Quantum Memory training module, which enhances
working memory, cognitive flexibility, and strategic thinking.
"""

import pygame
import logging
import math
import random
from typing import Dict, Any, List, Tuple, Optional
from pygame import gfxdraw

# Import the enhanced generic renderer
from .enhanced_generic_renderer import EnhancedGenericRenderer

logger = logging.getLogger(__name__)

class QuantumMemoryRenderer(EnhancedGenericRenderer):
    """Specialized renderer for the Quantum Memory module."""
    
    def __init__(self, screen, module_id="quantum_memory", config=None, colors=None, fonts=None, width=None, height=None):
        """Initialize the Quantum Memory renderer.
        
        Args:
            screen: Pygame screen surface
            module_id: ID of the module (default: 'quantum_memory')
            config: Optional configuration dictionary
            colors: Optional color scheme dictionary
            fonts: Optional fonts dictionary
            width: Optional screen width
            height: Optional screen height
        """
        # Call parent constructor
        super().__init__(screen, module_id, config, colors, fonts, width, height)
        
        # Apply Quantum Memory specific colors
        self._apply_quantum_memory_colors()
        
        # Initialize quantum state animations
        self.animations = {}
        self.particle_systems = {}
        self.time_elapsed = 0
        self.last_update = pygame.time.get_ticks()
        
        # UI elements
        self.picker_dialog = None
        self.picker_selections = []
        
        # Cache for rendered symbols to improve performance
        self.symbol_cache = {}
        
    def _apply_quantum_memory_colors(self):
        """Apply color scheme specific to Quantum Memory module."""
        quantum_colors = {
            'quantum_bg': (5, 8, 20),  # Very dark blue background for quantum visualization
            'quantum_grid': (15, 25, 40),  # Slightly lighter blue for grid
            'quantum_box': (30, 40, 60),  # Box background
            'quantum_box_border': (60, 80, 120),  # Box border
            'quantum_symbol': (100, 160, 240),  # Bright blue for symbols
            'quantum_entangled': (180, 120, 240),  # Purple for entangled states
            'quantum_highlight': (140, 200, 255, 180),  # Highlight for selected states
            'quantum_particle': (160, 220, 255, 200),  # Bright particles
            'quantum_correct': (80, 220, 120),  # Green for correct selections
            'quantum_incorrect': (220, 80, 80),  # Red for incorrect selections
            'picker_bg': (20, 30, 50, 230),  # Semi-transparent picker background
            'picker_border': (60, 100, 160),  # Picker border
            'picker_selected': (80, 140, 220),  # Selected item in picker
            'picker_hover': (60, 120, 200),  # Hover state in picker
        }
        
        # Update the colors dictionary
        self.colors.update(quantum_colors)
        
        # Store these colors for future reference
        self.quantum_memory_colors = quantum_colors
    
    def render(self, state):
        """Render the Quantum Memory module based on its state.
        
        Args:
            state: Current module state containing the quantum memory information
                  
        Returns:
            List of rendered components for potential interaction
        """
        # Update time for animations
        current_time = pygame.time.get_ticks()
        delta_time = (current_time - self.last_update) / 1000.0  # Convert to seconds
        self.time_elapsed += delta_time
        self.last_update = current_time
        
        # Clear the screen with the background color
        self.screen.fill(self.colors['quantum_bg'])
        
        # Set up layout if not already done
        if not self.layout:
            self._setup_layout()
        
        # Apply module-specific colors
        self._apply_quantum_memory_colors()
        
        # Extract state information
        phase = state.get('phase', 'preparation')
        level = state.get('level', 1)
        score = state.get('score', 0)
        message = state.get('message', '')
        quantum_states = state.get('quantum_states', [])
        user_selections = state.get('user_selections', {})
        
        # Render all the standard components
        components = state.get('components', [])
        self._render_components(components)
        
        # Render quantum states based on phase
        self._render_quantum_states(quantum_states, phase, user_selections)
        
        # Render picker dialog if active
        if self.picker_dialog:
            self._render_picker_dialog()
        
        # Return interactive components for potential interaction
        interactives = self._create_interactive_components(quantum_states, phase)
        
        # Add picker dialog interactions if open
        if self.picker_dialog:
            interactives.extend(self._create_picker_interactives())
        
        return interactives
    
    def _render_quantum_states(self, states, phase, user_selections):
        """Render quantum states based on the current phase.
        
        Args:
            states: List of quantum state dictionaries
            phase: Current phase of the game
            user_selections: Dictionary of user selections
        """
        # Update animations for states
        self._update_state_animations(states, phase)
        
        # Render each state
        for state in states:
            state_id = state.get('id', 0)
            position = state.get('position', (0, 0))
            state_type = state.get('type', 'empty')
            
            # Get animation parameters
            animation = self.animations.get(state_id, {})
            pulse = animation.get('pulse', 0)
            rotation = animation.get('rotation', 0)
            
            # Base box size
            box_size = 60
            
            # Draw base box
            box_rect = pygame.Rect(
                position[0] - box_size // 2,
                position[1] - box_size // 2,
                box_size,
                box_size
            )
            
            # Check if entangled
            entangled_with = state.get('entangled_with')
            is_entangled = entangled_with is not None
            
            # Determine box color based on state and phase
            if state_type == 'feedback':
                # In feedback phase, color based on correctness
                if state.get('correct', False):
                    box_color = self.colors['quantum_correct']
                    border_color = self.colors['quantum_correct']
                else:
                    box_color = self.colors['quantum_incorrect']
                    border_color = self.colors['quantum_incorrect']
            elif is_entangled and phase == 'memorize':
                # Entangled state in memorize phase
                box_color = self.colors['quantum_box']
                border_color = self.colors['quantum_entangled']
            else:
                # Default colors
                box_color = self.colors['quantum_box']
                border_color = self.colors['quantum_box_border']
            
            # Draw box with pulse effect
            if phase in ['memorize', 'recall'] and (is_entangled or state_type == 'superposition'):
                pulse_size = box_size + int(pulse * 12)
                pulse_rect = pygame.Rect(
                    position[0] - pulse_size // 2,
                    position[1] - pulse_size // 2,
                    pulse_size,
                    pulse_size
                )
                pygame.draw.rect(
                    self.screen,
                    border_color,
                    pulse_rect,
                    2,
                    border_radius=4
                )
            
            # Draw main box
            pygame.draw.rect(
                self.screen,
                box_color,
                box_rect,
                0,
                border_radius=3
            )
            
            # Draw border
            pygame.draw.rect(
                self.screen,
                border_color,
                box_rect,
                2,
                border_radius=3
            )
            
            # Draw content based on state type
            if state_type == 'superposition':
                # Draw superposition symbols
                self._draw_superposition(state, box_rect, rotation)
                
                # Draw entanglement line if entangled
                if is_entangled is not None:
                    self._draw_entanglement(state, states)
            
            elif state_type == 'unknown':
                # Draw question mark for unknown state
                font = self.fonts.get('large', self.fonts['large'])
                text = font.render('?', True, self.colors['quantum_symbol'])
                text_rect = text.get_rect(center=position)
                self.screen.blit(text, text_rect)
                
                # Highlight if selected
                if state.get('selected', False):
                    pygame.draw.rect(
                        self.screen,
                        self.colors['quantum_highlight'],
                        box_rect,
                        0,
                        border_radius=3
                    )
            
            elif state_type in ['collapsed', 'feedback']:
                # Draw observed value
                observed = state.get('observed_value', '?')
                font = self.fonts.get('large', self.fonts['large'])
                text = font.render(observed, True, self.colors['quantum_symbol'])
                text_rect = text.get_rect(center=position)
                self.screen.blit(text, text_rect)
                
                # Draw entanglement line if entangled
                if is_entangled is not None:
                    self._draw_entanglement(state, states)
    
    def _draw_superposition(self, state, box_rect, rotation):
        """Draw superposition symbols for a quantum state.
        
        Args:
            state: Quantum state dictionary
            box_rect: Rectangle for the state box
            rotation: Current rotation angle for animation
        """
        # Get superposition symbols
        symbols = state.get('superposition', [])
        if not symbols:
            return
            
        # Calculate positions around a circle
        center = (box_rect.centerx, box_rect.centery)
        radius = min(box_rect.width, box_rect.height) * 0.3
        
        # Draw each symbol in the superposition
        for i, symbol in enumerate(symbols):
            # Calculate position on a circle with current rotation
            angle = (i / len(symbols) * 2 * math.pi) + rotation
            x = center[0] + math.cos(angle) * radius
            y = center[1] + math.sin(angle) * radius
            
            # Draw symbol
            font = self.fonts.get('medium', self.fonts['medium'])
            
            # Check symbol cache first for performance
            cache_key = f"{symbol}_{font}"
            if cache_key not in self.symbol_cache:
                text = font.render(symbol, True, self.colors['quantum_symbol'])
                self.symbol_cache[cache_key] = text
            else:
                text = self.symbol_cache[cache_key]
                
            text_rect = text.get_rect(center=(x, y))
            self.screen.blit(text, text_rect)
    
    def _draw_entanglement(self, state, all_states):
        """Draw entanglement line between entangled states.
        
        Args:
            state: Current quantum state
            all_states: List of all quantum states
        """
        entangled_with = state.get('entangled_with')
        if entangled_with is None:
            return
            
        # Find the entangled state
        for other_state in all_states:
            if other_state.get('id') == entangled_with:
                # Draw line between the two states
                start_pos = state.get('position', (0, 0))
                end_pos = other_state.get('position', (0, 0))
                
                # Calculate normal vector for wavy line
                dx = end_pos[0] - start_pos[0]
                dy = end_pos[1] - start_pos[1]
                length = math.sqrt(dx*dx + dy*dy)
                if length < 1:
                    return
                    
                nx = -dy / length * 8  # Normal vector x (perpendicular)
                ny = dx / length * 8   # Normal vector y (perpendicular)
                
                # Draw wavy entanglement line
                points = []
                segments = 12
                
                for i in range(segments + 1):
                    t = i / segments
                    x = start_pos[0] + dx * t
                    y = start_pos[1] + dy * t
                    
                    # Add wave effect
                    wave = math.sin(t * math.pi * 4 + self.time_elapsed * 3) * 0.5
                    x += nx * wave
                    y += ny * wave
                    
                    points.append((x, y))
                
                # Draw line segments
                if len(points) >= 2:
                    for i in range(len(points) - 1):
                        pygame.draw.line(
                            self.screen,
                            self.colors['quantum_entangled'],
                            points[i],
                            points[i+1],
                            2
                        )
                break
    
    def _update_state_animations(self, states, phase):
        """Update animations for quantum states.
        
        Args:
            states: List of quantum state dictionaries
            phase: Current phase of the game
        """
        # Update existing animations
        for state_id, animation in list(self.animations.items()):
            # Update pulse animation
            animation['pulse'] = (math.sin(self.time_elapsed * 3 + state_id * 0.5) + 1) * 0.5
            
            # Update rotation animation
            if phase == 'memorize':
                # Rotate faster in memorize phase
                animation['rotation'] += 0.02
            else:
                animation['rotation'] += 0.005
        
        # Initialize animations for new states
        for state in states:
            state_id = state.get('id', 0)
            if state_id not in self.animations:
                self.animations[state_id] = {
                    'pulse': 0,
                    'rotation': random.random() * math.pi * 2,  # Random initial rotation
                    'particles': []
                }
        
        # Remove animations for states that no longer exist
        existing_ids = [state.get('id') for state in states]
        for state_id in list(self.animations.keys()):
            if state_id not in existing_ids:
                del self.animations[state_id]
    
    def _create_interactive_components(self, states, phase):
        """Create interactive components for the quantum states.
        
        Args:
            states: List of quantum state dictionaries
            phase: Current phase of the game
            
        Returns:
            List of interactive components
        """
        interactive_components = []
        
        # Only create interactive components in recall phase
        if phase != 'recall':
            return interactive_components
        
        # Add interactive quantum states
        for state in states:
            state_id = state.get('id', 0)
            position = state.get('position', (0, 0))
            
            # Only make non-collapsed states interactive
            if state.get('type') == 'unknown' and not state.get('collapsed', False):
                interactive_components.append({
                    'type': 'circle',
                    'id': f'quantum_state_{state_id}',
                    'position': position,
                    'radius': 30,  # Half of box size
                    'action': 'select_quantum_state',
                    'data': {'state_id': state_id}
                })
        
        return interactive_components
    
    def _create_picker_interactives(self):
        """Create interactive components for the picker dialog.
        
        Returns:
            List of interactive components for the picker
        """
        if not self.picker_dialog:
            return []
            
        interactive_components = []
        
        # Add interactive elements for each choice
        choices = self.picker_dialog.get('choices', [])
        for i, choice in enumerate(choices):
            rect = choice.get('rect')
            
            interactive_components.append({
                'type': 'rectangle',
                'id': f'picker_choice_{i}',
                'rect': rect,
                'action': 'select_quantum_value',
                'data': {
                    'state_id': self.picker_dialog.get('state_id'),
                    'choice_index': i,
                    'choice_value': choice.get('value')
                }
            })
        
        # Add submit button
        submit_button = self.picker_dialog.get('submit_button')
        if submit_button:
            interactive_components.append({
                'type': 'rectangle',
                'id': 'picker_submit',
                'rect': submit_button.get('rect'),
                'action': 'submit_quantum_selection',
                'data': {
                    'state_id': self.picker_dialog.get('state_id')
                }
            })
        
        # Add cancel/close button
        close_button = self.picker_dialog.get('close_button')
        if close_button:
            interactive_components.append({
                'type': 'rectangle',
                'id': 'picker_close',
                'rect': close_button.get('rect'),
                'action': 'close_quantum_picker',
                'data': {}
            })
            
        return interactive_components
    
    def _render_picker_dialog(self):
        """Render the picker dialog for selecting quantum state values."""
        if not self.picker_dialog:
            return
            
        # Get dialog properties
        rect = self.picker_dialog.get('rect')
        state_id = self.picker_dialog.get('state_id')
        choices = self.picker_dialog.get('choices', [])
        
        # Draw dialog background with semi-transparency
        dialog_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        pygame.draw.rect(
            dialog_surface,
            self.colors['picker_bg'],
            pygame.Rect(0, 0, rect.width, rect.height),
            0,
            border_radius=8
        )
        
        # Draw dialog border
        pygame.draw.rect(
            dialog_surface,
            self.colors['picker_border'],
            pygame.Rect(0, 0, rect.width, rect.height),
            2,
            border_radius=8
        )
        
        # Draw dialog title
        font = self.fonts.get('medium', self.fonts['medium'])
        title = f"Select Quantum Value{' (multiple allowed)' if self.picker_dialog.get('multiple', False) else ''}"
        title_surf = font.render(title, True, self.colors['text'])
        title_rect = title_surf.get_rect(centerx=rect.width//2, top=15)
        dialog_surface.blit(title_surf, title_rect)
        
        # Draw choices
        for i, choice in enumerate(choices):
            choice_rect = pygame.Rect(choice.get('rect'))
            # Convert to local coordinates
            choice_rect.x -= rect.x
            choice_rect.y -= rect.y
            
            # Determine color based on selection state
            if choice.get('selected', False):
                color = self.colors['picker_selected']
            elif choice.get('hover', False):
                color = self.colors['picker_hover']
            else:
                color = self.colors['quantum_box']
            
            # Draw choice box
            pygame.draw.rect(
                dialog_surface,
                color,
                choice_rect,
                0,
                border_radius=4
            )
            
            # Draw choice border
            pygame.draw.rect(
                dialog_surface,
                self.colors['picker_border'],
                choice_rect,
                1,
                border_radius=4
            )
            
            # Draw choice symbol
            symbol = choice.get('value', '?')
            symbol_surf = font.render(symbol, True, self.colors['quantum_symbol'])
            symbol_rect = symbol_surf.get_rect(center=choice_rect.center)
            dialog_surface.blit(symbol_surf, symbol_rect)
        
        # Draw submit button
        submit_button = self.picker_dialog.get('submit_button')
        if submit_button:
            button_rect = pygame.Rect(submit_button.get('rect'))
            # Convert to local coordinates
            button_rect.x -= rect.x
            button_rect.y -= rect.y
            
            # Determine color based on hover state
            if submit_button.get('hover', False):
                color = self.colors['picker_hover']
            else:
                color = self.colors['button']
            
            # Draw button
            pygame.draw.rect(
                dialog_surface,
                color,
                button_rect,
                0,
                border_radius=4
            )
            
            # Draw button text
            button_text = 'Submit'
            button_surf = font.render(button_text, True, self.colors['button_text'])
            button_text_rect = button_surf.get_rect(center=button_rect.center)
            dialog_surface.blit(button_surf, button_text_rect)
        
        # Draw close button
        close_button = self.picker_dialog.get('close_button')
        if close_button:
            button_rect = pygame.Rect(close_button.get('rect'))
            # Convert to local coordinates
            button_rect.x -= rect.x
            button_rect.y -= rect.y
            
            # Determine color based on hover state
            if close_button.get('hover', False):
                color = self.colors['picker_hover']
            else:
                color = self.colors['button']
            
            # Draw button
            pygame.draw.rect(
                dialog_surface,
                color,
                button_rect,
                0,
                border_radius=4
            )
            
            # Draw button text
            button_text = 'Cancel'
            button_surf = font.render(button_text, True, self.colors['button_text'])
            button_text_rect = button_surf.get_rect(center=button_rect.center)
            dialog_surface.blit(button_surf, button_text_rect)
        
        # Draw dialog to screen
        self.screen.blit(dialog_surface, rect)
    
    def show_quantum_picker(self, state_id, superposition_count, position=None):
        """Show the quantum state value picker dialog.
        
        Args:
            state_id: ID of the quantum state to pick values for
            superposition_count: Number of superposition states to show
            position: Optional position override (default: center of screen)
        """
        # Set up dialog with default position
        if position is None:
            position = (self.width // 2, self.height // 2)
        
        # Calculate dialog size based on number of choices
        dialog_width = min(400, max(200, superposition_count * 50 + 60))
        dialog_height = 250
        
        # Create dialog rectangle
        dialog_rect = pygame.Rect(
            position[0] - dialog_width // 2,
            position[1] - dialog_height // 2,
            dialog_width,
            dialog_height
        )
        
        # Generate choices
        quantum_symbols = ["⟲", "⟳", "↑", "↓", "↔", "↕", "⊕", "⊗", "⊙", "△", "▽", "□", "◇", "○", "●", "★"]
        choices = []
        
        # Calculate grid dimensions
        cols = min(4, superposition_count)
        rows = (superposition_count + cols - 1) // cols
        
        # Calculate choice size
        choice_width = (dialog_width - 40) // cols
        choice_height = choice_width
        
        # Generate choices in a grid
        for i in range(superposition_count):
            row = i // cols
            col = i % cols
            
            x = dialog_rect.x + 20 + col * choice_width
            y = dialog_rect.y + 60 + row * choice_height
            
            # Use the same symbols as the module
            if i < len(quantum_symbols):
                value = quantum_symbols[i]
            else:
                value = str(i)
                
            choices.append({
                'rect': pygame.Rect(x, y, choice_width - 10, choice_height - 10),
                'value': value,
                'selected': False,
                'hover': False
            })
        
        # Create submit button
        submit_button = {
            'rect': pygame.Rect(
                dialog_rect.x + dialog_width // 2 - 80,
                dialog_rect.y + dialog_height - 50,
                70,
                30
            ),
            'hover': False
        }
        
        # Create close button
        close_button = {
            'rect': pygame.Rect(
                dialog_rect.x + dialog_width // 2 + 10,
                dialog_rect.y + dialog_height - 50,
                70,
                30
            ),
            'hover': False
        }
        
        # Save dialog
        self.picker_dialog = {
            'rect': dialog_rect,
            'state_id': state_id,
            'choices': choices,
            'multiple': True,  # Allow multiple selections
            'submit_button': submit_button,
            'close_button': close_button
        }
        
        # Reset selections
        self.picker_selections = []
    
    def handle_picker_selection(self, choice_index):
        """Handle selection in the quantum picker dialog.
        
        Args:
            choice_index: Index of the selected choice
            
        Returns:
            True if selection was handled, False otherwise
        """
        if not self.picker_dialog:
            return False
            
        choices = self.picker_dialog.get('choices', [])
        if choice_index < 0 or choice_index >= len(choices):
            return False
            
        # Toggle selection
        choice = choices[choice_index]
        choice['selected'] = not choice['selected']
        
        # Update selection list
        value = choice.get('value')
        if choice['selected']:
            if value not in self.picker_selections:
                self.picker_selections.append(value)
        else:
            if value in self.picker_selections:
                self.picker_selections.remove(value)
                
        return True
    
    def get_picker_selections(self):
        """Get the currently selected values from the picker.
        
        Returns:
            List of selected value indices
        """
        if not self.picker_dialog:
            return []
            
        selected_indices = []
        for i, choice in enumerate(self.picker_dialog.get('choices', [])):
            if choice.get('selected', False):
                selected_indices.append(i)
                
        return selected_indices
    
    def close_picker(self):
        """Close the quantum picker dialog."""
        self.picker_dialog = None
        self.picker_selections = []
    
    def update_button_hover(self, mouse_pos):
        """Update hover state for buttons in the picker dialog.
        
        Args:
            mouse_pos: Current mouse position
            
        Returns:
            True if any button hover state changed, False otherwise
        """
        if not self.picker_dialog:
            return False
            
        changed = False
        
        # Update choices hover state
        for choice in self.picker_dialog.get('choices', []):
            rect = choice.get('rect')
            was_hover = choice.get('hover', False)
            is_hover = rect.collidepoint(mouse_pos)
            
            if was_hover != is_hover:
                choice['hover'] = is_hover
                changed = True
        
        # Update submit button hover state
        submit_button = self.picker_dialog.get('submit_button')
        if submit_button:
            rect = submit_button.get('rect')
            was_hover = submit_button.get('hover', False)
            is_hover = rect.collidepoint(mouse_pos)
            
            if was_hover != is_hover:
                submit_button['hover'] = is_hover
                changed = True
        
        # Update close button hover state
        close_button = self.picker_dialog.get('close_button')
        if close_button:
            rect = close_button.get('rect')
            was_hover = close_button.get('hover', False)
            is_hover = rect.collidepoint(mouse_pos)
            
            if was_hover != is_hover:
                close_button['hover'] = is_hover
                changed = True
                
        return changed 