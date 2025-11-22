#!/usr/bin/env python3
"""
Direct ExpandVision MVC Module Launcher

This script directly launches the ExpandVision MVC module for testing
without relying on complex import structures.
"""

import os
import sys
import time
import pygame
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent))

# Import the module directly
from MetaMindIQTrain.modules.expand_vision_Grid_mvc import ExpandVision

# Initialize pygame
pygame.init()

# Set up window
width, height = 1024, 768
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("ExpandVision MVC Test")

# Set up fonts
title_font = pygame.font.SysFont("arial", 24)
regular_font = pygame.font.SysFont("arial", 18)
small_font = pygame.font.SysFont("arial", 14)

# Create the module
module = ExpandVision(screen_width=width, screen_height=height)

# Set up colors (in case the renderer needs them)
colors = {
    "background": (240, 240, 240),
    "text": (0, 0, 0),
    "circle": (50, 120, 200),
    "circle_border": (30, 100, 180),
    "button": (200, 200, 200),
    "button_hover": (180, 180, 180),
    "number": (200, 50, 50)
}

# Simple built-in renderer
def render_state(state):
    """Render the module state directly to the screen."""
    screen.fill(colors["background"])
    
    # Render all components
    components = state.get("components", [])
    for component in components:
        comp_type = component.get("type", "")
        
        if comp_type == "text":
            render_text(component)
        elif comp_type == "rect":
            render_rect(component)
        elif comp_type == "circle":
            render_circle(component)
        elif comp_type == "button":
            render_button(component)
        elif comp_type == "peripheral_number":
            render_peripheral_number(component)
    
    # Draw debug info if needed
    if show_debug:
        # Draw FPS
        fps_text = f"FPS: {int(clock.get_fps())}"
        fps_surface = small_font.render(fps_text, True, (0, 0, 0))
        screen.blit(fps_surface, (5, 5))
        
        # Draw component count
        count_text = f"Components: {len(components)}"
        count_surface = small_font.render(count_text, True, (0, 0, 0))
        screen.blit(count_surface, (5, 25))
        
        # Draw center marker
        pygame.draw.line(screen, (255, 0, 0), (width//2-10, height//2), (width//2+10, height//2), 1)
        pygame.draw.line(screen, (255, 0, 0), (width//2, height//2-10), (width//2, height//2+10), 1)

def render_text(component):
    """Render a text component."""
    text = component.get("text", "")
    position = component.get("position", [0, 0])
    font_size = component.get("font_size", 18)
    color = component.get("color", colors["text"])
    
    # Select font based on size
    if font_size >= 24:
        font = title_font
    elif font_size >= 16:
        font = regular_font
    else:
        font = small_font
    
    # Render text
    text_surface = font.render(text, True, color)
    screen.blit(text_surface, position)

def render_rect(component):
    """Render a rectangle component."""
    position = component.get("position", [0, 0])
    size = component.get("size", [100, 100])
    color = component.get("color", (200, 200, 200))
    border_color = component.get("border_color", (100, 100, 100))
    border_width = component.get("border_width", 1)
    
    # Draw rectangle
    rect = pygame.Rect(position[0], position[1], size[0], size[1])
    pygame.draw.rect(screen, color, rect)
    
    # Draw border if needed
    if border_width > 0:
        pygame.draw.rect(screen, border_color, rect, border_width)

def render_circle(component):
    """Render a circle component."""
    position = component.get("position", [width//2, height//2])
    radius = component.get("radius", 30)
    color = component.get("color", colors["circle"])
    border_color = component.get("border_color", colors["circle_border"])
    border_width = component.get("border_width", 2)
    
    # Draw circle
    pygame.draw.circle(screen, color, position, radius)
    
    # Draw border if needed
    if border_width > 0:
        pygame.draw.circle(screen, border_color, position, radius, border_width)

def render_peripheral_number(component):
    """Render a peripheral number component."""
    position = component.get("position", [0, 0])
    number = component.get("number", 0)
    font_size = component.get("font_size", 20)
    color = component.get("color", colors["number"])
    
    # Render number
    number_text = str(number)
    text_surface = regular_font.render(number_text, True, color)
    text_rect = text_surface.get_rect(center=position)
    screen.blit(text_surface, text_rect)

def render_button(component):
    """Render a button component."""
    position = component.get("position", [0, 0])
    size = component.get("size", [100, 40])
    text = component.get("text", "")
    active = component.get("active", True)
    
    # Choose color based on state
    if active:
        color = colors["button"]
        text_color = colors["text"]
    else:
        color = (180, 180, 180)  # Disabled color
        text_color = (120, 120, 120)  # Disabled text color
    
    # Draw button
    rect = pygame.Rect(position[0], position[1], size[0], size[1])
    pygame.draw.rect(screen, color, rect)
    pygame.draw.rect(screen, (100, 100, 100), rect, 2)
    
    # Draw text
    if text:
        text_surface = regular_font.render(text, True, text_color)
        text_rect = text_surface.get_rect(center=(
            position[0] + size[0] // 2,
            position[1] + size[1] // 2
        ))
        screen.blit(text_surface, text_rect)

# Game loop
clock = pygame.time.Clock()
running = True
last_time = time.time()
show_debug = True

while running:
    # Calculate delta time
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
                # Toggle debug display
                show_debug = not show_debug
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Handle clicks
            x, y = event.pos
            module.handle_click(x, y)
    
    # Update module
    module.update(dt)
    
    # Render state
    render_state(module.get_state())
    
    # Update display
    pygame.display.flip()
    
    # Cap at 60 FPS
    clock.tick(60)

# Clean up
pygame.quit()
sys.exit(0) 