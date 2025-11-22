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
import pygame
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional

# Add the parent directory to sys.path for absolute imports when imported directly
if __name__ == "__main__" or not __package__:
    project_root = Path(__file__).parent.parent.parent.parent
    sys.path.insert(0, str(project_root))
    from MetaMindIQTrain.core.theme_manager import ThemeManager
    from MetaMindIQTrain.core.config import config
else:
    # Use relative imports when imported as a module
    from ....core.theme_manager import ThemeManager
    from ....core.config import config


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
        for i, path in enumerate(self.model.target_nodes):
            if i < len(self.model.target_nodes) - 1:
                start = path["position"]
                end = self.model.target_nodes[i + 1]["position"]
                
                # Draw path
                pygame.draw.line(
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
            pygame.draw.circle(
                renderer.screen,
                color,
                node["position"],
                node["radius"]
            )
            
            # Draw node border
            pygame.draw.circle(
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