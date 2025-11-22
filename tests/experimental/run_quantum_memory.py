#!/usr/bin/env python3
"""
Run Quantum Memory Module

This script launches the Quantum Memory training module, which challenges users to track
multiple probability states simultaneously, enhancing working memory and cognitive flexibility.

Usage:
    python run_quantum_memory.py [--fullscreen] [--debug] [--duration SECONDS]

Options:
    --fullscreen    Run in fullscreen mode
    --debug         Enable debug logging
    --duration      Duration in seconds (default: 300)
"""

import sys
import os
import argparse
import logging
import pygame
import time
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add project directory to path
script_dir = Path(__file__).resolve().parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

# Import the quantum memory module and unified renderer
try:
    from MetaMindIQTrain.modules.quantum_memory import QuantumMemoryModule
    from MetaMindIQTrain.clients.unified.renderer import UnifiedRenderer
    from MetaMindIQTrain.clients.unified.pygame_adapter import PyGameAdapter
except ImportError as e:
    logger.error(f"Import error: {e}")
    sys.exit(1)

def main():
    """Run the Quantum Memory module visualization."""
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Run Quantum Memory training module")
    parser.add_argument("--fullscreen", action="store_true", help="Run in fullscreen mode")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    parser.add_argument("--duration", type=int, default=300, help="Duration in seconds (default: 300)")
    
    args = parser.parse_args()
    
    # Set logging level
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        
    # Initialize PyGame
    pygame.init()
    
    # Get screen info
    screen_info = pygame.display.Info()
    
    # Configure display settings
    if args.fullscreen:
        width = screen_info.current_w
        height = screen_info.current_h
    else:
        width = 1024
        height = 768
        
    # Create platform adapter and renderer
    adapter = PyGameAdapter(fullscreen=args.fullscreen)
    renderer = UnifiedRenderer(adapter, width=width, height=height)
    
    # Create quantum memory module
    module = QuantumMemoryModule()
    
    # Set window title
    pygame.display.set_caption("Quantum Memory Training")
    
    # Print instructions
    print("\nQuantum Memory Training")
    print("======================")
    print("This exercise trains your working memory and cognitive flexibility.")
    print("1. Observe the quantum states displayed around the screen")
    print("2. Remember which states have which values")
    print("3. When challenged, select the state that matches the target value")
    print("4. The difficulty increases as you progress")
    print("\nControls:")
    print("- Left mouse button: Select quantum states")
    print("- ESC key: Exit")
    
    # Main game loop
    running = True
    start_time = time.time()
    last_update = pygame.time.get_ticks()
    
    while running and (time.time() - start_time < args.duration):
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Handle left click
                x, y = pygame.mouse.get_pos()
                module.handle_click(x, y)
        
        # Get current module state
        state = module.get_state()
        
        # Get components for rendering
        components = state.get('components', [])
        
        # Convert components to state dictionary for renderer
        render_state = {}
        for component in components:
            component_id = component.get('id', f"component_{len(render_state)}")
            render_state[component_id] = component
            
        # Render the state
        renderer.render(render_state)
        
        # Control frame rate
        pygame.time.delay(16)  # ~60 FPS
    
    # Cleanup
    renderer.shutdown()
    print("\nTraining session complete!")
    print(f"Final score: {module.score}")

if __name__ == "__main__":
    main() 