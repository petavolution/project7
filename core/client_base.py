"""
Client Base Module

This module provides the base client class that all rendering clients should extend.
It handles WebSocket communication, state management, and defines the interface
that client implementations must provide.
"""

import socketio
import time
import logging
import json
import threading
import queue
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Callable, List, Tuple
from . import MESSAGE_TYPES, PROTOCOL_VERSION, apply_delta

# Setup logging
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


class BaseClient(ABC):
    """Base class for all MetaMindIQTrain clients.
    
    This class handles WebSocket communication with the server and maintains
    the client-side state. It defines an interface that client implementations
    must provide to render the training modules.
    """
    
    def __init__(self, server_url: str = "http://localhost:5000"):
        """Initialize the client.
        
        Args:
            server_url: URL of the MetaMindIQTrain server
        """
        self.logger = logging.getLogger(f"{self.__class__.__name__}")
        self.server_url = server_url
        self.sio = socketio.Client(reconnection=True, reconnection_attempts=10, 
                                   reconnection_delay=1, reconnection_delay_max=5)
        self.state = {}
        self.session_id = None
        self.user_id = None
        self.connected = False
        self.callbacks = {}
        self.last_state_version = 0
        self.pending_state_updates = queue.Queue()
        self.message_queue = queue.Queue()
        self.outbound_queue = queue.Queue()
        self.last_server_communication = 0
        self.connection_timeout = 10  # seconds
        self.message_processor_active = False
        self.outbound_processor_active = False
        self.stats = {
            "messages_received": 0,
            "messages_sent": 0,
            "state_updates": 0,
            "state_deltas": 0,
            "last_ping": 0,
            "avg_latency": 0,
            "reconnections": 0
        }
        
        # Register socket.io event handlers
        self._register_event_handlers()
    
    def _register_event_handlers(self) -> None:
        """Register handlers for socket.io events."""
        # Basic socket.io events
        self.sio.on('connect', self._on_connect)
        self.sio.on('disconnect', self._on_disconnect)
        self.sio.on('error', self._on_error)
        self.sio.on('reconnect', self._on_reconnect)
        
        # Application-specific events
        self.sio.on('connected', self._on_connected)
        self.sio.on('session_joined', self._on_session_joined)
        self.sio.on('state_update', self._on_state_update)
        self.sio.on('state_delta', self._on_state_delta)
        self.sio.on('round_completed', self._on_round_completed)
        self.sio.on('input_processed', self._on_input_processed)
        self.sio.on('sequence', self._on_sequence)
        self.sio.on('session_ended', self._on_session_ended)
    
    def connect(self) -> bool:
        """Connect to the server.
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            self.logger.info(f"Connecting to server at {self.server_url}")
            self.sio.connect(self.server_url, transports=['websocket'])
            
            # Start message processor thread
            if not self.message_processor_active:
                self.message_processor_active = True
                threading.Thread(target=self._process_incoming_messages, 
                                daemon=True).start()
                
            # Start outbound processor thread
            if not self.outbound_processor_active:
                self.outbound_processor_active = True
                threading.Thread(target=self._process_outbound_messages,
                                daemon=True).start()
                
            # Start ping thread for connection monitoring
            threading.Thread(target=self._ping_server, daemon=True).start()
            
            return True
        except Exception as e:
            self.logger.error(f"Connection error: {str(e)}")
            return False
    
    def disconnect(self) -> None:
        """Disconnect from the server."""
        try:
            if self.connected:
                self.logger.info("Disconnecting from server")
                self.sio.disconnect()
        except Exception as e:
            self.logger.error(f"Disconnect error: {str(e)}")
    
    def join_session(self, session_id: str, user_id: str) -> None:
        """Join a training session.
        
        Args:
            session_id: ID of the session to join
            user_id: ID of the user joining
        """
        self.session_id = session_id
        self.user_id = user_id
        
        # Queue message for reliable delivery
        self._queue_outbound_message('join_session', {
            'session_id': session_id,
            'user_id': user_id,
            'client_info': {
                'type': self.__class__.__name__,
                'protocol_version': PROTOCOL_VERSION
            }
        })
    
    def end_session(self) -> None:
        """End the current training session."""
        if not self.session_id:
            self.logger.warning("Cannot end session: No active session")
            return
            
        self._queue_outbound_message('end_session', {
            'session_id': self.session_id
        })
    
    def get_state(self) -> None:
        """Request the current state from the server."""
        if not self.session_id:
            self.logger.warning("Cannot get state: No active session")
            return
            
        self._queue_outbound_message('get_state', {
            'session_id': self.session_id
        })
    
    def do_round(self) -> None:
        """Request the server to execute a training round."""
        if not self.session_id:
            self.logger.warning("Cannot do round: No active session")
            return
            
        self._queue_outbound_message('do_round', {
            'session_id': self.session_id,
            'timestamp': time.time()
        })
    
    def process_input(self, input_data: Dict[str, Any]) -> None:
        """Send user input to the server.
        
        Args:
            input_data: User input data
        """
        if not self.session_id:
            self.logger.warning("Cannot process input: No active session")
            return
            
        # Add timestamp for response time calculation
        if 'timestamp' not in input_data:
            input_data['timestamp'] = time.time()
            
        self._queue_outbound_message('process_input', {
            'session_id': self.session_id,
            'input': input_data
        })
    
    def get_sequence(self, sequence_type: str = 'default') -> None:
        """Request a sequence from the server.
        
        Args:
            sequence_type: Type of sequence to request
        """
        if not self.session_id:
            self.logger.warning("Cannot get sequence: No active session")
            return
            
        self._queue_outbound_message('get_sequence', {
            'session_id': self.session_id,
            'type': sequence_type
        })
    
    def register_callback(self, event: str, callback: Callable) -> None:
        """Register a callback for an event.
        
        Args:
            event: Event name
            callback: Callback function
        """
        self.callbacks[event] = callback
    
    def _trigger_callback(self, event: str, data: Any = None) -> None:
        """Trigger a registered callback.
        
        Args:
            event: Event name
            data: Event data
        """
        if event in self.callbacks and callable(self.callbacks[event]):
            try:
                self.callbacks[event](data)
            except Exception as e:
                self.logger.error(f"Error in {event} callback: {str(e)}")
    
    def _on_connect(self) -> None:
        """Handle connection to server."""
        self.connected = True
        self.last_server_communication = time.time()
        self.logger.info("Connected to server")
        
        # If reconnecting, rejoin the session
        if self.session_id and self.user_id:
            self.join_session(self.session_id, self.user_id)
            
        self.on_connect()
    
    def _on_disconnect(self) -> None:
        """Handle disconnection from server."""
        self.connected = False
        self.logger.warning("Disconnected from server")
        self.on_disconnect()
    
    def _on_reconnect(self) -> None:
        """Handle reconnection to server."""
        self.stats["reconnections"] += 1
        self.logger.info("Reconnected to server")
        
        # If we had an active session, rejoin it
        if self.session_id and self.user_id:
            self.join_session(self.session_id, self.user_id)
    
    def _on_connected(self, data: Dict[str, Any]) -> None:
        """Handle successful connection confirmation from server."""
        self.logger.info(f"Server assigned SID: {data.get('sid', 'unknown')}")
        self.last_server_communication = time.time()
    
    def _on_session_joined(self, data: Dict[str, Any]) -> None:
        """Handle session joined confirmation.
        
        Args:
            data: Session data
        """
        self.logger.info(f"Joined session: {data.get('session_id')}")
        self.session_id = data.get('session_id')
        self.last_server_communication = time.time()
        
        # Queue for processing
        self.message_queue.put(('session_joined', data))
        
        self.on_session_joined(data)
    
    def _on_state_update(self, data: Dict[str, Any]) -> None:
        """Handle full state update.
        
        Args:
            data: State data
        """
        self.last_server_communication = time.time()
        self.stats["state_updates"] += 1
        
        # Track state version
        new_version = data.get('state_version', 0)
        if new_version > self.last_state_version:
            # Queue for processing
            self.pending_state_updates.put(('full', new_version, data))
            self.last_state_version = new_version
        
        self.on_state_update(data)
    
    def _on_state_delta(self, data: Dict[str, Any]) -> None:
        """Handle delta state update.
        
        Args:
            data: Delta state data
        """
        self.last_server_communication = time.time()
        self.stats["state_deltas"] += 1
        
        # Track state version
        new_version = data.get('state_version', 0)
        if new_version > self.last_state_version:
            # Queue for processing
            self.pending_state_updates.put(('delta', new_version, data))
            self.last_state_version = new_version
        
        self.on_state_delta(data)
    
    def _on_round_completed(self, data: Dict[str, Any]) -> None:
        """Handle round completed notification.
        
        Args:
            data: Round data
        """
        self.last_server_communication = time.time()
        
        # Calculate latency
        if 'timestamp' in data:
            latency = time.time() - data['timestamp']
            # Update exponential moving average
            self.stats["avg_latency"] = 0.9 * self.stats["avg_latency"] + 0.1 * latency
        
        # Queue for processing
        self.message_queue.put(('round_completed', data))
        
        self.on_round_completed(data)
    
    def _on_input_processed(self, data: Dict[str, Any]) -> None:
        """Handle input processed notification.
        
        Args:
            data: Processing result
        """
        self.last_server_communication = time.time()
        
        # Calculate latency
        if 'request_timestamp' in data:
            latency = time.time() - data['request_timestamp']
            # Update exponential moving average
            self.stats["avg_latency"] = 0.9 * self.stats["avg_latency"] + 0.1 * latency
        
        # Queue for processing
        self.message_queue.put(('input_processed', data))
        
        self.on_input_processed(data)
    
    def _on_sequence(self, data: Dict[str, Any]) -> None:
        """Handle sequence data.
        
        Args:
            data: Sequence data
        """
        self.last_server_communication = time.time()
        
        # Queue for processing
        self.message_queue.put(('sequence', data))
        
        self.on_sequence(data)
    
    def _on_session_ended(self, data: Dict[str, Any]) -> None:
        """Handle session ended notification.
        
        Args:
            data: Session end data
        """
        self.last_server_communication = time.time()
        
        # Reset session
        self.session_id = None
        
        # Queue for processing
        self.message_queue.put(('session_ended', data))
        
        self.on_session_ended(data)
    
    def _on_error(self, data: Dict[str, Any]) -> None:
        """Handle error from server.
        
        Args:
            data: Error data
        """
        self.last_server_communication = time.time()
        self.logger.error(f"Server error: {data.get('message', 'Unknown error')}")
        
        # Queue for processing
        self.message_queue.put(('error', data))
        
        self.on_error(data)
    
    def _process_incoming_messages(self) -> None:
        """Process incoming messages in a separate thread."""
        self.logger.info("Starting message processor thread")
        while self.message_processor_active:
            try:
                # Process pending state updates first to maintain state integrity
                if not self.pending_state_updates.empty():
                    update_type, version, data = self.pending_state_updates.get(block=False)
                    
                    if update_type == 'full':
                        # Replace entire state
                        self.state = data
                    elif update_type == 'delta':
                        # Apply delta to existing state
                        self.state = apply_delta(self.state, data)
                    
                    self.logger.debug(f"Applied state update, version: {version}")
                    self.pending_state_updates.task_done()
                
                # Process other messages
                if not self.message_queue.empty():
                    message_type, data = self.message_queue.get(block=False)
                    self.stats["messages_received"] += 1
                    
                    # Custom processing for each message type
                    if message_type == 'round_completed':
                        # Update round counter in local state
                        if 'round' in data and self.state:
                            self.state['round'] = data['round']
                    
                    self.message_queue.task_done()
                    
                # Small sleep to prevent CPU hogging
                time.sleep(0.01)
            except queue.Empty:
                # Queue is empty, just wait
                time.sleep(0.05)
            except Exception as e:
                self.logger.error(f"Error processing messages: {str(e)}")
                time.sleep(0.1)
    
    def _process_outbound_messages(self) -> None:
        """Process outbound messages in a separate thread for reliable delivery."""
        self.logger.info("Starting outbound message processor thread")
        while self.outbound_processor_active:
            try:
                if not self.outbound_queue.empty() and self.connected:
                    event, data = self.outbound_queue.get(block=False)
                    
                    # Add timestamp for latency tracking
                    if 'timestamp' not in data:
                        data['timestamp'] = time.time()
                    
                    # Send the message
                    self.sio.emit(event, data)
                    self.stats["messages_sent"] += 1
                    self.last_server_communication = time.time()
                    
                    self.outbound_queue.task_done()
                    
                # Small sleep to prevent CPU hogging
                time.sleep(0.01)
            except queue.Empty:
                # Queue is empty, just wait
                time.sleep(0.05)
            except Exception as e:
                self.logger.error(f"Error sending messages: {str(e)}")
                time.sleep(0.1)
    
    def _queue_outbound_message(self, event: str, data: Dict[str, Any]) -> None:
        """Queue a message for reliable delivery.
        
        Args:
            event: Event name
            data: Event data
        """
        self.outbound_queue.put((event, data))
    
    def _ping_server(self) -> None:
        """Send periodic pings to keep connection alive."""
        while self.connected:
            try:
                # Check if we haven't communicated with the server for too long
                time_since_last = time.time() - self.last_server_communication
                
                # If it's been too long since last communication, send a ping
                if time_since_last > 5:  # Ping every 5 seconds of inactivity
                    self.sio.emit('ping', {'timestamp': time.time()})
                    self.stats["last_ping"] = time.time()
                
                # Check for connection timeout
                if time_since_last > self.connection_timeout:
                    self.logger.warning(f"No server communication for {time_since_last:.1f} seconds. Reconnecting...")
                    self.sio.disconnect()
                    time.sleep(0.5)
                    self.sio.connect(self.server_url, transports=['websocket'])
                
                time.sleep(1)
            except Exception as e:
                self.logger.error(f"Ping error: {str(e)}")
                time.sleep(2)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get client statistics.
        
        Returns:
            Dictionary of client statistics
        """
        return {
            "connected": self.connected,
            "session_active": self.session_id is not None,
            "messages_received": self.stats["messages_received"],
            "messages_sent": self.stats["messages_sent"],
            "state_updates": self.stats["state_updates"],
            "state_deltas": self.stats["state_deltas"],
            "avg_latency_ms": self.stats["avg_latency"] * 1000,
            "last_server_communication_s": time.time() - self.last_server_communication,
            "reconnections": self.stats["reconnections"]
        }
    
    @abstractmethod
    def on_connect(self) -> None:
        """Handle connection event."""
        pass
    
    @abstractmethod
    def on_disconnect(self) -> None:
        """Handle disconnection event."""
        pass
    
    @abstractmethod
    def on_session_joined(self, data: Dict[str, Any]) -> None:
        """Handle session joined event.
        
        Args:
            data: Session data
        """
        pass
    
    @abstractmethod
    def on_state_update(self, data: Dict[str, Any]) -> None:
        """Handle state update event.
        
        Args:
            data: State data
        """
        pass
    
    @abstractmethod
    def on_state_delta(self, data: Dict[str, Any]) -> None:
        """Handle state delta event.
        
        Args:
            data: Delta data
        """
        pass
    
    @abstractmethod
    def on_round_completed(self, data: Dict[str, Any]) -> None:
        """Handle round completed event.
        
        Args:
            data: Round data
        """
        pass
    
    @abstractmethod
    def on_input_processed(self, data: Dict[str, Any]) -> None:
        """Handle input processed event.
        
        Args:
            data: Processing result
        """
        pass
    
    @abstractmethod
    def on_sequence(self, data: Dict[str, Any]) -> None:
        """Handle sequence event.
        
        Args:
            data: Sequence data
        """
        pass
    
    @abstractmethod
    def on_session_ended(self, data: Dict[str, Any]) -> None:
        """Handle session ended event.
        
        Args:
            data: Session end data
        """
        pass
    
    @abstractmethod
    def on_error(self, data: Dict[str, Any]) -> None:
        """Handle error event.
        
        Args:
            data: Error data
        """
        pass
    
    @abstractmethod
    def run(self) -> None:
        """Run the client application."""
        pass 