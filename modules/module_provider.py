#!/usr/bin/env python3
"""
Module Provider - Manages and provides training modules for the MetaMind IQ Train Platform.
"""

import importlib
import os
import logging
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional

# Configure logging
logger = logging.getLogger(__name__)

# Define available modules with metadata
AVAILABLE_MODULES = {
    'memory_matrix': {
        'name': 'Memory Matrix',
        'description': 'Enhance spatial and visual memory',
        'difficulty': 'Easy',
        'category': 'Memory',
        'module_path': 'MetaMindIQTrain.modules.memory_matrix',
        'class_name': 'MemoryMatrixModule'
    },
    'music_theory': {
        'name': 'Music Theory',
        'description': 'Train your ear and musical cognition',
        'difficulty': 'Medium',
        'category': 'Music',
        'module_path': 'MetaMindIQTrain.modules.music.music_theory',
        'class_name': 'MusicTheoryModule'
    },
    'pattern_recognition': {
        'name': 'Pattern Recognition',
        'description': 'Identify complex patterns and sequences',
        'difficulty': 'Medium',
        'category': 'Cognition',
        'module_path': 'MetaMindIQTrain.modules.pattern_recognition',
        'class_name': 'PatternRecognitionModule'
    },
    'synesthetic_training': {
        'name': 'Synesthetic Training',
        'description': 'Develop cross-sensory connections',
        'difficulty': 'Hard',
        'category': 'Perception',
        'module_path': 'MetaMindIQTrain.modules.synesthetic_training',
        'class_name': 'SynestheticTrainingModule'
    },
    'psychoacoustic_wizard': {
        'name': 'Psychoacoustic Wizard',
        'description': 'Master rhythm, timing, and audio-visual integration',
        'difficulty': 'Medium',
        'category': 'Music',
        'module_path': 'MetaMindIQTrain.modules.music.psychoacoustic_wizard',
        'class_name': 'PsychoacousticWizardModule'
    }
}

class ModuleProvider:
    """
    Manages and provides training modules for the MetaMind IQ Train platform.
    
    This class is responsible for loading, instantiating, and managing training modules.
    It serves as a registry for all available modules and handles module discovery.
    """
    
    def __init__(self):
        """Initialize the ModuleProvider."""
        self.modules = {}
        self.loaded_modules = {}
        self.discover_modules()
    
    def discover_modules(self):
        """
        Discover available training modules.
        
        This method populates the modules dictionary with information about
        available training modules based on the AVAILABLE_MODULES definition.
        """
        self.modules = AVAILABLE_MODULES.copy()
        logger.info(f"Discovered {len(self.modules)} modules")
    
    def get_module_info(self, module_id: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a specific module.
        
        Args:
            module_id: The ID of the module to retrieve information for.
            
        Returns:
            Dict containing module information or None if not found.
        """
        return self.modules.get(module_id)
    
    def list_modules(self) -> List[Dict[str, Any]]:
        """
        List all available modules with their metadata.
        
        Returns:
            List of dictionaries containing module information.
        """
        return [{'id': module_id, **info} for module_id, info in self.modules.items()]
    
    def load_module(self, module_id: str) -> Any:
        """
        Load and instantiate a training module.
        
        Args:
            module_id: The ID of the module to load.
            
        Returns:
            An instance of the requested training module or None if not found.
            
        Raises:
            ImportError: If the module cannot be imported.
            AttributeError: If the specified class cannot be found in the module.
        """
        # Check if module is already loaded
        if module_id in self.loaded_modules:
            return self.loaded_modules[module_id]
        
        # Check if module exists
        if module_id not in self.modules:
            logger.error(f"Module '{module_id}' not found")
            return None
        
        module_info = self.modules[module_id]
        
        try:
            # Import the module
            module_path = module_info['module_path']
            module = importlib.import_module(module_path)
            
            # Get the module class
            class_name = module_info['class_name']
            module_class = getattr(module, class_name)
            
            # Instantiate the module
            module_instance = module_class()
            
            # Store the loaded module
            self.loaded_modules[module_id] = module_instance
            
            logger.info(f"Loaded module '{module_id}'")
            return module_instance
            
        except ImportError as e:
            logger.error(f"Error importing module '{module_id}': {e}")
            raise
        except AttributeError as e:
            logger.error(f"Error finding class '{class_name}' in module '{module_path}': {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error loading module '{module_id}': {e}")
            raise
    
    def get_modules_by_category(self, category: str) -> List[Dict[str, Any]]:
        """
        Get modules filtered by category.
        
        Args:
            category: The category to filter by.
            
        Returns:
            List of dictionaries containing module information for the specified category.
        """
        return [{'id': module_id, **info} for module_id, info in self.modules.items() 
                if info['category'] == category]
    
    def get_modules_by_difficulty(self, difficulty: str) -> List[Dict[str, Any]]:
        """
        Get modules filtered by difficulty.
        
        Args:
            difficulty: The difficulty level to filter by.
            
        Returns:
            List of dictionaries containing module information for the specified difficulty.
        """
        return [{'id': module_id, **info} for module_id, info in self.modules.items() 
                if info['difficulty'] == difficulty]

# For testing when run directly
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    # Create module provider
    provider = ModuleProvider()
    
    # List all modules
    modules = provider.list_modules()
    print(f"Available modules: {len(modules)}")
    for module in modules:
        print(f"- {module['name']} ({module['category']}): {module['description']}")
    
    # Try loading a module
    if modules:
        first_module_id = modules[0]['id']
        module = provider.load_module(first_module_id)
        if module:
            print(f"Successfully loaded module: {module.name}")

def register_module(module_class):
    """
    Register a new module dynamically.
    
    Args:
        module_class: The module class to register
    """
    if not hasattr(module_class, 'name') or not module_class.name:
        logger.error("Cannot register module without name attribute")
        return False
        
    # Generate a module_id from the name
    module_id = module_class.__name__.lower().replace('module', '')
    
    # Check if already registered
    if module_id in AVAILABLE_MODULES:
        logger.warning(f"Module '{module_id}' already registered, updating")
    
    # Get required attributes with defaults
    module_path = module_class.__module__
    name = getattr(module_class, 'name', module_class.__name__)
    description = getattr(module_class, 'description', 'No description available')
    difficulty = getattr(module_class, 'difficulty', 'Medium')
    category = getattr(module_class, 'category', 'Misc')
    
    # Register the module
    AVAILABLE_MODULES[module_id] = {
        'name': name,
        'description': description,
        'difficulty': difficulty,
        'category': category,
        'module_path': module_path,
        'class_name': module_class.__name__
    }
    
    logger.info(f"Registered module '{module_id}' from {module_path}")
    return True 