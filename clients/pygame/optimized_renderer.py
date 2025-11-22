#!/usr/bin/env python3
"""
Optimized Renderer for PyGame

This module provides an optimized renderer for PyGame that uses the component-based
rendering system with additional performance optimizations:
- Surface caching
- Dirty region rendering
- Component pooling
- Efficient theme integration
- Adaptive rendering based on frame rate

This renderer serves as a bridge between module-specific renderers and the
base component renderer infrastructure.
"""

import pygame
import logging
import time
from typing import Dict, Any, List, Tuple, Optional, Union

# Try to import from the package first
try:
    from MetaMindIQTrain.core.theme import Theme, get_theme, set_theme
    from MetaMindIQTrain.core.unified_component_system import Component, ComponentFactory, UI
    from MetaMindIQTrain.clients.pygame.renderers.base_component_renderer import BaseComponentRenderer
except ImportError:
    # For direct execution during development
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))
    from core.theme import Theme, get_theme, set_theme
    from core.unified_component_system import Component, ComponentFactory, UI
    from clients.pygame.renderers.base_component_renderer import BaseComponentRenderer

# Configure logging
logger = logging.getLogger(__name__)

class OptimizedRenderer(BaseComponentRenderer):
    """Optimized renderer with performance optimizations."""
    
    def __init__(self, screen, module_id=None, title_font=None, regular_font=None, 
                 small_font=None, colors=None, width=None, height=None):
        """Initialize the optimized renderer.
        
        Args:
            screen: PyGame screen surface
            module_id: Module ID (optional)
            title_font: Font for titles (optional)
            regular_font: Font for regular text (optional)
            small_font: Font for small text (optional)
            colors: Dictionary of colors (optional)
            width: Screen width (optional)
            height: Screen height (optional)
        """
        # Initialize base renderer
        super().__init__(screen, module_id, title_font, regular_font, small_font, colors, width, height)
        
        # Rendering optimizations
        self.dirty_regions = []
        self.full_redraw_needed = True
        self.previous_components = {}
        self.components_to_render = {}
        self.background_surface = None
        
        # Performance tracking
        self.frame_times = []
        self.max_frame_times = 60  # Track last 60 frames
        self.target_fps = 60
        self.current_quality = 1.0  # Quality scaling factor (1.0 = full quality)
        self.last_quality_adjust = time.time()
        self.quality_adjust_interval = 5.0  # Seconds between quality adjustments
        
        # Double buffering
        self.buffer_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        
        # Create static background once
        self._create_background()
    
    def _create_background(self):
        """Create a static background for the renderer."""
        # Create background surface
        self.background_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        
        # Draw base background
        background_color = self.colors.get('background', (30, 30, 30))
        self.background_surface.fill(background_color)
        
        # Draw gradient if available in theme
        theme = get_theme()
        if theme and theme.has_gradient('background'):
            start_color, end_color = theme.get_gradient('background')
            self._draw_gradient_background(self.background_surface, start_color, end_color)
    
    def _draw_gradient_background(self, surface, start_color, end_color, direction='vertical'):
        """Draw a gradient background.
        
        Args:
            surface: Surface to draw on
            start_color: Start color of gradient
            end_color: End color of gradient
            direction: 'vertical' or 'horizontal'
        """
        width, height = surface.get_width(), surface.get_height()
        
        if direction == 'horizontal':
            for x in range(width):
                progress = x / width
                color = self._interpolate_color(start_color, end_color, progress)
                pygame.draw.line(surface, color, (x, 0), (x, height))
        else:  # vertical
            for y in range(height):
                progress = y / height
                color = self._interpolate_color(start_color, end_color, progress)
                pygame.draw.line(surface, color, (0, y), (width, y))
    
    def _interpolate_color(self, start_color, end_color, progress):
        """Interpolate between two colors.
        
        Args:
            start_color: Start color
            end_color: End color
            progress: Progress from 0.0 to 1.0
            
        Returns:
            Interpolated color
        """
        r = int(start_color[0] + (end_color[0] - start_color[0]) * progress)
        g = int(start_color[1] + (end_color[1] - start_color[1]) * progress)
        b = int(start_color[2] + (end_color[2] - start_color[2]) * progress)
        
        if len(start_color) > 3 and len(end_color) > 3:
            a = int(start_color[3] + (end_color[3] - start_color[3]) * progress)
            return (r, g, b, a)
        
        return (r, g, b)
    
    def register_dirty_region(self, region):
        """Register a region that needs to be redrawn.
        
        Args:
            region: Rect representing the dirty region
        """
        self.dirty_regions.append(region)
    
    def register_component_update(self, component_id, component):
        """Register a component that needs to be updated.
        
        Args:
            component_id: Unique ID of the component
            component: Component object
        """
        self.components_to_render[component_id] = component
        
        # Mark region as dirty
        region = pygame.Rect(
            component.layout['x'],
            component.layout['y'],
            component.layout['width'],
            component.layout['height']
        )
        self.register_dirty_region(region)
    
    def clear_updates(self):
        """Clear all pending updates."""
        self.dirty_regions.clear()
        self.components_to_render.clear()
        self.full_redraw_needed = False
    
    def force_full_redraw(self):
        """Force a full redraw on the next render."""
        self.full_redraw_needed = True
        
        # Clear the component cache to ensure fresh rendering
        self.cache.clear()
    
    def _optimize_dirty_regions(self):
        """Optimize dirty regions by merging overlapping rectangles."""
        if not self.dirty_regions:
            return []
        
        # Start with the first region
        optimized = [self.dirty_regions[0]]
        
        for region in self.dirty_regions[1:]:
            merged = False
            for i, existing in enumerate(optimized):
                # If regions are close, merge them
                if region.colliderect(existing) or region.inflate(20, 20).colliderect(existing):
                    optimized[i] = existing.union(region)
                    merged = True
                    break
            
            if not merged:
                optimized.append(region)
        
        return optimized
    
    def _adjust_quality(self):
        """Adjust rendering quality based on performance."""
        now = time.time()
        
        # Check if it's time to adjust quality
        if now - self.last_quality_adjust < self.quality_adjust_interval:
            return
        
        # Calculate average FPS
        if len(self.frame_times) > 10:
            avg_frame_time = sum(self.frame_times) / len(self.frame_times)
            current_fps = 1.0 / avg_frame_time if avg_frame_time > 0 else 0
            
            # Adjust quality based on FPS
            if current_fps < self.target_fps * 0.8 and self.current_quality > 0.5:
                # Reduce quality if FPS is below 80% of target
                self.current_quality = max(0.5, self.current_quality - 0.1)
                logger.info(f"Reducing render quality to {self.current_quality:.1f} (FPS: {current_fps:.1f})")
            elif current_fps > self.target_fps * 0.95 and self.current_quality < 1.0:
                # Increase quality if FPS is above 95% of target
                self.current_quality = min(1.0, self.current_quality + 0.1)
                logger.info(f"Increasing render quality to {self.current_quality:.1f} (FPS: {current_fps:.1f})")
        
        self.last_quality_adjust = now
    
    def _record_frame_time(self, frame_time):
        """Record a frame time for performance tracking.
        
        Args:
            frame_time: Time taken to render the frame
        """
        self.frame_times.append(frame_time)
        
        # Keep only the last N frames
        if len(self.frame_times) > self.max_frame_times:
            self.frame_times.pop(0)
        
        # Calculate FPS
        if len(self.frame_times) > 0:
            avg_frame_time = sum(self.frame_times) / len(self.frame_times)
            self.fps = 1.0 / avg_frame_time if avg_frame_time > 0 else 0
    
    def render(self, state):
        """Render the current state.
        
        Args:
            state: Current state object
            
        Returns:
            List of updated regions
        """
        # Start timing
        start_time = time.time()
        
        # Adjust quality based on performance
        self._adjust_quality()
        
        # Prepare for rendering
        ui = self.create_ui(state)
        
        # If quality is less than 1.0, scale down rendering
        if self.current_quality < 1.0:
            scaled_width = int(self.width * self.current_quality)
            scaled_height = int(self.height * self.current_quality)
            buffer = pygame.Surface((scaled_width, scaled_height), pygame.SRCALPHA)
        else:
            buffer = self.buffer_surface
        
        # Check if we need a full redraw
        if self.full_redraw_needed:
            # Draw background first
            buffer.blit(self.background_surface, (0, 0))
            
            # Render all components
            self._render_all_components(ui, buffer)
            
            # Full screen is dirty
            updated_regions = [pygame.Rect(0, 0, self.width, self.height)]
        else:
            # Copy background to buffer for the dirty regions only
            optimized_regions = self._optimize_dirty_regions()
            
            for region in optimized_regions:
                # Draw background in dirty region
                buffer.blit(self.background_surface, region, region)
                
                # Render components that intersect with this region
                self._render_components_in_region(ui, buffer, region)
            
            updated_regions = optimized_regions
        
        # Scaling back up if needed
        if self.current_quality < 1.0:
            # Scale buffer back to full size
            pygame.transform.scale(buffer, (self.width, self.height), self.buffer_surface)
            
            # Use full buffer for rendering
            buffer = self.buffer_surface
            
            # Entire screen is updated when scaling
            updated_regions = [pygame.Rect(0, 0, self.width, self.height)]
        
        # Draw buffer to screen
        self.screen.blit(buffer, (0, 0))
        
        # Update display for dirty regions
        if len(updated_regions) > 0:
            pygame.display.update(updated_regions)
        
        # Record stats
        end_time = time.time()
        self.last_render_time = end_time - start_time
        self._record_frame_time(self.last_render_time)
        self.frame_count += 1
        
        # Clear dirty regions
        self.clear_updates()
        
        return updated_regions
    
    def _render_all_components(self, ui, buffer):
        """Render all components in the UI.
        
        Args:
            ui: UI object with components
            buffer: Surface to render on
        """
        # Render all components
        for component in ui.components:
            # Render component and its children
            surface = self.render_component_tree(component)
            
            # Blit to buffer
            buffer.blit(surface, (component.layout['x'], component.layout['y']))
    
    def _render_components_in_region(self, ui, buffer, region):
        """Render components that intersect with a region.
        
        Args:
            ui: UI object with components
            buffer: Surface to render on
            region: Rect representing the region to render
        """
        # Find components that intersect with the region
        for component in ui.components:
            component_rect = pygame.Rect(
                component.layout['x'],
                component.layout['y'],
                component.layout['width'],
                component.layout['height']
            )
            
            if component_rect.colliderect(region):
                # Render component and its children
                surface = self.render_component_tree(component)
                
                # Blit to buffer
                buffer.blit(surface, (component.layout['x'], component.layout['y']))
    
    def create_ui(self, state):
        """Create a UI from the current state.
        
        Args:
            state: Current state object
            
        Returns:
            UI object with components
        """
        # Create a new UI
        ui = UI(self.width, self.height)
        
        # Add standard layout components
        self._add_layout_components(ui, state)
        
        # Add module-specific components
        self._add_module_components(ui, state)
        
        return ui
    
    def _add_layout_components(self, ui, state):
        """Add standard layout components to the UI.
        
        Args:
            ui: UI object to add components to
            state: Current state object
        """
        # Add header
        header = self.component_factory.container(
            x=0, 
            y=0, 
            width=self.width, 
            height=self.layout['header_rect'].height
        )
        ui.add(header)
        
        # Add module title to header
        module_name = self.module_info.get('name', 'Module')
        title = self.component_factory.text(
            text=module_name,
            x=self.layout['padding']['medium'],
            y=0,
            width=self.width // 2,
            height=self.layout['header_rect'].height
        )
        header.add_child(title)
        
        # Add score if available
        if hasattr(state, 'score') or (isinstance(state, dict) and 'score' in state):
            score_value = state.score if hasattr(state, 'score') else state.get('score', 0)
            score = self.component_factory.text(
                text=f"Score: {score_value}",
                x=self.width - 200,
                y=0,
                width=180,
                height=self.layout['header_rect'].height,
                text_align='right'
            )
            header.add_child(score)
        
        # Add footer
        footer = self.component_factory.container(
            x=0, 
            y=self.height - self.layout['footer_rect'].height, 
            width=self.width, 
            height=self.layout['footer_rect'].height
        )
        ui.add(footer)
        
        # Add instructions in footer if available
        instructions = getattr(state, 'instructions', 
                              state.get('instructions', '') if isinstance(state, dict) else '')
        if instructions:
            instructions_text = self.component_factory.text(
                text=instructions,
                x=self.layout['padding']['medium'],
                y=0,
                width=self.width - (2 * self.layout['padding']['medium']),
                height=self.layout['footer_rect'].height,
                text_align='center'
            )
            footer.add_child(instructions_text)
    
    def _add_module_components(self, ui, state):
        """Add module-specific components to the UI.
        
        This method should be overridden by module-specific renderers.
        
        Args:
            ui: UI object to add components to
            state: Current state object
        """
        # This is a placeholder that should be overridden
        # For the base implementation, just add a message in the content area
        content_rect = self.layout['content_rect']
        
        message = self.component_factory.text(
            text=f"Module: {self.module_id if self.module_id else 'Unknown'}",
            x=content_rect.width // 4,
            y=content_rect.height // 3,
            width=content_rect.width // 2,
            height=40,
            text_align='center'
        )
        ui.add(message)
        
        # Add a message that this should be overridden
        if not self.module_id:
            hint = self.component_factory.text(
                text="Override _add_module_components to add module UI",
                x=content_rect.width // 4,
                y=content_rect.height // 2,
                width=content_rect.width // 2,
                height=30,
                text_align='center'
            )
            ui.add(hint)
    
    def handle_event(self, event, state):
        """Handle PyGame events.
        
        Args:
            event: PyGame event
            state: Current state object
            
        Returns:
            Updated state if changed, None otherwise
        """
        # Handle mouse events for components
        if event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEMOTION, pygame.MOUSEBUTTONUP):
            # Get mouse position
            pos = pygame.mouse.get_pos()
            
            # Create UI to check for component interactions
            ui = self.create_ui(state)
            
            # Check if any component was clicked
            for component in ui.components:
                result = self._check_component_interaction(component, event, pos, state)
                if result:
                    return result
        
        # Handle window resize
        if event.type == pygame.VIDEORESIZE:
            self.width, self.height = event.w, event.h
            self._setup_layout()
            self._create_background()
            self.force_full_redraw()
        
        return None
    
    def _check_component_interaction(self, component, event, pos, state, parent_x=0, parent_y=0):
        """Check if a component was interacted with.
        
        Args:
            component: Component to check
            event: PyGame event
            pos: Mouse position
            state: Current state object
            parent_x: X offset of parent component
            parent_y: Y offset of parent component
            
        Returns:
            Updated state if changed, None otherwise
        """
        # Calculate absolute position
        abs_x = parent_x + component.layout['x']
        abs_y = parent_y + component.layout['y']
        
        # Check if position is within component
        x, y = pos
        if (abs_x <= x < abs_x + component.layout['width'] and 
            abs_y <= y < abs_y + component.layout['height']):
            
            # Convert to relative position within component
            rel_x = x - abs_x
            rel_y = y - abs_y
            
            # Handle button clicks
            if component.type == 'button' and event.type == pygame.MOUSEBUTTONDOWN:
                # Check if onClick handler is available
                on_click = component.props.get('onClick')
                if on_click and callable(on_click):
                    # Call handler with state
                    return on_click(state)
            
            # Handle grid cell clicks
            if component.type == 'grid' and event.type == pygame.MOUSEBUTTONDOWN:
                # Calculate cell coordinates
                cols = component.props.get('cols', 3)
                rows = component.props.get('rows', 3)
                cell_width = component.layout['width'] / cols
                cell_height = component.layout['height'] / rows
                
                col = int(rel_x // cell_width)
                row = int(rel_y // cell_height)
                
                # Check if onCellClick handler is available
                on_cell_click = component.props.get('onCellClick')
                if on_cell_click and callable(on_cell_click):
                    # Call handler with state and cell coordinates
                    return on_cell_click(state, row, col)
            
            # Handle symbol cell clicks
            if component.type == 'symbol_cell' and event.type == pygame.MOUSEBUTTONDOWN:
                # Check if onClick handler is available
                on_click = component.props.get('onClick')
                if on_click and callable(on_click):
                    # Call handler with state
                    return on_click(state)
        
        # Check children
        for child in component.children:
            result = self._check_component_interaction(child, event, pos, state, abs_x, abs_y)
            if result:
                return result
        
        return None
    
    def cleanup(self):
        """Clean up resources used by the renderer."""
        # Clear caches
        self.clear_cache()
        
        # Release surfaces
        self.background_surface = None
        self.buffer_surface = None 