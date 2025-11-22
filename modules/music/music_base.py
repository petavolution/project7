#!/usr/bin/env python3
"""
Optimized Music Training Module Base Class

This module provides a base class for all music-related training modules
in the MetaMindIQTrain platform, building on the unified component system.
"""

import logging
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Union

# Import the training module base class
from MetaMindIQTrain.core.module_manager import TrainingModule

# Import audio engine
from MetaMindIQTrain.core.audio.engine import get_audio_engine

# Import component system
from MetaMindIQTrain.core.component_system import UIComponent, Text, Button

logger = logging.getLogger(__name__)

# Musical constants
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

class PianoKey(UIComponent):
    """Piano key UI component."""
    
    def __init__(self, note_name: str, midi_note: int, is_black: bool = False):
        """Initialize a piano key.
        
        Args:
            note_name: Note name (e.g., 'C4')
            midi_note: MIDI note number
            is_black: Whether this is a black key
        """
        super().__init__(f"piano_key_{note_name}")
        
        # Set key properties
        self.set_property('note_name', note_name)
        self.set_property('midi_note', midi_note)
        self.set_property('is_black', is_black)
        self.set_property('highlighted', False)
        
        # Calculate frequency from MIDI note number
        frequency = 440.0 * (2 ** ((midi_note - 69) / 12))
        self.set_property('frequency', frequency)
        
        # Set visual properties
        if is_black:
            self.set_property('color', (40, 40, 40, 255))
            self.set_property('highlight_color', (80, 80, 160, 255))
        else:
            self.set_property('color', (240, 240, 240, 255))
            self.set_property('highlight_color', (200, 200, 255, 255))
            
        # Add event handler for clicks
        self.add_event_handler('mouse_down', self._handle_mouse_down)
        
    def highlight(self, highlighted: bool = True):
        """Highlight or unhighlight the key.
        
        Args:
            highlighted: Whether to highlight the key
        """
        self.set_property('highlighted', highlighted)
        
    def _handle_mouse_down(self, event) -> bool:
        """Handle mouse down events on the key.
        
        Args:
            event: Mouse event
            
        Returns:
            True if the event was handled, False otherwise
        """
        # Trigger the key_pressed event on the parent
        # This will bubble up to the MusicTrainingModule
        self.trigger_event('key_pressed', self)
        return True
        
    def render(self, renderer):
        """Render the key.
        
        Args:
            renderer: Renderer to use
        """
        if not self.is_visible():
            return
            
        # Get key position and size
        x, y = self.get_absolute_position()
        width, height = self.get_size()
        
        # Determine key color based on highlighting
        is_highlighted = self.get_property('highlighted', False)
        color = self.get_property('highlight_color' if is_highlighted else 'color')
        
        # Draw key
        renderer.draw_rectangle(x, y, width, height, color)
        
        # Draw border
        border_color = (0, 0, 0, 255)
        renderer.draw_line(x, y, x + width, y, border_color)
        renderer.draw_line(x + width, y, x + width, y + height, border_color)
        renderer.draw_line(x + width, y + height, x, y + height, border_color)
        renderer.draw_line(x, y + height, x, y, border_color)
        
        # Draw note name at the bottom of the key
        if not self.get_property('is_black'):
            note_name = self.get_property('note_name')
            renderer.draw_text(
                x + width // 2, y + height - 20,
                note_name,
                12, (0, 0, 0, 255),
                "center"
            )

class MusicTrainingModule(TrainingModule):
    """
    Base class for all music training modules.
    
    This class extends the core TrainingModule with music-specific
    functionality, including note generation, audio synthesis,
    and common musical operations.
    """
    
    def __init__(self, module_id: Optional[str] = None):
        """Initialize the music training module."""
        # Initialize the base module
        super().__init__(module_id)
        
        # Set module properties
        self.set_property('category', 'Music')
        
        # Initialize audio engine
        self.audio_engine = get_audio_engine()
        
        # Add music-specific event handlers
        self.add_event_handler('stop', self._handle_stop_music)
        self.add_event_handler('key_pressed', self._handle_key_pressed)
        
        # Common audio settings with reasonable defaults
        self.set_property('volume', 0.5)
        self.set_property('duration', 0.5)  # Default note duration in seconds
        self.set_property('waveform', 'sine')  # Default waveform type
        
        # Default ADSR envelope
        self.set_property('envelope', {
            'attack': 0.01,
            'decay': 0.05,
            'sustain': 0.7,
            'release': 0.1
        })
        
        # UI state
        self.set_property('piano_visible', False)
        self.set_property('staff_visible', False)
        self.set_property('notation_visible', False)
        
        # Initialize piano keyboard
        self._init_piano()
        
        logger.info(f"Initialized music training module using {self.audio_engine.get_backend_name()}")
    
    def _init_piano(self):
        """Initialize the piano keyboard component."""
        # Create the piano container
        piano_container = UIComponent("piano_container")
        self.add_child(piano_container)
        
        # Initialize a standard piano keyboard (2 octaves centered around middle C)
        octave_start = 4  # Middle C (C4)
        num_octaves = 2
        
        # Calculate key dimensions
        white_key_width = 24
        white_key_height = 100
        black_key_width = white_key_width * 0.6
        black_key_height = white_key_height * 0.65
        
        # Count white keys to determine piano width
        white_key_count = 0
        for octave in range(octave_start, octave_start + num_octaves):
            for note_idx, note_name in enumerate(NOTES):
                if '#' not in note_name:
                    white_key_count += 1
                    
        # Create white keys first
        white_index = 0
        self.piano_keys = []
        
        for octave in range(octave_start, octave_start + num_octaves):
            for note_idx, note_name in enumerate(NOTES):
                if '#' not in note_name:
                    # Calculate MIDI note number
                    midi_note = MIDI_BASE + (octave * 12) + note_idx
                    
                    # Create the key
                    key = PianoKey(f"{note_name}{octave}", midi_note, False)
                    
                    # Set size and position
                    key.set_size(white_key_width, white_key_height)
                    key.set_position(white_index * white_key_width, 0)
                    
                    # Add to piano container
                    piano_container.add_child(key)
                    
                    # Store reference
                    self.piano_keys.append(key)
                    
                    # Increment white key index
                    white_index += 1
        
        # Create black keys on top
        white_index = 0
        for octave in range(octave_start, octave_start + num_octaves):
            for note_idx, note_name in enumerate(NOTES):
                # Track white key position
                if '#' not in note_name:
                    white_index += 1
                elif '#' in note_name:
                    # Calculate MIDI note number
                    midi_note = MIDI_BASE + (octave * 12) + note_idx
                    
                    # Create the key
                    key = PianoKey(f"{note_name}{octave}", midi_note, True)
                    
                    # Set size and position
                    key.set_size(black_key_width, black_key_height)
                    
                    # Position relative to previous white key
                    x = ((white_index - 1) * white_key_width) + (white_key_width * 0.7)
                    key.set_position(x, 0)
                    
                    # Add to piano container
                    piano_container.add_child(key)
                    
                    # Store reference
                    self.piano_keys.append(key)
    
    def _handle_stop_music(self) -> bool:
        """Handle stop event to clean up audio resources.
        
        Returns:
            True if handling was successful
        """
        self.stop_all_sounds()
        return True
        
    def _handle_key_pressed(self, key: PianoKey) -> bool:
        """Handle piano key press events.
        
        Args:
            key: The pressed key
            
        Returns:
            True if the event was handled
        """
        # Play the note
        midi_note = key.get_property('midi_note')
        self.play_note(midi_note)
        
        # Highlight the key
        key.highlight(True)
        
        # Schedule unhighlighting
        import threading
        duration = self.get_property('duration', 0.5)
        
        def unhighlight():
            import time
            time.sleep(duration)
            key.highlight(False)
            
        threading.Thread(target=unhighlight).start()
        
        return True
    
    def show_piano(self, visible: bool = True):
        """Show or hide the piano keyboard.
        
        Args:
            visible: Whether the piano should be visible
        """
        self.set_property('piano_visible', visible)
        
        # Update visibility of the piano container
        piano_container = self.get_child("piano_container")
        if piano_container:
            piano_container.set_visible(visible)
    
    def play_note(self, note, duration=None):
        """Play a single note.
        
        Args:
            note: Either a MIDI note number, a frequency, or a note name (e.g., 'C4')
            duration: Duration in seconds (or uses default if None)
        """
        if duration is None:
            duration = self.get_property('duration', 0.5)
            
        # Convert note to frequency if needed
        frequency = self._note_to_frequency(note)
        
        # Play the note using the audio engine
        if frequency > 0:
            self.audio_engine.play_note(
                frequency, 
                duration=duration,
                envelope=self.get_property('envelope'),
                waveform=self.get_property('waveform', 'sine')
            )
    
    def play_chord(self, root_note, chord_type="Major", duration=None):
        """Play a chord.
        
        Args:
            root_note: Root note (MIDI, frequency, or name)
            chord_type: Type of chord from CHORDS dictionary
            duration: Duration in seconds (or uses default if None)
        """
        if duration is None:
            duration = self.get_property('duration', 0.5)
            
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
            envelope=self.get_property('envelope'),
            waveform=self.get_property('waveform', 'sine')
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
            envelope=self.get_property('envelope'),
            waveform=self.get_property('waveform', 'sine')
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
            midi_note = key.get_property('midi_note')
            if midi_note in midi_notes:
                key.highlight(highlight)
    
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
    
    def position_piano(self):
        """Position the piano at the bottom of the screen."""
        screen_width = self.get_property('screen_width', 800)
        screen_height = self.get_property('screen_height', 600)
        
        # Get piano container
        piano_container = self.get_child("piano_container")
        if piano_container:
            # Calculate the piano width
            total_width = 0
            for key in self.piano_keys:
                if not key.get_property('is_black', False):
                    width, _ = key.get_size()
                    total_width += width
                    
            # Center the piano horizontally and position at the bottom
            x = (screen_width - total_width) // 2
            y = screen_height - 150
            
            piano_container.set_position(x, y)
    
    def _handle_resize(self, width: int, height: int) -> bool:
        """Handle resize events.
        
        Args:
            width: New screen width
            height: New screen height
            
        Returns:
            True if the resize was handled successfully
        """
        # Call parent handler first
        super()._handle_resize(width, height)
        
        # Reposition piano
        self.position_piano()
        
        return True
    
    def stop_all_sounds(self):
        """Stop all playing sounds."""
        if self.audio_engine:
            self.audio_engine.stop_all()
    
    def render(self, renderer):
        """Render the module.
        
        Args:
            renderer: The renderer to use
        """
        # First get the screen dimensions
        width = self.get_property('screen_width')
        height = self.get_property('screen_height')
        
        # Draw background
        renderer.draw_rectangle(0, 0, width, height, (20, 20, 40, 255))
        
        # Make sure the piano is positioned correctly
        self.position_piano()
        
        # Render all children (includes piano if visible)
        for child in self.get_children():
            if isinstance(child, UIComponent) and child.is_visible():
                child.render(renderer)
                
        # Show module name at the top
        name = self.get_property('name')
        renderer.draw_text(
            width // 2, 30, 
            name, 
            32, (255, 255, 255, 255), 
            "center"
        )

# For testing when run directly
if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    
    # Import renderer
    from MetaMindIQTrain.core.renderer import get_renderer
    
    # Create renderer and module
    renderer = get_renderer()
    renderer.initialize(800, 600, "Music Module Test")
    
    # Create module
    module = MusicTrainingModule()
    module.trigger_event('initialize')
    module.trigger_event('resize', 800, 600)
    module.show_piano(True)
    
    # Main loop
    running = True
    last_time = time.time()
    
    while running and renderer.is_running():
        # Process events
        events = renderer.process_events()
        for event in events:
            if event['type'] == 'quit':
                running = False
            elif event['type'] == 'mouse_down':
                # Check for piano key clicks
                for key in module.piano_keys:
                    x, y = event['pos']
                    if key.contains_point(x, y):
                        module._handle_key_pressed(key)
        
        # Calculate delta time
        current_time = time.time()
        delta_time = current_time - last_time
        last_time = current_time
        
        # Update module
        module.trigger_event('update', delta_time)
        
        # Render
        renderer.clear((20, 20, 40, 255))
        module.render(renderer)
        renderer.present()
        
        # Cap frame rate
        elapsed = time.time() - current_time
        if elapsed < 1/60:
            time.sleep(1/60 - elapsed)
    
    # Clean up
    module.stop_all_sounds()
    renderer.shutdown() 