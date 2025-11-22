"""Module Registry for MetaMindIQTrain

Manages available modules for the application.
"""

class ModuleRegistry:
    """Registry for modules that can be loaded in the application."""
    
    def __init__(self):
        """Initialize the module registry."""
        self.modules = {}
        
    def register_module(self, name, module_class):
        """Register a module.
        
        Args:
            name: Module name
            module_class: Module class
        """
        self.modules[name] = module_class
        
    def get_module(self, name):
        """Get a module by name.
        
        Args:
            name: Module name
            
        Returns:
            Module class or None if not found
        """
        return self.modules.get(name)
        
    def get_module_names(self):
        """Get all registered module names.
        
        Returns:
            List of module names
        """
        return list(self.modules.keys())
