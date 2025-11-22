#!/usr/bin/env python3
"""
Test Runner for MetaMindIQTrain.

This script discovers and runs all the tests for the MetaMindIQTrain system.
It provides a simple interface to run all tests or specific test modules.
"""

import os
import sys
import argparse
import unittest
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


def run_tests(test_pattern=None, verbosity=2):
    """
    Run tests matching the specified pattern.
    
    Args:
        test_pattern: Pattern to match test modules
        verbosity: Verbosity level for test output
        
    Returns:
        Test result object
    """
    # Discover tests
    if test_pattern:
        test_pattern = f"*{test_pattern}*"
    else:
        test_pattern = "*test_*.py"
        
    tests_dir = Path(__file__).parent
    loader = unittest.TestLoader()
    suite = loader.discover(str(tests_dir), pattern=test_pattern)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=verbosity)
    result = runner.run(suite)
    
    return result


def main():
    """Main entry point for the test runner."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Run tests for MetaMindIQTrain")
    parser.add_argument(
        "-m", "--module", 
        help="Specific test module to run (e.g. 'module_loading' for tests/modules/test_module_loading.py)"
    )
    parser.add_argument(
        "-v", "--verbosity", 
        type=int, 
        default=2, 
        choices=[0, 1, 2], 
        help="Verbosity level (0=quiet, 1=normal, 2=verbose)"
    )
    parser.add_argument(
        "-l", "--list",
        action="store_true",
        help="List available test modules without running them"
    )
    args = parser.parse_args()
    
    # List test modules if requested
    if args.list:
        print("Available test modules:")
        test_dir = Path(__file__).parent
        for test_file in test_dir.glob("**/*test_*.py"):
            rel_path = test_file.relative_to(test_dir)
            name = str(rel_path).replace(".py", "").replace("/", ".")
            print(f"  {name}")
        return 0
    
    # Run the tests
    print(f"Running {'all tests' if not args.module else f'tests matching \'{args.module}\''}...")
    result = run_tests(args.module, args.verbosity)
    
    # Return exit code based on test result
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(main()) 