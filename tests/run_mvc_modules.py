#!/usr/bin/env python3
"""
Interactive MVC Module Runner for MetaMindIQTrain

This script allows running any of the MVC-based modules interactively
with a Pygame window. It supports command-line arguments to specify
which module to run and provides a consistent interface for all modules.

Usage:
    python run_mvc_modules.py [module_name] [--difficulty N] [--debug]

Modules:
    symbol_memory - SymbolMemory training module
    morph_matrix - MorphMatrix training module
    expand_vision - ExpandVision training module
    
Options:
    --difficulty N - Set difficulty level (1-10, default: 3)
    --debug - Enable debug information display
"""

import os
import sys
import time
import argparse
import pygame
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import needed components
try:
    # Try direct imports based on the current directory structure
    from modules.symbol_memory_mvc import SymbolMemory as SymbolMemoryMVC
    from modules.morph_matrix_mvc import MorphMatrix as MorphMatrixMVC
    from MetaMindIQTrain.modules.expand_vision_Grid_mvc import ExpandVision as ExpandVisionMVC
    from core.theme_manager import ThemeManager
except ImportError as e:
    try:
        # Try with full paths as fallback
        from MetaMindIQTrain.modules.symbol_memory_mvc import SymbolMemory as SymbolMemoryMVC
        from MetaMindIQTrain.modules.morph_matrix_mvc import MorphMatrix as MorphMatrixMVC
        from MetaMindIQTrain.modules.expand_vision_Grid_mvc import ExpandVision as ExpandVisionMVC
        from MetaMindIQTrain.core.theme_manager import ThemeManager
    except ImportError as e:
        print(f"Error importing modules: {e}")
        sys.exit(1)

# Import renderers - attempt to find them in both possible locations
try:
    # Try direct imports first
    from clients.pygame.renderers.symbol_memory_mvc_renderer import SymbolMemoryMVCRenderer
    from clients.pygame.renderers.morph_matrix_mvc_renderer import MorphMatrixMVCRenderer
    from clients.pygame.renderers.expand_vision_mvc_renderer import ExpandVisionGridMVCRenderer
except ImportError:
    try:
        # Try alternative import path
        from clients.pygame.renderers import (
            SymbolMemoryMVCRenderer,
            MorphMatrixMVCRenderer,
            ExpandVisionMVCRenderer
        )
    except ImportError:
        try:
            # Try with full paths as last resort
            from MetaMindIQTrain.clients.pygame.renderers.symbol_memory_mvc_renderer import SymbolMemoryMVCRenderer
            from MetaMindIQTrain.clients.pygame.renderers.morph_matrix_mvc_renderer import MorphMatrixMVCRenderer
            from MetaMindIQTrain.clients.pygame.renderers.expand_vision_mvc_renderer import ExpandVisionGridMVCRenderer
        except ImportError as e:
            print(f"Error importing renderers: {e}")
            print("Checking available renderer modules...")
            
            # Try to list available renderer modules to help diagnose
            try:
                import importlib.util
                clients_path = project_root / 'clients' / 'pygame' / 'renderers'
                if clients_path.exists():
                    print(f"Available files in {clients_path}:")
                    for file in clients_path.glob("*.py"):
                        print(f"  - {file.name}")
                else:
                    print(f"Renderer directory not found: {clients_path}")
            except Exception as e:
                print(f"Error checking renderers: {e}")
            
            sys.exit(1)


def parse_arguments():
    parser = argparse.ArgumentParser(description="Run MVC-based modules interactively")
    
    parser.add_argument(
        "module",
        nargs="?",
        choices=["symbol_memory", "morph_matrix", "expand_vision"],
        default="symbol_memory",
        help="Module to run (default: symbol_memory)"
    )
    
    parser.add_argument(
        "--difficulty",
        type=int,
        default=3,
        choices=range(1, 11),
        help="Difficulty level (1-10, default: 3)"
    )
    
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug information display"
    )
    
    parser.add_argument(
        "--width",
        type=int,
        default=1024,
        help="Screen width (default: 1024)"
    )
    
    parser.add_argument(
        "--height",
        type=int,
        default=768,
        help="Screen height (default: 768)"
    )
    
    return parser.parse_args()


def run_symbol_memory(difficulty, screen, debug=False):
    """Run the SymbolMemory MVC module.
    
    Args:
        difficulty: Difficulty level (1-10)
        screen: Pygame screen
        debug: Whether to show debug information
    """
    # Initialize fonts
    title_font = pygame.font.SysFont("arial", 24)
    regular_font = pygame.font.SysFont("arial", 18)
    small_font = pygame.font.SysFont("arial", 14)
    
    # Create module
    module = SymbolMemoryMVC(difficulty=difficulty)
    
    # Create renderer
    renderer = SymbolMemoryMVCRenderer(
        screen=screen,
        title_font=title_font,
        regular_font=regular_font,
        small_font=small_font
    )
    
    # Set up event handlers
    renderer.set_event_handlers(
        on_yes_click=lambda: module.process_input({"action": "answer_yes"}),
        on_no_click=lambda: module.process_input({"action": "answer_no"}),
        on_continue_click=lambda: module.process_input({"action": "continue"})
    )
    
    # Enable debug mode if requested
    renderer.show_debug = debug
    
    return module, renderer


def run_morph_matrix(difficulty, screen, debug=False):
    """Run the MorphMatrix MVC module.
    
    Args:
        difficulty: Difficulty level (1-10)
        screen: Pygame screen
        debug: Whether to show debug information
    """
    # Initialize fonts
    title_font = pygame.font.SysFont("arial", 24)
    regular_font = pygame.font.SysFont("arial", 18)
    small_font = pygame.font.SysFont("arial", 14)
    
    # Create module
    module = MorphMatrixMVC(difficulty=difficulty)
    
    # Create renderer
    renderer = MorphMatrixMVCRenderer(
        screen=screen,
        title_font=title_font,
        regular_font=regular_font,
        small_font=small_font
    )
    
    # Enable debug mode if requested
    renderer.show_debug = debug
    
    return module, renderer


def run_expand_vision(screen_width, screen_height, screen, debug=False):
    """Run the ExpandVision MVC module.
    
    Args:
        screen_width: Screen width
        screen_height: Screen height
        screen: Pygame screen
        debug: Whether to show debug information
    """
    # Initialize fonts
    title_font = pygame.font.SysFont("arial", 24)
    regular_font = pygame.font.SysFont("arial", 18)
    small_font = pygame.font.SysFont("arial", 14)
    
    # Create module
    module = ExpandVisionMVC(screen_width=screen_width, screen_height=screen_height)
    
    # Create renderer
    renderer = ExpandVisionGridMVCRenderer(
        screen=screen,
        title_font=title_font,
        regular_font=regular_font,
        small_font=small_font
    )
    
    # Enable debug mode if requested
    renderer.show_debug = debug
    
    return module, renderer


def main():
    # Parse arguments
    args = parse_arguments()
    
    # Initialize pygame
    pygame.init()
    
    # Set up the window
    screen = pygame.display.set_mode((args.width, args.height))
    pygame.display.set_caption(f"MetaMindIQTrain - {args.module.replace('_', ' ').title()} MVC Test")
    
    # Set platform for theme manager
    ThemeManager.set_platform("pygame")
    
    # Create clock for FPS limiting
    clock = pygame.time.Clock()
    
    # Initialize the selected module
    module = None
    renderer = None
    
    if args.module == "symbol_memory":
        module, renderer = run_symbol_memory(args.difficulty, screen, args.debug)
    elif args.module == "morph_matrix":
        module, renderer = run_morph_matrix(args.difficulty, screen, args.debug)
    elif args.module == "expand_vision":
        module, renderer = run_expand_vision(args.width, args.height, screen, args.debug)
    else:
        print(f"Unknown module: {args.module}")
        pygame.quit()
        sys.exit(1)
    
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


if __name__ == "__main__":
    main() 