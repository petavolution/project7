#!/usr/bin/env python3
"""
Music Training Module Base Class

This module provides the base class for all music-related training modules
in the MetaMindIQTrain platform. It builds on the core TrainingModule
with music-specific capabilities.
"""

import logging
import sys
import random
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Union

# Add parent directory to path for direct execution
if __name__ == "__main__" or not __package__:
    project_root = Path(__file__).parent.parent.parent
    sys.path.insert(0, str(project_root))
    from MetaMindIQTrain.core.training_module import TrainingModule
    from MetaMindIQTrain.core.audio.engine import get_audio_engine
else:
    # Use relative imports when imported as a module
    from ...core.training_module import TrainingModule
    from ...core.audio.engine import get_audio_engine

# Configure logging
logger = logging.getLogger(__name__)

# Musical constants and utilities
NOTES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
MIDI_BASE = 12  # MIDI note number for C0

# Common scales
SCALES = {
    "Major": [0, 2, 4, 5, 7, 9, 11],
    "Minor": [0, 2, 3, 5, 7, 8, 10],
    "Pentatonic": [0, 2, 4, 7, 9],
    "Blues": [0, 3, 5, 6, 7, 10],
    "Chromatic": list(range(12)),
    "Whole Tone": [0, 2, 4, 6, 8, 10],
    "Dorian": [0, 2, 3, 5, 7, 9, 10],
    "Phrygian": [0, 1, 3, 5, 7, 8, 10],
    "Lydian": [0, 2, 4, 6, 7, 9, 11],
    "Mixolydian": [0, 2, 4, 5, 7, 9, 10],
    "Locrian": [0, 1, 3, 5, 6, 8, 10],
}

# Common intervals
INTERVALS = {
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

# Common chords
CHORDS = {
    "Major": [0, 4, 7],
    "Minor": [0, 3, 7],
    "Diminished": [0, 3, 6],
    "Augmented": [0, 4, 8],
    "Suspended 4th": [0, 5, 7],
    "Dominant 7th": [0, 4, 7, 10],
    "Major 7th": [0, 4, 7, 11],
    "Minor 7th": [0, 3, 7, 10],
    "Half Diminished": [0, 3, 6, 10],
    "Diminished 7th": [0, 3, 6, 9]
}

class MusicTrainingModule(TrainingModule):
    """
    Base class for all music training modules.
    
    This class extends the core TrainingModule with music-specific
    functionality, including note generation, audio synthesis,
    and common musical operations.
    """
    
    def __init__(self):
        """Initialize the music training module."""
        # Initialize the base module
        super().__init__()
        
        # Initialize audio engine
        self.audio_engine = get_audio_engine()
        
        # Common audio settings with reasonable defaults
        self.volume = 0.5
        self.duration = 0.5  # Default note duration in seconds
        self.waveform = 'sine'  # Default waveform type
        
        # Default ADSR envelope
        self.envelope = {
            'attack': 0.01,
            'decay': 0.05,
            'sustain': 0.7,
            'release': 0.1
        }
        
        # Module metadata (to be overridden by subclasses)
        self.category = "Music"
        
        # Common UI components
        self.piano_visible = False
        self.staff_visible = False
        self.guitar_visible = False
        
        # Create piano keyboard (hidden by default)
        self.piano_keys = []
        self._init_piano()
        
        logger.info(f"Initialized music training module using {self.audio_engine.get_backend_name()}")
    
    def _init_piano(self):
        """Initialize the piano keyboard data structure."""
        # Initialize a standard piano keyboard (2 octaves centered around middle C)
        octave_start = 4  # Middle C (C4)
        num_octaves = 2
        
        # Create the keys
        self.piano_keys = []
        for octave in range(octave_start, octave_start + num_octaves):
            for note_idx, note_name in enumerate(NOTES):
                # Calculate MIDI note number
                midi_note = MIDI_BASE + (octave * 12) + note_idx
                
                # Calculate frequency using equal temperament formula: f = 440 * 2^((n-69)/12)
                frequency = 440.0 * (2 ** ((midi_note - 69) / 12))
                
                # Determine if it's a white or black key
                is_black = '#' in note_name
                
                self.piano_keys.append({
                    'note_name': f"{note_name}{octave}",
                    'midi_note': midi_note,
                    'frequency': frequency,
                    'is_black': is_black,
                    'highlighted': False
                })
    
    def play_note(self, note, duration=None):
        """Play a single note.
        
        Args:
            note: Either a MIDI note number, a frequency, or a note name (e.g., 'C4')
            duration: Duration in seconds (or uses default if None)
        """
        if duration is None:
            duration = self.duration
            
        # Convert note to frequency if needed
        frequency = self._note_to_frequency(note)
        
        # Play the note using the audio engine
        if frequency > 0:
            self.audio_engine.play_note(
                frequency, 
                duration=duration,
                envelope=self.envelope,
                waveform=self.waveform
            )
    
    def play_chord(self, root_note, chord_type="Major", duration=None):
        """Play a chord.
        
        Args:
            root_note: Root note (MIDI, frequency, or name)
            chord_type: Type of chord from CHORDS dictionary
            duration: Duration in seconds (or uses default if None)
        """
        if duration is None:
            duration = self.duration
            
        # Get root frequency
        root_freq = self._note_to_frequency(root_note)
        
        # Get chord intervals
        intervals = CHORDS.get(chord_type, CHORDS["Major"])
        
        # Calculate all frequencies in the chord
        frequencies = [root_freq * (2 ** (interval / 12)) for interval in intervals]
        
        # Play the chord
        self.audio_engine.play_chord(
            frequencies,
            duration=duration,
            envelope=self.envelope,
            waveform=self.waveform
        )
    
    def play_scale(self, root_note, scale_type="Major", duration=0.2, ascending=True):
        """Play a scale.
        
        Args:
            root_note: Root note (MIDI, frequency, or name)
            scale_type: Type of scale from SCALES dictionary
            duration: Duration of each note
            ascending: Whether to play ascending (True) or descending (False)
        """
        # Get scale intervals
        intervals = SCALES.get(scale_type, SCALES["Major"])
        
        # Convert root note to MIDI if it's not already
        if isinstance(root_note, str):  # Note name
            root_midi = self._note_name_to_midi(root_note)
        elif isinstance(root_note, float):  # Frequency
            root_midi = self._frequency_to_midi(root_note)
        else:  # MIDI number
            root_midi = root_note
        
        # Generate MIDI notes for the scale
        scale_midi = [root_midi + interval for interval in intervals]
        
        # Add the octave if not chromatic
        if scale_type != "Chromatic":
            scale_midi.append(root_midi + 12)
        
        # Reverse if descending
        if not ascending:
            scale_midi.reverse()
        
        # Convert to frequencies
        frequencies = [440.0 * (2 ** ((midi - 69) / 12)) for midi in scale_midi]
        
        # Create durations list (all the same)
        durations = [duration] * len(frequencies)
        
        # Play as a sequence
        self.audio_engine.play_sequence(
            frequencies,
            durations,
            interval=0.05,
            envelope=self.envelope,
            waveform=self.waveform
        )
    
    def highlight_piano_keys(self, notes, highlight=True):
        """Highlight keys on the piano.
        
        Args:
            notes: List of notes to highlight (MIDI, frequency, or name)
            highlight: Whether to highlight (True) or unhighlight (False)
        """
        # Convert all notes to MIDI numbers for comparison
        midi_notes = []
        for note in notes:
            if isinstance(note, str):  # Note name
                midi_notes.append(self._note_name_to_midi(note))
            elif isinstance(note, float):  # Frequency
                midi_notes.append(self._frequency_to_midi(note))
            else:  # MIDI number
                midi_notes.append(note)
        
        # Update piano key highlighting
        for key in self.piano_keys:
            if key['midi_note'] in midi_notes:
                key['highlighted'] = highlight
    
    def _note_to_frequency(self, note) -> float:
        """Convert a note to its frequency.
        
        Args:
            note: Either a MIDI note number, a frequency, or a note name (e.g., 'C4')
            
        Returns:
            Frequency in Hz
        """
        if isinstance(note, str):  # Note name
            # Convert note name to MIDI
            midi_note = self._note_name_to_midi(note)
            if midi_note is None:
                return 0
            
            # Calculate frequency
            return 440.0 * (2 ** ((midi_note - 69) / 12))
            
        elif isinstance(note, float):  # Already a frequency
            return note
            
        else:  # MIDI note number
            return 440.0 * (2 ** ((note - 69) / 12))
    
    def _note_name_to_midi(self, note_name) -> Optional[int]:
        """Convert a note name to MIDI note number.
        
        Args:
            note_name: Note name with octave (e.g., 'C4', 'F#5')
            
        Returns:
            MIDI note number or None if invalid
        """
        try:
            # Split into note and octave
            if len(note_name) == 2:
                note = note_name[0]
                octave = int(note_name[1])
            elif len(note_name) == 3:
                note = note_name[:2]  # Note with accidental
                octave = int(note_name[2])
            else:
                logger.warning(f"Invalid note name: {note_name}")
                return None
            
            # Get the index of the note in our list
            if note in NOTES:
                note_idx = NOTES.index(note)
            else:
                # Handle alternative notations (e.g., 'Db' instead of 'C#')
                flat_to_sharp = {'Db': 'C#', 'Eb': 'D#', 'Gb': 'F#', 'Ab': 'G#', 'Bb': 'A#'}
                if note in flat_to_sharp:
                    note_idx = NOTES.index(flat_to_sharp[note])
                else:
                    logger.warning(f"Invalid note: {note}")
                    return None
            
            # Calculate MIDI note number
            midi_note = MIDI_BASE + (octave * 12) + note_idx
            return midi_note
            
        except (ValueError, IndexError) as e:
            logger.warning(f"Error parsing note name {note_name}: {e}")
            return None
    
    def _frequency_to_midi(self, frequency) -> int:
        """Convert a frequency to the closest MIDI note number.
        
        Args:
            frequency: Frequency in Hz
            
        Returns:
            Closest MIDI note number
        """
        # Use the formula: MIDI = 69 + 12 * log2(f/440)
        import math
        if frequency <= 0:
            return 0
        return round(69 + 12 * math.log2(frequency / 440.0))
    
    def build_ui(self):
        """
        Build the UI components for the current state.
        
        This method overrides the base implementation to add music-specific
        UI components like the piano keyboard.
        
        Returns:
            UI: The UI instance with components
        """
        # First build the standard UI from the base class
        super().build_ui()
        
        # Add music-specific UI elements
        if self.piano_visible:
            self._add_piano_to_ui()
        
        if self.staff_visible:
            self._add_staff_to_ui()
        
        if self.guitar_visible:
            self._add_guitar_to_ui()
        
        return self.ui
    
    def _add_piano_to_ui(self):
        """Add piano keyboard to the UI."""
        # Calculate piano dimensions
        key_width = 24
        white_key_height = 100
        black_key_height = 65
        
        # Calculate starting x position to center the piano
        white_key_count = sum(1 for key in self.piano_keys if not key['is_black'])
        piano_width = white_key_count * key_width
        start_x = (self.screen_width - piano_width) // 2
        
        # Piano container
        self.ui.add_component(self.ui.container(
            id="piano_container",
            position=(start_x, self.screen_height - 150),
            size=(piano_width, white_key_height),
            children=[]
        ))
        
        # Add white keys first (so they're behind black keys)
        white_index = 0
        for i, key in enumerate(self.piano_keys):
            if not key['is_black']:
                # Determine key color based on highlighting
                key_color = (200, 200, 255) if key['highlighted'] else (255, 255, 255)
                
                self.ui.add_component(self.ui.rectangle(
                    id=f"piano_key_{i}",
                    position=(start_x + (white_index * key_width), self.screen_height - 150),
                    size=(key_width, white_key_height),
                    color=key_color,
                    border_color=(0, 0, 0),
                    border_width=1,
                    data={"note": key['note_name'], "midi": key['midi_note']}
                ))
                white_index += 1
        
        # Add black keys on top
        white_index = 0
        for i, key in enumerate(self.piano_keys):
            if not key['is_black']:
                white_index += 1
            else:
                # Determine key color based on highlighting
                key_color = (100, 100, 180) if key['highlighted'] else (0, 0, 0)
                
                # Calculate position (offset from previous white key)
                x_pos = start_x + ((white_index - 1) * key_width) + (key_width * 0.7)
                
                self.ui.add_component(self.ui.rectangle(
                    id=f"piano_key_{i}",
                    position=(x_pos, self.screen_height - 150),
                    size=(key_width * 0.6, black_key_height),
                    color=key_color,
                    border_color=(0, 0, 0),
                    border_width=1,
                    data={"note": key['note_name'], "midi": key['midi_note']}
                ))
    
    def _add_staff_to_ui(self):
        """Add musical staff to the UI."""
        # TODO: Implement staff visualization
        staff_width = min(800, self.screen_width - 100)
        staff_height = 150
        
        # Staff container
        x = (self.screen_width - staff_width) // 2
        y = (self.screen_height - staff_height) // 2 - 50
        
        self.ui.add_component(self.ui.container(
            id="staff_container",
            position=(x, y),
            size=(staff_width, staff_height),
            children=[]
        ))
        
        # Add the five lines of the staff
        line_spacing = staff_height / 6
        for i in range(5):
            y_pos = y + line_spacing * (i + 1)
            self.ui.add_component(self.ui.line(
                id=f"staff_line_{i}",
                start_pos=(x, y_pos),
                end_pos=(x + staff_width, y_pos),
                color=(0, 0, 0),
                thickness=1
            ))
        
        # Add clef (placeholder - would be an image in a real implementation)
        self.ui.add_component(self.ui.text(
            id="treble_clef",
            text="𝄞",  # Treble clef Unicode character
            position=(x + 30, y + 3 * line_spacing),
            font_size=48,
            color=(0, 0, 0),
            align="center"
        ))
    
    def _add_guitar_to_ui(self):
        """Add guitar fretboard to the UI."""
        # TODO: Implement guitar fretboard visualization
        pass
    
    def handle_click(self, x, y):
        """
        Handle a click event.
        
        This method should detect if a music-specific UI element was clicked
        (like a piano key) and handle it appropriately.
        
        Args:
            x: The x-coordinate of the click.
            y: The y-coordinate of the click.
            
        Returns:
            dict: A dictionary containing the result of the click.
        """
        # Default implementation checks for piano key clicks
        if self.piano_visible:
            # Get all piano key components
            for component in self.ui.components:
                if component.id.startswith("piano_key_"):
                    # Check if click is inside the component
                    if component.contains_point(x, y):
                        # Get the note data from the component
                        note_name = component.data.get("note")
                        midi_note = component.data.get("midi")
                        
                        # Play the note
                        self.play_note(midi_note)
                        
                        return {
                            "action": "piano_key_click",
                            "note": note_name,
                            "midi": midi_note
                        }
        
        # Not handled here, pass to subclass
        return {"action": "unhandled_click", "x": x, "y": y}
    
    def stop_all_sounds(self):
        """Stop all playing sounds."""
        self.audio_engine.stop_all()

# Example usage when run directly
if __name__ == "__main__":
    # Basic test function for the music training module
    import time
    
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    # Create an instance
    module = MusicTrainingModule()
    
    # Play a C major scale
    print("Playing C major scale...")
    module.play_scale("C4", "Major")
    time.sleep(3)
    
    # Play a chord
    print("Playing C major chord...")
    module.play_chord("C4", "Major")
    time.sleep(2)
    
    # Play a sequence of notes
    print("Playing sequence...")
    module.play_note("C4", 0.5)
    time.sleep(0.6)
    module.play_note("E4", 0.5)
    time.sleep(0.6)
    module.play_note("G4", 0.5)
    time.sleep(0.6)
    module.play_note("C5", 1.0)
    time.sleep(2)
    
    print("Test complete.") 