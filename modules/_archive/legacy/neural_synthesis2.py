#!/usr/bin/env python3
"""
Neural Synthesis Module.

Cross-modal cognitive training that integrates visual and auditory patterns,
leveraging dynamic neural adaptation to optimize cognitive development.
"""

import random
import time
import numpy as np
from typing import Dict, List, Tuple, Any, Optional, Union, Callable
import logging
import pygame
from pygame import Surface, Rect
from enum import Enum

from MetaMindIQTrain.core.training_module import TrainingModule
from MetaMindIQTrain.core.components import (
    Component, Panel, Grid, TextDisplay, Button, ProgressBar
)
from MetaMindIQTrain.core.neural_patterns import (
    NeuralPattern, PatternType, PatternComplexity, DifficultyAxis, UserPerformanceModel
)

logger = logging.getLogger(__name__)

class TrainingPhase(Enum):
    """Training phases in the Neural Synthesis module."""
    PRESENTATION = "presentation"  # Pattern is presented to the user
    DELAY = "delay"                # Delay between presentation and recall
    RECALL = "recall"              # User is asked to recall the pattern
    FEEDBACK = "feedback"          # Feedback is given to the user
    REST = "rest"                  # Short rest between patterns
    COMPLETE = "complete"          # Training session complete

# Define colors for the module
COLORS = {
    'background': (240, 240, 245),
    'panel': (255, 255, 255),
    'text': (60, 60, 80),
    'highlight': (70, 130, 240),
    'success': (100, 200, 100),
    'error': (240, 90, 90),
    'neutral': (200, 200, 200),
    # Color palette for notes (aligned with musical notes C through B)
    'note_colors': [
        (255, 75, 75),    # C - Red
        (255, 165, 75),   # D - Orange
        (255, 225, 75),   # E - Yellow
        (125, 255, 75),   # F - Green
        (75, 175, 255),   # G - Light Blue
        (135, 75, 255),   # A - Purple
        (255, 75, 225)    # B - Pink
    ]
}

# Note frequencies (C4 through B4)
NOTE_FREQUENCIES = {
    'C': 261.63,
    'D': 293.66,
    'E': 329.63,
    'F': 349.23,
    'G': 392.00,
    'A': 440.00,
    'B': 493.88
}

class NeuralSynthesis2(TrainingModule):
    """Neural Synthesis training module for cross-modal cognitive training."""

    def __init__(self, **kwargs):
        """Initialize the Neural Synthesis module.
        
        Args:
            **kwargs: Additional arguments to pass to the TrainingModule constructor
        """
        super().__init__(**kwargs)
        
        # Session state
        self.state = {
            'phase': 'ready',  # ready, observation, reproduction, feedback, complete
            'current_pattern': None,
            'user_sequence': [],
            'score': 0,
            'level': 1,
            'max_level': 10,
            'round': 0,
            'max_rounds': 3,
            'accuracy': 0.0,
            'last_response_time': 0.0,
            'feedback_message': 'Press Start to begin training',
            'feedback_type': 'neutral'  # neutral, success, error
        }
        
        # Create neural pattern generator
        self.user_model = UserPerformanceModel()
        self.pattern_generator = NeuralPattern(
            pattern_type=PatternType.MULTIMODAL,
            user_model=self.user_model
        )
        
        # Component references
        self.pattern_grid = None
        self.feedback_text = None
        self.level_progress = None
        self.start_button = None
        self.reset_button = None
        
        # Set up UI
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the UI components."""
        # Override this method in the concrete implementation
        pass
    
    def start_session(self):
        """Start a training session."""
        self.state['phase'] = 'observation'
        self.state['round'] = 1
        self.state['score'] = 0
        self.state['feedback_message'] = 'Observe the pattern'
        self.generate_pattern()
    
    def reset_session(self):
        """Reset the training session."""
        self.state['phase'] = 'ready'
        self.state['round'] = 0
        self.state['score'] = 0
        self.state['feedback_message'] = 'Press Start to begin training'
        self.state['feedback_type'] = 'neutral'
    
    def generate_pattern(self):
        """Generate a new pattern based on the current level."""
        complexity = PatternComplexity.MEDIUM
        self.state['current_pattern'] = self.pattern_generator.generate(complexity=complexity)
    
    def process_user_input(self, input_data):
        """Process user input during reproduction phase."""
        if self.state['phase'] != 'reproduction':
            return
            
        # Add to user sequence
        self.state['user_sequence'].append(input_data)
        
        # Check if complete
        if len(self.state['user_sequence']) >= len(self.state['current_pattern']['sequence']):
            self.evaluate_performance()
    
    def evaluate_performance(self):
        """Evaluate user performance based on accuracy and reaction time."""
        # Calculate accuracy
        correct = 0
        pattern_seq = self.state['current_pattern']['sequence']
        user_seq = self.state['user_sequence']
        
        for i in range(min(len(pattern_seq), len(user_seq))):
            if pattern_seq[i] == user_seq[i]:
                correct += 1
                
        accuracy = correct / len(pattern_seq) if pattern_seq else 0
        
        # Update state
        self.state['accuracy'] = accuracy
        self.state['phase'] = 'feedback'
        
        if accuracy >= 0.8:
            self.state['score'] += 1
            self.state['feedback_message'] = 'Great job!'
            self.state['feedback_type'] = 'success'
        else:
            self.state['feedback_message'] = 'Try again!'
            self.state['feedback_type'] = 'error'
            
        # Update user model
        self.user_model.update(accuracy, time.time() - self.state['last_response_time'])
    
    def render(self, surface):
        """Render the module UI.
        
        Args:
            surface: The surface to render on
        """
        # Clear background
        surface.fill(COLORS['background'])
        
        # Render components
        for component in self.components:
            component.render(surface)
    
    def update(self, dt):
        """Update the module state.
        
        Args:
            dt: Time delta in seconds
        """
        # Handle phase transitions
        if self.state['phase'] == 'observation' and time.time() > self.state['last_response_time'] + 3.0:
            self.state['phase'] = 'reproduction'
            self.state['user_sequence'] = []
            self.state['last_response_time'] = time.time()
            self.state['feedback_message'] = 'Reproduce the pattern'
            
        elif self.state['phase'] == 'feedback' and time.time() > self.state['last_response_time'] + 2.0:
            self.state['round'] += 1
            if self.state['round'] > self.state['max_rounds']:
                self.state['phase'] = 'complete'
                self.state['feedback_message'] = 'Training complete!'
            else:
                self.state['phase'] = 'observation'
                self.state['feedback_message'] = 'Observe the pattern'
                self.generate_pattern()
            self.state['last_response_time'] = time.time()
    
    def handle_event(self, event):
        """Handle an event."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()
            self.handle_click(pos)
    
    def handle_click(self, pos):
        """Handle a mouse click at the given position."""
        # Check if any buttons were clicked
        for component in self.components:
            if isinstance(component, Button) and component.rect.collidepoint(pos):
                action = component.action
                if action == "start":
                    self.start_session()
                elif action == "reset":
                    self.reset_session()
                return
            
        # If in recall phase, check if grid was clicked
        if self.state['phase'] == 'reproduction' and hasattr(self, 'pattern_grid'):
            if self.pattern_grid.rect.collidepoint(pos):
                grid_pos = self.pattern_grid.get_cell_at_position(pos)
                if grid_pos:
                    self.process_user_input(grid_pos)

    def get_metrics(self):
        """Get module performance metrics.
        
        Returns:
            Dictionary of metrics
        """
        return {
            'score': self.state['score'],
            'level': self.state['level'],
            'accuracy': self.state['accuracy'],
            'rounds_completed': self.state['round'] - 1
        }
    
    def load_user_data(self, data):
        """Load user data from a saved state.
        
        Args:
            data: The saved user data
        """
        if 'user_model' in data:
            self.user_model = data['user_model']
        if 'level' in data:
            self.state['level'] = data['level']
    
    def save_user_data(self):
        """Save user data.
        
        Returns:
            Dictionary of user data to save
        """
        return {
            'user_model': self.user_model,
            'level': self.state['level'],
            'score': self.state['score']
        }

    def initialize(self) -> None:
        """Initialize the module."""
        super().initialize()
        self._reset_state()
        self._update_components_from_state()
        
        # Initialize audio if we're in pygame environment
        try:
            if pygame.mixer.get_init() is None:
                pygame.mixer.init(frequency=44100, size=-16, channels=1, buffer=512)
            self.audio_initialized = True
        except (ImportError, pygame.error):
            logger.warning("Failed to initialize pygame audio. Sound will be disabled.")
            self.audio_initialized = False
            self.sound_enabled = False
    
    def _update_observation_phase(self, current_time):
        """Update the observation phase state.
        
        Args:
            current_time: Current time in milliseconds
        """
        pattern = self.state['current_pattern']
        if pattern is None:
            self._start_next_pattern()
            return
        
        # Handle element display timing
        if not self.displaying_element:
            # Time to show the next element?
            element_interval = self.element_display_duration + self.inter_element_delay
            elapsed = current_time - self.pattern_start_time
            target_element = int(elapsed / element_interval)
            
            if target_element >= len(pattern['sequence']):
                # Finished showing all elements
                self._start_reproduction_phase()
                return
            
            if target_element > self.current_element_index:
                # Show the next element
                self.current_element_index = target_element
                visual_element, audio_element = pattern['sequence'][target_element]
                
                # Update grid
                grid = self.components['pattern_grid']
                grid.clear_active_cells()
                self._highlight_visual_element(visual_element)
                
                # Play sound
                self._play_note(audio_element)
                
                self.displaying_element = True
                self.element_display_time = current_time
        else:
            # Check if it's time to hide the current element
            if current_time - self.element_display_time >= self.element_display_duration:
                # Hide the element
                grid = self.components['pattern_grid']
                grid.clear_active_cells()
                self.displaying_element = False
    
    def _update_reproduction_phase(self, current_time):
        """Update the reproduction phase state.
        
        Args:
            current_time: Current time in milliseconds
        """
        # Check for timeout
        pattern = self.state['current_pattern']
        if pattern and 'display_time' in pattern:
            # Allow twice the original display time for reproduction
            timeout = self.reproduction_start_time + pattern['display_time'] * 2
            if current_time > timeout and len(self.state['user_sequence']) < len(pattern['sequence']):
                # Timeout - evaluate what they've done so far
                self._evaluate_performance()
        
        # Update countdown if needed
        remaining = max(0, timeout - current_time) if 'timeout' in locals() else 0
        remaining_seconds = int(remaining / 1000)
        if remaining_seconds != getattr(self, 'last_remaining_seconds', None):
            self.last_remaining_seconds = remaining_seconds
            if remaining_seconds <= 5:  # Only show countdown when ≤ 5 seconds remain
                self.components['feedback_text'].text = f"Reproduce the pattern... {remaining_seconds}s"
    
    def _start_next_pattern(self):
        """Generate and start the next multimodal pattern."""
        # Generate a pattern with appropriate difficulty
        complexity = {
            axis: PatternComplexity(self.metrics['current_difficulty'][axis.value]) 
            for axis in DifficultyAxis
        }
        pattern = self.pattern_generator.generate_pattern(complexity)
        
        # Store the current pattern
        self.state['current_pattern'] = pattern
        self.state['user_sequence'] = []
        
        # Update state
        self.state['phase'] = 'observation'
        self.state['feedback_message'] = 'Observe the pattern...'
        self.state['feedback_type'] = 'neutral'
        
        # Reset timing information
        current_time = pygame.time.get_ticks() if pygame is not None else int(time.time() * 1000)
        self.pattern_start_time = current_time
        self.current_element_index = -1  # Start before the first element
        self.displaying_element = False
        
        # Configure the grid based on the pattern
        self._configure_grid_for_pattern(pattern)
        
        # Update metrics
        self.metrics['total_patterns'] += 1
    
    def _start_reproduction_phase(self):
        """Start the reproduction phase."""
        # Update state
        self.state['phase'] = 'reproduction'
        self.state['feedback_message'] = 'Reproduce the pattern...'
        self.state['feedback_type'] = 'neutral'
        
        # Reset the grid for user input
        grid = self.components['pattern_grid']
        grid.clear_active_cells()
        
        # Reset timing information
        current_time = pygame.time.get_ticks() if pygame is not None else int(time.time() * 1000)
        self.reproduction_start_time = current_time
    
    def _configure_grid_for_pattern(self, pattern):
        """Configure the grid for the current pattern.
        
        Args:
            pattern: The pattern to configure the grid for
        """
        num_colors = pattern['num_visual_elements']
        seq_len = pattern['sequence_length']
        
        # Calculate grid dimensions to fit the elements
        grid_size = max(3, int(np.ceil(np.sqrt(num_colors))))
        
        # Update grid
        grid = self.components['pattern_grid']
        grid.rows = grid_size
        grid.columns = grid_size
        grid.clear_active_cells()
    
    def _highlight_visual_element(self, element_index):
        """Highlight a visual element in the grid.
        
        Args:
            element_index: Index of the element to highlight
        """
        # Convert the element index to grid coordinates
        grid = self.components['pattern_grid']
        num_cols = grid.columns
        row = element_index // num_cols
        col = element_index % num_cols
        
        # Highlight the cell
        if 0 <= row < grid.rows and 0 <= col < grid.columns:
            grid.set_active_cell(row, col)
            
            # Use color based on element index (mod 7 to match our 7 colors)
            color_index = element_index % len(COLORS['note_colors'])
            grid.active_color = COLORS['note_colors'][color_index]
    
    def _play_note(self, note):
        """Play a musical note.
        
        Args:
            note: The note to play (e.g., 'C', 'D', 'E', etc.)
        """
        if not self.sound_enabled or not self.audio_initialized:
            return
        
        try:
            # Get the frequency for the note
            freq = NOTE_FREQUENCIES.get(note, 440)  # Default to A
            
            # Generate a simple sine wave
            sample_rate = 44100
            duration = 0.3  # seconds
            samples = np.sin(2 * np.pi * np.arange(sample_rate * duration) * freq / sample_rate)
            samples = np.int16(samples * 32767 * 0.3)  # Convert to 16-bit int with volume adjustment
            
            # Create a pygame Sound object and play it
            sound = pygame.mixer.Sound(samples.tobytes())
            sound.play()
        except Exception as e:
            logger.error(f"Error playing sound: {e}")
            self.sound_enabled = False
    
    def get_state(self) -> Dict:
        """Get the current state of the module.
        
        Returns:
            The current state as a dictionary
        """
        return {
            'state': self.state,
            'metrics': self.metrics
        }
    
    def set_state(self, state: Dict) -> None:
        """Set the state of the module.
        
        Args:
            state: The state to set
        """
        if 'state' in state:
            self.state = state['state']
        if 'metrics' in state:
            self.metrics = state['metrics']
        
        self._update_components_from_state()
    
    @classmethod
    def get_module_info(cls) -> Dict:
        """Get module information.
        
        Returns:
            Module information as a dictionary
        """
        return {
            'id': 'neural_synthesis',
            'name': 'Neural Synthesis',
            'description': 'Cross-modal cognitive training integrating visual and auditory patterns',
            'thumbnail': 'neural_synthesis.png',
            'category': 'advanced_cognition',
            'difficulty': 'advanced',
            'skills': ['memory', 'pattern_recognition', 'auditory_processing', 'cross_modal_integration'],
            'duration': '10-15 min'
        }


def create_module(**kwargs) -> NeuralSynthesis2:
    """Create a new instance of the Neural Synthesis module.
    
    Args:
        **kwargs: Additional arguments to pass to the module constructor
        
    Returns:
        A new instance of the Neural Synthesis module
    """
    return NeuralSynthesis2(**kwargs)