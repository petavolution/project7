"""
Module Registry
Manages the registration and discovery of training modules
"""

import importlib
import logging
import inspect
import os
import sys
from typing import Dict, List, Any, Optional, Callable, Type, Union, TypeVar
from pathlib import Path
import concurrent.futures
import time
import threading
import functools
import re

from MetaMindIQTrain.core.training_module import TrainingModule

logger = logging.getLogger(__name__)

T = TypeVar('T', bound=TrainingModule)

# Module cache to avoid repeated imports
_module_cache = {}
_module_info_cache = {}
_module_class_cache = {}
_discovering = False
_discovery_lock = threading.RLock()
_last_discovery_time = 0
_DISCOVERY_TIMEOUT = 30  # seconds

def discover_modules(force_refresh: bool = False) -> List[str]:
    """
    Discover available training modules
    
    Args:
        force_refresh: Force rediscovery even if cached
        
    Returns:
        List of module names
    """
    global _discovering, _last_discovery_time
    
    # Check if we need to refresh
    current_time = time.time()
    if not force_refresh and _module_cache and current_time - _last_discovery_time < _DISCOVERY_TIMEOUT:
        return list(_module_cache.keys())
        
    # Use a lock to prevent multiple threads from discovering simultaneously
    with _discovery_lock:
        # Double-check after acquiring lock
        if _discovering:
            return list(_module_cache.keys())
            
        _discovering = True
        try:
            # Import all module files in the modules directory
            modules_dir = os.path.dirname(os.path.abspath(__file__))
            module_files = [f for f in os.listdir(modules_dir) 
                           if f.endswith('_module.py')]
            
            # Clear cache if forcing refresh
            if force_refresh:
                _module_cache.clear()
                _module_info_cache.clear()
                _module_class_cache.clear()
            
            # Process modules in parallel for faster loading
            with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                futures = {executor.submit(_process_module_file, f): f for f in module_files
                          if force_refresh or f not in _module_cache}
                
                for future in concurrent.futures.as_completed(futures):
                    # Just wait for completion, results are stored in cache
                    try:
                        future.result()
                    except Exception as e:
                        logger.error(f"Error processing module: {e}")
            
            _last_discovery_time = time.time()
            return list(_module_cache.keys())
        finally:
            _discovering = False

def _process_module_file(filename: str) -> None:
    """
    Process a module file and add it to the cache
    
    Args:
        filename: Name of the module file
    """
    try:
        # Extract module name from filename
        module_name = filename[:-3]  # Remove .py
        
        # Import the module
        module_path = f"MetaMindIQTrain.modules.{module_name}"
        module = importlib.import_module(module_path)
        
        # Find training module class
        for name, obj in inspect.getmembers(module):
            if (inspect.isclass(obj) and issubclass(obj, TrainingModule) and 
                obj is not TrainingModule):
                
                # Get module ID from info or from filename
                module_info = getattr(obj, "get_module_info", lambda: {})()
                module_id = module_info.get('id', module_name.replace('_module', ''))
                
                # Store in cache
                _module_cache[module_id] = module
                _module_info_cache[module_id] = module_info
                _module_class_cache[module_id] = obj
                break
    except Exception as e:
        logger.error(f"Failed to load module from {filename}: {e}")

def get_available_modules(force_refresh: bool = False) -> List[str]:
    """
    Get list of available module IDs
    
    Args:
        force_refresh: Force rediscovery even if cached
        
    Returns:
        List of module IDs
    """
    return discover_modules(force_refresh)

def get_module_info(module_id: str) -> Dict[str, Any]:
    """
    Get information about a specific module
    
    Args:
        module_id: ID of the module
        
    Returns:
        Module information dictionary
    """
    # Ensure modules are discovered
    if not _module_cache:
        discover_modules()
        
    if module_id not in _module_info_cache:
        # Try to load the module
        logger.debug(f"Module {module_id} not found in cache, trying to discover it")
        discover_modules(force_refresh=True)
        
    return _module_info_cache.get(module_id, {})

def get_module_class(module_id: str) -> Optional[Type[TrainingModule]]:
    """
    Get the module class by ID
    
    Args:
        module_id: ID of the module
        
    Returns:
        Module class or None if not found
    """
    # Ensure modules are discovered
    if not _module_cache:
        discover_modules()
        
    if module_id not in _module_class_cache:
        # Try to load the module
        logger.debug(f"Module {module_id} not found in cache, trying to discover it")
        discover_modules(force_refresh=True)
        
    return _module_class_cache.get(module_id)

def create_module_instance(module_id: str, **kwargs) -> Optional[TrainingModule]:
    """
    Create a new instance of a module
    
    Args:
        module_id: ID of the module
        **kwargs: Additional arguments to pass to the module constructor
        
    Returns:
        Module instance or None if module not found
    """
    module_class = get_module_class(module_id)
    if not module_class:
        logger.error(f"Module {module_id} not found")
        return None
        
    try:
        # Look for a create_module factory function first
        if hasattr(module_class, 'create_module'):
            return module_class.create_module(**kwargs)
        
        # Otherwise instantiate directly
        return module_class(**kwargs)
    except Exception as e:
        logger.error(f"Failed to create module {module_id}: {e}")
        return None 