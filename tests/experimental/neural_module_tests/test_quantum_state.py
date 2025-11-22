#!/usr/bin/env python3
"""
Test Quantum State Management

This module tests the functionality of the quantum state management system.
"""

import unittest
import sys
from pathlib import Path
import json
import time

# Add the parent directory to sys.path if needed
parent_dir = str(Path(__file__).parent.parent.parent)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from MetaMindIQTrain.core.quantum_state import (
    StateVector, QuantumStateManager, global_state_manager
)


class TestStateVector(unittest.TestCase):
    """Test the StateVector functionality."""
    
    def setUp(self):
        """Set up test fixture."""
        self.initial_data = {"key1": "value1", "key2": {"nested": 42}}
        self.state = StateVector(data=self.initial_data)
        
    def test_creation_and_properties(self):
        """Test creation and basic properties of a StateVector."""
        self.assertEqual(self.state.data, self.initial_data)
        self.assertEqual(self.state.amplitude, 1.0)
        self.assertEqual(self.state.probability, 1.0)
        self.assertFalse(self.state.collapsed)
        self.assertTrue(hasattr(self.state, 'state_id'))
        self.assertTrue(hasattr(self.state, 'timestamp'))
    
    def test_update(self):
        """Test updating a state with a delta."""
        delta = {"key1": "new_value", "key3": "added_value"}
        updated_state = self.state.update(delta)
        
        # Check that original state is unchanged
        self.assertEqual(self.state.data["key1"], "value1")
        self.assertNotIn("key3", self.state.data)
        
        # Check that updated state has the changes
        self.assertEqual(updated_state.data["key1"], "new_value")
        self.assertEqual(updated_state.data["key3"], "added_value")
        self.assertEqual(updated_state.data["key2"], self.state.data["key2"])
        
    def test_merge(self):
        """Test merging two states."""
        other_data = {"key1": "other_value", "key4": "other_added"}
        other_state = StateVector(data=other_data, amplitude=0.8, probability=0.9)
        
        merged_state = self.state.merge(other_state)
        
        # Check that original states are unchanged
        self.assertEqual(self.state.data["key1"], "value1")
        self.assertEqual(other_state.data["key1"], "other_value")
        
        # Check that merged state combines both states
        self.assertEqual(merged_state.data["key1"], "other_value")  # Other state's value wins
        self.assertEqual(merged_state.data["key2"], self.state.data["key2"])
        self.assertEqual(merged_state.data["key4"], "other_added")
        
        # Check that probability and amplitude are combined
        self.assertEqual(merged_state.amplitude, self.state.amplitude * other_state.amplitude)
        self.assertEqual(merged_state.probability, self.state.probability * other_state.probability)
        
    def test_entangle(self):
        """Test entangling two states."""
        other_state = StateVector(data={"other": "data"})
        
        self.state.entangle(other_state)
        
        # Check that states are now entangled
        self.assertIn(other_state, self.state.entangled)
        self.assertIn(self.state, other_state.entangled)
        
    def test_observe(self):
        """Test observing a state."""
        # Define an observable function
        def compute_sum(data):
            return data["key2"]["nested"] + 10
            
        self.state.add_observable("sum", compute_sum)
        
        # Observe the whole state
        full_state = self.state.observe()
        self.assertEqual(full_state, self.state.data)
        self.assertTrue(self.state.collapsed)
        
        # Observe a specific key
        key_value = self.state.observe("key1")
        self.assertEqual(key_value, "value1")
        
        # Observe a computed observable
        computed_value = self.state.observe("sum")
        self.assertEqual(computed_value, 52)  # 42 + 10
        
    def test_to_dict_from_dict(self):
        """Test serialization and deserialization."""
        state_dict = self.state.to_dict()
        
        # Check that dictionary has expected fields
        self.assertIn("state_id", state_dict)
        self.assertIn("timestamp", state_dict)
        self.assertIn("collapsed", state_dict)
        self.assertIn("data", state_dict)
        
        # Recreate from dictionary
        recreated_state = StateVector.from_dict(state_dict)
        
        # Check that data is preserved
        self.assertEqual(recreated_state.data, self.state.data)
        self.assertEqual(recreated_state.state_id, self.state.state_id)


class TestQuantumStateManager(unittest.TestCase):
    """Test the QuantumStateManager functionality."""
    
    def setUp(self):
        """Set up test fixture."""
        self.manager = QuantumStateManager()
        
    def test_create_get_state(self):
        """Test creating and retrieving states."""
        initial_data = {"test": "data"}
        state = self.manager.create_state(initial_data)
        
        # Check that state is created with correct data
        self.assertEqual(state.data, initial_data)
        
        # Check that current state is set
        self.assertEqual(self.manager.current_state_id, state.state_id)
        
        # Get state by ID
        retrieved_state = self.manager.get_state(state.state_id)
        self.assertEqual(retrieved_state.data, initial_data)
        
        # Get current state
        current_state = self.manager.get_state()
        self.assertEqual(current_state.data, initial_data)
        
    def test_update_state(self):
        """Test updating a state."""
        initial_state = self.manager.create_state({"key": "value"})
        
        # Update state
        delta = {"key": "new_value", "added": 42}
        updated_state = self.manager.update_state(initial_state.state_id, delta)
        
        # Check that update worked
        self.assertEqual(updated_state.data["key"], "new_value")
        self.assertEqual(updated_state.data["added"], 42)
        
        # Check that current state is updated
        self.assertEqual(self.manager.current_state_id, updated_state.state_id)
        
        # Check history
        self.assertEqual(len(self.manager.history), 2)
        self.assertEqual(self.manager.history[0], initial_state)
        self.assertEqual(self.manager.history[1], updated_state)
        
    def test_compute_delta(self):
        """Test computing delta between states."""
        state1 = self.manager.create_state({"a": 1, "b": 2, "c": {"nested": 3}})
        state2 = self.manager.create_state({"a": 1, "b": 4, "c": {"nested": 5, "new": 6}, "d": 7})
        
        delta = self.manager.compute_delta(state1.state_id, state2.state_id)
        
        # Check that delta contains changed/added values
        self.assertNotIn("a", delta)  # Unchanged
        self.assertEqual(delta["b"], 4)  # Changed
        self.assertIn("c", delta)  # Nested changes
        self.assertEqual(delta["c"]["nested"], 5)  # Changed nested
        self.assertEqual(delta["c"]["new"], 6)  # Added nested
        self.assertEqual(delta["d"], 7)  # Added
        
    def test_entangle_states(self):
        """Test entangling states."""
        state1 = self.manager.create_state({"a": 1})
        state2 = self.manager.create_state({"b": 2})
        
        self.manager.entangle_states(state1.state_id, state2.state_id)
        
        # Get the updated states after entanglement
        updated_state1 = self.manager.get_state(state1.state_id)
        updated_state2 = self.manager.get_state(state2.state_id)
        
        # Check that states are entangled
        self.assertTrue(any(e.state_id == state2.state_id for e in updated_state1.entangled))
        self.assertTrue(any(e.state_id == state1.state_id for e in updated_state2.entangled))


if __name__ == '__main__':
    unittest.main() 