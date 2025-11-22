#!/usr/bin/env python3
"""
Synesthetic Training View Component

This module handles the UI representation for the Synesthetic Training module:
- Layout calculations based on screen dimensions
- Component tree building for rendering
- Visual representation of cross-sensory associations
- Theme-aware styling
"""

import sys
import math
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional

# Add the parent directory to sys.path for absolute imports when imported directly
if __name__ == "__main__" or not __package__:
    project_root = Path(__file__).parent.parent.parent.parent
    sys.path.insert(0, str(project_root))
    from MetaMindIQTrain.core.theme_manager import ThemeManager
else:
    # Use relative imports when imported as a module
    from ....core.theme_manager import ThemeManager


class SynestheticTrainingView:
    """View component for Synesthetic Training module - handles UI representation."""
    
    def __init__(self, model):
        """Initialize the view with reference to the model.
        
        Args:
            model: Synesthetic Training Model instance
        """
        self.model = model
        self.screen_width = 800  # Default width
        self.screen_height = 600  # Default height
        
    def set_dimensions(self, width, height):
        """Set the screen dimensions.
        
        Args:
            width: Screen width
            height: Screen height
        """
        self.screen_width = width
        self.screen_height = height
    
    def build_component_tree(self):
        """Build a component tree for rendering.
        
        Returns:
            Dict containing the UI component tree
        """
        # Root container
        root = {
            "type": "container",
            "id": "synesthetic_training_root",
            "width": self.screen_width,
            "height": self.screen_height,
            "properties": {
                "style": {
                    "backgroundColor": ThemeManager.get_color("bg_color")
                }
            },
            "children": [
                # Header
                self._build_header(),
                
                # Status bar
                self._build_status_bar(),
                
                # Main content area
                self._build_content_area()
            ]
        }
        
        return root
    
    def _build_header(self):
        """Build the header component.
        
        Returns:
            Dict representing the header component
        """
        return {
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
                    "text": "Synesthetic Training",
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
        }
    
    def _build_status_bar(self):
        """Build the status bar component.
        
        Returns:
            Dict representing the status bar component
        """
        # Message
        message = self.model.message
        
        # Level and trial info
        level_info = f"Level: {self.model.level}   Trial: {self.model.current_trial + 1}"
        
        # Timer for association and recall phases
        phase_time = 0
        remaining = 0
        progress = 0
        
        if self.model.phase in ["association", "recall"]:
            phase_time = self.model.config[f"{self.model.phase}_time"]
            remaining = max(0, phase_time - self.model.elapsed_time)
            progress = 1.0 - (remaining / phase_time)
        
        # Create children components
        children = [
            # Message
            {
                "type": "text",
                "id": "message",
                "x": self.screen_width // 2,
                "y": 60,
                "width": self.screen_width - 40,
                "height": 30,
                "text": message,
                "properties": {
                    "style": {
                        "color": ThemeManager.get_color("highlight_color"),
                        "textAlign": "center",
                        "fontSize": 16
                    }
                }
            },
            
            # Level and trial info
            {
                "type": "text",
                "id": "level_info",
                "x": self.screen_width // 2,
                "y": 85,
                "width": self.screen_width - 40,
                "height": 20,
                "text": level_info,
                "properties": {
                    "style": {
                        "color": ThemeManager.get_color("text_color"),
                        "textAlign": "center",
                        "fontSize": 14
                    }
                }
            }
        ]
        
        # Add timer components if needed
        timer_components = self._build_timer_components(phase_time, remaining, progress)
        children.extend(timer_components)
        
        return {
            "type": "container",
            "id": "status_bar",
            "x": 0,
            "y": 50,
            "width": self.screen_width,
            "height": 100,
            "properties": {
                "style": {
                    "backgroundColor": ThemeManager.get_color("bg_color")
                }
            },
            "children": children
        }
    
    def _build_timer_components(self, phase_time, remaining, progress):
        """Build timer components for phases that need them.
        
        Args:
            phase_time: Total time for the phase
            remaining: Remaining time
            progress: Progress as a ratio (0.0 to 1.0)
            
        Returns:
            List of timer components
        """
        if self.model.phase not in ["association", "recall"]:
            return []
            
        return [
            # Progress bar
            {
                "type": "progressBar",
                "id": "timer_progress",
                "x": 100,
                "y": 115,
                "width": self.screen_width - 200,
                "height": 10,
                "value": progress,
                "properties": {
                    "style": {
                        "barColor": ThemeManager.get_color("primary_color"),
                        "backgroundColor": ThemeManager.get_color("card_bg")
                    }
                }
            },
            
            # Time text
            {
                "type": "text",
                "id": "timer_text",
                "x": self.screen_width // 2,
                "y": 130,
                "width": 100,
                "height": 20,
                "text": f"{int(remaining)}s",
                "properties": {
                    "style": {
                        "color": ThemeManager.get_color("text_secondary_color"),
                        "textAlign": "center",
                        "fontSize": 12
                    }
                }
            }
        ]
    
    def _build_content_area(self):
        """Build the main content area based on the current phase.
        
        Returns:
            Dict representing the content area component
        """
        content = {
            "type": "container",
            "id": "content_area",
            "x": 0,
            "y": 150,
            "width": self.screen_width,
            "height": self.screen_height - 150,
            "properties": {
                "style": {
                    "backgroundColor": ThemeManager.get_color("bg_color")
                }
            },
            "children": []
        }
        
        # Add phase-specific content
        if self.model.phase == "preparation":
            content["children"] = self._build_preparation_components()
        elif self.model.phase == "association":
            content["children"] = self._build_association_components()
        elif self.model.phase == "recall":
            content["children"] = self._build_recall_components()
        elif self.model.phase == "feedback":
            content["children"] = self._build_feedback_components()
        
        return content
    
    def _build_preparation_components(self):
        """Build components for the preparation phase.
        
        Returns:
            List of components
        """
        return [
            {
                "type": "text",
                "id": "preparation_text",
                "x": self.screen_width // 2,
                "y": 250,
                "width": self.screen_width - 100,
                "height": 60,
                "text": "Get ready to form cross-sensory associations...",
                "properties": {
                    "style": {
                        "color": ThemeManager.get_color("text_color"),
                        "textAlign": "center",
                        "fontSize": 24
                    }
                }
            },
            {
                "type": "text",
                "id": "preparation_subtext",
                "x": self.screen_width // 2,
                "y": 320,
                "width": self.screen_width - 100,
                "height": 30,
                "text": "This training enhances your brain's ability to connect different sensory inputs.",
                "properties": {
                    "style": {
                        "color": ThemeManager.get_color("text_secondary_color"),
                        "textAlign": "center",
                        "fontSize": 16
                    }
                }
            }
        ]
    
    def _build_association_components(self):
        """Build components for the association phase.
        
        Returns:
            List of components
        """
        components = []
        
        # Instructions
        components.append({
            "type": "text",
            "id": "association_instructions",
            "x": self.screen_width // 2,
            "y": 180,
            "width": self.screen_width - 100,
            "height": 30,
            "text": "Memorize these associations:",
            "properties": {
                "style": {
                    "color": ThemeManager.get_color("highlight_color"),
                    "textAlign": "center",
                    "fontSize": 18
                }
            }
        })
        
        # Create a grid layout for associations
        associations = self.model.current_associations
        num_associations = len(associations)
        
        cols = min(3, num_associations)
        rows = (num_associations + cols - 1) // cols
        
        cell_width = 180
        cell_height = 180
        
        # Calculate start position to center the grid
        start_x = (self.screen_width - (cols * cell_width)) // 2 + cell_width // 2
        start_y = 230
        
        # Add each association pair
        for i, association in enumerate(associations):
            row = i // cols
            col = i % cols
            
            x = start_x + col * cell_width
            y = start_y + row * cell_height
            
            # Adjust y for multiple rows
            if rows > 1:
                y = start_y + row * (350 // rows)
            
            # Get stimuli
            first_stimulus = association["first_stimulus"]
            second_stimulus = association["second_stimulus"]
            
            # Add association container
            components.append({
                "type": "rectangle",
                "id": f"association_container_{i}",
                "x": x - 70,
                "y": y - 70,
                "width": 140,
                "height": 140,
                "properties": {
                    "style": {
                        "fillColor": ThemeManager.get_color("card_bg"),
                        "strokeColor": ThemeManager.get_color("border_color"),
                        "strokeWidth": 2,
                        "cornerRadius": 5
                    }
                }
            })
            
            # Add first stimulus (top)
            components.extend(self._create_stimulus_components(first_stimulus, (x, y - 30), f"first_{i}"))
            
            # Add arrow connecting the two
            components.append({
                "type": "text",
                "id": f"arrow_{i}",
                "x": x,
                "y": y,
                "width": 20,
                "height": 20,
                "text": "↓",
                "properties": {
                    "style": {
                        "color": ThemeManager.get_color("highlight_color"),
                        "textAlign": "center",
                        "fontSize": 16
                    }
                }
            })
            
            # Add second stimulus (bottom)
            components.extend(self._create_stimulus_components(second_stimulus, (x, y + 30), f"second_{i}"))
        
        return components
    
    def _build_recall_components(self):
        """Build components for the recall phase.
        
        Returns:
            List of components
        """
        components = []
        
        # Instructions
        components.append({
            "type": "text",
            "id": "recall_instructions",
            "x": self.screen_width // 2,
            "y": 180,
            "width": self.screen_width - 100,
            "height": 30,
            "text": "Match each item with its association:",
            "properties": {
                "style": {
                    "color": ThemeManager.get_color("highlight_color"),
                    "textAlign": "center",
                    "fontSize": 18
                }
            }
        })
        
        # Create a layout for stimuli and responses
        stimuli = self.model.current_stimuli
        associations = self.model.current_associations
        user_responses = self.model.user_responses
        num_items = len(stimuli)
        
        # Display stimuli on the left
        stimulus_x = self.screen_width // 4
        
        for i, stimulus in enumerate(stimuli):
            y = 250 + i * (300 / max(1, num_items - 1)) if num_items > 1 else 300
            
            # Add stimulus container
            components.append({
                "type": "rectangle",
                "id": f"stimulus_container_{i}",
                "x": stimulus_x - 40,
                "y": y - 40,
                "width": 80,
                "height": 80,
                "properties": {
                    "style": {
                        "fillColor": ThemeManager.get_color("card_bg"),
                        "strokeColor": ThemeManager.get_color("primary_color"),
                        "strokeWidth": 2,
                        "cornerRadius": 5
                    }
                }
            })
            
            # Add the stimulus
            components.extend(self._create_stimulus_components(stimulus, (stimulus_x, y), f"stimulus_{i}"))
            
            # Add user's response line if selected
            if user_responses[i] is not None:
                # Find which response this is
                response_idx = None
                for j, assoc in enumerate(associations):
                    if assoc["second_stimulus"] == user_responses[i]:
                        response_idx = j
                        break
                
                if response_idx is not None:
                    response_y = 250 + response_idx * (300 / max(1, num_items - 1)) if num_items > 1 else 300
                    response_x = 3 * self.screen_width // 4
                    
                    # Draw connection line
                    components.append({
                        "type": "line",
                        "id": f"connection_{i}",
                        "x1": stimulus_x + 45,
                        "y1": y,
                        "x2": response_x - 45,
                        "y2": response_y,
                        "properties": {
                            "style": {
                                "strokeColor": ThemeManager.get_color("highlight_color"),
                                "strokeWidth": 2
                            }
                        }
                    })
        
        # Display response options on the right
        response_x = 3 * self.screen_width // 4
        
        for i, association in enumerate(associations):
            y = 250 + i * (300 / max(1, num_items - 1)) if num_items > 1 else 300
            
            # Add response container
            components.append({
                "type": "rectangle",
                "id": f"response_container_{i}",
                "x": response_x - 40,
                "y": y - 40,
                "width": 80,
                "height": 80,
                "properties": {
                    "style": {
                        "fillColor": ThemeManager.get_color("card_bg"),
                        "strokeColor": ThemeManager.get_color("primary_color"),
                        "strokeWidth": 2,
                        "cornerRadius": 5
                    }
                }
            })
            
            # Add the response stimulus
            components.extend(self._create_stimulus_components(association["second_stimulus"], (response_x, y), f"response_{i}"))
        
        # Add submit button
        components.append({
            "type": "button",
            "id": "submit_button",
            "x": self.screen_width // 2 - 50,
            "y": self.screen_height - 80,
            "width": 100,
            "height": 40,
            "text": "Submit",
            "action": "submit",
            "properties": {
                "style": {
                    "backgroundColor": ThemeManager.get_color("primary_color"),
                    "color": ThemeManager.get_color("text_on_primary_color"),
                    "borderRadius": 5,
                    "fontSize": 16
                }
            }
        })
        
        return components
    
    def _build_feedback_components(self):
        """Build components for the feedback phase.
        
        Returns:
            List of components
        """
        components = []
        
        # Accuracy text
        components.append({
            "type": "text",
            "id": "accuracy_text",
            "x": self.screen_width // 2,
            "y": 180,
            "width": self.screen_width - 100,
            "height": 30,
            "text": f"Your accuracy: {self.model.success_rate:.0%}",
            "properties": {
                "style": {
                    "color": ThemeManager.get_color("highlight_color"),
                    "textAlign": "center",
                    "fontSize": 18
                }
            }
        })
        
        # Create a layout similar to recall but showing correct vs. user answers
        stimuli = self.model.current_stimuli
        user_responses = self.model.user_responses
        correct_associations = self.model.correct_associations
        num_items = len(stimuli)
        
        for i, stimulus in enumerate(stimuli):
            y = 250 + i * (300 / max(1, num_items - 1)) if num_items > 1 else 300
            
            # Stimulus column
            stimulus_x = self.screen_width // 6
            
            # Add stimulus container
            components.append({
                "type": "rectangle",
                "id": f"stimulus_container_{i}",
                "x": stimulus_x - 30,
                "y": y - 30,
                "width": 60,
                "height": 60,
                "properties": {
                    "style": {
                        "fillColor": ThemeManager.get_color("card_bg"),
                        "strokeColor": ThemeManager.get_color("primary_color"),
                        "strokeWidth": 2,
                        "cornerRadius": 5
                    }
                }
            })
            
            # Add the stimulus
            components.extend(self._create_stimulus_components(stimulus, (stimulus_x, y), f"stimulus_{i}", 0.8))
            
            # Correct column
            correct_x = self.screen_width // 2
            
            # Get the correct association
            correct_stimulus = correct_associations[i]
            
            # Add correct answer container
            components.append({
                "type": "rectangle",
                "id": f"correct_container_{i}",
                "x": correct_x - 30,
                "y": y - 30,
                "width": 60,
                "height": 60,
                "properties": {
                    "style": {
                        "fillColor": ThemeManager.get_color("card_bg"),
                        "strokeColor": ThemeManager.get_color("success_color"),
                        "strokeWidth": 2,
                        "cornerRadius": 5
                    }
                }
            })
            
            # Add the correct stimulus
            components.extend(self._create_stimulus_components(correct_stimulus, (correct_x, y), f"correct_{i}", 0.8))
            
            # User column
            user_x = 5 * self.screen_width // 6
            
            # Get the user's answer
            user_stimulus = user_responses[i]
            
            # Determine if correct
            is_correct = user_stimulus == correct_stimulus
            
            # Add user answer container
            components.append({
                "type": "rectangle",
                "id": f"user_container_{i}",
                "x": user_x - 30,
                "y": y - 30,
                "width": 60,
                "height": 60,
                "properties": {
                    "style": {
                        "fillColor": ThemeManager.get_color("card_bg"),
                        "strokeColor": ThemeManager.get_color("success_color") if is_correct else ThemeManager.get_color("error_color"),
                        "strokeWidth": 2,
                        "cornerRadius": 5
                    }
                }
            })
            
            # Add the user stimulus
            components.extend(self._create_stimulus_components(user_stimulus, (user_x, y), f"user_{i}", 0.8))
            
            # Add labels if first item
            if i == 0:
                components.append({
                    "type": "text",
                    "id": "stimulus_label",
                    "x": stimulus_x,
                    "y": 210,
                    "width": 80,
                    "height": 20,
                    "text": "Stimulus",
                    "properties": {
                        "style": {
                            "color": ThemeManager.get_color("text_secondary_color"),
                            "textAlign": "center",
                            "fontSize": 14
                        }
                    }
                })
                
                components.append({
                    "type": "text",
                    "id": "correct_label",
                    "x": correct_x,
                    "y": 210,
                    "width": 80,
                    "height": 20,
                    "text": "Correct",
                    "properties": {
                        "style": {
                            "color": ThemeManager.get_color("text_secondary_color"),
                            "textAlign": "center",
                            "fontSize": 14
                        }
                    }
                })
                
                components.append({
                    "type": "text",
                    "id": "user_label",
                    "x": user_x,
                    "y": 210,
                    "width": 80,
                    "height": 20,
                    "text": "Your Answer",
                    "properties": {
                        "style": {
                            "color": ThemeManager.get_color("text_secondary_color"),
                            "textAlign": "center",
                            "fontSize": 14
                        }
                    }
                })
            
        
        return components
    
    def _create_stimulus_components(self, stimulus, position, id_prefix, scale=1.0):
        """Create components for a stimulus.
        
        Args:
            stimulus: Stimulus data
            position: (x, y) position
            id_prefix: Prefix for component IDs
            scale: Scale factor for the stimulus size (default: 1.0)
            
        Returns:
            List of components
        """
        if not stimulus:
            return []
            
        components = []
        x, y = position
        
        stimulus_type = stimulus.get("type")
        value = stimulus.get("value")
        
        if stimulus_type == "color":
            # Color is represented as a colored circle
            r, g, b = value
            color = f"rgb({r}, {g}, {b})"
            radius = int(25 * scale)
            
            components.append({
                "type": "circle",
                "id": f"{id_prefix}_color",
                "x": x,
                "y": y,
                "radius": radius,
                "properties": {
                    "style": {
                        "fillColor": color,
                        "strokeColor": ThemeManager.get_color("border_color"),
                        "strokeWidth": 1
                    }
                }
            })
            
        elif stimulus_type == "shape":
            # Shape is represented as a shape name
            size = int(40 * scale)
            
            components.append({
                "type": "shape",
                "id": f"{id_prefix}_shape",
                "x": x,
                "y": y,
                "width": size,
                "height": size,
                "shape": value,  # e.g., "circle", "square", etc.
                "properties": {
                    "style": {
                        "fillColor": ThemeManager.get_color("primary_color"),
                        "strokeColor": ThemeManager.get_color("border_color"),
                        "strokeWidth": 1
                    }
                }
            })
            
        elif stimulus_type == "sound":
            # Sound is represented as a speaker icon with a tooltip
            size = int(40 * scale)
            
            components.append({
                "type": "icon",
                "id": f"{id_prefix}_sound",
                "x": x,
                "y": y,
                "width": size,
                "height": size,
                "icon": "speaker",
                "properties": {
                    "style": {
                        "fillColor": ThemeManager.get_color("primary_color"),
                        "tooltip": value
                    }
                }
            })
            
        elif stimulus_type == "position":
            # Position is represented as a dot on a small grid
            size = int(40 * scale)
            pos_x, pos_y = value
            
            # Grid background
            components.append({
                "type": "rectangle",
                "id": f"{id_prefix}_position_grid",
                "x": x - size // 2,
                "y": y - size // 2,
                "width": size,
                "height": size,
                "properties": {
                    "style": {
                        "fillColor": ThemeManager.get_color("card_bg"),
                        "strokeColor": ThemeManager.get_color("border_color"),
                        "strokeWidth": 1
                    }
                }
            })
            
            # Position dot
            dot_x = x - size // 2 + int(pos_x * size)
            dot_y = y - size // 2 + int(pos_y * size)
            
            components.append({
                "type": "circle",
                "id": f"{id_prefix}_position_dot",
                "x": dot_x,
                "y": dot_y,
                "radius": int(4 * scale),
                "properties": {
                    "style": {
                        "fillColor": ThemeManager.get_color("primary_color")
                    }
                }
            })
            
        elif stimulus_type == "number":
            # Number is represented as text
            font_size = int(16 * scale)
            
            components.append({
                "type": "text",
                "id": f"{id_prefix}_number",
                "x": x,
                "y": y,
                "width": int(40 * scale),
                "height": int(40 * scale),
                "text": str(value),
                "properties": {
                    "style": {
                        "color": ThemeManager.get_color("text_color"),
                        "textAlign": "center",
                        "fontSize": font_size
                    }
                }
            })
            
        elif stimulus_type == "texture":
            # Texture is represented as a patterned rectangle
            size = int(40 * scale)
            
            components.append({
                "type": "texture",
                "id": f"{id_prefix}_texture",
                "x": x - size // 2,
                "y": y - size // 2,
                "width": size,
                "height": size,
                "texture": value,
                "properties": {
                    "style": {
                        "fillColor": ThemeManager.get_color("primary_color"),
                        "backgroundColor": ThemeManager.get_color("card_bg")
                    }
                }
            })
        
        return components 