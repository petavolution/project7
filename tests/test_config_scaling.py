#!/usr/bin/env python3
"""
Test Configuration-Based UI Scaling

This script verifies that the UI elements scale correctly based on the configuration.
It displays a simple UI with all the standard layout elements at different resolutions.
If pygame is not available, it will test the scaling calculations only.
"""

import sys
import os
from pathlib import Path

# Add the project root to the Python path
# Adjust path to work from tests directory
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

# Import configuration and renderers
from MetaMindIQTrain.config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, DEFAULT_FONT,
    calculate_sizes
)
from MetaMindIQTrain.module_registry import configure_modules_display

# Try to import pygame, but don't fail if not available
PYGAME_AVAILABLE = False
try:
    import pygame
    PYGAME_AVAILABLE = True
    print(f"pygame-ce {pygame.__version__} (SDL {pygame.get_sdl_version()})")
    print(f"Using {pygame.__name__} {pygame.__version__}")
except ImportError:
    print("Warning: pygame not available, running calculation-only test")


class ConfigScalingTester:
    """Test class to verify configuration-based UI scaling."""
    
    def __init__(self):
        """Initialize the tester with various screen resolutions."""
        # Only initialize pygame if available
        if PYGAME_AVAILABLE:
            pygame.init()
        
        # Define test resolutions
        self.resolutions = [
            (1440, 1024),  # Default configuration
            (1920, 1080),  # Full HD
            (1280, 720),   # HD Ready
            
        ]
        
    def run_test(self):
        """Run the scaling test for all resolutions."""
        print("Testing UI scaling for multiple resolutions...")
        
        for width, height in self.resolutions:
            print(f"\nTesting resolution: {width}x{height}")
            if PYGAME_AVAILABLE:
                self._test_resolution(width, height)
            else:
                # Test scaling calculations only
                self._test_scaling_calculation(width, height)
            
        if PYGAME_AVAILABLE:
            print("\nTesting complete. Press any key to exit.")
            self._wait_for_keypress()
        else:
            print("\nCalculation testing complete.")
            
    def _test_scaling_calculation(self, width, height):
        """Test the scaling calculations without pygame visualization."""
        # Configure the module display with this resolution
        configure_modules_display(width, height)
        
        # Calculate sizes and print them
        sizes = calculate_sizes(width, height)
        print(f"Calculated sizes for {width}x{height}:")
        for key, value in sizes.items():
            print(f"  {key}: {value}")
        
        # Verify some key calculations
        margin = sizes['UI_MARGIN']
        expected_margin = int(min(width, height) * 0.01)  # 1% of min dimension
        margin_correct = margin == expected_margin
        
        padding = sizes['UI_PADDING']
        expected_padding = int(min(width, height) * 0.02)  # 2% of min dimension
        padding_correct = padding == expected_padding
        
        print(f"Margin calculation correct: {margin_correct} ({margin} == {expected_margin})")
        print(f"Padding calculation correct: {padding_correct} ({padding} == {expected_padding})")
        
        return margin_correct and padding_correct
    
    def _test_resolution(self, width, height):
        """Test scaling for a specific resolution.
        
        Args:
            width: Screen width
            height: Screen height
        """
        # Create the window at the specified resolution
        screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption(f"Scaling Test: {width}x{height}")
        
        # Configure modules for this resolution
        configure_modules_display(width, height)
        
        # Calculate sizes for this resolution
        sizes = calculate_sizes(width, height)
        
        # Create fonts
        title_font = pygame.font.SysFont(DEFAULT_FONT, sizes['TITLE_FONT_SIZE'], bold=True)
        regular_font = pygame.font.SysFont(DEFAULT_FONT, sizes['REGULAR_FONT_SIZE'])
        small_font = pygame.font.SysFont(DEFAULT_FONT, sizes['SMALL_FONT_SIZE'])
        
        # Create the renderer for this resolution
        try:
            from MetaMindIQTrain.clients.pygame.renderers.base_renderer import BaseRenderer
            renderer = BaseRenderer(screen, title_font, regular_font, small_font)
            
            # Create a simple state for rendering
            state = {
                'module_name': 'UI Scaling Test',
                'description': f'Testing UI scaling at {width}x{height}',
                'level': 1,
                'score': 100,
                'help_text': 'Press any key to continue to the next resolution'
            }
            
            # Clear the screen and draw the standard layout
            screen.fill((240, 240, 245))
            renderer.draw_standard_layout(state)
            
            # Draw test patterns in the content area to verify scaling
            self._draw_test_patterns(renderer, state)
            
            # Update the display
            pygame.display.flip()
            
            # Wait for a keypress
            self._wait_for_keypress()
            
        except Exception as e:
            print(f"Error testing resolution {width}x{height}: {e}")
    
    def _draw_test_patterns(self, renderer, state):
        """Draw test patterns in the content area.
        
        Args:
            renderer: BaseRenderer instance
            state: State dictionary
        """
        # Get the content area
        content_rect = renderer.get_content_rect()
        
        # Draw a grid of percentage-based boxes
        grid_rows = 3
        grid_cols = 4
        
        for row in range(grid_rows):
            for col in range(grid_cols):
                # Calculate percentage position within the content area
                x_percent = 0.1 + (col * 0.2)
                y_percent = 0.2 + (row * 0.25)
                
                # Content area starts at the top of content_rect
                x = content_rect.x + int(x_percent * content_rect.width)
                y = content_rect.y + int(y_percent * content_rect.height)
                
                # Draw a box at percentage positions
                box_width = int(0.15 * content_rect.width)
                box_height = int(0.15 * content_rect.height)
                
                box_rect = pygame.Rect(
                    x - box_width // 2,
                    y - box_height // 2,
                    box_width,
                    box_height
                )
                
                # Draw box with alternating colors
                color = (100, 150, 200) if (row + col) % 2 == 0 else (150, 200, 100)
                pygame.draw.rect(renderer.screen, color, box_rect)
                pygame.draw.rect(renderer.screen, (30, 30, 30), box_rect, 2)
                
                # Draw position text
                position_text = f"{int(x_percent*100)}%, {int(y_percent*100)}%"
                renderer.draw_text(position_text, box_rect.centerx, box_rect.centery, renderer.small_font)
    
    def _wait_for_keypress(self):
        """Wait for any key to be pressed."""
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    waiting = False


if __name__ == "__main__":
    tester = ConfigScalingTester()
    tester.run_test()
    # Only quit pygame if it was initialized
    if PYGAME_AVAILABLE:
        pygame.quit()
    print("Test complete") 