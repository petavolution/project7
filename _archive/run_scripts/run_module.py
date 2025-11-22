#!/usr/bin/env python3
"""
Run Any Training Module

This script provides a unified way to run any training module as a standalone application.
It uses the standardized BaseRenderer and module-specific renderers.
"""

import sys
import os
import pygame
import argparse
import importlib
from pathlib import Path

# Add parent directory to path
script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir.parent))  # Add the parent directory to path

# Import the module registry and configuration
from MetaMindIQTrain.module_registry import create_module_instance, configure_modules_display
from MetaMindIQTrain.config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, DEFAULT_FPS, 
    DEFAULT_FONT, DEFAULT_SIZES, calculate_sizes
)


def main():
    """Run any training module as a standalone application."""
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Run any training module.")
    parser.add_argument("module", type=str, help="Module ID to run (e.g., 'symbol_memory', 'morph_matrix', 'expand_vision')")
    parser.add_argument("--level", type=int, default=1, help="Starting level (default: 1)")
    parser.add_argument("--fullscreen", action="store_true", help="Run in fullscreen mode")
    parser.add_argument("--difficulty", type=int, default=None, choices=[1, 2, 3, 4, 5],
                        help="Initial difficulty level (1-5)")
    args = parser.parse_args()
    
    # Initialize PyGame
    pygame.init()
    
    # Set up display
    if args.fullscreen:
        screen_info = pygame.display.Info()
        screen_width, screen_height = screen_info.current_w, screen_info.current_h
        screen = pygame.display.set_mode((screen_width, screen_height), pygame.FULLSCREEN)
        print(f"Running in fullscreen mode: {screen_width}x{screen_height}")
    else:
        screen_width, screen_height = SCREEN_WIDTH, SCREEN_HEIGHT
        screen = pygame.display.set_mode((screen_width, screen_height))
        print(f"Running at configured resolution: {screen_width}x{screen_height}")
    
    # Calculate sizes based on actual screen dimensions
    calculated_sizes = calculate_sizes(screen_width, screen_height)
    
    # Configure all modules to use the same display settings
    configure_modules_display(screen_width, screen_height)
    
    # Create a unique session ID
    import uuid
    session_id = str(uuid.uuid4())
    
    # Create the module instance
    try:
        module = create_module_instance(args.module, session_id)
        print(f"Created {module.name} module (Level {module.level})")
    except (ImportError, AttributeError) as e:
        print(f"Error: Could not create module '{args.module}': {e}")
        pygame.quit()
        sys.exit(1)
    
    # Set window title based on module name
    pygame.display.set_caption(f"{module.name} Training")
    
    # Create a clock for framerate control
    clock = pygame.time.Clock()
    fps = DEFAULT_FPS
    
    # Create fonts with sizes based on actual screen dimensions
    title_font = pygame.font.SysFont(DEFAULT_FONT, calculated_sizes['TITLE_FONT_SIZE'], bold=True)
    regular_font = pygame.font.SysFont(DEFAULT_FONT, calculated_sizes['REGULAR_FONT_SIZE'])
    small_font = pygame.font.SysFont(DEFAULT_FONT, calculated_sizes['SMALL_FONT_SIZE'])
    
    # Set initial level if provided
    if hasattr(module, 'level'):
        module.level = args.level
    
    # Adjust difficulty if provided
    if args.difficulty is not None:
        if hasattr(module, 'current_symbols_count') and args.module == 'symbol_memory':
            module.current_symbols_count = args.difficulty + 2  # For SymbolMemory
        elif hasattr(module, 'number_range') and args.module == 'expand_vision':
            module.number_range = 10 + (args.difficulty * 2)  # For ExpandVision
    
    # Use the EnhancedGenericRenderer for all modules
    from MetaMindIQTrain.clients.pygame.renderers.enhanced_generic_renderer import EnhancedGenericRenderer
    renderer = EnhancedGenericRenderer(screen, title_font, regular_font, small_font)
    print(f"Using enhanced generic renderer for module {args.module}")
    
    # Print help information
    print("\n" + "="*60)
    print(f"  {module.name}: {module.description}")
    print("="*60)
    
    # Print module-specific instructions
    if args.module == 'symbol_memory':
        print("\nSymbol Memory Training")
        print("=====================")
        print("This exercise tests your memory and pattern recognition.")
        print("1. Memorize the pattern of symbols shown")
        print("2. After a short delay, a similar pattern will appear")
        print("3. Determine if the pattern has been modified or not")
        print("\nControls:")
        print("- Y: Answer YES (pattern was modified)")
        print("- N: Answer NO (pattern was not modified)")
        print("- SPACE: Start a new challenge")
        print("- R: Reset level")
        print("- A: Advance to next level")
        print("- ESC: Exit")
    
    elif args.module == 'expand_vision':
        print("\nExpand Vision Training")
        print("=====================")
        print("This exercise trains your peripheral vision and calculation ability.")
        print("1. Focus on the center red dot at all times")
        print("2. The circle expands and numbers appear in your peripheral vision")
        print("3. Calculate the sum of all numbers while maintaining center focus")
        print("\nControls:")
        print("- 0-9: Enter your calculated sum")
        print("- MINUS: Enter negative number")
        print("- BACKSPACE: Delete last digit")
        print("- ENTER: Submit your answer")
        print("- SPACE: Start a new challenge")
        print("- R: Reset level")
        print("- A: Advance to next level")
        print("- ESC: Exit")
    
    elif args.module == 'morph_matrix':
        print("\nMorph Matrix Training")
        print("====================")
        print("This exercise trains your pattern recognition abilities.")
        print("1. Several matrix patterns will be shown")
        print("2. Some patterns are exact rotations, others have been modified")
        print("3. Click to select the patterns that are exact rotations (not modified)")
        print("4. Click the 'Check Answers' button when done")
        print("\nControls:")
        print("- MOUSE: Click on patterns to select/deselect them")
        print("- CHECK BUTTON: Click to submit your selections")
        print("- SPACE: Start a new challenge")
        print("- R: Reset level")
        print("- A: Advance to next level")
        print("- ESC: Exit")
    
    else:
        print("\nControls:")
        print("- SPACE: Start new challenge/round")
        print("- R: Reset level")
        print("- A: Advance to next level")
        print("- ESC: Exit")
    
    print("\nClick in the window to interact. Good luck!\n")
    
    # Track user input for number entry (for ExpandVision)
    user_input = ""
    input_active = False
    
    # Set up automatic animation timing
    last_update_time = pygame.time.get_ticks()
    update_interval = {
        'symbol_memory': 3000,  # 3 seconds between phases for memory module (match demo)
        'expand_vision': 200,   # 200ms for circle expansion in vision module (faster animation)
        'morph_matrix': 0       # No automatic updates for morph matrix
    }.get(args.module, 0)
    
    # Track phase transitions for SymbolMemory
    current_phase = "initial"
    phase_transition_time = 0
    
    # If the module was started, trigger initial challenge
    if hasattr(module, 'start_challenge'):
        module.start_challenge()
        print("Started initial challenge")
        
        # Initialize phase tracking for symbol memory
        if args.module == 'symbol_memory':
            current_phase = "memorize"
            phase_transition_time = pygame.time.get_ticks() + 3000  # 3 seconds to memorize
    
    # Main game loop
    running = True
    while running:
        # Process events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE:
                    # Start a new challenge if the module supports it
                    if hasattr(module, 'start_challenge'):
                        module.start_challenge()
                        print("Started new challenge")
                elif event.key == pygame.K_r:
                    # Reset level
                    if hasattr(module, 'reset_level'):
                        module.reset_level()
                        print("Level reset")
                        
                        # Reset phase tracking for symbol memory
                        if args.module == 'symbol_memory':
                            current_phase = "memorize"
                            phase_transition_time = pygame.time.get_ticks() + 3000
                
                # Advance level with 'A' key (like in the demos)
                elif event.key == pygame.K_a:
                    if hasattr(module, 'advance_level'):
                        module.advance_level()
                        print(f"Advanced to level {module.level}")
                        
                        # Reset phase tracking for symbol memory if applicable
                        if args.module == 'symbol_memory':
                            current_phase = "memorize"
                            phase_transition_time = pygame.time.get_ticks() + 3000
                
                # Module-specific key handling
                if args.module == 'symbol_memory':
                    if event.key == pygame.K_y:
                        # User says "Yes, pattern was modified"
                        result = module.process_input({"answer": "yes"})
                        print("User selected: YES (pattern was modified)")
                        if 'result' in result and 'message' in result['result']:
                            print(result['result']['message'])
                    elif event.key == pygame.K_n:
                        # User says "No, pattern was not modified"
                        result = module.process_input({"answer": "no"})
                        print("User selected: NO (pattern was not modified)")
                        if 'result' in result and 'message' in result['result']:
                            print(result['result']['message'])
                
                elif args.module == 'expand_vision':
                    # Handle number input for ExpandVision
                    if event.key in range(pygame.K_0, pygame.K_9 + 1):
                        # Convert key to number
                        digit = event.key - pygame.K_0
                        user_input += str(digit)
                        input_active = True
                        print(f"Number input: {user_input}")
                    elif event.key == pygame.K_MINUS:
                        # Allow negative numbers
                        if not user_input or user_input[0] != '-':
                            user_input = '-' + user_input
                        print(f"Number input: {user_input}")
                    elif event.key == pygame.K_BACKSPACE:
                        # Handle backspace
                        user_input = user_input[:-1]
                        print(f"Number input: {user_input}")
                    elif event.key == pygame.K_RETURN and input_active:
                        # Submit the number
                        try:
                            num_sum = int(user_input)
                            result = module.process_input({"sum": num_sum})
                            print(f"Submitted sum: {num_sum}")
                            if 'result' in result:
                                if result['result'].get('correct', False):
                                    print(f"Correct! +{result['result'].get('points', 0)} points")
                                else:
                                    print(f"Incorrect. The correct sum was {result['result'].get('numbers', [])} = {sum(result['result'].get('numbers', []))}")
                            # Reset input
                            user_input = ""
                            input_active = False
                        except ValueError:
                            print("Invalid number input. Please try again.")
                            user_input = ""
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    # Get mouse position
                    screen_x, screen_y = pygame.mouse.get_pos()
                    
                    # Convert to content coordinates using the renderer
                    x, y = renderer.adjust_mouse_position(screen_x, screen_y)
                    
                    # Check if a button was clicked in the renderer
                    button_clicked = False
                    for button in renderer.buttons:
                        if 'actual_rect' in button and button['actual_rect'].collidepoint(screen_x, screen_y):
                            # Handle specific button actions
                            if button['action'] == 'yes':
                                result = module.process_input({"answer": "yes"})
                                print("User clicked: YES (pattern was modified)")
                                if 'result' in result and 'message' in result['result']:
                                    print(result['result']['message'])
                                button_clicked = True
                            elif button['action'] == 'no':
                                result = module.process_input({"answer": "no"})
                                print("User clicked: NO (pattern was not modified)")
                                if 'result' in result and 'message' in result['result']:
                                    print(result['result']['message'])
                                button_clicked = True
                            elif button['action'] == 'check':
                                result = module.check_answers()
                                print(f"Checked answers: {module.message}")
                                button_clicked = True
                            elif button['action'] == 'continue' and args.module == 'symbol_memory':
                                # Handle continue button for symbol memory feedback state
                                result = module.process_input({"action": "continue"})
                                print("Continuing to next trial")
                                
                                # Reset phase tracking for symbol memory
                                current_phase = "memorize"
                                phase_transition_time = pygame.time.get_ticks() + 3000
                                
                                button_clicked = True
                            elif button['action'] == 'start_challenge':
                                # Handle start challenge button
                                if hasattr(module, 'start_challenge'):
                                    module.start_challenge()
                                    print("Started new challenge")
                                    if args.module == 'symbol_memory':
                                        current_phase = "memorize"
                                        phase_transition_time = pygame.time.get_ticks() + 3000
                                button_clicked = True
                            elif button['action'] == 'reset_level':
                                # Handle reset level button
                                if hasattr(module, 'reset_level'):
                                    module.reset_level()
                                    print("Level reset")
                                    if args.module == 'symbol_memory':
                                        current_phase = "memorize"
                                        phase_transition_time = pygame.time.get_ticks() + 3000
                                button_clicked = True
                            elif button['action'] == 'advance_level':
                                # Handle advance level button
                                if hasattr(module, 'advance_level'):
                                    module.advance_level()
                                    print(f"Advanced to level {module.level}")
                                    if args.module == 'symbol_memory':
                                        current_phase = "memorize"
                                        phase_transition_time = pygame.time.get_ticks() + 3000
                                button_clicked = True
                    
                    # If no button was clicked, forward the click to the module
                    if not button_clicked and hasattr(module, 'handle_click'):
                        result = module.handle_click(x, y)
                        if result and result.get('success', False):
                            print(result.get('message', 'Click handled'))
        
        # Handle automatic updates based on timing
        current_time = pygame.time.get_ticks()
        
        # Handle phase transitions for SymbolMemory
        if args.module == 'symbol_memory' and phase_transition_time > 0 and current_time >= phase_transition_time:
            if current_phase == "memorize":
                # Transition to question phase
                if hasattr(module, 'show_modified_pattern'):
                    module.show_modified_pattern()
                    current_phase = "question"
                    phase_transition_time = 0  # No further automatic transitions
                    print("Transitioned to question phase")
            phase_transition_time = 0  # Reset timer
        
        # Handle automatic updates for modules
        if update_interval > 0 and current_time - last_update_time >= update_interval:
            # Update based on module type
            if args.module == 'expand_vision' and hasattr(module, '_round_logic'):
                # Call the round logic method if available to expand circle
                module._round_logic()
                last_update_time = current_time
                
                # Check if we've reached the number display phase
                if module.show_numbers and not module.get_state().get('show_numbers', False):
                    print("Numbers now visible - calculate the sum")
            
            elif args.module == 'symbol_memory' and hasattr(module, 'update') and current_phase == "initial":
                # Call the update method for symbol memory module
                module.update()
                last_update_time = current_time
        
        # Get current state
        state = module.get_state()
        
        # Add user input to state if active (for ExpandVision)
        if args.module == 'expand_vision' and input_active:
            state['user_input'] = user_input
            
        # Add phase transition time for SymbolMemory countdown display
        if args.module == 'symbol_memory' and current_phase == "memorize" and phase_transition_time > 0:
            state['phase_transition_time'] = phase_transition_time
        
        # Add screen dimensions to state to support responsive rendering
        state['screen_width'] = screen_width
        state['screen_height'] = screen_height
        
        # Draw the state using the renderer
        renderer.render(state)
        
        # Update display
        pygame.display.flip()
        
        # Cap framerate
        clock.tick(fps)
    
    # Clean up
    pygame.quit()


if __name__ == "__main__":
    main() 