#!/usr/bin/env python3
"""
Base training module for MetaMindIQTrain

This module provides the base class for all training modules in the MetaMindIQTrain platform.
Optimized with delta encoding for efficient state updates and performance improvements.
"""

import json
import logging
import time
import uuid
import sys
import os
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Tuple, Set
from pathlib import Path

# Ensure project root is in path for imports
_project_root = Path(__file__).resolve().parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

# Import config - try multiple approaches for robustness
try:
    from config import SCREEN_WIDTH, SCREEN_HEIGHT, calculate_sizes
except ImportError:
    try:
        from ..config import SCREEN_WIDTH, SCREEN_HEIGHT, calculate_sizes
    except ImportError:
        # Fallback defaults if config unavailable
        SCREEN_WIDTH = 1440
        SCREEN_HEIGHT = 1024
        def calculate_sizes(width, height):
            return {
                'SCREEN_WIDTH': width,
                'SCREEN_HEIGHT': height,
                'UI_HEADER_HEIGHT': int(height * 0.15),
                'UI_FOOTER_HEIGHT': int(height * 0.12),
                'UI_CONTENT_HEIGHT': int(height * 0.73),
            }

# Import components - try multiple approaches
try:
    from core.components import UI, Component, get_component_stats
except ImportError:
    try:
        from .components import UI, Component, get_component_stats
    except ImportError:
        # Minimal fallback if components unavailable
        class UI:
            def __init__(self): self.components = []
            def clear(self): self.components = []
            def add_component(self, c): self.components.append(c)
            def to_dict(self): return {'components': self.components}
            def text(self, **kwargs): return kwargs
        class Component: pass
        def get_component_stats(): return {}

# Set up logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DeltaEncoder:
    """Delta encoding for efficient state updates."""
    
    @staticmethod
    def compute_delta(previous_state: Dict[str, Any], current_state: Dict[str, Any]) -> Dict[str, Any]:
        """Compute delta between previous and current state.
        
        Args:
            previous_state: Previous state dictionary
            current_state: Current state dictionary
            
        Returns:
            Delta dictionary with only changed values
        """
        if not previous_state:
            return current_state
            
        delta = {}
        DeltaEncoder._compute_delta_recursive(previous_state, current_state, delta, "")
        return delta
    
    @staticmethod
    def _compute_delta_recursive(prev: Any, curr: Any, delta: Dict[str, Any], path: str) -> None:
        """Recursively compute delta between two states.
        
        Args:
            prev: Previous value
            curr: Current value
            delta: Output delta dictionary
            path: Current path in the state (for nested dicts)
        """
        # Handle different types
        if type(prev) != type(curr):
            # Types are different, include the entire current value
            if path:
                delta[path] = curr
            else:
                # Root level, copy all keys
                for key, value in curr.items():
                    delta[key] = value
            return
            
        # Handle dict type
        if isinstance(curr, dict):
            # Find keys only in current dict
            for key in set(curr.keys()) - set(prev.keys()):
                new_path = f"{path}.{key}" if path else key
                delta[new_path] = curr[key]
                
            # Find keys in both dicts
            for key in set(curr.keys()) & set(prev.keys()):
                new_path = f"{path}.{key}" if path else key
                if curr[key] != prev[key]:
                    if isinstance(curr[key], dict) and isinstance(prev[key], dict):
                        # Recurse for nested dicts
                        DeltaEncoder._compute_delta_recursive(prev[key], curr[key], delta, new_path)
                    else:
                        # Add changed value
                        delta[new_path] = curr[key]
            
            # Keys only in previous dict are considered deleted
            for key in set(prev.keys()) - set(curr.keys()):
                new_path = f"{path}.{key}" if path else key
                delta[new_path] = None  # Null indicates deletion
                
        # Handle non-dict type
        elif curr != prev:
            delta[path] = curr
    
    @staticmethod
    def apply_delta(base_state: Dict[str, Any], delta: Dict[str, Any]) -> Dict[str, Any]:
        """Apply delta to base state to get updated state.
        
        Args:
            base_state: Base state dictionary
            delta: Delta dictionary with changes
            
        Returns:
            Updated state dictionary
        """
        if not delta:
            return base_state
            
        # Make a deep copy of base state
        result = json.loads(json.dumps(base_state))
        
        # Apply each delta path
        for path, value in delta.items():
            if "." in path:
                # Handle nested path
                parts = path.split(".")
                curr = result
                
                # Navigate to parent object
                for part in parts[:-1]:
                    if part not in curr:
                        curr[part] = {}
                    curr = curr[part]
                    
                # Set or delete value
                if value is None:
                    # Delete key
                    if parts[-1] in curr:
                        del curr[parts[-1]]
                else:
                    # Set value
                    curr[parts[-1]] = value
            else:
                # Handle top-level path
                if value is None:
                    # Delete key
                    if path in result:
                        del result[path]
                else:
                    # Set value
                    result[path] = value
                    
        return result

class StateManager:
    """Manages module state with optimized delta encoding."""
    
    def __init__(self):
        """Initialize the state manager."""
        self.previous_state = {}
        self.current_state = {}
        self.delta_mode = True  # Whether to use delta encoding
        self.version = 0  # State version for tracking changes
    
    def update_state(self, new_state: Dict[str, Any]) -> Dict[str, Any]:
        """Update current state and compute delta if enabled.
        
        Args:
            new_state: New state dictionary
            
        Returns:
            State update to send (full state or delta)
        """
        self.previous_state = self.current_state
        self.current_state = new_state
        self.version += 1
        
        if self.delta_mode and self.previous_state:
            # Compute and return delta
            delta = DeltaEncoder.compute_delta(self.previous_state, self.current_state)
            
            # Add metadata
            delta["_meta"] = {
                "version": self.version,
                "is_delta": True,
                "base_version": self.version - 1
            }
            
            return delta
        else:
            # Return full state
            new_state["_meta"] = {
                "version": self.version,
                "is_delta": False
            }
            
            return new_state
    
    def get_full_state(self) -> Dict[str, Any]:
        """Get current full state with metadata.
        
        Returns:
            Current state dictionary with metadata
        """
        state = self.current_state.copy()
        state["_meta"] = {
            "version": self.version,
            "is_delta": False
        }
        
        return state
    
    def reset(self):
        """Reset the state manager."""
        self.previous_state = {}
        self.current_state = {}
        self.version = 0

class PerformanceMonitor:
    """Monitors module performance metrics."""
    
    def __init__(self):
        """Initialize the performance monitor."""
        self.frame_times = []
        self.max_samples = 100
        self.start_time = time.time()
        self.last_time = self.start_time
        self.metrics = {
            'avg_frame_time': 0,
            'min_frame_time': float('inf'),
            'max_frame_time': 0,
            'total_frames': 0,
            'fps': 0
        }
    
    def update(self):
        """Update performance metrics."""
        current_time = time.time()
        frame_time = current_time - self.last_time
        self.last_time = current_time
        
        # Update frame times
        self.frame_times.append(frame_time)
        if len(self.frame_times) > self.max_samples:
            self.frame_times.pop(0)
        
        # Update metrics
        if frame_time < self.metrics['min_frame_time']:
            self.metrics['min_frame_time'] = frame_time
            
        if frame_time > self.metrics['max_frame_time']:
            self.metrics['max_frame_time'] = frame_time
            
        self.metrics['avg_frame_time'] = sum(self.frame_times) / len(self.frame_times)
        self.metrics['total_frames'] += 1
        
        elapsed = current_time - self.start_time
        if elapsed > 0:
            self.metrics['fps'] = self.metrics['total_frames'] / elapsed
    
    def get_metrics(self) -> Dict[str, float]:
        """Get current performance metrics.
        
        Returns:
            Dictionary with performance metrics
        """
        return self.metrics.copy()
    
    def reset(self):
        """Reset the performance monitor."""
        self.frame_times = []
        self.start_time = time.time()
        self.last_time = self.start_time
        self.metrics = {
            'avg_frame_time': 0,
            'min_frame_time': float('inf'),
            'max_frame_time': 0,
            'total_frames': 0,
            'fps': 0
        }

class TrainingModule(ABC):
    """
    Base class for all training modules.
    
    This abstract class defines the interface that all training modules must implement.
    It provides common functionality and state management with optimized performance.
    """
    
    # Class-level screen dimensions that will be set by the runner
    # Default to config values but can be overridden at runtime
    SCREEN_WIDTH = SCREEN_WIDTH
    SCREEN_HEIGHT = SCREEN_HEIGHT
    
    @classmethod
    def configure_display(cls, width, height):
        """Configure the display settings for all modules.
        
        This is called once at application startup to set the display dimensions
        that all modules will use.
        
        Args:
            width: Screen width in pixels
            height: Screen height in pixels
        """
        cls.SCREEN_WIDTH = width
        cls.SCREEN_HEIGHT = height
        logger.info(f"Configured display settings: {width}x{height}")
    
    def __init__(self):
        """Initialize the training module."""
        # Module metadata
        self.name = "Base Training Module"
        self.description = "Base class for all training modules"
        self.category = "General"
        self.difficulty = "Easy"
        
        # Session information
        self.session_id = str(uuid.uuid4())
        self.start_time = time.time()
        self.last_update_time = time.time()
        
        # Game state
        self.score = 0
        self.level = 1
        self.message = ""
        self.is_completed = False
        
        # UI helpers
        self.ui = UI()
        
        # Performance monitoring
        self.performance = PerformanceMonitor()
        
        # State management
        self.state_manager = StateManager()
        
        # Screen dimensions from class level or config defaults
        self.screen_width = self.__class__.SCREEN_WIDTH
        self.screen_height = self.__class__.SCREEN_HEIGHT
        
        # Calculate UI sizes based on current dimensions
        self.ui_sizes = calculate_sizes(self.screen_width, self.screen_height)
        
        # Track dynamic properties for delta calculation
        self._tracked_properties = set(['score', 'level', 'message', 'is_completed'])
        
        # Initialize any module-specific state
        self.initialize()
        
        logger.info(f"Initialized module {self.name} for session {self.session_id}")
    
    def initialize(self):
        """Initialize module-specific state.
        
        This method is called during initialization and can be overridden
        by subclasses to set up module-specific state.
        """
        pass
    
    @staticmethod
    def get_name():
        """Get the name of the module."""
        return "Base Training Module"
    
    @staticmethod
    def get_description():
        """Get the description of the module."""
        return "Base class for all training modules"
    
    @abstractmethod
    def handle_click(self, x, y):
        """
        Handle a click event.
        
        Args:
            x: The x-coordinate of the click.
            y: The y-coordinate of the click.
            
        Returns:
            dict: A dictionary containing the result of the click.
        """
        pass
    
    def build_ui(self):
        """
        Build the UI components for the current state.
        
        This method should be overridden by subclasses to build the UI
        using the component system. The base implementation creates a
        simple UI with module name, level, and score.
        
        Returns:
            UI: The UI instance with components
        """
        self.ui.clear()
        
        # Add module name
        self.ui.add_component(self.ui.text(
            text=self.name,
            position=(self.screen_width // 2, 30),
            font_size=24,
            color=(255, 255, 255),
            align="center"
        ))
        
        # Add level and score
        self.ui.add_component(self.ui.text(
            text=f"Level: {self.level}",
            position=(20, 20),
            font_size=18,
            color=(200, 200, 200)
        ))
        
        self.ui.add_component(self.ui.text(
            text=f"Score: {self.score}",
            position=(self.screen_width - 20, 20),
            font_size=18,
            color=(200, 200, 200),
            align="right"
        ))
        
        # Add message if any
        if self.message:
            self.ui.add_component(self.ui.text(
                text=self.message,
                position=(self.screen_width // 2, self.screen_height - 30),
                font_size=18,
                color=(255, 255, 0),
                align="center"
            ))
            
        return self.ui
    
    def get_state(self):
        """
        Get the current state of the module.
        
        This method builds a standard state object with common fields
        and UI components. It calls build_ui() to get the UI components
        for the current state.
        
        Returns:
            dict: A dictionary containing the current state.
        """
        # Update performance metrics
        self.performance.update()
        
        # Build UI components
        ui = self.build_ui()
        
        # Create state object
        state = {
            # Module info
            'module': {
                'name': self.name,
                'description': self.description
            },
            # Session info
            'session': {
                'id': self.session_id,
                'start_time': self.start_time,
                'elapsed_time': time.time() - self.start_time
            },
            # Game state
            'game': {
                'score': self.score,
                'level': self.level,
                'message': self.message,
                'is_completed': self.is_completed
            },
            # UI components
            'ui': ui.to_dict(),
            # Performance metrics
            'performance': self.performance.get_metrics(),
            # Component system stats
            'component_stats': get_component_stats()
        }
        
        # Add module-specific state
        state.update(self.get_module_state())
        
        # Update state manager and get delta or full state
        return self.state_manager.update_state(state)
    
    def get_full_state(self):
        """
        Get the full current state without delta encoding.
        
        Returns:
            dict: A dictionary containing the current full state.
        """
        return self.state_manager.get_full_state()
    
    def get_module_state(self):
        """
        Get module-specific state.
        
        This method should be overridden by subclasses to provide
        module-specific state information.
        
        Returns:
            dict: A dictionary containing module-specific state.
        """
        return {}
    
    def update(self, dt):
        """
        Update the module state.

        This method is called periodically to update the module state.
        It can be overridden by subclasses to implement time-based updates.

        Args:
            dt: Time delta since last update in seconds.
        """
        self.last_update_time = time.time()

    def render(self, renderer):
        """
        Render the module using the provided renderer.

        This method renders the module's UI using the renderer abstraction.
        It can be overridden by subclasses to implement custom rendering.
        The default implementation renders a basic placeholder UI.

        Args:
            renderer: The renderer instance to use for drawing.
        """
        # Clear with background color
        renderer.clear((20, 20, 40, 255))

        # Draw module name as title
        renderer.draw_text(
            self.screen_width // 2, 50,
            self.name,
            font_size=32,
            color=(255, 255, 255, 255),
            align="center"
        )

        # Draw description
        if hasattr(self, 'description'):
            renderer.draw_text(
                self.screen_width // 2, 100,
                self.description,
                font_size=20,
                color=(200, 200, 200, 255),
                align="center"
            )

        # Draw score and level
        renderer.draw_text(
            50, 30,
            f"Level: {self.level}",
            font_size=18,
            color=(200, 200, 200, 255),
            align="left"
        )

        renderer.draw_text(
            self.screen_width - 50, 30,
            f"Score: {self.score}",
            font_size=18,
            color=(200, 200, 200, 255),
            align="right"
        )

        # Draw message if any
        if self.message:
            renderer.draw_text(
                self.screen_width // 2, self.screen_height - 50,
                self.message,
                font_size=18,
                color=(255, 255, 0, 255),
                align="center"
            )
        
    def track_property(self, property_name):
        """
        Track a module property for delta calculation.
        
        Args:
            property_name: Name of the property to track
        """
        self._tracked_properties.add(property_name)
    
    def reset(self):
        """
        Reset the module to its initial state.
        
        This method resets common properties and should be called
        by subclasses that override it.
        """
        self.score = 0
        self.level = 1
        self.message = ""
        self.is_completed = False
        self.ui.clear()
        self.state_manager.reset()
        self.performance.reset()
        
        logger.info(f"Reset module {self.name}")
        
    def cleanup(self):
        """
        Clean up module resources.
        
        This method is called when the module is no longer needed.
        It should be overridden by subclasses that need to clean up resources.
        """
        self.ui.clear()
        logger.info(f"Cleaned up module {self.name}")


# Dictionary of available modules
# This will be populated by implementations
available_modules = {}

def get_available_modules() -> Dict[str, type]:
    """Get available training modules.

    Returns:
        Dictionary of available modules
    """
    modules = {}

    # Try to import test module - multiple import paths for robustness
    try:
        from modules.test_module import TestTrainingModule
        modules['test_module'] = TestTrainingModule
    except ImportError:
        try:
            from MetaMindIQTrain.modules.test_module import TestTrainingModule
            modules['test_module'] = TestTrainingModule
        except ImportError:
            pass  # Module not available

    return modules 