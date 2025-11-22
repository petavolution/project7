# Synesthetic Training Module

## Overview
The Synesthetic Training module trains cross-modal sensory associations through pattern recognition exercises that connect different sensory inputs (visual, auditory, spatial, numeric). It enhances perceptual binding and multisensory integration capabilities.

## Features
- Cross-modal sensory association training
- Multiple sensory types: color, shape, sound, position, number, texture
- Adaptive difficulty progression
- Performance tracking and feedback
- Configurable sensory combinations

## Module Structure
This module follows the Model-View-Controller (MVC) design pattern:

1. **Model** (`synesthetic_training_model.py`): Handles the core game logic, including:
   - Cross-sensory association generation
   - Game state management 
   - Scoring and performance tracking
   - Phase transitions
   - Difficulty progression

2. **View** (`synesthetic_training_view.py`): Handles the UI representation, including:
   - Layout calculations
   - Component tree building
   - Visual representation of cross-sensory associations
   - Theme-aware styling

3. **Controller** (`synesthetic_training_controller.py`): Handles user interactions, including:
   - Mouse click processing and hit detection
   - Action handling for associations
   - Game state updates
   - User input validation

4. **Main MVC Integration** (`synesthetic_training_mvc.py`): Integrates all components into a cohesive module that inherits from BaseModule and interfaces with the MetaMindIQTrain framework.

## Usage
The module can be imported and used as follows:

```python
from MetaMindIQTrain.modules.evolve.synesthetic_training.synesthetic_training_mvc import SynestheticTraining

# Create module instance with optional custom configuration
module = SynestheticTraining(config={
    'screen_width': 1024,
    'screen_height': 768,
    'enabled_senses': ['color', 'shape', 'sound', 'position'],
    'association_count': 5,
    'difficulty': 3
})

# Get UI component tree for rendering
component_tree = module.get_component_tree()

# Update module state (called each frame)
state = module.update(delta_time=0.016)  # ~60fps

# Handle user input
response = module.handle_input({
    'type': 'click',
    'x': 250,
    'y': 300
})
```

## Phases
The module operates in three distinct phases:

1. **Preparation Phase**: Displays instructions and prepares the user for the exercise
2. **Association Phase**: Presents cross-sensory associations for the user to memorize
3. **Recall Phase**: Tests the user's memory of the presented associations
4. **Feedback Phase**: Provides feedback on performance and advances to the next level if successful 