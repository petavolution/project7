#!/usr/bin/env python3
"""
Unified Configuration System for MetaMindIQTrain

This module provides a centralized, unified configuration system for the entire application.
It handles loading configurations from files, environment variables, and provides
defaults for all settings. This approach reduces duplication and simplifies changes.
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, Union, List
from pydantic import BaseModel, Field

# Set up logging
logger = logging.getLogger(__name__)

# Base configuration models
class UIConfig(BaseModel):
    """UI configuration settings."""
    screen_width: int = 1440
    screen_height: int = 1024
    fps: int = 60
    font_name: str = 'Arial'
    title_font_size_percent: float = 0.035
    regular_font_size_percent: float = 0.023
    small_font_size_percent: float = 0.018
    dark_theme: bool = True

class ColorConfig(BaseModel):
    """Color configuration settings."""
    # Main backgrounds
    background: tuple = (15, 18, 28)
    header_bg: tuple = (22, 26, 38)
    footer_bg: tuple = (22, 26, 38)
    content_bg: tuple = (18, 22, 32)
    
    # Text colors
    text: tuple = (220, 225, 235)
    text_secondary: tuple = (180, 185, 195)
    
    # Accent colors
    primary: tuple = (80, 120, 200)
    success: tuple = (70, 200, 120)
    warning: tuple = (240, 180, 60)
    error: tuple = (230, 70, 80)
    highlight: tuple = (100, 160, 255)
    
    # UI elements
    button: tuple = (40, 50, 80)
    button_hover: tuple = (50, 65, 100)
    button_text: tuple = (220, 225, 235)
    grid_bg: tuple = (25, 30, 45)
    grid_line: tuple = (60, 70, 90)
    divider: tuple = (60, 70, 100)

class LayoutConfig(BaseModel):
    """Layout configuration settings."""
    header_height_percent: float = 0.15
    footer_height_percent: float = 0.12
    content_height_percent: float = 0.73
    padding_percent: float = 0.02
    margin_percent: float = 0.01
    button_width_percent: float = 0.15
    button_height_percent: float = 0.06
    button_spacing_percent: float = 0.02

class ServerConfig(BaseModel):
    """Server configuration settings."""
    host: str = '0.0.0.0'
    port: int = 5000
    debug: bool = False
    secret_key: str = 'metamind-development-key'
    session_timeout: int = 3600  # 1 hour
    max_active_sessions: int = 100

class ModuleConfig(BaseModel):
    """Base module configuration settings."""
    enabled: bool = True
    difficulty_levels: int = 10
    session_timeout: int = 1800  # 30 minutes
    custom_settings: Dict[str, Any] = Field(default_factory=dict)

class SystemConfig(BaseModel):
    """System-wide configuration settings."""
    app_name: str = "MetaMindIQTrain"
    version: str = "1.3.0"
    dev_mode: bool = False
    log_level: str = "INFO"
    data_dir: str = "./data"
    resources_dir: str = "./resources"
    cache_dir: str = "./cache"

class UnifiedConfig(BaseModel):
    """Unified application configuration."""
    system: SystemConfig = Field(default_factory=SystemConfig)
    ui: UIConfig = Field(default_factory=UIConfig)
    colors: ColorConfig = Field(default_factory=ColorConfig)
    layout: LayoutConfig = Field(default_factory=LayoutConfig)
    server: ServerConfig = Field(default_factory=ServerConfig)
    modules: Dict[str, ModuleConfig] = Field(default_factory=dict)
    module_colors: Dict[str, Dict[str, Any]] = Field(default_factory=dict)

# Initialize default configuration
config = UnifiedConfig()

# Module-specific color palettes
DEFAULT_MODULE_COLORS = {
    'symbol_memory': {
        'symbol_colors': [
            (100, 160, 255),  # Light blue
            (70, 200, 120),   # Green
            (240, 180, 60),   # Amber
            (230, 70, 80),    # Red
            (180, 90, 230),   # Purple
            (240, 130, 50),   # Orange
            (60, 190, 200),   # Teal
            (220, 110, 190),  # Pink
        ],
        'background': (15, 18, 28),
        'correct_highlight': (70, 200, 120, 180),  # Semi-transparent green
        'incorrect_highlight': (230, 70, 80, 180),  # Semi-transparent red
    },
    'morph_matrix': {
        'matrix_on_color': (100, 160, 255),  # Light blue for "on" cells
        'matrix_off_color': (30, 35, 50),    # Dark blue for "off" cells
        'matrix_border_color': (60, 70, 90), # Mid-tone for borders
        'selection_color': (80, 120, 200),   # Highlight for selected matrices
        'correct_color': (70, 200, 120),     # Green for correct selections
        'incorrect_color': (230, 70, 80),    # Red for incorrect selections
    },
    'expand_vision': {
        'focus_point_color': (80, 120, 200),  # Blue for central focus point
        'circle_color': (100, 160, 255),      # Light blue for expanding circle
        'number_colors': [
            (220, 225, 235),  # Light text
            (240, 180, 60),   # Amber
            (70, 200, 120),   # Green
            (230, 70, 80),    # Red
            (180, 90, 230),   # Purple
        ],
        'answer_correct_color': (70, 200, 120),
        'answer_incorrect_color': (230, 70, 80),
    },
    'neural_flow': {
        'neural_bg': (5, 10, 25),  # Very dark background for neural visualization
        'neural_node': (80, 140, 240),  # Bright blue nodes
        'neural_path': (40, 70, 120, 150),  # Semi-transparent path
        'neural_pulse': (140, 200, 255),  # Brighter pulse
        'neural_active': (120, 220, 255),  # Active path color
        'neural_particle': (200, 230, 255),  # Bright particles
        'focus_point': (255, 255, 255),  # White focus point
        'target_node': (255, 180, 80),  # Target node in orange
        'success_node': (120, 255, 140),  # Success node in green
        'error_node': (255, 100, 100),  # Error node in red
        'info_text': (180, 220, 250),  # Light blue for information text
    }
}

# Default module configuration
DEFAULT_MODULE_CONFIG = {
    'neural_flow': ModuleConfig(
        custom_settings={
            'preparation_time': 5,
            'trial_time': 60,
            'feedback_time': 3,
            'min_nodes': 10,
            'max_nodes': 50,
            'initial_target_count': 3,
            'max_target_count': 10,
            'points_per_target': 10,
            'error_penalty': 5,
            'target_timeout': 5,
            'level_up_threshold': 3,
            'accuracy_threshold': 0.7,
        }
    ),
    'expand_vision': ModuleConfig(
        custom_settings={
            'vision_radius_start': 100,
            'vision_radius_increment': 50,
            'min_number_count': 3,
            'max_number_count': 12,
            'preparation_time': 3,
            'response_time': 5,
            'level_up_threshold': 3,
        }
    ),
    'symbol_memory': ModuleConfig(
        custom_settings={
            'symbol_set_size': 5,
            'symbol_display_time': 2.0,
            'inter_symbol_time': 0.5,
            'feedback_time': 1.0,
            'level_up_threshold': 3,
        }
    ),
    'morph_matrix': ModuleConfig(
        custom_settings={
            'matrix_size_min': 3,
            'matrix_size_max': 7,
            'display_time': 3.0,
            'response_time': 5.0,
            'feedback_time': 1.5,
            'level_up_threshold': 3,
        }
    )
}

def load_config(config_path: Optional[Union[str, Path]] = None, 
                env_prefix: str = "METAMIND_") -> UnifiedConfig:
    """Load configuration from file and environment variables.
    
    Args:
        config_path: Path to configuration file
        env_prefix: Prefix for environment variables
        
    Returns:
        Loaded configuration
    """
    global config
    
    # Start with default config
    config = UnifiedConfig()
    
    # Set default module colors
    config.module_colors = DEFAULT_MODULE_COLORS
    
    # Set default module configurations
    config.modules = DEFAULT_MODULE_CONFIG
    
    # Load from file if provided
    if config_path:
        try:
            config_path = Path(config_path)
            if config_path.exists():
                with open(config_path, 'r') as f:
                    file_config = json.load(f)
                
                # Update config with file values
                config = UnifiedConfig.parse_obj(file_config)
                logger.info(f"Loaded configuration from {config_path}")
            else:
                logger.warning(f"Configuration file not found: {config_path}")
        except Exception as e:
            logger.error(f"Error loading configuration file: {str(e)}")
    
    # Override with environment variables
    _load_from_env(env_prefix)
    
    return config

def _load_from_env(prefix: str):
    """Load configuration from environment variables.
    
    Args:
        prefix: Prefix for environment variables
    """
    # TODO: Implement environment variable loading
    pass

def get_module_config(module_id: str) -> ModuleConfig:
    """Get configuration for a specific module.
    
    Args:
        module_id: Module identifier
        
    Returns:
        Module configuration
    """
    if module_id in config.modules:
        return config.modules[module_id]
    else:
        # Return default module config
        return ModuleConfig()

def get_module_colors(module_id: str) -> Dict[str, Any]:
    """Get color scheme for a specific module.
    
    Args:
        module_id: Module identifier
        
    Returns:
        Module color scheme
    """
    if module_id in config.module_colors:
        return config.module_colors[module_id]
    else:
        # Return empty dict if no specific colors
        return {}

def calculate_sizes(screen_width=None, screen_height=None):
    """Calculate actual pixel sizes based on percentages and current dimensions.
    
    Args:
        screen_width: Optional override width
        screen_height: Optional override height
        
    Returns:
        Dictionary of calculated sizes
    """
    # Use provided dimensions or defaults
    width = screen_width or config.ui.screen_width
    height = screen_height or config.ui.screen_height
    
    sizes = {
        # Screen dimensions
        'SCREEN_WIDTH': width,
        'SCREEN_HEIGHT': height,
        
        # Font sizes
        'TITLE_FONT_SIZE': int(config.ui.title_font_size_percent * height),
        'REGULAR_FONT_SIZE': int(config.ui.regular_font_size_percent * height),
        'SMALL_FONT_SIZE': int(config.ui.small_font_size_percent * height),
        
        # Layout heights
        'UI_HEADER_HEIGHT': int(config.layout.header_height_percent * height),
        'UI_FOOTER_HEIGHT': int(config.layout.footer_height_percent * height),
        'UI_CONTENT_HEIGHT': int(config.layout.content_height_percent * height),
        
        # Derived layout positions
        'UI_CONTENT_TOP': int(config.layout.header_height_percent * height),
        'UI_CONTENT_BOTTOM': height - int(config.layout.footer_height_percent * height),
        
        # Spacing
        'UI_PADDING': int(config.layout.padding_percent * min(width, height)),
        'UI_MARGIN': int(config.layout.margin_percent * min(width, height)),
        
        # Button dimensions
        'BUTTON_WIDTH': int(config.layout.button_width_percent * width),
        'BUTTON_HEIGHT': int(config.layout.button_height_percent * height),
        'BUTTON_SPACING': int(config.layout.button_spacing_percent * width),
    }
    
    return sizes

# Initialize the configuration system
load_config()

# Default sizes based on configured screen dimensions
DEFAULT_SIZES = calculate_sizes() 