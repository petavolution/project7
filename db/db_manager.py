"""
Simple Storage Manager

A simplified storage module for the MetaMindIQTrain platform.
This version uses simple file-based storage to save session data.
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Storage directory
DATA_DIR = 'data'

def ensure_data_dir() -> str:
    """Ensure the data directory exists.
    
    Returns:
        Path to data directory
    """
    data_dir = Path(DATA_DIR)
    data_dir.mkdir(exist_ok=True)
    return str(data_dir)

def save_session_data(session_id: str, data: Dict[str, Any]) -> bool:
    """Save session data to a file.
    
    Args:
        session_id: Session identifier
        data: Session data
        
    Returns:
        True if successful, False otherwise
    """
    data_dir = ensure_data_dir()
    file_path = Path(data_dir) / f"session_{session_id}.json"
    
    try:
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
        return True
    except Exception as e:
        logger.error(f"Error saving session data: {str(e)}")
        return False

def load_session_data(session_id: str) -> Optional[Dict[str, Any]]:
    """Load session data from a file.
    
    Args:
        session_id: Session identifier
        
    Returns:
        Session data, or None if not found
    """
    data_dir = ensure_data_dir()
    file_path = Path(data_dir) / f"session_{session_id}.json"
    
    if not file_path.exists():
        return None
    
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading session data: {str(e)}")
        return None

def delete_session_data(session_id: str) -> bool:
    """Delete session data file.
    
    Args:
        session_id: Session identifier
        
    Returns:
        True if successful, False otherwise
    """
    data_dir = ensure_data_dir()
    file_path = Path(data_dir) / f"session_{session_id}.json"
    
    if not file_path.exists():
        return True
    
    try:
        file_path.unlink()
        return True
    except Exception as e:
        logger.error(f"Error deleting session data: {str(e)}")
        return False

def save_metrics(metrics_data: Dict[str, Any]) -> bool:
    """Save metrics data to a file.
    
    Args:
        metrics_data: Metrics data
        
    Returns:
        True if successful, False otherwise
    """
    data_dir = ensure_data_dir()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_path = Path(data_dir) / f"metrics_{timestamp}.json"
    
    try:
        with open(file_path, 'w') as f:
            json.dump(metrics_data, f, indent=2)
        return True
    except Exception as e:
        logger.error(f"Error saving metrics data: {str(e)}")
        return False 