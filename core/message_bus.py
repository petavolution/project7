"""
Message Bus Module

This module implements a message bus system to facilitate communication between
the server, orchestration layer, and modules. It provides a publish-subscribe
pattern for event handling and component decoupling.
"""

import time
import logging
import threading
import queue
from typing import Dict, Any, List, Callable, Set, Optional, Tuple

# Setup logging
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class MessageBus:
    """
    Implements a message bus for event-based communication.
    
    The message bus allows components to publish events and subscribe to them,
    decoupling event producers from consumers.
    """
    
    def __init__(self):
        """Initialize the message bus."""
        self.subscribers: Dict[str, List[Tuple[Callable, Dict[str, Any]]]] = {}
        self.message_queue = queue.Queue()
        self.is_processing = False
        self.processor_thread = None
        self.bus_lock = threading.RLock()
        self.metrics = {
            "messages_published": 0,
            "messages_processed": 0,
            "subscribers_count": 0,
            "last_message_time": 0
        }
    
    def start(self) -> None:
        """Start the message processor."""
        with self.bus_lock:
            if not self.is_processing:
                self.is_processing = True
                self.processor_thread = threading.Thread(
                    target=self._process_messages,
                    daemon=True
                )
                self.processor_thread.start()
                logger.info("Message bus started")
    
    def stop(self) -> None:
        """Stop the message processor."""
        with self.bus_lock:
            if self.is_processing:
                self.is_processing = False
                if self.processor_thread and self.processor_thread.is_alive():
                    self.processor_thread.join(timeout=2.0)
                logger.info("Message bus stopped")
    
    def subscribe(self, 
                 event_type: str, 
                 callback: Callable, 
                 filters: Optional[Dict[str, Any]] = None) -> None:
        """Subscribe to an event type.
        
        Args:
            event_type: Type of event to subscribe to
            callback: Function to call when event occurs
            filters: Optional filters to apply to events
        """
        with self.bus_lock:
            if event_type not in self.subscribers:
                self.subscribers[event_type] = []
            
            # Create subscriber entry with callback and filters
            subscriber = (callback, filters or {})
            self.subscribers[event_type].append(subscriber)
            
            # Update metrics
            self.metrics["subscribers_count"] = sum(
                len(subs) for subs in self.subscribers.values()
            )
            
            logger.debug(f"Subscribed to {event_type} events")
    
    def unsubscribe(self, 
                   event_type: str, 
                   callback: Callable) -> bool:
        """Unsubscribe from an event type.
        
        Args:
            event_type: Type of event to unsubscribe from
            callback: Callback function to remove
            
        Returns:
            True if successful, False otherwise
        """
        with self.bus_lock:
            if event_type not in self.subscribers:
                return False
            
            # Find and remove the subscriber
            subscribers = self.subscribers[event_type]
            for i, (cb, _) in enumerate(subscribers):
                if cb == callback:
                    subscribers.pop(i)
                    
                    # Update metrics
                    self.metrics["subscribers_count"] = sum(
                        len(subs) for subs in self.subscribers.values()
                    )
                    
                    # Clean up empty subscriber lists
                    if not subscribers:
                        del self.subscribers[event_type]
                    
                    logger.debug(f"Unsubscribed from {event_type} events")
                    return True
            
            return False
    
    def publish(self, 
               event_type: str, 
               event_data: Dict[str, Any], 
               immediate: bool = False) -> None:
        """Publish an event.
        
        Args:
            event_type: Type of event to publish
            event_data: Event data to distribute
            immediate: If True, process immediately; otherwise, queue for processing
        """
        # Add timestamp and event type
        message = {
            "event_type": event_type,
            "timestamp": time.time(),
            "data": event_data
        }
        
        # Ensure the bus is running
        if not self.is_processing and not immediate:
            self.start()
        
        # Update metrics
        self.metrics["messages_published"] += 1
        self.metrics["last_message_time"] = message["timestamp"]
        
        if immediate:
            # Process immediately if requested
            self._dispatch_message(message)
        else:
            # Queue for async processing
            self.message_queue.put(message)
    
    def _process_messages(self) -> None:
        """Process queued messages in a background thread."""
        logger.info("Starting message processor thread")
        
        while self.is_processing:
            try:
                # Wait for a message with timeout
                try:
                    message = self.message_queue.get(timeout=1.0)
                except queue.Empty:
                    # No messages, check if we should continue
                    continue
                
                # Process the message
                self._dispatch_message(message)
                
                # Mark as done
                self.message_queue.task_done()
                
                # Update metrics
                self.metrics["messages_processed"] += 1
                
            except Exception as e:
                logger.error(f"Error processing message: {str(e)}")
                time.sleep(0.1)
    
    def _dispatch_message(self, message: Dict[str, Any]) -> None:
        """Dispatch a message to subscribers.
        
        Args:
            message: Message to dispatch
        """
        event_type = message["event_type"]
        
        # Make a copy of subscribers to avoid modification during iteration
        with self.bus_lock:
            if event_type not in self.subscribers:
                return
            
            subscribers = list(self.subscribers[event_type])
        
        # Dispatch to each subscriber
        for callback, filters in subscribers:
            try:
                # Check if message matches filters
                if self._matches_filters(message["data"], filters):
                    callback(message["data"])
            except Exception as e:
                logger.error(f"Error dispatching message to subscriber: {str(e)}")
    
    def _matches_filters(self, 
                        data: Dict[str, Any], 
                        filters: Dict[str, Any]) -> bool:
        """Check if data matches filters.
        
        Args:
            data: Data to check
            filters: Filters to apply
            
        Returns:
            True if data matches filters or filters is empty, False otherwise
        """
        if not filters:
            return True
        
        for key, value in filters.items():
            # Handle nested keys with dot notation
            if "." in key:
                parts = key.split(".")
                current = data
                for part in parts:
                    if not isinstance(current, dict) or part not in current:
                        return False
                    current = current[part]
                
                if current != value:
                    return False
            
            # Direct key match
            elif key not in data or data[key] != value:
                return False
        
        return True
    
    def get_stats(self) -> Dict[str, Any]:
        """Get message bus statistics.
        
        Returns:
            Dictionary with statistics
        """
        with self.bus_lock:
            return {
                "is_active": self.is_processing,
                "subscribers_count": self.metrics["subscribers_count"],
                "messages_published": self.metrics["messages_published"],
                "messages_processed": self.metrics["messages_processed"],
                "pending_messages": self.message_queue.qsize(),
                "event_types": list(self.subscribers.keys())
            }


# Common event types
class EventTypes:
    """Common event types for the message bus."""
    
    # Session events
    SESSION_CREATED = "session.created"
    SESSION_JOINED = "session.joined"
    SESSION_ENDED = "session.ended"
    CLIENT_JOINED = "client.joined"
    CLIENT_LEFT = "client.left"
    
    # Training module events
    ROUND_STARTED = "round.started"
    ROUND_COMPLETED = "round.completed"
    INPUT_PROCESSED = "input.processed"
    STATE_CHANGED = "state.changed"
    MODULE_INITIALIZED = "module.initialized"
    DIFFICULTY_CHANGED = "difficulty.changed"
    
    # Server events
    SERVER_STARTED = "server.started"
    SERVER_STOPPING = "server.stopping"
    ERROR_OCCURRED = "error.occurred"


# Global instance for use throughout the application
message_bus = MessageBus() 