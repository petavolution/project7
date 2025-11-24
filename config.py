#!/usr/bin/env python3
"""
Configuration Module for MetaMindIQTrain

This module contains centralized configuration settings for the entire application.
All modules should import their settings from here rather than hardcoding values.
"""

# Display settings
# IMPORTANT: This is the single source of truth for screen dimensions.
# All components should use these values and never hardcode dimensions.
SCREEN_WIDTH = 1440  # Default width for the application
SCREEN_HEIGHT = 1024  # Default height for the application

# Default window title
DEFAULT_WINDOW_TITLE = "MetaMindIQTrain"

# FPS settings
DEFAULT_FPS = 60

# Font settings - font sizes as percentage of screen height
DEFAULT_FONT = 'Arial'
TITLE_FONT_SIZE_PERCENT = 0.035  # Approximately 36px at 1024 height
REGULAR_FONT_SIZE_PERCENT = 0.023  # Approximately 24px at 1024 height
SMALL_FONT_SIZE_PERCENT = 0.018  # Approximately 18px at 1024 height

# Dark Theme Color Settings
# Main backgrounds
DEFAULT_BG_COLOR = (15, 18, 28)      # Dark blue-black background
HEADER_BG_COLOR = (22, 26, 38)        # Slightly lighter dark blue for header
FOOTER_BG_COLOR = (22, 26, 38)        # Slightly lighter dark blue for footer
CONTENT_BG_COLOR = (18, 22, 32)       # Mid dark blue for content area

# Text colors
DEFAULT_TEXT_COLOR = (220, 225, 235)  # Light blue-white text for high contrast

# Accent colors
ACCENT_COLOR_PRIMARY = (80, 120, 200)   # Vibrant blue accent
ACCENT_COLOR_SUCCESS = (70, 200, 120)   # Green for success/positive feedback
ACCENT_COLOR_WARNING = (240, 180, 60)   # Amber for warnings
ACCENT_COLOR_ERROR = (230, 70, 80)      # Red for errors/failures
ACCENT_COLOR_HIGHLIGHT = (100, 160, 255) # Lighter blue for highlights

# Element colors
BUTTON_COLOR = (40, 50, 80)            # Dark blue buttons
BUTTON_HOVER_COLOR = (50, 65, 100)     # Slightly lighter when hovered
BUTTON_TEXT_COLOR = (220, 225, 235)    # Light text on buttons
GRID_BG_COLOR = (25, 30, 45)           # Slightly lighter than background for grids
GRID_LINE_COLOR = (60, 70, 90)         # Mid-tone blue for grid lines

# Section divider settings
SECTION_DIVIDER_COLOR = (60, 70, 100)  # Medium blue divider for visibility
SECTION_DIVIDER_THICKNESS = 2          # Thickness of section dividers

# UI Layout settings as percentages of screen dimensions
# These settings define the standard layout sections for all modules
UI_HEADER_HEIGHT_PERCENT = 0.15  # Header takes 15% of screen height
UI_FOOTER_HEIGHT_PERCENT = 0.12  # Footer takes 12% of screen height
UI_CONTENT_HEIGHT_PERCENT = 0.73  # Content area takes 73% of screen height (remaining space)

# UI Component spacing as percentages
UI_PADDING_PERCENT = 0.02  # Padding is 2% of screen dimension
UI_MARGIN_PERCENT = 0.01   # Margin is 1% of screen dimension

# Standard button dimensions as percentages
BUTTON_WIDTH_PERCENT = 0.15     # 15% of screen width
BUTTON_HEIGHT_PERCENT = 0.06    # 6% of screen height
BUTTON_SPACING_PERCENT = 0.02   # 2% of screen width

# Module-specific settings
DEFAULT_SYMBOL_SIZE_PERCENT = 0.0625  # Default size for symbols as percentage of screen height (64px at 1024 height)

# Module Selection UI Settings
MODULE_LIST_ITEM_HEIGHT_PERCENT = 0.10  # Each module list item takes 10% of screen height
MODULE_LIST_SPACING_PERCENT = 0.01      # 1% spacing between module list items
MODULE_LIST_WIDTH_PERCENT = 0.60        # Module list width is 60% of screen width
MODULE_DESCRIPTION_HEIGHT_PERCENT = 0.05 # Description height is 5% of screen height

# UI Theme configuration - centralized theme styling for all modules
UI_THEME = {
    "colors": {
        "bg_color": (15, 18, 28),           # Main background
        "bg_dark": (10, 12, 20),             # Darker background
        "bg_light": (30, 35, 50),            # Lighter background for cards
        "card_bg": (22, 26, 38),             # Card background
        "card_hover": (35, 42, 60),          # Card hover state
        "text_color": (220, 225, 235),       # Primary text
        "text_muted": (150, 155, 165),       # Muted text
        "border_color": (60, 70, 90),        # Border color
        "primary_color": (80, 120, 200),     # Primary accent
        "secondary_color": (100, 160, 255),  # Secondary accent
        "success_color": (70, 200, 120),     # Success/correct
        "error_color": (230, 70, 80),        # Error/incorrect
        "warning_color": (240, 180, 60),     # Warning
    },
    "layouts": {
        "symbol_memory": {
            "grid_margin": 5,      # Grid margin as percentage
            "grid_padding": 2,     # Grid padding as percentage
            "cell_margin": 1,      # Cell margin as percentage
        },
        "morph_matrix": {
            "grid_margin": 5,
            "grid_padding": 2,
            "cell_margin": 1,
        },
        "expand_vision": {
            "grid_margin": 5,
            "grid_padding": 2,
        },
        "neural_flow": {
            "node_radius": 2,
            "node_padding": 3,
            "path_thickness": 1,
        },
        "neural_synthesis": {
            "grid_margin": 5,
            "grid_padding": 2,
            "cell_margin": 1,
        }
    }
}

# Module-specific settings for visual customization
MODULE_SETTINGS = {
    "symbol_memory": {
        "visual_scale": 1.0,          # Scale factor for visual elements
        "preserve_font_size": True,   # Keep font size consistent
        "animation_speed": 1.0,       # Animation speed multiplier
    },
    "morph_matrix": {
        "visual_scale": 1.0,
        "preserve_font_size": True,
        "animation_speed": 1.0,
    },
    "expand_vision": {
        "visual_scale": 1.0,
        "preserve_font_size": True,
        "animation_speed": 1.0,
    },
    "expand_vision_grid": {
        "visual_scale": 1.0,
        "preserve_font_size": True,
        "animation_speed": 1.0,
    },
    "neural_flow": {
        "visual_scale": 1.0,
        "preserve_font_size": True,
        "animation_speed": 1.0,
    },
    "quantum_memory": {
        "visual_scale": 1.0,
        "preserve_font_size": True,
        "animation_speed": 1.0,
    },
    "neural_synthesis": {
        "visual_scale": 1.0,
        "preserve_font_size": True,
        "animation_speed": 1.0,
    },
    "synesthetic_training": {
        "visual_scale": 1.0,
        "preserve_font_size": True,
        "animation_speed": 1.0,
    }
}

# Module-specific color schemes - providing consistent dark theme across modules
MODULE_COLORS = {
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
    }
}

# Function to calculate actual sizes based on current screen dimensions
def calculate_sizes(screen_width=None, screen_height=None):
    """Calculate actual pixel sizes based on percentages and current dimensions.
    
    Args:
        screen_width: Optional custom screen width (uses default if None)
        screen_height: Optional custom screen height (uses default if None)
        
    Returns:
        Dictionary with calculated pixel sizes
    """
    # Use provided dimensions or defaults
    width = screen_width if screen_width is not None else SCREEN_WIDTH
    height = screen_height if screen_height is not None else SCREEN_HEIGHT
    
    sizes = {
        # Store actual screen dimensions
        'SCREEN_WIDTH': width,
        'SCREEN_HEIGHT': height,
        
        # Font sizes
        'TITLE_FONT_SIZE': int(TITLE_FONT_SIZE_PERCENT * height),
        'REGULAR_FONT_SIZE': int(REGULAR_FONT_SIZE_PERCENT * height),
        'SMALL_FONT_SIZE': int(SMALL_FONT_SIZE_PERCENT * height),
        
        # Layout heights
        'UI_HEADER_HEIGHT': int(UI_HEADER_HEIGHT_PERCENT * height),
        'UI_FOOTER_HEIGHT': int(UI_FOOTER_HEIGHT_PERCENT * height),
        'UI_CONTENT_HEIGHT': int(UI_CONTENT_HEIGHT_PERCENT * height),
        
        # Derived layout positions
        'UI_CONTENT_TOP': int(UI_HEADER_HEIGHT_PERCENT * height),
        'UI_CONTENT_BOTTOM': height - int(UI_FOOTER_HEIGHT_PERCENT * height),
        
        # Spacing
        'UI_PADDING': int(UI_PADDING_PERCENT * min(width, height)),
        'UI_MARGIN': int(UI_MARGIN_PERCENT * min(width, height)),
        
        # Button dimensions
        'BUTTON_WIDTH': int(BUTTON_WIDTH_PERCENT * width),
        'BUTTON_HEIGHT': int(BUTTON_HEIGHT_PERCENT * height),
        'BUTTON_SPACING': int(BUTTON_SPACING_PERCENT * width),
        
        # Module-specific settings converted to pixels
        'DEFAULT_SYMBOL_SIZE': int(DEFAULT_SYMBOL_SIZE_PERCENT * height),
        
        # Module Selection UI
        'MODULE_LIST_ITEM_HEIGHT': int(MODULE_LIST_ITEM_HEIGHT_PERCENT * height),
        'MODULE_LIST_SPACING': int(MODULE_LIST_SPACING_PERCENT * height),
        'MODULE_LIST_WIDTH': int(MODULE_LIST_WIDTH_PERCENT * width),
        'MODULE_DESCRIPTION_HEIGHT': int(MODULE_DESCRIPTION_HEIGHT_PERCENT * height),
    }
    
    return sizes

# Default sizes based on configured screen dimensions
# These will be recalculated when the actual screen dimensions are known
DEFAULT_SIZES = calculate_sizes(SCREEN_WIDTH, SCREEN_HEIGHT)

# Extract default values for backward compatibility
TITLE_FONT_SIZE = DEFAULT_SIZES['TITLE_FONT_SIZE']
REGULAR_FONT_SIZE = DEFAULT_SIZES['REGULAR_FONT_SIZE']
SMALL_FONT_SIZE = DEFAULT_SIZES['SMALL_FONT_SIZE']
UI_HEADER_HEIGHT = DEFAULT_SIZES['UI_HEADER_HEIGHT']
UI_FOOTER_HEIGHT = DEFAULT_SIZES['UI_FOOTER_HEIGHT']
UI_CONTENT_TOP = DEFAULT_SIZES['UI_CONTENT_TOP']
UI_CONTENT_BOTTOM = DEFAULT_SIZES['UI_CONTENT_BOTTOM']
UI_CONTENT_HEIGHT = DEFAULT_SIZES['UI_CONTENT_HEIGHT']
UI_PADDING = DEFAULT_SIZES['UI_PADDING']
UI_MARGIN = DEFAULT_SIZES['UI_MARGIN']
BUTTON_WIDTH = DEFAULT_SIZES['BUTTON_WIDTH']
BUTTON_HEIGHT = DEFAULT_SIZES['BUTTON_HEIGHT']
BUTTON_SPACING = DEFAULT_SIZES['BUTTON_SPACING']
DEFAULT_SYMBOL_SIZE = DEFAULT_SIZES['DEFAULT_SYMBOL_SIZE']

# Helper function to scale coordinates and sizes for different resolutions
def scale_for_resolution(value, original_dimension, target_dimension):
    """Scale a value from original resolution to target resolution
    
    Args:
        value: Value to scale (coordinate or size)
        original_dimension: Original dimension (width or height)
        target_dimension: Target dimension
        
    Returns:
        Scaled value
    """
    scale_factor = target_dimension / original_dimension
    return int(value * scale_factor)

# Helper function to scale coordinates for different aspect ratios
def scale_coordinates(x, y, original_width, original_height, target_width, target_height):
    """Scale coordinates from original resolution to target resolution
    
    Args:
        x: X coordinate in original resolution
        y: Y coordinate in original resolution
        original_width: Original screen width
        original_height: Original screen height
        target_width: Target screen width
        target_height: Target screen height
        
    Returns:
        Tuple (scaled_x, scaled_y)
    """
    scaled_x = scale_for_resolution(x, original_width, target_width)
    scaled_y = scale_for_resolution(y, original_height, target_height)
    return (scaled_x, scaled_y)

# Helper function to maintain aspect ratio when resizing
def maintain_aspect_ratio(width, height, target_width=None, target_height=None):
    """Calculate dimensions that maintain aspect ratio when resizing
    
    Args:
        width: Original width
        height: Original height
        target_width: Target width (if None, will be calculated from target_height)
        target_height: Target height (if None, will be calculated from target_width)
        
    Returns:
        Tuple (new_width, new_height) that maintains aspect ratio
    """
    if target_width is None and target_height is None:
        # No target dimensions provided, return original
        return (width, height)
    
    aspect_ratio = width / height
    
    if target_width is not None and target_height is not None:
        # Both dimensions provided, use the limiting factor
        width_scale = target_width / width
        height_scale = target_height / height
        
        if width_scale < height_scale:
            # Width is the limiting factor
            new_width = target_width
            new_height = int(new_width / aspect_ratio)
        else:
            # Height is the limiting factor
            new_height = target_height
            new_width = int(new_height * aspect_ratio)
            
        return (new_width, new_height)
    
    elif target_width is not None:
        # Calculate height based on width
        new_width = target_width
        new_height = int(new_width / aspect_ratio)
        return (new_width, new_height)
    
    else:
        # Calculate width based on height
        new_height = target_height
        new_width = int(new_height * aspect_ratio)
        return (new_width, new_height) 