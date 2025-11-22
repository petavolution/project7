# Quantum Memory Module

## Overview
The Quantum Memory module implements an innovative cognitive training exercise that leverages quantum-inspired mechanics to enhance working memory, cognitive flexibility, and strategic thinking. It simulates quantum superposition and entanglement concepts to create a unique memory challenge that adapts to the user's performance.

## Features
- Quantum-inspired memory training
- Simulated superposition and entanglement mechanics
- Adaptive difficulty progression
- Performance tracking and feedback
- Multi-phase gameplay (preparation, memorize, recall, feedback)

## Module Structure
This module follows the Model-View-Controller (MVC) design pattern:

1. **Model** (`quantum_memory_model.py`): Handles the core game logic, including:
   - Quantum state generation and management
   - Game state management
   - Phase transitions
   - Scoring and performance tracking
   - Quantum collapse mechanics

2. **View** (`quantum_memory_view.py`): Handles the UI representation, including:
   - Component tree building
   - Layout calculations
   - Quantum state visualization
   - Theme-aware styling

3. **Controller** (`quantum_memory_controller.py`): Handles user interactions, including:
   - Input processing
   - Click detection
   - Action handling
   - State updates

4. **Main MVC Integration** (`quantum_memory_mvc.py`): Integrates all components into a cohesive module that inherits from BaseModule and interfaces with the MetaMindIQTrain framework.

## Game Mechanics
Quantum Memory simulates quantum physics concepts to create a cognitive challenge:

1. **Quantum States**: Each round presents a grid of quantum states, each existing in superposition between multiple possible values.

2. **Quantum Entanglement**: Some states are entangled, meaning they will collapse to the same value.

3. **Superposition**: Each quantum state can exist in multiple states simultaneously until observed.

4. **Collapse**: When observed (during recall phase), quantum states collapse to a single value.

## Gameplay Phases
The module operates in four distinct phases:

1. **Preparation Phase**: Introduces the training exercise and prepares the user.

2. **Memorize Phase**: Shows quantum states in superposition and their possible values. Users must memorize the states and notice which ones are entangled.

3. **Recall Phase**: Quantum states collapse, and users must select the correct values for each state.

4. **Feedback Phase**: Provides performance feedback and advances to the next level if successful.

## Usage
The module can be imported and used as follows:

```python
from MetaMindIQTrain.modules.evolve.quantum_memory.quantum_memory_mvc import QuantumMemory

# Create module instance with optional custom configuration
module = QuantumMemory(config={
    'screen_width': 1024,
    'screen_height': 768,
    'initial_quantum_states': 4,
    'entanglement_probability': 0.5,
    'superposition_states': 3
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