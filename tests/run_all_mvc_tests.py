#!/usr/bin/env python3
"""
Run All MVC Tests for MetaMindIQTrain

This script runs all the MVC-related tests to ensure that the
MVC-based modules are working correctly. It runs both unit tests
and functional tests for the MVC architecture.

Usage:
    python run_all_mvc_tests.py [--skip-interactive] [--skip-integration]

Options:
    --skip-interactive: Skip tests that require user interaction
    --skip-integration: Skip integration tests
"""

import os
import sys
import time
import argparse
import unittest
import subprocess
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Process command line arguments
parser = argparse.ArgumentParser(description="Run all MVC tests for MetaMindIQTrain")
parser.add_argument("--skip-interactive", action="store_true", help="Skip tests requiring user interaction")
parser.add_argument("--skip-integration", action="store_true", help="Skip integration tests")
args = parser.parse_args()

def print_header(text):
    """Print a header with decorative formatting."""
    print("\n" + "=" * 80)
    print(f" {text} ".center(80, "="))
    print("=" * 80)

def print_subheader(text):
    """Print a subheader with decorative formatting."""
    print("\n" + "-" * 80)
    print(f" {text} ".center(80, "-"))
    print("-" * 80)

def run_command(command, cwd=None):
    """Run a command and return its output and success status."""
    try:
        result = subprocess.run(
            command,
            cwd=cwd or os.getcwd(),
            check=True,
            capture_output=True,
            text=True
        )
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, e.stdout + "\n" + e.stderr

print_header("MetaMindIQTrain MVC Test Suite")
print(f"Running tests from: {project_root}")
print(f"Skip interactive tests: {args.skip_interactive}")
print(f"Skip integration tests: {args.skip_integration}")

# Test start time
start_time = time.time()

# Initialize test results
results = {
    "passed": 0,
    "failed": 0,
    "skipped": 0
}

# Step 1: Run the check_all_mvc_modules.py script
print_subheader("MVC Module Check")
print("Running basic MVC module checks...")

cmd = [sys.executable, "tests/check_all_mvc_modules.py", "--headless"]
success, output = run_command(cmd, project_root)

print(output)
if success:
    results["passed"] += 1
    print("✅ MVC Module Check passed")
else:
    results["failed"] += 1
    print("❌ MVC Module Check failed")

# Step 2: Run unit tests for MVC modules
print_subheader("MVC Unit Tests")
print("Running unit tests for MVC modules...")

loader = unittest.TestLoader()
suite = loader.discover("tests/modules", pattern="test_mvc_*.py")
runner = unittest.TextTestRunner(verbosity=2)
result = runner.run(suite)

if result.wasSuccessful():
    results["passed"] += 1
    print("✅ MVC Unit Tests passed")
else:
    results["failed"] += 1
    print("❌ MVC Unit Tests failed")

# Step 3: Run integration tests if not skipped
if not args.skip_integration:
    print_subheader("MVC Integration Tests")
    print("Running integration tests for MVC modules...")
    
    loader = unittest.TestLoader()
    suite = loader.discover("tests/integration", pattern="test_mvc_*.py")
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    if result.wasSuccessful():
        results["passed"] += 1
        print("✅ MVC Integration Tests passed")
    else:
        results["failed"] += 1
        print("❌ MVC Integration Tests failed")
else:
    results["skipped"] += 1
    print("⏭️ MVC Integration Tests skipped")

# Step 4: Run interactive tests if not skipped
if not args.skip_interactive:
    print_subheader("Interactive MVC Tests")
    print("Note: These tests require user interaction")
    print("Running interactive tests for each MVC module...")
    
    interactive_tests = [
        ["tests/run_mvc_modules.py", "symbol_memory", "--debug"],
        ["tests/run_mvc_modules.py", "morph_matrix", "--debug"],
        ["tests/run_mvc_modules.py", "expand_vision", "--debug"]
    ]
    
    for i, test_cmd in enumerate(interactive_tests):
        module_name = test_cmd[1]
        print(f"\nRunning {module_name} interactive test ({i+1}/{len(interactive_tests)})...")
        print(f"Command: {' '.join([sys.executable] + test_cmd)}")
        
        try:
            input("\nPress Enter to start the test (or Ctrl+C to skip)...")
            subprocess.run([sys.executable] + test_cmd, cwd=project_root)
            
            # Ask for confirmation
            result = input("\nDid the test complete successfully? (y/n): ").strip().lower()
            if result == 'y':
                results["passed"] += 1
                print(f"✅ {module_name} interactive test passed")
            else:
                results["failed"] += 1
                print(f"❌ {module_name} interactive test failed")
        except KeyboardInterrupt:
            print(f"\n⏭️ {module_name} interactive test skipped")
            results["skipped"] += 1
else:
    results["skipped"] += len(["symbol_memory", "morph_matrix", "expand_vision"])
    print("⏭️ Interactive MVC Tests skipped")

# Calculate elapsed time
elapsed_time = time.time() - start_time

# Print summary
print_subheader("Test Summary")
print(f"Tests passed: {results['passed']}")
print(f"Tests failed: {results['failed']}")
print(f"Tests skipped: {results['skipped']}")
print(f"Total time: {elapsed_time:.2f} seconds")

if results["failed"] > 0:
    print("\n❌ Some tests failed!")
    sys.exit(1)
else:
    print("\n✅ All tests passed!")

print_header("MVC Test Suite Complete") 