#!/usr/bin/env python3
"""
Music Theory Training Module

A cognitive training module focused on musical pattern recognition, 
interval identification, and scale familiarity. This module challenges
users to identify musical elements and strengthens auditory-cognitive connections.
"""

import random
import math
import time
import logging
import numpy as np
from typing import Dict, Any, List, Tuple, Optional
import sys
from pathlib import Path

# Add the parent directory to sys.path for absolute imports when imported directly
if __name__ == "__main__" or not __package__:
    project_root = Path(__file__).parent.parent.parent
    sys.path.insert(0, str(project_root))
    from MetaMindIQTrain.modules.music.audio_synthesis import MusicTrainingModule, AUDIO_AVAILABLE
else:
    # Use relative imports when imported as a module
    from .audio_synthesis import MusicTrainingModule, AUDIO_AVAILABLE

# Configure logging
logger = logging.getLogger(__name__)

class MusicTheoryModule(MusicTrainingModule):
    """
    MusicTheory training module with auditory pattern recognition challenges.
    
    This module presents various musical elements (scales, intervals, chords)
    and challenges users to identify them, enhancing auditory-cognitive connections.
    """
    
    def __init__(self):
        """Initialize the MusicTheory module."""
        # Initialize the base module
        super().__init__()
        
        # Module metadata
        self.name = "Music Theory"
        self.description = "Train your ear and musical cognition"
        self.category = "Music"
        self.difficulty = "Medium"
        
        # Audio settings
        self.duration = 0.5      # Duration of each note in seconds
        self.volume = 0.3        # Volume level (0.0 to 1.0)
        self.base_frequency = 440.0  # A4 = 440Hz
        
        # Enhanced music theory components
        self.scales = {
            "Major": [0, 2, 4, 5, 7, 9, 11],
            "Minor": [0, 2, 3, 5, 7, 8, 10],
            "Pentatonic": [0, 2, 4, 7, 9],
            "Blues": [0, 3, 5, 6, 7, 10],
            "Chromatic": list(range(12)),
            "Whole Tone": [0, 2, 4, 6, 8, 10],
            "Hirajoshi": [0, 4, 6, 7, 11],
            "Byzantine": [0, 1, 4, 5, 7, 8, 11]
        }
        
        self.intervals = {
            "Unison": 0,
            "Minor Second": 1,
            "Major Second": 2,
            "Minor Third": 3,
            "Major Third": 4,
            "Perfect Fourth": 5,
            "Tritone": 6,
            "Perfect Fifth": 7,
            "Minor Sixth": 8,
            "Major Sixth": 9,
            "Minor Seventh": 10,
            "Major Seventh": 11,
            "Octave": 12
        }
        
        self.chords = {
            "Major": [0, 4, 7],
            "Minor": [0, 3, 7],
            "Diminished": [0, 3, 6],
            "Augmented": [0, 4, 8],
            "Suspended 4th": [0, 5, 7],
            "7th": [0, 4, 7, 10],
            "Major 7th": [0, 4, 7, 11]
        }
        
        # Challenge settings
        self.challenge_types = ["scales", "intervals", "chords"]
        self.current_challenge_type = "scales"
        self.current_challenge = None
        self.current_options = []
        self.correct_answer = None
        self.user_answer = None
        self.answered = False
        
        # Difficulty settings
        self.difficulties = {
            1: {"options": 3, "types": ["scales"], "elements": ["Major", "Minor", "Pentatonic"]},
            2: {"options": 4, "types": ["scales", "intervals"], "elements": ["Major", "Minor", "Pentatonic", "Blues"]},
            3: {"options": 5, "types": ["scales", "intervals", "chords"], "elements": ["Major", "Minor", "Pentatonic", "Blues", "Chromatic"]},
            4: {"options": 6, "types": ["scales", "intervals", "chords"], "elements": list(self.scales.keys())[:6]},
            5: {"options": 8, "types": ["scales", "intervals", "chords"], "elements": list(self.scales.keys())}
        }
        
        # Game state
        self.state = "challenge"  # can be "challenge", "feedback", "completed"
        self.score = 0
        self.level = 1
        self.max_level = 5
        self.consecutive_correct = 0
        self.challenges_per_level = 5
        self.current_level_challenges = 0
        self.message = "Listen to the audio and select the correct option"
        
        # Generate initial challenge
        self.generate_challenge()
    
    def generate_challenge(self):
        """Generate a new musical challenge based on current level and difficulty."""
        difficulty = self.difficulties[min(self.level, self.max_level)]
        
        # Select challenge type based on current level
        available_types = difficulty["types"]
        self.current_challenge_type = random.choice(available_types)
        
        # Select available elements based on difficulty
        available_elements = difficulty["elements"]
        
        # Use either MIDI numbers or note names for the challenge
        # Choose based on even/odd level to ensure consistent behavior
        use_midi = (self.level % 2 == 0)
        
        if self.current_challenge_type == "scales":
            # Filter scales to only include those in available_elements
            available_scales = {k: v for k, v in self.scales.items() if k in available_elements}
            scale_name = random.choice(list(available_scales.keys()))
            scale = available_scales[scale_name]
            
            if use_midi:
                # Generate a melodic pattern from the scale using MIDI numbers
                root_note = random.randint(48, 60)  # Middle C range
                melody = [root_note + note for note in random.sample(scale, min(5, len(scale)))]
                
                self.current_challenge = {
                    "type": "scales",
                    "name": scale_name,
                    "melody": melody,
                    "root": root_note,
                    "use_midi": True
                }
            else:
                # Generate a root note using note names
                root_note = f"{random.choice(['C', 'D', 'E', 'F', 'G', 'A', 'B'])}{random.randint(3, 5)}"
                
                self.current_challenge = {
                    "type": "scales",
                    "name": scale_name,
                    "root_note": root_note,
                    "use_midi": False
                }
            
            self.correct_answer = scale_name
            
        elif self.current_challenge_type == "intervals":
            # Select an interval
            interval_name = random.choice(list(self.intervals.keys()))
            interval_value = self.intervals[interval_name]
            
            if use_midi:
                # Generate notes for the interval using MIDI numbers
                root_note = random.randint(48, 60)
                interval_notes = [root_note, root_note + interval_value]
                
                self.current_challenge = {
                    "type": "intervals",
                    "name": interval_name,
                    "notes": interval_notes,
                    "root": root_note,
                    "use_midi": True
                }
            else:
                # Generate root note for the interval using note names
                root_note = f"{random.choice(['C', 'D', 'E', 'F', 'G', 'A', 'B'])}{random.randint(3, 5)}"
                
                self.current_challenge = {
                    "type": "intervals",
                    "name": interval_name,
                    "root_note": root_note,
                    "use_midi": False
                }
            
            self.correct_answer = interval_name
            
        elif self.current_challenge_type == "chords":
            # Select a chord
            chord_name = random.choice(list(self.chords.keys()))
            chord = self.chords[chord_name]
            
            if use_midi:
                # Generate notes for the chord using MIDI numbers
                root_note = random.randint(48, 60)
                chord_notes = [root_note + note for note in chord]
                
                self.current_challenge = {
                    "type": "chords",
                    "name": chord_name,
                    "notes": chord_notes,
                    "root": root_note,
                    "use_midi": True
                }
            else:
                # Generate root note for the chord using note names
                root_note = f"{random.choice(['C', 'D', 'E', 'F', 'G', 'A', 'B'])}{random.randint(3, 5)}"
                
                self.current_challenge = {
                    "type": "chords",
                    "name": chord_name,
                    "root_note": root_note,
                    "use_midi": False
                }
            
            self.correct_answer = chord_name
        
        # Generate options for multiple choice
        num_options = difficulty["options"]
        if self.current_challenge_type == "scales":
            self.current_options = [self.correct_answer]
            while len(self.current_options) < num_options:
                option = random.choice(available_elements)
                if option not in self.current_options and option in self.scales:
                    self.current_options.append(option)
        elif self.current_challenge_type == "intervals":
            self.current_options = [self.correct_answer]
            all_intervals = list(self.intervals.keys())
            while len(self.current_options) < num_options:
                option = random.choice(all_intervals)
                if option not in self.current_options:
                    self.current_options.append(option)
        elif self.current_challenge_type == "chords":
            self.current_options = [self.correct_answer]
            all_chords = list(self.chords.keys())
            while len(self.current_options) < num_options:
                option = random.choice(all_chords)
                if option not in self.current_options:
                    self.current_options.append(option)
        
        # Shuffle options
        random.shuffle(self.current_options)
        
        # Reset state
        self.user_answer = None
        self.answered = False
        self.state = "challenge"
        
        # Generate message based on challenge type
        if self.current_challenge_type == "scales":
            self.message = "Listen to the melody and identify the scale"
        elif self.current_challenge_type == "intervals":
            self.message = "Listen to the interval and identify it"
        elif self.current_challenge_type == "chords":
            self.message = "Listen to the chord and identify it"
    
    def play_current_challenge(self):
        """Play the current challenge audio."""
        if not AUDIO_AVAILABLE:
            logger.warning("Cannot play challenge: sounddevice not available")
            return False
            
        challenge = self.current_challenge
        if not challenge:
            return False
            
        challenge_type = challenge["type"]
        
        try:
            if challenge.get("use_midi", False):
                # Handle MIDI-based challenges
                if challenge_type == "scales":
                    # Play the scale melody
                    for note in challenge["melody"]:
                        frequency = self._midi_to_frequency(note)
                        self.play_sound(frequency, duration=self.duration, volume=self.volume)
                        time.sleep(self.duration * 0.2)  # Short pause between notes
                    return True
                    
                elif challenge_type == "intervals":
                    # Play the interval notes
                    for note in challenge["notes"]:
                        frequency = self._midi_to_frequency(note)
                        self.play_sound(frequency, duration=self.duration, volume=self.volume)
                        time.sleep(self.duration * 0.2)  # Short pause between notes
                    # Play both notes together
                    for note in challenge["notes"]:
                        frequency = self._midi_to_frequency(note)
                        self.play_sound(frequency, duration=self.duration, volume=self.volume)
                    return True
                    
                elif challenge_type == "chords":
                    # Play the chord notes sequentially first
                    for note in challenge["notes"]:
                        frequency = self._midi_to_frequency(note)
                        self.play_sound(frequency, duration=self.duration, volume=self.volume)
                        time.sleep(self.duration * 0.2)  # Short pause between notes
                    # Then play the chord (base class handles the chord)
                    root_midi = challenge["root"]
                    root_note = self._midi_to_note_name(root_midi)
                    self.play_chord(challenge["name"], root_note)
                    return True
            else:
                # Handle note name-based challenges
                if challenge_type == "scales":
                    # Play the scale
                    scale_name = challenge["name"]
                    root_note = challenge["root_note"]
                    self.play_scale(scale_name, root_note)
                    return True
                    
                elif challenge_type == "intervals":
                    # Play the interval
                    interval_name = challenge["name"]
                    root_note = challenge["root_note"]
                    self.play_interval(interval_name, root_note, direction="both")
                    return True
                    
                elif challenge_type == "chords":
                    # Play the chord
                    chord_name = challenge["name"]
                    root_note = challenge["root_note"]
                    self.play_chord(chord_name, root_note)
                    return True
                
            return False
            
        except Exception as e:
            logger.error(f"Error playing challenge: {e}")
            return False
    
    def _midi_to_frequency(self, midi_note):
        """Convert a MIDI note number to frequency in Hz."""
        return 440.0 * (2 ** ((midi_note - 69) / 12.0))
    
    def _midi_to_note_name(self, midi_note):
        """Convert a MIDI note number to a note name (e.g., C4)."""
        notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        octave = (midi_note // 12) - 1
        note_name = notes[midi_note % 12]
        return f"{note_name}{octave}"
    
    def handle_click(self, x, y):
        """
        Handle a click event.
        
        Args:
            x: The x-coordinate of the click.
            y: The y-coordinate of the click.
            
        Returns:
            dict: A dictionary containing the result of the click.
        """
        # Process click based on UI state
        ui_components = self.ui.components
        
        # Find if any option was clicked
        option_clicked = None
        for component in ui_components:
            # Only process button components
            if component.get('type') != 'button':
                continue
                
            # Check if the click is within the button's bounds
            button_x, button_y = component.get('position', (0, 0))
            button_width, button_height = component.get('size', (0, 0))
            
            # Calculate button bounds
            left = button_x - button_width // 2
            right = button_x + button_width // 2
            top = button_y - button_height // 2
            bottom = button_y + button_height // 2
            
            if left <= x <= right and top <= y <= bottom:
                option_clicked = component.get('text')
                break
        
        # Handle play button click
        if option_clicked == "Play Audio":
            self.play_current_challenge()
            return {
                "success": True,
                "message": "Playing audio..."
            }
        
        # Handle answer option clicks during challenge
        if self.state == "challenge" and option_clicked in self.current_options:
            self.user_answer = option_clicked
            self.answered = True
            
            # Check if answer is correct
            correct = (self.user_answer == self.correct_answer)
            
            # Update consecutive correct count
            if correct:
                self.consecutive_correct += 1
                self.score += 100 * self.level
                message = f"Correct! That was a {self.correct_answer}."
            else:
                self.consecutive_correct = 0
                message = f"Incorrect. That was a {self.correct_answer}."
            
            # Update current level challenges count
            self.current_level_challenges += 1
            
            # Check for level advancement
            if self.current_level_challenges >= self.challenges_per_level:
                # Reset challenges count
                self.current_level_challenges = 0
                
                # Check if we should advance to the next level
                if self.consecutive_correct >= 3 and self.level < self.max_level:
                    self.level += 1
                    message += f" Advanced to level {self.level}!"
            
            # Provide feedback temporarily
            self.state = "feedback"
            self.message = message
            
            # Generate next challenge after a delay (handled by update method)
            
            return {
                "success": True,
                "message": message,
                "correct": correct
            }
            
        # Handle continue button during feedback
        if self.state == "feedback" and option_clicked == "Continue":
            self.generate_challenge()
            return {
                "success": True,
                "message": "Next challenge..."
            }
        
        return {
            "success": False,
            "message": "Click outside of interactive areas"
        }
    
    def build_ui(self):
        """
        Build the UI components for the current state.
        
        Returns:
            UI: The UI instance with components
        """
        # Create base UI from parent class
        super().build_ui()
        
        # Clear existing components and build new ones
        self.ui.components = []
        
        # Add module name
        self.ui.add_component(self.ui.text(
            text=self.name,
            position=(self.screen_width // 2, 30),
            font_size=24,
            color=(255, 255, 255),
            align="center"
        ))
        
        # Add level and score
        self.ui.add_component(self.ui.text(
            text=f"Level: {self.level}",
            position=(20, 20),
            font_size=18,
            color=(200, 200, 200)
        ))
        
        self.ui.add_component(self.ui.text(
            text=f"Score: {self.score}",
            position=(self.screen_width - 20, 20),
            font_size=18,
            color=(200, 200, 200),
            align="right"
        ))
        
        # Add challenge type
        challenge_type_display = {
            "scales": "Scale Identification",
            "intervals": "Interval Identification",
            "chords": "Chord Identification"
        }.get(self.current_challenge_type, "Music Challenge")
        
        self.ui.add_component(self.ui.text(
            text=challenge_type_display,
            position=(self.screen_width // 2, 60),
            font_size=20,
            color=(180, 200, 255),
            align="center"
        ))
        
        # Add message if any
        if self.message:
            self.ui.add_component(self.ui.text(
                text=self.message,
                position=(self.screen_width // 2, self.screen_height - 30),
                font_size=18,
                color=(255, 255, 0),
                align="center"
            ))
        
        # Add play button
        play_button_y = 150
        self.ui.add_component(self.ui.button(
            text="Play Audio",
            position=(self.screen_width // 2, play_button_y),
            size=(200, 60),
            color=(60, 80, 120),
            hover_color=(80, 100, 150),
            text_color=(255, 255, 255)
        ))
        
        # Add options
        if self.current_options:
            # Calculate grid layout
            option_width = 300
            option_height = 60
            options_per_row = 2
            vertical_spacing = 20
            horizontal_spacing = 40
            
            grid_width = options_per_row * option_width + (options_per_row - 1) * horizontal_spacing
            start_x = (self.screen_width - grid_width) // 2 + option_width // 2
            start_y = 250
            
            for i, option in enumerate(self.current_options):
                row = i // options_per_row
                col = i % options_per_row
                
                x = start_x + col * (option_width + horizontal_spacing)
                y = start_y + row * (option_height + vertical_spacing)
                
                # Determine button color based on state and selection
                if self.state == "feedback" and option == self.user_answer:
                    color = (0, 150, 0) if option == self.correct_answer else (150, 0, 0)
                    hover_color = (0, 180, 0) if option == self.correct_answer else (180, 0, 0)
                else:
                    color = (60, 70, 100)
                    hover_color = (80, 90, 130)
                
                self.ui.add_component(self.ui.button(
                    text=option,
                    position=(x, y),
                    size=(option_width, option_height),
                    color=color,
                    hover_color=hover_color,
                    text_color=(255, 255, 255)
                ))
        
        # Add continue button during feedback
        if self.state == "feedback":
            self.ui.add_component(self.ui.button(
                text="Continue",
                position=(self.screen_width // 2, self.screen_height - 80),
                size=(150, 50),
                color=(80, 120, 80),
                hover_color=(100, 150, 100),
                text_color=(255, 255, 255)
            ))
        
        return self.ui
    
    def update(self, dt):
        """
        Update the module state.
        
        Args:
            dt: Time delta since last update in seconds.
        """
        # Transition back to challenge state after feedback delay
        if self.state == "feedback":
            # Wait for button click to proceed instead of automatic transition
            pass
    
    def get_module_state(self):
        """
        Get module-specific state.
        
        Returns:
            dict: A dictionary containing module-specific state.
        """
        # Get base module state
        base_state = super().get_module_state()
        
        # Create module-specific state
        module_state = {
            'challenge': {
                'type': self.current_challenge_type,
                'challenge': self.current_challenge,
                'options': self.current_options,
                'state': self.state,
                'message': self.message,
                'answer': self.correct_answer,
                'user_answer': self.user_answer
            },
            'progress': {
                'level': self.level,
                'max_level': self.max_level,
                'challenges_per_level': self.challenges_per_level,
                'current_level_challenges': self.current_level_challenges,
                'consecutive_correct': self.consecutive_correct
            }
        }
        
        # Merge states
        base_state.update(module_state)
        
        return base_state


# Register this module when imported
if __name__ != "__main__":
    # This import is here to avoid circular imports
    from MetaMindIQTrain.modules.module_provider import register_module
    register_module(MusicTheoryModule)

# Test function when run directly
if __name__ == "__main__":
    # Create and test the module
    module = MusicTheoryModule()
    print(f"Created module: {module.name}")
    print(f"Description: {module.description}")
    
    # Test challenge generation
    print("Generating a new challenge...")
    module.generate_challenge()
    print(f"Challenge type: {module.current_challenge_type}")
    print(f"Correct answer: {module.correct_answer}")
    print(f"Options: {module.current_options}")
    
    # Play the challenge if audio is available
    if AUDIO_AVAILABLE:
        print("Playing challenge sound...")
        module.play_current_challenge()
        
    # Get module state
    state = module.get_state()
    print("Module state generated") 