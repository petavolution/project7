#!/usr/bin/env python3
"""
Core Application for MetaMindIQTrain

This module provides the main application class that brings together
the component system, renderer, and module manager to create a unified
application framework.
"""

import logging
import sys
import time
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Union, Callable

# Ensure project root is in path
_project_root = Path(__file__).resolve().parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

# Import core components - try multiple approaches for robustness
try:
    from core.component_system import Component, UIComponent
except ImportError:
    try:
        from MetaMindIQTrain.core.component_system import Component, UIComponent
    except ImportError:
        # Minimal fallback
        class Component: pass
        class UIComponent: pass

try:
    from core.renderer import get_renderer
except ImportError:
    try:
        from MetaMindIQTrain.core.renderer import get_renderer
    except ImportError:
        def get_renderer(): return None

try:
    from core.training_module import TrainingModule
except ImportError:
    try:
        from MetaMindIQTrain.core.training_module import TrainingModule
    except ImportError:
        class TrainingModule: pass

# Import module registry - prefer module_registry.py for actual module loading
try:
    import module_registry as mod_reg
except ImportError:
    try:
        import MetaMindIQTrain.module_registry as mod_reg
    except ImportError:
        mod_reg = None

# Also import core module manager for compatibility
try:
    from core.module_manager import get_module_registry as get_core_module_registry
except ImportError:
    try:
        from MetaMindIQTrain.core.module_manager import get_module_registry as get_core_module_registry
    except ImportError:
        def get_core_module_registry(): return None

logger = logging.getLogger(__name__)

class Application:
    """Main application class for MetaMindIQTrain."""
    
    def __init__(self):
        """Initialize the application."""
        self.renderer = get_renderer()
        # Use core module registry for compatibility, but also track loaded modules directly
        core_registry = get_core_module_registry()
        if core_registry:
            self.module_registry = core_registry
        else:
            # Create a minimal registry object if none available
            class MinimalRegistry:
                def __init__(self):
                    self.modules = {}
                    self.loaded_modules = {}
                def discover_modules(self): pass
                def unload_all(self): self.loaded_modules.clear()
            self.module_registry = MinimalRegistry()

        self.running = False
        self.active_module_id = None
        self.fps = 60
        self.frame_time = 1.0 / self.fps
        self.last_frame_time = 0
        self.frame_count = 0
        self.show_fps = False
        self.background_color = (20, 20, 40, 255)

        # Event handlers
        self.event_handlers = {
            'quit': [],
            'mouse_down': [],
            'mouse_up': [],
            'mouse_move': [],
            'key_down': [],
            'key_up': []
        }
        
    def initialize(self, width: int = 1024, height: int = 768, 
                  title: str = "MetaMindIQTrain", 
                  backend: str = "auto") -> bool:
        """Initialize the application.
        
        Args:
            width: Window width
            height: Window height
            title: Window title
            backend: Renderer backend ("pygame", "webgl", "headless", or "auto")
            
        Returns:
            True if initialization was successful, False otherwise
        """
        # Initialize the renderer
        if not self.renderer.initialize(width, height, backend, title):
            logger.error("Failed to initialize renderer")
            return False
            
        logger.info(f"Renderer initialized: {self.renderer.get_backend_name()}")
        
        # Initialize the module registry (should already be initialized)
        if not self.module_registry.modules:
            logger.info("Discovering modules...")
            self.module_registry.discover_modules()
            
        # Discover specialized module loaders
        self._discover_specialized_loaders()
        
        # Register event handlers
        self._register_default_handlers()
        
        logger.info("Application initialized")
        return True
        
    def _discover_specialized_loaders(self):
        """Discover and register specialized module loaders."""
        try:
            # Check if music module loader is available
            # This is intentionally a soft dependency
            from MetaMindIQTrain.server.optimized import get_music_module_loader
            
            # Get the loader
            music_loader = get_music_module_loader()
            
            # Register with the module registry
            self.module_registry.register_specialized_loader('music', music_loader)
            
            logger.info("Registered music module loader")
            
        except ImportError:
            logger.debug("Music module loader not available")
            
    def _register_default_handlers(self):
        """Register default event handlers."""
        # Quit handler
        self.add_event_handler('quit', self._handle_quit)
        
    def add_event_handler(self, event_type: str, handler: Callable):
        """Add an event handler.
        
        Args:
            event_type: Event type
            handler: Event handler function
        """
        if event_type in self.event_handlers:
            self.event_handlers[event_type].append(handler)
        else:
            self.event_handlers[event_type] = [handler]
            
    def _handle_quit(self, event):
        """Handle quit events.
        
        Args:
            event: Event data
        """
        self.running = False
        
    def load_module(self, module_id: str) -> bool:
        """Load a module.

        Args:
            module_id: Module ID

        Returns:
            True if the module was loaded successfully, False otherwise
        """
        # Check if already loaded
        if module_id in self.module_registry.loaded_modules:
            return True

        # Try to load using module_registry.py first (has actual module definitions)
        module = None
        if mod_reg:
            module = mod_reg.create_module_instance(module_id)

        # Fallback to core module manager
        if not module and hasattr(self.module_registry, 'load_module'):
            module = self.module_registry.load_module(module_id)

        if not module:
            logger.error(f"Failed to load module: {module_id}")
            return False

        # Store in loaded_modules
        self.module_registry.loaded_modules[module_id] = module

        # Set screen dimensions on the module
        width, height = self.renderer.get_size()
        if hasattr(module, 'screen_width'):
            module.screen_width = width
        if hasattr(module, 'screen_height'):
            module.screen_height = height

        # Configure the TrainingModule class display settings
        if hasattr(TrainingModule, 'configure_display'):
            TrainingModule.configure_display(width, height)

        logger.info(f"Loaded module: {module_id}")
        return True
        
    def start_module(self, module_id: str) -> bool:
        """Start a module.

        Args:
            module_id: Module ID

        Returns:
            True if the module was started successfully, False otherwise
        """
        # Stop the current module if any
        if self.active_module_id:
            self.stop_module(self.active_module_id)

        # Load the module if not loaded
        if module_id not in self.module_registry.loaded_modules:
            if not self.load_module(module_id):
                return False

        # Get the module
        module = self.module_registry.loaded_modules.get(module_id)
        if not module:
            logger.error(f"Module '{module_id}' not found after loading")
            return False

        # Start the module - handle both old-style (trigger_event) and new-style modules
        if hasattr(module, 'trigger_event') and callable(module.trigger_event):
            module.trigger_event('start')
        elif hasattr(module, 'is_completed'):
            # Reset completed flag for modules without trigger_event
            module.is_completed = False

        # Set as active module
        self.active_module_id = module_id

        logger.info(f"Started module: {module_id}")
        return True
        
    def stop_module(self, module_id: str) -> bool:
        """Stop a module.

        Args:
            module_id: Module ID

        Returns:
            True if the module was stopped successfully, False otherwise
        """
        # Get the module
        module = self.module_registry.loaded_modules.get(module_id)

        # Stop the module - handle both old-style and new-style modules
        if module:
            if hasattr(module, 'trigger_event') and callable(module.trigger_event):
                module.trigger_event('stop')
            elif hasattr(module, 'cleanup') and callable(module.cleanup):
                module.cleanup()

        # Clear active module if this is the active one
        if self.active_module_id == module_id:
            self.active_module_id = None

        logger.info(f"Stopped module: {module_id}")
        return True
        
    def unload_module(self, module_id: str) -> bool:
        """Unload a module.
        
        Args:
            module_id: Module ID
            
        Returns:
            True if the module was unloaded successfully, False otherwise
        """
        # Stop the module if it's active
        if self.active_module_id == module_id:
            self.stop_module(module_id)
            
        # Unload the module
        if not self.module_registry.unload_module(module_id):
            logger.error(f"Failed to unload module: {module_id}")
            return False
            
        logger.info(f"Unloaded module: {module_id}")
        return True
        
    def reset_module(self, module_id: str) -> bool:
        """Reset a module.
        
        Args:
            module_id: Module ID
            
        Returns:
            True if the module was reset successfully, False otherwise
        """
        # Reset the module
        if not self.module_registry.reset_module(module_id):
            logger.error(f"Failed to reset module: {module_id}")
            return False
            
        logger.info(f"Reset module: {module_id}")
        return True
        
    def run(self):
        """Run the application main loop."""
        if not self.renderer:
            logger.error("Renderer not initialized")
            return
            
        self.running = True
        self.last_frame_time = time.time()
        
        logger.info("Starting main loop")
        
        # Main loop
        while self.running and self.renderer.is_running():
            # Calculate delta time
            current_time = time.time()
            delta_time = current_time - self.last_frame_time
            
            # Process events
            self._process_events()
            
            # Update active module
            if self.active_module_id:
                # Try to get the module and call update() directly
                module = self.module_registry.loaded_modules.get(self.active_module_id)
                if module:
                    if hasattr(module, 'update') and callable(module.update):
                        module.update(delta_time)
                    else:
                        self.module_registry.update_module(self.active_module_id, delta_time)
                
            # Render
            self._render()
            
            # Cap frame rate
            elapsed = time.time() - current_time
            if elapsed < self.frame_time:
                time.sleep(self.frame_time - elapsed)
                
            # Update frame time
            self.last_frame_time = current_time
            self.frame_count += 1
            
        logger.info("Main loop ended")
        
    def _process_events(self):
        """Process events from the renderer."""
        events = self.renderer.process_events()
        
        for event in events:
            event_type = event.get('type')
            
            # Dispatch to handlers
            if event_type in self.event_handlers:
                for handler in self.event_handlers[event_type]:
                    handler(event)
                    
            # Handle module events
            if self.active_module_id and event_type in ['mouse_down', 'mouse_up', 'key_down', 'key_up']:
                module = self.module_registry.loaded_modules.get(self.active_module_id)
                if module:
                    module.trigger_event(event_type, event)
                    
    def _render(self):
        """Render the current frame."""
        # Clear screen
        self.renderer.clear(self.background_color)

        # Render active module
        if self.active_module_id:
            # Try to get the module and call render() directly
            module = self.module_registry.loaded_modules.get(self.active_module_id)
            if module:
                # Call render() directly if the module has it
                if hasattr(module, 'render') and callable(module.render):
                    module.render(self.renderer)
                else:
                    # Fallback to trigger_event for legacy modules
                    self.module_registry.render_module(self.active_module_id, self.renderer)

        # Render FPS if enabled
        if self.show_fps:
            fps = 1.0 / max(0.001, time.time() - self.last_frame_time)
            self.renderer.draw_text(
                10, 10,
                f"FPS: {fps:.1f}",
                16, (255, 255, 0, 255),
                "left"
            )

        # Present the frame
        self.renderer.present()
        
    def shutdown(self):
        """Shut down the application."""
        logger.info("Shutting down application")
        
        # Unload all modules
        self.module_registry.unload_all()
        
        # Shut down renderer
        if self.renderer:
            self.renderer.shutdown()
            
        logger.info("Application shut down")
        
    def set_fps(self, fps: int):
        """Set the target frames per second.
        
        Args:
            fps: Target FPS
        """
        self.fps = max(1, fps)
        self.frame_time = 1.0 / self.fps
        
    def set_background_color(self, color: Tuple[int, int, int, int]):
        """Set the background color.
        
        Args:
            color: RGBA color
        """
        self.background_color = color
        
    def toggle_fps_display(self):
        """Toggle FPS display."""
        self.show_fps = not self.show_fps
        
    def get_module_info(self, module_id: str) -> Optional[Dict[str, Any]]:
        """Get information about a module.
        
        Args:
            module_id: Module ID
            
        Returns:
            Dictionary containing module information or None if not found
        """
        return self.module_registry.get_module_info(module_id)
        
    def get_module_state(self, module_id: str) -> Optional[Dict[str, Any]]:
        """Get the state of a module.
        
        Args:
            module_id: Module ID
            
        Returns:
            Dictionary containing the module state or None if not found
        """
        return self.module_registry.get_module_state(module_id)
        
    def list_modules(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """List available modules.

        Args:
            category: Optional category filter

        Returns:
            List of dictionaries containing module information
        """
        # Prefer module_registry.py's AVAILABLE_MODULES
        if mod_reg and hasattr(mod_reg, 'AVAILABLE_MODULES'):
            modules = mod_reg.AVAILABLE_MODULES
            if category:
                modules = [m for m in modules if m.get('category', '').lower() == category.lower()]
            return modules

        # Fallback to core module registry
        if hasattr(self.module_registry, 'list_modules'):
            return self.module_registry.list_modules(category)

        return []
        
    def get_active_module_id(self) -> Optional[str]:
        """Get the ID of the active module.
        
        Returns:
            Module ID or None if no module is active
        """
        return self.active_module_id

# Singleton instance
_app_instance = None

def get_application() -> Application:
    """Get the singleton application instance.
    
    Returns:
        Application instance
    """
    global _app_instance
    if _app_instance is None:
        _app_instance = Application()
    return _app_instance 