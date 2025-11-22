#!/usr/bin/env python3
"""
MorphMatrix MVC Test Launcher

This script launches the MorphMatrix module with the new MVC architecture,
providing a standalone test environment to verify the implementation.

Key features:
1. Independent pygame window
2. Full MVC component testing
3. Performance monitoring
4. Theme support
"""

import os
import sys
import time
import pygame
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

# Import needed components
try:
    from MetaMindIQTrain.modules.morph_matrix_mvc import MorphMatrix
    from MetaMindIQTrain.clients.pygame.renderers.morph_matrix_mvc_renderer import MorphMatrixMVCRenderer
    from MetaMindIQTrain.clients.pygame.renderer_adapter import create_mvc_renderer
    from MetaMindIQTrain.core.theme_manager import ThemeManager
except ImportError as e:
    print(f"Error importing modules: {e}")
    sys.exit(1)

def main():
    """Main entry point for the MorphMatrix MVC test launcher."""
    # Initialize pygame
    pygame.init()
    
    # Set up the window
    screen_width = 1024
    screen_height = 768
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("MorphMatrix MVC Test")
    
    # Set platform for theme manager
    ThemeManager.set_platform("pygame")
    
    # Initialize fonts
    title_font = pygame.font.SysFont("arial", 24)
    regular_font = pygame.font.SysFont("arial", 18)
    small_font = pygame.font.SysFont("arial", 14)
    
    # Create clock for FPS limiting
    clock = pygame.time.Clock()
    
    # Create the MorphMatrix module (default difficulty 3)
    module = MorphMatrix(difficulty=3)
    
    # Create the renderer
    renderer = MorphMatrixMVCRenderer(
        screen=screen,
        title_font=title_font,
        regular_font=regular_font,
        small_font=small_font
    )
    
    # Set up event handlers
    renderer.set_event_handlers(
        on_pattern_click=lambda idx: handle_pattern_click(module, idx),
        on_submit_click=lambda: handle_submit_click(module),
        on_next_click=lambda: handle_next_click(module, renderer)
    )
    
    # Enable debug mode
    renderer.show_debug = True
    
    # Game loop
    running = True
    last_time = time.time()
    
    while running:
        # Calculate dt (delta time)
        current_time = time.time()
        dt = current_time - last_time
        last_time = current_time
        
        # Process events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_d:
                    # Toggle debug mode
                    renderer.show_debug = not getattr(renderer, "show_debug", False)
                elif event.key == pygame.K_t:
                    # Switch theme
                    current_theme = ThemeManager._current_theme
                    new_theme = "light" if current_theme == "default" else "default"
                    ThemeManager.set_current_theme(new_theme)
                    print(f"Switched to {new_theme} theme")
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Direct event handling - alternative to component-based approach
                pass
            
            # Let the renderer handle the event first
            if renderer.handle_event(event, module.get_state()):
                continue
        
        # Update module state
        module.update(dt)
        
        # Render the current state
        renderer.render(module.get_state())
        
        # Update display
        pygame.display.flip()
        
        # Cap at 60 FPS
        clock.tick(60)
    
    # Clean up
    pygame.quit()
    sys.exit(0)

def handle_pattern_click(module, pattern_index):
    """Handle pattern click event.
    
    Args:
        module: MorphMatrix module instance
        pattern_index: Index of the clicked pattern
    """
    # Process the input
    module.process_input({
        "action": "select_pattern",
        "pattern_index": pattern_index
    })

def handle_submit_click(module):
    """Handle submit button click event.
    
    Args:
        module: MorphMatrix module instance
    """
    # Process the input
    result = module.process_input({
        "action": "submit"
    })
    
    # Print result for debugging
    correct = result.get("correct", False)
    score_change = result.get("score_change", 0)
    print(f"Answer submitted: {'Correct!' if correct else 'Incorrect.'} Score change: {score_change}")

def handle_next_click(module, renderer):
    """Handle next challenge button click event.
    
    Args:
        module: MorphMatrix module instance
        renderer: MorphMatrixMVCRenderer instance
    """
    # Process the input
    module.process_input({
        "action": "next_round"
    })
    
    # Print for debugging
    print("Starting next round")

if __name__ == "__main__":
    main() 