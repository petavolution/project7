#!/usr/bin/env python3
"""
Theme System for MetaMindIQTrain

This module defines a theme system that provides consistent styling across
different renderers (pygame, web, etc.) for the MetaMindIQTrain application.
"""

import json
import logging
from typing import Dict, Any, Optional, Tuple, List, Union
from pathlib import Path
import os

# Global theme instance
_current_theme = None
_registered_themes = {}

def get_theme():
    """Get the current theme.
    
    Returns:
        Current theme instance or None if not initialized
    """
    return _current_theme

def set_theme(theme):
    """Set the current theme.
    
    Args:
        theme: Theme instance to use
    """
    global _current_theme
    _current_theme = theme
    logging.info(f"Theme set: {theme.name}")

def register_theme(theme):
    """Register a theme.
    
    Args:
        theme: Theme instance to register
        
    Returns:
        The registered theme
    """
    global _registered_themes
    _registered_themes[theme.id] = theme
    logging.info(f"Theme registered: {theme.name} (ID: {theme.id})")
    return theme

def get_registered_theme(theme_id):
    """Get a registered theme by ID.
    
    Args:
        theme_id: ID of the theme to get
        
    Returns:
        Theme instance or None if not found
    """
    return _registered_themes.get(theme_id)

def create_dark_theme():
    """Create a dark theme.
    
    Returns:
        Dark theme instance
    """
    theme = Theme(
        id="dark",
        name="Dark Theme",
        platform="pygame",
        colors={
            "background": (15, 18, 28),          # Dark blue-black background
            "card_background": (25, 30, 45),     # Slightly lighter card background
            "surface": (35, 40, 55),             # Surface elements
            "border": (60, 70, 90),              # Border color
            
            "text_primary": (230, 235, 245),     # Primary text (white with slight blue tint)
            "text_secondary": (180, 185, 200),   # Secondary text (light gray)
            "text_disabled": (120, 125, 140),    # Disabled text (medium gray)
            
            "primary": (75, 120, 210),           # Primary action color (blue)
            "primary_hover": (90, 140, 230),     # Primary hover state
            "primary_active": (60, 100, 190),    # Primary active state
            "secondary": (70, 80, 100),          # Secondary action color
            "secondary_hover": (80, 90, 110),    # Secondary hover state
            "secondary_active": (60, 70, 90),    # Secondary active state
            "accent": (255, 140, 0),             # Accent color (orange)
            
            "success": (70, 200, 120),           # Success/correct (green)
            "error": (240, 80, 80),              # Error/incorrect (red)
            "warning": (255, 190, 50),           # Warning (yellow)
            "info": (70, 145, 240),              # Information (blue)
        },
        spacing={
            "xs": 4,
            "sm": 8,
            "md": 16,
            "lg": 24,
            "xl": 32,
            "xxl": 48,
        },
        border_radius={
            "none": 0,
            "sm": 4,
            "md": 8, 
            "lg": 12,
            "xl": 16,
            "pill": 999,
            "circle": "50%",
        },
        font_size={
            "xs": 12,
            "sm": 14,
            "md": 16,
            "lg": 20,
            "xl": 24,
            "xxl": 32,
            "xxxl": 48,
        }
    )
    
    register_theme(theme)
    return theme

def create_light_theme():
    """Create a light theme.
    
    Returns:
        Light theme instance
    """
    theme = Theme(
        id="light",
        name="Light Theme",
        platform="pygame",
        colors={
            "background": (245, 245, 250),       # Very light gray background
            "card_background": (255, 255, 255),  # White card background
            "surface": (240, 240, 245),          # Surface elements
            "border": (200, 200, 210),           # Light gray border
            
            "text_primary": (30, 35, 40),        # Primary text (dark gray)
            "text_secondary": (100, 105, 115),   # Secondary text (medium gray)
            "text_disabled": (160, 165, 175),    # Disabled text (light gray)
            
            "primary": (60, 110, 200),           # Primary action color (blue)
            "primary_hover": (75, 130, 220),     # Primary hover state
            "primary_active": (45, 90, 180),     # Primary active state
            "secondary": (220, 220, 230),        # Secondary action color
            "secondary_hover": (230, 230, 240),  # Secondary hover state
            "secondary_active": (210, 210, 220), # Secondary active state
            "accent": (255, 140, 0),             # Accent color (orange)
            
            "success": (60, 190, 110),           # Success/correct (green)
            "error": (230, 70, 70),              # Error/incorrect (red)
            "warning": (245, 180, 40),           # Warning (yellow)
            "info": (60, 135, 230),              # Information (blue)
        },
        spacing={
            "xs": 4,
            "sm": 8,
            "md": 16,
            "lg": 24,
            "xl": 32,
            "xxl": 48,
        },
        border_radius={
            "none": 0,
            "sm": 4,
            "md": 8, 
            "lg": 12,
            "xl": 16,
            "pill": 999,
            "circle": "50%",
        },
        font_size={
            "xs": 12,
            "sm": 14,
            "md": 16,
            "lg": 20,
            "xl": 24,
            "xxl": 32,
            "xxxl": 48,
        }
    )
    
    register_theme(theme)
    return theme


class Theme:
    """Theme definition for consistent styling across platforms."""
    
    def __init__(self, name: str, platform: str = "all", id: str = None):
        """Initialize a theme.
        
        Args:
            name: Theme name
            platform: Target platform (pygame, web, or all)
            id: Theme ID (defaults to lowercase name if not provided)
        """
        self.name = name
        self.platform = platform
        self.id = id or name.lower().replace(" ", "_")
        
        # Color palette
        self.colors = {
            # UI colors
            "background": (30, 36, 44),        # Dark blue/gray background
            "card_background": (40, 44, 52),   # Slightly lighter card background
            "surface": (45, 50, 60),           # Surface elements
            "border": (60, 70, 80),            # Border color
            
            # Text colors
            "text_primary": (255, 255, 255),   # Primary text (white)
            "text_secondary": (180, 185, 190), # Secondary text (light gray)
            "text_disabled": (120, 125, 130),  # Disabled text (medium gray)
            
            # Interactive elements
            "primary": (0, 120, 255),          # Primary action color (blue)
            "primary_hover": (30, 140, 255),   # Primary hover state
            "primary_active": (0, 100, 220),   # Primary active state
            "secondary": (80, 90, 100),        # Secondary action color
            "secondary_hover": (90, 100, 110), # Secondary hover state
            "secondary_active": (70, 80, 90),  # Secondary active state
            "accent": (255, 149, 0),           # Accent color (orange)
            
            # Status colors
            "success": (75, 210, 75),          # Success/correct (green)
            "error": (255, 75, 75),            # Error/incorrect (red)
            "warning": (255, 200, 55),         # Warning (yellow)
            "info": (75, 150, 255),            # Information (blue)
            
            # Cell states
            "cell_background": (40, 44, 52),
            "cell_highlight": (60, 70, 90),
            "cell_active": (60, 120, 220),
            "cell_correct": (75, 210, 75),
            "cell_incorrect": (255, 75, 75),
            
            # Overlay and modal colors
            "overlay": (0, 0, 0, 160),         # Semi-transparent overlay
            "modal_background": (50, 55, 65),  # Modal dialog background
        }
        
        # Sizing and spacing
        self.spacing = {
            "xs": 4,
            "sm": 8,
            "md": 16,
            "lg": 24,
            "xl": 32,
            "xxl": 48,
        }
        
        # Border radii
        self.border_radius = {
            "none": 0,
            "sm": 4,
            "md": 8, 
            "lg": 12,
            "xl": 16,
            "pill": 999,
            "circle": "50%",
        }
        
        # Font sizes
        self.font_size = {
            "xs": 12,
            "sm": 14,
            "md": 16,
            "lg": 20,
            "xl": 24,
            "xxl": 32,
            "xxxl": 48,
        }
        
        # Line heights
        self.line_height = {
            "xs": 1.0,  # No extra line height
            "sm": 1.2,  # Slightly tighter
            "md": 1.5,  # Standard
            "lg": 1.8,  # More spacious
            "xl": 2.0,  # Double height
        }
        
        # Font weights
        self.font_weight = {
            "light": 300,
            "normal": 400,
            "medium": 500,
            "semibold": 600,
            "bold": 700,
        }
        
        # Animation durations (ms)
        self.animation = {
            "fast": 100,
            "normal": 200,
            "slow": 300,
            "very_slow": 500,
        }
        
        # Shadow levels
        self.shadow = {
            "none": "none",
            "sm": "0 1px 2px rgba(0, 0, 0, 0.1)",
            "md": "0 2px 4px rgba(0, 0, 0, 0.15)",
            "lg": "0 4px 8px rgba(0, 0, 0, 0.2)",
            "xl": "0 8px 16px rgba(0, 0, 0, 0.25)",
        }
        
        # Opacity levels
        self.opacity = {
            "invisible": 0,
            "faint": 0.25,
            "semi": 0.5,
            "mostly": 0.75,
            "full": 1.0,
        }
        
        # Default component style presets
        self.component_styles = {
            "text": {
                "color": self.colors["text_primary"],
                "fontSize": self.font_size["md"],
                "fontWeight": self.font_weight["normal"],
                "lineHeight": self.line_height["md"],
                "textAlign": "left",
                "opacity": self.opacity["full"],
                "variant": {
                    "title": {
                        "fontSize": self.font_size["xxl"],
                        "fontWeight": self.font_weight["bold"],
                    },
                    "subtitle": {
                        "fontSize": self.font_size["lg"],
                        "fontWeight": self.font_weight["medium"],
                        "color": self.colors["text_secondary"],
                    },
                    "caption": {
                        "fontSize": self.font_size["sm"],
                        "color": self.colors["text_secondary"],
                    },
                    "label": {
                        "fontSize": self.font_size["sm"],
                        "fontWeight": self.font_weight["medium"],
                    },
                },
                "state": {
                    "disabled": {
                        "color": self.colors["text_disabled"],
                        "opacity": self.opacity["semi"],
                    },
                    "highlighted": {
                        "color": self.colors["primary"],
                    },
                    "error": {
                        "color": self.colors["error"],
                    },
                }
            },
            "rect": {
                "backgroundColor": self.colors["surface"],
                "borderWidth": 0,
                "borderColor": self.colors["border"],
                "borderRadius": self.border_radius["none"],
                "opacity": self.opacity["full"],
                "variant": {
                    "card": {
                        "backgroundColor": self.colors["card_background"],
                        "borderRadius": self.border_radius["md"],
                        "borderWidth": 1,
                    },
                    "panel": {
                        "backgroundColor": self.colors["background"],
                        "borderWidth": 1,
                    },
                },
                "state": {
                    "disabled": {
                        "opacity": self.opacity["semi"],
                    },
                    "highlighted": {
                        "borderColor": self.colors["primary"],
                        "borderWidth": 2,
                    },
                }
            },
            "circle": {
                "backgroundColor": self.colors["surface"],
                "borderWidth": 0,
                "borderColor": self.colors["border"],
                "opacity": self.opacity["full"],
                "variant": {
                    "indicator": {
                        "backgroundColor": self.colors["primary"],
                        "size": self.spacing["md"],
                    },
                    "status": {
                        "size": self.spacing["sm"],
                    },
                },
                "state": {
                    "active": {
                        "backgroundColor": self.colors["primary"],
                    },
                    "success": {
                        "backgroundColor": self.colors["success"],
                    },
                    "error": {
                        "backgroundColor": self.colors["error"],
                    },
                    "warning": {
                        "backgroundColor": self.colors["warning"],
                    },
                }
            },
            "button": {
                "backgroundColor": self.colors["primary"],
                "color": self.colors["text_primary"],
                "borderWidth": 0,
                "borderColor": self.colors["border"],
                "borderRadius": self.border_radius["md"],
                "fontSize": self.font_size["md"],
                "fontWeight": self.font_weight["medium"],
                "padding": self.spacing["md"],
                "variant": {
                    "primary": {
                        "backgroundColor": self.colors["primary"],
                        "color": self.colors["text_primary"],
                    },
                    "secondary": {
                        "backgroundColor": self.colors["secondary"],
                        "color": self.colors["text_primary"],
                    },
                    "outline": {
                        "backgroundColor": "transparent",
                        "borderWidth": 1,
                        "borderColor": self.colors["primary"],
                        "color": self.colors["primary"],
                    },
                    "text": {
                        "backgroundColor": "transparent",
                        "color": self.colors["primary"],
                        "padding": 0,
                    },
                },
                "state": {
                    "hover": {
                        "backgroundColor": self.colors["primary_hover"],
                    },
                    "active": {
                        "backgroundColor": self.colors["primary_active"],
                    },
                    "disabled": {
                        "backgroundColor": self.colors["secondary"],
                        "color": self.colors["text_disabled"],
                        "opacity": self.opacity["semi"],
                    },
                }
            },
            "progress": {
                "backgroundColor": self.colors["secondary"],
                "fillColor": self.colors["primary"],
                "borderRadius": self.border_radius["pill"],
                "height": self.spacing["md"],
                "variant": {
                    "success": {
                        "fillColor": self.colors["success"],
                    },
                    "warning": {
                        "fillColor": self.colors["warning"],
                    },
                    "error": {
                        "fillColor": self.colors["error"],
                    },
                }
            }
        }
    
    def update(self, colors=None, spacing=None, border_radius=None, font_size=None, 
            line_height=None, font_weight=None, animation=None, shadow=None, opacity=None):
        """Update theme properties.
        
        Args:
            colors: Dictionary of colors to update
            spacing: Dictionary of spacing values to update
            border_radius: Dictionary of border radius values to update
            font_size: Dictionary of font size values to update
            line_height: Dictionary of line height values to update
            font_weight: Dictionary of font weight values to update
            animation: Dictionary of animation values to update
            shadow: Dictionary of shadow values to update
            opacity: Dictionary of opacity values to update
            
        Returns:
            Self for method chaining
        """
        if colors:
            self.colors.update(colors)
        if spacing:
            self.spacing.update(spacing)
        if border_radius:
            self.border_radius.update(border_radius)
        if font_size:
            self.font_size.update(font_size)
        if line_height:
            self.line_height.update(line_height)
        if font_weight:
            self.font_weight.update(font_weight)
        if animation:
            self.animation.update(animation)
        if shadow:
            self.shadow.update(shadow)
        if opacity:
            self.opacity.update(opacity)
            
        return self
    
    def get_style(self, component, variant=None, state=None):
        """Get style for a component, variant, and state.
        
        Args:
            component: Component type
            variant: Optional variant name
            state: Optional state name
            
        Returns:
            Style dictionary for the component
        """
        # Get base component style
        if component not in self.component_styles:
            return {}
            
        base_style = dict(self.component_styles[component])
        
        # Apply variant style
        if variant and "variant" in base_style and variant in base_style["variant"]:
            variant_style = base_style["variant"][variant]
            base_style.update(variant_style)
        
        # Apply state style
        if state and "state" in base_style and state in base_style["state"]:
            state_style = base_style["state"][state]
            base_style.update(state_style)
        
        # Remove internal definitions
        if "variant" in base_style:
            del base_style["variant"]
        if "state" in base_style:
            del base_style["state"]
            
        return base_style
    
    def export_json(self):
        """Export theme as JSON.
        
        Returns:
            JSON string representation of the theme
        """
        # Convert all values to JSON-serializable types
        def process_value(value):
            if isinstance(value, (list, tuple)) and len(value) in (3, 4) and all(isinstance(x, int) for x in value):
                return list(value)
            elif isinstance(value, dict):
                return {k: process_value(v) for k, v in value.items()}
            return value
            
        theme_dict = {
            "id": self.id,
            "name": self.name,
            "platform": self.platform,
            "colors": process_value(self.colors),
            "spacing": process_value(self.spacing),
            "border_radius": process_value(self.border_radius),
            "font_size": process_value(self.font_size),
            "line_height": process_value(self.line_height),
            "font_weight": process_value(self.font_weight),
            "animation": process_value(self.animation),
            "shadow": process_value(self.shadow),
            "opacity": process_value(self.opacity),
            "component_styles": process_value(self.component_styles)
        }
        
        return json.dumps(theme_dict, indent=2)
    
    @classmethod
    def from_json(cls, json_str):
        """Create a theme from JSON.
        
        Args:
            json_str: JSON string representation of the theme
            
        Returns:
            Theme instance
        """
        theme_dict = json.loads(json_str)
        
        # Create base theme
        theme = cls(
            name=theme_dict.get("name", "Unnamed Theme"),
            platform=theme_dict.get("platform", "all"),
            id=theme_dict.get("id")
        )
        
        # Update theme properties
        theme.colors = theme_dict.get("colors", theme.colors)
        theme.spacing = theme_dict.get("spacing", theme.spacing)
        theme.border_radius = theme_dict.get("border_radius", theme.border_radius)
        theme.font_size = theme_dict.get("font_size", theme.font_size)
        theme.line_height = theme_dict.get("line_height", theme.line_height)
        theme.font_weight = theme_dict.get("font_weight", theme.font_weight)
        theme.animation = theme_dict.get("animation", theme.animation)
        theme.shadow = theme_dict.get("shadow", theme.shadow)
        theme.opacity = theme_dict.get("opacity", theme.opacity)
        theme.component_styles = theme_dict.get("component_styles", theme.component_styles)
        
        return theme
    
    def save_to_file(self, path):
        """Save theme to a file.
        
        Args:
            path: File path to save theme to
        """
        with open(path, "w") as f:
            f.write(self.export_json())
            
    @classmethod
    def load_from_file(cls, path):
        """Load theme from a file.
        
        Args:
            path: File path to load theme from
            
        Returns:
            Theme instance
        """
        with open(path, "r") as f:
            return cls.from_json(f.read())


class ThemeProvider:
    """Provider for accessing theme properties."""
    
    def __init__(self, theme=None):
        """Initialize the theme provider.
        
        Args:
            theme: Theme instance to use or None to use the global theme
        """
        self.theme = theme
        
    def get_theme(self):
        """Get the current theme.
        
        Returns:
            Current theme instance
        """
        return self.theme or get_theme()
        
    def set_theme(self, theme):
        """Set the current theme.
        
        Args:
            theme: Theme instance to use
        """
        self.theme = theme
        
    def get_style(self, component, variant=None, state=None, **overrides):
        """Get style for a component, variant, and state with optional overrides.
        
        Args:
            component: Component type
            variant: Optional variant name
            state: Optional state name
            **overrides: Style overrides
            
        Returns:
            Style dictionary for the component
        """
        theme = self.get_theme()
        if not theme:
            return overrides
            
        # Get base style
        style = theme.get_style(component, variant, state)
        
        # Apply overrides
        if overrides:
            style.update(overrides)
            
        return style 