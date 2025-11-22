#!/usr/bin/env python3
"""
CLI Test Framework for MetaMindIQTrain

Headless testing framework for debugging and validating core functionality.
All tests run in CLI mode without requiring a display.
"""

import sys
import os
import argparse
import time
import traceback
from pathlib import Path
from typing import List, Dict, Any, Callable, Optional, Tuple

# Ensure project root is in path
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Set up logging first
from core.debug_logging import setup_logging, log_startup_info, log_exception, get_logger

# Initialize logging
logger = setup_logging()
log_startup_info()
test_logger = get_logger(__name__)


class TestResult:
    """Result of a single test."""

    def __init__(self, name: str, passed: bool, message: str = "", duration: float = 0.0):
        self.name = name
        self.passed = passed
        self.message = message
        self.duration = duration

    def __repr__(self):
        status = "PASS" if self.passed else "FAIL"
        return f"[{status}] {self.name}: {self.message} ({self.duration:.3f}s)"


class TestSuite:
    """Collection of tests with reporting."""

    def __init__(self, name: str):
        self.name = name
        self.tests: List[Tuple[str, Callable]] = []
        self.results: List[TestResult] = []

    def add_test(self, name: str, test_func: Callable) -> None:
        """Add a test to the suite."""
        self.tests.append((name, test_func))

    def run(self) -> bool:
        """Run all tests and return True if all passed."""
        test_logger.info(f"\n{'='*60}")
        test_logger.info(f"Running Test Suite: {self.name}")
        test_logger.info(f"{'='*60}")

        for name, test_func in self.tests:
            start_time = time.time()
            try:
                test_func()
                duration = time.time() - start_time
                result = TestResult(name, True, "OK", duration)
                test_logger.info(f"  [PASS] {name} ({duration:.3f}s)")
            except AssertionError as e:
                duration = time.time() - start_time
                result = TestResult(name, False, str(e), duration)
                test_logger.error(f"  [FAIL] {name}: {e}")
                log_exception(e, name)
            except Exception as e:
                duration = time.time() - start_time
                result = TestResult(name, False, f"Exception: {e}", duration)
                test_logger.error(f"  [ERROR] {name}: {type(e).__name__}: {e}")
                log_exception(e, name)

            self.results.append(result)

        return self.report()

    def report(self) -> bool:
        """Print test report and return True if all passed."""
        passed = sum(1 for r in self.results if r.passed)
        failed = len(self.results) - passed
        total_time = sum(r.duration for r in self.results)

        test_logger.info(f"\n{'-'*60}")
        test_logger.info(f"Results for {self.name}:")
        test_logger.info(f"  Passed: {passed}/{len(self.results)}")
        test_logger.info(f"  Failed: {failed}/{len(self.results)}")
        test_logger.info(f"  Total time: {total_time:.3f}s")
        test_logger.info(f"{'-'*60}\n")

        return failed == 0


# ============================================================================
# Core Import Tests
# ============================================================================

def test_config_import():
    """Test that config module imports correctly."""
    from config import SCREEN_WIDTH, SCREEN_HEIGHT, calculate_sizes
    assert SCREEN_WIDTH > 0, "SCREEN_WIDTH must be positive"
    assert SCREEN_HEIGHT > 0, "SCREEN_HEIGHT must be positive"
    sizes = calculate_sizes(1024, 768)
    assert 'UI_HEADER_HEIGHT' in sizes, "calculate_sizes must return UI_HEADER_HEIGHT"
    assert sizes['UI_HEADER_HEIGHT'] > 0, "Header height must be positive"


def test_core_training_module_import():
    """Test that TrainingModule imports correctly."""
    from core.training_module import TrainingModule
    assert TrainingModule is not None, "TrainingModule should not be None"
    assert hasattr(TrainingModule, 'get_state'), "TrainingModule should have get_state method"


def test_module_registry_import():
    """Test that module registry imports correctly."""
    import module_registry
    assert hasattr(module_registry, 'AVAILABLE_MODULES'), "Should have AVAILABLE_MODULES"
    assert hasattr(module_registry, 'create_module_instance'), "Should have create_module_instance"


def test_core_components_import():
    """Test that core components import correctly."""
    try:
        from core.components import UI, Component
        assert UI is not None, "UI should not be None"
    except ImportError:
        # Components may have pygame dependency
        test_logger.warning("core.components requires pygame - skipping detailed test")


# ============================================================================
# Module Loading Tests
# ============================================================================

def test_list_available_modules():
    """Test listing available modules."""
    from module_registry import AVAILABLE_MODULES
    assert len(AVAILABLE_MODULES) > 0, "Should have at least one module registered"
    test_logger.info(f"  Found {len(AVAILABLE_MODULES)} registered modules")
    for mod in AVAILABLE_MODULES[:5]:  # Show first 5
        test_logger.debug(f"    - {mod['id']}: {mod['name']}")


def test_module_info():
    """Test getting module info."""
    from module_registry import get_module_info, AVAILABLE_MODULES
    if AVAILABLE_MODULES:
        first_module = AVAILABLE_MODULES[0]
        info = get_module_info(first_module['id'])
        assert info is not None, f"Should get info for {first_module['id']}"
        assert 'name' in info, "Info should have name"


def test_module_class_loading():
    """Test loading module classes."""
    from module_registry import get_module_class, AVAILABLE_MODULES

    loaded = 0
    failed = []

    for mod in AVAILABLE_MODULES:
        try:
            cls = get_module_class(mod['id'])
            if cls is not None:
                loaded += 1
                test_logger.debug(f"    Loaded: {mod['id']}")
            else:
                failed.append(mod['id'])
        except Exception as e:
            failed.append(f"{mod['id']} ({type(e).__name__})")

    test_logger.info(f"  Loaded {loaded}/{len(AVAILABLE_MODULES)} module classes")
    if failed:
        test_logger.warning(f"  Failed to load: {failed[:5]}")  # Show first 5


# ============================================================================
# State Management Tests
# ============================================================================

def test_delta_encoder():
    """Test delta encoding functionality."""
    from core.training_module import DeltaEncoder

    state1 = {'a': 1, 'b': 2, 'c': {'x': 10}}
    state2 = {'a': 1, 'b': 3, 'c': {'x': 10, 'y': 20}}

    delta = DeltaEncoder.compute_delta(state1, state2)
    assert 'b' in delta or delta.get('b') == 3, "Delta should contain changed 'b'"

    test_logger.debug(f"    Delta computed: {delta}")


def test_state_manager():
    """Test state manager functionality."""
    from core.training_module import StateManager

    sm = StateManager()
    state1 = {'score': 0, 'level': 1}
    state2 = {'score': 10, 'level': 1}

    result1 = sm.update_state(state1)
    assert '_meta' in result1, "Result should have metadata"

    result2 = sm.update_state(state2)
    assert result2['_meta']['version'] == 2, "Version should increment"


def test_performance_monitor():
    """Test performance monitoring."""
    from core.training_module import PerformanceMonitor

    pm = PerformanceMonitor()
    for _ in range(10):
        pm.update()
        time.sleep(0.01)

    metrics = pm.get_metrics()
    assert 'fps' in metrics, "Should have fps metric"
    assert metrics['total_frames'] == 10, "Should have 10 frames recorded"


# ============================================================================
# Renderer Tests
# ============================================================================

def test_headless_renderer_init():
    """Test headless renderer initialization."""
    from core.renderer import Renderer, HeadlessBackend

    renderer = Renderer()
    success = renderer.initialize(800, 600, backend="headless", title="Test")
    assert success, "Headless renderer should initialize successfully"
    assert renderer.backend is not None, "Backend should be set"
    assert renderer.backend_name == "headless", "Backend should be headless"
    assert renderer.get_size() == (800, 600), "Size should be 800x600"
    renderer.shutdown()
    test_logger.info("  Headless renderer initialized and shutdown successfully")


def test_renderer_draw_operations():
    """Test renderer draw operations in headless mode."""
    from core.renderer import Renderer

    renderer = Renderer()
    renderer.initialize(800, 600, backend="headless")

    # Test all draw operations
    renderer.clear((0, 0, 0, 255))
    renderer.draw_rectangle(10, 10, 100, 50, (255, 0, 0, 255))
    renderer.draw_rounded_rectangle(20, 20, 80, 40, (0, 255, 0, 255), radius=5)
    renderer.draw_circle(100, 100, 30, (0, 0, 255, 255))
    renderer.draw_line(0, 0, 100, 100, (255, 255, 255, 255), thickness=2)
    renderer.draw_text(50, 50, "Test", font_size=16, color=(255, 255, 255, 255))
    renderer.present()

    # Check rendered elements were recorded
    elements = renderer.backend.get_rendered_elements()
    assert len(elements) > 0, "Should have rendered elements"

    # Find specific element types
    types = [e['type'] for e in elements]
    assert 'clear' in types, "Should have clear operation"
    assert 'rectangle' in types, "Should have rectangle operation"
    assert 'circle' in types, "Should have circle operation"
    assert 'present' in types, "Should have present operation"

    renderer.shutdown()
    test_logger.info(f"  Rendered {len(elements)} elements successfully")


# ============================================================================
# Application Lifecycle Tests
# ============================================================================

def test_app_initialization():
    """Test application initialization in headless mode."""
    from core.app import Application

    app = Application()
    success = app.initialize(800, 600, "Test App", backend="headless")
    assert success, "App should initialize successfully"
    assert app.renderer is not None, "Renderer should be set"
    assert app.renderer.backend_name == "headless", "Backend should be headless"
    app.shutdown()
    test_logger.info("  Application initialized and shutdown successfully")


def test_app_module_lifecycle():
    """Test application module load/start/stop/unload cycle."""
    from core.app import Application
    from module_registry import AVAILABLE_MODULES

    if not AVAILABLE_MODULES:
        test_logger.warning("  No modules available")
        return

    app = Application()
    app.initialize(800, 600, "Test App", backend="headless")

    # Try first available module
    mod_id = AVAILABLE_MODULES[0]['id']

    # Load module
    loaded = app.load_module(mod_id)
    assert loaded, f"Should load module {mod_id}"
    assert mod_id in app.module_registry.loaded_modules, "Module should be in loaded_modules"

    # Start module
    started = app.start_module(mod_id)
    assert started, f"Should start module {mod_id}"
    assert app.active_module_id == mod_id, "Module should be active"

    # Stop module
    stopped = app.stop_module(mod_id)
    assert stopped, f"Should stop module {mod_id}"
    assert app.active_module_id is None, "No module should be active"

    # Unload module
    unloaded = app.unload_module(mod_id)
    assert unloaded, f"Should unload module {mod_id}"

    app.shutdown()
    test_logger.info(f"  Module lifecycle test passed for {mod_id}")


# ============================================================================
# Module Rendering Tests
# ============================================================================

def test_module_render_pipeline():
    """Test module rendering through the full pipeline."""
    from core.app import Application
    from module_registry import AVAILABLE_MODULES

    if not AVAILABLE_MODULES:
        test_logger.warning("  No modules available")
        return

    app = Application()
    app.initialize(800, 600, "Test App", backend="headless")

    # Test each module's render capability
    rendered_count = 0
    failed = []

    for mod_info in AVAILABLE_MODULES:
        mod_id = mod_info['id']
        try:
            if app.load_module(mod_id) and app.start_module(mod_id):
                # Simulate one frame
                app.renderer.clear(app.background_color)
                module = app.module_registry.loaded_modules.get(mod_id)
                if module and hasattr(module, 'render'):
                    module.render(app.renderer)
                    rendered_count += 1
                    test_logger.debug(f"    Rendered: {mod_id}")
                app.stop_module(mod_id)
        except Exception as e:
            failed.append(f"{mod_id}: {e}")
            test_logger.debug(f"    Failed to render {mod_id}: {e}")

    app.shutdown()

    assert rendered_count > 0, "At least one module should render"
    test_logger.info(f"  Rendered {rendered_count}/{len(AVAILABLE_MODULES)} modules")
    if failed:
        test_logger.warning(f"  Failed: {failed[:3]}")


# ============================================================================
# Integration Tests
# ============================================================================

def test_headless_module_state():
    """Test getting module state in headless mode."""
    from module_registry import create_module_instance, AVAILABLE_MODULES

    # Find a simple module to test
    test_modules = ['test_module', 'symbol_memory', 'morph_matrix']

    for mod_id in test_modules:
        try:
            instance = create_module_instance(mod_id)
            if instance:
                state = instance.get_state()
                assert 'game' in state or 'score' in state or state, "State should have content"
                test_logger.info(f"  Got state from {mod_id}")
                return
        except Exception as e:
            test_logger.debug(f"  Could not test {mod_id}: {e}")

    test_logger.warning("  No testable modules found (may need pygame)")


# ============================================================================
# Main Test Runner
# ============================================================================

def create_core_test_suite() -> TestSuite:
    """Create the core functionality test suite."""
    suite = TestSuite("Core Functionality")

    # Import tests
    suite.add_test("Config Import", test_config_import)
    suite.add_test("TrainingModule Import", test_core_training_module_import)
    suite.add_test("Module Registry Import", test_module_registry_import)
    suite.add_test("Core Components Import", test_core_components_import)

    return suite


def create_module_test_suite() -> TestSuite:
    """Create the module loading test suite."""
    suite = TestSuite("Module Loading")

    suite.add_test("List Available Modules", test_list_available_modules)
    suite.add_test("Get Module Info", test_module_info)
    suite.add_test("Load Module Classes", test_module_class_loading)

    return suite


def create_state_test_suite() -> TestSuite:
    """Create the state management test suite."""
    suite = TestSuite("State Management")

    suite.add_test("Delta Encoder", test_delta_encoder)
    suite.add_test("State Manager", test_state_manager)
    suite.add_test("Performance Monitor", test_performance_monitor)

    return suite


def create_renderer_test_suite() -> TestSuite:
    """Create the renderer test suite."""
    suite = TestSuite("Renderer")

    suite.add_test("Headless Renderer Init", test_headless_renderer_init)
    suite.add_test("Renderer Draw Operations", test_renderer_draw_operations)

    return suite


def create_app_test_suite() -> TestSuite:
    """Create the application lifecycle test suite."""
    suite = TestSuite("Application Lifecycle")

    suite.add_test("App Initialization", test_app_initialization)
    suite.add_test("Module Lifecycle", test_app_module_lifecycle)
    suite.add_test("Module Render Pipeline", test_module_render_pipeline)

    return suite


def create_integration_test_suite() -> TestSuite:
    """Create the integration test suite."""
    suite = TestSuite("Integration")

    suite.add_test("Headless Module State", test_headless_module_state)

    return suite


def run_all_tests() -> bool:
    """Run all test suites."""
    test_logger.info("\n" + "=" * 60)
    test_logger.info("MetaMindIQTrain CLI Test Framework")
    test_logger.info("=" * 60 + "\n")

    all_passed = True

    # Run each test suite
    suites = [
        create_core_test_suite(),
        create_module_test_suite(),
        create_state_test_suite(),
        create_renderer_test_suite(),
        create_app_test_suite(),
        create_integration_test_suite(),
    ]

    for suite in suites:
        if not suite.run():
            all_passed = False

    # Final summary
    test_logger.info("\n" + "=" * 60)
    if all_passed:
        test_logger.info("ALL TESTS PASSED")
    else:
        test_logger.error("SOME TESTS FAILED - Check debug-log.txt for details")
    test_logger.info("=" * 60)

    return all_passed


def main():
    """Main entry point for CLI tests."""
    import logging as log_module

    parser = argparse.ArgumentParser(description='MetaMindIQTrain CLI Test Framework')
    parser.add_argument('--suite', choices=['core', 'modules', 'state', 'renderer', 'app', 'integration', 'all'],
                        default='all', help='Test suite to run')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')

    args = parser.parse_args()

    if args.verbose:
        setup_logging(console_level=log_module.DEBUG)

    success = False

    if args.suite == 'all':
        success = run_all_tests()
    elif args.suite == 'core':
        success = create_core_test_suite().run()
    elif args.suite == 'modules':
        success = create_module_test_suite().run()
    elif args.suite == 'state':
        success = create_state_test_suite().run()
    elif args.suite == 'renderer':
        success = create_renderer_test_suite().run()
    elif args.suite == 'app':
        success = create_app_test_suite().run()
    elif args.suite == 'integration':
        success = create_integration_test_suite().run()

    test_logger.info(f"\nDebug log written to: {PROJECT_ROOT / 'debug-log.txt'}")

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
