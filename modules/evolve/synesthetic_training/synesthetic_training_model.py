#!/usr/bin/env python3
"""
Synesthetic Training Model Component

This module handles the core game logic for the Synesthetic Training module:
- Cross-sensory association generation
- Game state management
- Scoring and performance tracking
- Phase transitions
- Difficulty progression
"""

import random
import math
import time
import logging
import sys
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional

# Add the parent directory to sys.path for absolute imports when imported directly
if __name__ == "__main__" or not __package__:
    project_root = Path(__file__).parent.parent.parent.parent
    sys.path.insert(0, str(project_root))

logger = logging.getLogger(__name__)

class SynestheticTrainingModel:
    """Model component for Synesthetic Training module - handles core game logic."""
    
    def __init__(self, config=None):
        """Initialize the model with game state and business logic.
        
        Args:
            config: Optional configuration dictionary
        """
        # Module metadata
        self.id = "synesthetic_training"
        self.name = "Synesthetic Training"
        self.description = (
            "Develop synesthetic abilities by training your brain to form cross-sensory "
            "associations. Enhance neural connectivity between different sensory regions, "
            "boost creativity, and expand your cognitive flexibility through multimodal training."
        )
        
        # Game state
        self.phase = "preparation"  # preparation, association, recall, feedback
        self.level = 1
        self.score = 0
        self.trials_completed = 0
        self.current_trial = 0
        self.start_time = None
        self.last_time = None
        self.elapsed_time = 0
        self.success_rate = 0.0
        self.message = "Welcome to Synesthetic Training"
        
        # Synesthetic training specific state
        self.current_associations = []
        self.current_stimuli = []
        self.user_responses = []
        self.correct_associations = []
        
        # Set default configuration
        self._set_default_config()
        
        # Apply custom configuration if provided
        if config:
            self.config.update(config)
            
        # Initialize game
        self._init_game()
        
    def _set_default_config(self):
        """Set default configuration values."""
        self.config = {
            # Time settings
            "preparation_time": 3,
            "association_time": 10,
            "recall_time": 15,
            "feedback_time": 3,
            
            # Game parameters
            "initial_associations": 3,
            "max_associations": 12,
            "points_per_correct": 10,
            "bonus_for_streak": 5,
            "error_penalty": 2,
            
            # Association types (will be used in different combinations)
            "enabled_senses": [
                "color",    # Visual: colors
                "shape",    # Visual: shapes
                "sound",    # Auditory: tones/sounds
                "position", # Spatial: positions on screen
                "number",   # Numerical: digits/numbers
                "texture"   # Tactile simulation: visual textures
            ],
            
            # Difficulty parameters
            "level_up_threshold": 3,
            "accuracy_threshold": 0.7,
            "adaptive_difficulty": True,
        }
    
    def _init_game(self):
        """Initialize or reset the game state."""
        self.phase = "preparation"
        self.current_associations = []
        self.current_stimuli = []
        self.user_responses = []
        self.correct_associations = []
        
        # Calculate number of associations based on level
        num_associations = min(
            self.config["initial_associations"] + (self.level // 2),
            self.config["max_associations"]
        )
        
        # Determine which senses to use based on level
        available_senses = self.config["enabled_senses"]
        
        # At higher levels, use more complex combinations
        if self.level <= 3:
            # Basic level: just color-number or shape-sound associations
            sense_pairs = [("color", "number"), ("shape", "sound")]
            selected_pair = sense_pairs[self.level % len(sense_pairs)]
        else:
            # More advanced: use more sense combinations
            first_sense_options = available_senses[:4]  # Limit first sense options
            second_sense_options = [s for s in available_senses if s not in first_sense_options[:2]]  # Avoid too similar senses
            
            # Randomly select senses to associate
            first_sense = random.choice(first_sense_options)
            second_sense = random.choice(second_sense_options)
            selected_pair = (first_sense, second_sense)
        
        # Generate associations
        self._generate_associations(num_associations, selected_pair)
        
        # Set start time for preparation phase
        self.start_time = time.time()
        self.last_time = self.start_time
        self.elapsed_time = 0
        
        # Set message
        self.message = f"Prepare to form {selected_pair[0]}-{selected_pair[1]} associations..."
    
    def _generate_associations(self, num_associations, sense_pair):
        """Generate cross-sensory associations for the current trial.
        
        Args:
            num_associations: Number of associations to generate
            sense_pair: Tuple of (sense1, sense2) to associate
        """
        # Clear existing associations
        self.current_associations = []
        self.current_stimuli = []
        
        first_sense, second_sense = sense_pair
        
        # Generate stimuli based on selected senses
        first_stimuli = self._generate_stimuli_for_sense(first_sense, num_associations)
        second_stimuli = self._generate_stimuli_for_sense(second_sense, num_associations)
        
        # Shuffle second stimuli to create random associations
        random.shuffle(second_stimuli)
        
        # Create associations
        for i in range(num_associations):
            association = {
                "id": i,
                "first_sense": first_sense,
                "second_sense": second_sense,
                "first_stimulus": first_stimuli[i],
                "second_stimulus": second_stimuli[i]
            }
            self.current_associations.append(association)
        
        # Store for later phases
        self.current_stimuli = first_stimuli
        self.correct_associations = [a["second_stimulus"] for a in self.current_associations]
        
    def _generate_stimuli_for_sense(self, sense, count):
        """Generate sensory stimuli for a given sense.
        
        Args:
            sense: The sensory type to generate stimuli for
            count: Number of stimuli to generate
            
        Returns:
            List of stimuli for the specified sense
        """
        stimuli = []
        
        if sense == "color":
            # Generate distinct colors
            hues = [i * (360 / count) for i in range(count)]
            for hue in hues:
                # Convert HSV to RGB (simplified)
                h = hue / 360
                s = 0.7 + random.random() * 0.3  # High saturation
                v = 0.8 + random.random() * 0.2  # High value
                
                # HSV to RGB conversion
                if s == 0.0:
                    r = g = b = int(v * 255)
                else:
                    h *= 6.0
                    i = int(h)
                    f = h - i
                    p = v * (1.0 - s)
                    q = v * (1.0 - s * f)
                    t = v * (1.0 - s * (1.0 - f))
                    
                    if i % 6 == 0:
                        r, g, b = v, t, p
                    elif i % 6 == 1:
                        r, g, b = q, v, p
                    elif i % 6 == 2:
                        r, g, b = p, v, t
                    elif i % 6 == 3:
                        r, g, b = p, q, v
                    elif i % 6 == 4:
                        r, g, b = t, p, v
                    else:
                        r, g, b = v, p, q
                
                color = (int(r * 255), int(g * 255), int(b * 255))
                stimuli.append({"type": "color", "value": color})
                
        elif sense == "shape":
            # Generate different shapes
            shapes = ["circle", "square", "triangle", "hexagon", "diamond", 
                     "star", "cross", "heart", "pentagon", "octagon", "crescent", "arrow"]
            selected_shapes = random.sample(shapes, min(count, len(shapes)))
            
            # Repeat shapes if we need more than available
            while len(selected_shapes) < count:
                selected_shapes.append(random.choice(shapes))
                
            for shape in selected_shapes:
                stimuli.append({"type": "shape", "value": shape})
                
        elif sense == "sound":
            # Generate different sound types
            # These will be converted to actual sounds in the renderer
            sound_types = ["low_tone", "medium_tone", "high_tone", 
                          "chirp", "buzz", "chime", "bell", "beep", "boop"]
            selected_sounds = random.sample(sound_types, min(count, len(sound_types)))
            
            # Repeat sounds if we need more than available
            while len(selected_sounds) < count:
                selected_sounds.append(random.choice(sound_types))
                
            for sound in selected_sounds:
                stimuli.append({"type": "sound", "value": sound})
                
        elif sense == "position":
            # Generate different positions on a 3x3 or larger grid
            
            # Determine grid size based on count (ensure we have enough positions)
            grid_size = max(3, math.ceil(math.sqrt(count * 1.5)))
            positions = []
            
            # Generate grid positions
            for row in range(grid_size):
                for col in range(grid_size):
                    positions.append((col / grid_size, row / grid_size))
            
            # Shuffle and select the required number
            random.shuffle(positions)
            selected_positions = positions[:count]
            
            for position in selected_positions:
                stimuli.append({"type": "position", "value": position})
                
        elif sense == "number":
            # Generate unique numbers
            if count <= 10:
                # Use single digits for easier recall
                numbers = random.sample(range(1, 10), min(count, 9))
                
                # If we need more than 9, add more
                while len(numbers) < count:
                    numbers.append(random.randint(10, 99))
            else:
                # For larger counts, use double digits
                numbers = random.sample(range(10, 100), count)
                
            for number in numbers:
                stimuli.append({"type": "number", "value": number})
                
        elif sense == "texture":
            # Generate different texture patterns
            textures = ["dots", "stripes", "waves", "grid", "crosshatch", 
                       "zigzag", "gradient", "noise", "checkers", "honeycomb"]
            selected_textures = random.sample(textures, min(count, len(textures)))
            
            # Repeat textures if we need more than available
            while len(selected_textures) < count:
                selected_textures.append(random.choice(textures))
                
            for texture in selected_textures:
                stimuli.append({"type": "texture", "value": texture})
                
        return stimuli
    
    def update(self, delta_time):
        """Update the model state based on time.
        
        Args:
            delta_time: Time delta in seconds
        """
        # Update elapsed time
        self.elapsed_time += delta_time
        
        # Check for phase transitions
        self._check_phase_transitions()
    
    def _check_phase_transitions(self):
        """Check and handle phase transitions."""
        if self.phase == "preparation":
            # Transition to association phase
            if self.elapsed_time >= self.config["preparation_time"]:
                self.phase = "association"
                self.elapsed_time = 0
                self.message = "Memorize these associations!"
        
        elif self.phase == "association":
            # Transition to recall phase
            if self.elapsed_time >= self.config["association_time"]:
                self.phase = "recall"
                self.elapsed_time = 0
                self.user_responses = [None] * len(self.current_stimuli)
                self.message = "Recall the associations!"
        
        elif self.phase == "recall":
            # Transition to feedback phase
            if self.elapsed_time >= self.config["recall_time"] or self._all_responses_provided():
                self.phase = "feedback"
                self.elapsed_time = 0
                self._calculate_score()
                
                # Generate feedback message
                if self.success_rate >= 0.9:
                    self.message = "Excellent synesthetic perception! Your neural connections are strengthening."
                elif self.success_rate >= 0.7:
                    self.message = "Good work! Your cross-sensory associations are developing."
                else:
                    self.message = "Keep practicing to strengthen your synesthetic abilities."
                
                # Update trials
                self.trials_completed += 1
                self.current_trial += 1
                
                # Check for level up
                if (self.trials_completed % self.config["level_up_threshold"] == 0 and 
                    self.success_rate >= self.config["accuracy_threshold"] and
                    self.level < 20):  # Max level cap
                    
                    self.level += 1
                    self.message = f"Level up! Now at level {self.level}. Your synesthetic abilities are expanding!"
        
        elif self.phase == "feedback":
            # Transition to preparation for next trial
            if self.elapsed_time >= self.config["feedback_time"]:
                self._init_game()
    
    def _all_responses_provided(self):
        """Check if all stimuli have been matched with responses.
        
        Returns:
            True if all responses have been provided, False otherwise
        """
        return None not in self.user_responses
    
    def _calculate_score(self):
        """Calculate score based on user responses."""
        correct_count = 0
        total_count = len(self.current_stimuli)
        
        for i, (user_response, correct_response) in enumerate(zip(self.user_responses, self.correct_associations)):
            if user_response == correct_response:
                # Correct association
                correct_count += 1
                
                # Award points
                points = self.config["points_per_correct"]
                
                # Check for streaks (consecutive correct answers)
                if i > 0 and self.user_responses[i-1] == self.correct_associations[i-1]:
                    points += self.config["bonus_for_streak"]
                
                self.score += points
            else:
                # Wrong association, penalize
                self.score = max(0, self.score - self.config["error_penalty"])
        
        # Calculate success rate
        self.success_rate = correct_count / total_count if total_count > 0 else 0
    
    def process_action(self, action, data):
        """Process an action from the user.
        
        Args:
            action: The action to process
            data: Additional data for the action
            
        Returns:
            Dictionary containing the response
        """
        # Only process actions in recall phase
        if self.phase != "recall":
            return {"result": "ignored", "reason": f"not in recall phase (current: {self.phase})"}
            
        if action == "associate":
            stimulus_index = data.get("stimulus_index")
            response_index = data.get("response_index")
            
            # Validate indices
            if (stimulus_index is None or response_index is None or
                stimulus_index < 0 or stimulus_index >= len(self.current_stimuli) or
                response_index < 0 or response_index >= len(self.current_associations)):
                return {"result": "error", "reason": "invalid indices"}
            
            # Store the association
            self.user_responses[stimulus_index] = self.current_associations[response_index]["second_stimulus"]
            
            return {
                "result": "success",
                "stimulus_index": stimulus_index,
                "response_index": response_index
            }
            
        elif action == "submit":
            # Auto-fill any remaining responses with None
            for i in range(len(self.user_responses)):
                if self.user_responses[i] is None:
                    # Find an unused response
                    used_responses = set(r for r in self.user_responses if r is not None)
                    available_responses = [
                        r["second_stimulus"] for r in self.current_associations
                        if r["second_stimulus"] not in used_responses
                    ]
                    
                    if available_responses:
                        self.user_responses[i] = random.choice(available_responses)
            
            # Immediately transition to feedback phase
            self.phase = "feedback"
            self.elapsed_time = self.config["recall_time"]  # Force timeout
            
            return {"result": "success", "phase": "feedback"}
        
        # Unknown action
        return {"result": "error", "reason": "unknown action"}
    
    def get_state(self):
        """Get the current model state.
        
        Returns:
            Dict: Current state of the model
        """
        state = {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "phase": self.phase,
            "level": self.level,
            "score": self.score,
            "message": self.message,
            "trial": self.current_trial,
            "trials_completed": self.trials_completed,
            "success_rate": self.success_rate,
            "elapsed_time": self.elapsed_time,
        }
        
        # Add phase-specific data
        if self.phase == "association":
            state["associations"] = self.current_associations
        elif self.phase == "recall":
            state["stimuli"] = self.current_stimuli
            state["associations"] = self.current_associations
            state["responses"] = self.user_responses
        elif self.phase == "feedback":
            state["stimuli"] = self.current_stimuli
            state["associations"] = self.current_associations
            state["correct_associations"] = self.correct_associations
            state["user_responses"] = self.user_responses
            
        return state
        
    def reset(self):
        """Reset the model state."""
        self.level = 1
        self.score = 0
        self.trials_completed = 0
        self.current_trial = 0
        self.success_rate = 0.0
        self._init_game() 