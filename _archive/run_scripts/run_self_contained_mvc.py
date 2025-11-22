#!/usr/bin/env python3
"""
Self-Contained MVC Module Runner

This script directly imports and runs the MVC modules
without relying on complex package imports.
"""

import os
import sys
import time
import pygame
import importlib.util
from pathlib import Path

# Initialize pygame
pygame.init()

# Set up window
width, height = 1024, 768
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("MVC Module Test")

# Set up fonts
title_font = pygame.font.SysFont("arial", 24)
regular_font = pygame.font.SysFont("arial", 18)
small_font = pygame.font.SysFont("arial", 14)

def import_module_from_file(module_name, file_path):
    """Import a module directly from a file path."""
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def select_module():
    """Let the user select which module to run."""
    print("Select which module to run:")
    print("1. Symbol Memory")
    print("2. Morph Matrix")
    print("3. Expand Vision")
    print("q. Quit")
    
    choice = input("Enter choice (1-3, q): ").strip().lower()
    
    if choice == "q":
        pygame.quit()
        sys.exit(0)
    
    try:
        choice_num = int(choice)
        if choice_num < 1 or choice_num > 3:
            print("Invalid choice. Please enter 1-3 or q.")
            return select_module()
        return choice_num
    except ValueError:
        print("Invalid choice. Please enter 1-3 or q.")
        return select_module()

def run_module(module_path, module_class, difficulty=3):
    """Run the specified module with a simple game loop."""
    try:
        # Import the module
        print(f"Importing module from {module_path}")
        module = import_module_from_file(module_class, module_path)
        
        # Create an instance of the main class
        if module_class == "ExpandVisionMVC":
            model = getattr(module, "ExpandVision")(screen_width=width, screen_height=height)
        else:
            model = getattr(module, module_class.replace("MVC", ""))(difficulty=difficulty)
        
        print(f"Created {module_class} instance")
        
        # Set up basic colors
        colors = {
            "background": (240, 240, 240),
            "text": (0, 0, 0),
            "grid_border": (100, 100, 100),
            "grid_bg": (230, 230, 230),
            "button": (200, 200, 200)
        }
        
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
                        show_debug = not show_debug
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    x, y = event.pos
                    if hasattr(model, "handle_click"):
                        model.handle_click(x, y)
            
            # Update model
            model.update(dt)
            
            # Get state
            state = model.get_state()
            
            # Render components
            screen.fill(colors["background"])
            render_state(state, screen, title_font, regular_font, small_font, show_debug, clock)
            
            # Update display
            pygame.display.flip()
            
            # Cap at 60 FPS
            clock.tick(60)
        
        # Clean up
        pygame.quit()
        sys.exit(0)
        
    except Exception as e:
        print(f"Error running module: {e}")
        import traceback
        traceback.print_exc()
        pygame.quit()
        sys.exit(1)

def render_state(state, screen, title_font, regular_font, small_font, show_debug, clock):
    """Render the module state."""
    components = state.get("components", [])
    
    for comp in components:
        comp_type = comp.get("type", "")
        
        if comp_type == "text":
            render_text(comp, screen, title_font, regular_font, small_font)
        elif comp_type == "rect":
            render_rect(comp, screen)
        elif comp_type == "button":
            render_button(comp, screen, regular_font)
        elif comp_type == "grid":
            render_grid(comp, screen, regular_font)
        elif comp_type == "matrix":
            render_matrix(comp, screen)
        elif comp_type == "circle":
            render_circle(comp, screen)
    
    # Draw debug info
    if show_debug:
        fps = int(clock.get_fps())
        fps_text = small_font.render(f"FPS: {fps}", True, (0, 0, 0))
        screen.blit(fps_text, (10, 10))
        
        component_text = small_font.render(f"Components: {len(components)}", True, (0, 0, 0))
        screen.blit(component_text, (10, 30))

def render_text(comp, screen, title_font, regular_font, small_font):
    """Render a text component."""
    text = comp.get("text", "")
    position = comp.get("position", [0, 0])
    font_size = comp.get("font_size", 18)
    color = comp.get("color", (0, 0, 0))
    
    if font_size >= 24:
        font = title_font
    elif font_size >= 16:
        font = regular_font
    else:
        font = small_font
    
    if text:
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect(center=position)
        screen.blit(text_surface, text_rect)

def render_rect(comp, screen):
    """Render a rectangle component."""
    position = comp.get("position", [0, 0])
    size = comp.get("size", [100, 100])
    color = comp.get("color", (230, 230, 230))
    border_color = comp.get("border_color", (100, 100, 100))
    border_width = comp.get("border_width", 1)
    
    rect = pygame.Rect(position[0], position[1], size[0], size[1])
    pygame.draw.rect(screen, color, rect)
    
    if border_width > 0:
        pygame.draw.rect(screen, border_color, rect, border_width)

def render_button(comp, screen, font):
    """Render a button component."""
    position = comp.get("position", [0, 0])
    size = comp.get("size", [100, 40])
    text = comp.get("text", "")
    active = comp.get("active", True)
    
    color = (200, 200, 200) if active else (180, 180, 180)
    text_color = (0, 0, 0) if active else (120, 120, 120)
    
    rect = pygame.Rect(position[0], position[1], size[0], size[1])
    pygame.draw.rect(screen, color, rect)
    pygame.draw.rect(screen, (100, 100, 100), rect, 2)
    
    if text:
        text_surface = font.render(text, True, text_color)
        text_rect = text_surface.get_rect(center=(
            position[0] + size[0] // 2,
            position[1] + size[1] // 2
        ))
        screen.blit(text_surface, text_rect)

def render_grid(comp, screen, font):
    """Render a grid component."""
    position = comp.get("position", [0, 0])
    size = comp.get("size", [300, 300])
    grid_size = comp.get("grid_size", 3)
    cells = comp.get("cells", [])
    
    # Draw grid background
    cell_width = size[0] // grid_size
    cell_height = size[1] // grid_size
    
    rect = pygame.Rect(position[0], position[1], size[0], size[1])
    pygame.draw.rect(screen, (230, 230, 230), rect)
    pygame.draw.rect(screen, (100, 100, 100), rect, 2)
    
    # Draw grid lines
    for i in range(1, grid_size):
        # Vertical lines
        pygame.draw.line(
            screen, 
            (100, 100, 100),
            (position[0] + i * cell_width, position[1]),
            (position[0] + i * cell_width, position[1] + size[1]),
            1
        )
        
        # Horizontal lines
        pygame.draw.line(
            screen, 
            (100, 100, 100),
            (position[0], position[1] + i * cell_height),
            (position[0] + size[0], position[1] + i * cell_height),
            1
        )
    
    # Draw cell contents
    for cell in cells:
        cell_x = cell.get("x", 0)
        cell_y = cell.get("y", 0)
        text = cell.get("text", "")
        
        # Skip if outside grid bounds
        if cell_x >= grid_size or cell_y >= grid_size:
            continue
        
        # Calculate position
        text_x = position[0] + cell_x * cell_width + cell_width // 2
        text_y = position[1] + cell_y * cell_height + cell_height // 2
        
        # Render text
        text_surface = font.render(text, True, (50, 50, 200))
        text_rect = text_surface.get_rect(center=(text_x, text_y))
        screen.blit(text_surface, text_rect)

def render_matrix(comp, screen):
    """Render a matrix component."""
    position = comp.get("position", [0, 0])
    size = comp.get("size", [150, 150])
    matrix = comp.get("matrix", [])
    
    if not matrix:
        return
    
    matrix_size = len(matrix)
    cell_width = size[0] // matrix_size
    cell_height = size[1] // matrix_size
    
    for y in range(matrix_size):
        for x in range(matrix_size):
            if y < len(matrix) and x < len(matrix[y]):
                cell_value = matrix[y][x]
                cell_x = position[0] + x * cell_width
                cell_y = position[1] + y * cell_height
                
                cell_rect = pygame.Rect(cell_x, cell_y, cell_width, cell_height)
                cell_color = (50, 50, 200) if cell_value == 1 else (230, 230, 230)
                pygame.draw.rect(screen, cell_color, cell_rect)
                pygame.draw.rect(screen, (100, 100, 100), cell_rect, 1)

def render_circle(comp, screen):
    """Render a circle component."""
    position = comp.get("position", [0, 0])
    radius = comp.get("radius", 30)
    color = comp.get("color", (50, 120, 200))
    border_color = comp.get("border_color", (30, 100, 180))
    border_width = comp.get("border_width", 2)
    
    pygame.draw.circle(screen, color, position, radius)
    
    if border_width > 0:
        pygame.draw.circle(screen, border_color, position, radius, border_width)

if __name__ == "__main__":
    try:
        module_choice = select_module()
        
        if module_choice == 1:
            module_path = Path(__file__).parent / "modules" / "symbol_memory_mvc.py"
            module_class = "SymbolMemoryMVC"
        elif module_choice == 2:
            module_path = Path(__file__).parent / "modules" / "morph_matrix_mvc.py"
            module_class = "MorphMatrixMVC"
        elif module_choice == 3:
            module_path = Path(__file__).parent / "modules" / "expand_vision_mvc.py"
            module_class = "ExpandVisionMVC"
        
        run_module(module_path, module_class)
        
    except KeyboardInterrupt:
        print("\nProgram interrupted. Exiting...")
        pygame.quit()
        sys.exit(0) 