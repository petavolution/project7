#!/usr/bin/env python3
"""
Neural Flow View Component

This module handles the UI representation for the Neural Flow training module:
- Layout calculations based on screen dimensions
- Component tree building for rendering
- Visual representation of the neural network
- Theme-aware styling
"""

import math
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional

# Lazy import for pygame - only load if actually needed for pygame-specific rendering
pygame = None
def _get_pygame():
    """Lazy load pygame only when needed."""
    global pygame
    if pygame is None:
        try:
            import pygame as _pygame
            pygame = _pygame
        except ImportError:
            pass
    return pygame

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

# Import config
try:
    from core.config import config
except ImportError:
    try:
        from config import config
    except ImportError:
        # Minimal fallback config
        class config:
            UI_THEME = {"colors": {}, "layouts": {"neural_flow": {"node_radius": 2, "node_padding": 3, "path_thickness": 1}}}
            MODULE_SETTINGS = {"neural_flow": {"visual_scale": 1.0}}


class NeuralFlowView:
    """View component for NeuralFlow module - handles UI representation."""
    
    def __init__(self, model):
        """Initialize the view with reference to the model.
        
        Args:
            model: NeuralFlowModel instance
        """
        self.model = model
        self.screen_width = 800  # Default width
        self.screen_height = 600  # Default height
        
        # Neural network visualization properties
        self.node_radius = 12
        self.node_padding = 20
        self.path_thickness = 2
        
        # UI element references
        self.node_rects = {}  # Rectangles for nodes
        self.path_rects = {}  # Rectangles for paths
    
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
        """Calculate layout based on screen dimensions."""
        # Get theme styling for neural flow
        theme = config.UI_THEME
        neural_layout = theme["layouts"]["neural_flow"]
        
        # Get module-specific settings including scaling factor
        module_settings = config.MODULE_SETTINGS["neural_flow"]
        visual_scale = module_settings.get("visual_scale", 1.0)  # Default to 1.0 if not specified
        
        # Calculate content area dimensions
        content_width = self.screen_width
        content_height = int(self.screen_height * 0.7)  # 70% of screen height
        content_y = int(self.screen_height * 0.15)  # 15% from top
        
        # Calculate node radius and padding based on screen size
        self.node_radius = int(min(content_width, content_height) * neural_layout["node_radius"] / 100 * visual_scale)
        self.node_padding = int(min(content_width, content_height) * neural_layout["node_padding"] / 100 * visual_scale)
        self.path_thickness = int(min(content_width, content_height) * neural_layout["path_thickness"] / 100 * visual_scale)
    
    def build_component_tree(self):
        """Build a component tree for rendering.
        
        Returns:
            Root component of the UI tree
        """
        # Root container
        root = {
            "type": "container",
            "id": "neural_flow_root",
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
                            "text": "Neural Flow - Cognitive Enhancement",
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
                
                # Instructions/Message
                {
                    "type": "text",
                    "id": "instructions",
                    "x": 20,
                    "y": 60,
                    "width": self.screen_width - 40,
                    "height": 30,
                    "text": self.model.message,
                    "properties": {
                        "style": {
                            "color": ThemeManager.get_color("text_color"),
                            "textAlign": "center"
                        }
                    }
                },
                
                # Neural network visualization
                {
                    "type": "container",
                    "id": "neural_network",
                    "x": 0,
                    "y": 100,
                    "width": self.screen_width,
                    "height": self.screen_height - 200,
                    "properties": {
                        "style": {
                            "backgroundColor": ThemeManager.get_color("card_bg"),
                            "borderColor": ThemeManager.get_color("border_color"),
                            "borderWidth": 2,
                            "borderRadius": 5
                        }
                    },
                    "children": self._create_neural_network_components()
                },
                
                # Status bar
                {
                    "type": "container",
                    "id": "status_bar",
                    "x": 0,
                    "y": self.screen_height - 100,
                    "width": self.screen_width,
                    "height": 100,
                    "properties": {
                        "style": {
                            "backgroundColor": ThemeManager.get_color("card_bg")
                        }
                    },
                    "children": self._create_status_components()
                }
            ]
        }
        
        return root
    
    def _create_neural_network_components(self):
        """Create component specs for neural network visualization.
        
        Returns:
            List of component specifications
        """
        components = []
        
        # Draw paths first (so they appear behind nodes)
        for i, path in enumerate(self.model.target_nodes):
            if i < len(self.model.target_nodes) - 1:
                start = path["position"]
                end = self.model.target_nodes[i + 1]["position"]
                
                # Create path component
                path_component = {
                    "type": "line",
                    "id": f"path_{i}",
                    "x1": start[0],
                    "y1": start[1],
                    "x2": end[0],
                    "y2": end[1],
                    "properties": {
                        "style": {
                            "strokeColor": ThemeManager.get_color("neural_path"),
                            "strokeWidth": self.path_thickness
                        }
                    }
                }
                components.append(path_component)
        
        # Draw nodes
        for i, node in enumerate(self.model.target_nodes):
            # Determine node color based on state
            if node in self.model.success_nodes:
                color = ThemeManager.get_color("success_node")
            elif node in self.model.error_nodes:
                color = ThemeManager.get_color("error_node")
            elif node in self.model.active_nodes:
                color = ThemeManager.get_color("neural_active")
            else:
                color = ThemeManager.get_color("neural_node")
            
            # Create node component
            node_component = {
                "type": "circle",
                "id": f"node_{i}",
                "x": node["position"][0],
                "y": node["position"][1],
                "radius": node["radius"],
                "properties": {
                    "style": {
                        "fillColor": color,
                        "strokeColor": ThemeManager.get_color("border_color"),
                        "strokeWidth": 2
                    }
                }
            }
            components.append(node_component)
        
        return components
    
    def _create_status_components(self):
        """Create component specs for status bar.
        
        Returns:
            List of component specifications
        """
        components = []
        
        # Level indicator
        components.append({
            "type": "text",
            "id": "level",
            "x": 20,
            "y": 20,
            "width": 100,
            "height": 30,
            "text": f"Level: {self.model.level}",
            "properties": {
                "style": {
                    "color": ThemeManager.get_color("text_color"),
                    "fontSize": 16
                }
            }
        })
        
        # Progress indicator
        if self.model.phase == self.model.PHASE_ACTIVE:
            progress_text = f"Nodes: {self.model.targets_found}/{len(self.model.target_nodes)}"
        else:
            progress_text = f"Accuracy: {self.model.accuracy:.0%}"
        
        components.append({
            "type": "text",
            "id": "progress",
            "x": self.screen_width // 2 - 100,
            "y": 20,
            "width": 200,
            "height": 30,
            "text": progress_text,
            "properties": {
                "style": {
                    "color": ThemeManager.get_color("text_color"),
                    "fontSize": 16,
                    "textAlign": "center"
                }
            }
        })
        
        # Phase indicator
        components.append({
            "type": "text",
            "id": "phase",
            "x": self.screen_width - 120,
            "y": 20,
            "width": 100,
            "height": 30,
            "text": f"Phase: {self.model.phase.capitalize()}",
            "properties": {
                "style": {
                    "color": ThemeManager.get_color("text_color"),
                    "fontSize": 16,
                    "textAlign": "right"
                }
            }
        })
        
        return components
    
    def render(self, renderer):
        """Render the neural network visualization.
        
        Args:
            renderer: UIRenderer instance
        """
        # Get theme styling
        theme = config.UI_THEME
        
        # Get module-specific settings including scaling factor
        module_settings = config.MODULE_SETTINGS["neural_flow"]
        visual_scale = module_settings.get("visual_scale", 1.0)  # Default to 1.0 if not specified
        
        # Draw paths first (so they appear behind nodes)
        pg = _get_pygame()
        if not pg or not hasattr(renderer, 'screen'):
            # If pygame not available or not a pygame renderer, skip pygame-specific rendering
            return

        for i, path in enumerate(self.model.target_nodes):
            if i < len(self.model.target_nodes) - 1:
                start = path["position"]
                end = self.model.target_nodes[i + 1]["position"]

                # Draw path
                pg.draw.line(
                    renderer.screen,
                    theme["colors"]["neural_path"],
                    start,
                    end,
                    self.path_thickness
                )

        # Draw nodes
        for i, node in enumerate(self.model.target_nodes):
            # Determine node color based on state
            if node in self.model.success_nodes:
                color = theme["colors"]["success_node"]
            elif node in self.model.error_nodes:
                color = theme["colors"]["error_node"]
            elif node in self.model.active_nodes:
                color = theme["colors"]["neural_active"]
            else:
                color = theme["colors"]["neural_node"]

            # Draw node
            pg.draw.circle(
                renderer.screen,
                color,
                node["position"],
                node["radius"]
            )

            # Draw node border
            pg.draw.circle(
                renderer.screen,
                theme["colors"]["border_color"],
                node["position"],
                node["radius"],
                2
            )
    
    def render_status(self, renderer):
        """Render status information.
        
        Args:
            renderer: UIRenderer instance
        """
        # Get theme styling
        theme = config.UI_THEME
        
        # Draw level
        level_text = f"Level: {self.model.level}"
        level_font = renderer.fonts["medium"]
        level_surf = level_font.render(level_text, True, theme["colors"]["text"])
        renderer.screen.blit(level_surf, (20, self.screen_height - 80))
        
        # Draw progress
        if self.model.phase == self.model.PHASE_ACTIVE:
            progress_text = f"Nodes: {self.model.targets_found}/{len(self.model.target_nodes)}"
        else:
            progress_text = f"Accuracy: {self.model.accuracy:.0%}"
        
        progress_font = renderer.fonts["medium"]
        progress_surf = progress_font.render(progress_text, True, theme["colors"]["text"])
        progress_rect = progress_surf.get_rect(center=(self.screen_width // 2, self.screen_height - 80))
        renderer.screen.blit(progress_surf, progress_rect)
        
        # Draw phase
        phase_text = f"Phase: {self.model.phase.capitalize()}"
        phase_font = renderer.fonts["medium"]
        phase_surf = phase_font.render(phase_text, True, theme["colors"]["text"])
        phase_rect = phase_surf.get_rect(topright=(self.screen_width - 20, self.screen_height - 80))
        renderer.screen.blit(phase_surf, phase_rect)

    def render_to_renderer(self, renderer, model):
        """Render the view using the renderer abstraction.

        This method uses the renderer's drawing API instead of pygame directly,
        allowing for headless rendering and different backend support.

        Args:
            renderer: The renderer instance with drawing methods
            model: The model containing game state
        """
        # Get theme colors with defaults
        bg_color = (20, 25, 31)
        card_bg = (30, 36, 44)
        text_color = (240, 240, 240)
        primary_color = (0, 120, 255)
        success_color = (50, 255, 80)
        error_color = (255, 50, 50)
        border_color = (60, 70, 80)
        neural_node = (80, 100, 140)
        neural_active = (100, 200, 255)
        neural_path = (50, 60, 80)

        try:
            theme = config.UI_THEME
            if theme and "colors" in theme:
                colors = theme["colors"]
                bg_color = colors.get("bg_color", bg_color)
                card_bg = colors.get("card_bg", card_bg)
                text_color = colors.get("text", text_color)
                primary_color = colors.get("primary", primary_color)
                success_color = colors.get("success_node", success_color)
                error_color = colors.get("error_node", error_color)
                border_color = colors.get("border_color", border_color)
                neural_node = colors.get("neural_node", neural_node)
                neural_active = colors.get("neural_active", neural_active)
                neural_path = colors.get("neural_path", neural_path)
        except Exception:
            pass

        # Clear with background color
        renderer.clear((*bg_color, 255))

        # Draw header background
        header_height = 60
        renderer.draw_rectangle(0, 0, self.screen_width, header_height, (*card_bg, 255))

        # Draw title
        renderer.draw_text(
            self.screen_width // 2, 20,
            "Neural Flow - Path Training",
            font_size=20,
            color=(*text_color, 255),
            align="center"
        )

        # Draw score and level
        score = model.score if hasattr(model, 'score') else 0
        level = model.level if hasattr(model, 'level') else 1
        renderer.draw_text(
            self.screen_width - 30, 20,
            f"Score: {score}",
            font_size=16,
            color=(*text_color, 255),
            align="right"
        )
        renderer.draw_text(
            30, 20,
            f"Level: {level}",
            font_size=16,
            color=(*text_color, 255),
            align="left"
        )

        # Draw paths between nodes
        target_nodes = model.target_nodes if hasattr(model, 'target_nodes') else []
        for i in range(len(target_nodes) - 1):
            if i < len(target_nodes) - 1:
                start = target_nodes[i].get("position", (0, 0))
                end = target_nodes[i + 1].get("position", (0, 0))
                renderer.draw_line(
                    start[0], start[1],
                    end[0], end[1],
                    (*neural_path, 255),
                    width=self.path_thickness
                )

        # Draw nodes
        success_nodes = model.success_nodes if hasattr(model, 'success_nodes') else []
        error_nodes = model.error_nodes if hasattr(model, 'error_nodes') else []
        active_nodes = model.active_nodes if hasattr(model, 'active_nodes') else []

        for node in target_nodes:
            pos = node.get("position", (0, 0))
            radius = node.get("radius", self.node_radius)

            # Determine node color based on state
            if node in success_nodes:
                color = success_color
            elif node in error_nodes:
                color = error_color
            elif node in active_nodes:
                color = neural_active
            else:
                color = neural_node

            # Draw filled node
            renderer.draw_circle(pos[0], pos[1], radius, (*color, 255))
            # Draw node border
            renderer.draw_circle(pos[0], pos[1], radius, (*border_color, 255), filled=False)

        # Draw phase indicator
        phase = model.phase if hasattr(model, 'phase') else 'waiting'
        phase_text = f"Phase: {phase.capitalize()}"
        renderer.draw_text(
            self.screen_width // 2, header_height + 10,
            phase_text,
            font_size=14,
            color=(*text_color, 255),
            align="center"
        )

        # Draw progress at bottom
        targets_found = model.targets_found if hasattr(model, 'targets_found') else 0
        total_targets = len(target_nodes)
        progress_text = f"Nodes: {targets_found}/{total_targets}"
        renderer.draw_text(
            self.screen_width // 2, self.screen_height - 40,
            progress_text,
            font_size=16,
            color=(*text_color, 255),
            align="center"
        )

        # Draw message if any
        message = model.message if hasattr(model, 'message') else ""
        if message:
            renderer.draw_text(
                self.screen_width // 2, self.screen_height - 70,
                message,
                font_size=14,
                color=(*primary_color, 255),
                align="center"
            ) 