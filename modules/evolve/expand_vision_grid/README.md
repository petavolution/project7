# ExpandVision Grid Module

## Overview
ExpandVision Grid is a cognitive training module focused on enhancing peripheral vision and numerical processing through a grid-based approach. Unlike the standard ExpandVision module (which displays numbers at four cardinal points), this module displays numbers in a full grid pattern surrounding the central focal point.

## How It Works
1. Users focus on a central circle (maintaining gaze fixation)
2. Numbers briefly appear in a grid pattern surrounding the center
3. Users must calculate the sum of all numbers in the grid while maintaining central focus
4. The grid gradually expands and grows in size as users progress, extending their peripheral awareness

## Module Structure
This module follows the Model-View-Controller (MVC) architecture:

- **expand_vision_grid_mvc.py** - Main entry point that integrates MVC components
- **expand_vision_grid_model.py** - Core game logic and grid management
- **expand_vision_grid_view.py** - UI representation and grid rendering
- **expand_vision_grid_controller.py** - Input handling and user interaction

## Key Features
- **Grid-Based Layout**: Numbers appear in a grid pattern rather than just at cardinal points
- **Adaptive Difficulty**: Grid size increases from 3×3 to 5×5 as user skill improves
- **Expanding Grid Spacing**: Distance between grid points increases over time
- **Color-Coded Quadrants**: Numbers are color-coded based on their position in the grid
- **Weighted Scoring**: Higher scores for processing larger, more complex grids
- **Adaptive Timing**: Display duration adjusts based on grid complexity
- **Theme-Aware Styling**: Consistent visual presentation across platform

## Integration
The module integrates with the MetaMindIQTrain platform by:
- Extending the TrainingModule base class
- Using the ThemeManager for consistent styling
- Providing a component-based UI for flexible rendering

## Cognitive Training Benefits
- Improved peripheral vision awareness across the entire visual field
- Enhanced ability to process multiple stimuli simultaneously
- Better numerical processing under divided attention
- Increased visual scanning efficiency in grid-like patterns
- Training of spatial working memory

## Usage
```python
from MetaMindIQTrain.modules.evolve.expand_vision_grid.expand_vision_grid_mvc import ExpandVisionGrid

# Initialize the module
module = ExpandVisionGrid(screen_width=800, screen_height=600)

# In your game loop
needs_update = module.update(delta_time)
if needs_update:
    ui_tree = module.build_component_tree()
    # Render the UI tree
``` 