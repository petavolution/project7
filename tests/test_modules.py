#!/usr/bin/env python3
"""
Test Module Runner

This script tests all unified training modules to ensure they work with
the unified component system and renderer.

Usage:
    python test_modules.py [module_name]

Options:
    --list: List all available modules
    --all: Run all available modules in sequence
"""

import os
import sys
import time
import logging
import importlib
import argparse
from pathlib import Path

# Add the parent directory to sys.path
parent_dir = str(Path(__file__).parent.parent.absolute())
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("module_tester")

try:
    # Try direct imports
    from core.unified_component_system import (
        Component, UI, ComponentFactory
    )
    from clients.pygame.unified_renderer import UnifiedRenderer
    logger.info("Imported core components successfully")
except ImportError as e:
    logger.error(f"Failed to import required modules: {e}")
    sys.exit(1)


class ModuleTester:
    """Test runner for unified modules."""
    
    def __init__(self):
        """Initialize the tester."""
        self.renderer = None
        self.module = None
        self.module_name = None
        self.running = False
        self.fps = 60
        self.start_time = 0
        self.frame_count = 0
        self.last_stats_time = 0
        self.width = 1440
        self.height = 1024
    
    def list_modules(self):
        """List all available unified modules."""
        modules_dir = Path(parent_dir) / "modules"
        print("Available unified modules:")
        
        unified_modules = []
        for file_path in modules_dir.glob("unified_*.py"):
            module_name = file_path.stem
            unified_modules.append(module_name)
        
        # Print in alphabetical order
        for module_name in sorted(unified_modules):
            print(f"  - {module_name}")
        
        return unified_modules
    
    def load_module(self, module_name):
        """Load a unified module.
        
        Args:
            module_name: Name of the module to load
            
        Returns:
            True if module was loaded successfully, False otherwise
        """
        try:
            logger.info(f"Loading module: {module_name}")
            
            # Check if module file exists
            module_path = Path(parent_dir) / "modules" / f"{module_name}.py"
            if not module_path.exists():
                logger.error(f"Module not found: {module_path}")
                return False
            
            # Import the module
            try:
                # Import directly
                module_import_name = f"modules.{module_name}"
                logger.debug(f"Trying to import as {module_import_name}")
                module = importlib.import_module(module_import_name)
            except ImportError as e:
                logger.error(f"Failed to import module {module_name}: {e}")
                return False
            
            # Find the module class (assume the class name matches the file name without the unified_ prefix)
            class_name = module_name.replace("unified_", "")
            class_name = "".join(word.capitalize() for word in class_name.split("_"))
            class_name = f"Unified{class_name}"
            
            logger.debug(f"Looking for class {class_name} in module {module_name}")
            
            # Create renderer if not already created (needed for effects)
            if not self.renderer:
                self.initialize_renderer()
            
            # Get the class
            if hasattr(module, class_name):
                module_class = getattr(module, class_name)
                
                # Initialize with renderer if the module supports it
                try:
                    # Check if the constructor accepts a renderer parameter
                    import inspect
                    sig = inspect.signature(module_class.__init__)
                    if 'renderer' in sig.parameters:
                        # Pass renderer to module
                        self.module = module_class(renderer=self.renderer)
                    else:
                        # Fall back to default init
                        self.module = module_class()
                except Exception as e:
                    logger.warning(f"Error checking constructor, falling back to default: {e}")
                    self.module = module_class()
                
                self.module_name = module_name
                logger.info(f"Module {module_name} loaded successfully as {class_name}")
                return True
            else:
                logger.error(f"Class {class_name} not found in module {module_name}")
                return False
            
        except Exception as e:
            logger.error(f"Error loading module {module_name}: {e}")
            logger.exception("Exception details")
            return False
    
    def initialize_renderer(self):
        """Initialize the pygame renderer."""
        try:
            logger.info("Initializing pygame renderer")
            self.renderer = UnifiedRenderer(
                screen_width=self.width,
                screen_height=self.height,
                title=f"ModuleTester - {self.module_name}"
            )
            
            success = self.renderer.initialize()
            if not success:
                logger.error("Failed to initialize renderer")
                return False
            
            # Set FPS
            self.renderer.fps = self.fps
            return True
            
        except Exception as e:
            logger.error(f"Error initializing renderer: {e}")
            logger.exception("Exception details")
            return False
    
    def run_test(self, module_name):
        """Run a test for a specific module.
        
        Args:
            module_name: Name of the module to test
            
        Returns:
            True if test was successful, False otherwise
        """
        # Load the module
        if not self.load_module(module_name):
            return False
        
        # Initialize the renderer
        if not self.initialize_renderer():
            return False
        
        try:
            # Initialize the module
            logger.info("Initializing module")
            self.module.initialize()
            
            # Main loop
            logger.info("Starting main loop")
            self.running = True
            self.start_time = time.time()
            self.frame_count = 0
            self.last_stats_time = time.time()
            
            while self.running and self.renderer.is_running():
                # Process events
                events = self.renderer.process_events()
                
                # Handle events
                for event in events:
                    if event["type"] == "quit":
                        self.running = False
                    elif event["type"] == "click" and event.get("component_id"):
                        self.module.handle_click(event["component_id"], event["pos"])
                    elif event["type"] == "keydown":
                        self.module.handle_key(event["key"])
                
                # Update module
                self.module.update()
                
                # Get current state
                state = self.module.get_state()
                
                # Build UI
                self.module.build_ui()
                
                # Render
                self.renderer.render(state)
                
                # Update stats
                self.frame_count += 1
                current_time = time.time()
                if current_time - self.last_stats_time >= 5.0:
                    self.show_stats()
                    self.last_stats_time = current_time
            
            logger.info("Test completed")
            return True
            
        except Exception as e:
            logger.error(f"Error running test: {e}")
            logger.exception("Exception details")
            return False
        
        finally:
            # Cleanup
            if self.renderer:
                self.renderer.shutdown()
            
            if self.module:
                self.module.shutdown()
    
    def run_all_tests(self):
        """Run tests for all available modules in sequence."""
        modules = self.list_modules()
        results = {}
        
        for module_name in modules:
            logger.info(f"Testing module: {module_name}")
            results[module_name] = self.run_test(module_name)
        
        # Print summary
        print("\nTest Results:")
        success_count = 0
        for module_name, success in results.items():
            status = "PASS" if success else "FAIL"
            print(f"  {module_name}: {status}")
            if success:
                success_count += 1
        
        print(f"\nSummary: {success_count}/{len(modules)} modules passed")
        
        return success_count == len(modules)
    
    def show_stats(self):
        """Show performance statistics."""
        if not self.renderer:
            return
            
        stats = self.renderer.get_stats()
        elapsed = time.time() - self.start_time
        fps = self.frame_count / elapsed if elapsed > 0 else 0
        
        logger.info(f"FPS: {fps:.1f}, Render time: {stats['render_time']*1000:.2f}ms")
        
        # Log component stats
        comp_stats = stats.get('component_stats', {})
        if comp_stats:
            logger.debug(f"Components: created={comp_stats.get('created', 0)}, " +
                        f"cached={comp_stats.get('cached', 0)}, " +
                        f"reused={comp_stats.get('reused', 0)}")
        
        # Log cache stats
        cache_stats = stats.get('surface_cache', {})
        if cache_stats:
            logger.debug(f"Surface cache: size={cache_stats.get('size', 0)}, " +
                        f"hit_rate={cache_stats.get('hit_rate', 0)*100:.1f}%")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Test Module Runner")
    
    # Add module argument (optional)
    parser.add_argument(
        "module",
        nargs="?",
        help="Name of the module to test"
    )
    
    # Add options
    parser.add_argument(
        "--list",
        action="store_true",
        help="List all available modules"
    )
    
    parser.add_argument(
        "--all",
        action="store_true",
        help="Run all modules in sequence"
    )
    
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging"
    )
    
    args = parser.parse_args()
    
    # Set debug logging if requested
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.setLevel(logging.DEBUG)
    
    tester = ModuleTester()
    
    # List modules if requested
    if args.list:
        tester.list_modules()
        return 0
    
    # Run all tests if requested
    if args.all:
        success = tester.run_all_tests()
        return 0 if success else 1
    
    # Run specific module if provided
    if args.module:
        success = tester.run_test(args.module)
        return 0 if success else 1
    
    # If no arguments, show help
    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main()) 