#!/usr/bin/env python3
"""
Run Symbol Memory Module

This script launches the Symbol Memory training module, which features a
grid-based memory challenge that starts at 3x3 and increases by 1 each level.

Usage:
    python run_symbol_memory.py [--fullscreen] [--debug] [--duration SECONDS]

Options:
    --fullscreen    Run in fullscreen mode
    --debug         Enable debug logging
    --duration      Duration in seconds (default: 300)
"""

import sys
import os
import argparse
from pathlib import Path

# Add the parent directory to the Python path so we can import properly
current_dir = Path(__file__).resolve().parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

# Import the symbol memory visual module
import symbol_memory_visual

def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Run Symbol Memory training module")
    parser.add_argument("--fullscreen", action="store_true", help="Run in fullscreen mode")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    parser.add_argument("--duration", type=int, default=300, help="Duration in seconds (default: 300)")
    
    args = parser.parse_args()
    
    # Run the visualization
    symbol_memory_visual.main(
        duration=args.duration,
        fullscreen=args.fullscreen,
        debug=args.debug
    )

if __name__ == "__main__":
    main() 