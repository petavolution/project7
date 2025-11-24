#!/usr/bin/env python3
"""
Component System for MetaMindIQTrain

Provides base component classes for UI construction and event handling.
"""

import logging

logger = logging.getLogger(__name__)


class UIComponent:
    """Base UI component class."""
    pass


class Component:
    """Base component class with property and event handling."""

    def __init__(self, component_id=None):
        self.id = component_id
        self._properties = {}
        self._event_handlers = {}
        self._mounted = False
        self.parent = None

    def set_property(self, key, value):
        """Set a component property."""
        self._properties[key] = value
        return self

    def get_property(self, key, default=None):
        """Get a component property."""
        return self._properties.get(key, default)

    def add_event_handler(self, event_type, handler):
        """Add an event handler."""
        if event_type not in self._event_handlers:
            self._event_handlers[event_type] = []
        self._event_handlers[event_type].append(handler)
        return self

    def trigger_event(self, event_type, *args, **kwargs):
        """Trigger an event and call all registered handlers."""
        handlers = self._event_handlers.get(event_type, [])
        result = True
        for handler in handlers:
            try:
                handler_result = handler(*args, **kwargs)
                if handler_result is False:
                    result = False
            except Exception as e:
                logger.error(f"Error in event handler for {event_type}: {e}")
                result = False
        return result

class Container:
    def __init__(self, component_id=None):
        self.id = component_id
        self.children = []
        self._mounted = False
        
    def get_children(self):
        return self.children.copy()
        
    def add_child(self, child):
        self.children.append(child)
        child.parent = self
        return child
        
    def remove_child(self, child):
        if child in self.children:
            self.children.remove(child)
            child.parent = None
            return True
        return False
        
    def clear_children(self):
        self.children.clear()
        
    def count_children(self, recursive=True):
        return len(self.children)
        
    def set_size(self, width, height):
        self.width = width
        self.height = height
        return self
        
    def set_property(self, key, value):
        setattr(self, key, value)
        return self
        
    def trigger_event(self, event_type, event_data=None):
        return True

class Text:
    def __init__(self, component_id=None):
        self.id = component_id
        self._mounted = False
    
    def set_text(self, text):
        self.text = text
        return self
        
    def set_position(self, x, y):
        self.x = x
        self.y = y
        return self
        
    def set_property(self, key, value):
        setattr(self, key, value)
        return self

class Button:
    def __init__(self, component_id=None, text=""):
        self.id = component_id
        self.text = text
        self._mounted = False
        self.parent = None
        
    def set_text(self, text):
        self.text = text
        return self
        
    def set_position(self, x, y):
        self.x = x
        self.y = y
        return self
        
    def set_size(self, width, height):
        self.width = width
        self.height = height
        return self
        
    def set_on_click(self, handler):
        self.on_click_handler = handler
        return self
        
    def trigger_event(self, event_type, event_data=None):
        if event_type == "mouse_up" and hasattr(self, "on_click_handler"):
            self.on_click_handler(self)
        return True

class RootComponent(Container):
    def __init__(self, width=800, height=600, background_color=None):
        super().__init__("root")
        self.width = width
        self.height = height
        self.background_color = background_color
        self._mounted = True
        
    def is_dirty(self):
        return True

def mount_component_tree(root):
    root._mounted = True
    for child in root.get_children():
        mount_component_tree(child)

def unmount_component_tree(root):
    root._mounted = False
    for child in root.get_children():
        unmount_component_tree(child)