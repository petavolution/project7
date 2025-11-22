#!/usr/bin/env python3
"""
Music Notation Visualizer for Music Training Modules

This module provides components to display musical notation, including
staff notation, pitch representation, and interactive music notation rendering.
"""

import logging
from typing import Dict, List, Tuple, Optional, Any
import math

# Configure logging
logger = logging.getLogger(__name__)

class StaffSymbols:
    """Constants for music notation symbols."""
    
    # Clefs
    TREBLE_CLEF = "treble"
    BASS_CLEF = "bass"
    ALTO_CLEF = "alto"
    
    # Notes
    WHOLE_NOTE = "whole"
    HALF_NOTE = "half"
    QUARTER_NOTE = "quarter"
    EIGHTH_NOTE = "eighth"
    SIXTEENTH_NOTE = "sixteenth"
    
    # Rests
    WHOLE_REST = "whole_rest"
    HALF_REST = "half_rest"
    QUARTER_REST = "quarter_rest"
    EIGHTH_REST = "eighth_rest"
    SIXTEENTH_REST = "sixteenth_rest"
    
    # Accidentals
    SHARP = "sharp"
    FLAT = "flat"
    NATURAL = "natural"
    DOUBLE_SHARP = "double_sharp"
    DOUBLE_FLAT = "double_flat"
    
    # Time signatures
    COMMON_TIME = "common_time"
    CUT_TIME = "cut_time"
    TIME_4_4 = "4/4"
    TIME_3_4 = "3/4"
    TIME_2_4 = "2/4"
    TIME_6_8 = "6/8"
    
    # Other symbols
    BAR_LINE = "bar_line"
    DOUBLE_BAR_LINE = "double_bar_line"
    REPEAT_START = "repeat_start"
    REPEAT_END = "repeat_end"
    
    # Articulations
    STACCATO = "staccato"
    ACCENT = "accent"
    TENUTO = "tenuto"
    FERMATA = "fermata"
    
    # Dynamic markings
    PIANO = "p"
    FORTE = "f"
    MEZZO_PIANO = "mp"
    MEZZO_FORTE = "mf"
    PIANISSIMO = "pp"
    FORTISSIMO = "ff"


class MusicNote:
    """
    Represents a single music note in notation.
    """
    
    def __init__(self, pitch, duration, octave=4, accidental=None, 
                 dotted=False, tied=False, stem_direction="up"):
        """
        Initialize a music note.
        
        Args:
            pitch: Note pitch (A-G)
            duration: Note duration (whole, half, quarter, etc.)
            octave: Octave number
            accidental: Optional accidental (sharp, flat, natural, etc.)
            dotted: Whether the note is dotted
            tied: Whether the note is tied to the next note
            stem_direction: Direction of the note stem ("up" or "down")
        """
        self.pitch = pitch
        self.duration = duration
        self.octave = octave
        self.accidental = accidental
        self.dotted = dotted
        self.tied = tied
        self.stem_direction = stem_direction
        
        # Virtual position on staff (Middle C = 0, positive values go up, negative down)
        self.staff_position = self._calculate_staff_position()
    
    def _calculate_staff_position(self):
        """
        Calculate the vertical position of the note on the staff.
        
        Middle C = 0, each step is one staff line or space (positive up, negative down).
        
        Returns:
            int: Staff position value
        """
        # Note index (C=0, D=1, E=2, F=3, G=4, A=5, B=6)
        note_indices = {"C": 0, "D": 1, "E": 2, "F": 3, "G": 4, "A": 5, "B": 6}
        
        if self.pitch not in note_indices:
            logger.warning(f"Invalid pitch: {self.pitch}, defaulting to C")
            pitch_idx = 0
        else:
            pitch_idx = note_indices[self.pitch]
        
        # Calculate position relative to C4 (middle C)
        octave_offset = (self.octave - 4) * 7  # Each octave has 7 notes
        return pitch_idx + octave_offset
    
    def get_midi_number(self):
        """
        Get the MIDI note number for this note.
        
        Returns:
            int: MIDI note number
        """
        # Base note values in octave 0
        base_values = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}
        
        if self.pitch not in base_values:
            logger.warning(f"Invalid pitch: {self.pitch}, defaulting to C")
            base = 0
        else:
            base = base_values[self.pitch]
        
        # Adjust for octave (MIDI octaves start at C)
        midi_number = base + (self.octave * 12) + 12  # +12 because MIDI octave 0 starts at C-1
        
        # Adjust for accidentals
        if self.accidental == "sharp":
            midi_number += 1
        elif self.accidental == "flat":
            midi_number -= 1
        elif self.accidental == "double_sharp":
            midi_number += 2
        elif self.accidental == "double_flat":
            midi_number -= 2
        
        return midi_number
    
    def to_dict(self):
        """
        Convert the note to a dictionary for rendering.
        
        Returns:
            dict: Dictionary with note properties
        """
        return {
            'pitch': self.pitch,
            'duration': self.duration,
            'octave': self.octave,
            'accidental': self.accidental,
            'dotted': self.dotted,
            'tied': self.tied,
            'stem_direction': self.stem_direction,
            'staff_position': self.staff_position,
            'midi_number': self.get_midi_number()
        }


class MusicStaff:
    """
    Represents a musical staff with notes and symbols.
    """
    
    def __init__(self, clef=StaffSymbols.TREBLE_CLEF, key_signature=None, 
                 time_signature=StaffSymbols.TIME_4_4):
        """
        Initialize a music staff.
        
        Args:
            clef: The clef type (treble, bass, alto)
            key_signature: The key signature (e.g., "C", "G", "F", "Bb")
            time_signature: The time signature (e.g., "4/4", "3/4")
        """
        self.clef = clef
        self.key_signature = key_signature
        self.time_signature = time_signature
        self.measures = []  # List of lists of notes/rests
        self.current_measure = []
    
    def add_note(self, note):
        """
        Add a note to the current measure.
        
        Args:
            note: MusicNote object to add
        """
        self.current_measure.append(note)
    
    def add_rest(self, duration, dotted=False):
        """
        Add a rest to the current measure.
        
        Args:
            duration: Rest duration (whole, half, quarter, etc.)
            dotted: Whether the rest is dotted
        """
        # Use a MusicNote with special "rest" pitch
        rest = MusicNote("rest", duration, dotted=dotted)
        self.current_measure.append(rest)
    
    def end_measure(self):
        """End the current measure and start a new one."""
        if self.current_measure:
            self.measures.append(self.current_measure)
            self.current_measure = []
    
    def clear(self):
        """Clear the staff."""
        self.measures = []
        self.current_measure = []
    
    def get_notes(self, include_current=True):
        """
        Get all notes in the staff.
        
        Args:
            include_current: Whether to include notes in the current measure
            
        Returns:
            list: List of all notes/rests
        """
        all_notes = []
        
        for measure in self.measures:
            all_notes.extend(measure)
        
        if include_current and self.current_measure:
            all_notes.extend(self.current_measure)
        
        return all_notes
    
    def to_dict(self):
        """
        Convert the staff to a dictionary for rendering.
        
        Returns:
            dict: Dictionary with staff properties
        """
        all_measures = self.measures.copy()
        if self.current_measure:
            all_measures.append(self.current_measure)
        
        return {
            'clef': self.clef,
            'key_signature': self.key_signature,
            'time_signature': self.time_signature,
            'measures': [
                [note.to_dict() for note in measure]
                for measure in all_measures
            ]
        }


class ChordSymbol:
    """
    Represents a chord symbol in notation.
    """
    
    def __init__(self, root, quality="", extensions=None, bass_note=None):
        """
        Initialize a chord symbol.
        
        Args:
            root: Root note of the chord (e.g., "C", "F#", "Bb")
            quality: Chord quality ("", "m", "dim", "aug", etc.)
            extensions: List of extensions ("7", "9", "13", etc.)
            bass_note: Optional bass note for inversions (e.g., "E" for C/E)
        """
        self.root = root
        self.quality = quality
        self.extensions = extensions or []
        self.bass_note = bass_note
    
    def __str__(self):
        """
        Get string representation of the chord.
        
        Returns:
            str: Formatted chord symbol
        """
        # Start with root note
        result = self.root
        
        # Add quality
        result += self.quality
        
        # Add extensions
        if self.extensions:
            result += "".join(self.extensions)
        
        # Add bass note if any
        if self.bass_note:
            result += f"/{self.bass_note}"
        
        return result
    
    def to_dict(self):
        """
        Convert the chord symbol to a dictionary.
        
        Returns:
            dict: Dictionary with chord symbol properties
        """
        return {
            'root': self.root,
            'quality': self.quality,
            'extensions': self.extensions,
            'bass_note': self.bass_note,
            'display': str(self)
        }


class NotationRenderer:
    """
    Base class for rendering musical notation.
    
    This is platform-agnostic and just provides data needed for rendering.
    Actual rendering is implemented by platform-specific renderers.
    """
    
    def __init__(self, width=800, height=200):
        """
        Initialize the notation renderer.
        
        Args:
            width: Width of the rendering area in pixels
            height: Height of the rendering area in pixels
        """
        self.width = width
        self.height = height
        self.staff = MusicStaff()
        self.chord_symbols = []
        self.symbols = []  # Other musical symbols (dynamics, articulations, etc.)
        self.highlighted_notes = []
    
    def set_staff(self, staff):
        """
        Set the staff to render.
        
        Args:
            staff: MusicStaff object
        """
        self.staff = staff
    
    def add_chord_symbol(self, position, chord_symbol):
        """
        Add a chord symbol to display above the staff.
        
        Args:
            position: Position index (which note/beat to align with)
            chord_symbol: ChordSymbol object
        """
        self.chord_symbols.append((position, chord_symbol))
    
    def add_symbol(self, position, symbol_type, above_staff=True):
        """
        Add a musical symbol (articulation, dynamic, etc.).
        
        Args:
            position: Position index (which note/beat to align with)
            symbol_type: Type of symbol (from StaffSymbols)
            above_staff: Whether to place the symbol above or below the staff
        """
        self.symbols.append((position, symbol_type, above_staff))
    
    def highlight_notes(self, note_indices):
        """
        Highlight specific notes in the notation.
        
        Args:
            note_indices: List of indices of notes to highlight
        """
        self.highlighted_notes = note_indices
    
    def get_render_data(self):
        """
        Get data needed for rendering the notation.
        
        Returns:
            dict: Dictionary with all rendering data
        """
        staff_data = self.staff.to_dict()
        
        chord_data = [
            {
                'position': pos,
                'chord': chord.to_dict()
            }
            for pos, chord in self.chord_symbols
        ]
        
        symbol_data = [
            {
                'position': pos,
                'type': sym,
                'above': above
            }
            for pos, sym, above in self.symbols
        ]
        
        return {
            'staff': staff_data,
            'chord_symbols': chord_data,
            'symbols': symbol_data,
            'highlighted_notes': self.highlighted_notes,
            'width': self.width,
            'height': self.height
        }


class SimpleNotationParser:
    """
    A simple parser for creating notation from string representations.
    """
    
    @staticmethod
    def parse_note(note_str):
        """
        Parse a note string like "C4q" (C quarter note in octave 4) or "D#5h." (D# dotted half note in octave 5).
        
        Args:
            note_str: String representation of the note
            
        Returns:
            MusicNote: Parsed note object
        """
        if not note_str:
            return None
        
        # Handle rests
        if note_str.startswith("r"):
            duration = note_str[1:]
            dotted = duration.endswith(".")
            if dotted:
                duration = duration[:-1]
                
            # Map duration symbols to actual durations
            duration_map = {
                "w": StaffSymbols.WHOLE_REST,
                "h": StaffSymbols.HALF_REST,
                "q": StaffSymbols.QUARTER_REST,
                "e": StaffSymbols.EIGHTH_REST,
                "s": StaffSymbols.SIXTEENTH_REST
            }
            
            if duration in duration_map:
                rest = MusicNote("rest", duration_map[duration], dotted=dotted)
                return rest
            else:
                logger.warning(f"Invalid rest duration: {duration}")
                return None
        
        # Parse pitch and accidental
        i = 0
        pitch = note_str[i]
        i += 1
        
        accidental = None
        if i < len(note_str) and (note_str[i] == "#" or note_str[i] == "b"):
            accidental = "sharp" if note_str[i] == "#" else "flat"
            i += 1
            
            # Handle double accidentals
            if i < len(note_str) and (note_str[i] == "#" or note_str[i] == "b"):
                accidental = "double_sharp" if accidental == "sharp" else "double_flat"
                i += 1
        
        # Parse octave
        if i < len(note_str) and note_str[i].isdigit():
            octave = int(note_str[i])
            i += 1
        else:
            octave = 4  # Default octave
        
        # Parse duration
        if i < len(note_str):
            duration_char = note_str[i]
            i += 1
            
            # Check for dotted note
            dotted = False
            if i < len(note_str) and note_str[i] == ".":
                dotted = True
                i += 1
            
            # Map duration symbols to actual durations
            duration_map = {
                "w": StaffSymbols.WHOLE_NOTE,
                "h": StaffSymbols.HALF_NOTE,
                "q": StaffSymbols.QUARTER_NOTE,
                "e": StaffSymbols.EIGHTH_NOTE,
                "s": StaffSymbols.SIXTEENTH_NOTE
            }
            
            if duration_char in duration_map:
                duration = duration_map[duration_char]
            else:
                logger.warning(f"Invalid note duration: {duration_char}")
                duration = StaffSymbols.QUARTER_NOTE
        else:
            # Default to quarter note if no duration specified
            duration = StaffSymbols.QUARTER_NOTE
            dotted = False
        
        # Create the note
        note = MusicNote(
            pitch=pitch,
            duration=duration,
            octave=octave,
            accidental=accidental,
            dotted=dotted
        )
        
        return note
    
    @staticmethod
    def parse_chord(chord_str):
        """
        Parse a chord string like "Cmaj7" or "F#m7b5/A".
        
        Args:
            chord_str: String representation of the chord
            
        Returns:
            ChordSymbol: Parsed chord symbol
        """
        if not chord_str:
            return None
        
        # Split for slash chords
        parts = chord_str.split("/")
        chord_part = parts[0]
        bass_note = parts[1] if len(parts) > 1 else None
        
        # Parse root and accidental
        i = 0
        root = chord_part[i]
        i += 1
        
        if i < len(chord_part) and (chord_part[i] == "#" or chord_part[i] == "b"):
            root += chord_part[i]
            i += 1
        
        # Parse quality and extensions
        quality = ""
        extensions = []
        
        if i < len(chord_part):
            # Check for common qualities
            if chord_part[i:].startswith("maj"):
                quality = "maj"
                i += 3
            elif chord_part[i:].startswith("min") or chord_part[i:].startswith("m"):
                quality = "m"
                i += 1 if chord_part[i] == "m" else 3
            elif chord_part[i:].startswith("dim") or chord_part[i:].startswith("°"):
                quality = "dim"
                i += 1 if chord_part[i] == "°" else 3
            elif chord_part[i:].startswith("aug") or chord_part[i:].startswith("+"):
                quality = "aug"
                i += 1 if chord_part[i] == "+" else 3
            elif chord_part[i:].startswith("sus"):
                quality = "sus"
                i += 3
                if i < len(chord_part) and chord_part[i].isdigit():
                    quality += chord_part[i]
                    i += 1
        
        # Parse extensions
        extension_part = chord_part[i:]
        if extension_part:
            # Common extensions
            if extension_part.isdigit():
                extensions.append(extension_part)
            else:
                # Complex extensions (e.g., 7b9#11)
                j = 0
                current_ext = ""
                
                while j < len(extension_part):
                    if extension_part[j].isdigit():
                        if current_ext:
                            extensions.append(current_ext)
                            current_ext = ""
                        current_ext = extension_part[j]
                    else:
                        current_ext += extension_part[j]
                    j += 1
                
                if current_ext:
                    extensions.append(current_ext)
        
        # Create the chord symbol
        chord = ChordSymbol(
            root=root,
            quality=quality,
            extensions=extensions,
            bass_note=bass_note
        )
        
        return chord
    
    @staticmethod
    def parse_staff(notation_str, key=None, time_signature=StaffSymbols.TIME_4_4):
        """
        Parse a string of notation into a MusicStaff.
        
        Format: "C4q D4q E4q F4q | G4q A4q B4q C5q"
        
        Args:
            notation_str: String representation of notation
            key: Optional key signature
            time_signature: Time signature
            
        Returns:
            MusicStaff: Parsed staff object
        """
        staff = MusicStaff(key_signature=key, time_signature=time_signature)
        
        # Split into measures
        measures = notation_str.split("|")
        
        for measure_str in measures:
            # Split into notes/chords
            elements = measure_str.strip().split()
            
            for element in elements:
                note = SimpleNotationParser.parse_note(element)
                if note:
                    staff.add_note(note)
            
            staff.end_measure()
        
        return staff


# Example usage
if __name__ == "__main__":
    # Set up a simple staff
    parser = SimpleNotationParser()
    
    # Parse a C major scale
    staff = parser.parse_staff("C4q D4q E4q F4q | G4q A4q B4q C5q", key="C")
    
    # Create a renderer
    renderer = NotationRenderer()
    renderer.set_staff(staff)
    
    # Add chord symbols
    renderer.add_chord_symbol(0, parser.parse_chord("C"))
    renderer.add_chord_symbol(4, parser.parse_chord("G"))
    
    # Generate render data
    render_data = renderer.get_render_data()
    
    print("Render data generated:")
    print(f"Staff has {len(staff.measures)} measures")
    print(f"Total notes: {len(staff.get_notes())}")
    
    print("\nNotation module successfully loaded!") 