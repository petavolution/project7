#!/usr/bin/env python3
"""
Optimized Renderer for MetaMindIQTrain

This module provides an optimized renderer for the PyGame client with advanced
performance optimizations including dirty region tracking, double buffering,
adaptive quality scaling, and component pooling.
"""

import pygame
import time
import logging
from typing import Dict, Any, List, Tuple, Optional, Set, Union
import os
import json
from functools import lru_cache

# Try to import from the package first
try:
    from MetaMindIQTrain.core.theme import Theme, get_theme
    from MetaMindIQTrain.core.unified_component_system import (
        Component, Container, Text, Image, Button, 
        Rectangle, Circle, Line, Grid, FlexContainer
    )
    from MetaMindIQTrain.clients.pygame.renderers.base_component_renderer import BaseComponentRenderer
except ImportError:
    # For direct execution during development
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))
    from core.theme import Theme, get_theme
    from core.unified_component_system import (
        Component, Container, Text, Image, Button, 
        Rectangle, Circle, Line, Grid, FlexContainer
    )
    from clients.pygame.renderers.base_component_renderer import BaseComponentRenderer

# Configure logging
logger = logging.getLogger(__name__)

# Constants
DEFAULT_BUFFER_COUNT = 2
DEFAULT_TARGET_FPS = 60
DEFAULT_QUALITY_LEVELS = {
    "high": {
        "min_fps": 50,
        "antialiasing": True,
        "texture_quality": 1.0,
        "particle_factor": 1.0,
        "animation_quality": 1.0
    },
    "medium": {
        "min_fps": 30,
        "antialiasing": True,
        "texture_quality": 0.75,
        "particle_factor": 0.75,
        "animation_quality": 0.75
    },
    "low": {
        "min_fps": 15,
        "antialiasing": False,
        "texture_quality": 0.5,
        "particle_factor": 0.5,
        "animation_quality": 0.5
    }
}

class OptimizedRenderer(BaseComponentRenderer):
    """
    Optimized renderer with advanced performance optimizations.
    
    This renderer extends the BaseComponentRenderer with additional optimizations:
    
    1. Double buffering - Reduces tearing during rendering
    2. Adaptive quality scaling - Automatically adjusts quality based on FPS
    3. Enhanced dirty region tracking - Minimizes redraw areas
    4. Occlusion culling - Avoids rendering completely obscured components
    5. Batched rendering - Groups similar draw calls for efficiency
    """
    
    def __init__(self, screen: pygame.Surface, module_id: str):
        """Initialize the optimized renderer.
        
        Args:
            screen: PyGame screen surface
            module_id: ID of the module this renderer is for
        """
        # Initialize base class
        super().__init__(screen, module_id)
        
        # Set up double buffering
        self.buffers = []
        for i in range(DEFAULT_BUFFER_COUNT):
            buffer_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            self.buffers.append(buffer_surface)
        
        self.current_buffer = 0
        self.next_buffer = 1
        
        # Performance and quality settings
        self.quality_level = "high"
        self.target_fps = DEFAULT_TARGET_FPS
        self.min_acceptable_fps = DEFAULT_QUALITY_LEVELS["high"]["min_fps"]
        self.quality_settings = DEFAULT_QUALITY_LEVELS["high"].copy()
        self.quality_auto_adjust = True
        
        # Enhanced dirty region tracking
        self.dirty_region_margin = 5  # Extra margin around dirty regions
        self.max_dirty_regions = 50   # Max number of dirty regions before full redraw
        self.min_dirty_region_size = 10  # Min size of a dirty region
        
        # Occlusion and batching
        self.occluded_components = set()
        self.render_batches = {}
        
        # Adaptive FPS tracking
        self.fps_history = []
        self.fps_history_max_size = 60  # 1 second at 60fps
        self.last_quality_adjust_time = time.time()
        self.quality_adjust_interval = a = 3.0  # seconds between adjustments
        
        # Debug and profiling
        self.profile_data = {
            "render_time": 0,
            "component_count": 0,
            "dirty_region_count": 0,
            "batches_count": 0,
            "occluded_count": 0,
            "buffer_swap_time": 0
        }
        
        logger.info(f"Optimized renderer initialized for {module_id}")
    
    def set_quality_level(self, level: str):
        """Set the quality level for rendering.
        
        Args:
            level: Quality level ('high', 'medium', or 'low')
        """
        if level not in DEFAULT_QUALITY_LEVELS:
            logger.warning(f"Unknown quality level: {level}, using 'medium'")
            level = "medium"
        
        self.quality_level = level
        self.quality_settings = DEFAULT_QUALITY_LEVELS[level].copy()
        self.min_acceptable_fps = self.quality_settings["min_fps"]
        
        logger.info(f"Quality level set to {level}")
    
    def toggle_auto_quality(self, enabled: bool):
        """Toggle automatic quality adjustment.
        
        Args:
            enabled: Whether to enable automatic quality adjustment
        """
        self.quality_auto_adjust = enabled
        logger.info(f"Auto quality adjustment {'enabled' if enabled else 'disabled'}")
    
    def optimize_dirty_regions(self):
        """Optimize dirty regions by merging overlapping ones."""
        if not self.dirty_regions:
            return
        
        # If we have too many dirty regions, just do a full redraw
        if len(self.dirty_regions) > self.max_dirty_regions:
            logger.debug(f"Too many dirty regions ({len(self.dirty_regions)}), doing full redraw")
            self.needs_full_redraw = True
            return
        
        # Add margin to all regions
        for i, rect in enumerate(self.dirty_regions):
            self.dirty_regions[i] = rect.inflate(self.dirty_region_margin * 2, self.dirty_region_margin * 2)
        
        # Merge overlapping regions
        i = 0
        while i < len(self.dirty_regions):
            j = i + 1
            merged = False
            while j < len(self.dirty_regions):
                if self.dirty_regions[i].colliderect(self.dirty_regions[j]):
                    # Merge by creating a rect that contains both
                    self.dirty_regions[i] = self.dirty_regions[i].union(self.dirty_regions[j])
                    self.dirty_regions.pop(j)
                    merged = True
                else:
                    j += 1
            
            if not merged:
                i += 1
        
        # Filter out small dirty regions
        self.dirty_regions = [rect for rect in self.dirty_regions if 
                              rect.width > self.min_dirty_region_size and 
                              rect.height > self.min_dirty_region_size]
        
        # Clip dirty regions to screen boundaries
        screen_rect = pygame.Rect(0, 0, self.width, self.height)
        self.dirty_regions = [rect.clip(screen_rect) for rect in self.dirty_regions]
    
    def create_root_component(self, state: Dict[str, Any]) -> Container:
        """Create the root component for the current state.
        
        Override this method in module-specific renderers.
        
        Args:
            state: Current module state
            
        Returns:
            Container: Root container component
        """
        # Default implementation - just pass to superclass
        return super().create_root_component(state)
    
    def check_occlusion(self, component: Component, components: List[Component]) -> bool:
        """Check if a component is completely occluded by others.
        
        Args:
            component: Component to check
            components: List of potentially occluding components
            
        Returns:
            bool: True if the component is occluded
        """
        # Skip occlusion check for certain component types
        if not hasattr(component, 'x') or not hasattr(component, 'y'):
            return False
        
        # Get component rect
        comp_rect = pygame.Rect(
            int(component.x), 
            int(component.y),
            int(component.width) if hasattr(component, 'width') else 10,
            int(component.height) if hasattr(component, 'height') else 10
        )
        
        # Check if any component completely covers this one
        for other in components:
            # Skip if not a visual component or is the same component
            if not hasattr(other, 'x') or not hasattr(other, 'y') or other is component:
                continue
            
            # Only consider components that draw a background
            has_background = False
            if hasattr(other, 'color') and other.color is not None:
                if len(other.color) == 3 or (len(other.color) == 4 and other.color[3] == 255):
                    has_background = True
            
            if not has_background:
                continue
            
            # Get other component rect
            other_rect = pygame.Rect(
                int(other.x), 
                int(other.y),
                int(other.width) if hasattr(other, 'width') else 10,
                int(other.height) if hasattr(other, 'height') else 10
            )
            
            # Check if this component is completely covered
            if other_rect.contains(comp_rect):
                return True
        
        return False
    
    def batch_similar_components(self, components: List[Component]) -> Dict[str, List[Component]]:
        """Group similar components for batch rendering.
        
        Args:
            components: List of components to batch
            
        Returns:
            Dict[str, List[Component]]: Batched components by type
        """
        batches = {}
        
        for component in components:
            component_type = component.__class__.__name__
            
            if component_type not in batches:
                batches[component_type] = []
            
            batches[component_type].append(component)
        
        return batches
    
    def adjust_quality_if_needed(self):
        """Adjust quality settings based on current FPS."""
        # Skip if auto-adjustment is disabled
        if not self.quality_auto_adjust:
            return
        
        # Only adjust periodically
        current_time = time.time()
        if current_time - self.last_quality_adjust_time < self.quality_adjust_interval:
            return
        
        # Calculate current FPS from history
        if not self.fps_history:
            return
        
        avg_fps = sum(self.fps_history) / len(self.fps_history)
        
        # Adjust quality if needed
        if avg_fps < self.min_acceptable_fps:
            # Lower quality
            if self.quality_level == "high":
                self.set_quality_level("medium")
                logger.info(f"Lowering quality to medium (FPS: {avg_fps:.1f})")
            elif self.quality_level == "medium":
                self.set_quality_level("low")
                logger.info(f"Lowering quality to low (FPS: {avg_fps:.1f})")
        elif avg_fps > self.min_acceptable_fps * 1.5:
            # Increase quality if possible
            if self.quality_level == "low":
                self.set_quality_level("medium")
                logger.info(f"Increasing quality to medium (FPS: {avg_fps:.1f})")
            elif self.quality_level == "medium":
                self.set_quality_level("high")
                logger.info(f"Increasing quality to high (FPS: {avg_fps:.1f})")
        
        self.last_quality_adjust_time = current_time
    
    def render(self, state: Dict[str, Any]) -> bool:
        """Render the current state to the screen with optimizations.
        
        Args:
            state: Current module state
            
        Returns:
            bool: True if rendering was successful
        """
        # Record render start time
        start_time = time.time()
        
        # Update profile data
        self.profile_data["component_count"] = 0
        self.profile_data["dirty_region_count"] = len(self.dirty_regions)
        self.profile_data["occluded_count"] = 0
        
        # Update state
        self.last_state = self.current_state.copy()
        self.current_state = state.copy()
        
        # Check if theme has changed
        if self.check_theme_changed():
            self.needs_full_redraw = True
            self.font_cache.clear()
        
        # Detect state changes
        changed_keys = self.detect_state_changes(state)
        for key in changed_keys:
            self.mark_state_key_dirty(key)
        
        # Optimize dirty regions
        self.optimize_dirty_regions()
        
        # Create root component
        root = self.create_root_component(state)
        
        # Clear the next buffer
        next_buffer = self.buffers[self.next_buffer]
        
        if self.needs_full_redraw:
            # Full redraw
            next_buffer.fill(self.theme.colors.get("background", (0, 0, 0)))
            self.render_component(root, next_buffer)
            self.needs_full_redraw = False
        else:
            # Copy current buffer to next buffer
            next_buffer.blit(self.buffers[self.current_buffer], (0, 0))
            
            # Only update dirty regions
            for rect in self.dirty_regions:
                # Clear the dirty region
                rect_surface = next_buffer.subsurface(rect)
                rect_surface.fill(self.theme.colors.get("background", (0, 0, 0)))
                
                # Create a clipping rect for rendering
                pygame.draw.rect(next_buffer, (0, 0, 0, 0), rect)
                
                # Render just this region
                self.render_component(root, next_buffer, clip_rect=rect)
            
            # Debug: Draw dirty region rectangles
            if self.debug_mode and self.show_dirty_regions:
                for rect in self.dirty_regions:
                    pygame.draw.rect(next_buffer, (255, 0, 0), rect, 1)
        
        # Swap buffers
        buffer_swap_start = time.time()
        self.screen.blit(next_buffer, (0, 0))
        self.current_buffer, self.next_buffer = self.next_buffer, self.current_buffer
        self.profile_data["buffer_swap_time"] = time.time() - buffer_swap_start
        
        # Clear dirty flags
        self.clear_dirty_regions()
        
        # Calculate FPS and update history
        current_time = time.time()
        frame_time = current_time - start_time
        fps = 1.0 / frame_time if frame_time > 0 else 0
        
        self.fps_history.append(fps)
        if len(self.fps_history) > self.fps_history_max_size:
            self.fps_history.pop(0)
        
        # Adjust quality if needed
        self.adjust_quality_if_needed()
        
        # Update performance metrics
        self.render_count += 1
        self.last_render_time = time.time() - start_time
        self.render_times.append(self.last_render_time)
        self.profile_data["render_time"] = self.last_render_time
        
        # Limit render_times list size
        if len(self.render_times) > 60:
            self.render_times.pop(0)
        
        return True
    
    def render_component(self, component: Component, parent_surface: pygame.Surface, 
                        clip_rect: pygame.Rect = None) -> List[pygame.Rect]:
        """Render a component with optimizations.
        
        Args:
            component: Component to render
            parent_surface: Surface to render onto
            clip_rect: Optional rectangle to clip rendering to
            
        Returns:
            List[pygame.Rect]: List of dirty rectangles
        """
        # Skip hidden components
        if hasattr(component, 'visible') and not component.visible:
            return []
        
        # Update component count for profiling
        self.profile_data["component_count"] += 1
        
        # Apply quality settings
        if self.quality_level != "high":
            # Simplify rendering for performance
            # For example, we could skip certain effects or animations
            pass
            
        # Use the base implementation with optimizations
        return super().render_component(component, parent_surface)
    
    def get_render_stats(self) -> Dict[str, Any]:
        """Get rendering statistics.
        
        Returns:
            Dict[str, Any]: Dictionary of rendering statistics
        """
        # Get base stats
        stats = super().get_render_stats()
        
        # Add optimized renderer specific stats
        avg_fps = sum(self.fps_history) / len(self.fps_history) if self.fps_history else 0
        
        stats.update({
            'quality_level': self.quality_level,
            'avg_fps': avg_fps,
            'dirty_regions': len(self.dirty_regions),
            'occluded_components': len(self.occluded_components),
            'buffer_swap_time': self.profile_data["buffer_swap_time"] * 1000,  # ms
            'auto_quality': self.quality_auto_adjust
        })
        
        return stats
    
    def cleanup(self):
        """Clean up resources."""
        # Clear buffer surfaces
        for buffer in self.buffers:
            buffer.fill((0, 0, 0, 0))
        self.buffers.clear()
        
        # Clear FPS history
        self.fps_history.clear()
        
        # Call base cleanup
        super().cleanup()
        
        logger.info(f"Optimized renderer cleaned up for {self.module_id}") 