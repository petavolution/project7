#!/usr/bin/env python3
"""
Event Bus

This module provides a central event system for decoupled communication
between components in the MetaMindIQTrain platform.
"""

import logging
from typing import Dict, List, Any, Callable, Optional
from collections import defaultdict

logger = logging.getLogger(__name__)

EventCallback = Callable[[Dict[str, Any]], None]

class EventBus:
    """Central event system for decoupled communication"""
    
    def __init__(self):
        """Initialize the event bus."""
        self.subscribers = defaultdict(list)
        logger.info("Event bus initialized")
        
    def subscribe(self, event_type: str, callback: EventCallback) -> None:
        """Subscribe to an event type.
        
        Args:
            event_type: Type of event to subscribe to
            callback: Function to call when event is published
        """
        self.subscribers[event_type].append(callback)
        logger.debug(f"Subscribed to event type: {event_type}")
        
    def unsubscribe(self, event_type: str, callback: EventCallback) -> bool:
        """Unsubscribe from an event type.
        
        Args:
            event_type: Type of event to unsubscribe from
            callback: Function to remove from subscribers
            
        Returns:
            True if successfully unsubscribed, False otherwise
        """
        if event_type in self.subscribers and callback in self.subscribers[event_type]:
            self.subscribers[event_type].remove(callback)
            logger.debug(f"Unsubscribed from event type: {event_type}")
            return True
        else:
            logger.warning(f"Attempted to unsubscribe from unknown event: {event_type}")
            return False
            
    def publish(self, event_type: str, data: Optional[Dict[str, Any]] = None) -> int:
        """Publish an event to all subscribers.
        
        Args:
            event_type: Type of event to publish
            data: Event data to pass to subscribers
            
        Returns:
            Number of subscribers that received the event
        """
        if not data:
            data = {}
            
        subscribers = self.subscribers[event_type]
        
        if subscribers:
            logger.debug(f"Publishing event {event_type} to {len(subscribers)} subscribers")
            
            for callback in subscribers:
                try:
                    callback(data)
                except Exception as e:
                    logger.error(f"Error in event handler for {event_type}: {e}")
        
        return len(subscribers)
        
    def clear_subscribers(self, event_type: Optional[str] = None) -> None:
        """Clear subscribers for a specific event type or all event types.
        
        Args:
            event_type: Event type to clear, or None to clear all
        """
        if event_type:
            self.subscribers[event_type].clear()
            logger.debug(f"Cleared subscribers for event type: {event_type}")
        else:
            self.subscribers.clear()
            logger.info("Cleared all event subscribers")
            
    def get_subscriber_count(self, event_type: Optional[str] = None) -> int:
        """Get the number of subscribers for an event type or all event types.
        
        Args:
            event_type: Event type to count, or None to count all
            
        Returns:
            Number of subscribers
        """
        if event_type:
            return len(self.subscribers[event_type])
        else:
            return sum(len(subscribers) for subscribers in self.subscribers.values()) 