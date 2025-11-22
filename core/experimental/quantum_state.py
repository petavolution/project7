#!/usr/bin/env python3
"""
Quantum State Management System for MetaMindIQTrain.

This module implements a quantum-inspired state management system
that provides entangled states, superposition, and probabilistic features
for highly efficient state synchronization between server and clients.
"""

import json
import hashlib
import time
import logging
import random
from typing import Dict, Any, List, Tuple, Optional, Union, Callable
from dataclasses import dataclass, field, asdict

logger = logging.getLogger(__name__)

@dataclass
class StateVector:
    """Represents a quantum-like state vector."""
    
    # State identification
    state_id: str = field(default_factory=lambda: f"state_{int(time.time() * 1000)}")
    timestamp: float = field(default_factory=time.time)
    
    # Quantum properties
    amplitude: float = 1.0
    probability: float = 1.0
    collapsed: bool = False
    
    # Actual data stored in the state
    data: Dict[str, Any] = field(default_factory=dict)
    
    # Entangled states (references to other state vectors that affect this one)
    entangled: List["StateVector"] = field(default_factory=list)
    
    # Observable functions that compute derived values when state is observed
    observables: Dict[str, Callable] = field(default_factory=dict)
    
    def __post_init__(self):
        """Initialize state hash."""
        self._hash = self._compute_hash()
    
    def __eq__(self, other):
        """Compare two state vectors for equality."""
        if not isinstance(other, StateVector):
            return False
        return self.state_id == other.state_id
    
    def __hash__(self):
        """Hash function for state vectors."""
        return hash(self.state_id)
    
    def _compute_hash(self) -> str:
        """Compute a hash of the state data."""
        serialized = json.dumps(self.data, sort_keys=True)
        return hashlib.sha256(serialized.encode()).hexdigest()
    
    def update(self, delta: Dict[str, Any]) -> "StateVector":
        """Update the state with a delta.
        
        Args:
            delta: Dictionary of changes to apply to the state
            
        Returns:
            New state vector with applied changes
        """
        # Create a copy of the current data
        new_data = {**self.data}
        
        # Apply the delta
        for key, value in delta.items():
            if isinstance(value, dict) and key in new_data and isinstance(new_data[key], dict):
                # Deep merge dictionaries
                new_data[key] = {**new_data[key], **value}
            else:
                # Direct assignment
                new_data[key] = value
        
        # Create a new state vector
        new_state = StateVector(
            state_id=f"{self.state_id}_updated_{int(time.time() * 1000)}",
            timestamp=time.time(),
            amplitude=self.amplitude,
            probability=self.probability,
            collapsed=False,
            data=new_data,
            entangled=self.entangled.copy(),
            observables=self.observables.copy()
        )
        
        # Update entangled states
        for entangled_state in new_state.entangled:
            entangled_state.notify_entangled(new_state)
        
        return new_state
    
    def merge(self, other_state: "StateVector") -> "StateVector":
        """Merge this state with another state.
        
        Args:
            other_state: Another state vector to merge with
            
        Returns:
            New merged state vector
        """
        # Create merged data
        merged_data = {**self.data}
        
        # Apply other state's data
        for key, value in other_state.data.items():
            if isinstance(value, dict) and key in merged_data and isinstance(merged_data[key], dict):
                # Deep merge dictionaries
                merged_data[key] = {**merged_data[key], **value}
            else:
                # Direct assignment
                merged_data[key] = value
        
        # Create a new state vector with merged data
        merged_state = StateVector(
            state_id=f"merged_{self.state_id}_{other_state.state_id}",
            timestamp=time.time(),
            amplitude=self.amplitude * other_state.amplitude,  # Combine amplitudes
            probability=self.probability * other_state.probability,  # Combine probabilities
            collapsed=False,
            data=merged_data,
            # Combine unique entangled states
            entangled=list(set(self.entangled + other_state.entangled)),
            # Combine observables
            observables={**self.observables, **other_state.observables}
        )
        
        return merged_state
    
    def entangle(self, other_state: "StateVector") -> None:
        """Entangle this state with another state.
        
        Args:
            other_state: Another state vector to entangle with
        """
        if other_state not in self.entangled:
            self.entangled.append(other_state)
        
        if self not in other_state.entangled:
            other_state.entangled.append(self)
    
    def notify_entangled(self, updated_state: "StateVector") -> None:
        """Notify this state that an entangled state has changed.
        
        Args:
            updated_state: The state that was updated
        """
        # In a real quantum system, this would trigger a collapse or update
        # of this state based on the entangled state's change
        self.probability *= updated_state.probability
        self.amplitude *= updated_state.amplitude
    
    def observe(self, key: Optional[str] = None) -> Any:
        """Observe the state, potentially collapsing superpositions.
        
        Args:
            key: Optional key to observe only a part of the state
            
        Returns:
            Observed value (or entire state if key is None)
        """
        # Mark state as collapsed (observed)
        self.collapsed = True
        
        # If key is specified and is an observable, compute it
        if key is not None and key in self.observables:
            return self.observables[key](self.data)
        
        # Otherwise return the raw data (or part of it)
        if key is not None:
            return self.data.get(key)
        
        return self.data
    
    def add_observable(self, key: str, func: Callable) -> None:
        """Add an observable function that computes a derived value.
        
        Args:
            key: Key for the observable
            func: Function that computes the observable value from state data
        """
        self.observables[key] = func
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert state vector to a dictionary.
        
        Returns:
            Dictionary representation of the state vector
        """
        return {
            'state_id': self.state_id,
            'timestamp': self.timestamp,
            'collapsed': self.collapsed,
            'data': self.data,
            # Exclude entangled states and observables from serialization
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "StateVector":
        """Create a state vector from a dictionary.
        
        Args:
            data: Dictionary representation of a state vector
            
        Returns:
            State vector instance
        """
        state_data = data.pop('data', {})
        return cls(data=state_data, **data)
    
    def compute_delta(self, other_state: "StateVector") -> Dict[str, Any]:
        """Compute a delta between this state and another state.
        
        Args:
            other_state: The state to compare with
            
        Returns:
            Dictionary containing only the changed values
        """
        delta = {}
        
        # Compare top-level keys
        for key, value in other_state.data.items():
            if key not in self.data:
                # New key
                delta[key] = value
            elif isinstance(value, dict) and isinstance(self.data[key], dict):
                # Compare nested dictionaries
                nested_delta = {}
                for nested_key, nested_value in value.items():
                    if nested_key not in self.data[key] or self.data[key][nested_key] != nested_value:
                        nested_delta[nested_key] = nested_value
                
                if nested_delta:
                    delta[key] = nested_delta
            elif self.data[key] != value:
                # Changed value
                delta[key] = value
        
        return delta


class QuantumStateManager:
    """Manages quantum-inspired state vectors for efficient synchronization."""
    
    def __init__(self):
        """Initialize the state manager."""
        self.states: Dict[str, StateVector] = {}
        self.history: List[StateVector] = []
        self.current_state_id: Optional[str] = None
        
    def create_state(self, initial_data: Optional[Dict[str, Any]] = None) -> StateVector:
        """Create a new state.
        
        Args:
            initial_data: Initial data for the state
            
        Returns:
            New state vector
        """
        # Initialize data if None
        if initial_data is None:
            initial_data = {}
            
        # Generate a unique state ID
        state_id = f"state_{int(time.time() * 1000000)}_{random.randint(1000, 9999)}"
        
        # Create the state
        state = StateVector(
            state_id=state_id,
            timestamp=time.time(),
            data=initial_data
        )
        
        # Store the state
        self.states[state.state_id] = state
        
        # Set as current state if this is the first state
        if self.current_state_id is None:
            self.current_state_id = state.state_id
            
        # Add to history
        self.history.append(state)
        
        return state
    
    def update_state(self, state_id: str, delta: Dict[str, Any]) -> StateVector:
        """Update a state with a delta.
        
        Args:
            state_id: ID of the state to update
            delta: Delta to apply
            
        Returns:
            Updated state vector
        """
        # Get the state
        state = self.get_state(state_id)
        
        # Update the state
        updated_state = state.update(delta)
        
        # Store the updated state
        self.states[updated_state.state_id] = updated_state
        self.history.append(updated_state)
        self.current_state_id = updated_state.state_id
        
        return updated_state
    
    def get_state(self, state_id: Optional[str] = None) -> Optional[StateVector]:
        """Retrieve a state by ID or the current state if no ID is provided.
        
        Args:
            state_id: Optional ID of the state to retrieve
            
        Returns:
            State vector with the given ID or current state
        """
        if state_id is None:
            # Return current state
            return self.states.get(self.current_state_id)
            
        # Return the specific state requested
        return self.states.get(state_id)
    
    def compute_delta(self, old_state_id: str, new_state_id: str) -> Dict[str, Any]:
        """Compute the delta between two states.
        
        Args:
            old_state_id: ID of the old state
            new_state_id: ID of the new state
            
        Returns:
            Dictionary containing only the changed values
        """
        old_state = self.get_state(old_state_id)
        new_state = self.get_state(new_state_id)
        
        if not old_state or not new_state:
            return {}
            
        delta = {}
        
        # Find all changed or added keys
        for key, new_value in new_state.data.items():
            if key not in old_state.data:
                # Added key
                delta[key] = new_value
            elif isinstance(new_value, dict) and isinstance(old_state.data[key], dict):
                # Handle nested dictionaries
                nested_delta = {}
                for nested_key, nested_value in new_value.items():
                    if nested_key not in old_state.data[key] or old_state.data[key][nested_key] != nested_value:
                        nested_delta[nested_key] = nested_value
                if nested_delta:
                    delta[key] = nested_delta
            elif old_state.data[key] != new_value:
                # Changed value
                delta[key] = new_value
                
        return delta
    
    def entangle_states(self, state_id1: str, state_id2: str) -> None:
        """Entangle two states, allowing them to influence each other.
        
        Args:
            state_id1: ID of first state to entangle
            state_id2: ID of second state to entangle
        """
        state1 = self.get_state(state_id1)
        state2 = self.get_state(state_id2)
        
        if state1 and state2:
            # Use the StateVector's entangle method
            state1.entangle(state2)


# Global state manager instance
global_state_manager = QuantumStateManager() 