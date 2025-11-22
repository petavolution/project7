import numpy as np
import random
import sounddevice as sd

# 31-EDO tuning system
EDO_DIVISIONS = 31
BASE_FREQ = 16.35  # C0 in Hz

def generate_31edo_frequencies(octaves=8):
    """Generate all 31-EDO frequencies across multiple octaves."""
    freqs = []
    for octave in range(octaves):
        for step in range(EDO_DIVISIONS):
            freq = BASE_FREQ * (2 ** octave) * (2 ** (step / EDO_DIVISIONS))
            freqs.append(freq)
    return freqs

# Harmonic purity ranking
HARMONIC_RATIOS = [1, 3/2, 5/4, 7/4, 9/8]

def harmonic_adjust(frequencies):
    """Adjusts frequencies to the nearest harmonic ratio to minimize beating."""
    adjusted = []
    for f in frequencies:
        best_fit = min(HARMONIC_RATIOS, key=lambda h: abs(f - h * f))
        adjusted.append(best_fit * f)
    return adjusted

# Real-time Schwebung minimization
def compute_beat_frequencies(frequencies):
    """Calculate beat frequencies to identify unstable pairs."""
    beats = []
    for i in range(len(frequencies)):
        for j in range(i + 1, len(frequencies)):
            beat_freq = abs(frequencies[i] - frequencies[j])
            if 1 <= beat_freq <= 15:  # Detect dissonant wobble range
                beats.append((frequencies[i], frequencies[j], beat_freq))
    return beats

# Dynamic Schwebung suppression
def auto_correct_beating(frequencies):
    """Dynamically adjust frequencies to reduce audible beating."""
    corrected = []
    for f in frequencies:
        beat_candidates = [f * r for r in HARMONIC_RATIOS]
        best_fit = min(beat_candidates, key=lambda h: sum(abs(h - other) for other in frequencies))
        corrected.append(best_fit)
    return corrected

# Psychoacoustic filtering & amplitude modulation
def amplitude_modulation(samples, rate=44100):
    """Apply dynamic amplitude modulation to smooth unstable tones."""
    envelope = np.sin(np.linspace(0, np.pi, len(samples)))
    return samples * envelope

# Random Melody Generation with Dynamic Harmonization
def generate_melody(duration=5, sample_rate=44100, style="microtonal"):
    """Generate a random melody using extreme harmonic purity adjustments."""
    melody_freqs = random.sample(generate_31edo_frequencies(), 5)
    melody_freqs = auto_correct_beating(melody_freqs)
    time = np.linspace(0, duration, sample_rate * duration, False)
    wave = sum(np.sin(2 * np.pi * f * time) for f in melody_freqs) / len(melody_freqs)
    wave = amplitude_modulation(wave)
    
    if style == "dubstep":
        wave *= np.sin(2 * np.pi * 0.5 * time)  # Add wobble bass effect
    elif style == "prog_metal":
        wave *= np.sign(np.sin(2 * np.pi * 0.25 * time))  # Add aggressive tone shifts
    
    return wave

# Play the generated melodies in different styles
melody_microtonal = generate_melody(style="microtonal")
melody_dubstep = generate_melody(style="dubstep")
melody_prog_metal = generate_melody(style="prog_metal")

sd.play(melody_microtonal, samplerate=44100)
sd.wait()
sd.play(melody_dubstep, samplerate=44100)
sd.wait()
sd.play(melody_prog_metal, samplerate=44100)
sd.wait()
