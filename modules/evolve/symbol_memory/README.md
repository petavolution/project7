# Symbol Memory Module

## Overview
Symbol Memory is a cognitive training module focused on enhancing visual working memory, attention to detail, and pattern recognition. This module challenges users to memorize a grid of symbols and then identify whether any changes have been made to the pattern, requiring focused attention and strong visual memory skills.

## How It Works
The module follows a multi-phase process for each challenge:

1. **Memorize Phase**: Users are shown a grid of symbols to memorize within a time limit
2. **Hidden Phase**: The symbols are briefly hidden to enforce mental rehearsal
3. **Compare Phase**: A potentially modified version of the pattern is displayed
4. **Answer Phase**: Users must identify whether the pattern was modified or remained the same
5. **Feedback Phase**: Immediate feedback is provided, along with scoring

## Module Structure
The Symbol Memory module follows the Model-View-Controller (MVC) pattern for clean separation of concerns:

- **symbol_memory_mvc.py**: The main module file that integrates all components
- **symbol_memory_model.py**: Manages game state, symbol generation, and scoring logic
- **symbol_memory_view.py**: Handles UI rendering and layout calculations
- **symbol_memory_controller.py**: Processes user input and manages interactions

## Key Features

### Visual Memory Training
- Various colorful symbols are used to enhance multisensory encoding
- Grid sizes increase with difficulty level (2×2 up to 6×6)
- Symbols are strategically placed for optimized memory challenges

### Adaptive Difficulty
- Grid size increases with player level
- Memorization time adjusts based on skill level
- Number of symbols increases with difficulty
- Modification types vary (changing, moving, adding, or removing symbols)

### Responsive Design
- Automatically adjusts to different screen sizes
- Calculates optimal layout based on available space
- Maintains usability across devices

### Theme-Aware Styling
- Uses ThemeManager for consistent visual styling
- Adapts to light/dark themes
- Visual cues for feedback and important information

## Cognitive Training Benefits
- Enhances visual working memory capacity
- Improves pattern recognition abilities
- Develops attention to detail
- Trains rapid visual processing
- Builds change detection skills

## Integration
Symbol Memory integrates with the MetaMindIQTrain platform as a training module, providing:

- Consistent interface with other modules
- State management for session persistence
- Adaptive difficulty progression
- Performance tracking and scoring

## Usage

```python
from MetaMindIQTrain.modules.evolve.symbol_memory.symbol_memory_mvc import SymbolMemory

# Create the module with initial difficulty level (1-10)
module = SymbolMemory(difficulty=3)

# Initialize UI dimensions
module.view.set_dimensions(800, 600)

# Get the UI component tree for rendering
ui_tree = module.build_ui()

# Handle user interactions
result = module.handle_click(x, y)
``` 