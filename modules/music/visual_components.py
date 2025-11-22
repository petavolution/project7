#!/usr/bin/env python3
"""
Visual Components for Music Training Modules

This module provides common visualization components that can be used across 
all music-related training modules in the MetaMindIQTrain platform.
"""

import logging
from typing import Dict, List, Tuple, Optional, Any
import math

# Configure logging
logger = logging.getLogger(__name__)

class PianoKeyboard:
    """
    A visual piano keyboard component that can be used to display notes,
    scales, chords and other musical elements.
    """
    
    def __init__(self, start_note="C3", num_octaves=2):
        """
        Initialize the piano keyboard visualization.
        
        Args:
            start_note: The starting note of the keyboard (e.g., "C3")
            num_octaves: Number of octaves to display
        """
        self.start_note = start_note
        self.num_octaves = num_octaves
        self.highlighted_notes = []
        
        # Parse start note
        self.start_note_name = start_note[0]
        if len(start_note) > 1 and start_note[1] in ['#', 'b']:
            self.start_note_name += start_note[1]
            self.start_octave = int(start_note[2:])
        else:
            self.start_octave = int(start_note[1:])
        
        # Define note properties
        self.white_notes = ['C', 'D', 'E', 'F', 'G', 'A', 'B']
        self.black_notes = ['C#', 'D#', 'F#', 'G#', 'A#']
        self.alt_black_notes = ['Db', 'Eb', 'Gb', 'Ab', 'Bb']
        
        # Calculate total number of keys
        self.num_white_keys = len(self.white_notes) * self.num_octaves
        if self.start_note_name in self.white_notes:
            start_idx = self.white_notes.index(self.start_note_name)
            self.num_white_keys -= start_idx
        
        # Calculate key dimensions (to be set by renderer)
        self.white_key_width = 0
        self.white_key_height = 0
        self.black_key_width = 0
        self.black_key_height = 0
        
    def set_dimensions(self, white_key_width, white_key_height):
        """
        Set the dimensions of the piano keys.
        
        Args:
            white_key_width: Width of a white key in pixels
            white_key_height: Height of a white key in pixels
        """
        self.white_key_width = white_key_width
        self.white_key_height = white_key_height
        self.black_key_width = int(white_key_width * 0.6)
        self.black_key_height = int(white_key_height * 0.6)
    
    def highlight_notes(self, notes):
        """
        Highlight specific notes on the keyboard.
        
        Args:
            notes: List of note names to highlight (e.g., ["C3", "E3", "G3"])
        """
        self.highlighted_notes = notes
    
    def highlight_scale(self, root_note, scale_type="major"):
        """
        Highlight notes in a scale.
        
        Args:
            root_note: Root note of the scale (e.g., "C4")
            scale_type: Type of scale (e.g., "major", "minor", "pentatonic")
        """
        # Define scale patterns (whole and half steps)
        scale_patterns = {
            "major": [0, 2, 4, 5, 7, 9, 11],      # W-W-H-W-W-W-H
            "minor": [0, 2, 3, 5, 7, 8, 10],      # W-H-W-W-H-W-W
            "pentatonic": [0, 2, 4, 7, 9],        # Major pentatonic
            "blues": [0, 3, 5, 6, 7, 10]          # Blues scale
        }
        
        pattern = scale_patterns.get(scale_type.lower(), scale_patterns["major"])
        
        # Calculate highlighted notes based on pattern
        notes = []
        root_name = root_note[0]
        if len(root_note) > 1 and root_note[1] in ['#', 'b']:
            root_name += root_note[1]
            octave = int(root_note[2:])
        else:
            octave = int(root_note[1:])
        
        # Generate note names
        all_notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        
        if root_name in all_notes:
            root_idx = all_notes.index(root_name)
            
            for offset in pattern:
                idx = (root_idx + offset) % 12
                curr_octave = octave + (root_idx + offset) // 12
                notes.append(f"{all_notes[idx]}{curr_octave}")
        
        self.highlighted_notes = notes
    
    def highlight_chord(self, root_note, chord_type="major"):
        """
        Highlight notes in a chord.
        
        Args:
            root_note: Root note of the chord (e.g., "C4")
            chord_type: Type of chord (e.g., "major", "minor", "7th")
        """
        # Define chord patterns (intervals from root)
        chord_patterns = {
            "major": [0, 4, 7],       # Major triad (1-3-5)
            "minor": [0, 3, 7],       # Minor triad (1-b3-5)
            "7th": [0, 4, 7, 10],     # Dominant 7th (1-3-5-b7)
            "maj7": [0, 4, 7, 11],    # Major 7th (1-3-5-7)
            "min7": [0, 3, 7, 10],    # Minor 7th (1-b3-5-b7)
            "dim": [0, 3, 6],         # Diminished (1-b3-b5)
            "aug": [0, 4, 8]          # Augmented (1-3-#5)
        }
        
        pattern = chord_patterns.get(chord_type.lower(), chord_patterns["major"])
        
        # Calculate highlighted notes based on pattern (similar to scale highlighting)
        notes = []
        root_name = root_note[0]
        if len(root_note) > 1 and root_note[1] in ['#', 'b']:
            root_name += root_note[1]
            octave = int(root_note[2:])
        else:
            octave = int(root_note[1:])
        
        # Generate note names
        all_notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        
        if root_name in all_notes:
            root_idx = all_notes.index(root_name)
            
            for offset in pattern:
                idx = (root_idx + offset) % 12
                curr_octave = octave + (root_idx + offset) // 12
                notes.append(f"{all_notes[idx]}{curr_octave}")
        
        self.highlighted_notes = notes
    
    def get_key_data(self):
        """
        Get data for rendering the keyboard.
        
        Returns:
            dict: Dictionary containing keyboard rendering data
        """
        # Calculate positions of white keys
        white_keys = []
        black_keys = []
        
        # Generate all notes in the range
        all_notes = []
        octave = self.start_octave
        note_idx = self.white_notes.index(self.start_note_name[0]) if self.start_note_name[0] in self.white_notes else 0
        
        for i in range(self.num_octaves * 7):
            note_name = self.white_notes[note_idx]
            all_notes.append(f"{note_name}{octave}")
            
            # Move to next note
            note_idx += 1
            if note_idx >= len(self.white_notes):
                note_idx = 0
                octave += 1
        
        # For simplicity, manually calculate black keys
        for i, note in enumerate(all_notes[:-1]):  # Skip last note
            note_name = note[0]
            octave = note[1:]
            
            # Check if there's a black key after this white key
            if note_name in ['C', 'D', 'F', 'G', 'A']:
                black_note = f"{note_name}#{octave}"
                black_keys.append(black_note)
        
        return {
            'white_keys': all_notes,
            'black_keys': black_keys,
            'highlighted': self.highlighted_notes
        }


class GuitarFretboard:
    """
    A visual guitar fretboard component that can be used to display notes,
    scales, chords and other musical elements.
    """
    
    def __init__(self, num_strings=6, num_frets=12, tuning=None):
        """
        Initialize the guitar fretboard visualization.
        
        Args:
            num_strings: Number of strings (default: 6 for standard guitar)
            num_frets: Number of frets to display
            tuning: Tuning of the strings (default: standard E A D G B E)
        """
        self.num_strings = num_strings
        self.num_frets = num_frets
        self.highlighted_positions = []  # List of (string, fret) tuples
        
        # Set default tuning if not provided
        if tuning is None:
            if num_strings == 6:  # Standard guitar
                self.tuning = ["E2", "A2", "D3", "G3", "B3", "E4"]
            elif num_strings == 4:  # Standard bass
                self.tuning = ["E1", "A1", "D2", "G2"]
            elif num_strings == 7:  # 7-string guitar
                self.tuning = ["B1", "E2", "A2", "D3", "G3", "B3", "E4"]
            else:
                # Generate a sensible default
                self.tuning = ["E2"] * num_strings
        else:
            self.tuning = tuning
    
    def highlight_notes(self, notes):
        """
        Highlight specific notes on the fretboard.
        
        Args:
            notes: List of note names to highlight (e.g., ["C3", "E3", "G3"])
        """
        positions = []
        
        # Find positions for each note on each string
        for note in notes:
            for string_idx, open_string in enumerate(self.tuning):
                string_positions = self._find_note_on_string(note, open_string, string_idx)
                positions.extend(string_positions)
        
        self.highlighted_positions = positions
    
    def _find_note_on_string(self, target_note, open_string, string_idx):
        """
        Find positions of a note on a specific string.
        
        Args:
            target_note: Note to find
            open_string: Open string note
            string_idx: String index
        
        Returns:
            List of (string, fret) tuples where the note appears
        """
        positions = []
        
        # Parse notes
        all_notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        
        # Parse target note
        target_name = target_note[0]
        if len(target_note) > 1 and target_note[1] in ['#', 'b']:
            target_name += target_note[1]
            target_octave = int(target_note[2:])
        else:
            target_octave = int(target_note[1:])
        
        target_idx = all_notes.index(target_name) if target_name in all_notes else 0
        target_absolute = target_octave * 12 + target_idx
        
        # Parse open string note
        open_name = open_string[0]
        if len(open_string) > 1 and open_string[1] in ['#', 'b']:
            open_name += open_string[1]
            open_octave = int(open_string[2:])
        else:
            open_octave = int(open_string[1:])
        
        open_idx = all_notes.index(open_name) if open_name in all_notes else 0
        open_absolute = open_octave * 12 + open_idx
        
        # Find positions
        for fret in range(self.num_frets + 1):  # Include open string (fret 0)
            fret_absolute = open_absolute + fret
            if fret_absolute == target_absolute:
                positions.append((string_idx, fret))
        
        return positions
    
    def highlight_scale(self, root_note, scale_type="major"):
        """
        Highlight notes in a scale on the fretboard.
        
        Args:
            root_note: Root note of the scale (e.g., "C4")
            scale_type: Type of scale (e.g., "major", "minor", "pentatonic")
        """
        # Define scale patterns (whole and half steps)
        scale_patterns = {
            "major": [0, 2, 4, 5, 7, 9, 11],      # W-W-H-W-W-W-H
            "minor": [0, 2, 3, 5, 7, 8, 10],      # W-H-W-W-H-W-W
            "pentatonic": [0, 2, 4, 7, 9],        # Major pentatonic
            "blues": [0, 3, 5, 6, 7, 10]          # Blues scale
        }
        
        pattern = scale_patterns.get(scale_type.lower(), scale_patterns["major"])
        
        # Generate note names in the scale
        all_notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        
        root_name = root_note[0]
        if len(root_note) > 1 and root_note[1] in ['#', 'b']:
            root_name += root_note[1]
            octave = int(root_note[2:])
        else:
            octave = int(root_note[1:])
        
        if root_name in all_notes:
            root_idx = all_notes.index(root_name)
            
            # Generate all notes in the scale
            scale_notes = []
            for offset in pattern:
                idx = (root_idx + offset) % 12
                curr_octave = octave
                note = f"{all_notes[idx]}{curr_octave}"
                scale_notes.append(note)
                
                # Also add octave above to ensure we find all positions
                note_above = f"{all_notes[idx]}{curr_octave + 1}"
                scale_notes.append(note_above)
                
                # For lower strings, also add octave below
                note_below = f"{all_notes[idx]}{curr_octave - 1}"
                scale_notes.append(note_below)
            
            self.highlight_notes(scale_notes)
    
    def highlight_chord(self, root_note, chord_type="major"):
        """
        Highlight notes in a chord on the fretboard.
        
        Args:
            root_note: Root note of the chord (e.g., "C4")
            chord_type: Type of chord (e.g., "major", "minor", "7th")
        """
        # Define chord patterns (intervals from root)
        chord_patterns = {
            "major": [0, 4, 7],       # Major triad (1-3-5)
            "minor": [0, 3, 7],       # Minor triad (1-b3-5)
            "7th": [0, 4, 7, 10],     # Dominant 7th (1-3-5-b7)
            "maj7": [0, 4, 7, 11],    # Major 7th (1-3-5-7)
            "min7": [0, 3, 7, 10],    # Minor 7th (1-b3-5-b7)
            "dim": [0, 3, 6],         # Diminished (1-b3-b5)
            "aug": [0, 4, 8]          # Augmented (1-3-#5)
        }
        
        pattern = chord_patterns.get(chord_type.lower(), chord_patterns["major"])
        
        # Generate note names in the chord (similar to scale highlighting)
        all_notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        
        root_name = root_note[0]
        if len(root_note) > 1 and root_note[1] in ['#', 'b']:
            root_name += root_note[1]
            octave = int(root_note[2:])
        else:
            octave = int(root_note[1:])
        
        if root_name in all_notes:
            root_idx = all_notes.index(root_name)
            
            # Generate all notes in the chord
            chord_notes = []
            for offset in pattern:
                idx = (root_idx + offset) % 12
                curr_octave = octave
                note = f"{all_notes[idx]}{curr_octave}"
                chord_notes.append(note)
                
                # Also add octave above and below to ensure we find all positions
                note_above = f"{all_notes[idx]}{curr_octave + 1}"
                chord_notes.append(note_above)
                
                note_below = f"{all_notes[idx]}{curr_octave - 1}"
                chord_notes.append(note_below)
            
            self.highlight_notes(chord_notes)
    
    def get_fretboard_data(self):
        """
        Get data for rendering the fretboard.
        
        Returns:
            dict: Dictionary containing fretboard rendering data
        """
        return {
            'num_strings': self.num_strings,
            'num_frets': self.num_frets,
            'tuning': self.tuning,
            'highlighted': self.highlighted_positions
        }


class WaveformVisualizer:
    """
    A simple waveform visualizer for audio data.
    """
    
    def __init__(self, samples=None, width=600, height=200):
        """
        Initialize the waveform visualizer.
        
        Args:
            samples: Audio samples to visualize (optional)
            width: Width of the visualization in pixels
            height: Height of the visualization in pixels
        """
        self.samples = samples
        self.width = width
        self.height = height
    
    def set_samples(self, samples):
        """
        Set the audio samples to visualize.
        
        Args:
            samples: Audio samples (numpy array)
        """
        self.samples = samples
    
    def get_waveform_points(self):
        """
        Calculate points for rendering the waveform.
        
        Returns:
            List of (x, y) points for drawing the waveform
        """
        if self.samples is None or len(self.samples) == 0:
            return []
        
        # Subsample to fit the width
        if len(self.samples) > self.width:
            step = len(self.samples) // self.width
            subsamples = [self.samples[i] for i in range(0, len(self.samples), step)][:self.width]
        else:
            subsamples = self.samples
        
        # Calculate points
        points = []
        mid_y = self.height // 2
        scale = self.height // 2 * 0.9  # 90% of half-height
        
        for i, sample in enumerate(subsamples):
            x = i * (self.width / len(subsamples))
            y = mid_y - sample * scale
            points.append((x, y))
        
        return points


# Simple testing code
if __name__ == "__main__":
    # Test keyboard
    keyboard = PianoKeyboard(start_note="C3", num_octaves=2)
    keyboard.highlight_chord("C3", "major")
    print("Piano Keyboard Data:")
    print(keyboard.get_key_data())
    
    # Test fretboard
    fretboard = GuitarFretboard()
    fretboard.highlight_scale("A2", "minor")
    print("\nGuitar Fretboard Data:")
    print(fretboard.get_fretboard_data())
    
    print("\nVisual Components module successfully loaded!") 