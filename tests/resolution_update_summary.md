# Resolution and UI Layout Update

## Overview
This update implements a dynamic resolution-based UI system for MetaMindIQTrain. The application now runs at a resolution of 1440x1024 by default, with all UI elements defined as percentages of the total window size, ensuring proper scaling across different resolutions.

## Key Changes

### 1. Configuration Updates (`MetaMindIQTrain/config.py`)
- Set the default resolution to 1440x1024
- Converted all UI element dimensions to percentages of screen size
- Added a `calculate_sizes()` function to convert percentages to actual pixel values at runtime
- Created distinct background colors for different UI sections (header, content, footer)
- Adjusted layout proportions for better visual appeal:
  - Header: 15% of screen height
  - Content: 73% of screen height
  - Footer: 12% of screen height

### 2. Renderer Updates (`MetaMindIQTrain/clients/pygame/renderers/base_renderer.py`)
- Updated the BaseRenderer to use the percentage-based dimensions
- Added colored section backgrounds for clear visual separation
- Improved positioning of header elements (title, description)
- Added helper methods for percentage-based positioning:
  - `percent_to_pixels(percent_w, percent_h)`
  - `percent_x(percent)`
  - `percent_y(percent)`
  - `percent_rect(x_percent, y_percent, width_percent, height_percent)`
  - `get_content_rect()`

### 3. Module Runner Updates (`MetaMindIQTrain/run_module.py`)
- Updated to use the configuration-provided resolution
- Corrected renderer path mappings
- Added fallback to EnhancedGenericRenderer instead of BaseRenderer
- Added detailed logging of the resolution being used

### 4. Testing
- Created a test script (`test_config_scaling.py`) to verify UI scaling across different resolutions
- The test displays the standard layout with percentage-based test patterns in the content area

## UI Layout Sections

The UI is now clearly divided into three sections:

1. **Header (15% of height)**
   - Module title and description
   - Level and score indicators
   - Slightly darker background color for visual distinction

2. **Content (73% of height)**
   - Main module content area
   - Lighter background color for focus
   - All module-specific UI elements are positioned using percentages

3. **Footer (12% of height)**
   - Navigation buttons (New Challenge, Reset Level, Next Level)
   - Help text
   - Slightly darker background color matching the header

## Using Percentage-Based Dimensions

When developing modules, use the following methods from the BaseRenderer class:

```python
# Convert percentage to pixels
width_px, height_px = renderer.percent_to_pixels(0.5, 0.3)  # 50% width, 30% height

# Convert percentage of width to pixels
x_px = renderer.percent_x(0.5)  # 50% of width

# Convert percentage of height to pixels
y_px = renderer.percent_y(0.25)  # 25% of height

# Create a rect from percentages
rect = renderer.percent_rect(0.1, 0.2, 0.3, 0.4)  # x, y, width, height as percentages

# Get the content rect (the area between header and footer)
content_rect = renderer.get_content_rect()
```

## How to Test

1. Run the test script to verify UI scaling:
   ```
   ./test_config_scaling.py
   ```

2. Run any module with the standard runner:
   ```
   python MetaMindIQTrain/run_module.py symbol_memory
   ```

3. You can also test fullscreen mode:
   ```
   python MetaMindIQTrain/run_module.py expand_vision --fullscreen
   ```

## Conclusion

The UI is now fully responsive to different resolutions. If the configuration file's resolution is changed, all modules will automatically adjust their layout and elements accordingly. This ensures a consistent user experience across different screen sizes while maintaining a clear separation between UI sections. 