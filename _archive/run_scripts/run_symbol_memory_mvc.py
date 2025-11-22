#!/usr/bin/env python3
"""
Symbol Memory MVC Test Launcher

This is a simple launcher for testing the Symbol Memory MVC module
independently of the main application.
"""

import sys
import time
import pygame
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).resolve().parent))

# Import the module classes
try:
    from MetaMindIQTrain.modules.symbol_memory_mvc import SymbolMemory
    from MetaMindIQTrain.core.theme_manager import ThemeManager
    from MetaMindIQTrain.core.ui_renderer import UIRenderer
    from MetaMindIQTrain.core import config
except ImportError:
    # Try relative imports if we're already in the MetaMindIQTrain directory
    from modules.symbol_memory_mvc import SymbolMemory
    from core.theme_manager import ThemeManager
    from core.ui_renderer import UIRenderer
    from core import config

def handle_select_answer(module, answer):
    """Handle selecting an answer (yes/no).
    
    Args:
        module: SymbolMemory module instance
        answer: Boolean answer (True for yes, False for no)
    
    Returns:
        Result dictionary
    """
    return module.process_input({"action": "select_answer", "value": answer})

def handle_continue(module):
    """Handle clicking the continue button.
    
    Args:
        module: SymbolMemory module instance
    
    Returns:
        Result dictionary
    """
    return module.process_input({"action": "continue"})

def main():
    """Main entry point for the Symbol Memory MVC test launcher."""
    # Initialize pygame
    pygame.init()
    
    # Set up the window based on config
    screen_width, screen_height = config.get_resolution()
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Symbol Memory MVC Test")
    
    # Set platform for theme manager
    ThemeManager.set_platform("pygame")
    
    # Initialize fonts
    pygame.font.init()
    
    # Create clock for FPS limiting
    clock = pygame.time.Clock()
    
    # Create the Symbol Memory module
    module = SymbolMemory()
    
    # Create the UI renderer
    ui_renderer = UIRenderer(screen, screen_width, screen_height)
    
    # Game loop
    running = True
    last_time = time.time()
    
    while running:
        # Calculate dt
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
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    x, y = event.pos
                    result = module.handle_click(x, y)
        
        # Update module state
        module.update(dt)
        
        # Clear the screen
        screen.fill(config.COLORS["background"])
        
        # Render UI layout
        ui_renderer.render_layout()
        
        # Render header with title
        ui_renderer.render_header("Symbol Memory", "Memorize the pattern and identify changes")
        
        # Get current module state
        state = module.get_state()
        phase = state.get("phase", "")
        
        # Render grid using enhanced styling
        module.view.render_grid(ui_renderer)
        
        # Render buttons using enhanced styling
        module.view.render_buttons(ui_renderer)
        
        # Display score
        score_text = f"Score: {state.get('score', 0)}"
        ui_renderer.render_text(
            score_text,
            (screen_width - 100, 30),
            font_key="regular",
            color=config.UI_THEME["colors"]["text_light"],
            align="right"
        )
        
        # Debugging info
        fps = clock.get_fps()
        ui_renderer.render_text(
            f"FPS: {fps:.1f}",
            (10, screen_height - 20),
            font_key="small",
            color=config.UI_THEME["colors"]["text_dark"],
            align="left"
        )
        
        # Update display
        pygame.display.flip()
        
        # Limit FPS
        clock.tick(config.DISPLAY_CONFIG["fps_limit"])

if __name__ == "__main__":
    main() 