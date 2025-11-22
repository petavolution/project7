#!/usr/bin/env python3
"""
Unified Audio Engine for MetaMindIQTrain

This module provides an optimized audio synthesis system with multiple backend support,
efficient caching, and a simplified API for music-related training modules.
"""

import numpy as np
import logging
import sys
import time
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional, Union, Callable
import threading
from abc import ABC, abstractmethod

# Add parent directory to path for direct imports when needed
if __name__ == "__main__" or not __package__:
    project_root = Path(__file__).parent.parent.parent
    sys.path.insert(0, str(project_root))
    from MetaMindIQTrain.core.training_module import TrainingModule
else:
    # Use relative imports when imported as a module
    from ...core.training_module import TrainingModule

# Configure logging
logger = logging.getLogger(__name__)

# Global audio availability flag
AUDIO_AVAILABLE = False

# Backend detection with lazily loaded dependencies
class AudioBackend(ABC):
    """Abstract base class for audio playback backends."""
    
    @abstractmethod
    def play(self, waveform: np.ndarray, sample_rate: int = 44100) -> None:
        """Play audio waveform.
        
        Args:
            waveform: NumPy array containing the audio data
            sample_rate: Sample rate in Hz
        """
        pass
        
    @abstractmethod
    def stop(self) -> None:
        """Stop any currently playing audio."""
        pass
    
    @property
    @abstractmethod
    def is_available(self) -> bool:
        """Check if this backend is available on the current system."""
        pass

class SoundDeviceBackend(AudioBackend):
    """Audio backend using sounddevice library."""
    
    def __init__(self):
        self._sd = None
        self._available = False
        self._try_load()
    
    def _try_load(self):
        try:
            import sounddevice as sd
            self._sd = sd
            self._available = True
            logger.info("SoundDevice backend initialized successfully")
        except ImportError:
            logger.warning("SoundDevice not available")
            self._available = False
    
    def play(self, waveform: np.ndarray, sample_rate: int = 44100) -> None:
        if not self._available:
            return
        
        try:
            self._sd.play(waveform, sample_rate)
        except Exception as e:
            logger.error(f"Error playing audio: {e}")
    
    def stop(self) -> None:
        if not self._available:
            return
            
        try:
            self._sd.stop()
        except Exception as e:
            logger.error(f"Error stopping audio: {e}")
    
    @property
    def is_available(self) -> bool:
        return self._available

class PyGameBackend(AudioBackend):
    """Audio backend using pygame.mixer."""
    
    def __init__(self):
        self._pygame = None
        self._available = False
        self._current_sound = None
        self._try_load()
    
    def _try_load(self):
        try:
            import pygame
            pygame.mixer.init(frequency=44100, size=-16, channels=1, buffer=512)
            self._pygame = pygame
            self._available = True
            logger.info("PyGame audio backend initialized successfully")
        except ImportError:
            logger.warning("PyGame not available")
            self._available = False
        except Exception as e:
            logger.warning(f"Error initializing PyGame audio: {e}")
            self._available = False
    
    def play(self, waveform: np.ndarray, sample_rate: int = 44100) -> None:
        if not self._available:
            return
            
        try:
            # Scale to int16 range
            waveform = np.int16(waveform * 32767)
            
            # Create pygame Sound object
            sound = self._pygame.sndarray.make_sound(waveform)
            sound.play()
            
            # Store reference to current sound
            self._current_sound = sound
        except Exception as e:
            logger.error(f"Error playing audio with PyGame: {e}")
    
    def stop(self) -> None:
        if not self._available or not self._current_sound:
            return
            
        try:
            self._current_sound.stop()
        except Exception as e:
            logger.error(f"Error stopping PyGame audio: {e}")
    
    @property
    def is_available(self) -> bool:
        return self._available

class SilentBackend(AudioBackend):
    """Fallback silent audio backend that does nothing."""
    
    def play(self, waveform: np.ndarray, sample_rate: int = 44100) -> None:
        pass
    
    def stop(self) -> None:
        pass
    
    @property
    def is_available(self) -> bool:
        return True

class AudioEngine:
    """Unified audio engine that manages synthesis and playback across different backends."""
    
    _instance = None
    
    @classmethod
    def get_instance(cls):
        """Get the singleton instance of the audio engine."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def __init__(self):
        """Initialize the audio engine."""
        self.backends = [
            SoundDeviceBackend(),
            PyGameBackend(),
            SilentBackend()  # Fallback silent backend
        ]
        
        # Select the first available backend
        self.active_backend = None
        for backend in self.backends:
            if backend.is_available:
                self.active_backend = backend
                break
        
        global AUDIO_AVAILABLE
        AUDIO_AVAILABLE = self.active_backend is not None and not isinstance(self.active_backend, SilentBackend)
        
        # Audio settings
        self.sample_rate = 44100
        self.cache_size_limit = 50  # Maximum number of cached sounds
        
        # Sound cache with LRU tracking
        self.sound_cache = {}  # Dict mapping keys to waveforms
        self.cache_usage = []  # LRU tracking
        
        logger.info(f"Audio engine initialized with backend: {self.active_backend.__class__.__name__}")
        logger.info(f"Audio available: {AUDIO_AVAILABLE}")
    
    def synthesize(self, freq: float, duration: float, waveshape: str = "sine", 
                 attack: float = 0.01, decay: float = 0.1, sustain: float = 0.7, 
                 release: float = 0.1, overtones: int = 3) -> np.ndarray:
        """Synthesize a sound with the specified parameters.
        
        Args:
            freq: Frequency in Hz
            duration: Duration in seconds
            waveshape: Type of waveform ('sine', 'sawtooth', 'square', 'triangle')
            attack, decay, sustain, release: ADSR envelope parameters
            overtones: Number of harmonic overtones
            
        Returns:
            NumPy array containing the synthesized waveform
        """
        # Create a cache key
        cache_key = f"{freq}_{duration}_{waveshape}_{attack}_{decay}_{sustain}_{release}_{overtones}"
        
        # Check cache first
        if cache_key in self.sound_cache:
            # Update cache usage (move to front)
            self.cache_usage.remove(cache_key)
            self.cache_usage.append(cache_key)
            return self.sound_cache[cache_key]
        
        # Generate time array (use vectorized operations for speed)
        t = np.linspace(0, duration, int(self.sample_rate * duration), endpoint=False)
        
        # Initialize empty waveform
        waveform = np.zeros_like(t)
        
        # Generate base waveform with overtones
        for i in range(1, overtones + 2):
            amplitude = 1.0 / i  # Diminishing amplitude for higher harmonics
            harmonic_freq = freq * i
            
            # Apply waveshape
            if waveshape == "sine":
                waveform += amplitude * np.sin(2 * np.pi * harmonic_freq * t)
            elif waveshape == "sawtooth":
                waveform += amplitude * (2 * (t * harmonic_freq - np.floor(0.5 + t * harmonic_freq)))
            elif waveshape == "square":
                waveform += amplitude * np.sign(np.sin(2 * np.pi * harmonic_freq * t))
            elif waveshape == "triangle":
                waveform += amplitude * (2 * np.abs(2 * (t * harmonic_freq - np.floor(t * harmonic_freq + 0.5))) - 1)
        
        # Normalize to prevent clipping
        waveform = waveform / np.max(np.abs(waveform))
        
        # Apply ADSR envelope
        total_samples = len(waveform)
        attack_samples = int(attack * self.sample_rate)
        decay_samples = int(decay * self.sample_rate)
        release_samples = int(release * self.sample_rate)
        sustain_samples = total_samples - (attack_samples + decay_samples + release_samples)
        
        # Ensure we have some samples for each phase
        if sustain_samples < 0:
            attack_samples = max(1, int(total_samples * 0.1))
            decay_samples = max(1, int(total_samples * 0.2))
            release_samples = max(1, int(total_samples * 0.3))
            sustain_samples = total_samples - (attack_samples + decay_samples + release_samples)
            sustain_samples = max(0, sustain_samples)
        
        # Create and apply envelope (vectorized)
        envelope = np.zeros(total_samples)
        
        if attack_samples > 0:
            envelope[:attack_samples] = np.linspace(0, 1, attack_samples)
        
        if decay_samples > 0:
            envelope[attack_samples:attack_samples + decay_samples] = np.linspace(1, sustain, decay_samples)
        
        if sustain_samples > 0:
            envelope[attack_samples + decay_samples:attack_samples + decay_samples + sustain_samples] = sustain
        
        if release_samples > 0:
            envelope[-release_samples:] = np.linspace(sustain, 0, release_samples)
        
        final_waveform = waveform * envelope
        
        # Cache the result (with LRU management)
        if len(self.cache_usage) >= self.cache_size_limit:
            # Remove least recently used item
            oldest_key = self.cache_usage.pop(0)
            self.sound_cache.pop(oldest_key, None)
            
        self.sound_cache[cache_key] = final_waveform
        self.cache_usage.append(cache_key)
        
        return final_waveform
    
    def play(self, waveform: np.ndarray, volume: float = 1.0) -> None:
        """Play a synthesized sound.
        
        Args:
            waveform: NumPy array containing the audio waveform
            volume: Volume level (0.0 to 1.0)
        """
        if self.active_backend is None:
            return
            
        # Apply volume
        scaled_waveform = waveform * volume
        
        # Play through the active backend
        self.active_backend.play(scaled_waveform, self.sample_rate)
    
    def stop(self) -> None:
        """Stop any currently playing audio."""
        if self.active_backend is not None:
            self.active_backend.stop()
    
    def play_note(self, note: str, duration: float = 0.5, volume: float = 1.0, 
                waveshape: str = "sine") -> None:
        """Play a musical note by name.
        
        Args:
            note: Note name (e.g., 'C4', 'F#5')
            duration: Duration in seconds
            volume: Volume level (0.0 to 1.0)
            waveshape: Waveform shape
        """
        freq = self.note_to_freq(note)
        waveform = self.synthesize(freq, duration, waveshape)
        self.play(waveform, volume)
    
    def play_chord(self, notes: List[str], duration: float = 1.0, 
                 volume: float = 1.0, waveshape: str = "sine") -> None:
        """Play a chord (multiple notes simultaneously).
        
        Args:
            notes: List of note names
            duration: Duration in seconds
            volume: Volume level (0.0 to 1.0)
            waveshape: Waveform shape
        """
        if not notes:
            return
            
        # Synthesize each note
        waveforms = []
        for note in notes:
            freq = self.note_to_freq(note)
            waveform = self.synthesize(freq, duration, waveshape)
            waveforms.append(waveform)
        
        # Mix waveforms together
        mixed = np.zeros_like(waveforms[0])
        for waveform in waveforms:
            mixed += waveform
            
        # Normalize to prevent clipping
        mixed = mixed / max(1.0, np.max(np.abs(mixed)))
        
        # Play the chord
        self.play(mixed, volume)
    
    def note_to_freq(self, note: str) -> float:
        """Convert a note name to frequency in Hz.
        
        Args:
            note: Note name (e.g., 'C4', 'F#5')
            
        Returns:
            Frequency in Hz
        """
        note_map = {
            'C': 0, 'C#': 1, 'Db': 1, 'D': 2, 'D#': 3, 'Eb': 3,
            'E': 4, 'F': 5, 'F#': 6, 'Gb': 6, 'G': 7, 'G#': 8,
            'Ab': 8, 'A': 9, 'A#': 10, 'Bb': 10, 'B': 11
        }
        
        # Extract note and octave
        if len(note) >= 2:
            if note[1] in '#b':
                note_val = note_map.get(note[:2], 0)
                octave = int(note[2:]) if len(note) > 2 else 4
            else:
                note_val = note_map.get(note[0], 0)
                octave = int(note[1:]) if len(note) > 1 else 4
        else:
            note_val = note_map.get(note, 0)
            octave = 4
        
        # A4 = 440Hz, each octave is 12 semitones
        # Calculate how many semitones away from A4
        a4_pos = 9 + 4 * 12  # A4 position
        note_pos = note_val + octave * 12  # Position of the requested note
        semitones_from_a4 = note_pos - a4_pos
        
        # Calculate frequency: f = 440 * 2^(n/12)
        freq = 440.0 * (2 ** (semitones_from_a4 / 12))
        
        return freq
    
    def play_scale(self, root_note: str, scale_name: str = "Major", 
                 duration: float = 0.4, volume: float = 1.0) -> None:
        """Play a musical scale.
        
        Args:
            root_note: Root note name
            scale_name: Name of the scale to play
            duration: Duration of each note
            volume: Volume level
        """
        # Define scale patterns (semitones from root)
        scales = {
            "Major": [0, 2, 4, 5, 7, 9, 11, 12],
            "Minor": [0, 2, 3, 5, 7, 8, 10, 12],
            "Pentatonic": [0, 2, 4, 7, 9, 12],
            "Blues": [0, 3, 5, 6, 7, 10, 12],
            "Chromatic": list(range(13))
        }
        
        pattern = scales.get(scale_name, scales["Major"])
        root_freq = self.note_to_freq(root_note)
        
        # Play each note in the scale
        for semitones in pattern:
            freq = root_freq * (2 ** (semitones / 12))
            waveform = self.synthesize(freq, duration, "sine")
            self.play(waveform, volume)
            
            # Small pause between notes
            time.sleep(duration * 0.9)

# Wrapper class for backward compatibility
class EnhancedAudioSynthesis:
    """Compatibility wrapper for the unified audio engine."""
    
    def __init__(self, fundamental_freq=440.0, duration=1.0, waveshape="sine",
                 attack=0.01, decay=0.1, sustain=0.8, release=0.1, num_overtones=5):
        """Initialize the audio synthesis wrapper."""
        self.fundamental_freq = fundamental_freq
        self.duration = duration
        self.waveshape = waveshape
        self.attack = attack
        self.decay = decay
        self.sustain = sustain
        self.release = release
        self.num_overtones = num_overtones
        self.sample_rate = 44100
        
        # Get the audio engine instance
        self.engine = AudioEngine.get_instance()
    
    def play_sound(self, waveform=None, frequency=None, duration=None, waveshape=None,
                  attack=None, decay=None, sustain=None, release=None, num_overtones=None, volume=1.0):
        """Play a synthesized sound."""
        # Use provided parameters or defaults
        freq = frequency if frequency is not None else self.fundamental_freq
        dur = duration if duration is not None else self.duration
        shape = waveshape if waveshape is not None else self.waveshape
        a = attack if attack is not None else self.attack
        d = decay if decay is not None else self.decay
        s = sustain if sustain is not None else self.sustain
        r = release if release is not None else self.release
        overtones = num_overtones if num_overtones is not None else self.num_overtones
        
        if waveform is None:
            # Synthesize new waveform
            waveform = self.engine.synthesize(freq, dur, shape, a, d, s, r, overtones)
        
        # Play the sound
        self.engine.play(waveform, volume)
    
    def get_note_frequency(self, note_name):
        """Get the frequency of a note by name."""
        return self.engine.note_to_freq(note_name)
    
    def play_note(self, note_name, duration=None, waveshape=None,
                 attack=None, decay=None, sustain=None, release=None, num_overtones=None, volume=1.0):
        """Play a musical note by name."""
        # Use provided parameters or defaults
        dur = duration if duration is not None else self.duration
        shape = waveshape if waveshape is not None else self.waveshape
        
        # Play through the engine
        self.engine.play_note(note_name, dur, volume, shape)

class MusicTrainingModule(TrainingModule):
    """Base class for music-related training modules."""
    
    def __init__(self):
        """Initialize the music training module."""
        super().__init__()
        
        # Initialize audio synthesis
        self.audio = EnhancedAudioSynthesis()
        
        # Common musical elements
        self.scales = {
            "Major": [0, 2, 4, 5, 7, 9, 11, 12],
            "Minor": [0, 2, 3, 5, 7, 8, 10, 12],
            "Pentatonic": [0, 2, 4, 7, 9, 12],
            "Blues": [0, 3, 5, 6, 7, 10, 12],
            "Chromatic": list(range(13)),
            "Whole Tone": [0, 2, 4, 6, 8, 10, 12],
            "Harmonic Minor": [0, 2, 3, 5, 7, 8, 11, 12],
            "Melodic Minor": [0, 2, 3, 5, 7, 9, 11, 12]
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
            "Major 7th": [0, 4, 7, 11],
            "Minor 7th": [0, 3, 7, 10]
        }
    
    def play_scale(self, root_note="C4", scale_name="Major", direction="ascending"):
        """Play a musical scale.
        
        Args:
            root_note: Root note name
            scale_name: Name of the scale to play
            direction: "ascending", "descending", or "both"
        """
        # Get the audio engine
        engine = AudioEngine.get_instance()
        
        # Get scale pattern
        pattern = self.scales.get(scale_name, self.scales["Major"])
        
        # Play the scale
        if direction in ["ascending", "both"]:
            engine.play_scale(root_note, scale_name)
        
        if direction in ["descending", "both"]:
            # Play descending (reverse the pattern except for the first note)
            if direction == "both":
                time.sleep(0.5)  # Pause between ascending and descending
                
            rev_pattern = pattern[::-1]
            root_freq = engine.note_to_freq(root_note)
            
            for semitones in rev_pattern:
                freq = root_freq * (2 ** (semitones / 12))
                waveform = engine.synthesize(freq, 0.4)
                engine.play(waveform, 0.7)
                time.sleep(0.35)
    
    def play_chord(self, chord_name, root_note="C4", arpeggio=False):
        """Play a chord.
        
        Args:
            chord_name: Name of the chord to play
            root_note: Root note name
            arpeggio: Whether to play the notes sequentially or simultaneously
        """
        # Get the audio engine
        engine = AudioEngine.get_instance()
        
        # Get chord pattern
        pattern = self.chords.get(chord_name, self.chords["Major"])
        
        # Convert root note to frequency
        root_freq = engine.note_to_freq(root_note)
        
        if arpeggio:
            # Play notes sequentially
            for semitones in pattern:
                freq = root_freq * (2 ** (semitones / 12))
                waveform = engine.synthesize(freq, 0.4)
                engine.play(waveform, 0.7)
                time.sleep(0.35)
        else:
            # Convert semitones to notes
            notes = []
            for semitones in pattern:
                # Calculate note name for display
                freq = root_freq * (2 ** (semitones / 12))
                notes.append(self._freq_to_note(freq))
            
            # Play chord
            engine.play_chord(notes, 1.0, 0.7)
    
    def play_interval(self, interval_name, root_note="C4", direction="ascending"):
        """Play a musical interval.
        
        Args:
            interval_name: Name of the interval to play
            root_note: Root note name
            direction: "ascending", "descending", or "both"
        """
        # Get the audio engine
        engine = AudioEngine.get_instance()
        
        # Get interval size in semitones
        semitones = self.intervals.get(interval_name, 0)
        
        # Convert root note to frequency
        root_freq = engine.note_to_freq(root_note)
        
        # Calculate second note frequency
        second_freq = root_freq * (2 ** (semitones / 12))
        
        # Convert to note names for chord playing
        root_note_name = root_note
        second_note_name = self._freq_to_note(second_freq)
        
        if direction == "ascending":
            # Play root note then interval note
            engine.play_note(root_note_name, 0.5, 0.7)
            time.sleep(0.5)
            engine.play_note(second_note_name, 0.5, 0.7)
        elif direction == "descending":
            # Play interval note then root note
            engine.play_note(second_note_name, 0.5, 0.7)
            time.sleep(0.5)
            engine.play_note(root_note_name, 0.5, 0.7)
        else:  # "both" or "harmonic"
            # Play both notes together
            engine.play_chord([root_note_name, second_note_name], 1.0, 0.7)
    
    def _freq_to_note(self, freq):
        """Convert a frequency to the closest note name.
        
        This is an approximate conversion for display purposes.
        
        Args:
            freq: Frequency in Hz
            
        Returns:
            Note name as string
        """
        note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        
        # A4 = 440Hz, calculate semitones from A4
        semitones_from_a4 = 12 * np.log2(freq / 440.0)
        
        # Round to nearest semitone
        semitones_rounded = round(semitones_from_a4)
        
        # Calculate note index and octave
        note_idx = (semitones_rounded + 9) % 12  # A is at index 9
        octave = 4 + (semitones_rounded + 9) // 12
        
        return f"{note_names[note_idx]}{octave}"
    
    def get_module_state(self):
        """Get module-specific state."""
        return {
            "audio_available": AUDIO_AVAILABLE,
            "music_support": {
                "scales": list(self.scales.keys()),
                "intervals": list(self.intervals.keys()),
                "chords": list(self.chords.keys())
            }
        }

# Initialize the audio engine on import
audio_engine = AudioEngine.get_instance() 