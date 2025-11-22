#!/usr/bin/env python3
"""
State Manager

This module provides a unified state management system with automatic delta encoding
for efficient state updates and synchronization between server and client.
"""

import logging
import uuid
from typing import Dict, Any, List, Optional
from .component_system import UniversalComponent

logger = logging.getLogger(__name__)

class StateManager:
    """Unified state management with automatic delta encoding"""
    
    def __init__(self):
        """Initialize the state manager."""
        self.components = {}
        self.session_id = str(uuid.uuid4())
        logger.info(f"State manager initialized with session ID: {self.session_id}")
        
    def register_component(self, component: UniversalComponent) -> None:
        """Register a component with the state manager.
        
        Args:
            component: The component to register
        """
        self.components[component.id] = component
        logger.debug(f"Registered component: {component.id} of type {component.type}")
        
    def create_component(self, component_type: str, component_id: Optional[str] = None, 
                        initial_state: Optional[Dict[str, Any]] = None) -> str:
        """Create and register a new component.
        
        Args:
            component_type: Type of component to create
            component_id: Optional ID for the component (generated if not provided)
            initial_state: Initial state for the component
            
        Returns:
            ID of the created component
        """
        # Generate ID if not provided
        if component_id is None:
            component_id = f"{component_type}_{str(uuid.uuid4())[:8]}"
            
        # Create component
        component = UniversalComponent(component_id, component_type)
        
        # Add initial state if provided
        if initial_state:
            component.update(initial_state)
            
        # Register the component
        self.register_component(component)
        
        return component_id
        
    def update_component(self, component_id: str, state_update: Dict[str, Any]) -> bool:
        """Update a component's state.
        
        Args:
            component_id: ID of the component to update
            state_update: New state properties to apply
            
        Returns:
            True if component was updated, False if not found
        """
        if component_id in self.components:
            self.components[component_id].update(state_update)
            return True
        else:
            logger.warning(f"Attempted to update unknown component: {component_id}")
            return False
            
    def remove_component(self, component_id: str) -> bool:
        """Remove a component from the state manager.
        
        Args:
            component_id: ID of the component to remove
            
        Returns:
            True if component was removed, False if not found
        """
        if component_id in self.components:
            del self.components[component_id]
            logger.debug(f"Removed component: {component_id}")
            return True
        else:
            logger.warning(f"Attempted to remove unknown component: {component_id}")
            return False
            
    def get_full_state(self) -> Dict[str, Dict[str, Any]]:
        """Get the complete state of all components.
        
        Returns:
            Dictionary mapping component IDs to their full states
        """
        return {cid: comp.get_full_state() for cid, comp in self.components.items()}
        
    def get_delta_state(self) -> Dict[str, Dict[str, Any]]:
        """Get only the components and properties that have changed.
        
        Returns:
            Dictionary mapping component IDs to their changed properties
        """
        delta = {cid: comp.get_delta() for cid, comp in self.components.items() 
                if comp.has_changes}
        
        if delta:
            logger.debug(f"Generated delta with {len(delta)} changed components")
            
        return delta
        
    def reset_delta_tracking(self) -> None:
        """Reset delta tracking for all components."""
        for component in self.components.values():
            component.reset_delta_tracking()
        
        logger.debug("Reset delta tracking for all components")
        
    def get_components_by_type(self, component_type: str) -> List[UniversalComponent]:
        """Get all components of a specific type.
        
        Args:
            component_type: Type of components to retrieve
            
        Returns:
            List of components of the specified type
        """
        return [comp for comp in self.components.values() if comp.type == component_type]
        
    def clear(self) -> None:
        """Remove all components from the state manager."""
        self.components.clear()
        logger.info("Cleared all components from state manager") 