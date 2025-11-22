"""
Context management system for MetaMindIQTrain application.
Manages application-wide state and provides subscription mechanisms.
"""

from typing import Dict, Any, List, Callable, Optional, Set

class ContextManager:
    """Manages context data and subscriptions throughout the application."""
    
    def __init__(self):
        """Initialize the context manager."""
        self.contexts = {}
        self.subscriptions = {}
        self.components = set()
        
    def set_context(self, key: str, value: Any) -> None:
        """Set a context value.
        
        Args:
            key: Context key
            value: Context value
        """
        old_value = self.contexts.get(key)
        self.contexts[key] = value
        
        # Notify subscribers of the change
        if key in self.subscriptions:
            for callback in self.subscriptions[key]:
                try:
                    callback(value, old_value)
                except Exception as e:
                    print(f"Error in context callback for {key}: {e}")
    
    def get_context(self, key: str, default: Any = None) -> Any:
        """Get a context value.
        
        Args:
            key: Context key
            default: Default value if the key doesn't exist
            
        Returns:
            Context value or default
        """
        return self.contexts.get(key, default)
    
    def subscribe(self, key: str, callback: Callable[[Any, Any], None]) -> None:
        """Subscribe to context changes.
        
        Args:
            key: Context key to subscribe to
            callback: Callback function that takes (new_value, old_value)
        """
        if key not in self.subscriptions:
            self.subscriptions[key] = set()
        self.subscriptions[key].add(callback)
    
    def unsubscribe(self, key: str, callback: Callable[[Any, Any], None]) -> bool:
        """Unsubscribe from context changes.
        
        Args:
            key: Context key
            callback: Callback function
            
        Returns:
            True if unsubscribed successfully, False otherwise
        """
        if key in self.subscriptions and callback in self.subscriptions[key]:
            self.subscriptions[key].remove(callback)
            return True
        return False
    
    def register_component(self, component) -> None:
        """Register a component with the context manager.
        
        Args:
            component: Component to register
        """
        self.components.add(component)
    
    def unregister_component(self, component) -> None:
        """Unregister a component from the context manager.
        
        Args:
            component: Component to unregister
        """
        if component in self.components:
            self.components.remove(component)
            
    def clear(self) -> None:
        """Clear all contexts and subscriptions."""
        self.contexts.clear()
        self.subscriptions.clear()
        self.components.clear()

# Singleton instance for easy access
_context_manager_instance = None

def get_context_manager() -> ContextManager:
    """Get the singleton context manager instance.
    
    Returns:
        ContextManager instance
    """
    global _context_manager_instance
    if _context_manager_instance is None:
        _context_manager_instance = ContextManager()
    return _context_manager_instance

def set_context(key: str, value: Any) -> None:
    """Set a context value using the singleton context manager.
    
    Args:
        key: Context key
        value: Context value
    """
    get_context_manager().set_context(key, value)
    
def get_context(key: str, default: Any = None) -> Any:
    """Get a context value using the singleton context manager.
    
    Args:
        key: Context key
        default: Default value if the key doesn't exist
        
    Returns:
        Context value or default
    """
    return get_context_manager().get_context(key, default)
    
def subscribe_to_context(key: str, callback: Callable[[Any, Any], None]) -> None:
    """Subscribe to context changes using the singleton context manager.
    
    Args:
        key: Context key to subscribe to
        callback: Callback function that takes (new_value, old_value)
    """
    get_context_manager().subscribe(key, callback)
    
def unsubscribe_from_context(key: str, callback: Callable[[Any, Any], None]) -> bool:
    """Unsubscribe from context changes using the singleton context manager.
    
    Args:
        key: Context key
        callback: Callback function
        
    Returns:
        True if unsubscribed successfully, False otherwise
    """
    return get_context_manager().unsubscribe(key, callback) 