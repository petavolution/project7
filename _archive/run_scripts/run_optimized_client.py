#!/usr/bin/env python3
"""
Optimized Client Launcher for MetaMindIQTrain

This launcher provides a unified, high-performance client for the MetaMindIQTrain
platform with the following optimizations:

- Delta encoding for efficient state updates
- Component caching for improved rendering performance
- WebSocket state synchronization with compression
- Dynamic resolution support for any screen size
- Automatic module detection and loading
- Support for multiple rendering backends (pygame, terminal)
"""

import os
import sys
import logging
import time
import json
import argparse
import asyncio
import zlib
import base64
import signal
import importlib
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple, Union

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("optimized_client")

# Add parent directory to path for imports
parent_dir = Path(__file__).resolve().parent
sys.path.append(str(parent_dir))

# Import required modules
try:
    import pygame
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False
    logger.warning("pygame not available, falling back to terminal mode")

try:
    import websockets
    WEBSOCKETS_AVAILABLE = True
except ImportError:
    WEBSOCKETS_AVAILABLE = False
    logger.warning("websockets library not available, will use local modules only")

# Import from MetaMindIQTrain
try:
    from MetaMindIQTrain.config import (
        SCREEN_WIDTH, SCREEN_HEIGHT, DEFAULT_WINDOW_TITLE,
        DEFAULT_FPS, DEFAULT_BG_COLOR
    )
except ImportError:
    # Fallback defaults if config not available
    logger.warning("MetaMindIQTrain config not available, using defaults")
    SCREEN_WIDTH = 1440
    SCREEN_HEIGHT = 1024
    DEFAULT_WINDOW_TITLE = "MetaMindIQTrain"
    DEFAULT_FPS = 60
    DEFAULT_BG_COLOR = (15, 18, 28)

try:
    from MetaMindIQTrain.core.components import Component, reset_component_stats
except ImportError:
    logger.warning("Component system not available, some features may be limited")
    
    # Fallback function if not available
    def reset_component_stats():
        pass

# Define the delta decoder for efficient state updates
class DeltaDecoder:
    """Handles delta-encoded state updates with compression support."""
    
    def __init__(self):
        """Initialize the delta decoder."""
        self.base_state = {}
        self.state_version = 0
        self.stats = {
            'delta_updates': 0,
            'full_updates': 0,
            'compressed_updates': 0,
            'bytes_received': 0,
            'bytes_decompressed': 0,
            'compression_ratio': 0
        }
    
    def process_update(self, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process an update that may be delta-encoded or compressed.
        
        Args:
            update_data: Update data from server
            
        Returns:
            Complete state after applying update
        """
        # Check for compressed data
        if isinstance(update_data, str) and update_data.startswith('COMPRESSED:'):
            compressed_data = update_data[11:]  # Remove the 'COMPRESSED:' prefix
            try:
                # Decode from base64 and decompress
                binary_data = base64.b64decode(compressed_data)
                json_data = zlib.decompress(binary_data).decode('utf-8')
                update_data = json.loads(json_data)
                
                # Update stats
                self.stats['compressed_updates'] += 1
                self.stats['bytes_received'] += len(compressed_data)
                self.stats['bytes_decompressed'] += len(json_data)
                self.stats['compression_ratio'] = (
                    len(json_data) / len(compressed_data) if len(compressed_data) > 0 else 0
                )
            except Exception as e:
                logger.error(f"Error decompressing data: {e}")
                return self.base_state
        
        # Extract metadata
        metadata = update_data.get('_meta', {})
        is_delta = metadata.get('is_delta', False)
        version = metadata.get('version', 0)
        
        # Handle full state update
        if not is_delta:
            self.base_state = update_data
            self.state_version = version
            self.stats['full_updates'] += 1
            return self.base_state
        
        # Handle delta update
        self.stats['delta_updates'] += 1
        
        # Check if update is applicable to our base state
        base_version = metadata.get('base_version', 0)
        if base_version != self.state_version:
            logger.warning(f"Delta update mismatch: base_version={base_version}, state_version={self.state_version}")
            # Request full state from server (handled by calling code)
            return None
        
        # Apply delta to base state
        self.base_state = self.apply_delta(self.base_state, update_data)
        self.state_version = version
        
        return self.base_state
    
    def apply_delta(self, base_state: Dict[str, Any], delta: Dict[str, Any]) -> Dict[str, Any]:
        """Apply delta to base state to get updated state.
        
        Args:
            base_state: Base state dictionary
            delta: Delta dictionary with changes
            
        Returns:
            Updated state dictionary
        """
        # Make a deep copy of base state
        result = json.loads(json.dumps(base_state))
        
        # Apply each delta path (skip metadata)
        for path, value in delta.items():
            if path == '_meta':
                continue
                
            if "." in path:
                # Handle nested path
                parts = path.split(".")
                curr = result
                
                # Navigate to parent object
                for part in parts[:-1]:
                    if part not in curr:
                        curr[part] = {}
                    curr = curr[part]
                    
                # Set or delete value
                if value is None:
                    # Delete key
                    if parts[-1] in curr:
                        del curr[parts[-1]]
                else:
                    # Set value
                    curr[parts[-1]] = value
            else:
                # Handle top-level path
                if value is None:
                    # Delete key
                    if path in result:
                        del result[path]
                else:
                    # Set value
                    result[path] = value
                    
        return result
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about delta processing.
        
        Returns:
            Dictionary with statistics
        """
        return self.stats.copy()
    
    def reset(self):
        """Reset the decoder state."""
        self.base_state = {}
        self.state_version = 0
        self.stats = {
            'delta_updates': 0,
            'full_updates': 0,
            'compressed_updates': 0,
            'bytes_received': 0,
            'bytes_decompressed': 0,
            'compression_ratio': 0
        }

class OptimizedClient:
    """High-performance client for MetaMindIQTrain with optimizations."""
    
    def __init__(self, args):
        """Initialize the optimized client.
        
        Args:
            args: Command-line arguments
        """
        self.args = args
        self.running = False
        self.clock = None
        self.screen = None
        self.renderer = None
        self.current_state = {}
        self.fps = args.fps or DEFAULT_FPS
        self.title = DEFAULT_WINDOW_TITLE
        self.frame_count = 0
        self.module_id = args.module
        
        # Configure screen dimensions
        self.width = args.width or SCREEN_WIDTH
        self.height = args.height or SCREEN_HEIGHT
        
        # Initialize delta decoder
        self.delta_decoder = DeltaDecoder()
        
        # Performance tracking
        self.start_time = time.time()
        self.last_frame_time = time.time()
        self.last_update_time = time.time()
        self.frame_times = []
        self.max_frame_time_samples = 100
        
        # Network stats
        self.network_stats = {
            'messages_received': 0,
            'messages_sent': 0,
            'last_ping_time': 0,
            'avg_ping': 0
        }
        
        # Input state
        self.input_state = {
            'mouse_pos': (0, 0),
            'mouse_buttons': [False, False, False],
            'keys_pressed': set(),
            'keys_down': {}
        }
        
        # Set up signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        logger.info(f"Optimized client initialized with dimensions {self.width}x{self.height}")
    
    def signal_handler(self, sig, frame):
        """Handle termination signals."""
        logger.info("Received termination signal")
        self.running = False
    
    async def connect(self):
        """Connect to the server or load local module."""
        if self.args.server and WEBSOCKETS_AVAILABLE:
            # Connect to WebSocket server
            server_uri = f"ws://{self.args.server}:{self.args.port}"
            try:
                self.websocket = await websockets.connect(server_uri)
                logger.info(f"Connected to server at {server_uri}")
                return True
            except Exception as e:
                logger.error(f"Failed to connect to server: {e}")
                return False
        else:
            # Local mode - load module directly
            try:
                # Import available modules
                if self.module_id:
                    # Try to import the module class
                    module_path = f"MetaMindIQTrain.modules.{self.module_id}"
                    module_class_name = ''.join(word.capitalize() for word in self.module_id.split('_'))
                    
                    try:
                        module_pkg = importlib.import_module(module_path)
                        module_class = getattr(module_pkg, module_class_name)
                        self.module_instance = module_class()
                        logger.info(f"Loaded module: {self.module_id}")
                        return True
                    except (ImportError, AttributeError) as e:
                        logger.error(f"Could not load module {self.module_id}: {e}")
                        return False
                else:
                    logger.error("No module specified and not connected to server")
                    return False
            except Exception as e:
                logger.error(f"Error in local mode: {e}")
                return False
    
    def init_pygame(self):
        """Initialize pygame renderer."""
        if not PYGAME_AVAILABLE:
            logger.error("pygame not available, cannot initialize pygame renderer")
            return False
        
        # Initialize pygame
        pygame.init()
        
        # Create the window with the configured dimensions
        if self.args.fullscreen:
            self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
            actual_size = self.screen.get_size()
            logger.info(f"Created fullscreen window with dimensions {actual_size[0]}x{actual_size[1]}")
        else:
            self.screen = pygame.display.set_mode((self.width, self.height))
            logger.info(f"Created window with dimensions {self.width}x{self.height}")
        
        # Set window title
        pygame.display.set_caption(self.title)
        
        # Create clock for FPS control
        self.clock = pygame.time.Clock()
        
        # Initialize the optimized renderer
        try:
            # First try to import our optimized renderer
            from MetaMindIQTrain.clients.pygame.optimized_renderer import OptimizedRenderer
            self.renderer = OptimizedRenderer(
                self.screen, 
                self.module_id or 'unknown',
                width=self.width,
                height=self.height
            )
            logger.info("Using optimized renderer")
        except ImportError:
            # Fall back to enhanced generic renderer
            try:
                from MetaMindIQTrain.clients.pygame.renderers.enhanced_generic_renderer import EnhancedGenericRenderer
                self.renderer = EnhancedGenericRenderer(
                    self.screen, 
                    self.module_id or 'unknown',
                    width=self.width,
                    height=self.height
                )
                logger.info("Using enhanced generic renderer")
            except ImportError:
                logger.error("Could not load any renderer")
                return False
        
        return True
    
    def init_terminal(self):
        """Initialize terminal renderer."""
        # Simple terminal renderer
        logger.info("Initialized terminal renderer")
        return True
    
    async def start(self):
        """Start the client."""
        # Choose renderer based on arguments
        if self.args.renderer == 'pygame' and PYGAME_AVAILABLE:
            if not self.init_pygame():
                return False
        elif self.args.renderer == 'terminal':
            if not self.init_terminal():
                return False
        else:
            logger.error(f"Unsupported renderer: {self.args.renderer}")
            return False
        
        # Connect to server or load local module
        if not await self.connect():
            return False
        
        # Reset component stats
        reset_component_stats()
        
        # Set up running flag
        self.running = True
        self.start_time = time.time()
        
        # Run main loop
        if self.args.renderer == 'pygame':
            await self.pygame_main_loop()
        else:
            await self.terminal_main_loop()
        
        # Clean up
        self.cleanup()
        
        return True
    
    async def pygame_main_loop(self):
        """Main loop for pygame renderer."""
        while self.running:
            # Process events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE and self.args.fullscreen:
                        self.running = False
                    self.input_state['keys_pressed'].add(event.key)
                    self.input_state['keys_down'][event.key] = time.time()
                    await self.handle_key_input(event.key)
                elif event.type == pygame.KEYUP:
                    if event.key in self.input_state['keys_pressed']:
                        self.input_state['keys_pressed'].remove(event.key)
                    if event.key in self.input_state['keys_down']:
                        del self.input_state['keys_down'][event.key]
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    await self.handle_click(mouse_x, mouse_y, event.button)
                # Track mouse position for hovering
                self.input_state['mouse_pos'] = pygame.mouse.get_pos()
                self.input_state['mouse_buttons'] = pygame.mouse.get_pressed()
            
            # Update state
            await self.update_state()
            
            # Render current state
            if self.current_state and self.renderer:
                self.renderer.render(self.current_state)
            
            # Update display
            pygame.display.flip()
            
            # Control FPS
            self.clock.tick(self.fps)
            
            # Track frame time
            current_time = time.time()
            frame_time = current_time - self.last_frame_time
            self.last_frame_time = current_time
            
            # Keep track of frame times for performance metrics
            self.frame_times.append(frame_time)
            if len(self.frame_times) > self.max_frame_time_samples:
                self.frame_times.pop(0)
            
            # Increment frame counter
            self.frame_count += 1
    
    async def terminal_main_loop(self):
        """Main loop for terminal renderer."""
        while self.running:
            # Clear the terminal
            os.system('clear' if os.name == 'posix' else 'cls')
            
            # Update state
            await self.update_state()
            
            # Display basic info
            if self.current_state:
                module_name = self.current_state.get('module', {}).get('name', 'Unknown Module')
                score = self.current_state.get('game', {}).get('score', 0)
                level = self.current_state.get('game', {}).get('level', 1)
                message = self.current_state.get('game', {}).get('message', '')
                
                print(f"=== {module_name} ===")
                print(f"Score: {score} | Level: {level}")
                print(f"Message: {message}")
                print("\nPress Ctrl+C to exit.")
            else:
                print("No state available.")
            
            # Increment frame counter
            self.frame_count += 1
            
            # Sleep to control update rate
            await asyncio.sleep(1.0 / self.fps)
    
    async def update_state(self):
        """Update the current state."""
        # Check if we're in server mode
        if hasattr(self, 'websocket'):
            # Periodically send ping to measure latency
            if time.time() - self.network_stats['last_ping_time'] > 2.0:
                ping_start = time.time()
                await self.websocket.send(json.dumps({"type": "ping", "time": ping_start}))
                self.network_stats['last_ping_time'] = ping_start
            
            # Check for server messages
            try:
                message = await asyncio.wait_for(self.websocket.recv(), 0.01)
                self.network_stats['messages_received'] += 1
                
                # Parse the message
                data = json.loads(message)
                
                # Handle different message types
                if data.get('type') == 'state':
                    # Process state update
                    state_data = data.get('state', {})
                    processed_state = self.delta_decoder.process_update(state_data)
                    
                    if processed_state is None:
                        # Delta update failed, request full state
                        await self.websocket.send(json.dumps({"type": "get_full_state"}))
                    else:
                        self.current_state = processed_state
                
                elif data.get('type') == 'pong':
                    # Update ping statistic
                    ping_time = data.get('time', 0)
                    ping_duration = time.time() - ping_time
                    self.network_stats['avg_ping'] = (
                        self.network_stats['avg_ping'] * 0.9 + ping_duration * 0.1
                    )
            
            except asyncio.TimeoutError:
                # No message available, continue
                pass
            except websockets.exceptions.ConnectionClosed:
                logger.warning("WebSocket connection closed")
                self.running = False
            except Exception as e:
                logger.error(f"Error receiving message: {e}")
        
        else:
            # Local mode - get state directly from module
            try:
                if hasattr(self, 'module_instance'):
                    # Update the module
                    current_time = time.time()
                    dt = current_time - self.last_update_time
                    self.last_update_time = current_time
                    
                    # Call update method
                    self.module_instance.update(dt)
                    
                    # Get the state
                    self.current_state = self.module_instance.get_state()
            except Exception as e:
                logger.error(f"Error updating local module: {e}")
    
    async def handle_click(self, x, y, button=1):
        """Handle mouse click event.
        
        Args:
            x: X coordinate
            y: Y coordinate
            button: Mouse button (1=left, 2=middle, 3=right)
        """
        # Convert click to logical coordinates if renderer is using scaling
        logical_x = x
        logical_y = y
        
        if hasattr(self.renderer, 'scale_x') and hasattr(self.renderer, 'scale_y'):
            logical_x = int(x / self.renderer.scale_x)
            logical_y = int(y / self.renderer.scale_y)
        
        # Handle in server mode
        if hasattr(self, 'websocket'):
            try:
                await self.websocket.send(json.dumps({
                    "type": "click",
                    "x": logical_x,
                    "y": logical_y,
                    "button": button
                }))
                self.network_stats['messages_sent'] += 1
            except Exception as e:
                logger.error(f"Error sending click event: {e}")
        
        # Handle in local mode
        elif hasattr(self, 'module_instance'):
            try:
                # Call module's handle_click method
                self.module_instance.handle_click(logical_x, logical_y)
            except Exception as e:
                logger.error(f"Error handling click in local module: {e}")
    
    async def handle_key_input(self, key):
        """Handle keyboard input.
        
        Args:
            key: Key code
        """
        # Handle in server mode
        if hasattr(self, 'websocket'):
            try:
                await self.websocket.send(json.dumps({
                    "type": "key",
                    "key": key
                }))
                self.network_stats['messages_sent'] += 1
            except Exception as e:
                logger.error(f"Error sending key event: {e}")
        
        # Handle in local mode - any specific key bindings
        elif hasattr(self, 'module_instance'):
            try:
                # Special keys for debugging
                if key == pygame.K_r:
                    # Reset the module
                    self.module_instance.reset()
                    logger.info("Module reset")
            except Exception as e:
                logger.error(f"Error handling key in local module: {e}")
    
    def cleanup(self):
        """Clean up resources."""
        try:
            # Display performance stats
            elapsed = time.time() - self.start_time
            avg_frame_time = sum(self.frame_times) / len(self.frame_times) if self.frame_times else 0
            avg_fps = 1.0 / avg_frame_time if avg_frame_time > 0 else 0
            
            logger.info(f"Performance: {self.frame_count} frames in {elapsed:.2f}s = {self.frame_count/elapsed:.2f} fps")
            logger.info(f"Average frame time: {avg_frame_time*1000:.2f}ms (average FPS: {avg_fps:.2f})")
            
            if hasattr(self, 'renderer') and self.renderer:
                if hasattr(self.renderer, 'cleanup'):
                    self.renderer.cleanup()
            
            if PYGAME_AVAILABLE and pygame.get_init():
                pygame.quit()
                
            logger.info("Cleanup complete")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")

# Constants
DEFAULT_FPS = 60
DEFAULT_WINDOW_TITLE = "MetaMind IQ Train - Optimized Client"
SCREEN_WIDTH = 1440
SCREEN_HEIGHT = 1024
DEFAULT_PORT = 8765

# Check for optional dependencies
PYGAME_AVAILABLE = False
WEBSOCKETS_AVAILABLE = False

try:
    import pygame
    PYGAME_AVAILABLE = True
except ImportError:
    logger.warning("pygame not available, GUI rendering will be disabled")

try:
    import websockets
    WEBSOCKETS_AVAILABLE = True
except ImportError:
    logger.warning("websockets not available, server mode will be disabled")

def reset_component_stats():
    """Reset component render statistics."""
    # For tracking component render stats across the application
    global component_stats
    component_stats = {
        'total_renders': 0,
        'cached_renders': 0,
        'total_render_time': 0,
        'components_created': 0
    }
    
    return component_stats

# Component stats global
component_stats = reset_component_stats()

async def main():
    """Main entry point for the optimized client."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="MetaMind IQ Train Optimized Client")
    
    # Module selection
    parser.add_argument('-m', '--module', type=str, help='Module ID to run (e.g. symbol_memory, morph_matrix, expand_vision)')
    
    # Renderer options
    parser.add_argument('-r', '--renderer', type=str, default='pygame', choices=['pygame', 'terminal'],
                        help='Renderer to use')
    
    # Display options
    parser.add_argument('-w', '--width', type=int, help=f'Window width (default: {SCREEN_WIDTH})')
    parser.add_argument('-h', '--height', type=int, help=f'Window height (default: {SCREEN_HEIGHT})')
    parser.add_argument('-f', '--fullscreen', action='store_true', help='Run in fullscreen mode')
    parser.add_argument('--fps', type=int, help=f'Target FPS (default: {DEFAULT_FPS})')
    
    # Network options
    parser.add_argument('-s', '--server', type=str, help='Server address')
    parser.add_argument('-p', '--port', type=int, default=DEFAULT_PORT, help=f'Server port (default: {DEFAULT_PORT})')
    
    # Debug options
    parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose logging')
    parser.add_argument('-d', '--debug', action='store_true', help='Enable debug mode with performance overlay')
    
    args = parser.parse_args()
    
    # Configure logging based on verbosity
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Check for required dependencies based on chosen renderer
    if args.renderer == 'pygame' and not PYGAME_AVAILABLE:
        logger.error("pygame is required for GUI rendering but is not available. Install with: pip install pygame")
        return 1
    
    if args.server and not WEBSOCKETS_AVAILABLE:
        logger.error("websockets package is required for server mode but is not available. Install with: pip install websockets")
        return 1
    
    # Create and start client
    client = OptimizedClient(args)
    
    try:
        success = await client.start()
        if not success:
            logger.error("Failed to start client")
            return 1
    except KeyboardInterrupt:
        logger.info("Client terminated by user")
    except Exception as e:
        logger.exception(f"Unhandled exception: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    # Run the async main function
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\nExiting client...")
        sys.exit(0)
