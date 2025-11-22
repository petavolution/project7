#!/usr/bin/env python3
"""
Run All Neural Module Tests

This script discovers and runs all test cases in the neural_module_tests
package, generating a comprehensive report of test results.
"""

import unittest
import sys
from pathlib import Path
import os
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('neural_tests_runner')

# Add the parent directory to sys.path if needed
parent_dir = str(Path(__file__).parent.parent.parent)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)


def discover_and_run_tests():
    """Discover and run all neural module tests."""
    
    # Get the directory containing this script
    test_dir = Path(__file__).parent
    
    logger.info(f"Looking for tests in: {test_dir}")
    
    # Make sure we're in a clean state
    if 'PYGAME_HIDE_SUPPORT_PROMPT' not in os.environ:
        os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'  # Hide pygame welcome message
    
    # Discover all tests
    test_loader = unittest.TestLoader()
    test_suite = test_loader.discover(
        start_dir=str(test_dir),
        pattern='test_*.py',
        top_level_dir=str(test_dir.parent.parent)
    )
    
    # Create a test runner with verbosity
    test_runner = unittest.TextTestRunner(verbosity=2)
    
    # Print test information
    test_count = test_suite.countTestCases()
    logger.info(f"Discovered {test_count} tests across all neural module test files")
    
    # List all test modules
    modules = set()
    for suite in test_suite:
        for test_case in suite:
            modules.add(test_case.__class__.__module__)
    
    logger.info(f"Test modules: {', '.join(sorted(modules))}")
    
    # Run the tests
    logger.info("Running all tests...")
    results = test_runner.run(test_suite)
    
    # Report results
    logger.info("Test run complete")
    logger.info(f"Ran {results.testsRun} tests")
    logger.info(f"Failures: {len(results.failures)}")
    logger.info(f"Errors: {len(results.errors)}")
    logger.info(f"Skipped: {len(results.skipped)}")
    
    # Generate detailed output for any failures or errors
    if results.failures or results.errors:
        logger.error("Detailed failure information:")
        
        for i, (test, traceback) in enumerate(results.failures, 1):
            logger.error(f"\nFAILURE {i}: {test}")
            logger.error(f"{traceback}")
            
        for i, (test, traceback) in enumerate(results.errors, 1):
            logger.error(f"\nERROR {i}: {test}")
            logger.error(f"{traceback}")
    
    # Return success status for exit code
    return len(results.failures) == 0 and len(results.errors) == 0


def main():
    """Main entry point for the test runner."""
    success = discover_and_run_tests()
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main() 