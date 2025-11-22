# MorphMatrix Module

## Overview
MorphMatrix is a cognitive training module focused on pattern recognition and visual-spatial reasoning. This module challenges users to distinguish between pure rotations of a pattern versus modified variations, requiring focused attention and careful analysis of visual details.

## How It Works
1. The user is presented with a reference pattern (indicated with a blue outline)
2. Multiple pattern variations are displayed, some being exact rotations of the original pattern and some having subtle modifications
3. The user must select all patterns that are exact rotations of the original (without modifications)
4. After submitting answers, the module provides immediate feedback and scoring
5. Difficulty progressively increases with correct answers

## Module Structure
The MorphMatrix module follows the Model-View-Controller (MVC) pattern for clean separation of concerns:

- **morph_matrix_mvc.py**: The main module file that integrates all components
- **morph_matrix_model.py**: Manages game state, pattern generation, and scoring logic
- **morph_matrix_view.py**: Handles UI rendering and layout calculations
- **morph_matrix_controller.py**: Processes user input and manages interactions

## Key Features

### Pattern Recognition
- Binary matrices displayed in a grid layout
- Pattern variations include pure rotations (0°, 90°, 180°, 270°)
- Modified patterns have subtle bit changes that must be detected

### Adaptive Difficulty
- Matrix size increases with player level (3×3 to 6×6)
- Number of modified patterns varies (1-4) for increasing challenge
- Scoring rewards speed and accuracy

### Responsive Design
- Automatically adjusts to different screen sizes
- Calculates optimal layout based on available space
- Maintains usability across devices

### Theme-Aware Styling
- Uses ThemeManager for consistent visual styling
- Adapts to light/dark themes
- Visual cues for selection and feedback states

## Cognitive Training Benefits
- Enhances visual-spatial reasoning
- Improves pattern recognition abilities
- Trains working memory and attention to detail
- Develops cognitive flexibility through rotation analysis

## Integration
MorphMatrix integrates with the MetaMindIQTrain platform as a training module, providing:

- Consistent interface with other modules
- State management for session persistence
- Adaptive difficulty progression
- Performance tracking and scoring

## Usage

```python
from MetaMindIQTrain.modules.evolve.morph_matrix.morph_matrix_mvc import MorphMatrix

# Create the module with initial difficulty level (1-10)
module = MorphMatrix(difficulty=3)

# Initialize UI dimensions
module.view.set_dimensions(800, 600)

# Get the UI component tree for rendering
ui_tree = module.build_ui()

# Handle user interactions
result = module.handle_click(x, y)
``` 