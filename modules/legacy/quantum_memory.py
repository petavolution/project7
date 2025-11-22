#!/usr/bin/env python3
"""
Quantum Memory Training Module

This module implements an innovative cognitive training exercise that leverages
quantum-inspired mechanics to enhance working memory, cognitive flexibility,
and strategic thinking. It simulates quantum superposition and entanglement
concepts to create a unique memory challenge that adapts to the user's performance.
"""

import random
import math
import time
import logging
from typing import Dict, Any, List, Tuple, Optional
import json

# Import base module class
from .base_module import BaseModule

logger = logging.getLogger(__name__)

class QuantumMemoryModule(BaseModule):
    """Quantum Memory module for enhancing working memory and cognitive flexibility."""
    
    def __init__(self, config=None):
        """Initialize the Quantum Memory module.
        
        Args:
            config: Optional configuration dictionary
        """
        # Initialize base class
        super().__init__(config)
        
        # Set module identification
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
        self.user_selections = []
        self.start_time = None
        self.last_time = None
        self.elapsed_time = 0
        self.success_rate = 0.0
        
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
    
    def _init_game(self):
        """Initialize or reset the game state."""
        self.phase = "preparation"
        self.quantum_states = []
        self.observed_states = []
        self.user_selections = []
        
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
            "quantum_states": self._get_visible_quantum_states(),
            "user_selections": self.user_selections,
            "components": self._generate_components(),
        }
        
        return state
    
    def _get_visible_quantum_states(self):
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
                self._init_game()
    
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
        # Check if click hits any quantum state
        for state in self.quantum_states:
            pos = state["position"]
            # Use a radius check (35px is half the cell width)
            dist = math.sqrt((pos[0] - x) ** 2 + (pos[1] - y) ** 2)
            
            if dist <= 35:
                # Toggle selection
                state["selected"] = not state["selected"]
                
                # If selected, show superposition picker dialog
                if state["selected"]:
                    return {
                        "result": "show_picker",
                        "state_id": state["id"],
                        "superposition_count": len(self.quantum_states[0]["superposition"])
                    }
                else:
                    # If deselected, remove from user selections
                    if state["id"] in self.user_selections:
                        del self.user_selections[state["id"]]
                    
                    return {
                        "result": "deselected",
                        "state_id": state["id"]
                    }
        
        return {"result": "no_hit"}
    
    def _handle_action(self, action, data):
        """Handle action input.
        
        Args:
            action: Action to perform
            data: Additional data for the action
            
        Returns:
            Dictionary containing the response
        """
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
        if self.phase in ["memorize", "recall"]:
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
        
        # Add phase-specific instruction
        phase_instructions = {
            "preparation": "Prepare your quantum memory...",
            "memorize": "Memorize all quantum states and their superpositions!",
            "recall": "Select states to recall their values.",
            "feedback": f"Success Rate: {self.success_rate:.0%}"
        }
        
        components.append({
            "type": "text",
            "text": phase_instructions.get(self.phase, ""),
            "position": (400, 530),
            "font_size": "medium",
            "color": "highlight",
            "align": "center"
        })
        
        # Add additional info for feedback phase
        if self.phase == "feedback":
            next_text = "Next trial starting soon..."
            if self.level > 1 and self.trials_completed % self.config["level_up_threshold"] == 0:
                next_text = f"Level {self.level} starting soon..."
                
            components.append({
                "type": "text",
                "text": next_text,
                "position": (400, 560),
                "font_size": "small",
                "color": "text_secondary",
                "align": "center"
            })
            
        # Add submit button in recall phase
        if self.phase == "recall":
            components.append({
                "type": "button",
                "text": "Submit",
                "rect": (350, 580, 100, 40),
                "action": "submit"
            })
            
        return components 