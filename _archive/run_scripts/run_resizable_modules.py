#!/usr/bin/env python3
"""
Resizable Modules Launcher

This script provides a simple launcher for running modules with
configurable resolution settings. It allows selecting from available
modules and adjusting screen dimensions before launch.
"""

import os
import sys
import pygame
import importlib.util
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent))

# Import the configuration module
from core import config

# Available modules
MODULES = {
    "symbol_memory": {
        "name": "Symbol Memory",
        "description": "Test your ability to memorize and recall patterns.",
        "path": "modules/symbol_memory_resizable.py",
        "class": "SymbolMemoryModule"
    }
    # Add more modules as they're implemented
}

# Resolution presets
RESOLUTION_PRESETS = [
    ("HD", 1280, 720),
    ("Full HD", 1920, 1080),
    ("Default", 1440, 1024),
    ("Custom", None, None)
]

def import_module_from_file(module_name, file_path):
    """Import a module directly from a file path."""
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def clear_screen():
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
    """Print the application header."""
    print("=" * 60)
    print("{:^60}".format("MetaMind IQ Train - Resizable Modules Launcher"))
    print("=" * 60)
    print("\nThis launcher allows you to run training modules with configurable resolution.")
    print("Current configuration settings:")
    print(f"  - Default resolution: {config.DISPLAY_CONFIG['default_width']}x{config.DISPLAY_CONFIG['default_height']}")
    print(f"  - Fullscreen: {config.DISPLAY_CONFIG['fullscreen']}")
    print(f"  - FPS limit: {config.DISPLAY_CONFIG['fps_limit']}\n")

def select_module():
    """Let the user select which module to run."""
    print("-" * 60)
    print("Available modules:")
    print("-" * 60)
    
    # List available modules
    for i, (module_id, module_info) in enumerate(MODULES.items(), 1):
        print(f"{i}. {module_info['name']} - {module_info['description']}")
    
    print("q. Quit")
    print("-" * 60)
    
    while True:
        choice = input("\nEnter module number (or q to quit): ").strip().lower()
        
        if choice == 'q':
            return None
        
        try:
            choice_num = int(choice)
            if 1 <= choice_num <= len(MODULES):
                # Get module ID from index
                module_id = list(MODULES.keys())[choice_num - 1]
                return MODULES[module_id]
            else:
                print("Invalid choice. Please enter a valid number.")
        except ValueError:
            print("Invalid input. Please enter a number or 'q'.")

def select_resolution():
    """Let the user select the screen resolution."""
    print("\n" + "-" * 60)
    print("Select resolution:")
    print("-" * 60)
    
    # List available presets
    for i, (name, width, height) in enumerate(RESOLUTION_PRESETS, 1):
        if width and height:
            print(f"{i}. {name} ({width}x{height})")
        else:
            print(f"{i}. {name}")
    
    print("-" * 60)
    
    while True:
        choice = input("\nEnter resolution number: ").strip()
        
        try:
            choice_num = int(choice)
            if 1 <= choice_num <= len(RESOLUTION_PRESETS):
                preset_name, width, height = RESOLUTION_PRESETS[choice_num - 1]
                
                # For custom resolution, prompt for dimensions
                if preset_name == "Custom":
                    width = input("Enter width (pixels): ").strip()
                    height = input("Enter height (pixels): ").strip()
                    
                    try:
                        width = int(width)
                        height = int(height)
                        
                        # Validate minimum dimensions
                        min_width = config.DISPLAY_CONFIG["min_width"]
                        min_height = config.DISPLAY_CONFIG["min_height"]
                        
                        if width < min_width or height < min_height:
                            print(f"Resolution too small. Minimum size is {min_width}x{min_height}.")
                            continue
                        
                    except ValueError:
                        print("Invalid dimensions. Please enter numeric values.")
                        continue
                
                return width, height
            else:
                print("Invalid choice. Please enter a valid number.")
        except ValueError:
            print("Invalid input. Please enter a number.")

def select_fullscreen():
    """Let the user choose fullscreen or windowed mode."""
    print("\n" + "-" * 60)
    print("Display mode:")
    print("-" * 60)
    print("1. Windowed")
    print("2. Fullscreen")
    print("-" * 60)
    
    while True:
        choice = input("\nEnter display mode number: ").strip()
        
        try:
            choice_num = int(choice)
            if choice_num == 1:
                return False
            elif choice_num == 2:
                return True
            else:
                print("Invalid choice. Please enter 1 or 2.")
        except ValueError:
            print("Invalid input. Please enter a number.")

def update_config(width, height, fullscreen):
    """Update the configuration with new settings."""
    # Update the config values
    config.DISPLAY_CONFIG["default_width"] = width
    config.DISPLAY_CONFIG["default_height"] = height
    config.DISPLAY_CONFIG["fullscreen"] = fullscreen
    
    print("\nConfiguration updated:")
    print(f"  - Resolution: {width}x{height}")
    print(f"  - Fullscreen: {fullscreen}")

def run_module(module_info, difficulty=3):
    """Run the selected module with the configured settings."""
    try:
        # Import the module
        module_path = Path(__file__).parent / module_info["path"]
        if not module_path.exists():
            print(f"Error: Module file not found at {module_path}")
            return
        
        print(f"\nImporting module from {module_path}...")
        module = import_module_from_file(module_info["name"], module_path)
        
        # Get the module class
        module_class = getattr(module, module_info["class"])
        
        # Create and run the module
        print(f"Starting {module_info['name']}...")
        instance = module_class(difficulty=difficulty)
        instance.run()
        
    except Exception as e:
        print(f"Error running module: {e}")
        import traceback
        traceback.print_exc()

def select_difficulty():
    """Let the user select difficulty level."""
    print("\n" + "-" * 60)
    print("Select difficulty level (1-10):")
    print("-" * 60)
    print("1-3: Easy")
    print("4-6: Medium")
    print("7-10: Hard")
    print("-" * 60)
    
    while True:
        choice = input("\nEnter difficulty (1-10): ").strip()
        
        try:
            difficulty = int(choice)
            if 1 <= difficulty <= 10:
                return difficulty
            else:
                print("Invalid choice. Please enter a number between 1 and 10.")
        except ValueError:
            print("Invalid input. Please enter a number.")

def main():
    """Main function to run the launcher."""
    try:
        # Initialize pygame for display enumeration
        pygame.init()
        
        while True:
            clear_screen()
            print_header()
            
            # Select module
            module_info = select_module()
            if not module_info:
                print("\nExiting... Goodbye!")
                break
            
            # Select resolution
            width, height = select_resolution()
            
            # Select fullscreen
            fullscreen = select_fullscreen()
            
            # Select difficulty
            difficulty = select_difficulty()
            
            # Update configuration
            update_config(width, height, fullscreen)
            
            # Confirm
            print("\n" + "-" * 60)
            print(f"Ready to launch {module_info['name']} at {width}x{height} " +
                  f"in {'fullscreen' if fullscreen else 'windowed'} mode " +
                  f"with difficulty {difficulty}.")
            
            confirm = input("\nLaunch now? (y/n): ").strip().lower()
            if confirm == 'y':
                # Run the module
                run_module(module_info, difficulty)
            
            # Ask if user wants to continue
            continue_choice = input("\nReturn to main menu? (y/n): ").strip().lower()
            if continue_choice != 'y':
                print("\nExiting... Goodbye!")
                break
        
    except KeyboardInterrupt:
        print("\n\nProgram interrupted. Exiting...")
    finally:
        pygame.quit()
        sys.exit(0)

if __name__ == "__main__":
    main() 