#!/usr/bin/env python3
"""
Basic Pygame Test

A simple test script to verify that pygame is working properly.
"""

import os
import sys
import time
import pygame
from pathlib import Path

# Get project root
project_root = Path(__file__).parent.parent.absolute()

# Add to path
sys.path.insert(0, str(project_root))

def main():
    """Run a basic Pygame test."""
    # Initialize Pygame
    pygame.init()
    
    # Create screen
    screen_width = 800
    screen_height = 600
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("MetaMindIQTrain - Basic Test")
    
    # Create a clock
    clock = pygame.time.Clock()
    
    # Font for text
    font = pygame.font.SysFont("Arial", 24)
    
    # Colors
    white = (255, 255, 255)
    black = (0, 0, 0)
    gray = (128, 128, 128)
    blue = (0, 0, 255)
    green = (0, 255, 0)
    
    # Test shapes
    shapes = [
        {"type": "rect", "color": blue, "rect": (100, 100, 200, 100)},
        {"type": "circle", "color": green, "center": (500, 150), "radius": 50},
        {"type": "text", "text": "Pygame is working!", "pos": (250, 300)}
    ]
    
    # Main loop
    running = True
    frame_count = 0
    start_time = time.time()
    
    while running:
        # Process events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
        # Clear screen
        screen.fill(black)
        
        # Draw test shapes
        for shape in shapes:
            if shape["type"] == "rect":
                pygame.draw.rect(screen, shape["color"], shape["rect"])
            elif shape["type"] == "circle":
                pygame.draw.circle(screen, shape["color"], shape["center"], shape["radius"])
            elif shape["type"] == "text":
                text_surface = font.render(shape["text"], True, white)
                screen.blit(text_surface, shape["pos"])
        
        # Calculate and display FPS
        frame_count += 1
        current_time = time.time()
        elapsed = current_time - start_time
        
        if elapsed >= 1.0:
            fps = frame_count / elapsed
            frame_count = 0
            start_time = current_time
            
            # Update window title with FPS
            pygame.display.set_caption(f"MetaMindIQTrain - Basic Test - FPS: {fps:.1f}")
        
        # Draw border
        pygame.draw.rect(screen, gray, (0, 0, screen_width, screen_height), 2)
        
        # Update display
        pygame.display.flip()
        
        # Limit to 60 FPS
        clock.tick(60)
    
    # Clean up
    pygame.quit()
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 