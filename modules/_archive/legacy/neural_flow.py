#!/usr/bin/env python3
"""
Neural Flow brain training module.

This module implements a cognitive training exercise that enhances neural 
pathway development, cognitive flexibility, and visual-spatial processing.
It visualizes a neural network with pulsing nodes and paths that the user
must follow and interact with based on specific patterns.
"""

import random
import math
import time
import logging
from typing import Dict, Any, List

# Import base module class
from .base_module import BaseModule

logger = logging.getLogger(__name__)

class NeuralFlowModule(BaseModule):
    """Neural Flow module for enhancing cognitive pathways and processing."""
    
    def __init__(self, config=None):
        """Initialize the Neural Flow module.
        
        Args:
            config: Optional configuration dictionary
        """
        # Initialize base class
        super().__init__(config)
        
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
        self.phase = "preparation"  # preparation, active, feedback
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
        self.phase = "preparation"
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
    
    def get_state(self) -> Dict[str, Any]:
        """Get the current state of the module.
        
        Returns:
            Dictionary containing the current state
        """
        # Calculate elapsed time
        current_time = time.time()
        if self.start_time:
            elapsed = current_time - self.start_time
        else:
            elapsed = 0
        
        # Update session time
        self.session_time += elapsed
        self.start_time = current_time
        
        # Check for phase transitions
        self._check_phase_transitions(elapsed)
        
        # Update timeouts for active nodes
        self._update_active_nodes(elapsed)
        
        # Build and return state
        state = {
            "module_id": self.id,
            "module_name": self.name,
            "phase": self.phase,
            "level": self.level,
            "score": self.score,
            "message": self.message,
            "target_nodes": self.target_nodes,
            "active_nodes": self.active_nodes,
            "success_nodes": self.success_nodes,
            "error_nodes": self.error_nodes,
            "regenerate_paths": False,  # Only true when paths should be regenerated
            "delta_time": int(elapsed * 1000),  # Convert to milliseconds
            "nodes_remaining": len(self.target_nodes) - self.targets_found,
            "accuracy": self.accuracy,
            "components": self._generate_components(),
        }
        
        # Return the state
        return state
    
    def _check_phase_transitions(self, elapsed):
        """Check and handle phase transitions.
        
        Args:
            elapsed: Time elapsed since last update
        """
        if self.phase == "preparation":
            # Check if preparation time has expired
            if self.session_time >= self.config["preparation_time"]:
                # Transition to active phase
                self.phase = "active"
                self.message = "Activate the highlighted nodes in sequence!"
                
                # Activate first target
                if self.target_nodes:
                    self._activate_next_target()
        
        elif self.phase == "active":
            # Check if all targets found or time expired
            if (self.targets_found >= len(self.target_nodes) or 
                self.session_time >= self.config["trial_time"]):
                
                # Transition to feedback phase
                self.phase = "feedback"
                
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
        
        elif self.phase == "feedback":
            # Check if feedback time has expired
            if self.session_time >= self.config["feedback_time"]:
                # Reset for next trial
                self._init_game()
    
    def _update_active_nodes(self, elapsed):
        """Update timeouts for active nodes.
        
        Args:
            elapsed: Time elapsed since last update
        """
        # Only update in active phase
        if self.phase != "active":
            return
            
        # Check for timeouts in active nodes
        for i in range(len(self.active_nodes) - 1, -1, -1):
            node = self.active_nodes[i]
            
            # Update elapsed time
            if node["activation_time"] is not None:
                node_elapsed = time.time() - node["activation_time"]
                
                # Check if timed out
                if node_elapsed > node["timeout"]:
                    # Move to error nodes
                    self.error_nodes.append(node)
                    self.active_nodes.pop(i)
                    
                    # Penalize score
                    self.score = max(0, self.score - self.config["error_penalty"])
                    
                    # Increment error count
                    self.error_count += 1
                    
                    # Provide feedback
                    self.message = "Too slow! Try to respond faster."
                    
                    # Activate next target if available
                    if self.targets_found < len(self.target_nodes):
                        self._activate_next_target()
    
    def _activate_next_target(self):
        """Activate the next target node."""
        # Determine which target to activate next
        if self.targets_found < len(self.target_nodes):
            target = self.target_nodes[self.targets_found]
            
            # Set activation time
            target["activation_time"] = time.time()
            
            # Move to active nodes
            self.active_nodes.append(target)
    
    def handle_input(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle user input.
        
        Args:
            input_data: Dictionary containing input data
            
        Returns:
            Dictionary containing the response
        """
        # Only process inputs in active phase
        if self.phase != "active":
            return {"result": "ignored", "reason": "not in active phase"}
        
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
    
    def _handle_action(self, action, data):
        """Handle action input.
        
        Args:
            action: Action to perform
            data: Additional data for the action
            
        Returns:
            Dictionary containing the response
        """
        if action == "activate_node":
            node_id = data.get("node_id")
            
            # Find the node in target nodes
            for i, node in enumerate(self.target_nodes):
                if node.get("id") == node_id and i == self.targets_found:
                    # Calculate response time
                    if node.get("activation_time") is not None:
                        response_time = time.time() - node["activation_time"]
                        self.response_times.append(response_time)
                    
                    # Move to success nodes
                    self.success_nodes.append(node)
                    
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
                    
                    return {"result": "success", "node_id": node_id}
        
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
        
        # Add status info
        status_text = f"Score: {self.score} | Level: {self.level}"
        if self.phase == "active":
            status_text += f" | Nodes: {self.targets_found}/{len(self.target_nodes)}"
        
        components.append({
            "type": "text",
            "text": status_text,
            "position": (400, 580),
            "font_size": "medium",
            "color": "text",
            "align": "center"
        })
        
        # In feedback phase, add performance metrics
        if self.phase == "feedback":
            # Calculate average response time
            avg_time = sum(self.response_times) / len(self.response_times) if self.response_times else 0
            
            components.append({
                "type": "text",
                "text": f"Accuracy: {self.accuracy:.0%} | Avg Response: {avg_time:.2f}s",
                "position": (400, 150),
                "font_size": "medium",
                "color": "text",
                "align": "center"
            })
            
            components.append({
                "type": "text",
                "text": "Next trial starting soon...",
                "position": (400, 180),
                "font_size": "small",
                "color": "text_secondary",
                "align": "center"
            })
        
        return components 