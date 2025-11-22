#!/usr/bin/env python3
"""
Unit Tests for Unified Component System

This script tests the key features of the unified component system:
1. Component creation and properties
2. Component hierarchy and child management
3. Component dirtying and cache invalidation
4. UI layout calculation
5. Delta calculation for state updates
"""

import os
import sys
import unittest
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.absolute()
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from MetaMindIQTrain.core.unified_component_system import (
        Component, ComponentFactory, UI, DeltaCalculator,
        get_stats, reset_stats
    )
except ImportError:
    print("Failed to import unified component system")
    sys.exit(1)

class TestComponent(unittest.TestCase):
    """Test cases for Component class."""
    
    def setUp(self):
        """Set up test case."""
        reset_stats()
    
    def test_component_creation(self):
        """Test component creation and basic properties."""
        # Create a simple component
        component = Component("test", x=10, y=20, width=100, height=50)
        
        # Check basic properties
        self.assertEqual(component.type, "test")
        self.assertEqual(component.layout["x"], 10)
        self.assertEqual(component.layout["y"], 20)
        self.assertEqual(component.layout["width"], 100)
        self.assertEqual(component.layout["height"], 50)
        self.assertEqual(len(component.children), 0)
        self.assertTrue(component.dirty)  # Component should start dirty
    
    def test_component_props(self):
        """Test component property setting and retrieval."""
        # Create a component with properties
        component = Component(
            "button", 
            x=10, y=20, 
            text="Click me", 
            enabled=True,
            color=(255, 255, 255)
        )
        
        # Check properties
        self.assertEqual(component.props.get("text"), "Click me")
        self.assertEqual(component.props.get("enabled"), True)
        self.assertEqual(component.style.get("color"), (255, 255, 255))
        
        # Test property modification
        component.set_props(text="New text")
        self.assertEqual(component.props.get("text"), "New text")
        self.assertTrue(component.dirty)  # Should be dirty after prop change
        
        # Test style modification
        component.mark_clean()
        component.set_style(color=(100, 100, 100))
        self.assertEqual(component.style.get("color"), (100, 100, 100))
        self.assertTrue(component.dirty)  # Should be dirty after style change
    
    def test_component_hierarchy(self):
        """Test component parent-child relationships."""
        parent = Component("parent", width=200, height=200)
        child1 = Component("child", width=50, height=50)
        child2 = Component("child", width=50, height=50)
        
        # Add children
        parent.add_child(child1)
        parent.add_child(child2)
        
        # Check parent-child relationships
        self.assertEqual(len(parent.children), 2)
        self.assertEqual(child1.parent, parent)
        self.assertEqual(child2.parent, parent)
        
        # Remove a child
        parent.remove_child(child1)
        self.assertEqual(len(parent.children), 1)
        self.assertIsNone(child1.parent)
        self.assertEqual(child2.parent, parent)
    
    def test_component_dirty_propagation(self):
        """Test dirty flag propagation through component hierarchy."""
        parent = Component("parent")
        child = Component("child")
        grandchild = Component("grandchild")
        
        # Build hierarchy
        parent.add_child(child)
        child.add_child(grandchild)
        
        # Mark all clean
        parent.mark_clean()
        child.mark_clean()
        grandchild.mark_clean()
        
        # Modify grandchild and check propagation
        grandchild.set_props(value=42)
        self.assertTrue(grandchild.dirty)
        self.assertTrue(child.dirty)
        self.assertTrue(parent.dirty)
        
        # Mark all clean again
        parent.mark_clean()
        child.mark_clean()
        grandchild.mark_clean()
        
        # Mark parent dirty - shouldn't affect children
        parent.mark_dirty()
        self.assertTrue(parent.dirty)
        self.assertFalse(child.dirty)
        self.assertFalse(grandchild.dirty)
    
    def test_component_needs_render(self):
        """Test needs_render method."""
        parent = Component("parent")
        child = Component("child")
        
        # Build hierarchy
        parent.add_child(child)
        
        # Parent should need render initially
        self.assertTrue(parent.needs_render())
        
        # Mark all clean
        parent.mark_clean()
        child.mark_clean()
        
        # Nothing should need render now
        self.assertFalse(parent.needs_render())
        
        # Mark child dirty
        child.mark_dirty()
        
        # Parent should need render since child is dirty
        self.assertTrue(parent.needs_render())
    
    def test_component_hash(self):
        """Test component hash calculation for rendering cache."""
        # Create two identical components
        c1 = Component("rect", x=10, y=10, width=100, height=50, backgroundColor=(255, 0, 0))
        c2 = Component("rect", x=10, y=10, width=100, height=50, backgroundColor=(255, 0, 0))
        
        # Create a component with different properties
        c3 = Component("rect", x=10, y=10, width=100, height=50, backgroundColor=(0, 255, 0))
        
        # Check hashes
        self.assertNotEqual(c1.id, c2.id)  # IDs should be different
        hash1 = c1.hash_for_rendering()
        hash2 = c2.hash_for_rendering()
        hash3 = c3.hash_for_rendering()
        
        # Different components with same properties should have same hash
        self.assertNotEqual(hash1, hash2)  # Different IDs lead to different hashes
        
        # Change properties and check hash changes
        c1.set_props(backgroundColor=(0, 0, 255))
        new_hash1 = c1.hash_for_rendering()
        self.assertNotEqual(hash1, new_hash1)


class TestComponentFactory(unittest.TestCase):
    """Test cases for ComponentFactory class."""
    
    def test_factory_methods(self):
        """Test component factory methods."""
        # Test text component
        text = ComponentFactory.text(
            text="Hello World",
            x=10, y=20,
            width=200, height=30,
            color=(255, 255, 255)
        )
        self.assertEqual(text.type, "text")
        self.assertEqual(text.props.get("text"), "Hello World")
        
        # Test rectangle component
        rect = ComponentFactory.rect(
            x=10, y=20,
            width=100, height=50,
            backgroundColor=(255, 0, 0)
        )
        self.assertEqual(rect.type, "rect")
        self.assertEqual(rect.style.get("backgroundColor"), (255, 0, 0))
        
        # Test circle component
        circle = ComponentFactory.circle(
            x=50, y=50,
            radius=25,
            backgroundColor=(0, 0, 255)
        )
        self.assertEqual(circle.type, "circle")
        self.assertEqual(circle.props.get("radius"), 25)
        
        # Test button component
        button = ComponentFactory.button(
            text="Click me",
            x=10, y=20,
            width=100, height=40
        )
        self.assertEqual(button.type, "button")
        self.assertEqual(button.props.get("text"), "Click me")
        
        # Test grid component
        grid = ComponentFactory.grid(
            rows=3, cols=3,
            x=10, y=20,
            width=300, height=300
        )
        self.assertEqual(grid.type, "grid")
        self.assertEqual(grid.props.get("rows"), 3)
        self.assertEqual(grid.props.get("cols"), 3)
        
        # Test container component
        container = ComponentFactory.container(
            x=10, y=20,
            width=400, height=300
        )
        self.assertEqual(container.type, "container")


class TestUI(unittest.TestCase):
    """Test cases for UI class."""
    
    def test_ui_creation(self):
        """Test UI creation and basic properties."""
        ui = UI(800, 600)
        self.assertEqual(ui.screen_width, 800)
        self.assertEqual(ui.screen_height, 600)
        self.assertIsNotNone(ui.root)
        self.assertEqual(len(ui.root.children), 0)
    
    def test_ui_add_remove(self):
        """Test adding and removing components from UI."""
        ui = UI(800, 600)
        
        # Add components
        c1 = Component("rect")
        c2 = Component("text")
        ui.add(c1)
        ui.add(c2)
        
        # Check components were added
        self.assertEqual(len(ui.root.children), 2)
        self.assertIn(c1, ui.root.children)
        self.assertIn(c2, ui.root.children)
        
        # Check component registration
        self.assertIn(c1.id, ui.components_by_id)
        self.assertIn(c2.id, ui.components_by_id)
        
        # Remove a component
        ui.remove(c1)
        self.assertEqual(len(ui.root.children), 1)
        self.assertNotIn(c1, ui.root.children)
        self.assertIn(c2, ui.root.children)
        
        # Check component was unregistered
        self.assertNotIn(c1.id, ui.components_by_id)
        self.assertIn(c2.id, ui.components_by_id)
        
        # Clear all components
        ui.clear()
        self.assertEqual(len(ui.root.children), 0)
        self.assertEqual(len(ui.components_by_id), 1)  # Only root remains
    
    def test_ui_find_component(self):
        """Test finding components by ID and position."""
        ui = UI(800, 600)
        
        # Add components
        c1 = Component("rect", x=10, y=10, width=100, height=100)
        c2 = Component("rect", x=200, y=200, width=100, height=100)
        ui.add(c1)
        ui.add(c2)
        
        # Find by ID
        found = ui.find_component_by_id(c1.id)
        self.assertEqual(found, c1)
        
        # Find by position
        found = ui.find_component_at(50, 50)
        self.assertEqual(found, c1)
        
        found = ui.find_component_at(250, 250)
        self.assertEqual(found, c2)
        
        # Position outside any component should return None
        found = ui.find_component_at(500, 500)
        self.assertIsNone(found)
    
    def test_ui_to_dict(self):
        """Test UI serialization to dictionary."""
        ui = UI(800, 600)
        
        # Add components
        c1 = Component("rect", x=10, y=10, width=100, height=100)
        c2 = Component("text", x=200, y=200, width=100, height=50, text="Hello")
        ui.add(c1)
        ui.add(c2)
        
        # Convert to dictionary
        ui_dict = ui.to_dict()
        
        # Check basic properties
        self.assertEqual(ui_dict["screen_width"], 800)
        self.assertEqual(ui_dict["screen_height"], 600)
        
        # Check components
        self.assertEqual(len(ui_dict["components"]), 2)
        
        # Find the text component
        text_comp = None
        for comp in ui_dict["components"]:
            if comp["type"] == "text":
                text_comp = comp
                break
        
        self.assertIsNotNone(text_comp)
        self.assertEqual(text_comp["props"].get("text"), "Hello")


class TestDeltaCalculator(unittest.TestCase):
    """Test cases for DeltaCalculator class."""
    
    def test_delta_calculation(self):
        """Test delta calculation between states."""
        old_state = {
            "count": 1,
            "items": ["a", "b", "c"],
            "config": {
                "enabled": True,
                "value": 42
            }
        }
        
        new_state = {
            "count": 2,  # Changed
            "items": ["a", "b", "c"],  # Unchanged
            "config": {
                "enabled": True,  # Unchanged
                "value": 43  # Changed
            }
        }
        
        delta = DeltaCalculator.calculate_delta(old_state, new_state)
        
        # Check that only changed values are in the delta
        self.assertIn("delta", delta)
        self.assertIn("count", delta["delta"])
        self.assertNotIn("items", delta["delta"])
        self.assertIn("config", delta["delta"])
        self.assertIn("value", delta["delta"]["config"])
        self.assertNotIn("enabled", delta["delta"]["config"])
        
        # Check paths
        self.assertIn("paths", delta)
        self.assertIn(".count", delta["paths"])
        self.assertIn(".config.value", delta["paths"])
        
        # Test with null old state (should return full state)
        delta = DeltaCalculator.calculate_delta(None, new_state)
        self.assertIn("full", delta)
        self.assertEqual(delta["full"], new_state)
    
    def test_nested_delta_calculation(self):
        """Test delta calculation with nested structures."""
        old_state = {
            "ui": {
                "components": [
                    {"id": "1", "props": {"text": "Hello"}},
                    {"id": "2", "props": {"value": 10}}
                ]
            }
        }
        
        new_state = {
            "ui": {
                "components": [
                    {"id": "1", "props": {"text": "Updated"}},  # Changed
                    {"id": "2", "props": {"value": 10}}  # Unchanged
                ]
            }
        }
        
        delta = DeltaCalculator.calculate_delta(old_state, new_state)
        
        # Check that only the changed component is in the delta
        self.assertIn("delta", delta)
        self.assertIn("ui", delta["delta"])
        self.assertIn("components", delta["delta"]["ui"])
        self.assertIn(0, delta["delta"]["ui"]["components"])
        self.assertNotIn(1, delta["delta"]["ui"]["components"])
        
        # Check the specific path changed
        self.assertIn(".ui.components.0.props.text", delta["paths"])


if __name__ == "__main__":
    unittest.main() 