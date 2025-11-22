#!/usr/bin/env python3
"""
Unified Audio Engine for MetaMindIQTrain

This module provides a unified audio engine with pluggable backends for
different audio output methods. It includes caching for performance optimization
and a consistent API regardless of the underlying audio implementation.
"""

import time
import logging
import threading
from abc import ABC, abstractmethod
from collections import OrderedDict
from typing import Dict, List, Tuple, Optional, Union, Any

import numpy as np

# Configure logging
logger = logging.getLogger(__name__)

# Simple LRU Cache implementation
class LRUCache:
    """Least Recently Used cache for audio data."""
    
    def __init__(self, max_size=100):
        """Initialize the LRU cache with maximum size.
        
        Args:
            max_size: Maximum number of items to store in cache
        """
        self.cache = OrderedDict()
        self.max_size = max_size
    
    def __contains__(self, key):
        """Check if key is in cache."""
        return key in self.cache
    
    def __getitem__(self, key):
        """Get item from cache and mark as recently used."""
        if key in self.cache:
            # Move to end to mark as recently used
            value = self.cache.pop(key)
            self.cache[key] = value
            return value
        raise KeyError(key)
    
    def __setitem__(self, key, value):
        """Add item to cache, evicting least recently used if necessary."""
        if key in self.cache:
            # Remove existing item first
            self.cache.pop(key)
        elif len(self.cache) >= self.max_size:
            # Remove oldest item if at capacity
            self.cache.popitem(last=False)
        # Add to end (most recently used)
        self.cache[key] = value

# Abstract base class for audio backends
class AudioBackend(ABC):
    """Abstract base class for audio backend implementations."""
    
    @abstractmethod
    def initialize(self):
        """Initialize the audio backend."""
        pass
    
    @abstractmethod
    def generate_waveform(self, frequency: float, duration: float, 
                         waveform: str = 'sine', envelope: Optional[Dict] = None) -> np.ndarray:
        """Generate a waveform with the specified parameters.
        
        Args:
            frequency: The frequency in Hz
            duration: Duration in seconds
            waveform: Type of waveform (sine, square, sawtooth, triangle)
            envelope: ADSR envelope parameters
            
        Returns:
            NumPy array with the generated audio data
        """
        pass
    
    @abstractmethod
    def play(self, audio_data: np.ndarray):
        """Play audio data.
        
        Args:
            audio_data: NumPy array with audio data to play
        """
        pass
    
    @abstractmethod
    def mix_frequencies(self, frequencies: List[float], duration: float,
                        waveform: str = 'sine', envelope: Optional[Dict] = None) -> np.ndarray:
        """Mix multiple frequencies together.
        
        Args:
            frequencies: List of frequencies in Hz
            duration: Duration in seconds
            waveform: Type of waveform
            envelope: ADSR envelope parameters
            
        Returns:
            NumPy array with mixed audio data
        """
        pass
    
    @abstractmethod
    def play_sequence(self, frequencies: List[float], durations: List[float],
                     interval: float = 0.1, envelope: Optional[Dict] = None, 
                     waveform: str = 'sine'):
        """Play a sequence of notes with specified timing.
        
        Args:
            frequencies: List of frequencies in Hz
            durations: List of durations in seconds
            interval: Time between notes in seconds
            envelope: ADSR envelope parameters
            waveform: Type of waveform
        """
        pass
    
    @abstractmethod
    def stop_all(self):
        """Stop all playing sounds."""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if this backend is available on the current system.
        
        Returns:
            True if available, False otherwise
        """
        pass

# SoundDevice backend implementation
class SoundDeviceBackend(AudioBackend):
    """SoundDevice backend implementation."""
    
    def __init__(self):
        """Initialize the SoundDevice backend."""
        self.sample_rate = 44100
        self.playing_sounds = []
        try:
            import sounddevice as sd
            self.sd = sd
            self.initialize()
        except ImportError:
            raise ImportError("sounddevice not installed")
    
    def initialize(self):
        """Initialize the audio backend."""
        logger.info("Initializing SoundDevice backend")
        self.sd.default.samplerate = self.sample_rate
    
    def generate_waveform(self, frequency, duration, waveform='sine', envelope=None):
        """Generate a waveform using sounddevice."""
        # Generate time array
        t = np.linspace(0, duration, int(self.sample_rate * duration), endpoint=False)
        
        # Generate basic waveform
        if waveform == 'sine':
            audio_data = np.sin(2 * np.pi * frequency * t)
        elif waveform == 'square':
            audio_data = np.sign(np.sin(2 * np.pi * frequency * t))
        elif waveform == 'sawtooth':
            audio_data = 2 * (t * frequency - np.floor(0.5 + t * frequency))
        elif waveform == 'triangle':
            audio_data = 2 * np.abs(2 * (t * frequency - np.floor(t * frequency + 0.5))) - 1
        else:
            logger.warning(f"Unknown waveform type: {waveform}, fallback to sine")
            audio_data = np.sin(2 * np.pi * frequency * t)
        
        # Apply envelope if specified
        if envelope:
            audio_data = self._apply_envelope(audio_data, envelope, duration)
        
        # Normalize to prevent clipping
        audio_data = audio_data / np.max(np.abs(audio_data))
        
        return audio_data
    
    def _apply_envelope(self, audio_data, envelope, duration):
        """Apply an ADSR envelope to the audio data."""
        sample_rate = self.sample_rate
        num_samples = len(audio_data)
        
        # Default ADSR values
        attack = envelope.get('attack', 0.01)
        decay = envelope.get('decay', 0.1)
        sustain = envelope.get('sustain', 0.7)
        release = envelope.get('release', 0.1)
        
        # Convert times to sample counts
        attack_samples = int(attack * sample_rate)
        decay_samples = int(decay * sample_rate)
        release_samples = int(release * sample_rate)
        sustain_samples = num_samples - attack_samples - decay_samples - release_samples
        
        # Create envelope array
        env = np.zeros(num_samples)
        
        # Attack phase
        if attack_samples > 0:
            env[:attack_samples] = np.linspace(0, 1, attack_samples)
        
        # Decay phase
        if decay_samples > 0:
            env[attack_samples:attack_samples+decay_samples] = np.linspace(1, sustain, decay_samples)
        
        # Sustain phase
        if sustain_samples > 0:
            env[attack_samples+decay_samples:attack_samples+decay_samples+sustain_samples] = sustain
        
        # Release phase
        if release_samples > 0:
            env[-release_samples:] = np.linspace(sustain, 0, release_samples)
        
        # Apply envelope
        return audio_data * env
    
    def play(self, audio_data):
        """Play audio data using sounddevice."""
        try:
            self.sd.play(audio_data, self.sample_rate)
        except Exception as e:
            logger.error(f"Error playing audio: {e}")
    
    def mix_frequencies(self, frequencies, duration, waveform='sine', envelope=None):
        """Mix multiple frequencies together."""
        # Generate each frequency
        waveforms = [self.generate_waveform(freq, duration, waveform, envelope) 
                    for freq in frequencies]
        
        # Mix them together
        mixed = np.zeros_like(waveforms[0])
        for wave in waveforms:
            mixed += wave
        
        # Normalize to prevent clipping
        mixed = mixed / max(1.0, np.max(np.abs(mixed)) * 1.5)
        
        return mixed
    
    def play_sequence(self, frequencies, durations, interval=0.1, envelope=None, waveform='sine'):
        """Play a sequence of notes with specified timing."""
        def play_thread():
            for i, (freq, dur) in enumerate(zip(frequencies, durations)):
                try:
                    audio_data = self.generate_waveform(freq, dur, waveform, envelope)
                    self.play(audio_data)
                    time.sleep(dur + interval)
                except Exception as e:
                    logger.error(f"Error playing sequence note {i}: {e}")
        
        # Start in a background thread
        thread = threading.Thread(target=play_thread)
        thread.daemon = True
        thread.start()
    
    def stop_all(self):
        """Stop all playing sounds."""
        try:
            self.sd.stop()
        except Exception as e:
            logger.error(f"Error stopping sounds: {e}")
    
    def is_available(self):
        """Check if this backend is available."""
        try:
            import sounddevice
            return True
        except ImportError:
            return False

# PyGame backend implementation
class PyGameBackend(AudioBackend):
    """PyGame backend implementation."""
    
    def __init__(self):
        """Initialize the PyGame backend."""
        self.sample_rate = 44100
        self.audio_channels = {}  # Track active channels
        try:
            import pygame
            self.pygame = pygame
            self.initialize()
        except ImportError:
            raise ImportError("pygame not installed")
    
    def initialize(self):
        """Initialize the audio backend."""
        logger.info("Initializing PyGame backend")
        self.pygame.mixer.init(frequency=self.sample_rate, channels=1)
    
    def generate_waveform(self, frequency, duration, waveform='sine', envelope=None):
        """Generate a waveform using PyGame."""
        # Generate audio data similar to SoundDevice backend
        samples = int(self.sample_rate * duration)
        t = np.linspace(0, duration, samples, endpoint=False)
        
        # Generate basic waveform
        if waveform == 'sine':
            audio_data = np.sin(2 * np.pi * frequency * t)
        elif waveform == 'square':
            audio_data = np.sign(np.sin(2 * np.pi * frequency * t))
        elif waveform == 'sawtooth':
            audio_data = 2 * (t * frequency - np.floor(0.5 + t * frequency))
        elif waveform == 'triangle':
            audio_data = 2 * np.abs(2 * (t * frequency - np.floor(t * frequency + 0.5))) - 1
        else:
            audio_data = np.sin(2 * np.pi * frequency * t)
        
        # Apply envelope if specified
        if envelope:
            # Apply ADSR envelope similar to SoundDevice backend
            sample_rate = self.sample_rate
            num_samples = len(audio_data)
            
            # Default ADSR values
            attack = envelope.get('attack', 0.01)
            decay = envelope.get('decay', 0.1)
            sustain = envelope.get('sustain', 0.7)
            release = envelope.get('release', 0.1)
            
            # Convert times to sample counts
            attack_samples = int(attack * sample_rate)
            decay_samples = int(decay * sample_rate)
            release_samples = int(release * sample_rate)
            sustain_samples = num_samples - attack_samples - decay_samples - release_samples
            
            # Create envelope array
            env = np.zeros(num_samples)
            
            # Attack phase
            if attack_samples > 0:
                env[:attack_samples] = np.linspace(0, 1, attack_samples)
            
            # Decay phase
            if decay_samples > 0:
                env[attack_samples:attack_samples+decay_samples] = np.linspace(1, sustain, decay_samples)
            
            # Sustain phase
            if sustain_samples > 0:
                env[attack_samples+decay_samples:attack_samples+decay_samples+sustain_samples] = sustain
            
            # Release phase
            if release_samples > 0:
                env[-release_samples:] = np.linspace(sustain, 0, release_samples)
            
            # Apply envelope
            audio_data = audio_data * env
        
        # Normalize to prevent clipping
        audio_data = audio_data / np.max(np.abs(audio_data))
        
        # Convert to 16-bit PCM
        audio_data = (audio_data * 32767).astype(np.int16)
        
        return audio_data
    
    def play(self, audio_data):
        """Play audio data using PyGame."""
        try:
            # Convert numpy array to PyGame Sound
            sound = self.pygame.mixer.Sound(buffer=audio_data)
            
            # Play the sound
            channel = sound.play()
            
            # Track the channel
            if channel is not None:
                self.audio_channels[id(sound)] = (sound, channel)
        except Exception as e:
            logger.error(f"Error playing audio with PyGame: {e}")
    
    def mix_frequencies(self, frequencies, duration, waveform='sine', envelope=None):
        """Mix multiple frequencies together."""
        if not frequencies:
            return np.zeros(int(self.sample_rate * duration))
        
        # Generate each waveform
        waveforms = []
        for freq in frequencies:
            waveform_data = self.generate_waveform(freq, duration, waveform, envelope)
            # Convert back to float for mixing
            waveforms.append(waveform_data.astype(np.float32) / 32767.0)
        
        # Mix waveforms
        mixed = np.zeros_like(waveforms[0])
        for wave in waveforms:
            mixed += wave
        
        # Normalize
        mixed = mixed / max(1.0, np.max(np.abs(mixed)) * 1.5)
        
        # Convert back to 16-bit PCM
        mixed = (mixed * 32767).astype(np.int16)
        
        return mixed
    
    def play_sequence(self, frequencies, durations, interval=0.1, envelope=None, waveform='sine'):
        """Play a sequence of notes with specified timing."""
        def play_thread():
            for i, (freq, dur) in enumerate(zip(frequencies, durations)):
                try:
                    audio_data = self.generate_waveform(freq, dur, waveform, envelope)
                    self.play(audio_data)
                    time.sleep(dur + interval)
                except Exception as e:
                    logger.error(f"Error playing sequence note {i}: {e}")
        
        # Start in a background thread
        thread = threading.Thread(target=play_thread)
        thread.daemon = True
        thread.start()
    
    def stop_all(self):
        """Stop all playing sounds."""
        try:
            self.pygame.mixer.stop()
            self.audio_channels.clear()
        except Exception as e:
            logger.error(f"Error stopping sounds: {e}")
    
    def is_available(self):
        """Check if this backend is available."""
        try:
            import pygame
            return True
        except ImportError:
            return False

# Silent backend for environments without audio capabilities
class SilentBackend(AudioBackend):
    """Silent backend implementation for environments without audio capabilities."""
    
    def initialize(self):
        """Initialize the silent backend."""
        logger.info("Using silent audio backend (no audio output)")
    
    def generate_waveform(self, frequency, duration, waveform='sine', envelope=None):
        """Generate a dummy waveform (no actual audio)."""
        # Generate empty audio data with correct shape
        samples = int(44100 * duration)
        return np.zeros(samples)
    
    def play(self, audio_data):
        """Simulate playing audio (no actual output)."""
        logger.debug(f"Silent backend: would play {len(audio_data)} samples")
    
    def mix_frequencies(self, frequencies, duration, waveform='sine', envelope=None):
        """Simulate mixing frequencies (no actual output)."""
        samples = int(44100 * duration)
        return np.zeros(samples)
    
    def play_sequence(self, frequencies, durations, interval=0.1, envelope=None, waveform='sine'):
        """Simulate playing a sequence (no actual output)."""
        total_duration = sum(durations) + interval * (len(durations) - 1)
        logger.debug(f"Silent backend: would play sequence for {total_duration:.2f}s")
    
    def stop_all(self):
        """Simulate stopping all sounds (no actual effect)."""
        pass
    
    def is_available(self):
        """Always available as fallback."""
        return True

# The main AudioEngine class
class AudioEngine:
    """Unified audio engine with pluggable backends and optimized synthesis."""
    
    def __init__(self, backend='auto'):
        """Initialize the AudioEngine with the specified backend.
        
        Args:
            backend: Backend to use ('auto', 'sounddevice', 'pygame', 'silent')
        """
        self.backend = self._initialize_backend(backend)
        self.cache = LRUCache(max_size=100)  # Cache for frequently used sounds
    
    def _initialize_backend(self, backend_name):
        """Initialize appropriate audio backend based on availability.
        
        Args:
            backend_name: Name of the backend to initialize
            
        Returns:
            Initialized AudioBackend instance
        """
        if backend_name == 'auto':
            # Try each backend in order of preference
            backends = [SoundDeviceBackend, PyGameBackend, SilentBackend]
            for backend_class in backends:
                try:
                    backend = backend_class()
                    logger.info(f"Using audio backend: {backend_class.__name__}")
                    return backend
                except ImportError:
                    continue
                except Exception as e:
                    logger.warning(f"Failed to initialize {backend_class.__name__}: {e}")
            
            # Fallback to silent backend
            logger.warning("No audio backends available, using silent mode")
            return SilentBackend()
        elif backend_name == 'sounddevice':
            return SoundDeviceBackend()
        elif backend_name == 'pygame':
            return PyGameBackend()
        else:
            return SilentBackend()  # Fallback silent backend
    
    def play_note(self, frequency, duration=0.5, envelope=None, waveform='sine'):
        """Play a note with caching for improved performance.
        
        Args:
            frequency: The frequency in Hz
            duration: Duration in seconds
            envelope: ADSR envelope parameters
            waveform: Type of waveform
        """
        try:
            # Generate cache key
            cache_key = f"{frequency}:{duration}:{waveform}:{envelope}"
            
            # Check cache first
            if cache_key in self.cache:
                sound_data = self.cache[cache_key]
            else:
                # Generate new sound and cache it
                sound_data = self.backend.generate_waveform(frequency, duration, waveform, envelope)
                self.cache[cache_key] = sound_data
            
            # Play the sound
            self.backend.play(sound_data)
        except Exception as e:
            logger.error(f"Error in play_note: {e}")
    
    def play_chord(self, frequencies, duration=0.5, envelope=None, waveform='sine'):
        """Play multiple notes simultaneously as a chord.
        
        Args:
            frequencies: List of frequencies in Hz
            duration: Duration in seconds
            envelope: ADSR envelope parameters
            waveform: Type of waveform
        """
        try:
            # Generate cache key
            cache_key = f"chord:{','.join(str(f) for f in frequencies)}:{duration}:{waveform}:{envelope}"
            
            # Check cache first
            if cache_key in self.cache:
                mixed_data = self.cache[cache_key]
            else:
                # Mix all frequencies together
                mixed_data = self.backend.mix_frequencies(frequencies, duration, waveform, envelope)
                self.cache[cache_key] = mixed_data
            
            # Play the mixed sound
            self.backend.play(mixed_data)
        except Exception as e:
            logger.error(f"Error in play_chord: {e}")
    
    def play_sequence(self, frequencies, durations, interval=0.1, envelope=None, waveform='sine'):
        """Play a sequence of notes with specified timing.
        
        Args:
            frequencies: List of frequencies in Hz
            durations: List of durations in seconds
            interval: Time between notes in seconds
            envelope: ADSR envelope parameters
            waveform: Type of waveform
        """
        try:
            self.backend.play_sequence(frequencies, durations, interval, envelope, waveform)
        except Exception as e:
            logger.error(f"Error in play_sequence: {e}")
    
    def stop_all(self):
        """Stop all playing sounds."""
        try:
            self.backend.stop_all()
        except Exception as e:
            logger.error(f"Error in stop_all: {e}")
    
    def get_backend_name(self):
        """Get the name of the current audio backend.
        
        Returns:
            String with the backend name
        """
        return self.backend.__class__.__name__

# Create a singleton instance
_audio_engine_instance = None

def get_audio_engine(backend='auto'):
    """Get or create the singleton AudioEngine instance.
    
    Args:
        backend: Backend to use (only used on first call)
        
    Returns:
        AudioEngine instance
    """
    global _audio_engine_instance
    if _audio_engine_instance is None:
        _audio_engine_instance = AudioEngine(backend)
    return _audio_engine_instance 