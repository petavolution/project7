# Neural Flow Module

A cognitive training module that enhances neural pathway development through interactive node activation exercises.

## Overview

The Neural Flow module is designed to improve cognitive processing speed and pattern recognition by presenting users with a series of nodes that must be activated in a specific sequence. The module features:

- Dynamic node generation and activation
- Progressive difficulty scaling
- Visual feedback for success and errors
- Adaptive timing based on performance
- Theme-aware styling

## How It Works

1. The module displays a network of nodes connected by paths
2. During the preparation phase, nodes are highlighted in sequence
3. In the active phase, users must click nodes in the correct order
4. Success and error feedback is provided through visual cues
5. Difficulty increases as users progress through levels

## Module Structure

The module follows the MVC (Model-View-Controller) pattern:

- `neural_flow_mvc.py`: Main entry point that integrates all components
- `neural_flow_model.py`: Core game logic and state management
- `neural_flow_view.py`: UI representation and rendering
- `neural_flow_controller.py`: User interaction and game flow

## Key Features

### Neural Network Visualization
- Dynamic node placement and path generation
- Color-coded nodes for different states (active, success, error)
- Smooth transitions between states
- Responsive layout based on screen dimensions

### Game Mechanics
- Three-phase gameplay (preparation, active, feedback)
- Progressive difficulty scaling
- Adaptive timing based on performance
- Score tracking and accuracy calculation

### User Interface
- Clear instructions and feedback
- Status information display
- Theme-aware styling
- Responsive layout

## Integration

The module integrates with the MetaMindIQTrain platform through:

```python
from MetaMindIQTrain.modules.evolve.neural_flow.neural_flow_mvc import NeuralFlow

# Initialize the module
module = NeuralFlow(screen_width=800, screen_height=600)

# Handle user input
module.handle_click((x, y))

# Update module state
module.update(delta_time)

# Build UI
component_tree = module.build_component_tree()

# Render
module.render(renderer)
```

## Cognitive Training Benefits

The Neural Flow module targets several cognitive abilities:

1. **Pattern Recognition**
   - Identifying and remembering node sequences
   - Recognizing visual patterns in node placement

2. **Processing Speed**
   - Quick response to node activation
   - Rapid visual scanning of the network

3. **Working Memory**
   - Maintaining sequence information
   - Tracking activated nodes

4. **Visual Attention**
   - Focusing on relevant nodes
   - Ignoring distractions

## Usage

```python
# Initialize the module
module = NeuralFlow()

# Process input data
input_data = {
    "screen_width": 800,
    "screen_height": 600
}
processed_data = module.process_input_data(input_data)

# Main game loop
while running:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.MOUSEBUTTONDOWN:
            module.handle_click(event.pos)
    
    # Update
    module.update(delta_time)
    
    # Render
    module.render(renderer)
```

## Configuration

The module can be configured through the following settings:

```python
config = {
    "preparation_duration": 3.0,  # Time to show sequence
    "active_duration": 10.0,      # Time to complete sequence
    "feedback_duration": 2.0,     # Time to show feedback
    "node_count": 5,              # Number of nodes per sequence
    "node_spacing": 100,          # Minimum distance between nodes
    "click_radius": 20,           # Click detection radius
    "visual_scale": 1.0           # UI scaling factor
}
```

## Dependencies

- Python 3.8+
- Pygame
- MetaMindIQTrain core modules 