#!/usr/bin/env python3
"""
Server-Client Integration Tests for MetaMindIQTrain.

This module tests the communication between the server and client
to ensure proper module loading and state synchronization.
"""

import os
import sys
import time
import unittest
import threading
import json
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parents[2]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Import server components
try:
    # Try relative imports
    from MetaMindIQTrain.server.optimized_server import MetaMindServer
    
    # Required for HTTP client
    import requests
    HAS_REQUESTS = True
except ImportError as e:
    print(f"Warning: Server components or requests library not available: {e}")
    HAS_REQUESTS = False


@unittest.skipIf(not HAS_REQUESTS, "Required server components not available")
class ServerClientIntegrationTests(unittest.TestCase):
    """Tests for server-client communication."""
    
    @classmethod
    def setUpClass(cls):
        """Start the server in a separate thread."""
        cls.server = None
        cls.server_thread = None
        cls.base_url = "http://localhost:5000"
        
        try:
            # Start server on a different port to avoid conflicts
            cls.server = MetaMindServer(host="localhost", port=5000, debug=False)
            
            # Start the server in a thread
            cls.server_thread = threading.Thread(target=cls.server.run)
            cls.server_thread.daemon = True
            cls.server_thread.start()
            
            # Give the server time to start
            time.sleep(2)
        except Exception as e:
            print(f"Failed to start server: {e}")
    
    def test_get_modules(self):
        """Test that the server provides a list of available modules."""
        try:
            response = requests.get(f"{self.base_url}/api/modules")
            self.assertEqual(response.status_code, 200)
            
            data = response.json()
            self.assertIn("modules", data)
            
            # Check for the expected modules
            module_ids = [m["id"] for m in data["modules"]]
            expected_modules = ["symbol_memory", "morph_matrix", "expand_vision"]
            
            for module_id in expected_modules:
                self.assertIn(module_id, module_ids, f"Module {module_id} not found in server response")
        except requests.exceptions.ConnectionError:
            self.skipTest("Server is not running")
    
    def test_create_session(self):
        """Test session creation for a specific module."""
        try:
            # Try to create a session for the symbol_memory module
            response = requests.post(
                f"{self.base_url}/api/sessions",
                json={"module_id": "symbol_memory"}
            )
            
            self.assertEqual(response.status_code, 200)
            
            data = response.json()
            self.assertIn("session_id", data)
            self.assertIn("state", data)
            
            # Verify the state has the basic structure
            self.assertIn("score", data["state"])
            self.assertIn("level", data["state"])
        except requests.exceptions.ConnectionError:
            self.skipTest("Server is not running")


if __name__ == "__main__":
    unittest.main() 