# MetaMindIQTrain Test Suite

This directory contains tests for the MetaMindIQTrain cognitive training platform.

## Directory Structure

- `modules/`: Tests for individual training modules
- `integration/`: Integration tests for server-client communication
- `core/`: Tests for core components and utilities
- `server/`: Tests for server functionality

## Running Tests

You can run the tests using the `run_tests.py` script:

```bash
# Run all tests
python tests/run_tests.py

# Run tests for a specific module
python tests/run_tests.py -m module_loading

# List available test modules
python tests/run_tests.py -l
```

## Test Types

### Module Tests
Tests that verify each training module can be loaded, instantiated, and interacted with correctly.

Key tests:
- `test_module_loading.py`: Verifies modules can be imported and instantiated
- `test_module_interaction.py`: Tests click handling and interaction
- `test_module_state.py`: Validates state management and progression

### Integration Tests
Tests that verify the server-client communication and module selection process.

Key tests:
- `test_server_client.py`: Tests API endpoints and session management

## Adding New Tests

To add a new test:

1. Create a new Python file with a name starting with `test_` in the appropriate directory
2. Inherit from `unittest.TestCase`
3. Implement test methods (names should start with `test_`)
4. Add the new test to `run_tests.py` if necessary

## Test Requirements

The tests require the following dependencies:

- Python 3.8+
- pytest (optional, for more advanced test features)
- requests (for API testing)

These are already included in the main project requirements.txt file.

## Test Categories

The tests are organized into several categories:

1. **Module Tests**: Tests for individual training modules
2. **Core System Tests**: Tests for the core system components
3. **Neural Module Tests**: Tests for neural pattern generation and quantum state components
4. **Integration Tests**: Tests that verify the interaction between components
5. **UI Tests**: Tests for the user interface components

## Test Scripts

- `check_all_modules.py`: Checks that all modules can be loaded successfully
- `check_modules.py`: Provides information about available modules
- `check_module_logic.py`: Tests core module logic without requiring UI interaction
- `test_modules_core.py`: Tests core functionality of each module
- `test_config_scaling.py`: Tests UI scaling configuration for different screen sizes
- `test_module_with_ui.py`: Interactive test for a specific module with UI
- `update_test_config.py`: Utility to update test configuration settings
- `run_all_tests.py`: Runs all tests in sequence, with interactive tests at the end
- `run_headless_tests.py`: Runs all non-interactive tests without requiring user input

## Running Tests

### All Tests

To run all tests, use the `run_all_tests.py` script:

```bash
python tests/run_all_tests.py
```

You can run specific test categories with command-line arguments:

```bash
# Run only neural module tests
python tests/run_all_tests.py --neural-only

# Run tests with a specific pattern
python tests/run_all_tests.py --pattern "test_neural_*.py"

# Generate XML report
python tests/run_all_tests.py --xml test_report.xml
```

### Neural Module Tests

The neural module tests are specifically focused on testing the neural pattern generation, quantum state, and network optimization components. These components form the foundation of the adaptive challenge generation system.

To run only the neural module tests:

```bash
python tests/neural_module_tests/run_all_neural_tests.py
```

## Test Environment

Tests use the Python `unittest` framework and can be run with or without a virtual environment. For consistency, it's recommended to use the project's virtual environment:

```bash
source metamind_venv/bin/activate
python tests/run_all_tests.py
```

## Adding New Tests

When adding new tests:

1. Place the test file in the appropriate directory
2. Follow the naming convention: `test_*.py`
3. Use the `unittest` framework
4. Ensure the test can run both standalone and as part of the test suite

For neural module tests, add them to the `neural_module_tests` directory.

## Test Dependencies

Tests require the following packages, which are included in `requirements.txt`:

- pytest
- pytest-cov
- numpy
- scipy
- matplotlib
- scikit-learn

## Development Workflow

During development, it's recommended to:

1. Write tests before implementing new features
2. Run specific test modules during development
3. Run the full test suite before submitting changes

This ensures that changes don't break existing functionality and that new features work as expected.

## Environment Variables

- `SDL_VIDEODRIVER`: Set to `dummy` for headless testing (no window will appear)

Example:

```bash
SDL_VIDEODRIVER=dummy python tests/run_all_tests.py --noninteractive
```

## Available Tests

### 1. Module Loading Test
Verifies that all modules can be loaded and initialized in headless mode.

```bash
python tests/check_all_modules.py
```

### 2. UI Scaling Test
Tests that UI elements scale correctly at different resolutions.

```bash
python tests/test_config_scaling.py
```

### 3. Module UI Test
Tests a specific module with full UI rendering.

```bash
python tests/test_module_with_ui.py symbol_memory
```

Available modules:
- `symbol_memory`
- `expand_vision`
- `morph_matrix`
- `test_module`

### 4. Core Module Logic Test
Tests the core module logic without requiring pygame for rendering.

```bash
python tests/test_modules_core.py
```

### 5. Module Logic Check
Simple check to verify the core functionality of modules without visual components.

```bash
python tests/check_module_logic.py
```

### 6. All Modules Check
Tests if all modules can be loaded with pygame.

```bash
python tests/check_modules.py
```

## Updating Configuration

To update configuration settings like screen dimensions across all tests, use the `update_test_config.py` script:

```bash
python tests/update_test_config.py
```

This script will guide you through updating the screen dimensions in the configuration file. After updating, you should run the tests to verify that everything works correctly with the new settings.

## Documentation

- `module_tests_summary.md`: Contains a summary of module test results
- `resolution_update_summary.md`: Documents the changes made for resolution support

## Requirements

All tests require the dependencies listed in `MetaMindIQTrain/requirements.txt`:

```
pygame-ce>=2.5.3  # Community edition of pygame
numpy>=2.2.4
pillow>=11.1.0
```

## Running Tests

Make sure you're in the project root directory (not in the tests directory) when running these tests. 