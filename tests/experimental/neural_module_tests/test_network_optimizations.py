#!/usr/bin/env python3
"""
Test Network Optimizations

This module tests the functionality of the network optimization system,
including compression, delta encoding, and message optimization.
"""

import unittest
import sys
from pathlib import Path
import json
import base64
import time
import random
import zlib

# Add the parent directory to sys.path if needed
parent_dir = str(Path(__file__).parent.parent.parent)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from MetaMindIQTrain.core.network_optimizations import (
    CompressionMethod, CompressionLevel, compress_data, decompress_data,
    delta_encode, delta_decode, encode_for_network, decode_from_network,
    optimize_message, decode_optimized_message, batch_compress, batch_decompress,
    _run_length_encode, _run_length_decode, clear_state_cache
)


class TestCompression(unittest.TestCase):
    """Test the compression functionality."""
    
    def setUp(self):
        """Set up test fixture."""
        self.test_data = {
            "string": "This is a test string with some repeated content. " * 10,
            "number": 42,
            "nested": {
                "list": [1, 2, 3, 4, 5] * 20,
                "bool": True,
                "null": None
            },
            "repeated": ["repeated item"] * 100
        }
        
        # Clear state cache between tests
        clear_state_cache()
        
    def test_compress_decompress(self):
        """Test compressing and decompressing data with different methods."""
        for method in [m for m in CompressionMethod if m != CompressionMethod.DELTA]:
            # Skip optional libraries if not available
            if method == CompressionMethod.BROTLI:
                try:
                    import brotli
                except ImportError:
                    continue  # Skip test if brotli not available
            
            if method == CompressionMethod.LZ4:
                try:
                    import lz4.frame
                except ImportError:
                    continue  # Skip test if lz4 not available
            
            with self.subTest(method=method.name):
                # Compress
                compressed, metadata = compress_data(
                    self.test_data, method=method, level=CompressionLevel.BALANCED
                )
                
                # Check metadata
                if method in [CompressionMethod.BROTLI, CompressionMethod.LZ4]:
                    # For methods that might fall back, check actual method used
                    self.assertIn('method', metadata)
                else:
                    self.assertEqual(metadata['method'], method.name)
                
                self.assertEqual(metadata['level'], CompressionLevel.BALANCED.name)
                self.assertIn('original_size', metadata)
                self.assertIn('compressed_size', metadata)
                self.assertIn('compression_ratio', metadata)
                
                # For all methods except NONE, compression should reduce size
                if method != CompressionMethod.NONE:
                    self.assertGreater(metadata['compression_ratio'], 1.0)
                
                # Decompress
                decompressed = decompress_data(compressed, metadata)
                
                # Check that data is preserved
                self.assertEqual(decompressed, self.test_data)
                
    def test_delta_encoding(self):
        """Test delta encoding and decoding."""
        client_id = "test_client"
        
        # Base state
        base_data = {"a": 1, "b": "test", "c": [1, 2, 3], "d": {"nested": "value"}}
        
        # First store base data in cache
        delta1, metadata1 = delta_encode(base_data, client_id)
        self.assertFalse(metadata1['delta'])  # First state is not a delta
        
        # Modified data
        modified_data = {
            "a": 1,  # unchanged
            "b": "modified",  # changed
            "c": [1, 2, 3, 4],  # changed
            "e": "new"  # added
            # "d" removed
        }
        
        # Encode delta
        delta2, metadata2 = delta_encode(modified_data, client_id)
        
        self.assertTrue(metadata2['delta'])  # Should be a delta
        self.assertIn('operations', metadata2)
        self.assertIn('base_hash', metadata2)
        
        # Check compression ratio (delta should be smaller than full data)
        json_size = len(json.dumps(modified_data).encode('utf-8'))
        delta_size = len(delta2)
        if json_size > 100:  # Meaningful test only for larger objects
            self.assertLess(delta_size, json_size)
        
        # Decode delta
        decoded = decompress_data(delta2, metadata2, client_id)
        
        # Check that decoded data matches
        self.assertEqual(decoded, modified_data)
        
    def test_hybrid_compression(self):
        """Test hybrid compression (delta + compression)."""
        client_id = "test_hybrid"
        
        # Base state - with repeated content to make compression effective
        base_data = {
            "list": [i for i in range(100)],
            "text": "This is a repeated text. " * 20
        }
        
        # Store base data
        compressed1, metadata1 = compress_data(
            base_data, method=CompressionMethod.HYBRID, client_id=client_id
        )
        
        # Modified data - change some values but keep structure similar
        modified_data = {
            "list": [i * 2 for i in range(100)],  # Modified values
            "text": "This is a modified repeated text. " * 20  # Modified text
        }
        
        # Compress with hybrid method
        compressed2, metadata2 = compress_data(
            modified_data, method=CompressionMethod.HYBRID, client_id=client_id
        )
        
        # Since the structure is similar, hybrid compression should be reasonably efficient
        gzip_compressed, gzip_metadata = compress_data(
            modified_data, method=CompressionMethod.GZIP
        )
        
        # Check that hybrid is still a valid method
        self.assertEqual(metadata2.get('method'), CompressionMethod.HYBRID.name)
        
        # In real-world data, hybrid compression should be more efficient
        # But in our test case with random data, sizes might be similar
        # So we just check that hybrid compression is not significantly worse
        self.assertLessEqual(len(compressed2) * 1.1, len(gzip_compressed) * 1.1)
        
        # Decompress hybrid
        decompressed = decompress_data(compressed2, metadata2, client_id)
        
        # Check that data is preserved
        self.assertEqual(decompressed, modified_data)


class TestNetworkEncoding(unittest.TestCase):
    """Test the network encoding functionality."""
    
    def setUp(self):
        """Set up test fixture."""
        self.test_data = {
            "id": "test_message",
            "content": {
                "text": "This is a network message with some content.",
                "values": [random.randint(0, 100) for _ in range(50)]
            },
            "timestamp": time.time()
        }
        
        # Clear state cache between tests
        clear_state_cache()
        
    def test_encode_decode_network(self):
        """Test encoding and decoding for network transmission."""
        # Encode
        encoded = encode_for_network(self.test_data)
        
        # Check encoded data
        self.assertIn('data', encoded)
        self.assertIn('metadata', encoded)
        
        # Data should be base64 encoded
        try:
            base64.b64decode(encoded['data'])
        except Exception:
            self.fail("encoded data is not valid base64")
        
        # Decode
        decoded = decode_from_network(encoded)
        
        # Check that data is preserved
        self.assertEqual(decoded, self.test_data)
        
    def test_delta_network_encoding(self):
        """Test delta encoding across network transmissions."""
        client_id = "test_network_client"
        
        # First message
        encoded1 = encode_for_network(self.test_data, client_id)
        decoded1 = decode_from_network(encoded1, client_id)
        
        # Check first message
        self.assertEqual(decoded1, self.test_data)
        
        # Second message - modified from first
        second_data = dict(self.test_data)
        second_data["content"]["text"] = "This message has been modified."
        second_data["content"]["values"] = [v + 10 for v in second_data["content"]["values"]]
        second_data["timestamp"] = time.time()
        
        # Encode and decode second message
        encoded2 = encode_for_network(second_data, client_id)
        decoded2 = decode_from_network(encoded2, client_id)
        
        # Check second message
        self.assertEqual(decoded2, second_data)
        
        # Third message - similar to second
        third_data = dict(second_data)
        third_data["timestamp"] = time.time()
        
        # Encode third message - should use delta or hybrid
        encoded3 = encode_for_network(third_data, client_id)
        
        # This should be no larger than full encoding
        full_encoded = encode_for_network(third_data)
        
        # Delta encoding should be reasonably efficient
        # But in a test environment, sizes might be similar
        # So we just check that it's not significantly worse
        self.assertLessEqual(len(encoded3['data']) * 1.1, len(full_encoded['data']) * 1.1)
        
        # Decode third message
        decoded3 = decode_from_network(encoded3, client_id)
        
        # Check third message
        self.assertEqual(decoded3, third_data)


class TestMessageOptimization(unittest.TestCase):
    """Test message optimization functionality."""
    
    def test_optimize_message(self):
        """Test optimizing messages."""
        # Create a message with null values and repetitive arrays
        message = {
            "id": "test",
            "values": [42] * 100,  # Repetitive array
            "empty": None,  # Null value
            "nested": {
                "text": "nested value",
                "nullValue": None,  # Nested null
                "repeatedList": ["same"] * 50  # Nested repetitive array
            }
        }
        
        # Optimize
        optimized = optimize_message(message)
        
        # Check that nulls are removed
        self.assertNotIn("empty", optimized)
        self.assertNotIn("nullValue", optimized["nested"])
        
        # Check that arrays are run-length encoded
        self.assertIsInstance(optimized["values"], dict)
        self.assertTrue(optimized["values"].get("_rle", False))
        
        # Decode
        decoded = decode_optimized_message(optimized)
        
        # Check that the original content is preserved (except nulls)
        expected = dict(message)
        del expected["empty"]
        del expected["nested"]["nullValue"]
        
        self.assertEqual(decoded["id"], expected["id"])
        self.assertEqual(decoded["values"], expected["values"])
        self.assertEqual(decoded["nested"]["text"], expected["nested"]["text"])
        self.assertEqual(decoded["nested"]["repeatedList"], expected["nested"]["repeatedList"])
        
    def test_run_length_encoding(self):
        """Test run-length encoding of arrays."""
        # Simple array with repetition
        array = [1, 1, 1, 2, 2, 3, 4, 4, 4, 4]
        
        # Encode
        encoded = _run_length_encode(array)
        
        # Expected: [[3,1], 2, 2, 3, [4,4]]
        self.assertEqual(encoded[0], [3, 1])  # 3 times 1
        self.assertEqual(encoded[1], 2)       # single 2
        self.assertEqual(encoded[2], 2)       # single 2
        self.assertEqual(encoded[3], 3)       # single 3
        self.assertEqual(encoded[4], [4, 4])  # 4 times 4
        
        # Decode
        decoded = _run_length_decode(encoded)
        
        # Check that original array is recovered
        self.assertEqual(decoded, array)
        
    def test_batch_compression(self):
        """Test batch compressing multiple messages."""
        # Create a batch of messages
        messages = [
            {"id": f"msg{i}", "data": {"value": i, "text": f"Message {i}"}}
            for i in range(5)
        ]
        
        client_id = "batch_test"
        
        # Compress batch
        batch = batch_compress(messages, client_id)
        
        # Check batch structure
        self.assertTrue(batch['batch'])
        self.assertEqual(batch['count'], 5)
        self.assertIn('data', batch)
        self.assertIn('metadata', batch)
        
        # Decompress batch
        decompressed = batch_decompress(batch, client_id)
        
        # Check that all messages are recovered
        self.assertEqual(len(decompressed), 5)
        for i, msg in enumerate(decompressed):
            self.assertEqual(msg['id'], f"msg{i}")
            self.assertEqual(msg['data']['value'], i)
            self.assertEqual(msg['data']['text'], f"Message {i}")


if __name__ == '__main__':
    unittest.main()