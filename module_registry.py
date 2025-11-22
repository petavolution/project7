#!/usr/bin/env python3
"""
Module Registry for MetaMindIQTrain

This module manages the available training modules and provides factory functions
to create module instances. It uses dynamic loading to avoid circular imports.
"""

import importlib
import logging
import os
import sys
import inspect
from pathlib import Path
from typing import Dict, List, Any, Optional, Type, Union

logger = logging.getLogger(__name__)

# Ensure project root is in path
_project_root = Path(__file__).resolve().parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

# Add modules directory to sys.path
modules_dir = str(_project_root / 'modules')
if modules_dir not in sys.path:
    sys.path.append(modules_dir)

# Import the base TrainingModule class - try multiple approaches
try:
    from core.training_module import TrainingModule
except ImportError:
    try:
        from MetaMindIQTrain.core.training_module import TrainingModule
    except ImportError:
        TrainingModule = None
        logger.warning("Could not import TrainingModule base class")

# Dictionary of available modules
# Each module must have at least:
# - id: Unique identifier
# - name: Display name
# - description: Short description
# - class_path: Import path for the module class (uses modules.evolve structure)
AVAILABLE_MODULES = [
    {
        'id': 'symbol_memory',
        'name': 'Symbol Memory',
        'description': 'Memory training with symbol patterns to enhance recall abilities.',
        'class_path': 'modules.evolve.symbol_memory.symbol_memory_mvc.SymbolMemory',
        'difficulty': 'Medium',
        'category': 'Memory'
    },
    {
        'id': 'morph_matrix',
        'name': 'Morph Matrix',
        'description': 'Matrix-based cognitive training module enhancing pattern recognition.',
        'class_path': 'modules.evolve.morph_matrix.morph_matrix_mvc.MorphMatrix',
        'difficulty': 'Medium',
        'category': 'Pattern Recognition'
    },
    {
        'id': 'expand_vision',
        'name': 'Expand Vision',
        'description': 'Peripheral vision training to enhance visual field awareness.',
        'class_path': 'modules.evolve.expand_vision.expand_vision_mvc.ExpandVision',
        'difficulty': 'Medium',
        'category': 'Visual Attention'
    },
    {
        'id': 'expand_vision_grid',
        'name': 'Expand Vision Grid',
        'description': 'Grid-based peripheral vision training.',
        'class_path': 'modules.evolve.expand_vision_grid.expand_vision_grid_mvc.ExpandVisionGrid',
        'difficulty': 'Medium',
        'category': 'Visual Attention'
    },
    {
        'id': 'neural_flow',
        'name': 'Neural Flow',
        'description': 'Train cognitive processing speed and neural pathway formation.',
        'class_path': 'modules.evolve.neural_flow.neural_flow_mvc.NeuralFlow',
        'difficulty': 'Hard',
        'category': 'Cognitive Flexibility'
    },
    {
        'id': 'quantum_memory',
        'name': 'Quantum Memory',
        'description': 'Advanced memory training using quantum-inspired mechanics.',
        'class_path': 'modules.evolve.quantum_memory.quantum_memory_mvc.QuantumMemory',
        'difficulty': 'Hard',
        'category': 'Advanced Memory'
    },
    {
        'id': 'neural_synthesis',
        'name': 'Neural Synthesis',
        'description': 'Multi-modal training combining visual and auditory patterns.',
        'class_path': 'modules.evolve.neural_synthesis.neural_synthesis_mvc.NeuralSynthesis',
        'difficulty': 'Medium',
        'category': 'Advanced Cognition'
    },
    {
        'id': 'synesthetic_training',
        'name': 'Synesthetic Training',
        'description': 'Cross-sensory association training for enhanced perception.',
        'class_path': 'modules.evolve.synesthetic_training.synesthetic_training_mvc.SynestheticTraining',
        'difficulty': 'Medium',
        'category': 'Cross-Modal'
    }
]

# Cache for loaded module classes
_module_class_cache = {}

# Registry for specialized module loaders
_module_type_loaders = {}

def register_module_type(module_type: str, loader: Any) -> bool:
    """Register a specialized loader for a module type.
    
    Args:
        module_type: Type of module (e.g., 'music')
        loader: Loader instance for this module type
    
    Returns:
        True if successful, False otherwise
    """
    global _module_type_loaders
    
    if module_type in _module_type_loaders:
        logger.warning(f"Module type '{module_type}' already has a registered loader")
    
    _module_type_loaders[module_type] = loader
    logger.info(f"Registered specialized loader for module type '{module_type}'")
    return True

def configure_modules_display(width: int, height: int):
    """Configure display settings for all modules.
    
    Args:
        width: Screen width
        height: Screen height
    """
    TrainingModule.configure_display(width, height)
    logger.info(f"Configured display settings for all modules: {width}x{height}")


def get_module_info(module_id: str) -> Optional[Dict[str, Any]]:
    """Get information about a module.
    
    Args:
        module_id: Module identifier
        
    Returns:
        Module information or None if not found
    """
    for module in AVAILABLE_MODULES:
        if module['id'] == module_id:
            return module
    return None


def get_module_class(module_id: str) -> Optional[Type[TrainingModule]]:
    """Get a module class by ID.
    
    This function loads the module class dynamically to avoid circular imports.
    It caches the loaded classes for efficiency.
    
    Args:
        module_id: Module identifier
        
    Returns:
        Module class or None if not found
    """
    # Check cache first
    if module_id in _module_class_cache:
        return _module_class_cache[module_id]
    
    # Get module info
    module_info = get_module_info(module_id)
    if not module_info:
        logger.error(f"Module {module_id} not found")
        return None
    
    # Check if this module has a specialized loader
    module_type = module_info.get('module_type')
    if module_type in _module_type_loaders:
        logger.debug(f"Using specialized loader for module type '{module_type}'")
        loader = _module_type_loaders[module_type]
        
        # Try to get the class through the loader
        if hasattr(loader, 'get_module_class'):
            try:
                module_class = loader.get_module_class(module_id)
                if module_class:
                    # Cache the class
                    _module_class_cache[module_id] = module_class
                    return module_class
            except Exception as e:
                logger.error(f"Error using specialized loader for {module_id}: {e}")
                # Fall back to standard loading
    
    # Standard loading path
    try:
        # Get module path
        class_path = module_info.get('class_path')
        if not class_path:
            logger.error(f"Module {module_id} has no class_path defined")
            return None
        
        # Split into module and class parts
        last_dot = class_path.rfind('.')
        if last_dot == -1:
            logger.error(f"Invalid class path format: {class_path}")
            return None
            
        module_path = class_path[:last_dot]
        class_name = class_path[last_dot + 1:]
        
        # Import the module
        module = importlib.import_module(module_path)
        
        # Get the class
        module_class = getattr(module, class_name)
        
        # Verify it's a TrainingModule subclass
        if not issubclass(module_class, TrainingModule):
            logger.error(f"Class {class_name} is not a TrainingModule subclass")
            return None
        
        # Cache the class
        _module_class_cache[module_id] = module_class
        
        return module_class
        
    except ImportError as e:
        logger.error(f"Error importing module {module_path}: {e}")
        return None
    except AttributeError as e:
        logger.error(f"Error finding class {class_name} in {module_path}: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error loading module class for {module_id}: {e}")
        return None


def create_module_instance(module_id: str, **kwargs) -> Optional[TrainingModule]:
    """Create an instance of a module.
    
    This function creates a new instance of the specified module.
    
    Args:
        module_id: Module identifier
        **kwargs: Additional parameters to pass to the module constructor
        
    Returns:
        Module instance or None if not found
    """
    # Get module info
    module_info = get_module_info(module_id)
    if not module_info:
        logger.error(f"Module {module_id} not found")
        return None
    
    # Check if this module has a specialized loader
    module_type = module_info.get('module_type')
    if module_type in _module_type_loaders:
        logger.debug(f"Using specialized loader to create module '{module_id}'")
        loader = _module_type_loaders[module_type]
        
        # Try to create the instance through the loader
        if hasattr(loader, 'load_module'):
            try:
                module_instance = loader.load_module(module_id, **kwargs)
                if module_instance:
                    logger.info(f"Created module instance for {module_id} using specialized loader")
                    return module_instance
            except Exception as e:
                logger.error(f"Error using specialized loader for {module_id}: {e}")
                # Fall back to standard loading
    
    # Standard loading path
    try:
        # Get the module class
        module_class = get_module_class(module_id)
        if not module_class:
            return None
        
        # Create an instance
        module_instance = module_class(**kwargs)
        
        logger.info(f"Created module instance for {module_id}")
        return module_instance
        
    except Exception as e:
        logger.error(f"Error creating module instance for {module_id}: {e}")
        return None


def get_available_modules() -> List[Dict[str, Any]]:
    """Get a list of available modules.
    
    Returns:
        List of module information dictionaries
    """
    modules = AVAILABLE_MODULES.copy()
    
    # Add modules from specialized loaders
    for module_type, loader in _module_type_loaders.items():
        if hasattr(loader, 'list_modules'):
            specialized_modules = loader.list_modules()
            for module in specialized_modules:
                # Add module type to identify the source
                module['module_type'] = module_type
                modules.append(module)
    
    return modules

def discover_modules_from_directory() -> List[Dict[str, Any]]:
    """Discover training modules from the modules directory.
    
    This function is for development use to automatically find new modules.
    
    Returns:
        List of discovered module information dictionaries
    """
    discovered_modules = []
    modules_path = Path(__file__).parent / 'modules'
    
    # Skip if modules directory doesn't exist
    if not modules_path.exists() or not modules_path.is_dir():
        return discovered_modules
    
    # Look for Python files that might contain modules
    for file_path in modules_path.glob('*.py'):
        if file_path.name.startswith('_'):
            continue
            
        try:
            # Import the module
            module_name = file_path.stem
            spec = importlib.util.spec_from_file_location(module_name, file_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Look for TrainingModule subclasses
            for name, obj in inspect.getmembers(module):
                if (inspect.isclass(obj) and issubclass(obj, TrainingModule) 
                    and obj is not TrainingModule):
                    
                    # Generate module info
                    module_id = module_name.lower()
                    module_info = {
                        'id': module_id,
                        'name': getattr(obj, 'name', name),
                        'description': getattr(obj, 'description', ''),
                        'class_path': f'MetaMindIQTrain.modules.{module_name}.{name}'
                    }
                    discovered_modules.append(module_info)
                    logger.info(f"Discovered module: {module_info['name']}")
        except Exception as e:
            logger.warning(f"Error discovering module in {file_path}: {e}")
    
    return discovered_modules 