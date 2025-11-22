# ExpandVision Module

## Overview
ExpandVision is a cognitive training module focused on enhancing peripheral vision and numerical processing. It trains users to maintain central focus while processing information from their peripheral vision.

## How It Works
1. Users focus on a central circle
2. Numbers briefly appear in the periphery (top, right, bottom, left)
3. Users must calculate the sum of all numbers while maintaining central focus
4. The distance of numbers from the center increases gradually to expand peripheral awareness

## Module Structure
This module follows the Model-View-Controller (MVC) architecture:

- **expand_vision_mvc.py** - Main entry point that integrates MVC components
- **expand_vision_model.py** - Core game logic and state management
- **expand_vision_view.py** - UI representation and rendering
- **expand_vision_controller.py** - Input handling and user interaction

## Key Features
- **Progressive Difficulty**: Numbers appear further from center as user skill improves
- **Phase-Based Gameplay**: Preparation → Active → Answer → Feedback cycle
- **Theme-Aware Styling**: Consistent visual presentation across platform
- **Responsive Layout**: Adapts to different screen sizes
- **Delta-Optimized Updates**: Efficient state management for smooth performance

## Integration
The module integrates with the MetaMindIQTrain platform by:
- Extending the TrainingModule base class
- Using the ThemeManager for consistent styling
- Providing a component-based UI for flexible rendering

## Cognitive Training Benefits
- Improved peripheral vision awareness
- Enhanced divided attention ability
- Better numerical processing under attention constraints
- Increased visual scanning efficiency

## Usage
```python
from MetaMindIQTrain.modules.evolve.expand_vision.expand_vision_mvc import ExpandVision

# Initialize the module
module = ExpandVision(screen_width=800, screen_height=600)

# In your game loop
needs_update = module.update()
if needs_update:
    ui_tree = module.build_component_tree()
    # Render the UI tree
``` 