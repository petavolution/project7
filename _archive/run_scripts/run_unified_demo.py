#!/usr/bin/env python3
"""
Unified MetaMindIQTrain Demo with Enhanced Theme System

This script demonstrates the MetaMindIQTrain system with:
- Enhanced theme-aware rendering
- Resolution-independent layout
- Dynamic module switching
"""

import pygame
import sys
import time
import os
import random
import argparse
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

# Import MetaMindIQTrain components
from MetaMindIQTrain.module_registry import get_available_modules, create_module_instance
from MetaMindIQTrain.clients.pygame.renderers.enhanced_generic_renderer import EnhancedGenericRenderer
from MetaMindIQTrain.core.theme import Theme, ThemeProvider, set_theme
from MetaMindIQTrain.config import SCREEN_WIDTH, SCREEN_HEIGHT, DEFAULT_FPS, calculate_sizes

# Initialize themes
DARK_THEME = Theme.dark_theme()
LIGHT_THEME = Theme.light_theme()

def run_demo(width=1440, height=1024, module_id=None, fps=DEFAULT_FPS, fullscreen=False, theme_name="dark"):
    """Run the unified demo with the enhanced theme system.
    
    Args:
        width: Screen width
        height: Screen height
        module_id: ID of the module to run
        fps: Target frames per second
        fullscreen: Whether to run in fullscreen mode
        theme_name: Theme to use ("dark" or "light")
    """
    # Initialize pygame
    pygame.init()
    
    # Set up display
    if fullscreen:
        screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        screen_width, screen_height = screen.get_size()
    else:
        screen = pygame.display.set_mode((width, height))
        screen_width, screen_height = width, height
    
    pygame.display.set_caption("MetaMindIQTrain Enhanced Demo")
    
    # Load fonts
    sizes = calculate_sizes(screen_width, screen_height)
    
    title_font = pygame.font.SysFont('Arial', sizes['TITLE_FONT_SIZE'])
    regular_font = pygame.font.SysFont('Arial', sizes['REGULAR_FONT_SIZE'])
    small_font = pygame.font.SysFont('Arial', sizes['SMALL_FONT_SIZE'])
    
    fonts = {
        'title': title_font,
        'regular': regular_font,
        'small': small_font
    }
    
    # Initialize theme
    theme = DARK_THEME if theme_name.lower() == "dark" else LIGHT_THEME
    set_theme(theme)
    
    # Available modules
    available_modules = get_available_modules()
    module_ids = [module['id'] for module in available_modules]
    
    # Default module
    if not module_id:
        if module_ids:
            module_id = module_ids[0]
        else:
            print("No modules available!")
            return
    
    # Create module instance
    current_module = create_module_instance(module_id)
    if not current_module:
        print(f"Failed to create module {module_id}")
        return
    
    # Create renderer
    renderer = EnhancedGenericRenderer(
        screen, 
        module_id, 
        fonts=fonts, 
        width=SCREEN_WIDTH,
        height=SCREEN_HEIGHT
    )
    
    # Set up clock for controlling framerate
    clock = pygame.time.Clock()
    
    # Game loop
    running = True
    next_module_time = time.time() + 20  # Switch modules every 20 seconds
    
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE:
                    # Switch module on spacebar
                    next_module_id = random.choice(module_ids)
                    current_module = create_module_instance(next_module_id)
                    renderer.set_active_module(next_module_id)
                    next_module_time = time.time() + 20
                elif event.key == pygame.K_t:
                    # Toggle theme
                    if theme == DARK_THEME:
                        theme = LIGHT_THEME
                    else:
                        theme = DARK_THEME
                    set_theme(theme)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Get click position
                x, y = event.pos
                # Handle click
                if current_module:
                    # Scale coordinates back to logical coordinates used by the module
                    logical_x = int(x * SCREEN_WIDTH / screen_width)
                    logical_y = int(y * SCREEN_HEIGHT / screen_height)
                    current_module.handle_click(logical_x, logical_y)
        
        # Auto-switch modules for the demo
        if time.time() > next_module_time:
            next_module_id = random.choice(module_ids)
            if next_module_id != module_id:
                module_id = next_module_id
                current_module = create_module_instance(module_id)
                renderer.set_active_module(module_id)
                next_module_time = time.time() + 20
        
        # Update module state
        current_module.update(1.0 / fps)
        
        # Clear screen
        screen.fill(theme.get_color("background"))
        
        # Render module
        state = current_module.get_state()
        renderer.render(state)
        
        # Show FPS
        fps_text = small_font.render(f"FPS: {int(clock.get_fps())}", True, theme.get_color("text_secondary"))
        screen.blit(fps_text, (10, 10))
        
        # Show current module name
        module_text = small_font.render(f"Module: {current_module.name}", True, theme.get_color("text_secondary"))
        screen.blit(module_text, (10, 40))
        
        # Show controls
        controls_text = small_font.render("Space: Switch Module | T: Toggle Theme | Esc: Exit", True, theme.get_color("text_secondary"))
        screen.blit(controls_text, (10, screen_height - 30))
        
        # Update display
        pygame.display.flip()
        
        # Cap the framerate
        clock.tick(fps)
    
    # Clean up
    pygame.quit()

def main():
    """Parse command line arguments and run demo."""
    parser = argparse.ArgumentParser(description="Run the unified MetaMindIQTrain demo")
    parser.add_argument("--width", type=int, default=1440, help="Screen width")
    parser.add_argument("--height", type=int, default=1024, help="Screen height")
    parser.add_argument("--module", type=str, help="Module ID to run")
    parser.add_argument("--fps", type=int, default=DEFAULT_FPS, help="Target FPS")
    parser.add_argument("--fullscreen", action="store_true", help="Run in fullscreen mode")
    parser.add_argument("--theme", type=str, default="dark", choices=["dark", "light"], help="UI theme")
    
    args = parser.parse_args()
    
    run_demo(
        width=args.width,
        height=args.height,
        module_id=args.module,
        fps=args.fps,
        fullscreen=args.fullscreen,
        theme_name=args.theme
    )

if __name__ == "__main__":
    main() 