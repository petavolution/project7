"""
Audio Engine Package for MetaMindIQTrain

This package provides audio generation and playback capabilities for the
MetaMindIQTrain platform, with a focus on music training modules.
"""

from MetaMindIQTrain.core.audio.engine import (
    AudioEngine, 
    get_audio_engine,
    SoundDeviceBackend,
    PyGameBackend,
    SilentBackend
)

__all__ = [
    'AudioEngine',
    'get_audio_engine',
    'SoundDeviceBackend',
    'PyGameBackend',
    'SilentBackend'
] 