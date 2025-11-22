#!/usr/bin/env python3
"""
Test Module With UI

This script runs a specified module with full UI, using the BaseRenderer.
It allows visual verification that the UI is scaling correctly.
"""

import sys
import os
import pygame
import argparse
from pathlib import Path

# Add project root to Python path
# Adjust path to work from tests directory
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

# Import from MetaMindIQTrain
from MetaMindIQTrain.module_registry import create_module_instance, configure_modules_display
from MetaMindIQTrain.config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, DEFAULT_FONT,
    calculate_sizes
)

def main():
    """Run a module with the standard BaseRenderer for UI scaling test."""
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Test module with full UI.")
    parser.add_argument(
        "module", 
        type=str, 
        choices=["symbol_memory", "expand_vision", "morph_matrix", "test_module"],
        default="symbol_memory",
        nargs="?",
        help="Module ID to run (default: symbol_memory)"
    )
    args = parser.parse_args()
    
    # Initialize pygame
    pygame.init()
    print(f"Using {pygame.__name__} {pygame.__version__}")
    
    # Set up display
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption(f"UI Scaling Test - {args.module}")
    
    # Configure modules display
    configure_modules_display(SCREEN_WIDTH, SCREEN_HEIGHT)
    
    # Calculate sizes
    sizes = calculate_sizes(SCREEN_WIDTH, SCREEN_HEIGHT)
    
    # Create fonts
    title_font = pygame.font.SysFont(DEFAULT_FONT, sizes['TITLE_FONT_SIZE'], bold=True)
    regular_font = pygame.font.SysFont(DEFAULT_FONT, sizes['REGULAR_FONT_SIZE'])
    small_font = pygame.font.SysFont(DEFAULT_FONT, sizes['SMALL_FONT_SIZE'])
    
    # Create module
    try:
        # Create a unique session ID
        import uuid
        session_id = str(uuid.uuid4())
        
        # Create module instance
        module = create_module_instance(args.module, session_id)
        print(f"Created module: {module.name} (Level {module.level})")
        
        # Create BaseRenderer
        from MetaMindIQTrain.clients.pygame.renderers.base_renderer import BaseRenderer
        renderer = BaseRenderer(screen, title_font, regular_font, small_font)
        
        # Start the module
        if hasattr(module, 'start_challenge'):
            module.start_challenge()
        
        # Create clock
        clock = pygame.time.Clock()
        
        # Main loop
        running = True
        while running:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_SPACE:
                        # Start challenge
                        if hasattr(module, 'start_challenge'):
                            module.start_challenge()
                    elif event.key == pygame.K_a:
                        # Advance level
                        if hasattr(module, 'advance_level'):
                            module.advance_level()
                    elif event.key == pygame.K_r:
                        # Reset level
                        if hasattr(module, 'reset_level'):
                            module.reset_level()
            
            # Get current state
            state = module.get_state()
            
            # Draw state using BaseRenderer
            renderer.draw_standard_layout(state)
            
            # Update the display
            pygame.display.flip()
            
            # Cap framerate
            clock.tick(60)
        
        # Cleanup
        pygame.quit()
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        pygame.quit()
        sys.exit(1)

if __name__ == "__main__":
    main() 