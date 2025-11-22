#!/usr/bin/env python3
"""
Example Module for MetaMindIQTrain

This is a demonstration module that showcases the new component system,
context integration, and rendering capabilities. It provides a simple interactive
UI for demonstrating the architecture.
"""

import logging
import time
from typing import Dict, Any, Optional, List

from MetaMindIQTrain.core.component_system import (
    Component, UIComponent, Container, Text, Button,
    register_component_type
)
from MetaMindIQTrain.core.context import ContextAware
from MetaMindIQTrain.core.app_context import get_color, get_font_size, get_spacing
from MetaMindIQTrain.core.renderer import Renderer

logger = logging.getLogger(__name__)

# Create a custom component for the example module
class Counter(UIComponent):
    """A simple counter component with increment and decrement buttons."""
    
    def __init__(self, component_id: Optional[str] = None):
        """Initialize the counter component."""
        super().__init__(component_id)
        
        # Set up properties
        self.set_property("count", 0)
        self.set_property("min_value", 0)
        self.set_property("max_value", 100)
        self.set_property("step", 1)
        
        # Create child components
        self._create_children()
        
    def _create_children(self):
        """Create the child components for the counter."""
        # Create container for layout
        container = Container("counter_container")
        container.set_property("background_color", get_color("background"))
        self.add_child(container)
        
        # Create decrement button
        decrement_btn = Button("decrement_btn")
        decrement_btn.set_text("-")
        decrement_btn.set_size(40, 40)
        decrement_btn.set_on_click(self._on_decrement)
        container.add_child(decrement_btn)
        
        # Create count display
        count_text = Text("count_text")
        count_text.set_text(str(self.get_property("count")))
        count_text.set_font_size(get_font_size("large"))
        count_text.set_property("color", get_color("text"))
        container.add_child(count_text)
        
        # Create increment button
        increment_btn = Button("increment_btn")
        increment_btn.set_text("+")
        increment_btn.set_size(40, 40)
        increment_btn.set_on_click(self._on_increment)
        container.add_child(increment_btn)
        
    def on_mount(self):
        """Handle component mounting."""
        self._update_layout()
        
    def _update_layout(self):
        """Update the layout of the child components."""
        # Get the container
        container = self.get_child("counter_container")
        if not container:
            return
            
        # Set container size to match parent
        width, height = self.get_size()
        container.set_size(width, height)
        
        # Get child components
        decrement_btn = container.get_child("decrement_btn")
        count_text = container.get_child("count_text")
        increment_btn = container.get_child("increment_btn")
        
        if not (decrement_btn and count_text and increment_btn):
            return
            
        # Set component positions
        spacing = get_spacing("normal")
        decrement_btn.set_position(spacing, (height - 40) // 2)
        
        # Center the count text
        count_text.set_position(width // 2, height // 2)
        count_text.set_property("align", "center")
        
        # Position increment button on the right
        increment_btn.set_position(width - 40 - spacing, (height - 40) // 2)
        
    def _on_increment(self, button):
        """Handle increment button click."""
        count = self.get_property("count")
        max_value = self.get_property("max_value")
        step = self.get_property("step")
        
        # Increment count, but don't exceed max_value
        new_count = min(count + step, max_value)
        self.set_property("count", new_count)
        
        # Update count text
        self._update_count_display()
        
    def _on_decrement(self, button):
        """Handle decrement button click."""
        count = self.get_property("count")
        min_value = self.get_property("min_value")
        step = self.get_property("step")
        
        # Decrement count, but don't go below min_value
        new_count = max(count - step, min_value)
        self.set_property("count", new_count)
        
        # Update count text
        self._update_count_display()
        
    def _update_count_display(self):
        """Update the count display."""
        container = self.get_child("counter_container")
        if not container:
            return
            
        count_text = container.get_child("count_text")
        if not count_text:
            return
            
        # Update text
        count = self.get_property("count")
        count_text.set_text(str(count))

# Register the custom component
register_component_type("Counter", Counter)

class ExampleModule(Component, ContextAware):
    """Example module showcasing the component system and context integration."""
    
    def __init__(self, module_id: str = "example_module"):
        """Initialize the example module.
        
        Args:
            module_id: Module ID
        """
        super().__init__(module_id)
        
        # Create the UI components
        self._create_ui()
        
    def _create_ui(self):
        """Create the UI components for the example module."""
        # Main container
        container = Container("main_container")
        container.set_property("background_color", get_color("background"))
        self.add_child(container)
        
        # Title
        title = Text("title")
        title.set_text("Example Module")
        title.set_font_size(get_font_size("heading"))
        title.set_property("color", get_color("primary"))
        container.add_child(title)
        
        # Description
        description = Text("description")
        description.set_text("This is an example module showcasing the new component system.")
        description.set_font_size(get_font_size("normal"))
        description.set_property("color", get_color("text"))
        container.add_child(description)
        
        # Counter component
        counter = Counter("counter")
        counter.set_size(300, 60)
        container.add_child(counter)
        
        # Reset button
        reset_btn = Button("reset_btn")
        reset_btn.set_text("Reset Counter")
        reset_btn.set_size(150, 40)
        reset_btn.set_on_click(self._on_reset)
        container.add_child(reset_btn)
        
        # Step size buttons
        step_container = Container("step_container")
        step_container.set_size(300, 50)
        container.add_child(step_container)
        
        step_label = Text("step_label")
        step_label.set_text("Step Size:")
        step_label.set_font_size(get_font_size("normal"))
        step_label.set_property("color", get_color("text"))
        step_container.add_child(step_label)
        
        for step in [1, 5, 10]:
            step_btn = Button(f"step_{step}_btn")
            step_btn.set_text(str(step))
            step_btn.set_size(40, 30)
            step_btn.set_property("step_value", step)
            step_btn.set_on_click(self._on_step_change)
            step_container.add_child(step_btn)
        
    def on_mount(self):
        """Handle component mounting."""
        self._update_layout()
        
    def on_update(self, delta_time: float):
        """Handle component update.
        
        Args:
            delta_time: Time elapsed since last update in seconds
        """
        # This method is called every frame
        pass
        
    def _update_layout(self):
        """Update the layout of the UI components."""
        # Get the container
        container = self.get_child("main_container")
        if not container:
            return
            
        # Set container size (assuming we're in a full-window context)
        from MetaMindIQTrain.core.application import get_application
        app = get_application()
        if app.renderer:
            width, height = app.renderer.get_size()
            container.set_size(width, height)
        else:
            container.set_size(800, 600)
            
        # Get child components
        title = container.get_child("title")
        description = container.get_child("description")
        counter = container.get_child("counter")
        reset_btn = container.get_child("reset_btn")
        step_container = container.get_child("step_container")
        
        if not (title and description and counter and reset_btn and step_container):
            return
            
        # Set component positions
        padding = get_spacing("large")
        title.set_position(width // 2, padding)
        title.set_property("align", "center")
        
        description.set_position(width // 2, padding + get_font_size("heading") + get_spacing("normal"))
        description.set_property("align", "center")
        
        counter.set_position((width - 300) // 2, 150)
        
        reset_btn.set_position((width - 150) // 2, 230)
        
        step_container.set_position((width - 300) // 2, 290)
        
        # Update step container layout
        self._update_step_container_layout(step_container)
        
    def _update_step_container_layout(self, container):
        """Update the layout of the step container.
        
        Args:
            container: Step container component
        """
        step_label = container.get_child("step_label")
        if not step_label:
            return
            
        # Position step label
        step_label.set_position(0, 15)
        
        # Position step buttons
        x_offset = 100
        for step in [1, 5, 10]:
            step_btn = container.get_child(f"step_{step}_btn")
            if step_btn:
                step_btn.set_position(x_offset, 10)
                x_offset += 50
                
    def _on_reset(self, button):
        """Handle reset button click."""
        counter = self.get_child("main_container").get_child("counter")
        if counter:
            counter.set_property("count", 0)
            counter._update_count_display()
            
    def _on_step_change(self, button):
        """Handle step button click."""
        step_value = button.get_property("step_value")
        
        counter = self.get_child("main_container").get_child("counter")
        if counter:
            counter.set_property("step", step_value)
            
def create_module(module_id: str = "example_module", options: Dict[str, Any] = None) -> ExampleModule:
    """Create an instance of the example module.
    
    Args:
        module_id: Module ID
        options: Module options
        
    Returns:
        Example module instance
    """
    module = ExampleModule(module_id)
    return module 