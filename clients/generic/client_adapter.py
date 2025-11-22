"""
Client Adapter for MetaMindIQTrain

This module provides a clean API for client applications (like the PyGame client)
to interact with the MetaMindIQTrain server. It handles WebSocket communication
and state management.
"""

import logging
import time
from typing import Dict, Any, Callable, Optional
from enum import Enum, auto

# Import socketio client
import socketio

# Create logger
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ConnectionState(Enum):
    """Connection state enum."""
    DISCONNECTED = auto()
    CONNECTING = auto()
    CONNECTED = auto()
    ERROR = auto()

class ClientAdapter:
    """
    Adapter for client applications to interact with the MetaMindIQTrain server.
    
    This class handles WebSocket communication and state management.
    It provides a clean API for client applications to use.
    """
    
    def __init__(self, server_url: str, 
                 reconnect_attempts: int = 3,
                 reconnect_delay: float = 1.0):
        """Initialize the client adapter.
        
        Args:
            server_url: Server URL
            reconnect_attempts: Maximum number of reconnection attempts
            reconnect_delay: Delay between reconnection attempts in seconds
        """
        self._server_url = server_url
        self._reconnect_attempts = reconnect_attempts
        self._reconnect_delay = reconnect_delay
        
        # Connection state
        self._connection_state = ConnectionState.DISCONNECTED
        
        # Current state
        self._current_state = {}
        
        # Session information
        self._session_id = None
        self._module_id = None
        self._user_id = None
        
        # Socket.IO client
        self._sio = socketio.Client()
        
        # Event handlers
        self._event_handlers = {}
        
        # Set up event handlers
        self._setup_event_handlers()
        
        logger.info(f"Client adapter initialized with server URL: {server_url}")
    
    def _setup_event_handlers(self):
        """Set up Socket.IO event handlers."""
        @self._sio.event
        def connect():
            """Handle Socket.IO connection event."""
            logger.info("Connected to server")
            self._connection_state = ConnectionState.CONNECTED
            self._trigger_event('connect', {})
        
        @self._sio.event
        def disconnect():
            """Handle Socket.IO disconnection event."""
            logger.info("Disconnected from server")
            self._connection_state = ConnectionState.DISCONNECTED
            self._trigger_event('disconnect', {})
        
        @self._sio.event
        def connect_error(data):
            """Handle Socket.IO connection error event."""
            logger.error(f"Connection error: {data}")
            self._connection_state = ConnectionState.ERROR
            self._trigger_event('error', {'message': str(data)})
        
        @self._sio.event
        def session_joined(data):
            """Handle session joined event."""
            logger.info(f"Joined session: {data.get('session_id')}")
            self._session_id = data.get('session_id')
            self._module_id = data.get('module_id')
            self._user_id = data.get('user_id')
            
            # Update state
            if 'state' in data:
                self._current_state = data['state']
            
            self._trigger_event('session_joined', data)
        
        @self._sio.event
        def session_ended(data):
            """Handle session ended event."""
            logger.info(f"Session ended: {data.get('session_id')}")
            self._session_id = None
            self._module_id = None
            self._current_state = {}
            self._trigger_event('session_ended', data)
        
        @self._sio.event
        def state_update(data):
            """Handle state update event."""
            if 'state' in data:
                self._current_state = data['state']
                self._trigger_event('state_update', data)
        
        @self._sio.event
        def input_result(data):
            """Handle input result event."""
            self._trigger_event('input_result', data)
        
        @self._sio.event
        def error(data):
            """Handle error event."""
            logger.error(f"Error from server: {data.get('message')}")
            self._trigger_event('error', data)
    
    def connect(self) -> bool:
        """Connect to the server.
        
        Returns:
            True if successful, False otherwise
        """
        if self._connection_state == ConnectionState.CONNECTED:
            logger.info("Already connected to server")
            return True
        
        self._connection_state = ConnectionState.CONNECTING
        logger.info(f"Connecting to server: {self._server_url}")
        
        try:
            self._sio.connect(
                self._server_url,
                wait_timeout=10,
                wait=True
            )
            return True
        except Exception as e:
            logger.error(f"Failed to connect to server: {str(e)}")
            self._connection_state = ConnectionState.ERROR
            self._trigger_event('error', {'message': str(e)})
            return False
    
    def disconnect(self):
        """Disconnect from the server."""
        if self._connection_state != ConnectionState.CONNECTED:
            logger.info("Not connected to server")
            return
        
        logger.info("Disconnecting from server")
        
        try:
            self._sio.disconnect()
        except Exception as e:
            logger.error(f"Error disconnecting from server: {str(e)}")
    
    def create_session(self, module_id: str, user_id: str, parameters: Dict[str, Any] = None):
        """Create a new training session.
        
        Args:
            module_id: Module identifier
            user_id: User identifier
            parameters: Module parameters
        """
        if self._connection_state != ConnectionState.CONNECTED:
            logger.error("Not connected to server")
            return False
        
        if parameters is None:
            parameters = {}
        
        logger.info(f"Creating session with module: {module_id}")
        
        self._sio.emit('create_session', {
            'module_id': module_id,
            'user_id': user_id,
            'parameters': parameters
        })
    
    def end_session(self):
        """End the current session."""
        if self._connection_state != ConnectionState.CONNECTED:
            logger.error("Not connected to server")
            return False
        
        if not self._session_id:
            logger.error("No active session")
            return False
        
        logger.info(f"Ending session: {self._session_id}")
        
        self._sio.emit('end_session')
    
    def get_available_modules(self, callback: Callable):
        """Get available modules.
        
        Args:
            callback: Callback function to handle the result
        """
        if self._connection_state != ConnectionState.CONNECTED:
            logger.error("Not connected to server")
            return
        
        logger.info("Getting available modules")
        
        self._sio.emit('get_available_modules', callback=callback)
    
    def send_input(self, input_data: Dict[str, Any]):
        """Send input to the server.
        
        Args:
            input_data: Input data
        """
        if self._connection_state != ConnectionState.CONNECTED:
            logger.error("Not connected to server")
            return
        
        if not self._session_id:
            logger.error("No active session")
            return
        
        self._sio.emit('process_input', {
            'input': input_data
        })
    
    def on(self, event: str, handler: Callable):
        """Register an event handler.
        
        Args:
            event: Event name
            handler: Event handler function
        """
        if event not in self._event_handlers:
            self._event_handlers[event] = []
        
        self._event_handlers[event].append(handler)
    
    def off(self, event: str, handler: Callable) -> bool:
        """Unregister an event handler.
        
        Args:
            event: Event name
            handler: Event handler function
            
        Returns:
            True if handler was removed, False otherwise
        """
        if event not in self._event_handlers:
            return False
        
        try:
            self._event_handlers[event].remove(handler)
            return True
        except ValueError:
            return False
    
    def get_current_state(self) -> Dict[str, Any]:
        """Get current state.
        
        Returns:
            Current state
        """
        return self._current_state
    
    def get_connection_state(self) -> ConnectionState:
        """Get connection state.
        
        Returns:
            Connection state
        """
        return self._connection_state
    
    def _trigger_event(self, event: str, data: Dict[str, Any]):
        """Trigger an event.
        
        Args:
            event: Event name
            data: Event data
        """
        if event not in self._event_handlers:
            return
        
        for handler in self._event_handlers[event]:
            try:
                handler(data)
            except Exception as e:
                logger.error(f"Error in event handler for {event}: {str(e)}")


def create_client(server_url: str = "http://localhost:5000") -> ClientAdapter:
    """Create a new client adapter.
    
    Args:
        server_url: Server URL
        
    Returns:
        Client adapter
    """
    client = ClientAdapter(server_url)
    return client 