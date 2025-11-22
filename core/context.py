#!/usr/bin/env python3
"""
Context System for MetaMindIQTrain

This module provides a reactive state management system that allows components
to share and react to state changes across the component hierarchy without 
requiring prop drilling or complex event systems.
"""

import logging
import uuid
import weakref
from typing import Dict, List, Any, Optional, Callable, Set, Generic, TypeVar, cast

logger = logging.getLogger(__name__)

T = TypeVar('T')  # Generic type for context values

class Context(Generic[T]):
    """A context for sharing state between components.
    
    Contexts allow components to access shared state without prop drilling.
    They provide a reactive system where components can subscribe to state changes.
    """
    
    # Registry of all active contexts
    _contexts: Dict[str, 'Context'] = {}
    
    def __init__(self, name: str, initial_value: T = None):
        """Initialize a new context.
        
        Args:
            name: Unique name for the context
            initial_value: Initial value for the context
        """
        self.name = name
        self._value = initial_value
        self._subscribers: Dict[str, weakref.ReferenceType] = {}
        self._callbacks: Dict[str, Callable[[T, T], None]] = {}
        
        # Register this context
        Context._contexts[name] = self
        
    def get(self) -> T:
        """Get the current value of the context.
        
        Returns:
            Current context value
        """
        return self._value
        
    def set(self, value: T) -> None:
        """Set the value of the context and notify subscribers.
        
        Args:
            value: New context value
        """
        if value == self._value:
            return  # No change, no notifications
            
        old_value = self._value
        self._value = value
        
        # Notify subscribers
        self._notify_subscribers(old_value, value)
        
    def _notify_subscribers(self, old_value: T, new_value: T) -> None:
        """Notify all subscribers of a value change.
        
        Args:
            old_value: Previous context value
            new_value: New context value
        """
        # Create a copy to avoid modification during iteration
        subscriber_items = list(self._subscribers.items())
        
        # Call all callbacks
        for subscriber_id, subscriber_ref in subscriber_items:
            # Get the callback
            callback = self._callbacks.get(subscriber_id)
            if not callback:
                continue
                
            # Get the subscriber object
            subscriber = subscriber_ref()
            if subscriber is None:
                # Subscriber has been garbage collected, remove it
                self._subscribers.pop(subscriber_id, None)
                self._callbacks.pop(subscriber_id, None)
                continue
                
            # Call the callback
            try:
                callback(old_value, new_value)
            except Exception as e:
                logger.error(f"Error in context callback: {e}")
                
    def subscribe(self, subscriber: Any, callback: Callable[[T, T], None]) -> str:
        """Subscribe to context changes.
        
        Args:
            subscriber: Object subscribing to changes
            callback: Function to call when the value changes, with signature (old_value, new_value)
            
        Returns:
            Subscription ID
        """
        subscriber_id = str(uuid.uuid4())
        self._subscribers[subscriber_id] = weakref.ref(subscriber)
        self._callbacks[subscriber_id] = callback
        return subscriber_id
        
    def unsubscribe(self, subscriber_id: str) -> bool:
        """Unsubscribe from context changes.
        
        Args:
            subscriber_id: Subscription ID returned from subscribe()
            
        Returns:
            True if the subscription was removed, False otherwise
        """
        if subscriber_id in self._subscribers:
            self._subscribers.pop(subscriber_id)
            self._callbacks.pop(subscriber_id, None)
            return True
        return False
        
    @staticmethod
    def get_context(name: str) -> Optional['Context']:
        """Get a context by name.
        
        Args:
            name: Context name
            
        Returns:
            Context object or None if not found
        """
        return Context._contexts.get(name)
        
    @staticmethod
    def create_context(name: str, initial_value: Any = None) -> 'Context':
        """Create or get a context by name.
        
        Args:
            name: Context name
            initial_value: Initial value for the context (only used if creating a new context)
            
        Returns:
            Context object
        """
        if name in Context._contexts:
            return Context._contexts[name]
            
        return Context(name, initial_value)

class ContextAware:
    """Mixin for classes that can subscribe to contexts.
    
    This mixin should be added to any class that needs to subscribe to contexts.
    It provides methods for subscribing and unsubscribing to contexts, and ensures
    that subscriptions are cleaned up when the object is destroyed.
    """
    
    def __init__(self):
        """Initialize the context-aware mixin."""
        self._context_subscriptions: Dict[str, Set[str]] = {}
        
    def subscribe_to_context(self, context_name: str, callback: Callable[[Any, Any], None]) -> str:
        """Subscribe to a context.
        
        Args:
            context_name: Name of the context to subscribe to
            callback: Function to call when the context value changes
            
        Returns:
            Subscription ID
        """
        context = Context.get_context(context_name)
        if not context:
            context = Context.create_context(context_name)
            
        # Subscribe to the context
        subscription_id = context.subscribe(self, callback)
        
        # Keep track of the subscription
        if context_name not in self._context_subscriptions:
            self._context_subscriptions[context_name] = set()
        self._context_subscriptions[context_name].add(subscription_id)
        
        # Immediate callback with current value
        callback(None, context.get())
        
        return subscription_id
        
    def unsubscribe_from_context(self, context_name: str, subscription_id: str) -> bool:
        """Unsubscribe from a context.
        
        Args:
            context_name: Name of the context
            subscription_id: Subscription ID returned from subscribe_to_context()
            
        Returns:
            True if the subscription was removed, False otherwise
        """
        context = Context.get_context(context_name)
        if not context:
            return False
            
        # Unsubscribe from the context
        result = context.unsubscribe(subscription_id)
        
        # Remove from subscription tracking
        if result and context_name in self._context_subscriptions:
            self._context_subscriptions[context_name].discard(subscription_id)
            if not self._context_subscriptions[context_name]:
                del self._context_subscriptions[context_name]
                
        return result
        
    def unsubscribe_from_all_contexts(self) -> None:
        """Unsubscribe from all contexts.
        
        This should be called when the object is being destroyed.
        """
        # Make a copy of the context subscriptions
        context_subscriptions = self._context_subscriptions.copy()
        
        # Unsubscribe from all contexts
        for context_name, subscription_ids in context_subscriptions.items():
            context = Context.get_context(context_name)
            if not context:
                continue
                
            for subscription_id in list(subscription_ids):
                context.unsubscribe(subscription_id)
                
        # Clear subscriptions
        self._context_subscriptions.clear()

def get_context(name: str) -> Context:
    """Get a context by name, creating it if it doesn't exist.
    
    Args:
        name: Context name
        
    Returns:
        Context object
    """
    return Context.create_context(name)

def create_context(name: str, initial_value: Any = None) -> Context:
    """Create a new context.
    
    Args:
        name: Context name
        initial_value: Initial value for the context
        
    Returns:
        Context object
    """
    return Context.create_context(name, initial_value)

def set_context_value(name: str, value: Any) -> None:
    """Set the value of a context.
    
    Args:
        name: Context name
        value: New context value
    """
    context = get_context(name)
    context.set(value)

def get_context_value(name: str) -> Any:
    """Get the value of a context.
    
    Args:
        name: Context name
        
    Returns:
        Current context value
    """
    context = get_context(name)
    return context.get() 