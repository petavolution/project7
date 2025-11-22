#!/usr/bin/env python3
"""
Advanced Interactive Music Theory Module (MusicTheory3)

This module extends the EnhancedMusicTheoryModule with improved UI components and interactive elements:
- Interactive piano keyboard visualization with mouse/keyboard input
- Real-time visual and audio feedback synchronized with playback
- Comprehensive progress tracking system
- Dynamic difficulty adjustments based on user performance
- Pygame-based interactive UI components

The module focuses on strengthening the connection between visual and auditory processing
through synchronized multi-modal interactions.
"""

import random
import math
import time
import logging
import numpy as np
import pygame
from typing import Dict, Any, List, Tuple, Optional, Union
import sys
from pathlib import Path

# Import enhanced music theory module
try:
    from MetaMindIQTrain.modules.music.music_theory2 import EnhancedMusicTheoryModule
except ImportError:
    # When running directly
    import sys
    from pathlib import Path
    project_root = Path(__file__).parent.parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    from MetaMindIQTrain.modules.music.music_theory2 import EnhancedMusicTheoryModule

# Configure logging
logger = logging.getLogger(__name__)

class InteractiveMusicTheoryModule(EnhancedMusicTheoryModule):
    """
    Advanced Interactive Music Theory module with rich UI and real-time feedback.
    
    This module extends the EnhancedMusicTheoryModule with a responsive interactive UI:
    - Visual piano keyboard interface for direct interaction
    - Synchronized audio-visual feedback
    - Real-time performance feedback
    - Dynamic difficulty adjustments
    - Progress tracking visualization
    """
    
    def __init__(self):
        """Initialize the Interactive Music Theory module."""
        # Initialize base class
        super().__init__()
        
        # Override module metadata
        self.name = "Interactive Music Theory"
        self.description = "Advanced interactive music training with real-time feedback"
        self.category = "Music"
        self.difficulty = "Adaptive"
        
        # Initialize Pygame components if used in pygame mode
        self.pygame_initialized = False
        self.surface = None
        
        # Piano keyboard settings
        self.keyboard_config = {
            "octaves": 2,                  # Number of octaves to display
            "start_note": 48,              # MIDI note number (C3)
            "white_key_width": 40,         # Width of white keys
            "white_key_height": 150,       # Height of white keys
            "black_key_width": 24,         # Width of black keys
            "black_key_height": 90,        # Height of black keys
            "key_spacing": 2,              # Spacing between keys
            "highlight_duration": 1000,    # Duration of highlight in ms
        }
        
        # UI element colors
        self.colors = {
            "white_key": (255, 255, 255),
            "black_key": (0, 0, 0),
            "key_border": (100, 100, 100),
            "highlight": (255, 200, 0),    # Yellow highlight
            "correct": (100, 255, 100),    # Green for correct answers
            "incorrect": (255, 100, 100),  # Red for incorrect answers
            "text": (30, 30, 30),
            "background": (240, 240, 245),
            "progress_bar": (100, 149, 237), # Cornflower blue
            "button": (200, 200, 210),
            "button_hover": (180, 180, 190),
            "button_text": (30, 30, 30)
        }
        
        # Interactive elements
        self.buttons = []
        self.active_notes = []  # Currently highlighted/playing notes
        self.played_notes = []  # Notes played by user
        
        # Feedback timing
        self.last_feedback_time = 0
        self.feedback_message = ""
        self.feedback_color = self.colors["text"]
        
        # Progress tracking
        self.progress = {
            "total_questions": 0,
            "correct_answers": 0,
            "current_streak": 0,
            "best_streak": 0,
            "session_start_time": None,
            "response_times": [],
            "accuracy_by_type": {},
            "difficulty_adjustment_factor": 1.0  # Starts at normal difficulty
        }
        
        # Sound resources
        self.sounds = {}  # Will store pygame Sound objects

        # Keyboard mapping (for computer keyboard input)
        self.key_mapping = {
            pygame.K_a: 0,   # C
            pygame.K_w: 1,   # C#
            pygame.K_s: 2,   # D
            pygame.K_e: 3,   # D#
            pygame.K_d: 4,   # E
            pygame.K_f: 5,   # F
            pygame.K_t: 6,   # F#
            pygame.K_g: 7,   # G
            pygame.K_y: 8,   # G#
            pygame.K_h: 9,   # A
            pygame.K_u: 10,  # A#
            pygame.K_j: 11,  # B
            pygame.K_k: 12   # Higher C
        }
    
    def initialize_pygame(self, surface):
        """Initialize Pygame components."""
        self.pygame_initialized = True
        self.surface = surface
        
        # Initialize sounds if pygame mixer is available
        if pygame.mixer.get_init():
            self._initialize_sounds()
        else:
            logger.warning("Pygame mixer not initialized. Sound will not be available.")
        
        # Create UI elements
        self._create_ui_elements()
        
        # Start progress tracking
        self.progress["session_start_time"] = time.time()
    
    def _initialize_sounds(self):
        """Initialize sound resources for notes."""
        try:
            # Generate basic waveforms for each note
            # This creates simple sine wave tones for each note
            for note in range(36, 85):  # C2 to C6
                frequency = 440 * (2 ** ((note - 69) / 12))  # A4 (note 69) = 440Hz
                self._generate_note_sound(note, frequency)
                
            # Add effect sounds
            self.sounds["correct"] = self._generate_effect_sound("correct")
            self.sounds["incorrect"] = self._generate_effect_sound("incorrect")
            self.sounds["complete"] = self._generate_effect_sound("complete")
            
        except Exception as e:
            logger.error(f"Error initializing sounds: {e}")
    
    def _generate_note_sound(self, note, frequency):
        """Generate a sine wave sound for a note."""
        try:
            sample_rate = 44100
            duration = 1.0  # 1 second
            
            # Generate a sine wave
            samples = np.sin(2 * np.pi * np.arange(sample_rate * duration) * frequency / sample_rate)
            
            # Apply simple ADSR envelope
            attack = int(0.02 * sample_rate)
            decay = int(0.1 * sample_rate)
            sustain_level = 0.7
            release = int(0.3 * sample_rate)
            
            # Attack phase
            if attack > 0:
                samples[:attack] *= np.linspace(0, 1, attack)
            
            # Decay phase
            if decay > 0:
                samples[attack:attack+decay] *= np.linspace(1, sustain_level, decay)
            
            # Sustain phase
            samples[attack+decay:-release] *= sustain_level
            
            # Release phase
            if release > 0:
                samples[-release:] *= np.linspace(sustain_level, 0, release)
            
            # Convert to 16-bit PCM
            samples = (samples * 32767).astype(np.int16)
            
            # Create a pygame Sound object
            sound_buffer = pygame.sndarray.make_sound(samples)
            self.sounds[note] = sound_buffer
            
        except Exception as e:
            logger.error(f"Error generating note sound {note}: {e}")
    
    def _generate_effect_sound(self, effect_type):
        """Generate sound effects like correct/incorrect answer indicators."""
        try:
            sample_rate = 44100
            duration = 0.5  # 0.5 second
            
            if effect_type == "correct":
                # Major chord arpeggio
                samples = np.zeros(int(sample_rate * duration))
                frequencies = [440, 554.37, 659.25]  # A4, C#5, E5
                for i, freq in enumerate(frequencies):
                    start = int(i * sample_rate * 0.1)
                    end = int(sample_rate * duration)
                    t = np.arange(start, end)
                    chunk = np.sin(2 * np.pi * t * freq / sample_rate)
                    chunk *= np.exp(-(t - start) / (sample_rate * 0.2))  # Exponential decay
                    samples[start:end] += chunk[:end-start]
                
            elif effect_type == "incorrect":
                # Dissonant sound
                frequencies = [415.30, 440]  # G#4, A4 - dissonant interval
                samples = np.zeros(int(sample_rate * duration))
                for freq in frequencies:
                    t = np.arange(int(sample_rate * duration))
                    chunk = np.sin(2 * np.pi * t * freq / sample_rate)
                    chunk *= np.exp(-t / (sample_rate * 0.15))  # Quick decay
                    samples += chunk
                
            elif effect_type == "complete":
                # Rising pattern
                samples = np.zeros(int(sample_rate * duration))
                base_freq = 330  # E4
                for i in range(6):
                    start = int(i * sample_rate * 0.08)
                    end = int(sample_rate * duration)
                    freq = base_freq * (2 ** (i / 12))
                    t = np.arange(start, end)
                    chunk = np.sin(2 * np.pi * t * freq / sample_rate)
                    env = np.exp(-(t - start) / (sample_rate * 0.2))
                    chunk *= env[:end-start]
                    samples[start:end] += chunk[:end-start]
            
            # Normalize and convert to 16-bit PCM
            if np.max(np.abs(samples)) > 0:
                samples /= np.max(np.abs(samples))
            samples = (samples * 32767).astype(np.int16)
            
            # Create a pygame Sound object
            return pygame.sndarray.make_sound(samples)
            
        except Exception as e:
            logger.error(f"Error generating effect sound {effect_type}: {e}")
            return None
    
    def _create_ui_elements(self):
        """Create buttons and other UI elements."""
        # This will be populated based on the module's needs
        self.buttons = []
        
        # Example button definitions:
        if self.surface:
            width, height = self.surface.get_size()
            
            # Play button
            self.buttons.append({
                "id": "play",
                "rect": pygame.Rect(width - 120, 20, 100, 40),
                "text": "Play",
                "action": self.play_current_challenge
            })
            
            # Submit button
            self.buttons.append({
                "id": "submit",
                "rect": pygame.Rect(width - 120, 70, 100, 40),
                "text": "Submit",
                "action": self.submit_answer
            })
    
    def render(self, surface=None):
        """Render the module UI using pygame."""
        if surface:
            self.surface = surface
            
        if not self.pygame_initialized and self.surface:
            self.initialize_pygame(self.surface)
            
        if not self.surface:
            return
        
        # Clear the surface
        self.surface.fill(self.colors["background"])
        
        # Render piano keyboard
        self._render_piano_keyboard()
        
        # Render progress bar
        self._render_progress_bar()
        
        # Render feedback message
        self._render_feedback()
        
        # Render challenge information
        self._render_challenge_info()
        
        # Render buttons
        self._render_buttons()
        
        # Render visualizations if active
        if self.visual_modes.get("waveform", False):
            self._render_waveform()
            
        if self.visual_modes.get("circle_of_fifths", False):
            self._render_circle_of_fifths()
    
    def _render_piano_keyboard(self):
        """Render an interactive piano keyboard."""
        if not self.surface:
            return
            
        # Get keyboard config
        config = self.keyboard_config
        
        # Calculate keyboard position (centered horizontally)
        width, height = self.surface.get_size()
        keyboard_width = (config["white_key_width"] * 7 * config["octaves"]) + (config["key_spacing"] * 7 * config["octaves"])
        x_start = (width - keyboard_width) // 2
        y_start = height - config["white_key_height"] - 50  # 50px from bottom
        
        # Keep track of key positions for interaction
        self.key_positions = []
        
        # Draw white keys first
        white_keys_per_octave = 7  # C, D, E, F, G, A, B
        for octave in range(config["octaves"]):
            for i in range(white_keys_per_octave):
                x = x_start + (octave * 7 + i) * (config["white_key_width"] + config["key_spacing"])
                
                # Determine note number (MIDI)
                note_idx = [0, 2, 4, 5, 7, 9, 11][i]  # White key indices in an octave
                note = config["start_note"] + octave * 12 + note_idx
                
                # Determine if this key is active
                is_active = note in self.active_notes
                is_played = note in self.played_notes
                
                # Draw key
                key_color = self.colors["correct"] if is_played else (
                    self.colors["highlight"] if is_active else self.colors["white_key"])
                
                key_rect = pygame.Rect(x, y_start, config["white_key_width"], config["white_key_height"])
                pygame.draw.rect(self.surface, key_color, key_rect)
                pygame.draw.rect(self.surface, self.colors["key_border"], key_rect, 2)
                
                # Store key position
                self.key_positions.append({"rect": key_rect, "note": note})
                
                # Draw note name
                note_name = self._midi_to_note_name(note)
                font = pygame.font.Font(None, 18)
                text = font.render(note_name, True, self.colors["text"])
                text_rect = text.get_rect(center=(x + config["white_key_width"] // 2, 
                                                 y_start + config["white_key_height"] - 20))
                self.surface.blit(text, text_rect)
        
        # Draw black keys on top
        black_key_positions = [1, 3, 6, 8, 10]  # Indices of black keys in an octave (C#, D#, F#, G#, A#)
        for octave in range(config["octaves"]):
            for i in black_key_positions:
                # Find the corresponding white key to the left
                white_idx = (i // 2) + (1 if i > 5 else 0)
                x_white = x_start + (octave * 7 + white_idx) * (config["white_key_width"] + config["key_spacing"])
                
                # Position black key at right edge of white key
                x = x_white + config["white_key_width"] - config["black_key_width"] // 2
                
                # Determine note number
                note = config["start_note"] + octave * 12 + i
                
                # Determine if this key is active
                is_active = note in self.active_notes
                is_played = note in self.played_notes
                
                # Draw key
                key_color = self.colors["correct"] if is_played else (
                    self.colors["highlight"] if is_active else self.colors["black_key"])
                
                key_rect = pygame.Rect(x, y_start, config["black_key_width"], config["black_key_height"])
                pygame.draw.rect(self.surface, key_color, key_rect)
                pygame.draw.rect(self.surface, self.colors["key_border"], key_rect, 1)
                
                # Store key position
                self.key_positions.append({"rect": key_rect, "note": note})
    
    def _render_progress_bar(self):
        """Render the progress tracking bar."""
        if not self.surface:
            return
            
        width, height = self.surface.get_size()
        
        # Progress bar position and size
        bar_width = width - 60
        bar_height = 20
        x = 30
        y = 20
        
        # Calculate progress
        if self.progress["total_questions"] > 0:
            progress_ratio = self.progress["correct_answers"] / max(1, self.progress["total_questions"])
        else:
            progress_ratio = 0
            
        progress_width = int(bar_width * progress_ratio)
        
        # Draw background
        pygame.draw.rect(self.surface, (200, 200, 200), 
                         pygame.Rect(x, y, bar_width, bar_height))
        
        # Draw progress
        pygame.draw.rect(self.surface, self.colors["progress_bar"], 
                         pygame.Rect(x, y, progress_width, bar_height))
        
        # Draw border
        pygame.draw.rect(self.surface, (100, 100, 100), 
                         pygame.Rect(x, y, bar_width, bar_height), 1)
        
        # Draw progress text
        font = pygame.font.Font(None, 24)
        text = f"Score: {self.progress['correct_answers']}/{self.progress['total_questions']}"
        text_surf = font.render(text, True, (30, 30, 30))
        text_rect = text_surf.get_rect(center=(x + bar_width // 2, y + bar_height // 2))
        self.surface.blit(text_surf, text_rect)
        
        # Draw streak info
        streak_text = f"Streak: {self.progress['current_streak']} (Best: {self.progress['best_streak']})"
        streak_surf = font.render(streak_text, True, (30, 30, 30))
        self.surface.blit(streak_surf, (x, y + bar_height + 10))
    
    def _render_feedback(self):
        """Render feedback messages to the user."""
        if not self.surface or not self.feedback_message:
            return
            
        # Check if feedback should still be displayed
        current_time = time.time() * 1000  # Convert to ms
        if current_time - self.last_feedback_time > 3000:  # 3 seconds
            self.feedback_message = ""
            return
            
        # Render message
        font = pygame.font.Font(None, 32)
        text = font.render(self.feedback_message, True, self.feedback_color)
        
        # Position at center of screen
        width, height = self.surface.get_size()
        text_rect = text.get_rect(center=(width // 2, height // 3))
        
        # Draw with semi-transparent background
        padding = 10
        bg_rect = pygame.Rect(text_rect.x - padding, text_rect.y - padding, 
                             text_rect.width + 2 * padding, text_rect.height + 2 * padding)
        s = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
        s.fill((240, 240, 240, 200))
        self.surface.blit(s, bg_rect)
        
        # Draw text
        self.surface.blit(text, text_rect)
    
    def _render_challenge_info(self):
        """Render information about the current challenge."""
        if not self.surface:
            return
            
        # Render challenge type and description
        width, height = self.surface.get_size()
        font = pygame.font.Font(None, 28)
        
        # Challenge type
        challenge_text = f"Challenge: {self.current_challenge_type.replace('_', ' ').title()}"
        text = font.render(challenge_text, True, self.colors["text"])
        self.surface.blit(text, (50, 60))
        
        # Challenge description/instructions
        font_small = pygame.font.Font(None, 24)
        if hasattr(self, 'current_message') and self.current_message:
            lines = self._wrap_text(self.current_message, font_small, width - 100)
            for i, line in enumerate(lines):
                text = font_small.render(line, True, self.colors["text"])
                self.surface.blit(text, (50, 90 + i * 25))
    
    def _wrap_text(self, text, font, max_width):
        """Wrap text to fit within a specified width."""
        words = text.split(' ')
        lines = []
        current_line = []
        
        for word in words:
            # Try adding the word to the current line
            test_line = ' '.join(current_line + [word])
            test_width = font.size(test_line)[0]
            
            if test_width <= max_width:
                current_line.append(word)
            else:
                # Line is too long, start a new line
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        
        # Add the last line
        if current_line:
            lines.append(' '.join(current_line))
            
        return lines
    
    def _render_buttons(self):
        """Render interactive buttons."""
        if not self.surface:
            return
            
        for button in self.buttons:
            # Draw button background
            pygame.draw.rect(self.surface, self.colors["button"], button["rect"])
            pygame.draw.rect(self.surface, self.colors["key_border"], button["rect"], 2)
            
            # Draw button text
            font = pygame.font.Font(None, 24)
            text = font.render(button["text"], True, self.colors["button_text"])
            text_rect = text.get_rect(center=button["rect"].center)
            self.surface.blit(text, text_rect)
    
    def _render_waveform(self):
        """Render a waveform visualization if playing notes."""
        if not self.surface or not self.active_notes:
            return
            
        width, height = self.surface.get_size()
        wave_height = 100
        wave_width = width - 100
        x_start = 50
        y_start = 180
        
        # Create a simple waveform
        pygame.draw.rect(self.surface, (230, 230, 240), 
                         pygame.Rect(x_start, y_start, wave_width, wave_height))
        pygame.draw.rect(self.surface, (180, 180, 190), 
                         pygame.Rect(x_start, y_start, wave_width, wave_height), 1)
        
        # Draw central line
        pygame.draw.line(self.surface, (180, 180, 190), 
                         (x_start, y_start + wave_height // 2), 
                         (x_start + wave_width, y_start + wave_height // 2))
        
        # Generate composite waveform from active notes
        if self.active_notes:
            points = []
            step = wave_width / 100
            
            # Create sine wave representations
            for i in range(100):
                x = x_start + i * step
                y = y_start + wave_height // 2
                
                for note in self.active_notes:
                    # Convert note to frequency
                    freq = 440 * (2 ** ((note - 69) / 12))  # A4 (MIDI 69) = 440Hz
                    # Simplified waveform calculation
                    amplitude = wave_height / (4 * len(self.active_notes))
                    phase = i / 10  # Simple phase for visualization
                    y += amplitude * math.sin(2 * math.pi * (freq / 1000) * phase)
                
                points.append((x, y))
            
            # Draw the waveform
            if len(points) > 1:
                pygame.draw.lines(self.surface, self.colors["progress_bar"], False, points, 2)
    
    def _render_circle_of_fifths(self):
        """Render a circle of fifths visualization."""
        if not self.surface:
            return
            
        width, height = self.surface.get_size()
        center_x = width * 0.75
        center_y = height * 0.35
        radius = min(width, height) * 0.15
        
        # Draw the circle
        pygame.draw.circle(self.surface, (240, 240, 240), (int(center_x), int(center_y)), int(radius), 0)
        pygame.draw.circle(self.surface, (180, 180, 190), (int(center_x), int(center_y)), int(radius), 2)
        
        # Define the notes in the circle of fifths
        notes = ["C", "G", "D", "A", "E", "B", "F#", "Db", "Ab", "Eb", "Bb", "F"]
        
        # Calculate positions and draw note names
        font = pygame.font.Font(None, 24)
        for i, note in enumerate(notes):
            angle = math.radians(i * 30 - 90)  # Start at the top with C
            x = center_x + radius * 0.8 * math.cos(angle)
            y = center_y + radius * 0.8 * math.sin(angle)
            
            text = font.render(note, True, self.colors["text"])
            text_rect = text.get_rect(center=(x, y))
            self.surface.blit(text, text_rect)
            
        # Highlight active notes
        for note in self.active_notes:
            note_name = self._midi_to_note_name(note).replace("b", "b").split("/")[0]
            note_name = note_name[0:2] if len(note_name) > 1 else note_name
            
            if note_name in notes:
                i = notes.index(note_name)
                angle = math.radians(i * 30 - 90)
                x = center_x + radius * 0.8 * math.cos(angle)
                y = center_y + radius * 0.8 * math.sin(angle)
                
                pygame.draw.circle(self.surface, self.colors["highlight"], 
                                  (int(x), int(y)), 15, 0)
                
                # Redraw note text
                text = font.render(note_name, True, self.colors["text"])
                text_rect = text.get_rect(center=(x, y))
                self.surface.blit(text, text_rect)
    
    def handle_event(self, event):
        """Handle pygame events for user interaction."""
        if not self.pygame_initialized:
            return False
            
        handled = False
        
        # Handle mouse events
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Check if a piano key was clicked
            mouse_pos = pygame.mouse.get_pos()
            for key in self.key_positions:
                if key["rect"].collidepoint(mouse_pos):
                    self.play_note(key["note"])
                    self.played_notes.append(key["note"])
                    handled = True
                    break
                    
            # Check if a button was clicked
            for button in self.buttons:
                if button["rect"].collidepoint(mouse_pos):
                    if "action" in button and callable(button["action"]):
                        button["action"]()
                    handled = True
                    break
        
        # Handle keyboard events
        elif event.type == pygame.KEYDOWN:
            if event.key in self.key_mapping:
                offset = self.key_mapping[event.key]
                note = self.keyboard_config["start_note"] + offset
                self.play_note(note)
                self.played_notes.append(note)
                handled = True
        
        return handled
    
    def play_note(self, note):
        """Play a note sound and highlight the corresponding key."""
        # Play the sound
        if pygame.mixer.get_init() and note in self.sounds:
            try:
                self.sounds[note].play()
            except Exception as e:
                logger.error(f"Error playing note {note}: {e}")
        
        # Add to active notes for highlighting
        if note not in self.active_notes:
            self.active_notes.append(note)
            
        # Schedule note to be removed from active list
        pygame.time.set_timer(pygame.USEREVENT + 1, self.keyboard_config["highlight_duration"])
    
    def play_current_challenge(self):
        """Play the current challenge (extends parent class method)."""
        # Call the parent method for basic functionality
        super().play_current_challenge()
        
        # Add visual feedback
        self.set_feedback("Playing challenge...", self.colors["text"])
        
        # If this is a sequence challenge, highlight the notes
        if self.current_challenge_type == "sequence_memory":
            self._play_visual_sequence()
    
    def _play_visual_sequence(self):
        """Play a sequence with visual highlights."""
        if "sequence" in self.current_challenge:
            sequence = self.current_challenge["sequence"]
            
            # Play each note with a delay
            for i, note in enumerate(sequence):
                # Schedule note to play with delay
                pygame.time.set_timer(pygame.USEREVENT + 2 + i, int(i * 500))
    
    def submit_answer(self):
        """Process the user's answer submission."""
        # In sequence challenges, check the played notes
        if self.current_challenge_type == "sequence_memory":
            correct = self._check_sequence_match()
            self._process_answer_result(correct)
            
        # Reset played notes
        self.played_notes = []
    
    def _check_sequence_match(self):
        """Check if the played sequence matches the challenge sequence."""
        if "sequence" not in self.current_challenge:
            return False
            
        target_sequence = self.current_challenge["sequence"]
        
        # Check if sequences match
        if len(self.played_notes) != len(target_sequence):
            return False
            
        for i, note in enumerate(target_sequence):
            if i >= len(self.played_notes) or self.played_notes[i] != note:
                return False
                
        return True
    
    def _process_answer_result(self, correct):
        """Process the result of an answer submission."""
        # Update progress tracking
        self.progress["total_questions"] += 1
        
        if correct:
            self.progress["correct_answers"] += 1
            self.progress["current_streak"] += 1
            self.progress["best_streak"] = max(
                self.progress["best_streak"], 
                self.progress["current_streak"]
            )
            
            # Play correct sound effect
            if "correct" in self.sounds:
                self.sounds["correct"].play()
                
            # Show feedback
            self.set_feedback("Correct!", self.colors["correct"])
            
            # Adjust difficulty if consistently correct
            if self.progress["current_streak"] >= 3:
                self._adjust_difficulty(0.1)  # Increase difficulty
        else:
            self.progress["current_streak"] = 0
            
            # Play incorrect sound effect
            if "incorrect" in self.sounds:
                self.sounds["incorrect"].play()
                
            # Show feedback
            self.set_feedback("Incorrect. Try again!", self.colors["incorrect"])
            
            # Adjust difficulty if incorrect
            self._adjust_difficulty(-0.05)  # Decrease difficulty
        
        # Update type-specific accuracy tracking
        challenge_type = self.current_challenge_type
        if challenge_type not in self.progress["accuracy_by_type"]:
            self.progress["accuracy_by_type"][challenge_type] = {
                "correct": 0,
                "total": 0
            }
            
        self.progress["accuracy_by_type"][challenge_type]["total"] += 1
        if correct:
            self.progress["accuracy_by_type"][challenge_type]["correct"] += 1
            
        # Generate a new challenge after delay
        pygame.time.set_timer(pygame.USEREVENT + 20, 2000)  # 2 seconds
    
    def _adjust_difficulty(self, change):
        """Dynamically adjust difficulty based on performance."""
        # Update difficulty adjustment factor
        self.progress["difficulty_adjustment_factor"] += change
        
        # Keep within reasonable bounds
        self.progress["difficulty_adjustment_factor"] = max(0.5, min(
            2.0, self.progress["difficulty_adjustment_factor"]))
            
        # Log difficulty change
        logger.debug(f"Difficulty adjusted to: {self.progress['difficulty_adjustment_factor']}")
    
    def set_feedback(self, message, color=None):
        """Set feedback message with optional color."""
        self.feedback_message = message
        self.feedback_color = color or self.colors["text"]
        self.last_feedback_time = time.time() * 1000  # Current time in ms
    
    def new_challenge(self):
        """Generate a new challenge with adjusted difficulty."""
        # Apply difficulty adjustment to parameters
        # Store original parameters
        original_level = self.level
        
        # Apply difficulty adjustment
        adjusted_level = min(self.max_level, max(1, int(
            self.level * self.progress["difficulty_adjustment_factor"])))
        self.level = adjusted_level
        
        # Generate the challenge
        super().generate_challenge()
        
        # Restore original level
        self.level = original_level
        
        # Clear active and played notes
        self.active_notes = []
        self.played_notes = []

# Simple test if run directly
if __name__ == "__main__":
    module = InteractiveMusicTheoryModule()
    print(f"Module name: {module.name}")
    print(f"Challenge type: {module.current_challenge_type}")
    print(f"Available visualization modes: {module.visual_modes}")
    
    # Initialize pygame for testing
    try:
        pygame.init()
        pygame.mixer.init()
        screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("Interactive Music Theory Module Test")
        
        # Initialize module with pygame
        module.initialize_pygame(screen)
        
        # Main loop
        running = True
        clock = pygame.time.Clock()
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.USEREVENT + 1:
                    # Clear highlighted notes
                    module.active_notes = []
                elif event.type in range(pygame.USEREVENT + 2, pygame.USEREVENT + 10):
                    # Play sequence notes
                    note_idx = event.type - (pygame.USEREVENT + 2)
                    if "sequence" in module.current_challenge and note_idx < len(module.current_challenge["sequence"]):
                        module.play_note(module.current_challenge["sequence"][note_idx])
                elif event.type == pygame.USEREVENT + 20:
                    # Generate new challenge after delay
                    module.new_challenge()
                    pygame.time.set_timer(pygame.USEREVENT + 20, 0)  # Cancel timer
                else:
                    # Handle regular events
                    module.handle_event(event)
            
            # Render
            module.render(screen)
            pygame.display.flip()
            clock.tick(60)
        
        pygame.quit()
    except Exception as e:
        print(f"Error in pygame test: {e}") 