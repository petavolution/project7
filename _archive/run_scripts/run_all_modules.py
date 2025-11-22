#!/usr/bin/env python3
"""
Run All Modules with Enhanced Generic Renderer

This script loads and runs all available training modules in sequence,
with support for both headless mode and interactive mode with display.
It serves as a comprehensive test to verify all modules are functioning correctly.
"""

import os
import sys
import time
import argparse
import logging
import pygame
from pathlib import Path

# Add the project root to the Python path
script_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(script_dir))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('ModuleRunner')

# Import module registry from MetaMindIQTrain
from MetaMindIQTrain.module_registry import create_module_instance, get_available_modules, configure_modules_display
from MetaMindIQTrain.config import SCREEN_WIDTH, SCREEN_HEIGHT, DEFAULT_FPS
from MetaMindIQTrain.clients.pygame.renderers.enhanced_generic_renderer import EnhancedGenericRenderer

def run_module(module_id, duration=10, headless=False, screen=None):
    """Run a specific module for a specified duration.
    
    Args:
        module_id: ID of the module to run
        duration: Duration in seconds to run the module
        headless: Whether to run in headless mode
        screen: PyGame screen surface (created if not provided)
        
    Returns:
        True if module ran successfully, False otherwise
    """
    try:
        # Create module instance
        module = create_module_instance(module_id)
        module_name = module.name
        
        logger.info(f"Running module: {module_name} (ID: {module_id})")
        
        # Create screen if not provided
        if screen is None:
            if headless:
                os.environ['SDL_VIDEODRIVER'] = 'dummy'
                screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
            else:
                screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
                pygame.display.set_caption(f"Running {module_name}")
        
        # Create fonts for the renderer
        fonts = {
            'small': pygame.font.SysFont("Arial", 18),
            'medium': pygame.font.SysFont("Arial", 24),
            'large': pygame.font.SysFont("Arial", 36),
            'title': pygame.font.SysFont("Arial", 48, bold=True)
        }
        
        # Create the enhanced generic renderer
        renderer = EnhancedGenericRenderer(screen, module_id, fonts=fonts)
        logger.info(f"Created renderer for {module_name}")
        
        # Initialize the module
        if hasattr(module, 'start_challenge'):
            module.start_challenge()
            logger.info(f"Started challenge for {module_name}")
        
        # Create a clock for framerate control
        clock = pygame.time.Clock()
        
        # Run the module for the specified duration
        start_time = time.time()
        frame_count = 0
        
        while time.time() - start_time < duration:
            # Process events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return False
            
            # Get the current state
            state = module.get_state()
            
            # Update the module if supported
            if hasattr(module, 'update'):
                module.update()
            
            # Clear the screen
            screen.fill((30, 30, 40))
            
            # Render the module
            renderer.render(state)
            
            # Show remaining time if not headless
            if not headless:
                time_left = int(duration - (time.time() - start_time))
                time_text = fonts['small'].render(f"Time remaining: {time_left}s", True, (255, 255, 255))
                screen.blit(time_text, (10, 10))
            
            # Update the display
            pygame.display.flip()
            
            # Cap the framerate
            clock.tick(DEFAULT_FPS)
            frame_count += 1
        
        # Calculate average FPS
        total_time = time.time() - start_time
        average_fps = frame_count / total_time if total_time > 0 else 0
        
        logger.info(f"Module {module_name} ran for {total_time:.2f} seconds")
        logger.info(f"Average FPS: {average_fps:.2f}")
        
        return True
    
    except Exception as e:
        logger.error(f"Error running module {module_id}: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all available modules."""
    parser = argparse.ArgumentParser(description="Run all training modules")
    parser.add_argument("--headless", action="store_true", help="Run in headless mode (no display)")
    parser.add_argument("--duration", type=int, default=10, help="Duration to run each module (seconds)")
    parser.add_argument("--module", type=str, help="Run a specific module by ID")
    args = parser.parse_args()
    
    # Initialize PyGame
    pygame.init()
    
    # Configure display settings for all modules
    configure_modules_display(SCREEN_WIDTH, SCREEN_HEIGHT)
    
    # Create screen
    if args.headless:
        os.environ['SDL_VIDEODRIVER'] = 'dummy'
        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        logger.info("Running in headless mode (no display)")
    else:
        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        logger.info(f"Running with display at {SCREEN_WIDTH}x{SCREEN_HEIGHT}")
    
    try:
        # Get available modules
        available_modules = get_available_modules()
        logger.info(f"Found {len(available_modules)} available modules:")
        for module_info in available_modules:
            logger.info(f" - {module_info['name']} ({module_info['id']})")
        
        # Run specific module if requested
        if args.module:
            found = False
            for module_info in available_modules:
                if module_info['id'] == args.module:
                    found = True
                    run_module(args.module, args.duration, args.headless, screen)
                    break
            
            if not found:
                logger.error(f"Module not found: {args.module}")
                return 1
        else:
            # Run all modules
            results = {}
            for module_info in available_modules:
                module_id = module_info['id']
                logger.info(f"\n{'='*80}\nRunning module: {module_info['name']} ({module_id})\n{'='*80}")
                success = run_module(module_id, args.duration, args.headless, screen)
                results[module_id] = "SUCCESS" if success else "FAILED"
            
            # Print summary
            logger.info("\n\nSummary of module tests:")
            logger.info("="*40)
            for module_id, result in results.items():
                logger.info(f"{module_id:20s} : {result}")
            
            # Overall status
            success_count = sum(1 for r in results.values() if r == "SUCCESS")
            logger.info(f"\nTotal modules: {len(results)}")
            logger.info(f"Successful: {success_count}")
            logger.info(f"Failed: {len(results) - success_count}")
            
            if success_count == len(results):
                logger.info("\nAll modules ran successfully!")
            else:
                logger.error("\nSome modules failed. See logs for details.")
                return 1
        
    except Exception as e:
        logger.error(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        pygame.quit()
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 