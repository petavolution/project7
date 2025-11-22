#!/usr/bin/env python3
"""
Application Context Provider for MetaMindIQTrain

This module provides a central application context with commonly used
application state that can be accessed from any component.
"""

import logging
import time
from typing import Dict, Any, Optional, List

from MetaMindIQTrain.core.context import create_context, set_context_value, get_context_value

logger = logging.getLogger(__name__)

# Define common context names
APP_STATE = "app.state"
USER_INFO = "app.user"
CURRENT_MODULE = "app.current_module"
THEME = "app.theme"
DEBUG_MODE = "app.debug_mode"
PERFORMANCE_METRICS = "app.performance"

def initialize_app_context():
    """Initialize the application context with default values."""
    # Application state
    create_context(APP_STATE, {
        "initialized": False,
        "loading": True,
        "error": None,
        "version": "1.0.0",
        "start_time": time.time()
    })
    
    # User information (empty until user logs in)
    create_context(USER_INFO, {
        "logged_in": False,
        "id": None,
        "name": None,
        "email": None,
        "preferences": {}
    })
    
    # Current module
    create_context(CURRENT_MODULE, {
        "id": None,
        "name": None,
        "type": None,
        "options": {},
        "state": {},
    })
    
    # Theme
    create_context(THEME, {
        "name": "default",
        "colors": {
            "primary": (100, 100, 200),
            "secondary": (80, 180, 80),
            "background": (30, 30, 40),
            "text": (240, 240, 240),
            "accent": (220, 100, 100),
            "success": (80, 200, 80),
            "warning": (200, 200, 80),
            "error": (200, 80, 80)
        },
        "fonts": {
            "primary": "default",
            "monospace": "monospace",
            "sizes": {
                "small": 12,
                "normal": 16,
                "large": 20,
                "heading": 24
            }
        },
        "spacing": {
            "small": 5,
            "normal": 10,
            "large": 20
        }
    })
    
    # Debug mode
    create_context(DEBUG_MODE, False)
    
    # Performance metrics
    create_context(PERFORMANCE_METRICS, {
        "fps": 0,
        "frame_time": 0,
        "memory_usage": 0,
        "render_count": 0,
        "component_stats": {}
    })
    
    logger.info("Application context initialized")

def set_app_initialized(initialized: bool = True):
    """Set the application initialized state.
    
    Args:
        initialized: Whether the app is initialized
    """
    state = get_context_value(APP_STATE)
    state["initialized"] = initialized
    state["loading"] = not initialized
    set_context_value(APP_STATE, state)

def set_app_loading(loading: bool):
    """Set the application loading state.
    
    Args:
        loading: Whether the app is loading
    """
    state = get_context_value(APP_STATE)
    state["loading"] = loading
    set_context_value(APP_STATE, state)

def set_app_error(error: Optional[str]):
    """Set the application error state.
    
    Args:
        error: Error message or None if no error
    """
    state = get_context_value(APP_STATE)
    state["error"] = error
    set_context_value(APP_STATE, state)

def set_user_info(user_info: Dict[str, Any]):
    """Set user information.
    
    Args:
        user_info: User information dictionary
    """
    set_context_value(USER_INFO, user_info)

def set_current_module(module_id: str, module_name: str, module_type: str, 
                     options: Dict[str, Any] = None):
    """Set the current active module.
    
    Args:
        module_id: Module ID
        module_name: Module name
        module_type: Module type
        options: Module options
    """
    module_info = get_context_value(CURRENT_MODULE)
    module_info.update({
        "id": module_id,
        "name": module_name,
        "type": module_type,
        "options": options or {}
    })
    set_context_value(CURRENT_MODULE, module_info)

def update_module_state(state_updates: Dict[str, Any]):
    """Update the current module's state.
    
    Args:
        state_updates: Dictionary of state updates
    """
    module_info = get_context_value(CURRENT_MODULE)
    if "state" not in module_info:
        module_info["state"] = {}
    module_info["state"].update(state_updates)
    set_context_value(CURRENT_MODULE, module_info)

def set_theme(theme_name: str, theme_data: Dict[str, Any] = None):
    """Set the application theme.
    
    Args:
        theme_name: Theme name
        theme_data: Optional complete theme data (if None, just update the name)
    """
    if theme_data is None:
        theme = get_context_value(THEME)
        theme["name"] = theme_name
        set_context_value(THEME, theme)
    else:
        theme_data["name"] = theme_name
        set_context_value(THEME, theme_data)

def set_debug_mode(enabled: bool):
    """Set debug mode.
    
    Args:
        enabled: Whether debug mode is enabled
    """
    set_context_value(DEBUG_MODE, enabled)

def update_performance_metrics(metrics_updates: Dict[str, Any]):
    """Update performance metrics.
    
    Args:
        metrics_updates: Dictionary of metrics updates
    """
    metrics = get_context_value(PERFORMANCE_METRICS)
    metrics.update(metrics_updates)
    set_context_value(PERFORMANCE_METRICS, metrics)

def track_component_render(component_id: str, render_time: float):
    """Track rendering performance for a component.
    
    Args:
        component_id: Component ID
        render_time: Time taken to render in milliseconds
    """
    metrics = get_context_value(PERFORMANCE_METRICS)
    
    # Update render count
    metrics["render_count"] += 1
    
    # Track component-specific metrics
    if "component_stats" not in metrics:
        metrics["component_stats"] = {}
        
    if component_id not in metrics["component_stats"]:
        metrics["component_stats"][component_id] = {
            "render_count": 0,
            "total_render_time": 0,
            "avg_render_time": 0,
            "max_render_time": 0
        }
        
    stats = metrics["component_stats"][component_id]
    stats["render_count"] += 1
    stats["total_render_time"] += render_time
    stats["avg_render_time"] = stats["total_render_time"] / stats["render_count"]
    stats["max_render_time"] = max(stats["max_render_time"], render_time)
    
    set_context_value(PERFORMANCE_METRICS, metrics)

def get_color(color_name: str) -> tuple:
    """Get a color from the current theme.
    
    Args:
        color_name: Color name (e.g., "primary", "text")
        
    Returns:
        Color tuple (R, G, B)
    """
    theme = get_context_value(THEME)
    return theme["colors"].get(color_name, (255, 255, 255))

def get_font_size(size_name: str) -> int:
    """Get a font size from the current theme.
    
    Args:
        size_name: Size name (e.g., "small", "normal")
        
    Returns:
        Font size in points
    """
    theme = get_context_value(THEME)
    return theme["fonts"]["sizes"].get(size_name, 16)

def get_spacing(spacing_name: str) -> int:
    """Get a spacing value from the current theme.
    
    Args:
        spacing_name: Spacing name (e.g., "small", "normal")
        
    Returns:
        Spacing value in pixels
    """
    theme = get_context_value(THEME)
    return theme["spacing"].get(spacing_name, 10) 