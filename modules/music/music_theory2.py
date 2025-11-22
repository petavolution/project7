#!/usr/bin/env python3
"""
Enhanced Music Theory Training Module (MusicTheory2)

This module extends the base MusicTheoryModule with enhanced multi-modal learning features:
- Advanced auditory pattern recognition exercises
- Working memory tasks for sequential musical patterns
- Cross-modal cognitive challenges (connecting sound to visual representation)
- Complex pattern recognition and categorization training

These enhancements aim to strengthen neural connections between auditory processing,
visual perception, and cognitive categorization systems.
"""

import random
import math
import time
import logging
import numpy as np
from typing import Dict, Any, List, Tuple, Optional
import sys
from pathlib import Path

# Import base music theory module
try:
    from MetaMindIQTrain.modules.music.music_theory import MusicTheoryModule
except ImportError:
    # When running directly
    import sys
    from pathlib import Path
    project_root = Path(__file__).parent.parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    from MetaMindIQTrain.modules.music.music_theory import MusicTheoryModule

# Configure logging
logger = logging.getLogger(__name__)

class EnhancedMusicTheoryModule(MusicTheoryModule):
    """
    Enhanced Music Theory module with multi-modal learning features.
    
    This module extends the base MusicTheory module with advanced exercises 
    that combine auditory and visual processing to strengthen cognitive abilities:
    - Enhanced auditory pattern recognition
    - Improved working memory for sequential patterns
    - Cross-modal cognitive integration
    - Complex pattern recognition and categorization
    """
    
    def __init__(self):
        """Initialize the Enhanced Music Theory module."""
        # Initialize base class
        super().__init__()
        
        # Override module metadata
        self.name = "Enhanced Music Theory"
        self.description = "Multi-modal music training for advanced cognitive development"
        self.category = "Music"
        self.difficulty = "Medium-Hard"
        
        # Additional challenge types
        self.challenge_types.extend([
            "pattern_completion", 
            "sequence_memory",
            "audio_visual_mapping",
            "pattern_categorization"
        ])
        
        # Visual representation settings
        self.visual_modes = {
            "piano_roll": True,        # Piano roll visualization
            "circle_of_fifths": True,  # Circle of fifths visualization
            "waveform": True,          # Audio waveform visualization
            "spectrogram": False,      # Spectrogram (requires additional libraries)
            "notation": True           # Musical notation
        }
        
        # Pattern memory settings
        self.max_sequence_length = 8
        self.current_sequence = []
        self.user_sequence = []
        
        # Pattern recognition settings
        self.pattern_categories = {
            "ascending": "Pattern moves consistently upward",
            "descending": "Pattern moves consistently downward",
            "arpeggiated": "Pattern follows chord tones",
            "scalar": "Pattern follows a scale",
            "chromatic": "Pattern uses chromatic (half-step) movement",
            "repetition": "Pattern contains repeated elements",
            "mirror": "Pattern contains mirrored/reflection elements"
        }
        
        # Cross-modal mapping
        self.color_to_note_mapping = {
            "C": (255, 0, 0),     # Red
            "D": (255, 165, 0),   # Orange
            "E": (255, 255, 0),   # Yellow
            "F": (0, 255, 0),     # Green
            "G": (0, 0, 255),     # Blue
            "A": (75, 0, 130),    # Indigo
            "B": (143, 0, 255)    # Violet
        }
        
        # Working memory enhancement
        self.memory_levels = {
            1: {"sequence_length": 3, "replay_count": 1, "tempo": 80},
            2: {"sequence_length": 4, "replay_count": 1, "tempo": 90},
            3: {"sequence_length": 5, "replay_count": 1, "tempo": 100},
            4: {"sequence_length": 6, "replay_count": 1, "tempo": 110},
            5: {"sequence_length": 8, "replay_count": 1, "tempo": 120}
        }
    
    def generate_challenge(self):
        """Generate a challenge with enhanced multi-modal features."""
        # First check if we should generate a standard challenge or enhanced challenge
        # For levels 1-3, use standard challenges 70% of the time
        # For levels 4-5, use standard challenges 40% of the time
        use_standard = random.random() < (0.7 if self.level <= 3 else 0.4)
        
        if use_standard:
            # Use the base class challenge generation
            super().generate_challenge()
        else:
            # Generate enhanced challenges
            difficulty = self.difficulties[min(self.level, self.max_level)]
            
            # Select an enhanced challenge type
            enhanced_types = [
                "pattern_completion", 
                "sequence_memory",
                "audio_visual_mapping",
                "pattern_categorization"
            ]
            self.current_challenge_type = random.choice(enhanced_types)
            
            # Generate the specific enhanced challenge
            if self.current_challenge_type == "pattern_completion":
                self._generate_pattern_completion_challenge()
            elif self.current_challenge_type == "sequence_memory":
                self._generate_sequence_memory_challenge()
            elif self.current_challenge_type == "audio_visual_mapping":
                self._generate_audio_visual_mapping_challenge()
            elif self.current_challenge_type == "pattern_categorization":
                self._generate_pattern_categorization_challenge()
            
            # Set appropriate message
            self._set_challenge_message()
    
    def _generate_pattern_completion_challenge(self):
        """
        Generate a pattern completion challenge.
        
        This challenge presents a musical pattern with missing elements
        that the user must identify to complete the pattern.
        """
        # Determine pattern type (scale, arpeggio, etc.)
        pattern_types = ["scale", "arpeggio", "interval_pattern"]
        pattern_type = random.choice(pattern_types)
        
        # Create a musical pattern with gaps
        if pattern_type == "scale":
            # Generate a scale with missing notes
            scale_name = random.choice(list(self.scales.keys()))
            scale = self.scales[scale_name]
            root_note = random.randint(48, 60)
            
            # Create full pattern
            full_pattern = [root_note + note for note in scale]
            
            # Remove 1-3 notes to create gaps
            num_gaps = min(3, max(1, len(full_pattern) // 3))
            gap_indices = random.sample(range(1, len(full_pattern) - 1), num_gaps)
            
            # Create pattern with gaps and store missing notes
            pattern_with_gaps = full_pattern.copy()
            missing_notes = []
            
            for idx in sorted(gap_indices, reverse=True):
                missing_notes.append(pattern_with_gaps[idx])
                pattern_with_gaps[idx] = None
            
            # Store the challenge
            self.current_challenge = {
                "type": "pattern_completion",
                "pattern_type": "scale",
                "name": scale_name,
                "full_pattern": full_pattern,
                "pattern_with_gaps": pattern_with_gaps,
                "missing_notes": missing_notes,
                "root": root_note
            }
            
            # Generate options (the correct missing notes plus distractors)
            self.current_options = [(note, self._midi_to_note_name(note)) for note in missing_notes]
            
            # Add distractors (incorrect options)
            distractors = []
            for _ in range(min(4, len(self.current_options) + 2)):
                # Generate plausible but incorrect notes
                distractor = root_note + random.choice(range(12))
                if distractor not in missing_notes and distractor not in [d[0] for d in distractors]:
                    distractors.append((distractor, self._midi_to_note_name(distractor)))
            
            self.current_options.extend(distractors)
            random.shuffle(self.current_options)
            
            # Set correct answer (simplistic - this would need refinement)
            self.correct_answer = self.current_options[0]
        
        elif pattern_type == "arpeggio":
            # Similar implementation for arpeggios
            # Placeholder for future implementation
            self._generate_pattern_completion_challenge()  # Retry with a different type
            
        elif pattern_type == "interval_pattern":
            # Similar implementation for interval patterns
            # Placeholder for future implementation
            self._generate_pattern_completion_challenge()  # Retry with a different type
    
    def _generate_sequence_memory_challenge(self):
        """
        Generate a sequence memory challenge.
        
        This challenge presents a musical sequence that the user
        must memorize and reproduce, enhancing working memory.
        """
        # Get sequence parameters based on level
        memory_level = self.memory_levels[min(self.level, self.max_level)]
        sequence_length = memory_level["sequence_length"]
        tempo = memory_level["tempo"]
        
        # Generate a sequence of notes
        root_note = random.randint(48, 60)
        
        # Use a musical scale as the source for notes
        scale_name = random.choice(["Major", "Minor", "Pentatonic"])
        scale = self.scales[scale_name]
        
        # Generate a melodic sequence from the scale
        sequence = []
        for _ in range(sequence_length):
            note_offset = random.choice(scale)
            sequence.append(root_note + note_offset)
        
        # Store the sequence as the challenge
        self.current_challenge = {
            "type": "sequence_memory",
            "sequence": sequence,
            "sequence_length": sequence_length,
            "tempo": tempo,
            "scale_name": scale_name,
            "root": root_note
        }
        
        # For sequence memory, options are the possible notes to select
        # This would typically be implemented in the UI as clickable piano keys
        self.current_options = []
        for offset in scale:
            note = root_note + offset
            self.current_options.append((note, self._midi_to_note_name(note)))
        
        # The correct answer is the full sequence
        self.correct_answer = sequence
        
        # Reset user's sequence input
        self.user_sequence = []
    
    def _generate_audio_visual_mapping_challenge(self):
        """
        Generate an audio-visual mapping challenge.
        
        This challenge trains the connection between auditory and visual
        processing by requiring matching of sounds to visual representations.
        """
        # Choose mapping type
        mapping_types = ["color_to_note", "shape_to_interval", "position_to_pitch"]
        mapping_type = random.choice(mapping_types)
        
        if mapping_type == "color_to_note":
            # Select a random note
            note_name = random.choice(list(self.color_to_note_mapping.keys()))
            note_color = self.color_to_note_mapping[note_name]
            
            # Calculate MIDI note number (in 4th octave)
            note_map = {"C": 60, "D": 62, "E": 64, "F": 65, "G": 67, "A": 69, "B": 71}
            midi_note = note_map[note_name]
            
            # Create challenge
            self.current_challenge = {
                "type": "audio_visual_mapping",
                "mapping_type": "color_to_note",
                "note_name": note_name,
                "note_color": note_color,
                "midi_note": midi_note
            }
            
            # Options are various colors
            self.current_options = list(self.color_to_note_mapping.items())
            random.shuffle(self.current_options)
            
            # Correct answer is the matching color
            self.correct_answer = (note_name, note_color)
            
        elif mapping_type == "shape_to_interval":
            # Placeholder for future implementation
            self._generate_audio_visual_mapping_challenge()  # Retry with a different type
            
        elif mapping_type == "position_to_pitch":
            # Placeholder for future implementation  
            self._generate_audio_visual_mapping_challenge()  # Retry with a different type
    
    def _generate_pattern_categorization_challenge(self):
        """
        Generate a pattern categorization challenge.
        
        This challenge trains the ability to recognize and categorize
        musical patterns based on their characteristics.
        """
        # Select a category to identify
        category = random.choice(list(self.pattern_categories.keys()))
        category_description = self.pattern_categories[category]
        
        # Generate a pattern matching this category
        root_note = random.randint(48, 60)
        pattern = []
        
        if category == "ascending":
            # Generate ascending pattern
            steps = random.sample([1, 2, 3, 4], k=4)
            current = root_note
            pattern = [current]
            for step in steps:
                current += step
                pattern.append(current)
                
        elif category == "descending":
            # Generate descending pattern
            steps = random.sample([1, 2, 3, 4], k=4)
            current = root_note + 12  # Start higher to have room to descend
            pattern = [current]
            for step in steps:
                current -= step
                pattern.append(current)
                
        elif category == "arpeggiated":
            # Generate pattern following chord tones
            chord_name = random.choice(list(self.chords.keys()))
            chord = self.chords[chord_name]
            pattern = [root_note + note for note in chord]
            # Add some repetition or octave jumps
            pattern = pattern + [pattern[0] + 12, pattern[1] + 12]
            
        elif category == "scalar":
            # Generate pattern following a scale
            scale_name = random.choice(list(self.scales.keys()))
            scale = self.scales[scale_name]
            pattern = [root_note + scale[i] for i in random.sample(range(len(scale)), min(5, len(scale)))]
            
        elif category == "chromatic":
            # Generate chromatic pattern
            direction = random.choice([1, -1])  # Up or down
            pattern = [root_note + i * direction for i in range(5)]
            
        elif category == "repetition":
            # Generate pattern with repetitions
            base_notes = [root_note + i for i in random.sample(range(5), 3)]
            pattern = base_notes + [base_notes[0], base_notes[1]]
            
        elif category == "mirror":
            # Generate mirrored pattern
            first_half = [root_note + i for i in random.sample(range(6), 3)]
            second_half = first_half.copy()
            second_half.reverse()
            pattern = first_half + second_half
        
        # Store the challenge
        self.current_challenge = {
            "type": "pattern_categorization",
            "category": category,
            "category_description": category_description,
            "pattern": pattern,
            "root": root_note
        }
        
        # Options are different categories
        self.current_options = list(self.pattern_categories.keys())
        random.shuffle(self.current_options)
        
        # Correct answer is the pattern category
        self.correct_answer = category
    
    def _set_challenge_message(self):
        """Set appropriate challenge message based on challenge type."""
        if self.current_challenge_type == "pattern_completion":
            self.message = "Listen to the pattern and identify the missing notes"
        elif self.current_challenge_type == "sequence_memory":
            self.message = "Memorize the sequence and repeat it back"
        elif self.current_challenge_type == "audio_visual_mapping":
            self.message = "Match the sound with its visual representation"
        elif self.current_challenge_type == "pattern_categorization":
            self.message = "Listen to the pattern and identify its category"
        else:
            self.message = "Listen carefully to the audio challenge"
    
    def play_current_challenge(self):
        """Play the current challenge audio with enhanced features."""
        if self.current_challenge_type in ["scales", "intervals", "chords"]:
            # Use base class implementation for standard challenges
            return super().play_current_challenge()
            
        elif self.current_challenge_type == "pattern_completion":
            # Play pattern with gaps (silent for missing notes)
            if not self.current_challenge:
                return False
                
            for note in self.current_challenge["pattern_with_gaps"]:
                if note is not None:
                    frequency = self._midi_to_frequency(note)
                    self.play_sound(frequency, duration=self.duration, volume=self.volume)
                else:
                    # Silent gap for missing note
                    time.sleep(self.duration)
                    
                # Short pause between notes
                time.sleep(self.duration * 0.2)
                
            return True
            
        elif self.current_challenge_type == "sequence_memory":
            # Play the sequence for memorization
            if not self.current_challenge:
                return False
                
            # Calculate note duration based on tempo
            tempo = self.current_challenge["tempo"]
            note_duration = 60 / tempo
            
            for note in self.current_challenge["sequence"]:
                frequency = self._midi_to_frequency(note)
                self.play_sound(frequency, duration=note_duration, volume=self.volume)
                # No pause between notes - timing is controlled by note duration
                
            return True
            
        elif self.current_challenge_type == "audio_visual_mapping":
            # Play the note to match with visual element
            if not self.current_challenge:
                return False
                
            if self.current_challenge["mapping_type"] == "color_to_note":
                midi_note = self.current_challenge["midi_note"]
                frequency = self._midi_to_frequency(midi_note)
                self.play_sound(frequency, duration=self.duration, volume=self.volume)
                return True
                
            return False
            
        elif self.current_challenge_type == "pattern_categorization":
            # Play the pattern to categorize
            if not self.current_challenge:
                return False
                
            for note in self.current_challenge["pattern"]:
                frequency = self._midi_to_frequency(note)
                self.play_sound(frequency, duration=self.duration, volume=self.volume)
                # Short pause between notes
                time.sleep(self.duration * 0.1)
                
            return True
            
        return False
    
    def handle_sequence_input(self, note):
        """
        Handle user input for sequence memory challenges.
        
        Args:
            note: The note input by the user
            
        Returns:
            dict: Status of the sequence input
        """
        if self.current_challenge_type != "sequence_memory":
            return {"success": False, "message": "Not a sequence memory challenge"}
            
        # Add the note to the user's sequence
        self.user_sequence.append(note)
        
        # Check if the sequence is complete
        if len(self.user_sequence) >= len(self.current_challenge["sequence"]):
            # Compare sequences
            correct = True
            for i, note in enumerate(self.current_challenge["sequence"]):
                if i >= len(self.user_sequence) or self.user_sequence[i] != note:
                    correct = False
                    break
                    
            # Reset user sequence
            self.user_sequence = []
            
            if correct:
                self.score += 100 * self.level
                return {
                    "success": True,
                    "complete": True,
                    "correct": True,
                    "message": "Correct sequence!"
                }
            else:
                return {
                    "success": True,
                    "complete": True,
                    "correct": False,
                    "message": "Incorrect sequence. Try again."
                }
                
        # Sequence not complete yet
        return {
            "success": True,
            "complete": False,
            "count": len(self.user_sequence),
            "total": len(self.current_challenge["sequence"]),
            "message": f"Note {len(self.user_sequence)} of {len(self.current_challenge['sequence'])}"
        }
    
    def render_piano_roll(self, width, height):
        """
        Generate data for rendering a piano roll visualization.
        
        Args:
            width: Available width for rendering
            height: Available height for rendering
            
        Returns:
            dict: Piano roll rendering data
        """
        # This would return data for the UI to render a piano roll
        # Implementation would depend on the specific challenge
        
        if not self.current_challenge:
            return {"success": False}
            
        if self.current_challenge_type == "scales":
            # For scale challenges
            scale_name = self.current_challenge["name"]
            
            if "use_midi" in self.current_challenge and self.current_challenge["use_midi"]:
                # MIDI-based challenge
                root = self.current_challenge["root"]
                scale = self.scales[scale_name]
                notes = [root + note for note in scale]
            else:
                # Note name-based challenge
                root_note = self.current_challenge["root_note"]
                # Convert note name to MIDI
                root = self._note_name_to_midi(root_note)
                scale = self.scales[scale_name]
                notes = [root + note for note in scale]
            
            # Piano roll spans roughly 2 octaves (24 keys)
            start_key = max(0, root - 6)
            end_key = start_key + 24
            
            return {
                "success": True,
                "start_key": start_key,
                "end_key": end_key,
                "notes": notes,
                "highlighted_keys": notes
            }
            
        # Similar implementations for other challenge types
        return {"success": False, "message": "Piano roll not available for this challenge"}
    
    def render_circle_of_fifths(self):
        """
        Generate data for rendering a circle of fifths visualization.
        
        Returns:
            dict: Circle of fifths rendering data
        """
        # This would return data for the UI to render a circle of fifths
        
        if not self.current_challenge:
            return {"success": False}
        
        # Circle of fifths order: C, G, D, A, E, B, F#, C#/Db, Ab, Eb, Bb, F
        circle = ["C", "G", "D", "A", "E", "B", "F#", "C#", "G#", "D#", "A#", "F"]
        
        # Determine which notes to highlight based on challenge type
        highlighted = []
        
        if self.current_challenge_type == "scales":
            scale_name = self.current_challenge["name"]
            
            # Different scales highlight different sections of the circle
            if scale_name == "Major":
                # For C Major, highlight C and neighbors
                highlighted = ["C", "G", "F"] 
            elif scale_name == "Minor":
                # For A Minor (relative of C Major), highlight A and neighbors
                highlighted = ["A", "E", "D"]
            # Other scales would have their own patterns
            
        return {
            "success": True,
            "circle": circle,
            "highlighted": highlighted
        }
    
    def render_waveform(self, width, height):
        """
        Generate data for rendering an audio waveform visualization.
        
        Args:
            width: Available width for rendering
            height: Available height for rendering
            
        Returns:
            dict: Waveform rendering data
        """
        # This would return data for the UI to render a waveform
        # In a real implementation, this might calculate actual waveform data
        # For this stub, we'll return placeholder data
        
        # Generate simple sine wave data as placeholder
        sample_rate = 44100
        duration = 2.0
        points = []
        
        if self.current_challenge_type == "intervals":
            # Generate different waveform patterns for intervals
            if "notes" in self.current_challenge:
                notes = self.current_challenge["notes"]
                frequencies = [self._midi_to_frequency(note) for note in notes]
                
                # Generate composite waveform (simplified)
                for i in range(int(width)):
                    t = i / width * duration
                    value = 0
                    for freq in frequencies:
                        value += math.sin(2 * math.pi * freq * t)
                    # Normalize and scale to height
                    value = value / len(frequencies)
                    value = value * height/3 + height/2
                    points.append((i, value))
        
        return {
            "success": True,
            "points": points,
            "color": (0, 120, 255)
        }
    
    def _note_name_to_midi(self, note_name):
        """Convert a note name (e.g., 'C4') to MIDI note number."""
        note_map = {"C": 0, "C#": 1, "D": 2, "D#": 3, "E": 4, "F": 5, 
                   "F#": 6, "G": 7, "G#": 8, "A": 9, "A#": 10, "B": 11}
        
        # Parse note and octave
        if len(note_name) < 2:
            return 60  # Default to middle C
            
        note = note_name[:-1]  # Everything except the last character
        octave = int(note_name[-1])  # Last character is the octave
        
        # Calculate MIDI note number
        midi_note = (octave + 1) * 12 + note_map.get(note, 0)
        return midi_note
    
    def build_ui(self):
        """
        Build enhanced UI with multi-modal visualization elements.
        
        Returns:
            UI: The UI instance with enhanced components
        """
        # First build the base UI
        super().build_ui()
        
        # Add enhanced visualization controls based on challenge type
        if self.current_challenge_type in ["pattern_completion", "sequence_memory", 
                                          "audio_visual_mapping", "pattern_categorization"]:
            # Add visualization toggle buttons
            viz_y = 100
            button_width = 150
            button_spacing = 20
            
            # Calculate positions for visualization toggle buttons
            total_width = len(self.visual_modes) * (button_width + button_spacing) - button_spacing
            start_x = (self.screen_width - total_width) // 2
            
            i = 0
            for viz_name, enabled in self.visual_modes.items():
                # Only show enabled visualizations
                if enabled:
                    viz_text = viz_name.replace('_', ' ').title()
                    x = start_x + i * (button_width + button_spacing)
                    
                    self.ui.add_component(self.ui.button(
                        text=viz_text,
                        position=(x, viz_y),
                        size=(button_width, 30),
                        color=(40, 60, 100),
                        hover_color=(60, 80, 120),
                        text_color=(200, 200, 255)
                    ))
                    i += 1
        
        return self.ui
    
    def get_module_state(self):
        """
        Get enhanced module-specific state.
        
        Returns:
            dict: A dictionary containing module-specific state.
        """
        # Get base state
        state = super().get_module_state()
        
        # Add enhanced state information
        enhanced_state = {
            'enhanced_features': {
                'visual_modes': self.visual_modes,
                'current_visualization': 'piano_roll'  # Default visualization
            }
        }
        
        # Add challenge-specific enhanced state
        if self.current_challenge_type == "sequence_memory":
            enhanced_state['sequence_memory'] = {
                'user_sequence': self.user_sequence,
                'sequence_length': len(self.current_challenge.get("sequence", [])),
                'completed': len(self.user_sequence) >= len(self.current_challenge.get("sequence", []))
            }
        
        # Merge with base state
        state.update(enhanced_state)
        
        return state


# Register this module when imported
if __name__ != "__main__":
    # This import is here to avoid circular imports
    from MetaMindIQTrain.modules.module_provider import register_module
    register_module(EnhancedMusicTheoryModule)

# Test function when run directly
if __name__ == "__main__":
    # Create and test the module
    module = EnhancedMusicTheoryModule()
    print(f"Created module: {module.name}")
    print(f"Description: {module.description}")
    
    # Test challenge generation
    print("Generating a new challenge...")
    module.generate_challenge()
    print(f"Challenge type: {module.current_challenge_type}")
    
    # Test playing the challenge
    print("Playing challenge...")
    module.play_current_challenge()
    
    # Test visualization
    print("Visualization modes:")
    for viz_name, enabled in module.visual_modes.items():
        status = "Enabled" if enabled else "Disabled"
        print(f"- {viz_name}: {status}")
    
    print("Module testing complete") 