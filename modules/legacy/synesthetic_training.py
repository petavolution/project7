#!/usr/bin/env python3
"""
Synesthetic Training Module

This innovative module trains users to develop synesthetic abilities - the ability to
associate one sensory input with another (such as colors with numbers, sounds with shapes).
The training enhances cognitive flexibility, creative thinking, and neural connectivity
between different sensory processing regions of the brain.
"""

import random
import math
import time
import logging
from typing import Dict, Any, List, Tuple, Optional
import pygame

# Import base module class
from .base_module import BaseModule

logger = logging.getLogger(__name__)

class SynestheticTrainingModule(BaseModule):
    """Synesthetic Training module for enhancing cross-sensory associations and cognitive flexibility."""
    
    def __init__(self, config=None):
        """Initialize the Synesthetic Training module.
        
        Args:
            config: Optional configuration dictionary
        """
        # Initialize base class
        super().__init__(config)
        
        # Set module identification
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
    
    def get_state(self) -> Dict[str, Any]:
        """Get the current state of the module.
        
        Returns:
            Dictionary containing the current state
        """
        # Calculate elapsed time
        current_time = time.time()
        delta_time = current_time - self.last_time
        self.last_time = current_time
        
        # Update elapsed time
        self.elapsed_time += delta_time
        
        # Check for phase transitions
        self._check_phase_transitions()
        
        # Build and return state
        state = {
            "module_id": self.id,
            "module_name": self.name,
            "phase": self.phase,
            "level": self.level,
            "score": self.score,
            "message": self.message,
            "trial": self.current_trial,
            "trials_completed": self.trials_completed,
            "success_rate": self.success_rate,
            "elapsed_time": self.elapsed_time,
            "components": self._generate_components(),
        }
        
        # Add phase-specific data
        if self.phase == "association":
            state["associations"] = self.current_associations
        elif self.phase == "recall":
            state["stimuli"] = self.current_stimuli
            state["responses"] = self.user_responses
        elif self.phase == "feedback":
            state["stimuli"] = self.current_stimuli
            state["correct_associations"] = self.correct_associations
            state["user_responses"] = self.user_responses
        
        return state
    
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
    
    def handle_input(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle user input.
        
        Args:
            input_data: Dictionary containing input data
            
        Returns:
            Dictionary containing the response
        """
        # Only process inputs in recall phase
        if self.phase != "recall":
            return {"result": "ignored", "reason": f"not in recall phase (current: {self.phase})"}
        
        # Get input type
        input_type = input_data.get("type")
        
        # Handle click input
        if input_type == "click":
            x = input_data.get("x", 0)
            y = input_data.get("y", 0)
            
            return self._handle_click(x, y)
        
        # Handle action input
        elif input_type == "action":
            action = input_data.get("action")
            data = input_data.get("data", {})
            
            return self._handle_action(action, data)
        
        # Unknown input type
        else:
            return {"result": "error", "reason": "unknown input type"}
    
    def _handle_click(self, x, y):
        """Handle mouse click input.
        
        Args:
            x: X coordinate of the click
            y: Y coordinate of the click
            
        Returns:
            Dictionary containing the response
        """
        # Handle click based on UI layout
        # This will be highly dependent on how the stimuli are rendered
        
        # Example implementation:
        # Check if click is on a stimulus
        stimulus_index = self._get_stimulus_at_position(x, y)
        if stimulus_index is not None:
            return {
                "result": "select_stimulus",
                "stimulus_index": stimulus_index
            }
            
        # Check if click is on a response option
        response_index = self._get_response_at_position(x, y)
        if response_index is not None:
            return {
                "result": "select_response",
                "response_index": response_index
            }
        
        return {"result": "no_hit"}
    
    def _get_stimulus_at_position(self, x, y):
        """Get the index of a stimulus at the given position.
        
        Args:
            x: X coordinate
            y: Y coordinate
            
        Returns:
            Index of the stimulus or None if not found
        """
        # This is a placeholder - the actual implementation would depend on
        # the specific rendering of stimuli in the UI
        return None
    
    def _get_response_at_position(self, x, y):
        """Get the index of a response option at the given position.
        
        Args:
            x: X coordinate
            y: Y coordinate
            
        Returns:
            Index of the response or None if not found
        """
        # This is a placeholder - the actual implementation would depend on
        # the specific rendering of response options in the UI
        return None
    
    def _handle_action(self, action, data):
        """Handle action input.
        
        Args:
            action: Action to perform
            data: Additional data for the action
            
        Returns:
            Dictionary containing the response
        """
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
    
    def _generate_components(self):
        """Generate UI components based on the current state.
        
        Returns:
            List of component dictionaries
        """
        components = []
        
        # Add phase message
        components.append({
            "type": "text",
            "text": self.message,
            "position": (400, 50),
            "font_size": "medium",
            "color": "info_text",
            "align": "center"
        })
        
        # Add level and score info
        components.append({
            "type": "text",
            "text": f"Level: {self.level}   Score: {self.score}",
            "position": (400, 80),
            "font_size": "medium",
            "color": "text",
            "align": "center"
        })
        
        # Add timer
        if self.phase in ["association", "recall"]:
            phase_time = self.config[f"{self.phase}_time"]
            remaining = max(0, phase_time - self.elapsed_time)
            progress = 1.0 - (remaining / phase_time)
            
            components.append({
                "type": "progress",
                "rect": (100, 120, 600, 20),
                "value": progress,
                "color": "primary"
            })
            
            components.append({
                "type": "text",
                "text": f"Time: {int(remaining)}s",
                "position": (400, 150),
                "font_size": "small",
                "color": "text_secondary",
                "align": "center"
            })
        
        # Add phase-specific components
        if self.phase == "association":
            # Association phase - display pairs to memorize
            self._add_association_components(components)
        elif self.phase == "recall":
            # Recall phase - display stimuli and response options
            self._add_recall_components(components)
        elif self.phase == "feedback":
            # Feedback phase - display correct vs. user answers
            self._add_feedback_components(components)
        
        # Add submit button in recall phase
        if self.phase == "recall":
            components.append({
                "type": "button",
                "text": "Submit",
                "rect": (350, 580, 100, 40),
                "action": "submit"
            })
        
        return components
    
    def _add_association_components(self, components):
        """Add association phase specific components.
        
        Args:
            components: List of components to add to
        """
        # Display instruction
        components.append({
            "type": "text",
            "text": "Memorize these associations:",
            "position": (400, 180),
            "font_size": "medium",
            "color": "highlight",
            "align": "center"
        })
        
        # Create a grid layout for associations
        num_associations = len(self.current_associations)
        cols = min(3, num_associations)
        rows = (num_associations + cols - 1) // cols
        
        cell_width = 180
        cell_height = 180
        start_x = 400 - (cols * cell_width) // 2
        start_y = 230
        
        # Add each association pair
        for i, association in enumerate(self.current_associations):
            row = i // cols
            col = i % cols
            
            x = start_x + col * cell_width + cell_width // 2
            y = start_y + row * cell_height + cell_height // 2
            
            # Adjust y for multiple rows
            if rows > 1:
                y = start_y + row * (350 // rows)
            
            # Get stimuli
            first_stimulus = association["first_stimulus"]
            second_stimulus = association["second_stimulus"]
            
            # Add container
            components.append({
                "type": "rect",
                "rect": (x - 70, y - 70, 140, 140),
                "color": "content_bg",
                "border_color": "divider",
                "border_width": 2,
                "corner_radius": 5
            })
            
            # Add first stimulus (top)
            self._add_stimulus_component(components, first_stimulus, (x, y - 30))
            
            # Add arrow connecting the two
            components.append({
                "type": "text",
                "text": "↓",
                "position": (x, y),
                "font_size": "medium",
                "color": "highlight",
                "align": "center"
            })
            
            # Add second stimulus (bottom)
            self._add_stimulus_component(components, second_stimulus, (x, y + 30))
    
    def _add_recall_components(self, components):
        """Add recall phase specific components.
        
        Args:
            components: List of components to add to
        """
        # Display instruction
        components.append({
            "type": "text",
            "text": "Match each item with its association:",
            "position": (400, 180),
            "font_size": "medium",
            "color": "highlight",
            "align": "center"
        })
        
        # Create a layout for stimuli and responses
        num_items = len(self.current_stimuli)
        
        # Display stimuli on the left
        stimulus_x = 200
        
        for i, stimulus in enumerate(self.current_stimuli):
            y = 230 + i * (300 / num_items)
            
            # Add stimulus container
            components.append({
                "type": "rect",
                "rect": (stimulus_x - 40, y - 40, 80, 80),
                "color": "content_bg",
                "border_color": "primary",
                "border_width": 2,
                "corner_radius": 5,
                "id": f"stimulus_{i}"
            })
            
            # Add the stimulus
            self._add_stimulus_component(components, stimulus, (stimulus_x, y))
            
            # Add user's response if any
            if self.user_responses[i] is not None:
                # Draw line connecting stimulus to response
                # This would be better handled by the renderer
                pass
        
        # Display response options on the right
        response_x = 600
        associations = self.current_associations
        
        for i, association in enumerate(associations):
            y = 230 + i * (300 / num_items)
            
            # Add response container
            components.append({
                "type": "rect",
                "rect": (response_x - 40, y - 40, 80, 80),
                "color": "content_bg",
                "border_color": "primary",
                "border_width": 2,
                "corner_radius": 5,
                "id": f"response_{i}"
            })
            
            # Add the response stimulus
            self._add_stimulus_component(components, association["second_stimulus"], (response_x, y))
    
    def _add_feedback_components(self, components):
        """Add feedback phase specific components.
        
        Args:
            components: List of components to add to
        """
        # Display instruction
        components.append({
            "type": "text",
            "text": f"Your accuracy: {self.success_rate:.0%}",
            "position": (400, 180),
            "font_size": "medium",
            "color": "highlight",
            "align": "center"
        })
        
        # Create a layout similar to recall but showing correct vs. user answers
        num_items = len(self.current_stimuli)
        
        for i, stimulus in enumerate(self.current_stimuli):
            y = 230 + i * (300 / num_items)
            
            # Display stimulus
            stimulus_x = 150
            
            # Add stimulus container
            components.append({
                "type": "rect",
                "rect": (stimulus_x - 30, y - 30, 60, 60),
                "color": "content_bg",
                "border_color": "primary",
                "border_width": 2,
                "corner_radius": 5
            })
            
            # Add the stimulus
            self._add_stimulus_component(components, stimulus, (stimulus_x, y))
            
            # Display correct answer
            correct_x = 300
            
            # Get the correct association
            correct_stimulus = self.correct_associations[i]
            
            # Add correct answer container
            components.append({
                "type": "rect",
                "rect": (correct_x - 30, y - 30, 60, 60),
                "color": "content_bg",
                "border_color": "success",
                "border_width": 2,
                "corner_radius": 5
            })
            
            # Add the correct stimulus
            self._add_stimulus_component(components, correct_stimulus, (correct_x, y))
            
            # Display user's answer
            user_x = 450
            
            # Get the user's answer
            user_stimulus = self.user_responses[i]
            
            # Determine if correct
            is_correct = user_stimulus == correct_stimulus
            
            # Add user answer container
            components.append({
                "type": "rect",
                "rect": (user_x - 30, y - 30, 60, 60),
                "color": "content_bg",
                "border_color": "success" if is_correct else "error",
                "border_width": 2,
                "corner_radius": 5
            })
            
            # Add the user stimulus
            self._add_stimulus_component(components, user_stimulus, (user_x, y))
            
            # Add labels
            if i == 0:
                components.append({
                    "type": "text",
                    "text": "Stimulus",
                    "position": (stimulus_x, 210),
                    "font_size": "small",
                    "color": "text_secondary",
                    "align": "center"
                })
                
                components.append({
                    "type": "text",
                    "text": "Correct",
                    "position": (correct_x, 210),
                    "font_size": "small",
                    "color": "text_secondary",
                    "align": "center"
                })
                
                components.append({
                    "type": "text",
                    "text": "Your Answer",
                    "position": (user_x, 210),
                    "font_size": "small",
                    "color": "text_secondary",
                    "align": "center"
                })
    
    def _add_stimulus_component(self, components, stimulus, position):
        """Add a component representing a stimulus to the components list.
        
        Args:
            components: List of components to add to
            stimulus: Stimulus to represent
            position: Position (x, y) to place the stimulus
        """
        if not stimulus:
            return
            
        stimulus_type = stimulus.get("type")
        value = stimulus.get("value")
        
        if stimulus_type == "color":
            # Color is represented as a colored circle
            components.append({
                "type": "circle",
                "position": position,
                "radius": 25,
                "color": value,
                "border_color": "divider",
                "border_width": 1
            })
            
        elif stimulus_type == "shape":
            # Shape is represented as a shape name (will be converted to visual by renderer)
            components.append({
                "type": "shape",
                "shape": value,
                "position": position,
                "size": 40,
                "color": "primary",
                "border_color": "divider",
                "border_width": 1
            })
            
        elif stimulus_type == "sound":
            # Sound is represented as a speaker icon with a tooltip
            components.append({
                "type": "icon",
                "icon": "speaker",
                "position": position,
                "size": 40,
                "color": "primary",
                "tooltip": value
            })
            
        elif stimulus_type == "position":
            # Position is represented as a dot on a small grid
            components.append({
                "type": "position_grid",
                "position": position,
                "size": 40,
                "value": value,
                "color": "primary",
                "background_color": "content_bg"
            })
            
        elif stimulus_type == "number":
            # Number is represented as text
            components.append({
                "type": "text",
                "text": str(value),
                "position": position,
                "font_size": "medium",
                "color": "text",
                "align": "center"
            })
            
        elif stimulus_type == "texture":
            # Texture is represented as a patterned rectangle
            components.append({
                "type": "texture",
                "texture": value,
                "rect": (position[0] - 25, position[1] - 25, 50, 50),
                "color": "primary",
                "background_color": "content_bg"
            }) 