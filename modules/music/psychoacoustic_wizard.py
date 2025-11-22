#!/usr/bin/env python3
"""
Psychoacoustic Wizard Module

A rhythm-based gameplay challenge that trains audio-visual integration,
timing precision, and pattern recognition through interactive music.

This module features:
- Rhythm gameplay with dynamic note highways
- Combo multiplier system for consecutive correct hits
- Crowd energy meter that responds to performance
- Adaptive tempo that increases with success
- Audio-visual synchronization training
"""

import time
import random
import math
import logging
from typing import Dict, List, Any, Tuple, Optional
import numpy as np

# Import base module
from MetaMindIQTrain.core.training_module import TrainingModule
from MetaMindIQTrain.modules.music.audio_synthesis import EnhancedAudioSynthesis

# Configure logging
logger = logging.getLogger(__name__)

class PsychoacousticWizardModule(TrainingModule, EnhancedAudioSynthesis):
    """
    The Psychoacoustic Wizard module trains audio-visual synchronization,
    rhythm perception, and reaction timing through an engaging rhythm game.
    
    Players respond to falling notes by pressing the corresponding keys at
    the right time, building combo multipliers and crowd energy while the
    tempo gradually increases.
    """
    
    def __init__(self, session_manager=None, config=None):
        """
        Initialize the Psychoacoustic Wizard module.
        
        Args:
            session_manager: The session manager for this training module
            config: Optional configuration parameters
        """
        TrainingModule.__init__(self)
        EnhancedAudioSynthesis.__init__(self)
        
        # Set module properties explicitly
        self.name = "Psychoacoustic Wizard"
        self.description = "Master rhythm, timing, and audio-visual integration"
        self.category = "Audio-Visual"
        self.difficulty = "Medium"
        
        # Game state
        self.combo_multiplier = 0
        self.max_combo = 0
        self.crowd_energy = 50.0  # 0-100 scale
        self.tempo = 60.0  # BPM, starting slow
        self.level = 1
        self.score = 0
        self.game_time = 0.0  # Time in seconds since game start
        self.last_update_time = time.time()
        
        # Note highway (list of notes to hit)
        self.note_highway = []
        self.hit_window = 0.15  # Time window in seconds for a hit to be valid
        
        # Audio buffer for visualization
        self.audio_buffer = None
        
        # Patterns for note sequences
        self.patterns = self._generate_patterns()
        self.current_pattern_index = 0
        
        # Performance tracking
        self.stats = {
            'notes_hit': 0,
            'notes_missed': 0,
            'max_combo': 0,
            'highest_energy': 0,
            'highest_level': 1,
            'perfect_patterns': 0
        }
        
        # Notes for the keyboard keys (C4 to B4)
        self.key_notes = ["C4", "D4", "E4", "F4", "G4", "A4", "B4"]
        
        # Start the challenge when initialized
        self.start_challenge()
    
    def _generate_patterns(self) -> List[List[Dict[str, Any]]]:
        """
        Generate rhythm patterns for different levels.
        
        Returns:
            List of level patterns, each containing note data
        """
        patterns = []
        
        # Level 1: Simple quarter notes (4/4 time)
        level1 = []
        for i in range(8):
            # Simple C-E-G pattern
            pitch = "CEGCEGCG"[i % 8]
            level1.append({
                'pitch': f"{pitch}4",
                'time': i * 60/self.tempo,  # Quarter notes
                'duration': 0.25,
                'velocity': 0.8
            })
        patterns.append(level1)
        
        # Level 2: Eighth notes (4/4 time)
        level2 = []
        for i in range(16):
            # More complex pattern
            if i % 8 == 0:
                pitch = "C"  # Downbeat
            elif i % 4 == 0:
                pitch = "G"  # Backbeat
            elif i % 2 == 0:
                pitch = "E"  # Even eighth
            else:
                pitch = "D"  # Odd eighth
            
            level2.append({
                'pitch': f"{pitch}4",
                'time': i * 30/self.tempo,  # Eighth notes
                'duration': 0.125,
                'velocity': 0.8 if i % 4 == 0 else 0.6
            })
        patterns.append(level2)
        
        # Level 3: Sixteenth notes (4/4 time)
        level3 = []
        for i in range(32):
            # Complex sixteenth note pattern
            if i % 16 == 0:
                pitch = "C"  # Downbeat
            elif i % 8 == 0:
                pitch = "G"  # Backbeat
            elif i % 4 == 0:
                pitch = "E"  # Quarter notes
            else:
                # Use a scale pattern for other sixteenths
                scale = ["C", "D", "E", "F", "G", "A", "B"]
                pitch = scale[i % 7]
            
            level3.append({
                'pitch': f"{pitch}4",
                'time': i * 15/self.tempo,  # Sixteenth notes
                'duration': 0.0625,
                'velocity': 0.9 if i % 8 == 0 else 0.7
            })
        patterns.append(level3)
        
        # Level 4: Syncopated rhythms
        level4 = []
        syncopation = [0, 2, 3, 6, 8, 10, 12, 14]  # Syncopated rhythm
        for i, beat in enumerate(syncopation):
            pitch = "CEGBAGEC"[i % 8]
            level4.append({
                'pitch': f"{pitch}4",
                'time': beat * 15/self.tempo,
                'duration': 0.125 if i % 2 == 0 else 0.25,
                'velocity': 0.85
            })
        patterns.append(level4)
        
        # Level 5: Complex mixed rhythms
        level5 = []
        # Add triplets and complex patterns
        triplets = []
        for i in range(12):
            pitch = "CEGCEGCEGCEG"[i]
            triplet_time = i * 20/self.tempo
            triplets.append({
                'pitch': f"{pitch}4",
                'time': triplet_time,
                'duration': 0.1,
                'velocity': 0.8 if i % 3 == 0 else 0.6
            })
        
        # Add some sixteenth note runs
        sixteenths = []
        for i in range(16):
            pitch = "CDEFGFED"[i % 8]
            sixteenth_time = 12 * 20/self.tempo + i * 15/self.tempo
            sixteenths.append({
                'pitch': f"{pitch}4",
                'time': sixteenth_time,
                'duration': 0.06,
                'velocity': 0.7
            })
        
        # Combine into level 5
        level5 = triplets + sixteenths
        patterns.append(level5)
        
        return patterns
    
    def start_challenge(self):
        """Start a new challenge with the current level."""
        # Reset game time
        self.game_time = 0.0
        self.last_update_time = time.time()
        
        # Initialize the note highway based on level
        self.initialize_note_highway()
        
        # Generate audio buffer for visualization
        self.generate_audio_buffer()
        
        logger.info(f"Started PsychoacousticWizard challenge at level {self.level}")
    
    def initialize_note_highway(self):
        """Initialize the note highway with a rhythmic pattern."""
        # Clear existing notes
        self.note_highway = []
        
        # Get pattern for the current level (capped by available patterns)
        pattern_index = min(self.level - 1, len(self.patterns) - 1)
        base_pattern = self.patterns[pattern_index]
        
        # Add some future time to account for the notes scrolling onto the screen
        future_time = 3.0  # 3 seconds of lead time
        
        # Add notes, shifting their times to account for the lead time
        for note in base_pattern:
            # Create a copy of the note
            new_note = note.copy()
            new_note['time'] += future_time
            
            # Add to the highway
            self.note_highway.append(new_note)
        
        self.current_pattern_index = pattern_index
    
    def update(self, dt):
        """
        Update the game state.
        
        Args:
            dt: Time delta in seconds
        """
        # Update game time
        current_time = time.time()
        time_elapsed = current_time - self.last_update_time
        self.last_update_time = current_time
        
        self.game_time += time_elapsed
        
        # Clean up passed notes (remove notes that are too old to hit)
        self.clean_up_notes()
        
        # Check if we need to add more notes
        if not self.note_highway:
            # Pattern complete, prepare for next pattern
            self.handle_pattern_complete()
        
        # Update crowd energy (slowly decays over time)
        energy_decay = 2.0 * dt  # Lose 2% energy per second
        self.crowd_energy = max(0, self.crowd_energy - energy_decay)
        
        # Track highest energy level
        if self.crowd_energy > self.stats['highest_energy']:
            self.stats['highest_energy'] = self.crowd_energy
    
    def clean_up_notes(self):
        """Clean up notes that are too old to hit."""
        # We consider a note "missed" if it's more than 0.2 seconds past the hit window
        missed_threshold = self.hit_window + 0.2
        
        missed_notes = []
        for note in self.note_highway[:]:
            time_passed = self.game_time - note['time']
            if time_passed > missed_threshold:
                # Remove the note
                self.note_highway.remove(note)
                missed_notes.append(note)
        
        # Handle missed notes
        for note in missed_notes:
            self.handle_note_miss(note)
    
    def handle_pattern_complete(self):
        """Handle completion of the current pattern."""
        # Increment level if energy is high enough
        if self.crowd_energy >= 70:
            self.level += 1
            self.stats['highest_level'] = max(self.stats['highest_level'], self.level)
            
            # Increase tempo
            self.increase_tempo(5)  # Increase by 5 BPM
            
            # Regenerate patterns at new tempo
            self.patterns = self._generate_patterns()
        
        # Start next pattern
        self.initialize_note_highway()
    
    def handle_note_hit(self, note_name):
        """
        Handle a note being hit.
        
        Args:
            note_name: The name of the note that was hit (e.g., 'C', 'D', etc.)
        
        Returns:
            bool: True if a note was successfully hit, False otherwise
        """
        # Find the closest note matching the hit note
        closest_note = None
        closest_time_diff = float('inf')
        
        for note in self.note_highway:
            note_pitch = note['pitch'][0]  # Extract just the letter name
            
            # Check if the pitch matches
            if note_pitch == note_name:
                # Calculate time difference
                time_diff = abs(self.game_time - note['time'])
                
                # Check if it's better than our current closest
                if time_diff < closest_time_diff:
                    closest_time_diff = time_diff
                    closest_note = note
        
        # Check if we found a matching note within the hit window
        if closest_note and closest_time_diff <= self.hit_window:
            # Remove the note from the highway
            self.note_highway.remove(closest_note)
            
            # Increase combo
            self.combo_multiplier += 1
            self.max_combo = max(self.max_combo, self.combo_multiplier)
            self.stats['max_combo'] = max(self.stats['max_combo'], self.max_combo)
            
            # Calculate score based on timing accuracy
            accuracy = 1.0 - (closest_time_diff / self.hit_window)
            base_points = 100
            score_increase = int(base_points * accuracy * (1 + self.combo_multiplier * 0.1))
            
            # Add score
            self.score += score_increase
            
            # Increase crowd energy
            energy_gain = 2.0 + (accuracy * 3.0)  # 2-5% depending on accuracy
            self.crowd_energy = min(100, self.crowd_energy + energy_gain)
            
            # Track hit notes
            self.stats['notes_hit'] += 1
            
            # Play the note sound (handled by renderer)
            # Generate animation effect (handled by renderer)
            
            # Return success
            return True
        
        # No hit
        return False
    
    def handle_note_miss(self, note):
        """
        Handle a note being missed.
        
        Args:
            note: The note data that was missed
        """
        # Reset combo
        self.combo_multiplier = 0
        
        # Decrease crowd energy
        self.crowd_energy = max(0, self.crowd_energy - 5.0)  # Lose 5% for a miss
        
        # Track missed notes
        self.stats['notes_missed'] += 1
    
    def increase_tempo(self, amount):
        """
        Increase the tempo by the specified amount.
        
        Args:
            amount: BPM to increase by
        """
        self.tempo += amount
        # Cap tempo to reasonable range
        self.tempo = min(180, max(60, self.tempo))
    
    def generate_audio_buffer(self):
        """Generate audio buffer for visualization."""
        # Create a simple audio buffer for visualization
        # This would be a short sample of audio corresponding to the current pattern
        sample_rate = 44100
        duration = 2.0  # 2 seconds
        
        # Create a silence buffer
        buffer = np.zeros(int(sample_rate * duration))
        
        # Add notes to the buffer based on the current pattern
        pattern_index = min(self.level - 1, len(self.patterns) - 1)
        pattern = self.patterns[pattern_index]
        
        # Add each note to the buffer
        for note in pattern:
            # Get the note time and pitch
            note_time = note['time']
            if note_time >= duration:
                continue  # Skip notes that don't fit in our buffer
                
            pitch = note['pitch']
            note_duration = note['duration']
            velocity = note['velocity']
            
            # Calculate frequency for the note
            note_name = pitch[0]
            octave = int(pitch[-1])
            
            # Get base frequency (A4 = 440 Hz)
            note_index = "C D EF G A B".replace(" ", "").find(note_name)
            if note_index == -1:
                continue  # Invalid note
                
            # Calculate semitones from A4
            semitones = note_index - 9  # A is 9 semitones from C
            semitones += (octave - 4) * 12  # Adjust for octave
            
            # Calculate frequency
            frequency = 440 * (2 ** (semitones / 12))
            
            # Generate a simple sine wave for the note
            t = np.arange(
                int(note_time * sample_rate),
                min(int((note_time + note_duration) * sample_rate), len(buffer))
            )
            if len(t) == 0:
                continue
                
            t_shifted = t - int(note_time * sample_rate)
            
            # Apply envelope
            envelope = np.ones_like(t_shifted, dtype=float)
            attack = int(0.01 * sample_rate)  # 10ms attack
            release = int(0.05 * sample_rate)  # 50ms release
            
            if attack > 0 and len(t_shifted) > attack:
                envelope[:attack] = np.linspace(0, 1, attack)
            if release > 0 and len(t_shifted) > release:
                release_start = max(0, len(t_shifted) - release)
                envelope[release_start:] = np.linspace(1, 0, len(t_shifted) - release_start)
            
            # Create the note and add to buffer
            note_wave = np.sin(2 * np.pi * frequency * t_shifted / sample_rate)
            note_wave *= envelope * velocity
            
            # Add to buffer
            buffer[t] += note_wave
        
        # Normalize buffer
        if np.max(np.abs(buffer)) > 0:
            buffer /= np.max(np.abs(buffer))
        
        # Store the buffer
        self.audio_buffer = buffer
    
    def display_status(self):
        """
        Return the current status as a string.
        
        Returns:
            str: Status string
        """
        return (f"Level: {self.level}, Tempo: {self.tempo:.0f} BPM, "
                f"Score: {self.score}, Combo: {self.combo_multiplier}x, "
                f"Energy: {self.crowd_energy:.0f}%")
    
    def process_input(self, input_data):
        """
        Process input from the client.
        
        Args:
            input_data: The input data from the client
        
        Returns:
            dict: Response data
        """
        # Handle key presses
        if 'key' in input_data:
            key = input_data['key']
            # Convert key to note name
            if key in "ABCDEFG":
                self.handle_note_hit(key)
        
        # Return current state
        return self.get_state()
    
    def get_state(self):
        """
        Get the current state for the client.
        
        Returns:
            dict: The current state
        """
        return {
            'level': self.level,
            'tempo': self.tempo,
            'score': self.score,
            'combo_multiplier': self.combo_multiplier,
            'crowd_energy': self.crowd_energy,
            'note_highway': self.note_highway,
            'game_time': self.game_time,
            'stats': self.stats
        }
        
    def handle_click(self, x, y):
        """
        Handle a click/tap event.
        
        Args:
            x: The x-coordinate of the click.
            y: The y-coordinate of the click.
            
        Returns:
            dict: A dictionary containing the result of the click.
        """
        # Calculate hit area based on screen dimensions
        screen_width = self.__class__.SCREEN_WIDTH or 1024
        screen_height = self.__class__.SCREEN_HEIGHT or 768
        
        # Define the hit zone area (bottom quarter of the screen)
        hit_zone_y = screen_height * 0.75
        hit_zone_height = screen_height * 0.1
        
        # Check if click is in the hit zone
        if hit_zone_y - hit_zone_height/2 <= y <= hit_zone_y + hit_zone_height/2:
            # Determine which note lane was clicked
            lane_width = screen_width / 7  # 7 notes (C through B)
            
            note_index = int(x / lane_width)
            if 0 <= note_index < 7:
                note_name = "CDEFGAB"[note_index]
                
                # Try to hit the note
                hit_successful = self.handle_note_hit(note_name)
                
                if hit_successful:
                    return {
                        "success": True,
                        "message": "Hit!",
                        "combo": self.combo_multiplier
                    }
            
            # If we got here, the click didn't hit any active note
            return {
                "success": False,
                "message": "Miss! Try to hit notes exactly when they reach the line."
            }
        
        return {
            "success": False,
            "message": "Click/tap when notes reach the target zone."
        }


# Register this module when imported
if __name__ != "__main__":
    # This import is here to avoid circular imports
    from MetaMindIQTrain.modules.module_provider import register_module
    register_module(PsychoacousticWizardModule) 