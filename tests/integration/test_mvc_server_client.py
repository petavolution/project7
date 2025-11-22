#!/usr/bin/env python3
"""
MVC Module Server-Client Integration Test

This module tests the client-server communication for MVC-based modules.
It verifies that the modules can be properly loaded by the server and
that clients can connect and interact with the modules.

Usage:
    1. Run the test directly: python test_mvc_server_client.py
    2. Include in test suite: pytest -xvs test_mvc_server_client.py
"""

import os
import sys
import unittest
import threading
import time
import json
import socket
import tempfile
from pathlib import Path
from unittest.mock import patch

# Add the project root to the Python path
project_root = Path(__file__).parents[2]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Need to set this for headless testing
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

try:
    # Import server components
    from MetaMindIQTrain.server.server import ModuleServer
    from MetaMindIQTrain.server.session_manager import SessionManager
    from MetaMindIQTrain.server.module_provider import ModuleProvider
    
    # Import client components
    from MetaMindIQTrain.clients.client import ModuleClient
    
    # Import MVC modules
    from MetaMindIQTrain.modules.symbol_memory_mvc import SymbolMemory as SymbolMemoryMVC
    from MetaMindIQTrain.modules.morph_matrix_mvc import MorphMatrix as MorphMatrixMVC
    from MetaMindIQTrain.modules.expand_vision_Grid_mvc import ExpandVision as ExpandVisionMVC
except ImportError as e:
    # Fallback to direct imports if the module structure is different
    try:
        # Try to determine if we're using alternative import paths
        import MetaMindIQTrain
        print(f"Using alternative import paths for {MetaMindIQTrain.__file__}")
        
        # Try importing directly
        import importlib.util
        import importlib
        
        # Load server and client modules dynamically
        server_spec = importlib.util.find_spec("server", package="MetaMindIQTrain")
        if server_spec:
            server_module = importlib.import_module("MetaMindIQTrain.server.server")
            session_module = importlib.import_module("MetaMindIQTrain.server.session_manager")
            provider_module = importlib.import_module("MetaMindIQTrain.server.module_provider")
            ModuleServer = server_module.ModuleServer
            SessionManager = session_module.SessionManager
            ModuleProvider = provider_module.ModuleProvider
            
        client_spec = importlib.util.find_spec("client", package="MetaMindIQTrain")
        if client_spec:
            client_module = importlib.import_module("MetaMindIQTrain.clients.client")
            ModuleClient = client_module.ModuleClient
            
        # Try to import MVC modules directly
        mvc_spec = importlib.util.find_spec("symbol_memory_mvc", package="MetaMindIQTrain.modules")
        if mvc_spec:
            symbol_memory_mvc = importlib.import_module("MetaMindIQTrain.modules.symbol_memory_mvc")
            morph_matrix_mvc = importlib.import_module("MetaMindIQTrain.modules.morph_matrix_mvc")
            expand_vision_mvc = importlib.import_module("MetaMindIQTrain.modules.expand_vision_mvc")
            SymbolMemoryMVC = symbol_memory_mvc.SymbolMemory
            MorphMatrixMVC = morph_matrix_mvc.MorphMatrix
            ExpandVisionMVC = expand_vision_mvc.ExpandVision
    except ImportError as inner_e:
        print(f"Error importing required modules: {inner_e}")
        print("Make sure the server and client components are properly installed.")
        raise


class MockServer:
    """Mock server for testing client-server communication."""
    
    def __init__(self, host='localhost', port=8000):
        """Initialize the mock server.
        
        Args:
            host: Server host
            port: Server port
        """
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.clients = []
        self.running = False
        self.thread = None
        
        # Initialize modules
        self.modules = {
            'symbol_memory_mvc': SymbolMemoryMVC(difficulty=1),
            'morph_matrix_mvc': MorphMatrixMVC(difficulty=1),
            'expand_vision_mvc': ExpandVisionMVC(screen_width=800, screen_height=600)
        }
        
        # Current active module
        self.active_module = None
    
    def start(self):
        """Start the server in a separate thread."""
        self.socket.bind((self.host, self.port))
        self.socket.listen(5)
        self.running = True
        self.thread = threading.Thread(target=self.run)
        self.thread.daemon = True
        self.thread.start()
        return self.thread
    
    def run(self):
        """Run the server loop."""
        print(f"Mock server running on {self.host}:{self.port}")
        
        while self.running:
            try:
                client_socket, addr = self.socket.accept()
                print(f"New client connected: {addr}")
                client_thread = threading.Thread(target=self.handle_client, args=(client_socket,))
                client_thread.daemon = True
                client_thread.start()
                self.clients.append((client_socket, addr, client_thread))
            except Exception as e:
                if self.running:  # Only print error if still running
                    print(f"Server error: {e}")
                break
    
    def handle_client(self, client_socket):
        """Handle client communication.
        
        Args:
            client_socket: Client socket connection
        """
        try:
            # Set a default module
            if not self.active_module and self.modules:
                self.active_module = next(iter(self.modules.values()))
            
            # Send initial state
            if self.active_module:
                state = self.active_module.get_state()
                response = {
                    'type': 'state_update',
                    'data': state
                }
                client_socket.sendall(json.dumps(response).encode() + b'\n')
            
            # Handle client messages
            while self.running:
                # Receive data from client
                data = b''
                while b'\n' not in data:
                    chunk = client_socket.recv(4096)
                    if not chunk:
                        break
                    data += chunk
                
                if not data:
                    break
                
                # Parse and handle the message
                message = json.loads(data.decode().strip())
                message_type = message.get('type')
                
                if message_type == 'get_state':
                    # Send current state
                    if self.active_module:
                        state = self.active_module.get_state()
                        response = {
                            'type': 'state_update',
                            'data': state
                        }
                        client_socket.sendall(json.dumps(response).encode() + b'\n')
                
                elif message_type == 'click':
                    # Handle click event
                    if self.active_module:
                        x = message.get('x', 0)
                        y = message.get('y', 0)
                        self.active_module.handle_click(x, y)
                        
                        # Send updated state
                        state = self.active_module.get_state()
                        response = {
                            'type': 'state_update',
                            'data': state
                        }
                        client_socket.sendall(json.dumps(response).encode() + b'\n')
                
                elif message_type == 'select_module':
                    # Switch active module
                    module_id = message.get('module_id')
                    if module_id in self.modules:
                        self.active_module = self.modules[module_id]
                        
                        # Send updated state
                        state = self.active_module.get_state()
                        response = {
                            'type': 'state_update',
                            'data': state
                        }
                        client_socket.sendall(json.dumps(response).encode() + b'\n')
        except Exception as e:
            print(f"Error handling client: {e}")
        finally:
            client_socket.close()
    
    def stop(self):
        """Stop the server."""
        self.running = False
        
        # Close all client connections
        for client_socket, _, _ in self.clients:
            try:
                client_socket.close()
            except:
                pass
        
        # Close server socket
        try:
            self.socket.close()
        except:
            pass


class MVCServerClientTests(unittest.TestCase):
    """Tests for server-client communication with MVC modules."""
    
    @classmethod
    def setUpClass(cls):
        """Set up the test class."""
        # Create a temporary directory for test data
        cls.temp_dir = tempfile.TemporaryDirectory()
        
        # Create a mock server instance
        cls.server = MockServer(port=8001)
        cls.server_thread = cls.server.start()
        
        # Allow the server time to start
        time.sleep(0.5)
    
    @classmethod
    def tearDownClass(cls):
        """Clean up after tests."""
        # Stop the server
        cls.server.stop()
        
        # Clean up the temporary directory
        cls.temp_dir.cleanup()
    
    def test_client_connection(self):
        """Test that a client can connect to the server."""
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        try:
            # Connect to the server
            client.connect(('localhost', 8001))
            
            # Check that connection was successful
            self.assertTrue(client.fileno() > 0, "Client failed to connect to server")
            
            # Close the connection
            client.close()
        except Exception as e:
            self.fail(f"Connection test failed: {e}")
    
    def test_state_retrieval(self):
        """Test that a client can retrieve state from the server."""
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        try:
            # Connect to the server
            client.connect(('localhost', 8001))
            
            # Request state
            request = {
                'type': 'get_state'
            }
            client.sendall(json.dumps(request).encode() + b'\n')
            
            # Receive response
            data = b''
            while b'\n' not in data:
                chunk = client.recv(4096)
                if not chunk:
                    break
                data += chunk
            
            # Parse response
            response = json.loads(data.decode().strip())
            
            # Check that we received state data
            self.assertEqual(response['type'], 'state_update', "Unexpected response type")
            self.assertIn('data', response, "Response missing state data")
            self.assertIn('components', response['data'], "State missing components")
            
            # Close the connection
            client.close()
        except Exception as e:
            self.fail(f"State retrieval test failed: {e}")
    
    def test_module_interaction(self):
        """Test that a client can interact with a module."""
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        try:
            # Connect to the server
            client.connect(('localhost', 8001))
            
            # Send a click event
            request = {
                'type': 'click',
                'x': 400,
                'y': 300
            }
            client.sendall(json.dumps(request).encode() + b'\n')
            
            # Receive response
            data = b''
            while b'\n' not in data:
                chunk = client.recv(4096)
                if not chunk:
                    break
                data += chunk
            
            # Parse response
            response = json.loads(data.decode().strip())
            
            # Check that we received state data
            self.assertEqual(response['type'], 'state_update', "Unexpected response type")
            self.assertIn('data', response, "Response missing state data")
            
            # Close the connection
            client.close()
        except Exception as e:
            self.fail(f"Module interaction test failed: {e}")
    
    def test_module_selection(self):
        """Test that a client can select a different module."""
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        try:
            # Connect to the server
            client.connect(('localhost', 8001))
            
            # Select a different module
            request = {
                'type': 'select_module',
                'module_id': 'morph_matrix_mvc'
            }
            client.sendall(json.dumps(request).encode() + b'\n')
            
            # Receive response
            data = b''
            while b'\n' not in data:
                chunk = client.recv(4096)
                if not chunk:
                    break
                data += chunk
            
            # Parse response
            response = json.loads(data.decode().strip())
            
            # Check that we received state data
            self.assertEqual(response['type'], 'state_update', "Unexpected response type")
            self.assertIn('data', response, "Response missing state data")
            
            # Close the connection
            client.close()
        except Exception as e:
            self.fail(f"Module selection test failed: {e}")


if __name__ == "__main__":
    unittest.main() 