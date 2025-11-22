#!/usr/bin/env python3
"""
Music Components Renderer

This renderer provides shared functionality for music-related modules, integrating
the visual components, achievements, and notation capabilities.
"""

import pygame
import logging
import sys
import os
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any

# Import base renderer
from MetaMindIQTrain.clients.pygame.renderers.base_renderer import BaseRenderer

# Import music components
from MetaMindIQTrain.modules.music.visual_components import PianoKeyboard, GuitarFretboard, WaveformVisualizer
from MetaMindIQTrain.modules.music.notation import NotationRenderer, SimpleNotationParser, MusicStaff, ChordSymbol, StaffSymbols
from MetaMindIQTrain.modules.music.achievements import MusicAchievementSystem

# Configure logging
logger = logging.getLogger(__name__)

class MusicComponentsRenderer(BaseRenderer):
    """
    Base renderer for music-related modules that integrates all music visualization components.
    
    This renderer provides common functionality for displaying:
    - Piano keyboard visualization
    - Guitar fretboard visualization
    - Music notation (staff)
    - Waveform visualization
    - Achievement notifications
    
    Individual music module renderers can inherit from this class to get access
    to all these components without duplicating code.
    """
    
    def __init__(self, screen, session_manager, module, config=None):
        """
        Initialize the music components renderer.
        
        Args:
            screen: PyGame screen surface
            session_manager: SessionManager instance
            module: Training module instance
            config: Optional configuration dictionary
        """
        super().__init__(screen, session_manager, module, config)
        
        # Initialize common colors
        self.colors.update({
            'note_highlight': (255, 215, 0),   # Gold
            'piano_white_key': (255, 255, 255),
            'piano_black_key': (40, 40, 40),
            'piano_border': (100, 100, 100),
            'staff_lines': (50, 50, 50),
            'staff_background': (250, 250, 250),
            'notation_note': (0, 0, 0),
            'notation_highlight': (255, 50, 50),
            'fretboard_background': (165, 122, 80),  # Wood color
            'fretboard_fret': (160, 160, 160),       # Silver
            'fretboard_string': (210, 210, 210),     # String color
            'fretboard_marker': (250, 250, 250),     # Fret markers
            'fretboard_highlight': (255, 215, 0),    # Gold
            'waveform': (30, 130, 220),              # Waveform color
            'achievement': (255, 215, 0),            # Achievement highlight
            'correct': (50, 200, 50),                # Correct answer
            'incorrect': (200, 50, 50),              # Incorrect answer
        })
        
        # Screen dimensions
        self.width, self.height = screen.get_size()
        
        # Initialize keyboard component
        self.keyboard = PianoKeyboard(start_note="C3", num_octaves=2)
        self.keyboard.set_dimensions(white_key_width=40, white_key_height=120)
        
        # Initialize fretboard component
        self.fretboard = GuitarFretboard(num_strings=6, num_frets=12)
        
        # Initialize notation component
        self.notation = NotationRenderer(width=int(self.width * 0.8), height=150)
        
        # Initialize waveform visualizer
        self.waveform = WaveformVisualizer(width=int(self.width * 0.8), height=80)
        
        # Initialize achievements system
        self.achievement_system = MusicAchievementSystem()
        self.show_achievement = False
        self.current_achievement = None
        self.achievement_timer = 0
        self.achievement_display_time = 3000  # 3 seconds
        
        # Font initialization
        self.title_font = pygame.font.Font(None, 36)
        self.note_font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 18)
        
        # Performance feedback
        self.feedback_message = ""
        self.feedback_color = self.colors['text']
        self.feedback_timer = 0
        self.feedback_display_time = 1500  # 1.5 seconds
        
        # Sound generation
        self.sound_enabled = True
        self.sound_cache = {}  # Cache for PyGame sound objects
        
        # Parse common notation
        self.parser = SimpleNotationParser()
        
        # Status indicators
        self.last_answer_correct = None  # None, True, or False
        
    def register_module_specific_achievements(self):
        """
        Register module-specific achievements.
        
        Override this method in subclasses to add module-specific achievements.
        """
        pass
        
    def render_piano_keyboard(self, x, y):
        """
        Render the piano keyboard.
        
        Args:
            x: Left position of the keyboard
            y: Top position of the keyboard
            
        Returns:
            pygame.Rect: The area occupied by the keyboard
        """
        key_data = self.keyboard.get_key_data()
        white_keys = key_data['white_keys']
        black_keys = key_data['black_keys']
        highlighted = key_data['highlighted']
        
        # Draw white keys
        key_width = self.keyboard.white_key_width
        key_height = self.keyboard.white_key_height
        
        key_rects = {}  # Store rectangles for each key for hit detection
        
        # Draw white keys first
        for i, note in enumerate(white_keys):
            key_x = x + (i * key_width)
            key_rect = pygame.Rect(key_x, y, key_width, key_height)
            
            # Determine if highlighted
            is_highlighted = note in highlighted
            color = self.colors['note_highlight'] if is_highlighted else self.colors['piano_white_key']
            
            # Draw the key
            pygame.draw.rect(self.screen, color, key_rect)
            pygame.draw.rect(self.screen, self.colors['piano_border'], key_rect, 1)
            
            # Store rectangle
            key_rects[note] = key_rect
            
            # Draw note name at bottom of key
            note_name = note[0] if len(note) >= 1 else ""
            if len(note) > 1 and note[1] in ["#", "b"]:
                note_name += note[1]
                
            note_text = self.small_font.render(note_name, True, self.colors['text'])
            note_rect = note_text.get_rect(centerx=key_rect.centerx, bottom=key_rect.bottom - 5)
            self.screen.blit(note_text, note_rect)
        
        # Draw black keys on top
        black_key_width = self.keyboard.black_key_width
        black_key_height = self.keyboard.black_key_height
        
        for note in black_keys:
            # Find the white key to the left
            note_name = note[0]
            octave = note[1:] if len(note) > 1 else "4"
            left_white = f"{note_name}{octave}"
            
            if left_white in key_rects:
                left_rect = key_rects[left_white]
                
                # Position black key
                key_x = left_rect.right - (black_key_width // 2)
                key_rect = pygame.Rect(key_x, y, black_key_width, black_key_height)
                
                # Determine if highlighted
                is_highlighted = note in highlighted
                color = self.colors['note_highlight'] if is_highlighted else self.colors['piano_black_key']
                
                # Draw the key
                pygame.draw.rect(self.screen, color, key_rect)
                pygame.draw.rect(self.screen, self.colors['piano_border'], key_rect, 1)
                
                # Store rectangle
                key_rects[note] = key_rect
        
        # Return the area occupied by the keyboard
        keyboard_rect = pygame.Rect(x, y, len(white_keys) * key_width, key_height)
        return keyboard_rect
    
    def render_fretboard(self, x, y, width, height):
        """
        Render the guitar fretboard.
        
        Args:
            x: Left position of the fretboard
            y: Top position of the fretboard
            width: Width of the fretboard
            height: Height of the fretboard
            
        Returns:
            pygame.Rect: The area occupied by the fretboard
        """
        fretboard_data = self.fretboard.get_fretboard_data()
        num_strings = fretboard_data['num_strings']
        num_frets = fretboard_data['num_frets']
        highlighted = fretboard_data['highlighted']
        
        # Calculate spacing
        fret_spacing = width / (num_frets + 1)
        string_spacing = height / (num_strings + 1)
        
        # Draw fretboard background
        fretboard_rect = pygame.Rect(x, y, width, height)
        pygame.draw.rect(self.screen, self.colors['fretboard_background'], fretboard_rect)
        
        # Draw frets
        for i in range(num_frets + 1):  # +1 for nut
            fret_x = x + (i * fret_spacing)
            fret_width = 2 if i == 0 else 1  # Nut is thicker
            pygame.draw.line(
                self.screen,
                self.colors['fretboard_fret'],
                (fret_x, y),
                (fret_x, y + height),
                fret_width
            )
        
        # Draw position markers (dots)
        marker_positions = [3, 5, 7, 9, 12]
        for pos in marker_positions:
            if pos <= num_frets:
                marker_x = x + ((pos - 0.5) * fret_spacing)
                marker_y = y + (height / 2)
                
                # Special double dot for 12th fret
                if pos == 12:
                    pygame.draw.circle(
                        self.screen,
                        self.colors['fretboard_marker'],
                        (int(marker_x), int(marker_y - 20)),
                        5
                    )
                    pygame.draw.circle(
                        self.screen,
                        self.colors['fretboard_marker'],
                        (int(marker_x), int(marker_y + 20)),
                        5
                    )
                else:
                    pygame.draw.circle(
                        self.screen,
                        self.colors['fretboard_marker'],
                        (int(marker_x), int(marker_y)),
                        5
                    )
        
        # Draw strings
        for i in range(num_strings):
            string_y = y + ((i + 1) * string_spacing)
            string_thickness = 3 - min(2, int(i * 0.4))  # Thicker for lower strings
            pygame.draw.line(
                self.screen,
                self.colors['fretboard_string'],
                (x, string_y),
                (x + width, string_y),
                string_thickness
            )
        
        # Draw highlighted positions
        for string_idx, fret in highlighted:
            if 0 <= string_idx < num_strings and 0 <= fret <= num_frets:
                pos_x = x + (fret * fret_spacing) - (fret_spacing / 2) if fret > 0 else x + 10
                pos_y = y + ((string_idx + 1) * string_spacing)
                
                pygame.draw.circle(
                    self.screen,
                    self.colors['fretboard_highlight'],
                    (int(pos_x), int(pos_y)),
                    8
                )
        
        # Return the area occupied by the fretboard
        return fretboard_rect
    
    def render_music_notation(self, x, y):
        """
        Render music notation (staff).
        
        Args:
            x: Left position of the staff
            y: Top position of the staff
            
        Returns:
            pygame.Rect: The area occupied by the staff
        """
        render_data = self.notation.get_render_data()
        staff_data = render_data['staff']
        
        width = self.notation.width
        height = self.notation.height
        
        # Draw staff background
        staff_rect = pygame.Rect(x, y, width, height)
        pygame.draw.rect(self.screen, self.colors['staff_background'], staff_rect)
        pygame.draw.rect(self.screen, self.colors['staff_lines'], staff_rect, 1)
        
        # Draw staff lines (5 lines)
        line_spacing = height / 8
        for i in range(5):
            line_y = y + (height / 2) + ((i - 2) * line_spacing)
            pygame.draw.line(
                self.screen,
                self.colors['staff_lines'],
                (x, line_y),
                (x + width, line_y),
                1
            )
        
        # Draw clef
        clef_text = self.title_font.render("𝄞" if staff_data['clef'] == "treble" else "𝄢", True, self.colors['text'])
        clef_rect = clef_text.get_rect(left=x + 10, centery=y + (height / 2))
        self.screen.blit(clef_text, clef_rect)
        
        # Draw time signature
        time_sig = staff_data['time_signature']
        if time_sig:
            if time_sig == "common_time":
                time_text = self.title_font.render("𝄴", True, self.colors['text'])
            else:
                time_text = self.title_font.render(time_sig, True, self.colors['text'])
            
            time_rect = time_text.get_rect(left=x + 50, centery=y + (height / 2))
            self.screen.blit(time_text, time_rect)
        
        # Draw notes (simplified)
        note_position = 80
        highlighted_indices = render_data['highlighted_notes']
        
        note_index = 0
        for measure_idx, measure in enumerate(staff_data['measures']):
            for note in measure:
                is_highlighted = note_index in highlighted_indices
                color = self.colors['notation_highlight'] if is_highlighted else self.colors['notation_note']
                
                if note['pitch'] != "rest":
                    # Calculate vertical position
                    staff_position = note['staff_position']
                    note_y = y + (height / 2) - (staff_position * line_spacing / 2)
                    
                    # Draw note head
                    pygame.draw.ellipse(
                        self.screen,
                        color,
                        (x + note_position, note_y - 5, 10, 10)
                    )
                    
                    # Draw stem if not whole note
                    if note['duration'] != "whole":
                        stem_direction = note['stem_direction']
                        stem_height = 30
                        
                        if stem_direction == "up":
                            pygame.draw.line(
                                self.screen,
                                color,
                                (x + note_position + 8, note_y),
                                (x + note_position + 8, note_y - stem_height),
                                2
                            )
                        else:
                            pygame.draw.line(
                                self.screen,
                                color,
                                (x + note_position + 2, note_y),
                                (x + note_position + 2, note_y + stem_height),
                                2
                            )
                    
                    # Draw ledger lines if needed
                    if staff_position <= -6:  # Below staff
                        lines_needed = ((-staff_position - 4) // 2) + 1
                        for i in range(lines_needed):
                            line_y = y + (height / 2) + ((3 + i) * line_spacing)
                            pygame.draw.line(
                                self.screen,
                                self.colors['staff_lines'],
                                (x + note_position - 5, line_y),
                                (x + note_position + 15, line_y),
                                1
                            )
                    elif staff_position >= 6:  # Above staff
                        lines_needed = ((staff_position - 4) // 2) + 1
                        for i in range(lines_needed):
                            line_y = y + (height / 2) - ((3 + i) * line_spacing)
                            pygame.draw.line(
                                self.screen,
                                self.colors['staff_lines'],
                                (x + note_position - 5, line_y),
                                (x + note_position + 15, line_y),
                                1
                            )
                    
                    # Draw accidental if any
                    if note['accidental']:
                        acc_text = ""
                        if note['accidental'] == "sharp":
                            acc_text = "♯"
                        elif note['accidental'] == "flat":
                            acc_text = "♭"
                        elif note['accidental'] == "natural":
                            acc_text = "♮"
                        
                        if acc_text:
                            acc_render = self.note_font.render(acc_text, True, color)
                            acc_rect = acc_render.get_rect(right=x + note_position - 2, centery=note_y)
                            self.screen.blit(acc_render, acc_rect)
                
                # Advance position based on duration
                if note['duration'] in ["whole", "whole_rest"]:
                    note_position += 40
                elif note['duration'] in ["half", "half_rest"]:
                    note_position += 30
                else:
                    note_position += 25
                
                note_index += 1
            
            # Add bar line
            if measure_idx < len(staff_data['measures']) - 1:
                pygame.draw.line(
                    self.screen,
                    self.colors['staff_lines'],
                    (x + note_position, y),
                    (x + note_position, y + height),
                    1
                )
                note_position += 20
        
        # Draw chord symbols
        for chord_data in render_data['chord_symbols']:
            position = chord_data['position']
            chord = chord_data['chord']
            
            # Calculate horizontal position (simplified)
            chord_x = x + 80 + (position * 25)
            
            # Draw chord symbol
            chord_text = self.note_font.render(chord['display'], True, self.colors['text'])
            chord_rect = chord_text.get_rect(centerx=chord_x, bottom=y)
            self.screen.blit(chord_text, chord_rect)
        
        return staff_rect
    
    def render_waveform(self, x, y, samples=None):
        """
        Render audio waveform.
        
        Args:
            x: Left position of the waveform
            y: Top position of the waveform
            samples: Audio samples to visualize (optional)
            
        Returns:
            pygame.Rect: The area occupied by the waveform
        """
        if samples is not None:
            self.waveform.set_samples(samples)
        
        width = self.waveform.width
        height = self.waveform.height
        
        # Draw waveform background
        waveform_rect = pygame.Rect(x, y, width, height)
        pygame.draw.rect(self.screen, self.colors['background_alt'], waveform_rect)
        pygame.draw.rect(self.screen, self.colors['border'], waveform_rect, 1)
        
        # Get waveform points
        points = self.waveform.get_waveform_points()
        
        # Draw the waveform
        if points:
            # Convert to screen coordinates
            screen_points = [(x + p[0], y + p[1]) for p in points]
            
            # Draw the waveform line
            if len(screen_points) > 1:
                pygame.draw.lines(
                    self.screen,
                    self.colors['waveform'],
                    False,
                    screen_points,
                    2
                )
        
        return waveform_rect
    
    def display_achievement(self, achievement):
        """
        Display an achievement notification.
        
        Args:
            achievement: Achievement object to display
        """
        self.show_achievement = True
        self.current_achievement = achievement
        self.achievement_timer = pygame.time.get_ticks()
    
    def render_achievement_notification(self):
        """
        Render the achievement notification if active.
        """
        if not self.show_achievement or not self.current_achievement:
            return
        
        # Check if we should still show the notification
        current_time = pygame.time.get_ticks()
        if current_time - self.achievement_timer > self.achievement_display_time:
            self.show_achievement = False
            return
        
        # Calculate animation (fade in/out)
        elapsed = current_time - self.achievement_timer
        alpha = 255
        if elapsed < 500:  # Fade in
            alpha = int(255 * (elapsed / 500))
        elif elapsed > self.achievement_display_time - 500:  # Fade out
            alpha = int(255 * ((self.achievement_display_time - elapsed) / 500))
        
        # Create notification surface
        notification_width = 400
        notification_height = 80
        notification = pygame.Surface((notification_width, notification_height), pygame.SRCALPHA)
        
        # Fill with semi-transparent background
        notification.fill((0, 0, 0, 200))
        
        # Create text
        title_text = self.title_font.render(
            f"Achievement Unlocked: {self.current_achievement.name}",
            True,
            self.colors['achievement']
        )
        desc_text = self.note_font.render(
            self.current_achievement.description,
            True,
            self.colors['text']
        )
        points_text = self.note_font.render(
            f"+{self.current_achievement.points} points",
            True,
            self.colors['achievement']
        )
        
        # Position text
        title_rect = title_text.get_rect(centerx=notification_width//2, top=10)
        desc_rect = desc_text.get_rect(centerx=notification_width//2, top=title_rect.bottom + 5)
        points_rect = points_text.get_rect(centerx=notification_width//2, top=desc_rect.bottom + 5)
        
        # Draw text on notification
        notification.blit(title_text, title_rect)
        notification.blit(desc_text, desc_rect)
        notification.blit(points_text, points_rect)
        
        # Apply alpha
        notification.set_alpha(alpha)
        
        # Position notification at top of screen
        notification_rect = notification.get_rect(centerx=self.width//2, top=10)
        
        # Draw notification
        self.screen.blit(notification, notification_rect)
    
    def show_feedback(self, message, is_correct=None):
        """
        Show feedback message to the user.
        
        Args:
            message: Message to display
            is_correct: Whether the answer was correct (True/False/None)
        """
        self.feedback_message = message
        self.feedback_timer = pygame.time.get_ticks()
        self.last_answer_correct = is_correct
        
        if is_correct is True:
            self.feedback_color = self.colors['correct']
        elif is_correct is False:
            self.feedback_color = self.colors['incorrect']
        else:
            self.feedback_color = self.colors['text']
    
    def render_feedback(self):
        """
        Render feedback message if active.
        """
        if not self.feedback_message:
            return
        
        # Check if we should still show the message
        current_time = pygame.time.get_ticks()
        if current_time - self.feedback_timer > self.feedback_display_time:
            self.feedback_message = ""
            return
        
        # Calculate fade out
        elapsed = current_time - self.feedback_timer
        alpha = 255
        if elapsed > self.feedback_display_time - 500:  # Fade out
            alpha = int(255 * ((self.feedback_display_time - elapsed) / 500))
        
        # Create text
        feedback_text = self.title_font.render(self.feedback_message, True, self.feedback_color)
        feedback_text.set_alpha(alpha)
        
        # Position at bottom center
        feedback_rect = feedback_text.get_rect(centerx=self.width//2, bottom=self.height - 20)
        
        # Draw message
        self.screen.blit(feedback_text, feedback_rect)
    
    def play_note(self, note_name, duration=0.5):
        """
        Play a note using PyGame's sound system.
        
        Args:
            note_name: Note name with octave (e.g., "C4", "F#3")
            duration: Note duration in seconds
        """
        if not self.sound_enabled:
            return
        
        # Get frequency for the note
        frequency = self.get_note_frequency(note_name)
        
        # Create sound if not in cache
        if note_name not in self.sound_cache:
            # Create a simple sine wave
            sample_rate = 44100
            samples = np.sin(2 * np.pi * np.arange(sample_rate * duration) * frequency / sample_rate)
            
            # Apply simple envelope
            envelope = np.ones(len(samples))
            attack = int(sample_rate * 0.02)  # 20ms attack
            release = int(sample_rate * 0.1)   # 100ms release
            
            # Linear attack
            if attack > 0:
                envelope[:attack] = np.linspace(0, 1, attack)
            
            # Linear release
            if release > 0:
                envelope[-release:] = np.linspace(1, 0, release)
            
            # Apply envelope
            samples = samples * envelope
            
            # Convert to 16-bit values
            samples = (samples * 32767).astype(np.int16)
            
            # Create sound object
            sound = pygame.sndarray.make_sound(samples)
            
            # Store in cache
            self.sound_cache[note_name] = sound
        
        # Play the sound
        self.sound_cache[note_name].play()
    
    def get_note_frequency(self, note_name):
        """
        Get the frequency for a note name.
        
        Args:
            note_name: Note name with octave (e.g., "C4", "F#3")
            
        Returns:
            float: Frequency in Hz
        """
        # Parse note name
        note = note_name[0].upper()
        octave = int(note_name[-1])
        accidental = 0
        
        if len(note_name) > 2:
            if note_name[1] == '#':
                accidental = 1
            elif note_name[1] == 'b':
                accidental = -1
        
        # Note offsets from C
        note_offsets = {
            'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11
        }
        
        # Calculate semitones from A4 (440 Hz)
        semitones_from_a4 = (octave - 4) * 12 + note_offsets[note] - 9 + accidental
        
        # Calculate frequency using equal temperament formula
        frequency = 440 * (2 ** (semitones_from_a4 / 12))
        
        return frequency
    
    def render(self):
        """
        Render all components.
        
        This is a template method that can be overridden by subclasses.
        """
        # Clear screen
        self.screen.fill(self.colors['background'])
        
        # Draw title
        title = self.module.name if hasattr(self.module, 'name') else "Music Training"
        self.draw_title(title)
        
        # Draw components (position can be adjusted in subclasses)
        margin = 20
        y_position = 80
        
        # Render staff notation
        self.render_music_notation(self.width // 2 - self.notation.width // 2, y_position)
        y_position += self.notation.height + margin
        
        # Render piano keyboard
        keyboard_width = self.keyboard.white_key_width * len(self.keyboard.get_key_data()['white_keys'])
        self.render_piano_keyboard(self.width // 2 - keyboard_width // 2, y_position)
        y_position += self.keyboard.white_key_height + margin
        
        # Render feedback
        self.render_feedback()
        
        # Render achievement notification
        self.render_achievement_notification()
    
    def handle_event(self, event):
        """
        Handle PyGame events.
        
        Args:
            event: PyGame event object
            
        Returns:
            bool: Whether the event was handled
        """
        return super().handle_event(event)
    
    def update(self, dt):
        """
        Update logic.
        
        Args:
            dt: Time delta in seconds
        """
        super().update(dt)
        
        # Check for newly earned achievements
        if hasattr(self.module, 'stats'):
            newly_earned = self.achievement_system.check_achievement_progress(
                self.module.__class__.__name__,
                self.module.stats
            )
            
            # Display the first new achievement
            if newly_earned:
                self.display_achievement(newly_earned[0])
    
    def cleanup(self):
        """Clean up resources."""
        super().cleanup()
        
        # Save achievements
        self.achievement_system.save()
        
        # Clear sound cache
        self.sound_cache.clear()


# Register this renderer in the registry when imported
if __name__ != "__main__":
    try:
        from MetaMindIQTrain.clients.pygame.renderers.registry import register_renderer
        register_renderer("music_components", MusicComponentsRenderer)
        logger.info("Registered MusicComponentsRenderer")
    except ImportError:
        logger.warning("Failed to register MusicComponentsRenderer - registry not available") 