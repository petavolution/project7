#!/usr/bin/env python3
"""
Quantum Memory View Component

This module handles the UI representation for the Quantum Memory module:
- Component tree building
- Layout calculations
- Quantum state visualization
- Theme-aware styling
"""

import sys
import math
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


class QuantumMemoryView:
    """View component for Quantum Memory module - handles UI representation."""
    
    def __init__(self, model):
        """Initialize the view with reference to the model.
        
        Args:
            model: Quantum Memory Model instance
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
            "id": "quantum_memory_root",
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
                    "text": "Quantum Memory",
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
                "text": self.model.message,
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
                "text": f"Level: {self.model.level}   Trial: {self.model.current_trial + 1}",
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
        if self.model.phase in ["memorize", "recall"]:
            # Get phase-specific timer information
            phase_time = self.model.config[f"{self.model.phase}_time"]
            remaining = max(0, phase_time - self.model.elapsed_time)
            progress = 1.0 - (remaining / phase_time)
            
            # Add progress bar
            children.append({
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
            })
            
            # Add timer text
            children.append({
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
            })
        
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
            "children": self._build_phase_specific_components()
        }
        
        return content
    
    def _build_phase_specific_components(self):
        """Build components specific to the current phase.
        
        Returns:
            List of components
        """
        components = []
        
        if self.model.phase == "preparation":
            components.extend(self._build_preparation_components())
        elif self.model.phase == "memorize":
            components.extend(self._build_memorize_components())
        elif self.model.phase == "recall":
            components.extend(self._build_recall_components())
        elif self.model.phase == "feedback":
            components.extend(self._build_feedback_components())
        
        return components
    
    def _build_preparation_components(self):
        """Build components for the preparation phase.
        
        Returns:
            List of components
        """
        components = []
        
        # Add instruction text
        components.append({
            "type": "text",
            "id": "preparation_text",
            "x": self.screen_width // 2,
            "y": 250,
            "width": self.screen_width - 100,
            "height": 60,
            "text": "Prepare for quantum states...",
            "properties": {
                "style": {
                    "color": ThemeManager.get_color("text_color"),
                    "textAlign": "center",
                    "fontSize": 24
                }
            }
        })
        
        # Add explanation
        components.append({
            "type": "text",
            "id": "preparation_explanation",
            "x": self.screen_width // 2,
            "y": 320,
            "width": self.screen_width - 100,
            "height": 80,
            "text": "You will see quantum states in superposition. Memorize them, as they will collapse when observed. Your task is to recall their values after they collapse.",
            "properties": {
                "style": {
                    "color": ThemeManager.get_color("text_secondary_color"),
                    "textAlign": "center",
                    "fontSize": 16
                }
            }
        })
        
        # Add grid placeholders
        quantum_states = self.model.get_visible_quantum_states()
        for state in quantum_states:
            pos_x, pos_y = state["position"]
            
            # Add placeholder box
            components.append({
                "type": "rectangle",
                "id": f"quantum_box_{state['id']}",
                "x": pos_x - 30,
                "y": pos_y - 30,
                "width": 60,
                "height": 60,
                "properties": {
                    "style": {
                        "fillColor": ThemeManager.get_color("card_bg"),
                        "strokeColor": ThemeManager.get_color("border_color"),
                        "strokeWidth": 2,
                        "cornerRadius": 5
                    }
                }
            })
        
        return components
    
    def _build_memorize_components(self):
        """Build components for the memorize phase.
        
        Returns:
            List of components
        """
        components = []
        
        # Add instruction text
        components.append({
            "type": "text",
            "id": "memorize_instruction",
            "x": self.screen_width // 2,
            "y": 180,
            "width": self.screen_width - 100,
            "height": 30,
            "text": "Memorize these quantum states:",
            "properties": {
                "style": {
                    "color": ThemeManager.get_color("highlight_color"),
                    "textAlign": "center",
                    "fontSize": 18
                }
            }
        })
        
        # Draw quantum states in superposition
        quantum_states = self.model.get_visible_quantum_states()
        for state in quantum_states:
            pos_x, pos_y = state["position"]
            
            # Draw state box
            components.append({
                "type": "rectangle",
                "id": f"quantum_box_{state['id']}",
                "x": pos_x - 30,
                "y": pos_y - 30,
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
            
            # Draw superposition symbols
            if "superposition" in state:
                symbols = state["superposition"]
                symbol_count = len(symbols)
                
                # Arrange symbols in a grid or circle
                if symbol_count <= 4:
                    # Grid layout for 1-4 symbols
                    positions = [
                        (pos_x - 15, pos_y - 15),  # Top-left
                        (pos_x + 15, pos_y - 15),  # Top-right
                        (pos_x - 15, pos_y + 15),  # Bottom-left
                        (pos_x + 15, pos_y + 15),  # Bottom-right
                    ]
                    
                    for i, symbol in enumerate(symbols):
                        if i < len(positions):
                            components.append({
                                "type": "text",
                                "id": f"symbol_{state['id']}_{i}",
                                "x": positions[i][0],
                                "y": positions[i][1],
                                "width": 20,
                                "height": 20,
                                "text": symbol,
                                "properties": {
                                    "style": {
                                        "color": ThemeManager.get_color("text_color"),
                                        "textAlign": "center",
                                        "fontSize": 16
                                    }
                                }
                            })
                else:
                    # Circular layout for 5+ symbols
                    radius = 20
                    for i, symbol in enumerate(symbols):
                        angle = (i * 2 * math.pi) / symbol_count
                        symbol_x = pos_x + radius * math.cos(angle)
                        symbol_y = pos_y + radius * math.sin(angle)
                        
                        components.append({
                            "type": "text",
                            "id": f"symbol_{state['id']}_{i}",
                            "x": symbol_x,
                            "y": symbol_y,
                            "width": 20,
                            "height": 20,
                            "text": symbol,
                            "properties": {
                                "style": {
                                    "color": ThemeManager.get_color("text_color"),
                                    "textAlign": "center",
                                    "fontSize": 14
                                }
                            }
                        })
            
            # Draw entanglement lines
            if "entangled_with" in state and state["entangled_with"] is not None:
                entangled_id = state["entangled_with"]
                # Only draw the line once (from the lower ID to the higher ID)
                if state["id"] < entangled_id:
                    entangled_state = None
                    for s in quantum_states:
                        if s["id"] == entangled_id:
                            entangled_state = s
                            break
                    
                    if entangled_state:
                        ent_x, ent_y = entangled_state["position"]
                        components.append({
                            "type": "line",
                            "id": f"entanglement_{state['id']}_{entangled_id}",
                            "x1": pos_x,
                            "y1": pos_y,
                            "x2": ent_x,
                            "y2": ent_y,
                            "properties": {
                                "style": {
                                    "strokeColor": ThemeManager.get_color("highlight_color"),
                                    "strokeWidth": 2,
                                    "strokeDash": [4, 4]  # Dashed line
                                }
                            }
                        })
        
        return components
    
    def _build_recall_components(self):
        """Build components for the recall phase.
        
        Returns:
            List of components
        """
        components = []
        
        # Add instruction text
        components.append({
            "type": "text",
            "id": "recall_instruction",
            "x": self.screen_width // 2,
            "y": 180,
            "width": self.screen_width - 100,
            "height": 30,
            "text": "Select the quantum states to recall their values:",
            "properties": {
                "style": {
                    "color": ThemeManager.get_color("highlight_color"),
                    "textAlign": "center",
                    "fontSize": 18
                }
            }
        })
        
        # Draw quantum states
        quantum_states = self.model.get_visible_quantum_states()
        for state in quantum_states:
            pos_x, pos_y = state["position"]
            
            # Box style depends on state
            box_style = {}
            if state["type"] == "collapsed":
                # Already collapsed by user
                box_style = {
                    "fillColor": ThemeManager.get_color("card_bg"),
                    "strokeColor": ThemeManager.get_color("success_color"),
                    "strokeWidth": 2,
                    "cornerRadius": 5
                }
            else:
                # Still to be selected
                box_style = {
                    "fillColor": ThemeManager.get_color("card_bg"),
                    "strokeColor": ThemeManager.get_color("primary_color") if not state.get("selected", False) else ThemeManager.get_color("highlight_color"),
                    "strokeWidth": 2,
                    "cornerRadius": 5
                }
            
            # Draw state box
            components.append({
                "type": "rectangle",
                "id": f"quantum_box_{state['id']}",
                "x": pos_x - 30,
                "y": pos_y - 30,
                "width": 60,
                "height": 60,
                "properties": {
                    "style": box_style,
                    "interactive": True,
                    "action": {
                        "type": "click",
                        "state_id": state["id"]
                    }
                }
            })
            
            # If collapsed, show the observed value
            if "observed_value" in state and state["observed_value"]:
                components.append({
                    "type": "text",
                    "id": f"observed_{state['id']}",
                    "x": pos_x,
                    "y": pos_y,
                    "width": 40,
                    "height": 40,
                    "text": state["observed_value"],
                    "properties": {
                        "style": {
                            "color": ThemeManager.get_color("text_color"),
                            "textAlign": "center",
                            "fontSize": 20
                        }
                    }
                })
            elif state.get("selected", False):
                # Show "selected" indicator
                components.append({
                    "type": "text",
                    "id": f"selected_{state['id']}",
                    "x": pos_x,
                    "y": pos_y,
                    "width": 40,
                    "height": 40,
                    "text": "?",
                    "properties": {
                        "style": {
                            "color": ThemeManager.get_color("highlight_color"),
                            "textAlign": "center",
                            "fontSize": 20
                        }
                    }
                })
            else:
                # Show "?" for unknown states
                components.append({
                    "type": "text",
                    "id": f"unknown_{state['id']}",
                    "x": pos_x,
                    "y": pos_y,
                    "width": 40,
                    "height": 40,
                    "text": "?",
                    "properties": {
                        "style": {
                            "color": ThemeManager.get_color("text_secondary_color"),
                            "textAlign": "center",
                            "fontSize": 20
                        }
                    }
                })
            
            # Draw entanglement lines for collapsed states
            if "entangled_with" in state and state["entangled_with"] is not None and state["type"] == "collapsed":
                entangled_id = state["entangled_with"]
                # Only draw the line once (from the lower ID to the higher ID)
                if state["id"] < entangled_id:
                    entangled_state = None
                    for s in quantum_states:
                        if s["id"] == entangled_id and s["type"] == "collapsed":
                            entangled_state = s
                            break
                    
                    if entangled_state:
                        ent_x, ent_y = entangled_state["position"]
                        components.append({
                            "type": "line",
                            "id": f"entanglement_{state['id']}_{entangled_id}",
                            "x1": pos_x,
                            "y1": pos_y,
                            "x2": ent_x,
                            "y2": ent_y,
                            "properties": {
                                "style": {
                                    "strokeColor": ThemeManager.get_color("highlight_color"),
                                    "strokeWidth": 2,
                                    "strokeDash": [4, 4]  # Dashed line
                                }
                            }
                        })
        
        # Add submit button
        components.append({
            "type": "button",
            "id": "submit_button",
            "x": self.screen_width // 2 - 50,
            "y": self.screen_height - 80,
            "width": 100,
            "height": 40,
            "text": "Submit",
            "properties": {
                "style": {
                    "backgroundColor": ThemeManager.get_color("primary_color"),
                    "color": ThemeManager.get_color("text_on_primary_color"),
                    "borderRadius": 5,
                    "fontSize": 16
                },
                "action": {
                    "type": "action",
                    "action": "submit"
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
        
        # Add accuracy text
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
        
        # Draw quantum states with feedback
        quantum_states = self.model.get_visible_quantum_states()
        for state in quantum_states:
            pos_x, pos_y = state["position"]
            
            # Box style depends on correctness
            is_correct = state.get("correct", False)
            box_style = {
                "fillColor": ThemeManager.get_color("card_bg"),
                "strokeColor": ThemeManager.get_color("success_color") if is_correct else ThemeManager.get_color("error_color"),
                "strokeWidth": 2,
                "cornerRadius": 5
            }
            
            # Draw state box
            components.append({
                "type": "rectangle",
                "id": f"quantum_box_{state['id']}",
                "x": pos_x - 30,
                "y": pos_y - 30,
                "width": 60,
                "height": 60,
                "properties": {
                    "style": box_style
                }
            })
            
            # Show the correct value
            components.append({
                "type": "text",
                "id": f"value_{state['id']}",
                "x": pos_x,
                "y": pos_y,
                "width": 40,
                "height": 40,
                "text": state["observed_value"],
                "properties": {
                    "style": {
                        "color": ThemeManager.get_color("text_color"),
                        "textAlign": "center",
                        "fontSize": 20
                    }
                }
            })
            
            # If incorrect, show what the user selected
            if not is_correct and state["id"] in self.model.user_selections:
                user_selections = self.model.user_selections[state["id"]]
                if user_selections:
                    components.append({
                        "type": "text",
                        "id": f"user_selection_{state['id']}",
                        "x": pos_x,
                        "y": pos_y + 40,
                        "width": 60,
                        "height": 20,
                        "text": f"Selected: {', '.join(user_selections)}",
                        "properties": {
                            "style": {
                                "color": ThemeManager.get_color("error_color"),
                                "textAlign": "center",
                                "fontSize": 10
                            }
                        }
                    })
            
            # Draw entanglement lines
            if "entangled_with" in state and state["entangled_with"] is not None:
                entangled_id = state["entangled_with"]
                # Only draw the line once (from the lower ID to the higher ID)
                if state["id"] < entangled_id:
                    entangled_state = None
                    for s in quantum_states:
                        if s["id"] == entangled_id:
                            entangled_state = s
                            break
                    
                    if entangled_state:
                        ent_x, ent_y = entangled_state["position"]
                        components.append({
                            "type": "line",
                            "id": f"entanglement_{state['id']}_{entangled_id}",
                            "x1": pos_x,
                            "y1": pos_y,
                            "x2": ent_x,
                            "y2": ent_y,
                            "properties": {
                                "style": {
                                    "strokeColor": ThemeManager.get_color("highlight_color"),
                                    "strokeWidth": 2,
                                    "strokeDash": [4, 4]  # Dashed line
                                }
                            }
                        })
        
        # Add next trial text
        next_text = "Next trial starting soon..."
        if self.model.level > 1 and self.model.trials_completed % self.model.config["level_up_threshold"] == 0:
            next_text = f"Level {self.model.level} starting soon..."
            
        components.append({
            "type": "text",
            "id": "next_trial",
            "x": self.screen_width // 2,
            "y": self.screen_height - 80,
            "width": self.screen_width - 100,
            "height": 30,
            "text": next_text,
            "properties": {
                "style": {
                    "color": ThemeManager.get_color("text_secondary_color"),
                    "textAlign": "center",
                    "fontSize": 16
                }
            }
        })
        
        return components 