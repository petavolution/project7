"""
Orchestration Module

This module provides a central orchestration layer for managing the execution flow 
between training modules, the server, and client communication. It ensures efficient 
state management, optimized data transfer, and proper component lifecycle.
"""

import time
import logging
import json
import threading
import queue
from typing import Dict, Any, List, Optional, Callable, Set, Tuple
from functools import lru_cache

from .training_module import TrainingModule
from .config import MetaMindConfig, default_config
from .message_bus import message_bus, EventTypes

# Setup logging
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class SessionOrchestrator:
    """
    Orchestrates the execution flow for a single training session.
    
    This class manages the interaction between a training module, the server,
    and connected clients. It handles state synchronization, input processing,
    and efficient message distribution.
    """
    
    def __init__(self, 
                 session_id: str, 
                 module: TrainingModule, 
                 user_id: str,
                 config: Optional[MetaMindConfig] = None):
        """Initialize a session orchestrator.
        
        Args:
            session_id: Unique identifier for the session
            module: Training module instance
            user_id: User identifier
            config: Configuration settings (uses default if not provided)
        """
        self.session_id = session_id
        self.module = module
        self.user_id = user_id
        self.config = config or default_config
        self.clients: Set[str] = set()
        self.last_active = time.time()
        self.state_cache: Dict[int, Dict[str, Any]] = {}
        self.delta_cache: Dict[int, Dict[str, Any]] = {}
        self.session_lock = threading.RLock()
        self.input_queue = queue.Queue()
        self.is_processing = False
        self.processor_thread = None
        self.metrics = {
            "round_count": 0,
            "input_count": 0,
            "client_count": 0,
            "avg_processing_time": 0.0,
            "last_state_version": 0,
            "state_size_bytes": 0
        }
        
        # Publish session creation event
        message_bus.publish(
            EventTypes.SESSION_CREATED,
            {
                "session_id": session_id,
                "user_id": user_id,
                "module_id": module.module_name
            }
        )
    
    def add_client(self, client_id: str) -> Dict[str, Any]:
        """Add a client to the session.
        
        Args:
            client_id: Client identifier
            
        Returns:
            Current module state
        """
        with self.session_lock:
            self.clients.add(client_id)
            self.last_active = time.time()
            self.metrics["client_count"] = len(self.clients)
            
            # Get current state for the new client
            state = self.get_full_state()
            
            # Publish client joined event
            message_bus.publish(
                EventTypes.CLIENT_JOINED,
                {
                    "session_id": self.session_id,
                    "client_id": client_id,
                    "total_clients": len(self.clients)
                }
            )
            
            return state
    
    def remove_client(self, client_id: str) -> bool:
        """Remove a client from the session.
        
        Args:
            client_id: Client identifier
            
        Returns:
            True if successful, False if client not found
        """
        with self.session_lock:
            if client_id in self.clients:
                self.clients.remove(client_id)
                self.last_active = time.time()
                self.metrics["client_count"] = len(self.clients)
                
                # Publish client left event
                message_bus.publish(
                    EventTypes.CLIENT_LEFT,
                    {
                        "session_id": self.session_id,
                        "client_id": client_id,
                        "total_clients": len(self.clients)
                    }
                )
                
                return True
            return False
    
    def get_full_state(self) -> Dict[str, Any]:
        """Get the full state of the module.
        
        Returns:
            Complete module state
        """
        with self.session_lock:
            # Check if we have the current version cached
            version = self.module.state_version
            if version in self.state_cache:
                return self.state_cache[version]
            
            # Get fresh state
            state = self.module.get_state()
            
            # Cache the state
            self.state_cache[version] = state
            
            # Calculate approximate state size
            state_json = json.dumps(state)
            self.metrics["state_size_bytes"] = len(state_json)
            
            # Update metrics
            self.metrics["last_state_version"] = version
            
            return state
    
    def get_state_delta(self) -> Dict[str, Any]:
        """Get only state changes since the last update.
        
        Returns:
            Delta state with only changed values
        """
        with self.session_lock:
            # Check if we have the current version cached
            version = self.module.state_version
            if version in self.delta_cache:
                return self.delta_cache[version]
            
            # Get fresh delta
            delta = self.module.get_state_delta()
            
            # Cache the delta
            self.delta_cache[version] = delta
            
            return delta
    
    def execute_round(self) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """Execute a training round.
        
        Returns:
            Tuple of (full state, delta state)
        """
        with self.session_lock:
            start_time = time.time()
            
            # Publish round started event
            message_bus.publish(
                EventTypes.ROUND_STARTED,
                {
                    "session_id": self.session_id,
                    "round": self.module.round + 1,
                    "timestamp": start_time
                }
            )
            
            # Execute the round
            self.module.do_round()
            
            # Measure execution time
            execution_time = time.time() - start_time
            self.metrics["avg_processing_time"] = (
                0.9 * self.metrics["avg_processing_time"] + 
                0.1 * execution_time
            )
            
            # Increment metrics
            self.metrics["round_count"] += 1
            self.last_active = time.time()
            
            # Clear caches for old versions
            self._cleanup_caches()
            
            # Get updated state
            full_state = self.get_full_state()
            delta_state = self.get_state_delta()
            
            # Publish state changed event
            message_bus.publish(
                EventTypes.STATE_CHANGED,
                {
                    "session_id": self.session_id,
                    "state_version": self.module.state_version,
                    "changes": list(delta_state.keys())
                }
            )
            
            # Publish round completed event
            message_bus.publish(
                EventTypes.ROUND_COMPLETED,
                {
                    "session_id": self.session_id,
                    "round": self.module.round,
                    "execution_time": execution_time,
                    "timestamp": time.time()
                }
            )
            
            return full_state, delta_state
    
    def process_input(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process user input.
        
        This method can be called directly for synchronous processing or 
        queue_input can be used for asynchronous processing.
        
        Args:
            input_data: User input data
            
        Returns:
            Processing result
        """
        with self.session_lock:
            start_time = time.time()
            
            # Process the input
            result = self.module.process_input(input_data)
            
            # Measure execution time
            execution_time = time.time() - start_time
            self.metrics["avg_processing_time"] = (
                0.9 * self.metrics["avg_processing_time"] + 
                0.1 * execution_time
            )
            
            # Add processing time to result
            result["processing_time"] = execution_time
            
            # Update metrics
            self.metrics["input_count"] += 1
            self.last_active = time.time()
            
            # Clear caches for old versions
            self._cleanup_caches()
            
            # Publish state changed event if state changed
            if self.module.state_version > self.metrics["last_state_version"]:
                delta_state = self.get_state_delta()
                message_bus.publish(
                    EventTypes.STATE_CHANGED,
                    {
                        "session_id": self.session_id,
                        "state_version": self.module.state_version,
                        "changes": list(delta_state.keys())
                    }
                )
            
            # Publish input processed event
            message_bus.publish(
                EventTypes.INPUT_PROCESSED,
                {
                    "session_id": self.session_id,
                    "input_type": input_data.get("type", "unknown"),
                    "result": result,
                    "execution_time": execution_time
                }
            )
            
            return result
    
    def queue_input(self, input_data: Dict[str, Any]) -> None:
        """Queue user input for asynchronous processing.
        
        Args:
            input_data: User input data
        """
        self.input_queue.put(input_data)
        
        # Ensure processor is running
        self._ensure_processor_running()
    
    def _ensure_processor_running(self) -> None:
        """Ensure the input processor thread is running."""
        if self.processor_thread is None or not self.processor_thread.is_alive():
            self.is_processing = True
            self.processor_thread = threading.Thread(
                target=self._process_input_queue,
                daemon=True
            )
            self.processor_thread.start()
    
    def _process_input_queue(self) -> None:
        """Process queued inputs in a separate thread."""
        logger.info(f"Starting input processor for session {self.session_id}")
        
        while self.is_processing:
            try:
                # Get next input with timeout
                try:
                    input_data = self.input_queue.get(timeout=1.0)
                except queue.Empty:
                    # No input waiting, check if we should continue
                    if self.input_queue.empty() and time.time() - self.last_active > 5:
                        # Inactive for too long, stop processing
                        self.is_processing = False
                        break
                    continue
                
                # Process the input
                self.process_input(input_data)
                
                # Mark as done
                self.input_queue.task_done()
                
            except Exception as e:
                error_data = {
                    "session_id": self.session_id,
                    "error": str(e),
                    "component": "session_orchestrator",
                    "function": "_process_input_queue"
                }
                message_bus.publish(EventTypes.ERROR_OCCURRED, error_data)
                logger.error(f"Error processing input: {str(e)}")
                time.sleep(0.1)
    
    def _cleanup_caches(self) -> None:
        """Clean up old cached states and deltas."""
        # Keep only the latest state and delta
        current_version = self.module.state_version
        
        # Remove all except current version
        for version in list(self.state_cache.keys()):
            if version != current_version:
                del self.state_cache[version]
                
        for version in list(self.delta_cache.keys()):
            if version != current_version:
                del self.delta_cache[version]
    
    @property
    def is_active(self) -> bool:
        """Check if the session is still active.
        
        Returns:
            True if active, False otherwise
        """
        # Active if it has clients or was recently active
        return len(self.clients) > 0 or (time.time() - self.last_active < 
                                         self.config.server.session_timeout)
    
    def get_session_info(self) -> Dict[str, Any]:
        """Get session information.
        
        Returns:
            Dictionary with session information
        """
        return {
            "session_id": self.session_id,
            "user_id": self.user_id,
            "module_id": self.module.module_name,
            "client_count": len(self.clients),
            "active": self.is_active,
            "last_active": self.last_active,
            "metrics": {
                "round_count": self.metrics["round_count"],
                "input_count": self.metrics["input_count"],
                "avg_processing_time_ms": self.metrics["avg_processing_time"] * 1000,
                "state_version": self.metrics["last_state_version"],
                "state_size_bytes": self.metrics["state_size_bytes"]
            }
        }
    
    def shutdown(self) -> None:
        """Shutdown the orchestrator and release resources."""
        # Publish session ended event
        message_bus.publish(
            EventTypes.SESSION_ENDED,
            {
                "session_id": self.session_id,
                "user_id": self.user_id,
                "metrics": {
                    "round_count": self.metrics["round_count"],
                    "input_count": self.metrics["input_count"],
                    "final_state_version": self.metrics["last_state_version"]
                }
            }
        )
        
        self.is_processing = False
        
        # Wait for processor to finish (with timeout)
        if self.processor_thread and self.processor_thread.is_alive():
            self.processor_thread.join(timeout=2.0)
        
        # Clear collections
        with self.session_lock:
            self.clients.clear()
            self.state_cache.clear()
            self.delta_cache.clear()
            
            # Try to clear the queue
            while not self.input_queue.empty():
                try:
                    self.input_queue.get_nowait()
                    self.input_queue.task_done()
                except queue.Empty:
                    break


class OrchestrationManager:
    """
    Manages multiple session orchestrators and provides central coordination.
    
    This class is responsible for creating, tracking, and cleaning up session
    orchestrators. It also provides methods for broadcasting messages to
    multiple sessions and enforcing resource limits.
    """
    
    def __init__(self, config: Optional[MetaMindConfig] = None):
        """Initialize the orchestration manager.
        
        Args:
            config: Configuration settings (uses default if not provided)
        """
        self.config = config or default_config
        self.sessions: Dict[str, SessionOrchestrator] = {}
        self.manager_lock = threading.RLock()
        self.client_to_session: Dict[str, str] = {}
        self.cleanup_thread = None
        self.cleanup_active = False
        self.metrics = {
            "total_sessions": 0,
            "active_sessions": 0,
            "total_clients": 0,
            "peak_sessions": 0
        }
        
        # Start cleanup thread
        self._start_cleanup_thread()
        
        # Start message bus
        message_bus.start()
        
        # Subscribe to error events
        message_bus.subscribe(EventTypes.ERROR_OCCURRED, self._handle_error)
    
    def create_session(self, 
                      session_id: str, 
                      module: TrainingModule, 
                      user_id: str) -> SessionOrchestrator:
        """Create a new session orchestrator.
        
        Args:
            session_id: Unique identifier for the session
            module: Training module instance
            user_id: User identifier
            
        Returns:
            New session orchestrator
        """
        with self.manager_lock:
            # Create orchestrator
            orchestrator = SessionOrchestrator(
                session_id=session_id,
                module=module,
                user_id=user_id,
                config=self.config
            )
            
            # Store in sessions dictionary
            self.sessions[session_id] = orchestrator
            
            # Update metrics
            self.metrics["total_sessions"] += 1
            self.metrics["active_sessions"] = len(self.sessions)
            if self.metrics["active_sessions"] > self.metrics["peak_sessions"]:
                self.metrics["peak_sessions"] = self.metrics["active_sessions"]
            
            return orchestrator
    
    def get_session(self, session_id: str) -> Optional[SessionOrchestrator]:
        """Get a session orchestrator.
        
        Args:
            session_id: Unique identifier for the session
            
        Returns:
            Session orchestrator or None if not found
        """
        with self.manager_lock:
            return self.sessions.get(session_id)
    
    def add_client_to_session(self, 
                             session_id: str, 
                             client_id: str) -> Dict[str, Any]:
        """Add a client to a session.
        
        Args:
            session_id: Unique identifier for the session
            client_id: Client identifier
            
        Returns:
            Current module state
            
        Raises:
            KeyError: If session not found
        """
        with self.manager_lock:
            # Get the orchestrator
            orchestrator = self.sessions.get(session_id)
            if not orchestrator:
                raise KeyError(f"Session {session_id} not found")
            
            # Register client mapping for lookup
            self.client_to_session[client_id] = session_id
            
            # Add client to session
            state = orchestrator.add_client(client_id)
            
            # Update metrics
            self.metrics["total_clients"] += 1
            
            # Publish session joined event
            message_bus.publish(
                EventTypes.SESSION_JOINED,
                {
                    "session_id": session_id,
                    "client_id": client_id,
                    "user_id": orchestrator.user_id,
                    "module_id": orchestrator.module.module_name
                }
            )
            
            return state
    
    def remove_client(self, client_id: str) -> bool:
        """Remove a client from its session.
        
        Args:
            client_id: Client identifier
            
        Returns:
            True if successful, False otherwise
        """
        with self.manager_lock:
            # Get session ID for this client
            session_id = self.client_to_session.get(client_id)
            if not session_id:
                return False
            
            # Get the orchestrator
            orchestrator = self.sessions.get(session_id)
            if not orchestrator:
                # Clean up mapping
                del self.client_to_session[client_id]
                return False
            
            # Remove client from session
            result = orchestrator.remove_client(client_id)
            
            # Clean up mapping
            del self.client_to_session[client_id]
            
            return result
    
    def get_session_for_client(self, client_id: str) -> Optional[SessionOrchestrator]:
        """Get the session orchestrator for a client.
        
        Args:
            client_id: Client identifier
            
        Returns:
            Session orchestrator or None if not found
        """
        with self.manager_lock:
            session_id = self.client_to_session.get(client_id)
            if session_id:
                return self.sessions.get(session_id)
            return None
    
    def cleanup_sessions(self) -> int:
        """Clean up inactive sessions.
        
        Returns:
            Number of sessions removed
        """
        with self.manager_lock:
            sessions_to_remove = []
            
            # Identify inactive sessions
            for session_id, orchestrator in self.sessions.items():
                if not orchestrator.is_active:
                    sessions_to_remove.append(session_id)
            
            # Remove inactive sessions
            for session_id in sessions_to_remove:
                orchestrator = self.sessions[session_id]
                
                # Shutdown orchestrator
                orchestrator.shutdown()
                
                # Remove from sessions dictionary
                del self.sessions[session_id]
                
                logger.info(f"Removed inactive session: {session_id}")
            
            # Update metrics
            self.metrics["active_sessions"] = len(self.sessions)
            
            return len(sessions_to_remove)
    
    def _handle_error(self, error_data: Dict[str, Any]) -> None:
        """Handle error events from the message bus.
        
        Args:
            error_data: Error information
        """
        # Log the error
        component = error_data.get("component", "unknown")
        function = error_data.get("function", "unknown")
        error_msg = error_data.get("error", "Unknown error")
        session_id = error_data.get("session_id")
        
        if session_id:
            logger.error(f"Error in {component}.{function} for session {session_id}: {error_msg}")
        else:
            logger.error(f"Error in {component}.{function}: {error_msg}")
    
    def _start_cleanup_thread(self) -> None:
        """Start the cleanup thread."""
        self.cleanup_active = True
        self.cleanup_thread = threading.Thread(
            target=self._cleanup_thread_function,
            daemon=True
        )
        self.cleanup_thread.start()
    
    def _cleanup_thread_function(self) -> None:
        """Periodically clean up inactive sessions."""
        logger.info("Starting session cleanup thread")
        
        while self.cleanup_active:
            try:
                # Sleep for the configured interval
                time.sleep(self.config.server.cleanup_interval)
                
                # Clean up inactive sessions
                removed_count = self.cleanup_sessions()
                if removed_count > 0:
                    logger.info(f"Cleaned up {removed_count} inactive sessions")
                
            except Exception as e:
                error_data = {
                    "error": str(e),
                    "component": "orchestration_manager",
                    "function": "_cleanup_thread_function"
                }
                message_bus.publish(EventTypes.ERROR_OCCURRED, error_data)
                logger.error(f"Error in cleanup thread: {str(e)}")
                time.sleep(10)  # Wait a bit longer on error
    
    def shutdown(self) -> None:
        """Shutdown the orchestration manager."""
        logger.info("Shutting down orchestration manager")
        
        # Stop cleanup thread
        self.cleanup_active = False
        if self.cleanup_thread and self.cleanup_thread.is_alive():
            self.cleanup_thread.join(timeout=2.0)
        
        # Shutdown all sessions
        with self.manager_lock:
            for session_id, orchestrator in list(self.sessions.items()):
                try:
                    orchestrator.shutdown()
                except Exception as e:
                    logger.error(f"Error shutting down session {session_id}: {str(e)}")
            
            # Clear collections
            self.sessions.clear()
            self.client_to_session.clear()
            
        # Stop message bus
        message_bus.stop()
    
    def get_manager_stats(self) -> Dict[str, Any]:
        """Get statistics about the orchestration manager.
        
        Returns:
            Dictionary with statistics
        """
        with self.manager_lock:
            stats = {
                "active_sessions": len(self.sessions),
                "connected_clients": len(self.client_to_session),
                "total_sessions_created": self.metrics["total_sessions"],
                "total_clients_connected": self.metrics["total_clients"],
                "peak_concurrent_sessions": self.metrics["peak_sessions"]
            }
            
            # Add message bus stats
            message_bus_stats = message_bus.get_stats()
            stats["message_bus"] = message_bus_stats
            
            return stats


# Global instance of orchestration manager
orchestration_manager = OrchestrationManager() 