"""
Core package for MetaMindIQTrain

Contains the core components of the application architecture including
the component system, context management, rendering system, and application lifecycle.
"""

# Protocol definitions for client-server communication
PROTOCOL_VERSION = "1.0.0"

# Message types
MESSAGE_TYPES = {
    # Session management
    "JOIN_SESSION": "join_session",
    "SESSION_JOINED": "session_joined",
    "END_SESSION": "end_session",
    "SESSION_ENDED": "session_ended",
    
    # State management
    "GET_STATE": "get_state",
    "STATE_UPDATE": "state_update",
    "STATE_DELTA": "state_delta",
    
    # Training rounds
    "DO_ROUND": "do_round",
    "ROUND_COMPLETED": "round_completed",
    
    # User input
    "PROCESS_INPUT": "process_input",
    "INPUT_PROCESSED": "input_processed",
    
    # Module-specific
    "GET_SEQUENCE": "get_sequence",
    "SEQUENCE": "sequence",
    
    # Error handling
    "ERROR": "error"
}

# Delta encoding utilities
def compute_delta(old_state, new_state):
    """Compute the delta between two states.
    
    Args:
        old_state: Previous state dictionary
        new_state: Current state dictionary
        
    Returns:
        Delta dictionary with only changed values
    """
    if not old_state:
        return new_state
        
    delta = {}
    for key, value in new_state.items():
        if key not in old_state or old_state[key] != value:
            delta[key] = value
    
    return delta

def apply_delta(base_state, delta):
    """Apply a delta to a base state.
    
    Args:
        base_state: Base state dictionary
        delta: Delta dictionary with changes
        
    Returns:
        Updated state dictionary
    """
    result = base_state.copy()
    result.update(delta)
    return result

# Lazy import for TrainingModule to avoid circular import issues
# Use: from core.training_module import TrainingModule
# Or the lazy accessor: core.get_training_module_class()

_training_module_class = None

def get_training_module_class():
    """Lazy accessor for TrainingModule class."""
    global _training_module_class
    if _training_module_class is None:
        from .training_module import TrainingModule
        _training_module_class = TrainingModule
    return _training_module_class

# Also provide direct access for backwards compatibility
# This import happens after the functions are defined
try:
    from .training_module import TrainingModule
except ImportError:
    TrainingModule = None

__all__ = [
    'TrainingModule',
    'get_training_module_class',
    'compute_delta',
    'apply_delta',
    'PROTOCOL_VERSION',
    'MESSAGE_TYPES'
] 