# MetaMindIQTrain Training Modules

This directory contains the training modules for the MetaMindIQTrain platform. Each module is a separate Python file that implements a cognitive training exercise.

## Available Modules

### Symbol Memory

**File:** `symbol_memory.py`

A memory training module where users have to remember symbol patterns and identify changes. This module improves working memory, pattern recognition, and visual recall abilities.

### Morph Matrix

**File:** `morph_matrix.py`

A pattern recognition module focused on identifying rotated vs. mutated patterns. This module enhances visual discrimination, pattern recognition, and mental rotation skills.

### Expand Vision

**File:** `expand_vision.py`

A peripheral vision training module where users focus on a central point while observing numbers in their peripheral vision. This module improves peripheral awareness, visual attention distribution, and multi-object tracking.

### Neural Flow

**File:** `neural_flow.py`

A cognitive processing module that visualizes neural networks with pulsing nodes and paths that users must interact with based on specific patterns. This innovative module enhances:
- Cognitive processing speed
- Neural pathway formation
- Visual-spatial processing
- Cognitive flexibility
- Dynamic attention allocation

The Neural Flow module creates a dynamic neural network visualization with nodes and connections. As users progress through levels, the network becomes more complex, requiring faster responses and better pattern recognition.

### Quantum Memory

**File:** `quantum_memory.py`

A cutting-edge memory and cognition module based on quantum-inspired mechanics. This module creates a unique training experience by leveraging concepts from quantum physics such as superposition and entanglement. Users must memorize states that exist in multiple possible configurations simultaneously and then make strategic choices to "collapse" them correctly.

Key benefits include:
- Working memory enhancement
- Strategic thinking development
- Cognitive flexibility
- Adaptation to uncertainty
- Mental processing speed
- Pattern recognition in complex systems

The Quantum Memory module introduces increasingly complex quantum states as users progress, with entangled pairs that require understanding relationships between elements. The novel approach creates an engaging challenge that adapts to the user's performance, pushing cognitive boundaries in ways traditional memory exercises cannot.

## Creating New Modules

To create a new training module:

1. Create a new Python file in this directory
2. Implement a class that inherits from `BaseModule` in `MetaMindIQTrain.modules.base_module`
3. Implement the required methods: `__init__`, `get_state`, and `handle_input`
4. Register the module in `MetaMindIQTrain.module_registry.py`
5. Add the module to the server's module provider in `MetaMindIQTrain.server.module_provider.py`

See the existing modules for examples of how to implement a training module.

## Module Interface

Each module must implement the following interface:

- `__init__(self, config=None)`: Initialize the module with optional configuration
- `get_state(self) -> Dict[str, Any]`: Get the current state of the module
- `handle_input(self, input_data: Dict[str, Any]) -> Dict[str, Any]`: Handle user input

The state returned by `get_state` should include all information needed to render the module. The `handle_input` method should process user input and return a response indicating success or failure.

## Module Lifecycle

1. The module is initialized when a user starts a session
2. The server calls `get_state` to get the initial state
3. The client renders the module based on the state
4. When the user interacts with the module, the client sends input to the server
5. The server calls `handle_input` to process the input
6. The server calls `get_state` to get the updated state
7. The client renders the updated state
8. Steps 4-7 repeat until the session ends

## Renderers

Each module can have a specialized renderer in the client. The renderer is responsible for displaying the module's state on the screen. If a specialized renderer is not available, the client will use a generic renderer.

See `MetaMindIQTrain.clients.pygame.renderers` for examples of module renderers. 