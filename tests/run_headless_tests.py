#!/usr/bin/env python3
"""
Run Headless Tests

This script runs all the headless tests for the MetaMindIQTrain project in sequence.
It does not require any user interaction and can be used for automated testing.
"""

import sys
import os
import subprocess
from pathlib import Path

# Get the absolute path to the tests directory
TESTS_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = TESTS_DIR.parent

def print_separator(title):
    """Print a separator with a title for better readability."""
    print("\n" + "=" * 80)
    print(f" {title} ".center(80, "="))
    print("=" * 80 + "\n")

def run_test(script_name, args=None):
    """Run a test script and return whether it succeeded.
    
    Args:
        script_name: Name of the script in the tests directory
        args: Optional list of arguments to pass to the script
        
    Returns:
        True if the script succeeded (returned 0), False otherwise
    """
    print_separator(f"RUNNING TEST: {script_name}")
    
    # Construct the command
    script_path = TESTS_DIR / script_name
    cmd = [sys.executable, str(script_path)]
    
    if args:
        cmd.extend(args)
    
    # Run the command
    print(f"Command: {' '.join(cmd)}")
    print()
    
    result = subprocess.run(cmd)
    
    # Check the result
    success = result.returncode == 0
    status = "PASSED" if success else "FAILED"
    
    print(f"\nTest {script_name} {status} with return code {result.returncode}")
    
    return success

def main():
    """Main function to run all headless tests."""
    print_separator("RUNNING ALL METAMINDIQTRAIN HEADLESS TESTS")
    
    # Keep track of test results
    results = {}
    
    # Set SDL_VIDEODRIVER to dummy for headless tests
    os.environ['SDL_VIDEODRIVER'] = 'dummy'
    
    # Module registry checks
    results["check_all_modules.py"] = run_test("check_all_modules.py")
    results["check_modules.py"] = run_test("check_modules.py")
    
    # Module logic tests
    results["test_modules_core.py"] = run_test("test_modules_core.py")
    results["check_module_logic.py"] = run_test("check_module_logic.py")
    
    # UI scaling test (no interaction required)
    results["test_config_scaling.py"] = run_test("test_config_scaling.py")
    
    # Print summary
    print_separator("TEST RESULTS SUMMARY")
    
    for script, success in results.items():
        status = "PASSED" if success else "FAILED"
        print(f"{script}: {status}")
    
    # Calculate overall result
    total = len(results)
    passed = sum(1 for success in results.values() if success)
    failed = total - passed
    
    print(f"\nTotal tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    
    if failed == 0:
        print("\nAll headless tests passed!")
        return 0
    else:
        print("\nSome tests failed. See details above.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 