#!/usr/bin/env python3
"""
Neural Flow Model Component

This module handles the core game logic for the Neural Flow training module:
- Neural network state management
- Node generation and activation
- Phase transitions
- Score calculation
- Difficulty progression

The model is responsible for all data and business logic, independent of the UI.
"""

import random
import math
import time
import logging
from typing import Dict, Any, List, Tuple, Optional

# Add the parent directory to sys.path for absolute imports when imported directly
if __name__ == "__main__" or not __package__:
    project_root = Path(__file__).parent.parent.parent.parent
    sys.path.insert(0, str(project_root))

logger = logging.getLogger(__name__)

class NeuralFlowModel:
    """Model component for NeuralFlow module - handles core game logic."""
    
    # Game phases
    PHASE_PREPARATION = "preparation"
    PHASE_ACTIVE = "active"
    PHASE_FEEDBACK = "feedback"
    
    def __init__(self, config=None):
        """Initialize the model with game state and business logic.
        
        Args:
            config: Optional configuration dictionary
        """
        # Set module identification
        self.id = "neural_flow"
        self.name = "Neural Flow"
        self.description = (
            "Enhance your cognitive processing speed, neural pathway formation, "
            "and visual-spatial processing. Follow and interact with the dynamic "
            "neural pathways to improve cognitive flexibility and focus."
        )
        
        # Training difficulty levels
        self.max_level = 20
        self.level = 1
        
        # Game state
        self.phase = self.PHASE_PREPARATION
        self.score = 0
        self.start_time = None
        self.session_time = 0
        self.time_limit = 60  # seconds
        self.targets_found = 0
        self.trials_completed = 0
        
        # Neural network elements
        self.target_nodes = []
        self.active_nodes = []
        self.success_nodes = []
        self.error_nodes = []
        self.node_count = 0
        
        # Performance metrics
        self.response_times = []
        self.accuracy = 0
        self.error_count = 0
        
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
            # Time limits (in seconds)
            "preparation_time": 5,
            "trial_time": 60,
            "feedback_time": 3,
            
            # Gameplay parameters
            "min_nodes": 10,
            "max_nodes": 50,
            "initial_target_count": 3,
            "max_target_count": 10,
            "points_per_target": 10,
            "error_penalty": 5,
            
            # Difficulty parameters
            "target_timeout": 5,  # seconds
            "level_up_threshold": 3,  # trials to complete before level up
            "accuracy_threshold": 0.7,  # minimum accuracy to advance
        }
    
    def _init_game(self):
        """Initialize or reset the game state."""
        self.phase = self.PHASE_PREPARATION
        self.targets_found = 0
        self.active_nodes = []
        self.success_nodes = []
        self.error_nodes = []
        self.node_count = 0
        
        # Generate an appropriate number of target nodes based on level
        target_count = min(
            self.config["initial_target_count"] + (self.level // 2),
            self.config["max_target_count"]
        )
        
        # Clear targets
        self.target_nodes = []
        
        # Generate targets
        content_width = 800
        content_height = 600
        center_x = content_width // 2
        center_y = content_height // 2
        
        for i in range(target_count):
            # Create nodes with increasing distance from center as index increases
            angle = (i / target_count) * 2 * math.pi
            distance_factor = 0.3 + (i / target_count) * 0.5
            
            x = center_x + math.cos(angle) * (content_width * distance_factor)
            y = center_y + math.sin(angle) * (content_height * distance_factor)
            
            self.target_nodes.append({
                "id": self.node_count,
                "position": (int(x), int(y)),
                "radius": 12,
                "activation_time": None,
                "timeout": self.config["target_timeout"] * (1 - (self.level / (self.max_level * 2)))
            })
            
            self.node_count += 1
        
        # Set start time for preparation phase
        self.start_time = time.time()
        self.session_time = 0
        
        # Reset performance metrics for this level
        self.response_times = []
        self.accuracy = 0
        self.error_count = 0
        
        # Generate initial message
        self.message = "Prepare to follow the neural pathways. Starting soon..."
    
    def _activate_next_target(self):
        """Activate the next target node in sequence."""
        if self.targets_found < len(self.target_nodes):
            next_target = self.target_nodes[self.targets_found]
            next_target["activation_time"] = time.time()
            self.active_nodes.append(next_target)
            self.message = f"Activate the highlighted node! ({self.targets_found + 1}/{len(self.target_nodes)})"
    
    def update(self, dt):
        """Update the game state.
        
        Args:
            dt: Time delta since last update
        """
        # Update session time
        self.session_time = time.time() - self.start_time
        
        # Check for phase transitions
        self._check_phase_transitions(dt)
        
        # Update active nodes
        for node in self.active_nodes:
            if node["activation_time"] is not None:
                elapsed = time.time() - node["activation_time"]
                if elapsed >= node["timeout"]:
                    # Node timed out
                    self.error_nodes.append(node)
                    self.active_nodes.remove(node)
                    self.error_count += 1
                    self.score = max(0, self.score - self.config["error_penalty"])
                    self.message = "Node timed out! Focus on the active nodes."
    
    def _check_phase_transitions(self, dt):
        """Check and handle phase transitions.
        
        Args:
            dt: Time delta since last update
        """
        if self.phase == self.PHASE_PREPARATION:
            # Check if preparation time has expired
            if self.session_time >= self.config["preparation_time"]:
                # Transition to active phase
                self.phase = self.PHASE_ACTIVE
                self.message = "Activate the highlighted nodes in sequence!"
                
                # Activate first target
                if self.target_nodes:
                    self._activate_next_target()
        
        elif self.phase == self.PHASE_ACTIVE:
            # Check if all targets found or time expired
            if (self.targets_found >= len(self.target_nodes) or 
                self.session_time >= self.config["trial_time"]):
                
                # Transition to feedback phase
                self.phase = self.PHASE_FEEDBACK
                
                # Calculate accuracy
                if self.targets_found > 0:
                    self.accuracy = self.targets_found / (self.targets_found + self.error_count)
                else:
                    self.accuracy = 0
                
                # Generate feedback message
                if self.accuracy >= 0.9:
                    self.message = "Excellent work! Your neural pathways are strengthening."
                elif self.accuracy >= 0.7:
                    self.message = "Good job! Keep practicing to enhance your neural flow."
                else:
                    self.message = "Practice more to build stronger neural connections."
                
                # Increment trials completed
                self.trials_completed += 1
                
                # Check for level up
                if (self.trials_completed >= self.config["level_up_threshold"] and 
                    self.accuracy >= self.config["accuracy_threshold"] and
                    self.level < self.max_level):
                    
                    self.level += 1
                    self.trials_completed = 0
                    self.message = f"Level up! Now at level {self.level}. Neural connections intensifying!"
        
        elif self.phase == self.PHASE_FEEDBACK:
            # Check if feedback time has expired
            if self.session_time >= self.config["feedback_time"]:
                # Reset for next trial
                self._init_game()
    
    def process_click(self, x, y):
        """Process a mouse click.
        
        Args:
            x: X coordinate of click
            y: Y coordinate of click
            
        Returns:
            Dictionary containing the response
        """
        # Check if click hits any active node
        for i, node in enumerate(self.active_nodes):
            pos = node.get("position", (0, 0))
            radius = node.get("radius", 10)
            
            # Calculate distance from click to node center
            dist = math.sqrt((pos[0] - x) ** 2 + (pos[1] - y) ** 2)
            
            # Check if within radius
            if dist <= radius:
                # Calculate response time
                if node["activation_time"] is not None:
                    response_time = time.time() - node["activation_time"]
                    self.response_times.append(response_time)
                
                # Move to success nodes
                self.success_nodes.append(node)
                self.active_nodes.pop(i)
                
                # Increment score and targets found
                self.score += self.config["points_per_target"]
                self.targets_found += 1
                
                # Provide feedback
                self.message = "Great! Neural connection strengthened."
                
                # Activate next target if available
                if self.targets_found < len(self.target_nodes):
                    self._activate_next_target()
                else:
                    self.message = "All targets complete! Neural pathways optimized."
                
                return {"result": "success", "node_id": node.get("id")}
        
        # No hit, penalize
        self.score = max(0, self.score - self.config["error_penalty"])
        self.error_count += 1
        self.message = "Missed! Focus on the active nodes."
        
        return {"result": "error", "reason": "no hit"}
    
    def get_state(self):
        """Get the current model state.
        
        Returns:
            Dictionary with current game state
        """
        return {
            "phase": self.phase,
            "level": self.level,
            "score": self.score,
            "targets_found": self.targets_found,
            "total_targets": len(self.target_nodes),
            "target_nodes": self.target_nodes,
            "active_nodes": self.active_nodes,
            "success_nodes": self.success_nodes,
            "error_nodes": self.error_nodes,
            "message": self.message,
            "session_time": self.session_time,
            "accuracy": self.accuracy,
            "error_count": self.error_count,
            "trials_completed": self.trials_completed,
            "response_times": self.response_times
        } 