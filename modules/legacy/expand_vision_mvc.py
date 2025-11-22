#!/usr/bin/env python3
"""
ExpandVision Training Module - MVC Wrapper

This file serves as a compatibility wrapper for the ExpandVision cognitive training module.
It imports the modular implementation from the 'evolve/expand_vision' directory and
re-exports the main ExpandVision class to maintain backward compatibility.

The actual implementation has been restructured using a modular approach with
separate model, view, and controller components for better maintainability.

See the implementation in:
- evolve/expand_vision/expand_vision_mvc.py (main module)
- evolve/expand_vision/expand_vision_model.py (game logic)
- evolve/expand_vision/expand_vision_view.py (UI rendering)
- evolve/expand_vision/expand_vision_controller.py (user interaction)
"""

import sys
from pathlib import Path

# Add the parent directory to sys.path for absolute imports
if __name__ == "__main__" or not __package__:
    project_root = Path(__file__).parent.parent
    sys.path.insert(0, str(project_root))

# Import and re-export the main class for backward compatibility
from .evolve.expand_vision.expand_vision_mvc import ExpandVision

# For direct usage
if __name__ == "__main__":
    # Create an instance of the module with default dimensions
    screen_width, screen_height = 800, 600
    module = ExpandVision(screen_width, screen_height)
    
    # Use the module's methods as needed
    print("ExpandVision module initialized")
    print("Module state:", module.get_state()) 