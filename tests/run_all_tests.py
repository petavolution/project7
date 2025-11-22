#!/usr/bin/env python3
"""
Run All Tests

This script discovers and runs all test cases across the entire project,
including neural modules and standard modules.
"""

import unittest
import sys
import os
from pathlib import Path
import logging
import importlib
import argparse
from datetime import datetime

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('test_runner')

# Add the parent directory to sys.path if needed
parent_dir = str(Path(__file__).parent.parent)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)


def discover_and_run_tests(test_paths=None, pattern='test_*.py', verbosity=2, xml_report=None):
    """
    Discover and run all tests.
    
    Args:
        test_paths: List of directories to search for tests. If None, use the tests directory.
        pattern: Pattern to match test files.
        verbosity: Verbosity level for test runner.
        xml_report: If provided, generate XML report at this path.
    
    Returns:
        bool: True if all tests passed, False otherwise.
    """
    # If no test paths provided, use the directory containing this script
    if test_paths is None:
        test_paths = [str(Path(__file__).parent)]
    
    logger.info(f"Looking for tests in: {', '.join(test_paths)}")
    
    # Make sure we're in a clean state
    if 'PYGAME_HIDE_SUPPORT_PROMPT' not in os.environ:
        os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'  # Hide pygame welcome message
    
    # Create suite to hold all tests
    master_suite = unittest.TestSuite()
    
    # Discover tests in each path
    test_loader = unittest.TestLoader()
    for path in test_paths:
        test_path = Path(path)
        logger.info(f"Discovering tests in {test_path}")
        
        # Create a suite for this path
        discovered_suite = test_loader.discover(
            start_dir=str(test_path),
            pattern=pattern,
            top_level_dir=str(Path(__file__).parent.parent)
        )
        
        # Add to master suite
        master_suite.addTest(discovered_suite)
    
    # Count total tests
    test_count = master_suite.countTestCases()
    logger.info(f"Discovered {test_count} tests")
    
    # Create XML test runner if requested
    if xml_report:
        try:
            from xmlrunner import XMLTestRunner
            test_runner = XMLTestRunner(output=os.path.dirname(xml_report), 
                                        outsuffix=os.path.basename(xml_report))
            logger.info(f"Will generate XML report at {xml_report}")
        except ImportError:
            logger.warning("xmlrunner not installed. Falling back to text test runner.")
            test_runner = unittest.TextTestRunner(verbosity=verbosity)
    else:
        # Use text test runner
        test_runner = unittest.TextTestRunner(verbosity=verbosity)
    
    # Run the tests
    logger.info("Running all tests...")
    start_time = datetime.now()
    results = test_runner.run(master_suite)
    end_time = datetime.now()
    duration = end_time - start_time
    
    # Report results
    logger.info(f"Test run complete in {duration.total_seconds():.2f} seconds")
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
    parser = argparse.ArgumentParser(description='Run all tests for the MetaMindIQTrain project')
    parser.add_argument('--paths', nargs='+', help='Paths to search for tests')
    parser.add_argument('--pattern', default='test_*.py', help='Pattern to match test files')
    parser.add_argument('--verbosity', type=int, default=2, help='Verbosity level')
    parser.add_argument('--xml', help='Generate XML report at this path')
    parser.add_argument('--neural-only', action='store_true', help='Only run neural module tests')
    
    args = parser.parse_args()
    
    if args.neural_only:
        # Only run neural module tests
        test_paths = [str(Path(__file__).parent / 'neural_module_tests')]
    elif args.paths:
        test_paths = args.paths
    else:
        # Default: run all tests
        test_paths = [str(Path(__file__).parent)]
    
    success = discover_and_run_tests(
        test_paths=test_paths,
        pattern=args.pattern,
        verbosity=args.verbosity,
        xml_report=args.xml
    )
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main() 