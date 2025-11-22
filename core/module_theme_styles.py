#!/usr/bin/env python3
"""
Module Theme Styles for MetaMindIQTrain

This module defines and registers theme styles for all cognitive modules,
ensuring consistent visual appearance while allowing for module-specific
variations.
"""

import logging
from typing import Dict, Any

from MetaMindIQTrain.core.theme import Theme

logger = logging.getLogger(__name__)

def register_cognitive_module_styles(theme: Theme) -> None:
    """Register theme styles for all cognitive modules.
    
    This function registers theme styles for the following modules:
    - Symbol Memory
    - Morph Matrix
    - Expand Vision
    - Common module controls
    
    Args:
        theme: The theme to register styles for
    """
    logger.info(f"Registering cognitive module theme styles for '{theme.id}' theme")
    
    # Register common module styles
    _register_common_styles(theme)
    
    # Register module-specific styles
    _register_symbol_memory_styles(theme)
    _register_morph_matrix_styles(theme)
    _register_expand_vision_styles(theme)


def _register_common_styles(theme: Theme) -> None:
    """Register common styles shared across all modules.
    
    Args:
        theme: The theme to register styles for
    """
    # Common container
    theme.register_style("common.container", {
        "backgroundColor": theme.get_color("background"),
        "borderWidth": 0
    })
    
    # Common text styles
    theme.register_style("common.title", {
        "color": theme.get_color("text"),
        "fontSize": 36,
        "fontWeight": "bold"
    })
    
    theme.register_style("common.subtitle", {
        "color": theme.get_color("text_secondary"),
        "fontSize": 24
    })
    
    theme.register_style("common.instruction", {
        "color": theme.get_color("text_secondary"),
        "fontSize": 18
    })
    
    # Common button styles
    theme.register_style("common.button", {
        "backgroundColor": theme.get_color("primary"),
        "borderWidth": 0,
        "borderRadius": theme.get_border_radius("medium")
    })
    
    theme.register_style("common.button_text", {
        "color": theme.get_color("text"),
        "fontSize": 22,
        "fontWeight": "bold"
    })
    
    theme.register_style("common.button_description", {
        "color": theme.get_color("text"),
        "fontSize": 16
    })


def _register_symbol_memory_styles(theme: Theme) -> None:
    """Register styles for the Symbol Memory module.
    
    Args:
        theme: The theme to register styles for
    """
    # Container styles
    theme.register_style("symbol_memory.container", {
        "backgroundColor": theme.get_color("card"),
        "borderWidth": 2,
        "borderColor": theme.get_color("border"),
        "borderRadius": theme.get_border_radius("large")
    })
    
    # Title and instructions
    theme.register_style("symbol_memory.title", {
        "color": theme.get_color("text"),
        "fontSize": 32,
        "fontWeight": "bold"
    })
    
    theme.register_style("symbol_memory.instruction", {
        "color": theme.get_color("text_secondary"),
        "fontSize": 20
    })
    
    # Grid and symbols
    theme.register_style("symbol_memory.grid", {
        "backgroundColor": theme.get_color("surface"),
        "borderWidth": 2,
        "borderColor": theme.get_color("border"),
        "borderRadius": theme.get_border_radius("medium")
    })
    
    theme.register_style("symbol_memory.symbol", {
        "backgroundColor": theme.get_color("surface"),
        "borderWidth": 1,
        "borderColor": theme.get_color("border"),
        "borderRadius": theme.get_border_radius("small"),
        "color": theme.get_color("text"),
        "fontSize": 24
    })
    
    # Symbol states
    theme.register_style("symbol_memory.symbol.selected", {
        "backgroundColor": theme.get_color("primary"),
        "borderWidth": 1,
        "borderColor": theme.get_color("primary_hover"),
        "borderRadius": theme.get_border_radius("small"),
        "color": theme.get_color("text"),
        "fontSize": 24
    })
    
    theme.register_style("symbol_memory.symbol.correct", {
        "backgroundColor": theme.get_color("success"),
        "borderWidth": 1,
        "borderColor": theme.get_color("success"),
        "borderRadius": theme.get_border_radius("small"),
        "color": theme.get_color("text"),
        "fontSize": 24
    })
    
    theme.register_style("symbol_memory.symbol.incorrect", {
        "backgroundColor": theme.get_color("error"),
        "borderWidth": 1,
        "borderColor": theme.get_color("error"),
        "borderRadius": theme.get_border_radius("small"),
        "color": theme.get_color("text"),
        "fontSize": 24
    })
    
    theme.register_style("symbol_memory.symbol.hidden", {
        "backgroundColor": theme.get_color("surface"),
        "borderWidth": 1,
        "borderColor": theme.get_color("border"),
        "borderRadius": theme.get_border_radius("small"),
        "color": theme.get_color("surface"),  # Hide text by matching background
        "fontSize": 24
    })
    
    # Progress and score
    theme.register_style("symbol_memory.progress", {
        "backgroundColor": theme.get_color("surface"),
        "borderWidth": 0,
        "borderRadius": theme.get_border_radius("small")
    })
    
    theme.register_style("symbol_memory.progress.fill", {
        "backgroundColor": theme.get_color("primary"),
        "borderWidth": 0,
        "borderRadius": theme.get_border_radius("small")
    })
    
    theme.register_style("symbol_memory.score", {
        "color": theme.get_color("text_secondary"),
        "fontSize": 18
    })
    
    # Feedback styles
    theme.register_style("symbol_memory.feedback.correct", {
        "color": theme.get_color("success"),
        "fontSize": 32,
        "fontWeight": "bold"
    })
    
    theme.register_style("symbol_memory.feedback.incorrect", {
        "color": theme.get_color("error"),
        "fontSize": 32,
        "fontWeight": "bold"
    })


def _register_morph_matrix_styles(theme: Theme) -> None:
    """Register styles for the Morph Matrix module.
    
    Args:
        theme: The theme to register styles for
    """
    # Container styles
    theme.register_style("morph_matrix.container", {
        "backgroundColor": theme.get_color("card"),
        "borderWidth": 2,
        "borderColor": theme.get_color("border"),
        "borderRadius": theme.get_border_radius("large")
    })
    
    # Title and instructions
    theme.register_style("morph_matrix.title", {
        "color": theme.get_color("text"),
        "fontSize": 32,
        "fontWeight": "bold"
    })
    
    theme.register_style("morph_matrix.instruction", {
        "color": theme.get_color("text_secondary"),
        "fontSize": 20
    })
    
    # Matrix styles
    theme.register_style("morph_matrix.matrix", {
        "backgroundColor": theme.get_color("surface"),
        "borderWidth": 2,
        "borderColor": theme.get_color("primary"),
        "borderRadius": theme.get_border_radius("medium")
    })
    
    # Cell styles
    theme.register_style("morph_matrix.cell.filled", {
        "backgroundColor": theme.get_color("primary"),
        "borderWidth": 1,
        "borderColor": theme.get_color("primary_hover"),
        "borderRadius": theme.get_border_radius("small")
    })
    
    theme.register_style("morph_matrix.cell.empty", {
        "backgroundColor": theme.get_color("surface"),
        "borderWidth": 1,
        "borderColor": theme.get_color("border"),
        "borderRadius": theme.get_border_radius("small")
    })
    
    # Options container
    theme.register_style("morph_matrix.options_container", {
        "backgroundColor": theme.get_color("surface"),
        "borderWidth": 2,
        "borderColor": theme.get_color("border"),
        "borderRadius": theme.get_border_radius("medium")
    })
    
    # Option styles
    theme.register_style("morph_matrix.option", {
        "backgroundColor": theme.get_color("surface"),
        "borderWidth": 2,
        "borderColor": theme.get_color("border"),
        "borderRadius": theme.get_border_radius("small")
    })
    
    theme.register_style("morph_matrix.option.selected", {
        "backgroundColor": theme.get_color("surface"),
        "borderWidth": 2,
        "borderColor": theme.get_color("primary"),
        "borderRadius": theme.get_border_radius("small")
    })
    
    theme.register_style("morph_matrix.option.correct", {
        "backgroundColor": theme.get_color("surface"),
        "borderWidth": 2,
        "borderColor": theme.get_color("success"),
        "borderRadius": theme.get_border_radius("small")
    })
    
    theme.register_style("morph_matrix.option.incorrect", {
        "backgroundColor": theme.get_color("surface"),
        "borderWidth": 2,
        "borderColor": theme.get_color("error"),
        "borderRadius": theme.get_border_radius("small")
    })
    
    theme.register_style("morph_matrix.option.missed", {
        "backgroundColor": theme.get_color("surface"),
        "borderWidth": 2,
        "borderColor": theme.get_color("warning"),
        "borderRadius": theme.get_border_radius("small")
    })
    
    theme.register_style("morph_matrix.option_label", {
        "color": theme.get_color("text"),
        "fontSize": 16
    })
    
    # Score styles
    theme.register_style("morph_matrix.score", {
        "color": theme.get_color("text_secondary"),
        "fontSize": 18
    })
    
    # Feedback styles
    theme.register_style("morph_matrix.feedback.correct", {
        "color": theme.get_color("success"),
        "fontSize": 28,
        "fontWeight": "bold"
    })
    
    theme.register_style("morph_matrix.feedback.incorrect", {
        "color": theme.get_color("error"),
        "fontSize": 28,
        "fontWeight": "bold"
    })
    
    theme.register_style("morph_matrix.feedback.partial", {
        "color": theme.get_color("warning"),
        "fontSize": 28,
        "fontWeight": "bold"
    })


def _register_expand_vision_styles(theme: Theme) -> None:
    """Register styles for the Expand Vision module.
    
    Args:
        theme: The theme to register styles for
    """
    # Container styles
    theme.register_style("expand_vision.container", {
        "backgroundColor": theme.get_color("background"),
        "borderWidth": 0
    })
    
    # Title and instructions
    theme.register_style("expand_vision.title", {
        "color": theme.get_color("text"),
        "fontSize": 32,
        "fontWeight": "bold"
    })
    
    theme.register_style("expand_vision.instruction", {
        "color": theme.get_color("text_secondary"),
        "fontSize": 20
    })
    
    theme.register_style("expand_vision.info", {
        "color": theme.get_color("text_secondary"),
        "fontSize": 18
    })
    
    # Field styles
    theme.register_style("expand_vision.field", {
        "backgroundColor": theme.get_color("card"),
        "borderWidth": 2,
        "borderColor": theme.get_color("border"),
        "borderRadius": theme.get_border_radius("large")
    })
    
    # Expanding circle
    theme.register_style("expand_vision.expanding_circle", {
        "backgroundColor": theme.get_color("primary_hover"),
        "borderWidth": 0,
        "opacity": 0.3
    })
    
    # Center circle
    theme.register_style("expand_vision.center_circle", {
        "backgroundColor": theme.get_color("primary"),
        "borderWidth": 2,
        "borderColor": theme.get_color("border")
    })
    
    # Number elements
    theme.register_style("expand_vision.element", {
        "backgroundColor": theme.get_color("card"),
        "borderWidth": 2,
        "borderColor": theme.get_color("border")
    })
    
    theme.register_style("expand_vision.element_text", {
        "color": theme.get_color("text"),
        "fontSize": 24,
        "fontWeight": "bold"
    })
    
    # Timer styles
    theme.register_style("expand_vision.timer_bg", {
        "backgroundColor": theme.get_color("surface"),
        "borderWidth": 0,
        "borderRadius": theme.get_border_radius("small")
    })
    
    theme.register_style("expand_vision.timer_fill", {
        "backgroundColor": theme.get_color("warning"),
        "borderWidth": 0,
        "borderRadius": theme.get_border_radius("small")
    })
    
    # Button styles
    theme.register_style("expand_vision.button", {
        "backgroundColor": theme.get_color("primary"),
        "borderWidth": 0,
        "borderRadius": theme.get_border_radius("medium")
    })
    
    theme.register_style("expand_vision.button_text", {
        "color": theme.get_color("text"),
        "fontSize": 22,
        "fontWeight": "bold"
    })
    
    # Answer styles
    theme.register_style("expand_vision.question", {
        "color": theme.get_color("text"),
        "fontSize": 28
    })
    
    theme.register_style("expand_vision.answer", {
        "color": theme.get_color("text"),
        "fontSize": 48,
        "fontWeight": "bold"
    })
    
    # Score styles
    theme.register_style("expand_vision.score", {
        "color": theme.get_color("text_secondary"),
        "fontSize": 18
    })
    
    # Feedback styles
    theme.register_style("expand_vision.feedback.correct", {
        "color": theme.get_color("success"),
        "fontSize": 32,
        "fontWeight": "bold"
    })
    
    theme.register_style("expand_vision.feedback.incorrect", {
        "color": theme.get_color("error"),
        "fontSize": 32,
        "fontWeight": "bold"
    }) 