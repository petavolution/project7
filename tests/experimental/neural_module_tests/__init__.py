"""
Neural Module Tests Package

This package contains tests for the neural pattern generation, quantum state,
network optimization, and neural synthesis modules.

The tests validate the functionality, performance, and integration of all 
neural-inspired components in the MetaMindIQTrain system.
"""

# Make this a proper package
from pathlib import Path
import sys

# Add the parent directory to sys.path if needed
parent_dir = str(Path(__file__).parent.parent.parent)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir) 