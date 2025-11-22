#!/usr/bin/env python3
"""
Check All Modules

This script verifies that all modules can be loaded with pygame.
"""

import sys
import os
from pathlib import Path

# Add the project root to the Python path
# Adjust path to work from tests directory
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

import importlib

# Add parent directory to path if needed
script_dir = Path(__file__).parent

def check_module(module_path, expected_class=None):
    """Check if a module can be loaded and optionally verify a class exists."""
    try:
        module = importlib.import_module(module_path)
        status = f"✅ Successfully imported {module_path}"
        
        if expected_class and hasattr(module, expected_class):
            status += f" (found {expected_class})"
        elif expected_class:
            status += f" BUT {expected_class} class not found ❌"
            
        return True, status
    except Exception as e:
        return False, f"❌ Error importing {module_path}: {e}"

def main():
    """Check all module components."""
    print("=" * 60)
    print("CHECKING MODULE COMPONENTS")
    print("=" * 60)
    
    # Check core functionality
    print("\n## Core Functionality ##")
    modules_to_check = [
        ("MetaMindIQTrain.module_registry", None),
        ("MetaMindIQTrain.config", None),
    ]
    
    for module_path, expected_class in modules_to_check:
        _, status = check_module(module_path, expected_class)
        print(status)
    
    # Check renderers
    print("\n## Renderers ##")
    renderer_modules = [
        ("MetaMindIQTrain.clients.pygame.renderers.base_renderer", "BaseRenderer"),
        ("MetaMindIQTrain.clients.pygame.renderers.enhanced_generic_renderer", "EnhancedGenericRenderer"),
        ("MetaMindIQTrain.clients.pygame.renderers.registry", "RendererRegistry"),
    ]
    
    for module_path, expected_class in renderer_modules:
        _, status = check_module(module_path, expected_class)
        print(status)
    
    # Make sure old renderers are completely replaced
    print("\n## Checking Legacy Renderers (Should be in legacy_backup directory) ##")
    legacy_modules = [
        ("MetaMindIQTrain.clients.pygame.renderers.legacy_backup.SymbolMemory_renderer", "MemoryRenderer"),
        ("MetaMindIQTrain.clients.pygame.renderers.legacy_backup.MorphMmatrix_renderer", "MorphMatrixRenderer"),
        ("MetaMindIQTrain.clients.pygame.renderers.legacy_backup.expand_vision_renderer", "ExpandVisionRenderer"),
    ]
    
    for module_path, expected_class in legacy_modules:
        success, status = check_module(module_path, expected_class)
        if success:
            print(f"✅ Legacy renderer {module_path} found in the correct location")
        else:
            print(f"❓ Legacy renderer not found: {module_path}")
            
    # Make sure no module-specific renderers are in the main path
    print("\n## Checking No Module-Specific Renderers in Main Path ##")
    old_path_modules = [
        "MetaMindIQTrain.clients.pygame.renderers.SymbolMemory_renderer",
        "MetaMindIQTrain.clients.pygame.renderers.MorphMmatrix_renderer", 
        "MetaMindIQTrain.clients.pygame.renderers.expand_vision_renderer",
    ]
    
    for module_path in old_path_modules:
        success, _ = check_module(module_path)
        if not success:
            print(f"✅ Correctly removed: {module_path}")
        else:
            print(f"❌ Should be removed or moved to legacy: {module_path}")
    
    # Check actual training modules
    print("\n## Training Modules ##")
    training_modules = [
        "symbol_memory",
        "morph_matrix", 
        "expand_vision"
    ]
    
    for module_id in training_modules:
        try:
            # Import the module registry
            from MetaMindIQTrain.module_registry import create_module_instance
            
            # Try to create a module instance
            import uuid
            module = create_module_instance(module_id)
            print(f"✅ Successfully created {module_id} module (Level {module.level})")
            
            # Check some basic module properties
            print(f"   - Name: {module.name}")
            print(f"   - Description: {module.description}")
            print(f"   - Has start_challenge: {hasattr(module, 'start_challenge')}")
            print(f"   - Has get_state: {hasattr(module, 'get_state')}")
            
        except Exception as e:
            print(f"❌ Error creating {module_id} module: {e}")
    
    print("\n" + "=" * 60)
    print("CHECK COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    main() 