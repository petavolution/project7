#!/usr/bin/env python3
"""
Scaling Helper for Resolution-Independent UI

This module provides a scaling helper class to ensure UI elements scale
properly across different screen resolutions, maintaining consistent
appearance and proportions.
"""

import logging
from typing import Tuple, Union, List, Dict, Any

logger = logging.getLogger(__name__)

class ScalingHelper:
    """
    Helper class for resolution-independent UI scaling.
    
    This class provides methods to scale positions, sizes, and other values
    based on the current screen resolution relative to a reference resolution.
    This ensures consistent UI appearance across different screen sizes.
    """
    
    def __init__(self, scale_x=1.0, scale_y=1.0):
        """Initialize the scaling helper.
        
        Args:
            scale_x: Initial horizontal scale factor (default: 1.0)
            scale_y: Initial vertical scale factor (default: 1.0)
        """
        self.scale_x = scale_x
        self.scale_y = scale_y
        self.default_scale = 1.0
        self.current_width = 0
        self.current_height = 0
        self.reference_width = 0
        self.reference_height = 0
        
        logger.debug(f"ScalingHelper initialized with scale_x={scale_x}, scale_y={scale_y}")
    
    def update_scale_factors(self, 
                           current_width: int, 
                           current_height: int, 
                           reference_width: int = 1440, 
                           reference_height: int = 1024) -> None:
        """Update scale factors based on current and reference dimensions.
        
        Args:
            current_width: Current screen width
            current_height: Current screen height
            reference_width: Reference design width (default: 1440)
            reference_height: Reference design height (default: 1024)
        """
        self.current_width = current_width
        self.current_height = current_height
        self.reference_width = reference_width
        self.reference_height = reference_height
        
        self.scale_x = current_width / reference_width
        self.scale_y = current_height / reference_height
        # Use the smaller scale for default scale to prevent UI elements from being too large
        self.default_scale = min(self.scale_x, self.scale_y)
        
        logger.debug(
            f"Scale factors updated: scale_x={self.scale_x}, scale_y={self.scale_y}, "
            f"default_scale={self.default_scale}"
        )
    
    def scale_pos(self, pos: Tuple[float, float]) -> Tuple[float, float]:
        """Scale a position coordinate.
        
        Args:
            pos: (x, y) position tuple
            
        Returns:
            Scaled position tuple
        """
        return (pos[0] / self.scale_x, pos[1] / self.scale_y)
    
    def scale_size(self, size: Tuple[float, float]) -> Tuple[float, float]:
        """Scale a size dimension.
        
        Args:
            size: (width, height) size tuple
            
        Returns:
            Scaled size tuple
        """
        return (size[0] * self.scale_x, size[1] * self.scale_y)
    
    def scale_font_size(self, size: float) -> float:
        """Scale a font size.
        
        Args:
            size: Original font size
            
        Returns:
            Scaled font size
        """
        return size * self.default_scale
    
    def scale_value(self, value: float) -> float:
        """Scale a single value using the default scale factor.
        
        Args:
            value: Original value
            
        Returns:
            Scaled value
        """
        return value * self.default_scale
    
    def maintain_aspect_ratio(self, 
                            original_width: float, 
                            original_height: float, 
                            target_width: float = None, 
                            target_height: float = None) -> Tuple[float, float]:
        """Calculate dimensions that maintain the original aspect ratio.
        
        Args:
            original_width: Original width
            original_height: Original height
            target_width: Target width (if None, will be calculated from target_height)
            target_height: Target height (if None, will be calculated from target_width)
            
        Returns:
            (width, height) tuple with adjusted dimensions
        """
        aspect_ratio = original_width / original_height
        
        if target_width is not None and target_height is None:
            # Calculate height from width
            return (target_width, target_width / aspect_ratio)
        elif target_height is not None and target_width is None:
            # Calculate width from height
            return (target_height * aspect_ratio, target_height)
        elif target_width is not None and target_height is not None:
            # Use the constraining dimension
            target_ratio = target_width / target_height
            
            if target_ratio > aspect_ratio:
                # Height is the constraint
                return (target_height * aspect_ratio, target_height)
            else:
                # Width is the constraint
                return (target_width, target_width / aspect_ratio)
        else:
            # If no target dimensions provided, use the original
            return (original_width, original_height)
    
    def get_centered_position(self, 
                            container_width: float, 
                            container_height: float,
                            element_width: float, 
                            element_height: float) -> Tuple[float, float]:
        """Calculate the position to center an element in a container.
        
        Args:
            container_width: Width of the container
            container_height: Height of the container
            element_width: Width of the element to center
            element_height: Height of the element to center
            
        Returns:
            (x, y) position tuple for centered element
        """
        x = (container_width - element_width) / 2
        y = (container_height - element_height) / 2
        return (x, y) 