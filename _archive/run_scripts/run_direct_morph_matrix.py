#!/usr/bin/env python3
"""
Direct MorphMatrix MVC Module Launcher

This script directly launches the MorphMatrix MVC module for testing
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
from modules.morph_matrix_mvc import MorphMatrix

# Initialize pygame
pygame.init()

# Set up window
width, height = 1024, 768
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("MorphMatrix MVC Test")

# Set up fonts
title_font = pygame.font.SysFont("arial", 24)
regular_font = pygame.font.SysFont("arial", 18)
small_font = pygame.font.SysFont("arial", 14)

# Create the module
module = MorphMatrix(difficulty=3)

# Set up colors (in case the renderer needs them)
colors = {
    "background": (240, 240, 240),
    "text": (0, 0, 0),
    "grid_border": (100, 100, 100),
    "grid_bg": (230, 230, 230),
    "button": (200, 200, 200),
    "button_hover": (180, 180, 180),
    "selected": (100, 180, 255),
    "modified": (255, 100, 100),
    "cell_on": (50, 50, 200),
    "cell_off": (230, 230, 230)
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
        elif comp_type == "matrix":
            render_matrix(component)
        elif comp_type == "button":
            render_button(component)
    
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
    color = component.get("color", colors["grid_bg"])
    border_color = component.get("border_color", colors["grid_border"])
    border_width = component.get("border_width", 1)
    
    # Draw rectangle
    rect = pygame.Rect(position[0], position[1], size[0], size[1])
    pygame.draw.rect(screen, color, rect)
    
    # Draw border if needed
    if border_width > 0:
        pygame.draw.rect(screen, border_color, rect, border_width)

def render_matrix(component):
    """Render a binary matrix component."""
    position = component.get("position", [0, 0])
    size = component.get("size", [150, 150])
    matrix_data = component.get("matrix", [])
    selected = component.get("selected", False)
    modified = component.get("modified", False)
    
    # Get matrix dimensions
    if matrix_data and isinstance(matrix_data, list):
        matrix_size = len(matrix_data)
    else:
        matrix_size = 5  # Default size
    
    # Calculate cell size
    cell_width = size[0] // matrix_size
    cell_height = size[1] // matrix_size
    
    # Draw matrix background
    bg_color = colors["selected"] if selected else colors["grid_bg"]
    if modified and selected:
        bg_color = colors["modified"]
        
    matrix_rect = pygame.Rect(position[0], position[1], size[0], size[1])
    pygame.draw.rect(screen, bg_color, matrix_rect)
    pygame.draw.rect(screen, colors["grid_border"], matrix_rect, 2)
    
    # Draw matrix cells
    for y in range(matrix_size):
        for x in range(matrix_size):
            # Get cell value (0 or 1)
            cell_value = 0
            if y < len(matrix_data) and x < len(matrix_data[y]):
                cell_value = matrix_data[y][x]
            
            # Skip if cell is empty (0)
            if cell_value == 0:
                continue
            
            # Calculate cell position
            cell_x = position[0] + x * cell_width
            cell_y = position[1] + y * cell_height
            
            # Draw filled cell
            cell_rect = pygame.Rect(cell_x, cell_y, cell_width, cell_height)
            pygame.draw.rect(screen, colors["cell_on"], cell_rect)
            pygame.draw.rect(screen, colors["grid_border"], cell_rect, 1)

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
    pygame.draw.rect(screen, colors["grid_border"], rect, 2)
    
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