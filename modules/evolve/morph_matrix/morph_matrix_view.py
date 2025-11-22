#!/usr/bin/env python3
"""
MorphMatrix View Component

This module handles the UI representation for the MorphMatrix training module:
- Layout calculations based on screen dimensions
- Component tree building for rendering
- Visual representation of matrix patterns
- Theme-aware styling
"""

import math
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional

# Ensure project root is in path
_project_root = Path(__file__).resolve().parent.parent.parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

# Import theme manager - try multiple approaches
try:
    from core.theme_manager import ThemeManager
except ImportError:
    try:
        from core.theme import Theme as ThemeManager
    except ImportError:
        ThemeManager = None


class MorphMatrixView:
    """View component for MorphMatrix module - handles UI representation."""
    
    def __init__(self, model):
        """Initialize the view with reference to the model.
        
        Args:
            model: MorphMatrixModel instance
        """
        self.model = model
        self.screen_width = 800  # Default width
        self.screen_height = 600  # Default height
        
        # Grid layout properties
        self.grid_columns = 3
        self.grid_rows = 2
        self.cell_size = 30  # Will be adjusted based on matrix size
        self.pattern_margin = 20
        self.pattern_padding = 10
        
        # UI element references
        self.pattern_rects = []  # Rectangles for hit testing
        self.ui_components = []  # For component-based rendering
    
    def set_dimensions(self, width, height):
        """Set the screen dimensions.
        
        Args:
            width: Screen width
            height: Screen height
        """
        self.screen_width = width
        self.screen_height = height
        self.calculate_layout()
    
    def calculate_layout(self):
        """Calculate layout based on screen dimensions and matrix size."""
        # Calculate optimal cell size based on screen and matrix size
        matrix_size = self.model.matrix_size
        
        # Calculate pattern dimensions (each pattern is a container with a matrix)
        max_patterns_per_row = 3
        pattern_width = min(
            (self.screen_width - (max_patterns_per_row + 1) * self.pattern_margin) // max_patterns_per_row,
            (self.screen_height - 200) // 2  # Allow space for UI elements
        )
        
        # Max width 1/3 of screen, maintaining square aspect ratio
        pattern_width = min(pattern_width, self.screen_width // 3)
        pattern_height = pattern_width
        
        # Calculate cell size based on pattern size and matrix size
        available_size = pattern_width - 2 * self.pattern_padding
        self.cell_size = available_size // matrix_size
        
        # Calculate positions for patterns
        self.pattern_rects = []
        patterns_per_row = min(max_patterns_per_row, len(self.model.clusters))
        rows = math.ceil(len(self.model.clusters) / patterns_per_row)
        
        # Center the grid
        grid_width = patterns_per_row * pattern_width + (patterns_per_row - 1) * self.pattern_margin
        grid_height = rows * pattern_height + (rows - 1) * self.pattern_margin
        start_x = (self.screen_width - grid_width) // 2
        start_y = (self.screen_height - grid_height - 100) // 2 + 50  # Space for header
        
        # Calculate positions for each pattern
        for i, cluster in enumerate(self.model.clusters):
            row = i // patterns_per_row
            col = i % patterns_per_row
            
            x = start_x + col * (pattern_width + self.pattern_margin)
            y = start_y + row * (pattern_height + self.pattern_margin)
            
            # Store position in cluster
            cluster["position"] = (x, y)
            self.pattern_rects.append((x, y, pattern_width, pattern_height, i))
    
    def build_component_tree(self):
        """Build a component tree for rendering.
        
        This example uses a component-based approach with a hypothetical UI
        component system. Implement according to your actual UI component system.
        
        Returns:
            Root component of the UI tree
        """
        # Assuming a UI component system like described in ui_component.py
        # Depending on the actual implementation, you would create the
        # specific component instances here
        
        # For now, this is a placeholder that returns component specs
        # that would be used to create actual components
        
        # Root container
        root = {
            "type": "container",
            "id": "morph_matrix_root",
            "width": self.screen_width,
            "height": self.screen_height,
            "properties": {
                "style": {
                    "backgroundColor": ThemeManager.get_color("bg_color")
                }
            },
            "children": [
                # Header
                {
                    "type": "container",
                    "id": "header",
                    "x": 0,
                    "y": 0,
                    "width": self.screen_width,
                    "height": 50,
                    "properties": {
                        "style": {
                            "backgroundColor": ThemeManager.get_color("card_bg")
                        }
                    },
                    "children": [
                        # Title
                        {
                            "type": "text",
                            "id": "title",
                            "x": 20,
                            "y": 10,
                            "width": 300,
                            "height": 30,
                            "text": "MorphMatrix - Pattern Recognition",
                            "properties": {
                                "style": {
                                    "color": ThemeManager.get_color("text_color"),
                                    "fontSize": 18
                                }
                            }
                        },
                        # Score
                        {
                            "type": "text",
                            "id": "score",
                            "x": self.screen_width - 150,
                            "y": 10,
                            "width": 130,
                            "height": 30,
                            "text": f"Score: {self.model.score}",
                            "properties": {
                                "style": {
                                    "color": ThemeManager.get_color("text_color"),
                                    "textAlign": "right",
                                    "fontSize": 18
                                }
                            }
                        }
                    ]
                },
                
                # Instructions
                {
                    "type": "text",
                    "id": "instructions",
                    "x": 20,
                    "y": 60,
                    "width": self.screen_width - 40,
                    "height": 30,
                    "text": "Select all patterns that are rotations of the original pattern (blue outline).",
                    "properties": {
                        "style": {
                            "color": ThemeManager.get_color("text_color"),
                            "textAlign": "center"
                        }
                    }
                },
                
                # Pattern grid
                {
                    "type": "container",
                    "id": "pattern_grid",
                    "x": 0,
                    "y": 100,
                    "width": self.screen_width,
                    "height": self.screen_height - 150,
                    "children": self._create_pattern_components()
                },
                
                # Button container
                {
                    "type": "container",
                    "id": "button_container",
                    "x": 0,
                    "y": self.screen_height - 50,
                    "width": self.screen_width,
                    "height": 50,
                    "children": [
                        # Submit button
                        {
                            "type": "button",
                            "id": "submit_button",
                            "x": (self.screen_width - 120) // 2,
                            "y": 5,
                            "width": 120,
                            "height": 40,
                            "text": "Submit",
                            "properties": {
                                "style": {
                                    "backgroundColor": ThemeManager.get_color("primary_color"),
                                    "color": ThemeManager.get_color("text_color"),
                                    "borderRadius": 5
                                }
                            }
                        }
                    ] if self.model.game_state == "challenge_active" else [
                        # Next button (for challenge_complete state)
                        {
                            "type": "button",
                            "id": "next_button",
                            "x": (self.screen_width - 120) // 2,
                            "y": 5,
                            "width": 120,
                            "height": 40,
                            "text": "Next Challenge",
                            "properties": {
                                "style": {
                                    "backgroundColor": ThemeManager.get_color("primary_color"),
                                    "color": ThemeManager.get_color("text_color"),
                                    "borderRadius": 5
                                }
                            }
                        }
                    ]
                }
            ]
        }
        
        return root
    
    def _create_pattern_components(self):
        """Create component specs for patterns.
        
        Returns:
            List of pattern component specifications
        """
        patterns = []
        
        for i, cluster in enumerate(self.model.clusters):
            x, y = cluster["position"]
            width = height = self.pattern_rects[i][2]  # Use width from rect
            
            # Determine border color and width
            border_color = ThemeManager.get_color("primary_color") if i == 0 else ThemeManager.get_color("border_color")
            border_width = 3 if i == 0 else 1
            
            if cluster["selected"]:
                border_color = ThemeManager.get_color("accent_color")
                border_width = 2
            
            # Background color based on state
            bg_color = ThemeManager.get_color("card_bg")
            if self.model.answered:
                if i in self.model.modified_indices:
                    # Should not have been selected
                    bg_color = ThemeManager.get_color("error_color") if i in self.model.selected_patterns else bg_color
                else:
                    # Should have been selected
                    bg_color = ThemeManager.get_color("success_color") if i in self.model.selected_patterns else ThemeManager.get_color("error_color")
            
            # Create pattern container
            pattern = {
                "type": "container",
                "id": f"pattern_{i}",
                "x": x,
                "y": y,
                "width": width,
                "height": height,
                "properties": {
                    "style": {
                        "backgroundColor": bg_color,
                        "borderColor": border_color,
                        "borderWidth": border_width,
                        "borderRadius": 5
                    }
                },
                "children": self._create_matrix_cells(cluster["matrix"], x, y, width, height)
            }
            
            patterns.append(pattern)
        
        return patterns
    
    def _create_matrix_cells(self, matrix, pattern_x, pattern_y, pattern_width, pattern_height):
        """Create component specs for matrix cells.
        
        Args:
            matrix: Binary matrix data
            pattern_x: Pattern container X position
            pattern_y: Pattern container Y position
            pattern_width: Pattern container width
            pattern_height: Pattern container height
            
        Returns:
            List of cell component specifications
        """
        cells = []
        matrix_size = len(matrix)
        
        # Calculate cell size from pattern dimensions
        available_size = min(pattern_width, pattern_height) - 2 * self.pattern_padding
        cell_size = available_size // matrix_size
        
        # Calculate start position (center matrix in pattern)
        start_x = (pattern_width - (matrix_size * cell_size)) // 2
        start_y = (pattern_height - (matrix_size * cell_size)) // 2
        
        for row in range(matrix_size):
            for col in range(matrix_size):
                cell_x = start_x + col * cell_size
                cell_y = start_y + row * cell_size
                
                # Filled or empty?
                filled = matrix[row][col] == 1
                
                cell = {
                    "type": "container",
                    "id": f"cell_{row}_{col}",
                    "x": cell_x,
                    "y": cell_y,
                    "width": cell_size,
                    "height": cell_size,
                    "properties": {
                        "style": {
                            "backgroundColor": ThemeManager.get_color("accent_color") if filled else ThemeManager.get_color("card_hover"),
                            "borderColor": ThemeManager.get_color("border_color"),
                            "borderWidth": 1
                        }
                    }
                }
                
                cells.append(cell)
        
        return cells 