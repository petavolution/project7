#!/usr/bin/env python3
"""
Optimized Music Theory Training Module

A streamlined music theory training module that leverages the unified audio engine
and modern component architecture to provide an efficient and responsive user experience.
"""

import random
import time
import logging
from typing import Dict, Any, List, Tuple, Optional
from pathlib import Path

from MetaMindIQTrain.core.component_system import Component, UIComponent, Container, Text, Button
from MetaMindIQTrain.modules.music.audio_synthesis import AudioEngine, AUDIO_AVAILABLE, MusicTrainingModule
from MetaMindIQTrain.core.app_context import get_color, get_font_size, get_spacing

logger = logging.getLogger(__name__)

class MusicTheoryComponent(UIComponent):
    """Interactive music theory component with visual and audio feedback."""
    
    def __init__(self, component_id: Optional[str] = None):
        """Initialize the music theory component."""
        super().__init__(component_id)
        
        # Get audio engine singleton
        self.audio_engine = AudioEngine.get_instance()
        
        # UI properties
        self.set_property("background_color", get_color("background"))
        self.set_property("challenge_type", "scales")
        self.set_property("current_challenge", None)
        self.set_property("options", [])
        self.set_property("score", 0)
        self.set_property("level", 1)
        self.set_property("message", "Listen to the audio and identify the correct option")
        
        # Musical data
        self.scales = {
            "Major": [0, 2, 4, 5, 7, 9, 11, 12],
            "Minor": [0, 2, 3, 5, 7, 8, 10, 12],
            "Pentatonic": [0, 2, 4, 7, 9, 12],
            "Blues": [0, 3, 5, 6, 7, 10, 12]
        }
        
        self.intervals = {
            "Unison": 0,
            "Minor Second": 1,
            "Major Second": 2,
            "Minor Third": 3,
            "Major Third": 4,
            "Perfect Fourth": 5,
            "Perfect Fifth": 7,
            "Major Sixth": 9,
            "Minor Seventh": 10,
            "Octave": 12
        }
        
        self.chords = {
            "Major": [0, 4, 7],
            "Minor": [0, 3, 7],
            "Diminished": [0, 3, 6],
            "7th": [0, 4, 7, 10],
            "Major 7th": [0, 4, 7, 11]
        }
        
        # Difficulty levels
        self.difficulty_config = {
            1: {"options": 3, "types": ["scales"], "elements": ["Major", "Minor"]},
            2: {"options": 4, "types": ["scales", "intervals"], "elements": ["Major", "Minor", "Pentatonic"]},
            3: {"options": 4, "types": ["scales", "intervals", "chords"], "elements": ["Major", "Minor", "Pentatonic", "Blues"]},
            4: {"options": 5, "types": ["scales", "intervals", "chords"], "elements": list(self.scales.keys())},
            5: {"options": 6, "types": ["scales", "intervals", "chords"], "elements": list(self.scales.keys())}
        }
        
        # Create UI elements
        self._create_ui()
        
        # Generate initial challenge
        self.generate_challenge()
    
    def _create_ui(self):
        """Create UI elements for the music theory component."""
        # Create header
        header = Container("header")
        header.set_property("background_color", get_color("primary"))
        self.add_child(header)
        
        title = Text("title")
        title.set_text("Music Theory Training")
        title.set_font_size(get_font_size("heading"))
        title.set_property("color", get_color("text"))
        title.set_property("align", "center")
        header.add_child(title)
        
        # Level and score display
        stats = Container("stats")
        stats.set_property("background_color", None)
        self.add_child(stats)
        
        level_text = Text("level_text")
        level_text.set_text(f"Level: {self.get_property('level')}")
        level_text.set_font_size(get_font_size("normal"))
        level_text.set_property("color", get_color("text"))
        stats.add_child(level_text)
        
        score_text = Text("score_text")
        score_text.set_text(f"Score: {self.get_property('score')}")
        score_text.set_font_size(get_font_size("normal"))
        score_text.set_property("color", get_color("text"))
        score_text.set_property("align", "right")
        stats.add_child(score_text)
        
        # Challenge area
        challenge = Container("challenge")
        challenge.set_property("background_color", get_color("secondary"))
        self.add_child(challenge)
        
        challenge_text = Text("challenge_text")
        challenge_text.set_text("Identify the musical element:")
        challenge_text.set_font_size(get_font_size("normal"))
        challenge_text.set_property("color", get_color("text"))
        challenge_text.set_property("align", "center")
        challenge.add_child(challenge_text)
        
        # Play button
        play_button = Button("play_button")
        play_button.set_text("Play")
        play_button.set_size(120, 40)
        play_button.set_on_click(self._on_play_click)
        challenge.add_child(play_button)
        
        # Options area
        options = Container("options")
        options.set_property("background_color", None)
        self.add_child(options)
        
        # Message area
        message = Text("message")
        message.set_text(self.get_property("message"))
        message.set_font_size(get_font_size("normal"))
        message.set_property("color", get_color("accent"))
        message.set_property("align", "center")
        self.add_child(message)
        
        # Next button
        next_button = Button("next_button")
        next_button.set_text("Next Challenge")
        next_button.set_size(150, 40)
        next_button.set_on_click(self._on_next_click)
        next_button.set_visible(False)
        self.add_child(next_button)
    
    def on_mount(self):
        """Handle component mounting."""
        self._update_layout()
    
    def _update_layout(self):
        """Update the layout of UI components."""
        # Get container size
        width, height = self.get_size()
        
        # Header layout
        header = self.get_child("header")
        if header:
            header.set_size(width, 60)
            header.set_position(0, 0)
            
            title = header.get_child("title")
            if title:
                title.set_position(width // 2, 30)
        
        # Stats layout
        stats = self.get_child("stats")
        if stats:
            stats.set_size(width, 30)
            stats.set_position(0, 70)
            
            level_text = stats.get_child("level_text")
            if level_text:
                level_text.set_position(20, 15)
            
            score_text = stats.get_child("score_text")
            if score_text:
                score_text.set_position(width - 20, 15)
        
        # Challenge layout
        challenge = self.get_child("challenge")
        if challenge:
            challenge.set_size(width - 40, 100)
            challenge.set_position(20, 110)
            
            challenge_text = challenge.get_child("challenge_text")
            if challenge_text:
                challenge_text.set_position(challenge.get_size()[0] // 2, 30)
            
            play_button = challenge.get_child("play_button")
            if play_button:
                play_button.set_position(
                    (challenge.get_size()[0] - play_button.get_size()[0]) // 2, 
                    60
                )
        
        # Options layout
        options = self.get_child("options")
        if options:
            options.set_size(width - 40, 300)
            options.set_position(20, 220)
            
            # Layout option buttons
            self._update_options_layout()
        
        # Message layout
        message = self.get_child("message")
        if message:
            message.set_position(width // 2, height - 80)
        
        # Next button layout
        next_button = self.get_child("next_button")
        if next_button:
            next_button.set_position(
                (width - next_button.get_size()[0]) // 2,
                height - 50
            )
    
    def _update_options_layout(self):
        """Update the layout of option buttons."""
        options = self.get_child("options")
        if not options:
            return
        
        # Get options container size
        width, height = options.get_size()
        
        # Get current options
        option_elements = []
        for option in self.get_property("options"):
            option_btn = options.get_child(f"option_{option}")
            if option_btn:
                option_elements.append(option_btn)
        
        # Calculate button placement
        button_width = 200
        button_height = 50
        button_spacing = 20
        
        if option_elements:
            # Calculate grid layout
            num_options = len(option_elements)
            if num_options <= 4:
                # Single row layout
                total_width = num_options * button_width + (num_options - 1) * button_spacing
                start_x = (width - total_width) // 2
                y = (height - button_height) // 2
                
                for i, button in enumerate(option_elements):
                    x = start_x + i * (button_width + button_spacing)
                    button.set_position(x, y)
                    button.set_size(button_width, button_height)
            else:
                # Two row layout
                row1_count = num_options // 2
                row2_count = num_options - row1_count
                
                # First row
                total_width = row1_count * button_width + (row1_count - 1) * button_spacing
                start_x = (width - total_width) // 2
                y1 = height // 3 - button_height // 2
                
                for i in range(row1_count):
                    x = start_x + i * (button_width + button_spacing)
                    option_elements[i].set_position(x, y1)
                    option_elements[i].set_size(button_width, button_height)
                
                # Second row
                total_width = row2_count * button_width + (row2_count - 1) * button_spacing
                start_x = (width - total_width) // 2
                y2 = 2 * height // 3 - button_height // 2
                
                for i in range(row2_count):
                    x = start_x + i * (button_width + button_spacing)
                    option_elements[i + row1_count].set_position(x, y2)
                    option_elements[i + row1_count].set_size(button_width, button_height)
    
    def generate_challenge(self):
        """Generate a new musical challenge based on current level."""
        level = self.get_property("level")
        difficulty = self.difficulty_config[min(level, 5)]
        
        # Select challenge type
        available_types = difficulty["types"]
        challenge_type = random.choice(available_types)
        self.set_property("challenge_type", challenge_type)
        
        # Select available elements based on difficulty
        available_elements = difficulty["elements"]
        
        # Generate challenge based on type
        current_challenge = None
        correct_answer = None
        
        if challenge_type == "scales":
            # Select a scale
            scale_name = random.choice([s for s in available_elements if s in self.scales])
            root_note = f"{random.choice(['C', 'D', 'E', 'F', 'G', 'A', 'B'])}{random.randint(3, 5)}"
            
            current_challenge = {
                "type": "scale",
                "scale": scale_name,
                "root": root_note
            }
            
            correct_answer = scale_name
            
        elif challenge_type == "intervals":
            # Select an interval
            interval_name = random.choice([i for i in self.intervals.keys() if i not in ["Unison", "Octave"]])
            root_note = f"{random.choice(['C', 'D', 'E', 'F', 'G', 'A', 'B'])}{random.randint(3, 5)}"
            
            current_challenge = {
                "type": "interval",
                "interval": interval_name,
                "root": root_note
            }
            
            correct_answer = interval_name
            
        elif challenge_type == "chords":
            # Select a chord
            chord_name = random.choice([c for c in self.chords.keys()])
            root_note = f"{random.choice(['C', 'D', 'E', 'F', 'G', 'A', 'B'])}{random.randint(3, 5)}"
            
            current_challenge = {
                "type": "chord",
                "chord": chord_name,
                "root": root_note
            }
            
            correct_answer = chord_name
        
        # Generate options for multiple choice
        num_options = difficulty["options"]
        options = [correct_answer]
        
        if challenge_type == "scales":
            available_options = [s for s in self.scales.keys() if s in available_elements]
            while len(options) < num_options and len(available_options) > len(options):
                option = random.choice(available_options)
                if option not in options:
                    options.append(option)
                    
        elif challenge_type == "intervals":
            available_options = [i for i in self.intervals.keys() if i not in ["Unison", "Octave"]]
            while len(options) < num_options and len(available_options) > len(options):
                option = random.choice(available_options)
                if option not in options:
                    options.append(option)
                    
        elif challenge_type == "chords":
            available_options = list(self.chords.keys())
            while len(options) < num_options and len(available_options) > len(options):
                option = random.choice(available_options)
                if option not in options:
                    options.append(option)
        
        # Shuffle options
        random.shuffle(options)
        
        # Set properties
        self.set_property("current_challenge", current_challenge)
        self.set_property("options", options)
        self.set_property("correct_answer", correct_answer)
        self.set_property("answered", False)
        
        # Update UI
        self._update_challenge_ui()
        self._create_option_buttons()
        self._update_layout()
    
    def _update_challenge_ui(self):
        """Update the UI to reflect the current challenge."""
        challenge = self.get_child("challenge")
        if not challenge:
            return
            
        challenge_text = challenge.get_child("challenge_text")
        if not challenge_text:
            return
        
        current_challenge = self.get_property("current_challenge")
        if not current_challenge:
            return
            
        challenge_type = current_challenge.get("type")
        if challenge_type == "scale":
            text = f"Identify the scale (Root: {current_challenge['root']})"
        elif challenge_type == "interval":
            text = "Identify the interval"
        elif challenge_type == "chord":
            text = f"Identify the chord (Root: {current_challenge['root']})"
        else:
            text = "Listen and identify the musical element"
            
        challenge_text.set_text(text)
        
        # Hide next button and reset message
        next_button = self.get_child("next_button")
        if next_button:
            next_button.set_visible(False)
            
        message = self.get_child("message")
        if message:
            message.set_text("Listen to the audio and select the correct option")
            message.set_property("color", get_color("text"))
    
    def _create_option_buttons(self):
        """Create option buttons based on current options."""
        options_container = self.get_child("options")
        if not options_container:
            return
            
        # Clear existing options
        for child in options_container.get_children():
            options_container.remove_child(child)
            
        # Create new option buttons
        options = self.get_property("options")
        for option in options:
            button = Button(f"option_{option}")
            button.set_text(option)
            button.set_size(200, 50)
            button.set_property("option_value", option)
            button.set_on_click(self._on_option_click)
            options_container.add_child(button)
    
    def _on_play_click(self, button):
        """Handle play button click."""
        current_challenge = self.get_property("current_challenge")
        if not current_challenge:
            return
            
        # Stop any currently playing audio
        self.audio_engine.stop()
        
        # Play appropriate audio based on challenge type
        challenge_type = current_challenge.get("type")
        if challenge_type == "scale":
            self.audio_engine.play_scale(
                current_challenge["root"], 
                current_challenge["scale"],
                duration=0.3,
                volume=0.7
            )
        elif challenge_type == "interval":
            # Get interval semitones
            interval_name = current_challenge["interval"]
            semitones = self.intervals.get(interval_name, 0)
            
            # Get root note and calculate second note
            root_note = current_challenge["root"]
            root_freq = self.audio_engine.note_to_freq(root_note)
            second_freq = root_freq * (2 ** (semitones / 12))
            
            # Play notes sequentially
            root_wave = self.audio_engine.synthesize(root_freq, 0.5)
            self.audio_engine.play(root_wave, 0.7)
            time.sleep(0.6)
            
            second_wave = self.audio_engine.synthesize(second_freq, 0.5)
            self.audio_engine.play(second_wave, 0.7)
            
        elif challenge_type == "chord":
            # Get chord pattern
            chord_name = current_challenge["chord"]
            pattern = self.chords.get(chord_name, [0, 4, 7])
            
            # Play chord
            root_note = current_challenge["root"]
            root_freq = self.audio_engine.note_to_freq(root_note)
            
            # Create notes for the chord
            notes = []
            for semitones in pattern:
                freq = root_freq * (2 ** (semitones / 12))
                wave = self.audio_engine.synthesize(freq, 1.0)
                notes.append(wave)
            
            # Mix and play
            mixed = sum(notes) / len(notes)
            self.audio_engine.play(mixed, 0.7)
    
    def _on_option_click(self, button):
        """Handle option button click."""
        if self.get_property("answered"):
            return
            
        selected_option = button.get_property("option_value")
        correct_answer = self.get_property("correct_answer")
        
        # Mark as answered
        self.set_property("answered", True)
        
        # Check answer
        is_correct = selected_option == correct_answer
        
        # Update score
        current_score = self.get_property("score")
        if is_correct:
            new_score = current_score + 10
            self.set_property("score", new_score)
            
            # Update level if needed
            current_level = self.get_property("level")
            consecutive_correct = self.get_property("consecutive_correct", 0) + 1
            self.set_property("consecutive_correct", consecutive_correct)
            
            if consecutive_correct >= 3 and current_level < 5:
                new_level = current_level + 1
                self.set_property("level", new_level)
                self.set_property("consecutive_correct", 0)
                
                # Update level text
                stats = self.get_child("stats")
                if stats:
                    level_text = stats.get_child("level_text")
                    if level_text:
                        level_text.set_text(f"Level: {new_level}")
            
        else:
            # Reset consecutive correct counter
            self.set_property("consecutive_correct", 0)
        
        # Update score text
        stats = self.get_child("stats")
        if stats:
            score_text = stats.get_child("score_text")
            if score_text:
                score_text.set_text(f"Score: {self.get_property('score')}")
        
        # Update button colors
        options_container = self.get_child("options")
        if options_container:
            for child in options_container.get_children():
                option_value = child.get_property("option_value")
                
                if option_value == correct_answer:
                    # Correct answer - green
                    child.set_property("background_color", get_color("success"))
                elif option_value == selected_option and not is_correct:
                    # Wrong answer - red
                    child.set_property("background_color", get_color("error"))
        
        # Update feedback message
        message = self.get_child("message")
        if message:
            if is_correct:
                message.set_text("Correct! Well done!")
                message.set_property("color", get_color("success"))
            else:
                message.set_text(f"Incorrect. The answer was {correct_answer}")
                message.set_property("color", get_color("error"))
        
        # Show next button
        next_button = self.get_child("next_button")
        if next_button:
            next_button.set_visible(True)
    
    def _on_next_click(self, button):
        """Handle next button click."""
        # Generate a new challenge
        self.generate_challenge()

class MusicTheorySimplified(MusicTrainingModule):
    """Simplified Music Theory training module with optimized component structure."""
    
    def __init__(self, module_id: str = "music_theory_simplified"):
        """Initialize the music theory module."""
        super().__init__()
        
        # Module metadata
        self.id = module_id
        self.name = "Music Theory Training"
        self.description = "Train your ear and musical understanding with interactive exercises"
        
        # Create the main component
        self.main_component = MusicTheoryComponent("music_theory_component")
        self.add_child(self.main_component)
    
    def handle_click(self, x, y):
        """Handle mouse click events."""
        # The component system will handle the click events
        return {"handled": True}
    
    def on_mount(self):
        """Handle component mounting."""
        # Update the main component size
        width, height = self.get_size()
        self.main_component.set_size(width, height)
    
    def build_ui(self):
        """Build the UI components."""
        # The UI is handled by the component system
        return self.ui
    
    def update(self, dt):
        """Update game state."""
        # Game state updates are handled by the component system
        pass

def create_module(module_id: str = "music_theory_simplified", options: Dict[str, Any] = None) -> MusicTheorySimplified:
    """Create an instance of the Music Theory module.
    
    Args:
        module_id: Module ID
        options: Module options
        
    Returns:
        Music theory module instance
    """
    return MusicTheorySimplified(module_id) 