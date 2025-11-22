#!/usr/bin/env python3
"""
Symbol Memory Test Script

This script tests the Symbol Memory module functionality without the visual component,
focusing on the core mechanics of the grid-based pattern generation and modification.
"""

import sys
import os
from pathlib import Path

# Add the parent directory to sys.path
script_dir = Path(__file__).resolve().parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

# Import the Symbol Memory module
from MetaMindIQTrain.modules.symbol_memory import SymbolMemory

def print_grid(pattern, grid_size):
    """Print a grid visualization of the pattern."""
    print(f"Grid {grid_size}x{grid_size}:")
    print("+" + "-" * (grid_size * 3 - 1) + "+")
    for i in range(grid_size):
        row = "| "
        for j in range(grid_size):
            index = i * grid_size + j
            row += pattern[index] + " | "
        print(row)
        print("+" + "-" * (grid_size * 3 - 1) + "+")

def test_symbol_memory():
    """Test the Symbol Memory module functionality."""
    # Create an instance of the Symbol Memory module
    symbol_memory = SymbolMemory()
    
    print("\n=== Symbol Memory Module Test ===\n")
    
    # Test initial state
    print(f"Initial Level: {symbol_memory.level}")
    print(f"Initial Grid Size: {symbol_memory.current_grid_size}")
    print(f"Initial Score: {symbol_memory.score}")
    
    # Test pattern generation
    print("\n--- Initial Pattern ---")
    original_pattern = symbol_memory.original_pattern
    print_grid(original_pattern, symbol_memory.current_grid_size)
    
    # Test pattern modification
    print("\n--- Modified Pattern ---")
    modified_pattern = symbol_memory.modified_pattern
    print_grid(modified_pattern, symbol_memory.current_grid_size)
    
    print(f"Was the pattern modified? {symbol_memory.was_modified}")
    if symbol_memory.was_modified:
        print(f"Modified position: {symbol_memory.modified_position}")
        row = symbol_memory.modified_position // symbol_memory.current_grid_size
        col = symbol_memory.modified_position % symbol_memory.current_grid_size
        print(f"Modified at position (row, col): ({row}, {col})")
        print(f"Original symbol: {original_pattern[symbol_memory.modified_position]}")
        print(f"Modified symbol: {modified_pattern[symbol_memory.modified_position]}")
    
    # Test increasing levels and grid sizes
    print("\n=== Testing Level Progression ===\n")
    
    # Simulate correct answers to advance levels
    for level in range(2, min(5, symbol_memory.max_level + 1)):
        print(f"\n--- Testing Level {level} ---")
        
        # Force level increase
        symbol_memory.level = level
        symbol_memory._round_logic()
        
        print(f"Current Level: {symbol_memory.level}")
        print(f"Current Grid Size: {symbol_memory.current_grid_size}")
        
        # Show the new pattern
        print("\nNew Pattern:")
        print_grid(symbol_memory.original_pattern, symbol_memory.current_grid_size)
        
        # Show memorize and compare times
        print(f"Memorize Time: {symbol_memory.memorize_time}ms")
        print(f"Compare Time: {symbol_memory.compare_time}ms")
    
    print("\n=== Test Complete ===")

if __name__ == "__main__":
    test_symbol_memory() 