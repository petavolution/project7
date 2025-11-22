# Neural Synthesis Module

A multi-modal cognitive training module that integrates auditory and visual pattern recognition to enhance neural plasticity, cross-modal integration, and creative thinking.

## Overview

The Neural Synthesis module engages users in a synesthetic experience that maps visual patterns to auditory sequences and requires pattern recognition across multiple sensory domains. The module features:

- Visual-auditory pattern matching
- Progressive difficulty scaling
- Spatial memory training
- Cross-modal integration challenges
- Adaptive feedback mechanisms

## How It Works

1. The module displays a pattern of colored cells in a grid, each associated with a specific tone
2. During the observation phase, users must memorize the pattern sequence
3. In the reproduction phase, users must recreate the pattern by clicking cells in the correct order
4. The module provides immediate feedback on accuracy
5. Difficulty increases as users progress through levels, with larger grids and longer sequences

## Module Structure

The module follows the MVC (Model-View-Controller) pattern:

- `neural_synthesis_mvc.py`: Main entry point that integrates all components
- `neural_synthesis_model.py`: Core game logic and state management
- `neural_synthesis_view.py`: UI representation and rendering
- `neural_synthesis_controller.py`: User interaction and game flow

## Key Features

### Visual-Auditory Integration
- Colored cells mapped to musical tones
- Pattern sequences that span both visual and auditory domains
- Synesthetic training that enhances cross-modal processing

### Game Mechanics
- Three-phase gameplay (observation, reproduction, feedback)
- Progressive difficulty scaling (grid size and sequence length)
- Adaptive timing based on performance
- Score tracking and accuracy calculation

### User Interface
- Color-coded grid visualization
- Clear phase indicators
- Progressive feedback
- Theme-aware styling

## Integration

The module integrates with the MetaMindIQTrain platform through:

```python
from MetaMindIQTrain.modules.evolve.neural_synthesis.neural_synthesis_mvc import NeuralSynthesis

# Initialize the module
module = NeuralSynthesis(screen_width=800, screen_height=600)

# Handle user input
result = module.handle_click((x, y))

# Update module state
module.update(delta_time)

# Build UI
component_tree = module.build_component_tree()

# Render
module.render(renderer)
```

## Cognitive Training Benefits

The Neural Synthesis module targets several cognitive abilities:

1. **Cross-Modal Integration**
   - Strengthening connections between auditory and visual processing
   - Enhancing synesthetic awareness and processing

2. **Working Memory**
   - Holding pattern sequences in mind
   - Maintaining multi-sensory information

3. **Attention and Focus**
   - Maintaining focus during pattern observation
   - Filtering distractions during reproduction

4. **Cognitive Flexibility**
   - Adapting to changing patterns and sequences
   - Developing multiple strategies for memory encoding

## Usage

```python
# Initialize the module
module = NeuralSynthesis()

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
    component_tree = module.build_component_tree()
    # Use the component tree for rendering
```

## Configuration

The module can be adjusted through the model's properties:

- `grid_size`: Number of cells in each dimension of the grid (default: 4)
- `max_grid_size`: Maximum grid size (default: 8)
- `sequence_length`: Number of pattern elements (default: 4)
- `max_sequence_length`: Maximum sequence length (default: 12)
- `pattern_display_time`: Time to observe pattern in ms (default: 4000)
- `trials_per_level`: Number of trials before level advancement (default: 3)

## Dependencies

- Python 3.8+
- MetaMindIQTrain core modules 