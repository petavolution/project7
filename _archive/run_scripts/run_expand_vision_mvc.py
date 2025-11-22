#!/usr/bin/env python3
"""
ExpandVision MVC Test Launcher

This script launches the ExpandVision module with the new MVC architecture,
providing a standalone test environment to verify the implementation.

Key features:
1. Independent pygame window
2. Full MVC component testing
3. Performance monitoring
4. Theme support
5. Animation effects
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
    from MetaMindIQTrain.modules.expand_vision_mvc import ExpandVision
    from MetaMindIQTrain.clients.pygame.renderers.expand_vision_mvc_renderer import ExpandVisionGridMVCRenderer
    from MetaMindIQTrain.clients.pygame.renderer_adapter import create_mvc_renderer
    from MetaMindIQTrain.core.theme_manager import ThemeManager
except ImportError as e:
    print(f"Error importing modules: {e}")
    sys.exit(1)

def main():
    """Main entry point for the ExpandVision MVC test launcher."""
    # Initialize pygame
    pygame.init()
    
    # Set up the window
    screen_width = 1024
    screen_height = 768
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("ExpandVision MVC Test")
    
    # Set platform for theme manager
    ThemeManager.set_platform("pygame")
    
    # Initialize fonts
    title_font = pygame.font.SysFont("arial", 24)
    regular_font = pygame.font.SysFont("arial", 18)
    small_font = pygame.font.SysFont("arial", 14)
    
    # Create clock for FPS limiting
    clock = pygame.time.Clock()
    
    # Create the ExpandVision module
    module = ExpandVision()
    
    # Create the renderer
    renderer = ExpandVisionGridMVCRenderer(
        screen=screen,
        title_font=title_font,
        regular_font=regular_font,
        small_font=small_font
    )
    
    # Set up event handlers
    renderer.set_event_handlers(
        on_select_answer=lambda value: handle_select_answer(module, value)
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
                    renderer.show_debug = not renderer.show_debug
                elif event.key == pygame.K_t:
                    # Switch theme
                    current_theme = ThemeManager._current_theme
                    new_theme = "light" if current_theme == "default" else "default"
                    ThemeManager.set_current_theme(new_theme)
                    print(f"Switched to {new_theme} theme")
                elif event.key == pygame.K_r:
                    # Reset module
                    module.process_input({"action": "reset"})
                    print("Module reset")
            
            # Let the renderer handle the event first
            if renderer.handle_event(event, module.get_state()):
                continue
            
            # Direct click handling as backup
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                module.handle_click(event.pos[0], event.pos[1])
        
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

def handle_select_answer(module, value):
    """Handle answer selection.
    
    Args:
        module: ExpandVision module instance
        value: Selected answer value
    """
    result = module.process_input({"action": "select_answer", "value": value})
    
    # Print result for debugging
    if "correct" in result:
        correct = result["correct"]
        score_change = result.get("score_change", 0)
        print(f"Answer {value} submitted: {'Correct!' if correct else 'Incorrect.'} Score change: {score_change}")

if __name__ == "__main__":
    main() 