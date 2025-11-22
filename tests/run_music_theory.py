#!/usr/bin/env python3
"""
Test script for MusicTheory module.

This script runs the MusicTheory module standalone to verify it works correctly.
"""

import os
import sys
import time
import argparse
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Import required components
try:
    from MetaMindIQTrain.modules.music_theory import MusicTheory
    import pygame
    import numpy as np
    HAS_DEPENDENCIES = True
except ImportError as e:
    print(f"Error importing required dependencies: {e}")
    print("Please install the required packages:")
    print("  pip install pygame numpy sounddevice")
    HAS_DEPENDENCIES = False


def run_standalone_module():
    """Run the MusicTheory module in standalone mode."""
    if not HAS_DEPENDENCIES:
        return

    # Initialize PyGame
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Music Theory Module Test")
    clock = pygame.time.Clock()
    
    # Create the module
    module = MusicTheory()
    print(f"Created {module.name} module")
    
    # Main loop
    running = True
    last_state_update = time.time()
    
    while running:
        # Handle PyGame events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE:
                    # Play the audio
                    module._play_audio()
                elif event.key in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5]:
                    # Select an option (1-5)
                    option_index = event.key - pygame.K_1
                    if module.state == "challenge" and option_index < len(module.current_options):
                        result = module.process_input({"answer": module.current_options[option_index]})
                        print(f"Selected option: {module.current_options[option_index]}")
                        if "result" in result:
                            print(f"Result: {result['result']['message']}")
                elif event.key == pygame.K_RETURN:
                    # Continue to next challenge in feedback state
                    if module.state == "feedback":
                        module.generate_challenge()
                        print("Generated new challenge")
        
        # Clear screen
        screen.fill((30, 30, 40))
        
        # Draw module state information
        state = module.get_state()
        
        # Draw title
        font = pygame.font.SysFont('Arial', 32)
        title = font.render(f"Music Theory Module - Level {state['level']}", True, (255, 255, 255))
        screen.blit(title, (400 - title.get_width() // 2, 20))
        
        # Draw score
        font = pygame.font.SysFont('Arial', 24)
        score = font.render(f"Score: {state['score']}", True, (255, 255, 255))
        screen.blit(score, (700, 20))
        
        # Draw challenge type
        challenge_type = font.render(f"Challenge: {state['challenge_type']}", True, (255, 255, 255))
        screen.blit(challenge_type, (400 - challenge_type.get_width() // 2, 80))
        
        # Draw options
        font = pygame.font.SysFont('Arial', 20)
        y_pos = 150
        for i, option in enumerate(state['options']):
            option_text = font.render(f"{i+1}. {option}", True, (255, 255, 255))
            screen.blit(option_text, (50, y_pos))
            y_pos += 40
        
        # Draw message
        message = font.render(state['message'], True, (255, 255, 200))
        screen.blit(message, (400 - message.get_width() // 2, 400))
        
        # Draw instructions
        instructions = [
            "SPACE - Play audio",
            "1-5 - Select option",
            "ENTER - Continue to next challenge",
            "ESC - Quit"
        ]
        
        y_pos = 500
        for instruction in instructions:
            inst_text = font.render(instruction, True, (200, 200, 200))
            screen.blit(inst_text, (50, y_pos))
            y_pos += 25
        
        # Update display
        pygame.display.flip()
        
        # Cap at 60 FPS
        clock.tick(60)
    
    # Cleanup
    pygame.quit()


def main():
    """Main entry point for the test script."""
    parser = argparse.ArgumentParser(description="Test the MusicTheory module")
    args = parser.parse_args()
    
    run_standalone_module()


if __name__ == "__main__":
    main() 