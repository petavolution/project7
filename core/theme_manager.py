#!/usr/bin/env python3
"""
Unified Theme Manager for MetaMindIQTrain

This module provides centralized theme management for both PyGame and web clients,
ensuring consistent colors, fonts, and styling across all platforms.

Key features:
1. Single source of truth for theming
2. Support for multiple themes (dark, light)
3. Platform-specific overrides
4. Component style definitions
5. Easy export to CSS variables for web clients
"""

from typing import Dict, Any, List, Tuple, Optional
import json
import os
from pathlib import Path

class ThemeManager:
    """Centralized theme management for all platforms."""
    
    # Base themes that match the CSS variables
    THEMES = {
        "default": {
            # Base colors
            "bg_color": (20, 25, 31),        # #14191f
            "text_color": (240, 240, 240),   # #f0f0f0
            "primary_color": (0, 120, 255),  # #0078ff
            "card_bg": (30, 36, 44),         # #1e242c
            "card_hover": (42, 48, 56),      # #2a3038
            "accent_color": (50, 255, 50),   # #32ff32
            
            # Additional colors
            "success_color": (50, 255, 80),  # #32ff50
            "error_color": (255, 50, 50),    # #ff3232
            "warning_color": (255, 225, 50), # #ffe132
            "secondary_color": (128, 0, 255),# #8000ff
            "border_color": (60, 70, 80),    # #3c4650
            
            # Component-specific colors
            "button_bg": (0, 120, 255),      # #0078ff
            "button_hover": (30, 140, 255),  # #1e8cff
            "card_border": (40, 46, 54),     # #282e36
            
            # Fonts
            "font_family": "Arial",
            "title_size": 24,
            "text_size": 16,
            "small_text_size": 14,
            
            # Spacing
            "padding": 16,
            "margin": 16,
            "border_radius": 8,
            
            # Grid layout
            "grid_gap": 20,
            "min_card_width": 280,
            
            # Animation
            "transition_duration": 0.3,  # seconds
        },
        
        "light": {
            # Base colors - light theme
            "bg_color": (240, 240, 245),     # #f0f0f5
            "text_color": (20, 20, 20),      # #141414
            "primary_color": (0, 100, 230),  # #0064e6
            "card_bg": (255, 255, 255),      # #ffffff
            "card_hover": (245, 245, 250),   # #f5f5fa
            "accent_color": (30, 200, 30),   # #1ec81e
            
            # Additional colors
            "success_color": (30, 200, 60),  # #1ec83c
            "error_color": (230, 30, 30),    # #e61e1e
            "warning_color": (230, 180, 30), # #e6b41e
            "secondary_color": (110, 0, 220),# #6e00dc
            "border_color": (200, 200, 210), # #c8c8d2
            
            # Component-specific colors
            "button_bg": (0, 100, 230),      # #0064e6
            "button_hover": (20, 120, 245),  # #1478f5
            "card_border": (220, 220, 230),  # #dcdce6
            
            # Fonts (same structure as default)
            "font_family": "Arial",
            "title_size": 24,
            "text_size": 16,
            "small_text_size": 14,
            
            # Spacing (same structure as default)
            "padding": 16,
            "margin": 16,
            "border_radius": 8,
            
            # Grid layout
            "grid_gap": 20,
            "min_card_width": 280,
            
            # Animation
            "transition_duration": 0.3,  # seconds
        }
    }
    
    # Current theme and platform
    _current_theme = "default"
    _current_platform = "pygame"
    
    @classmethod
    def get_theme(cls, theme_name=None, platform=None):
        """Get a theme by name.
        
        Args:
            theme_name: Name of the theme (default, light, etc.)
            platform: Platform-specific version (pygame, web)
            
        Returns:
            Dictionary with theme colors and settings
        """
        theme_name = theme_name or cls._current_theme
        platform = platform or cls._current_platform
        
        if theme_name not in cls.THEMES:
            theme_name = "default"
            
        # Get base theme
        theme = cls.THEMES[theme_name].copy()
        
        # Apply platform-specific overrides
        if platform == "web":
            # Web platform might have slight modifications
            pass
        elif platform == "pygame":
            # PyGame specific adjustments (e.g., for fonts)
            pass
            
        return theme
    
    @classmethod
    def set_current_theme(cls, theme_name):
        """Set the current theme.
        
        Args:
            theme_name: Name of the theme
        """
        if theme_name in cls.THEMES:
            cls._current_theme = theme_name
    
    @classmethod
    def set_platform(cls, platform):
        """Set the current platform.
        
        Args:
            platform: Platform name (pygame, web)
        """
        cls._current_platform = platform
    
    @classmethod
    def get_color(cls, color_name, theme_name=None, platform=None):
        """Get a specific color from the theme.
        
        Args:
            color_name: Name of the color
            theme_name: Optional theme override
            platform: Optional platform override
            
        Returns:
            Color tuple (r, g, b)
        """
        theme = cls.get_theme(theme_name, platform)
        return theme.get(color_name, theme.get("text_color"))
    
    @classmethod
    def to_css_variables(cls, theme_name=None):
        """Convert a theme to CSS variables.
        
        Args:
            theme_name: Name of the theme
            
        Returns:
            CSS variable declarations as a string
        """
        theme = cls.get_theme(theme_name, platform="web")
        css = ":root {\n"
        
        for key, value in theme.items():
            if isinstance(value, tuple) and len(value) >= 3:
                # It's a color tuple
                css += f"    --{key}: rgb({value[0]}, {value[1]}, {value[2]});\n"
            elif isinstance(value, (int, float)):
                # It's a number
                if "duration" in key:
                    css += f"    --{key}: {value}s;\n"
                elif "size" in key:
                    css += f"    --{key}: {value}px;\n"
                else:
                    css += f"    --{key}: {value};\n"
            else:
                # It's a string or other value
                css += f"    --{key}: {value};\n"
                
        css += "}\n"
        return css
    
    @classmethod
    def save_theme_to_css(cls, output_path, theme_name=None):
        """Save a theme as CSS variables to a file.
        
        Args:
            output_path: Path to save the CSS file
            theme_name: Optional theme name
        """
        css = cls.to_css_variables(theme_name)
        
        with open(output_path, 'w') as f:
            f.write(css)
    
    @classmethod
    def rgb_to_hex(cls, rgb):
        """Convert RGB tuple to hex string.
        
        Args:
            rgb: RGB tuple (r, g, b)
            
        Returns:
            Hex color string (#RRGGBB)
        """
        return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"
    
    @classmethod
    def hex_to_rgb(cls, hex_color):
        """Convert hex color string to RGB tuple.
        
        Args:
            hex_color: Hex color string (#RRGGBB)
            
        Returns:
            RGB tuple (r, g, b)
        """
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4)) 