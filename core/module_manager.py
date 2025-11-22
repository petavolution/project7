#!/usr/bin/env python3
"""
Module Manager for MetaMindIQTrain

This module provides a unified management system for training modules,
handling their discovery, loading, lifecycle, and resource management.
It replaces the older module_registry with a more flexible and efficient design.
"""

import importlib
import logging
import sys
import inspect
import json
from pathlib import Path
from typing import Dict, List, Any, Optional, Type, Union, Callable

# Import the unified component system
from MetaMindIQTrain.core.component_system import Component

logger = logging.getLogger(__name__)

class TrainingModule(Component):
    """
    Base class for all training modules in the MetaMindIQTrain platform.
    
    This class extends the base Component with training-specific capabilities
    while maintaining modularity and composition over inheritance.
    """
    
    def __init__(self, module_id: Optional[str] = None):
        """Initialize a training module.
        
        Args:
            module_id: Optional module ID (defaults to class name if not provided)
        """
        super().__init__(module_id or self.__class__.__name__.lower())
        
        # Basic module properties
        self.set_property('name', self.__class__.__name__)
        self.set_property('description', 'Training module')
        self.set_property('category', 'General')
        self.set_property('difficulty', 'Medium')
        self.set_property('version', '1.0.0')
        
        # Runtime state
        self.set_property('initialized', False)
        self.set_property('active', False)
        self.set_property('score', 0)
        self.set_property('level', 1)
        
        # Add handler for lifecycle events
        self.add_event_handler('initialize', self._handle_initialize)
        self.add_event_handler('start', self._handle_start)
        self.add_event_handler('stop', self._handle_stop)
        self.add_event_handler('reset', self._handle_reset)
        self.add_event_handler('update', self._handle_update)
        
        # Register renderer events
        self.add_event_handler('render', self._handle_render)
        self.add_event_handler('resize', self._handle_resize)
        
        # Screen dimensions (will be updated by resize event)
        self.set_property('screen_width', 800)
        self.set_property('screen_height', 600)

    def _handle_initialize(self) -> bool:
        """Initialize the module.
        
        Returns:
            True if initialization was successful, False otherwise
        """
        # Set initialized flag
        self.set_property('initialized', True)
        logger.info(f"Module '{self.get_property('name')}' initialized")
        return True
        
    def _handle_start(self) -> bool:
        """Start the module.
        
        Returns:
            True if the module was started successfully, False otherwise
        """
        # Check if initialized
        if not self.get_property('initialized'):
            logger.warning(f"Cannot start module '{self.get_property('name')}' - not initialized")
            return False
            
        # Set active flag
        self.set_property('active', True)
        logger.info(f"Module '{self.get_property('name')}' started")
        return True
        
    def _handle_stop(self) -> bool:
        """Stop the module.
        
        Returns:
            True if the module was stopped successfully, False otherwise
        """
        # Set active flag
        self.set_property('active', False)
        logger.info(f"Module '{self.get_property('name')}' stopped")
        return True
        
    def _handle_reset(self) -> bool:
        """Reset the module.
        
        Returns:
            True if the module was reset successfully, False otherwise
        """
        # Reset score and level
        self.set_property('score', 0)
        self.set_property('level', 1)
        logger.info(f"Module '{self.get_property('name')}' reset")
        return True
        
    def _handle_update(self, delta_time: float) -> bool:
        """Update the module state.
        
        Args:
            delta_time: Time elapsed since the last update in seconds
            
        Returns:
            True if the module was updated successfully, False otherwise
        """
        # Base implementation does nothing
        return True
        
    def _handle_render(self, renderer) -> bool:
        """Render the module.
        
        Args:
            renderer: The renderer to use
            
        Returns:
            True if the module was rendered successfully, False otherwise
        """
        # Delegate to the render method
        self.render(renderer)
        return True
        
    def _handle_resize(self, width: int, height: int) -> bool:
        """Handle a resize event.
        
        Args:
            width: New screen width
            height: New screen height
            
        Returns:
            True if the resize was handled successfully, False otherwise
        """
        # Update screen dimensions
        self.set_property('screen_width', width)
        self.set_property('screen_height', height)
        return True
        
    def get_state(self) -> Dict[str, Any]:
        """Get the current state of the module.
        
        Returns:
            Dictionary containing the module state
        """
        # Get basic state from properties
        return {
            'id': self.id,
            'name': self.get_property('name'),
            'description': self.get_property('description'),
            'category': self.get_property('category'),
            'difficulty': self.get_property('difficulty'),
            'version': self.get_property('version'),
            'score': self.get_property('score'),
            'level': self.get_property('level'),
            'active': self.get_property('active'),
            'initialized': self.get_property('initialized')
        }
        
    def render(self, renderer):
        """Render the module.
        
        This method should be overridden by subclasses to implement rendering.
        
        Args:
            renderer: The renderer to use
        """
        # Base implementation renders a placeholder
        width = self.get_property('screen_width')
        height = self.get_property('screen_height')
        
        # Draw a background
        renderer.draw_rectangle(0, 0, width, height, (20, 20, 50, 255))
        
        # Draw module name
        name = self.get_property('name')
        renderer.draw_text(
            width // 2, height // 3, 
            name, 
            32, (255, 255, 255, 255), 
            "center"
        )
        
        # Draw module description
        description = self.get_property('description')
        renderer.draw_text(
            width // 2, height // 2, 
            description, 
            20, (200, 200, 200, 255), 
            "center"
        )
        
        # Draw score and level
        score = self.get_property('score')
        level = self.get_property('level')
        renderer.draw_text(
            width // 2, height * 2 // 3, 
            f"Score: {score} | Level: {level}", 
            24, (255, 255, 100, 255), 
            "center"
        )

class ModuleRegistry:
    """
    Registry for training modules.
    
    This class provides methods for discovering, loading, and managing
    training modules. It supports dynamic module discovery and specialized
    module loaders.
    """
    
    def __init__(self):
        """Initialize the module registry."""
        self.modules = {}  # Available module information
        self.loaded_modules = {}  # Loaded module instances
        self.specialized_loaders = {}  # Specialized module loaders
        
    def discover_modules(self):
        """Discover available modules from the module directory.
        
        This method scans the modules directory for Python files containing
        TrainingModule subclasses.
        """
        try:
            # Get the modules directory
            modules_dir = Path(__file__).parent.parent / "modules"
            
            if not modules_dir.exists():
                logger.warning(f"Modules directory not found: {modules_dir}")
                return
                
            # Scan for Python files
            for file_path in modules_dir.glob("**/*.py"):
                # Skip __init__.py, base files, and files beginning with underscore
                if file_path.name.startswith("__") or file_path.name.startswith("_"):
                    continue
                    
                # Skip obvious utilities
                if "utils" in file_path.name or "helpers" in file_path.name:
                    continue
                    
                # Generate module path
                rel_path = file_path.relative_to(modules_dir.parent)
                module_path = ".".join(rel_path.with_suffix("").parts)
                
                try:
                    # Import the module
                    module = importlib.import_module(module_path)
                    
                    # Look for TrainingModule subclasses
                    for name, obj in inspect.getmembers(module, inspect.isclass):
                        if (issubclass(obj, TrainingModule) and 
                            obj is not TrainingModule and 
                            obj.__module__ == module_path):
                            
                            # Create a module ID (use a reasonable default)
                            if hasattr(obj, 'ID'):
                                module_id = obj.ID
                            else:
                                module_id = name.lower()
                                
                            # Get the base directory name for category
                            category = file_path.parent.name.capitalize()
                            if category == "Modules":
                                category = "General"
                                
                            # Create module info
                            module_info = {
                                'id': module_id,
                                'name': getattr(obj, 'NAME', name),
                                'description': getattr(obj, 'DESCRIPTION', ''),
                                'category': getattr(obj, 'CATEGORY', category),
                                'difficulty': getattr(obj, 'DIFFICULTY', 'Medium'),
                                'version': getattr(obj, 'VERSION', '1.0.0'),
                                'class_path': f'{module_path}.{name}',
                                'file_path': str(file_path)
                            }
                            
                            # Add to registry
                            self.modules[module_id] = module_info
                            logger.info(f"Discovered module: {module_info['name']} ({module_id})")
                            
                except (ImportError, AttributeError) as e:
                    logger.warning(f"Error importing module from {file_path}: {e}")
                    
            logger.info(f"Discovered {len(self.modules)} modules")
                
        except Exception as e:
            logger.error(f"Error discovering modules: {e}")
            
    def register_specialized_loader(self, category: str, loader):
        """Register a specialized module loader.
        
        Args:
            category: Module category (e.g., 'music')
            loader: Loader instance
        """
        self.specialized_loaders[category.lower()] = loader
        logger.info(f"Registered specialized loader for '{category}' modules")
        
    def register_module(self, module_class: Type[TrainingModule], module_id: Optional[str] = None):
        """Register a module class directly.
        
        Args:
            module_class: TrainingModule subclass
            module_id: Optional module ID (defaults to class name)
        """
        # Use class name as ID if not provided
        if not module_id:
            module_id = module_class.__name__.lower()
            
        # Create module info
        module_info = {
            'id': module_id,
            'name': getattr(module_class, 'NAME', module_class.__name__),
            'description': getattr(module_class, 'DESCRIPTION', ''),
            'category': getattr(module_class, 'CATEGORY', 'General'),
            'difficulty': getattr(module_class, 'DIFFICULTY', 'Medium'),
            'version': getattr(module_class, 'VERSION', '1.0.0'),
            'class_path': f'{module_class.__module__}.{module_class.__name__}',
            'class': module_class  # Store the class directly
        }
        
        # Add to registry
        self.modules[module_id] = module_info
        logger.info(f"Registered module: {module_info['name']} ({module_id})")
        
    def get_module_info(self, module_id: str) -> Optional[Dict[str, Any]]:
        """Get information about a module.
        
        Args:
            module_id: Module ID
            
        Returns:
            Dictionary containing module information or None if not found
        """
        # Check registry
        if module_id in self.modules:
            return self.modules[module_id].copy()
            
        # Check specialized loaders
        for category, loader in self.specialized_loaders.items():
            if hasattr(loader, 'get_module_info'):
                info = loader.get_module_info(module_id)
                if info:
                    return info
                    
        return None
        
    def list_modules(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """List available modules.
        
        Args:
            category: Optional category filter
            
        Returns:
            List of dictionaries containing module information
        """
        result = []
        
        # Add modules from registry
        for module_id, info in self.modules.items():
            if category is None or info['category'].lower() == category.lower():
                result.append(info.copy())
                
        # Add modules from specialized loaders
        for loader_category, loader in self.specialized_loaders.items():
            if category is None or loader_category.lower() == category.lower():
                if hasattr(loader, 'list_modules'):
                    modules = loader.list_modules()
                    for module in modules:
                        module['from_specialized_loader'] = True
                        result.append(module)
                        
        return result
        
    def load_module(self, module_id: str, **kwargs) -> Optional[TrainingModule]:
        """Load a module by ID.
        
        Args:
            module_id: Module ID
            **kwargs: Additional parameters to pass to the module constructor
            
        Returns:
            Module instance or None if not found
        """
        # Check if already loaded
        if module_id in self.loaded_modules:
            return self.loaded_modules[module_id]
            
        # Get module info
        info = self.get_module_info(module_id)
        if not info:
            logger.error(f"Module '{module_id}' not found")
            return None
            
        # Check if a specialized loader should handle this
        category = info.get('category', '').lower()
        if category in self.specialized_loaders:
            logger.debug(f"Using specialized loader for '{module_id}'")
            loader = self.specialized_loaders[category]
            
            # Try to load using the specialized loader
            if hasattr(loader, 'load_module'):
                try:
                    module = loader.load_module(module_id, **kwargs)
                    if module:
                        self.loaded_modules[module_id] = module
                        return module
                except Exception as e:
                    logger.error(f"Error using specialized loader for '{module_id}': {e}")
                    # Fall back to standard loading
                    
        # Standard loading path
        try:
            # Check if class is directly available
            if 'class' in info:
                module_class = info['class']
            else:
                # Get class from path
                class_path = info['class_path']
                module_path, class_name = class_path.rsplit('.', 1)
                
                # Import the module
                module = importlib.import_module(module_path)
                
                # Get the class
                module_class = getattr(module, class_name)
                
            # Create instance
            instance = module_class(module_id=module_id, **kwargs)
            
            # Initialize the module
            instance.trigger_event('initialize')
            
            # Store in loaded modules
            self.loaded_modules[module_id] = instance
            
            logger.info(f"Loaded module: {info['name']} ({module_id})")
            return instance
            
        except ImportError as e:
            logger.error(f"Error importing module '{module_id}': {e}")
        except AttributeError as e:
            logger.error(f"Error finding class for module '{module_id}': {e}")
        except Exception as e:
            logger.error(f"Error creating module '{module_id}': {e}")
            
        return None
        
    def unload_module(self, module_id: str) -> bool:
        """Unload a module.
        
        Args:
            module_id: Module ID
            
        Returns:
            True if the module was unloaded successfully, False otherwise
        """
        # Check if loaded
        if module_id not in self.loaded_modules:
            logger.warning(f"Module '{module_id}' not loaded")
            return False
            
        # Get module info
        info = self.get_module_info(module_id)
        if not info:
            logger.error(f"Module '{module_id}' not found in registry")
            return False
            
        # Check if a specialized loader should handle this
        category = info.get('category', '').lower()
        if category in self.specialized_loaders:
            logger.debug(f"Using specialized loader to unload '{module_id}'")
            loader = self.specialized_loaders[category]
            
            # Try to unload using the specialized loader
            if hasattr(loader, 'unload_module'):
                try:
                    result = loader.unload_module(module_id)
                    if result:
                        # Remove from loaded modules
                        del self.loaded_modules[module_id]
                        return True
                except Exception as e:
                    logger.error(f"Error using specialized loader to unload '{module_id}': {e}")
                    # Fall back to standard unloading
                    
        # Standard unloading path
        try:
            # Get the module instance
            module = self.loaded_modules[module_id]
            
            # Stop the module if it's active
            if module.get_property('active'):
                module.trigger_event('stop')
                
            # Remove from loaded modules
            del self.loaded_modules[module_id]
            
            logger.info(f"Unloaded module: {module_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error unloading module '{module_id}': {e}")
            return False
            
    def unload_all(self):
        """Unload all loaded modules."""
        for module_id in list(self.loaded_modules.keys()):
            self.unload_module(module_id)
            
    def start_module(self, module_id: str) -> bool:
        """Start a module.
        
        Args:
            module_id: Module ID
            
        Returns:
            True if the module was started successfully, False otherwise
        """
        # Check if loaded
        if module_id not in self.loaded_modules:
            logger.warning(f"Cannot start module '{module_id}' - not loaded")
            return False
            
        # Get the module instance
        module = self.loaded_modules[module_id]
        
        # Start the module
        return module.trigger_event('start')
        
    def stop_module(self, module_id: str) -> bool:
        """Stop a module.
        
        Args:
            module_id: Module ID
            
        Returns:
            True if the module was stopped successfully, False otherwise
        """
        # Check if loaded
        if module_id not in self.loaded_modules:
            logger.warning(f"Cannot stop module '{module_id}' - not loaded")
            return False
            
        # Get the module instance
        module = self.loaded_modules[module_id]
        
        # Stop the module
        return module.trigger_event('stop')
        
    def reset_module(self, module_id: str) -> bool:
        """Reset a module.
        
        Args:
            module_id: Module ID
            
        Returns:
            True if the module was reset successfully, False otherwise
        """
        # Check if loaded
        if module_id not in self.loaded_modules:
            logger.warning(f"Cannot reset module '{module_id}' - not loaded")
            return False
            
        # Get the module instance
        module = self.loaded_modules[module_id]
        
        # Reset the module
        return module.trigger_event('reset')
        
    def update_module(self, module_id: str, delta_time: float) -> bool:
        """Update a module.
        
        Args:
            module_id: Module ID
            delta_time: Time elapsed since the last update in seconds
            
        Returns:
            True if the module was updated successfully, False otherwise
        """
        # Check if loaded
        if module_id not in self.loaded_modules:
            logger.warning(f"Cannot update module '{module_id}' - not loaded")
            return False
            
        # Get the module instance
        module = self.loaded_modules[module_id]
        
        # Update the module
        return module.trigger_event('update', delta_time)
        
    def render_module(self, module_id: str, renderer) -> bool:
        """Render a module.
        
        Args:
            module_id: Module ID
            renderer: The renderer to use
            
        Returns:
            True if the module was rendered successfully, False otherwise
        """
        # Check if loaded
        if module_id not in self.loaded_modules:
            logger.warning(f"Cannot render module '{module_id}' - not loaded")
            return False
            
        # Get the module instance
        module = self.loaded_modules[module_id]
        
        # Render the module
        return module.trigger_event('render', renderer)
        
    def resize_module(self, module_id: str, width: int, height: int) -> bool:
        """Resize a module.
        
        Args:
            module_id: Module ID
            width: New screen width
            height: New screen height
            
        Returns:
            True if the module was resized successfully, False otherwise
        """
        # Check if loaded
        if module_id not in self.loaded_modules:
            logger.warning(f"Cannot resize module '{module_id}' - not loaded")
            return False
            
        # Get the module instance
        module = self.loaded_modules[module_id]
        
        # Resize the module
        return module.trigger_event('resize', width, height)
        
    def get_module_state(self, module_id: str) -> Optional[Dict[str, Any]]:
        """Get the state of a module.
        
        Args:
            module_id: Module ID
            
        Returns:
            Dictionary containing the module state or None if not found
        """
        # Check if loaded
        if module_id not in self.loaded_modules:
            logger.warning(f"Cannot get state of module '{module_id}' - not loaded")
            return None
            
        # Get the module instance
        module = self.loaded_modules[module_id]
        
        # Get the module state
        return module.get_state()

# Singleton instance
_registry_instance = None

def get_module_registry() -> ModuleRegistry:
    """Get the singleton module registry instance.
    
    Returns:
        ModuleRegistry instance
    """
    global _registry_instance
    if _registry_instance is None:
        _registry_instance = ModuleRegistry()
        _registry_instance.discover_modules()
    return _registry_instance 