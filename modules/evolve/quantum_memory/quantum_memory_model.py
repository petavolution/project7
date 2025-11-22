#!/usr/bin/env python3
"""
Quantum Memory Model Component

This module handles the core game logic for the Quantum Memory module:
- Quantum state generation and management
- Game state management
- Phase transitions
- Scoring and performance tracking
- Quantum collapse mechanics
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

class QuantumMemoryModel:
    """Model component for Quantum Memory module - handles core game logic."""
    
    def __init__(self, config=None):
        """Initialize the model with game state and business logic.
        
        Args:
            config: Optional configuration dictionary
        """
        # Module metadata
        self.id = "quantum_memory"
        self.name = "Quantum Memory"
        self.description = (
            "Enhance your working memory and cognitive flexibility through quantum-inspired "
            "challenges. Memorize quantum states that exist in superposition and make strategic "
            "choices to collapse them correctly. Boost your mental adaptability and processing power."
        )
        
        # Game state
        self.phase = "preparation"  # preparation, memorize, recall, feedback
        self.level = 1
        self.score = 0
        self.trials_completed = 0
        self.current_trial = 0
        self.quantum_states = []
        self.observed_states = []
        self.user_selections = {}  # Dictionary mapping state ID to selected values
        self.start_time = None
        self.last_time = None
        self.elapsed_time = 0
        self.success_rate = 0.0
        self.message = "Welcome to Quantum Memory"
        
        # Set default configuration
        self._set_default_config()
        
        # Apply custom configuration if provided
        if config:
            self.config.update(config)
            
        # Initialize game
        self.init_game()
    
    def _set_default_config(self):
        """Set default configuration values."""
        self.config = {
            # Time settings
            "preparation_time": 3,
            "memorize_time": 5,
            "recall_time": 10,
            "feedback_time": 3,
            
            # Game parameters
            "initial_quantum_states": 3,
            "max_quantum_states": 12,
            "entanglement_probability": 0.3,
            "superposition_states": 2,
            "points_per_correct": 10,
            "bonus_for_entangled": 5,
            "error_penalty": 3,
            
            # Difficulty parameters
            "level_up_threshold": 3,
            "accuracy_threshold": 0.7,
            "adaptive_difficulty": True,
        }
    
    def init_game(self):
        """Initialize or reset the game state."""
        self.phase = "preparation"
        self.quantum_states = []
        self.observed_states = []
        self.user_selections = {}
        
        # Calculate number of quantum states based on level
        num_states = min(
            self.config["initial_quantum_states"] + (self.level // 2),
            self.config["max_quantum_states"]
        )
        
        # Generate quantum states
        self._generate_quantum_states(num_states)
        
        # Set start time for preparation phase
        self.start_time = time.time()
        self.last_time = self.start_time
        self.elapsed_time = 0
        
        # Set message
        self.message = "Prepare for quantum states. Focus your mind..."
    
    def _generate_quantum_states(self, num_states):
        """Generate quantum states for the current trial.
        
        Args:
            num_states: Number of quantum states to generate
        """
        # Clear existing states
        self.quantum_states = []
        quantum_symbols = ["⟲", "⟳", "↑", "↓", "↔", "↕", "⊕", "⊗", "⊙", "△", "▽", "□", "◇", "○", "●", "★"]
        positions = []
        
        # Calculate grid dimensions - always use a square grid that can fit all states
        grid_size = math.ceil(math.sqrt(num_states))
        cell_width = 70  # Fixed cell width in pixels
        cell_height = 70  # Fixed cell height in pixels
        
        # Calculate grid starting position (centered)
        grid_width = grid_size * cell_width
        grid_height = grid_size * cell_height
        grid_start_x = 400 - (grid_width // 2)  # Assuming 800px width content area
        grid_start_y = 300 - (grid_height // 2)  # Assuming 600px height content area
        
        # Generate positions on the grid
        for row in range(grid_size):
            for col in range(grid_size):
                if len(positions) < num_states:
                    x = grid_start_x + (col * cell_width) + (cell_width // 2)
                    y = grid_start_y + (row * cell_height) + (cell_height // 2)
                    positions.append((x, y))
        
        # Shuffle positions
        random.shuffle(positions)
        
        # Generate entanglement pairs - connect some states in pairs
        entangled_pairs = []
        available_indices = list(range(num_states))
        
        # Determine how many entangled pairs to create
        num_entangled = int(num_states * self.config["entanglement_probability"])
        num_entangled = num_entangled - (num_entangled % 2)  # Ensure even number
        
        for _ in range(num_entangled // 2):
            if len(available_indices) >= 2:
                # Pick two random indices
                idx1 = random.choice(available_indices)
                available_indices.remove(idx1)
                idx2 = random.choice(available_indices)
                available_indices.remove(idx2)
                
                # Create entangled pair
                entangled_pairs.append((idx1, idx2))
        
        # Create quantum states
        for i in range(num_states):
            # Determine if this state is entangled
            entangled_with = None
            for pair in entangled_pairs:
                if i == pair[0]:
                    entangled_with = pair[1]
                    break
                elif i == pair[1]:
                    entangled_with = pair[0]
                    break
            
            # Choose symbols for superposition
            # More superposition states at higher levels
            num_superposition = min(self.level // 3 + self.config["superposition_states"], len(quantum_symbols))
            superposition = random.sample(quantum_symbols, num_superposition)
            
            # Create the quantum state
            quantum_state = {
                "id": i,
                "position": positions[i],
                "superposition": superposition,
                "entangled_with": entangled_with,
                "observed_value": None,
                "collapsed": False,
                "selected": False,
            }
            
            self.quantum_states.append(quantum_state)
    
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
            # Transition to memorize phase
            if self.elapsed_time >= self.config["preparation_time"]:
                self.phase = "memorize"
                self.elapsed_time = 0
                self.message = "Memorize the quantum states and their possible values!"
        
        elif self.phase == "memorize":
            # Transition to recall phase
            if self.elapsed_time >= self.config["memorize_time"]:
                self.phase = "recall"
                self.elapsed_time = 0
                self._collapse_quantum_states()
                self.message = "Recall the quantum states by selecting the correct values!"
        
        elif self.phase == "recall":
            # Transition to feedback phase
            if self.elapsed_time >= self.config["recall_time"] or self._all_states_selected():
                self.phase = "feedback"
                self.elapsed_time = 0
                self._calculate_score()
                
                # Generate feedback message
                if self.success_rate >= 0.9:
                    self.message = "Excellent quantum memory! Your mind is operating at peak efficiency."
                elif self.success_rate >= 0.7:
                    self.message = "Good work! Your quantum intuition is developing nicely."
                else:
                    self.message = "Keep practicing to improve your quantum memory capacity."
                
                # Update trials
                self.trials_completed += 1
                self.current_trial += 1
                
                # Check for level up
                if (self.trials_completed % self.config["level_up_threshold"] == 0 and 
                    self.success_rate >= self.config["accuracy_threshold"] and
                    self.level < 20):  # Max level cap
                    
                    self.level += 1
                    self.message = f"Quantum level up! Now at level {self.level}. Your mind is expanding!"
        
        elif self.phase == "feedback":
            # Transition to preparation for next trial
            if self.elapsed_time >= self.config["feedback_time"]:
                self.init_game()
    
    def _collapse_quantum_states(self):
        """Collapse quantum states from superposition to single observed values."""
        # Reset observed states
        self.observed_states = []
        
        # Process entangled pairs first to ensure consistent collapse
        processed_states = set()
        
        # First pass: handle entangled states
        for i, state in enumerate(self.quantum_states):
            if state["entangled_with"] is not None and i not in processed_states:
                # Get entangled pair
                entangled_state = self.quantum_states[state["entangled_with"]]
                
                # Choose the same random index for both states
                index = random.randrange(len(state["superposition"]))
                
                # Ensure index is valid for both states
                index = min(index, len(entangled_state["superposition"]) - 1)
                
                # Collapse both states to the selected values
                state["observed_value"] = state["superposition"][index]
                entangled_state["observed_value"] = entangled_state["superposition"][index]
                
                # Mark both as processed
                processed_states.add(i)
                processed_states.add(state["entangled_with"])
        
        # Second pass: handle remaining non-entangled states
        for i, state in enumerate(self.quantum_states):
            if i not in processed_states:
                # Randomly select one of the superposition states
                state["observed_value"] = random.choice(state["superposition"])
                processed_states.add(i)
    
    def _all_states_selected(self):
        """Check if all quantum states have been selected by the user.
        
        Returns:
            True if all states have selections, False otherwise
        """
        return len(self.user_selections) == len(self.quantum_states)
    
    def _calculate_score(self):
        """Calculate score based on user selections."""
        correct_count = 0
        total_count = len(self.quantum_states)
        
        for state in self.quantum_states:
            state_id = state["id"]
            
            # Check if user made a selection for this state
            if state_id in self.user_selections:
                if state["observed_value"] in self.user_selections[state_id]:
                    # Correct selection
                    correct_count += 1
                    
                    # Award points
                    points = self.config["points_per_correct"]
                    
                    # Bonus for entangled states
                    if state["entangled_with"] is not None:
                        points += self.config["bonus_for_entangled"]
                    
                    self.score += points
            else:
                # No selection, penalize
                self.score = max(0, self.score - self.config["error_penalty"])
        
        # Calculate success rate
        if total_count > 0:
            self.success_rate = correct_count / total_count
        else:
            self.success_rate = 0
    
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
        
        if action == "select_value":
            state_id = data.get("state_id")
            value_indices = data.get("value_indices", [])
            
            # Validate the state ID
            if state_id < 0 or state_id >= len(self.quantum_states):
                return {"result": "error", "reason": "invalid state ID"}
            
            # Get the state
            state = self.quantum_states[state_id]
            
            # Mark as collapsed (from user perspective)
            state["collapsed"] = True
            state["selected"] = False
            
            # Store user selection
            selected_values = []
            for idx in value_indices:
                if 0 <= idx < len(state["superposition"]):
                    selected_values.append(state["superposition"][idx])
            
            self.user_selections[state_id] = selected_values
            
            return {
                "result": "success",
                "state_id": state_id,
                "values": selected_values
            }
            
        elif action == "submit":
            # Immediately transition to feedback phase
            self.phase = "feedback"
            self.elapsed_time = self.config["recall_time"]  # Force timeout
            
            return {"result": "success", "phase": "feedback"}
        
        # Unknown action
        return {"result": "error", "reason": "unknown action"}
    
    def toggle_state_selection(self, state_id):
        """Toggle the selection state of a quantum state.
        
        Args:
            state_id: ID of the state to toggle
            
        Returns:
            Dictionary with result information
        """
        # Validate the state ID
        if state_id < 0 or state_id >= len(self.quantum_states):
            return {"result": "error", "reason": "invalid state ID"}
        
        # Get the state
        state = self.quantum_states[state_id]
        
        # Toggle selection
        state["selected"] = not state["selected"]
        
        # If selected, return info for showing picker
        if state["selected"]:
            return {
                "result": "show_picker",
                "state_id": state_id,
                "superposition_count": len(state["superposition"])
            }
        else:
            # If deselected, remove from user selections
            if state_id in self.user_selections:
                del self.user_selections[state_id]
            
            return {
                "result": "deselected",
                "state_id": state_id
            }
    
    def get_visible_quantum_states(self):
        """Get the quantum states that should be visible in the current phase.
        
        Returns:
            List of visible quantum states with appropriate information level
        """
        visible_states = []
        
        if self.phase == "preparation":
            # In preparation, just return empty boxes
            for state in self.quantum_states:
                visible_states.append({
                    "id": state["id"],
                    "position": state["position"],
                    "type": "empty",
                })
        
        elif self.phase == "memorize":
            # In memorize phase, show all states in superposition
            for state in self.quantum_states:
                visible_states.append({
                    "id": state["id"],
                    "position": state["position"],
                    "superposition": state["superposition"],
                    "entangled_with": state["entangled_with"],
                    "type": "superposition",
                })
        
        elif self.phase == "recall":
            # In recall phase, show collapsed states or selection boxes
            for state in self.quantum_states:
                if state["collapsed"]:
                    visible_states.append({
                        "id": state["id"],
                        "position": state["position"],
                        "observed_value": state["observed_value"],
                        "entangled_with": state["entangled_with"],
                        "type": "collapsed",
                    })
                else:
                    visible_states.append({
                        "id": state["id"],
                        "position": state["position"],
                        "type": "unknown",
                        "selected": state["selected"],
                    })
        
        elif self.phase == "feedback":
            # In feedback phase, show all correct states and user selections
            for state in self.quantum_states:
                visible_states.append({
                    "id": state["id"],
                    "position": state["position"],
                    "observed_value": state["observed_value"],
                    "entangled_with": state["entangled_with"],
                    "correct": state["observed_value"] in self.user_selections.get(state["id"], []),
                    "type": "feedback",
                })
        
        return visible_states
    
    def get_state(self):
        """Get the current state of the model.
        
        Returns:
            Dictionary containing the current state
        """
        return {
            "module_id": self.id,
            "module_name": self.name,
            "description": self.description,
            "phase": self.phase,
            "level": self.level,
            "score": self.score,
            "message": self.message,
            "trial": self.current_trial,
            "trials_completed": self.trials_completed,
            "success_rate": self.success_rate,
            "elapsed_time": self.elapsed_time,
            "quantum_states": self.get_visible_quantum_states(),
            "user_selections": self.user_selections,
        }
    
    def reset(self):
        """Reset the model to initial state."""
        self.level = 1
        self.score = 0
        self.trials_completed = 0
        self.current_trial = 0
        self.success_rate = 0.0
        self.init_game()
        
    def get_default_config(self):
        """Get the default configuration.
        
        Returns:
            Dictionary with default configuration
        """
        return self.config.copy() 