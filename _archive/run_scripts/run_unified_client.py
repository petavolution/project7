#!/usr/bin/env python3
"""
Unified Client Launcher for MetaMindIQTrain

This launcher provides a high-performance client for the MetaMindIQTrain platform,
capable of loading and running any training module with optimized rendering.

Key optimizations:
1. Component caching and pooling for reduced memory usage
2. Delta encoding for efficient state updates
3. Batch rendering for improved performance
4. Dynamic resolution support for any screen size
5. Automatic module detection and loading
6. Support for multiple rendering backends (pygame, terminal)
"""

import os
import sys
import json
import time
import logging
import argparse
import importlib
import importlib.util
import signal
import traceback
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Union

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("unified_client")

# Add project root to path if needed
project_root = Path(__file__).parent.absolute()
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Try to import the unified component system
try:
    # Try direct import first
    from core.unified_component_system import Component, UI, ComponentFactory, get_stats, reset_stats
except ImportError:
    try:
        # Try with package name
        from MetaMindIQTrain.core.unified_component_system import Component, UI, ComponentFactory, get_stats, reset_stats
    except ImportError:
        try:
            # Try with relative import
            sys.path.append(str(project_root.parent))
            from MetaMindIQTrain.core.unified_component_system import Component, UI, ComponentFactory, get_stats, reset_stats
        except ImportError:
            logger.error("Failed to import unified component system")
            traceback.print_exc()
            sys.exit(1)


class UnifiedClient:
    """Unified client for MetaMindIQTrain platform."""
    
    def __init__(self):
        """Initialize the client."""
        self.args = None
        self.module = None
        self.module_name = None
        self.renderer = None
        self.running = False
        self.start_time = time.time()
        self.frame_count = 0
        self.last_stats_time = 0
        
        # Register signal handlers
        signal.signal(signal.SIGINT, self.handle_exit)
        signal.signal(signal.SIGTERM, self.handle_exit)
    
    def parse_arguments(self):
        """Parse command line arguments."""
        parser = argparse.ArgumentParser(description="MetaMindIQTrain Unified Client")
        
        parser.add_argument(
            "module",
            nargs="?",
            help="Module name to run"
        )
        
        parser.add_argument(
            "--list",
            action="store_true",
            help="List available modules"
        )
        
        parser.add_argument(
            "--terminal",
            action="store_true",
            help="Use terminal renderer"
        )
        
        parser.add_argument(
            "--width",
            type=int,
            default=1440,
            help="Screen width"
        )
        
        parser.add_argument(
            "--height",
            type=int,
            default=1024,
            help="Screen height"
        )
        
        parser.add_argument(
            "--fps",
            type=int,
            default=60,
            help="Target FPS"
        )
        
        parser.add_argument(
            "--debug",
            action="store_true",
            help="Enable debug logging"
        )
        
        self.args = parser.parse_args()
        
        if self.args.debug:
            logging.getLogger().setLevel(logging.DEBUG)
            
        return self.args
    
    def list_modules(self):
        """List available modules."""
        modules_dir = project_root / "modules"
        
        if not modules_dir.exists():
            logger.error(f"Modules directory not found: {modules_dir}")
            return
        
        print("Available modules:")
        
        for file_path in modules_dir.glob("*.py"):
            if file_path.stem.startswith("_"):
                continue
                
            try:
                # Try to import the module to check if it's valid
                spec = importlib.util.spec_from_file_location(file_path.stem, file_path)
                if spec and spec.loader:
                    mod = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(mod)
                    
                    # Check if it has a TrainingModule class
                    has_module = False
                    for attr_name in dir(mod):
                        attr = getattr(mod, attr_name)
                        if (hasattr(attr, "__module__") and 
                            attr.__module__ == file_path.stem and
                            attr_name != "TrainingModule" and
                            hasattr(attr, "build_ui")):
                            has_module = True
                            print(f"  - {file_path.stem}: {attr_name}")
                    
                    if not has_module:
                        print(f"  - {file_path.stem}")
            except Exception as e:
                logger.debug(f"Error loading module {file_path.stem}: {e}")
                print(f"  - {file_path.stem} (error loading)")
    
    def load_module(self, module_name):
        """Load a training module.
        
        Args:
            module_name: Name of the module to load
            
        Returns:
            True if module was loaded successfully, False otherwise
        """
        try:
            logger.info(f"Loading module: {module_name}")
            
            # Try to import as a Python module
            module_path = project_root / "modules" / f"{module_name}.py"
            
            if not module_path.exists():
                logger.error(f"Module not found: {module_path}")
                return False
            
            # Import the module
            spec = importlib.util.spec_from_file_location(module_name, module_path)
            if not spec or not spec.loader:
                logger.error(f"Failed to load module spec: {module_name}")
                return False
                
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            
            # Find the module class
            module_class = None
            for attr_name in dir(mod):
                attr = getattr(mod, attr_name)
                if (hasattr(attr, "__module__") and 
                    attr.__module__ == module_name and
                    attr_name != "TrainingModule" and
                    hasattr(attr, "build_ui")):
                    module_class = attr
                    break
            
            if not module_class:
                logger.error(f"No training module found in {module_name}")
                return False
            
            # Create an instance of the module
            self.module = module_class()
            self.module_name = module_name
            
            logger.info(f"Module {module_name} loaded successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error loading module {module_name}: {e}")
            logger.debug(traceback.format_exc())
            return False
    
    def initialize_renderer(self):
        """Initialize the renderer based on command line arguments."""
        try:
            if self.args.terminal:
                # Terminal renderer
                logger.info("Initializing terminal renderer")
                from MetaMindIQTrain.clients.terminal.unified_renderer import TerminalRenderer
                self.renderer = TerminalRenderer()
            else:
                # Pygame renderer
                logger.info("Initializing pygame renderer")
                from MetaMindIQTrain.clients.pygame.unified_renderer import UnifiedRenderer
                self.renderer = UnifiedRenderer(
                    screen_width=self.args.width,
                    screen_height=self.args.height,
                    title=f"MetaMindIQTrain - {self.module_name}"
                )
                self.renderer.fps = self.args.fps
            
            # Initialize the renderer
            success = self.renderer.initialize()
            if not success:
                logger.error("Failed to initialize renderer")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error initializing renderer: {e}")
            logger.debug(traceback.format_exc())
            return False
    
    def run(self):
        """Run the client."""
        # Parse arguments
        args = self.parse_arguments()
        
        # List modules if requested
        if args.list:
            self.list_modules()
            return
        
        # Check if a module was specified
        if not args.module:
            logger.error("No module specified")
            print("Please specify a module name or use --list to see available modules")
            return
        
        # Load the module
        if not self.load_module(args.module):
            return
        
        # Initialize the renderer
        if not self.initialize_renderer():
            return
        
        try:
            # Initialize the module
            logger.info("Initializing module")
            self.module.initialize()
            
            # Build the initial UI
            ui = self.module.build_ui()
            
            # Main loop
            logger.info("Starting main loop")
            self.running = True
            self.start_time = time.time()
            
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
                
                # Render
                self.renderer.render(state)
                
                # Update stats
                self.frame_count += 1
                current_time = time.time()
                if current_time - self.last_stats_time >= 5.0:
                    self.show_stats()
                    self.last_stats_time = current_time
            
            logger.info("Main loop ended")
            
        except Exception as e:
            logger.error(f"Error running client: {e}")
            logger.debug(traceback.format_exc())
        
        finally:
            # Cleanup
            if self.renderer:
                self.renderer.shutdown()
            
            if self.module:
                self.module.shutdown()
    
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
    
    def handle_exit(self, sig, frame):
        """Handle exit signals."""
        logger.info("Received exit signal, shutting down")
        self.running = False


# Main entry point
if __name__ == "__main__":
    client = UnifiedClient()
    client.run() 