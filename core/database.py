import csv
import os
import uuid
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging
from threading import Lock

# Configure logging
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class CSVDatabase:
    """Simple CSV-based database for storing training sessions.
    
    This implementation includes caching to reduce file I/O operations and
    uses a lock to ensure thread safety when multiple clients access the database.
    """
    
    def __init__(self, file_path: str, cache_size: int = 100):
        """Initialize the database.
        
        Args:
            file_path: Path to the CSV file
            cache_size: Maximum number of sessions to cache in memory
        """
        self.file_path = file_path
        self.cache_size = cache_size
        self.cache = {}  # Session ID -> session data
        self.last_accessed = []  # LRU tracking
        self.lock = Lock()  # For thread safety
        self._ensure_file_exists()
    
    def _ensure_file_exists(self) -> None:
        """Ensure the CSV file exists with headers."""
        if not os.path.exists(self.file_path):
            os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
            with open(self.file_path, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'session_id', 'user_id', 'module_type', 'created_at', 
                    'updated_at', 'status', 'difficulty_level', 'rounds_completed', 'score'
                ])
            logger.info(f"Created new database file at {self.file_path}")
    
    def _read_all(self) -> List[Dict[str, Any]]:
        """Read all records from the CSV file.
        
        Returns:
            List of dictionaries representing the records
        """
        try:
            with open(self.file_path, 'r', newline='') as f:
                reader = csv.DictReader(f)
                return list(reader)
        except Exception as e:
            logger.error(f"Error reading database: {str(e)}")
            return []
    
    def _write_all(self, records: List[Dict[str, Any]]) -> None:
        """Write all records to the CSV file.
        
        Args:
            records: List of dictionaries representing the records
        """
        if not records:
            return
            
        try:
            fieldnames = records[0].keys()
            with open(self.file_path, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(records)
        except Exception as e:
            logger.error(f"Error writing database: {str(e)}")
    
    def _update_cache(self, session_id: str, session_data: Dict[str, Any]) -> None:
        """Update the cache with a session.
        
        Args:
            session_id: ID of the session
            session_data: Session data
        """
        # Remove from LRU if already present
        if session_id in self.cache:
            self.last_accessed.remove(session_id)
        
        # Add to cache and LRU
        self.cache[session_id] = session_data
        self.last_accessed.append(session_id)
        
        # If cache is full, remove least recently used
        if len(self.cache) > self.cache_size:
            oldest_id = self.last_accessed.pop(0)
            del self.cache[oldest_id]
    
    def _access_cache(self, session_id: str) -> None:
        """Mark a session as recently accessed in the LRU cache.
        
        Args:
            session_id: ID of the session
        """
        if session_id in self.cache:
            self.last_accessed.remove(session_id)
            self.last_accessed.append(session_id)
    
    def create_session(self, session_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new training session.
        
        Args:
            session_data: Dictionary with session data
            
        Returns:
            Dictionary representing the created session
        """
        with self.lock:
            # If session_id is not provided, generate one
            if 'session_id' not in session_data:
                session_data['session_id'] = str(uuid.uuid4())
            
            # Ensure timestamp fields
            now = datetime.now().isoformat()
            if 'created_at' not in session_data:
                session_data['created_at'] = now
            if 'updated_at' not in session_data:
                session_data['updated_at'] = now
            
            # Ensure status field
            if 'status' not in session_data:
                session_data['status'] = 'active'
                
            # Ensure numeric fields are strings (for CSV compatibility)
            for field in ['difficulty_level', 'rounds_completed', 'score']:
                if field in session_data and not isinstance(session_data[field], str):
                    session_data[field] = str(session_data[field])
            
            # Read current records
            records = self._read_all()
            
            # Append new session
            records.append(session_data)
            
            # Write back to file
            self._write_all(records)
            
            # Update cache
            self._update_cache(session_data['session_id'], session_data)
            
            logger.info(f"Created session: {session_data['session_id']}")
            return session_data
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get a session by ID.
        
        Args:
            session_id: ID of the session to retrieve
            
        Returns:
            Dictionary representing the session, or None if not found
        """
        with self.lock:
            # Check cache first
            if session_id in self.cache:
                self._access_cache(session_id)
                return self.cache[session_id]
            
            # Not in cache, read from file
            records = self._read_all()
            for record in records:
                if record['session_id'] == session_id:
                    # Add to cache
                    self._update_cache(session_id, record)
                    return record
            
            logger.warning(f"Session not found: {session_id}")
            return None
    
    def update_session(self, session_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update a session.
        
        Args:
            session_id: ID of the session to update
            updates: Dictionary of fields to update
            
        Returns:
            Dictionary representing the updated session, or None if not found
        """
        with self.lock:
            # Ensure updated_at field
            updates['updated_at'] = datetime.now().isoformat()
            
            # Ensure numeric fields are strings (for CSV compatibility)
            for field in ['difficulty_level', 'rounds_completed', 'score']:
                if field in updates and not isinstance(updates[field], str):
                    updates[field] = str(updates[field])
            
            # Get all records
            records = self._read_all()
            updated_session = None
            
            # Find and update the session
            for i, record in enumerate(records):
                if record['session_id'] == session_id:
                    records[i].update(updates)
                    updated_session = records[i]
                    break
            
            # If found, write back to file and update cache
            if updated_session:
                self._write_all(records)
                self._update_cache(session_id, updated_session)
                logger.info(f"Updated session: {session_id}")
            else:
                logger.warning(f"Session not found for update: {session_id}")
                
            return updated_session
    
    def delete_session(self, session_id: str) -> bool:
        """Delete a session.
        
        Args:
            session_id: ID of the session to delete
            
        Returns:
            True if deleted, False if not found
        """
        with self.lock:
            # Remove from cache
            if session_id in self.cache:
                del self.cache[session_id]
                self.last_accessed.remove(session_id)
            
            # Get all records
            records = self._read_all()
            initial_count = len(records)
            
            # Filter out the session to delete
            records = [r for r in records if r['session_id'] != session_id]
            
            # If count changed, write back to file
            if len(records) < initial_count:
                self._write_all(records)
                logger.info(f"Deleted session: {session_id}")
                return True
            
            logger.warning(f"Session not found for deletion: {session_id}")
            return False
    
    def list_sessions(self, user_id: Optional[str] = None, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """List sessions with optional filtering.
        
        Args:
            user_id: Filter by user ID
            status: Filter by session status
            
        Returns:
            List of dictionaries representing the matching sessions
        """
        with self.lock:
            # Get all records
            records = self._read_all()
            
            # Apply filters
            if user_id:
                records = [r for r in records if r['user_id'] == user_id]
                
            if status:
                records = [r for r in records if r['status'] == status]
            
            # Update cache with any sessions we read
            for record in records:
                session_id = record['session_id']
                self._update_cache(session_id, record)
                
            return records
    
    def record_round_result(self, session_id: str, score_delta: int) -> Optional[Dict[str, Any]]:
        """Record the result of a training round.
        
        Args:
            session_id: ID of the session
            score_delta: Change in score
            
        Returns:
            Dictionary representing the updated session, or None if not found
        """
        with self.lock:
            # Get the session
            session = self.get_session(session_id)
            if not session:
                logger.warning(f"Session not found for round result: {session_id}")
                return None
                
            # Update rounds completed and score
            rounds_completed = int(session['rounds_completed']) + 1
            current_score = int(session['score'])
            new_score = current_score + score_delta
            
            # Apply updates
            updates = {
                'rounds_completed': str(rounds_completed),
                'score': str(new_score)
            }
            
            logger.info(f"Recorded round result for session {session_id}: +{score_delta} points")
            return self.update_session(session_id, updates)
    
    def export_to_json(self, output_path: str) -> bool:
        """Export the database to a JSON file.
        
        Args:
            output_path: Path to the output JSON file
            
        Returns:
            True if successful, False otherwise
        """
        with self.lock:
            try:
                # Get all records
                records = self._read_all()
                
                # Write to JSON file
                with open(output_path, 'w') as f:
                    json.dump(records, f, indent=2)
                
                logger.info(f"Exported database to {output_path}")
                return True
            except Exception as e:
                logger.error(f"Error exporting database: {str(e)}")
                return False 