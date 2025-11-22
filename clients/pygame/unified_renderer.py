#!/usr/bin/env python3
"""
Unified Pygame Renderer for MetaMindIQTrain

This renderer works with the unified component system to provide
high-performance rendering with automatic optimization. It includes
surface caching, batch rendering, and efficient state management.

Key optimizations:
1. Surface caching for frequently rendered components
2. Batch rendering for similar component types
3. Dirty region tracking for partial screen updates
4. Rendered component pooling to reduce memory allocations
5. Adaptive scaling for any screen resolution
"""

import pygame
import time
import logging
import math
import json
import threading
from typing import Dict, List, Tuple, Any, Optional, Union, Set
from collections import defaultdict, OrderedDict

# Import the unified component system
import sys
import os
from pathlib import Path

# Add project root to path for imports when run directly
if __name__ == "__main__":
    project_root = Path(__file__).parent.parent.parent
    sys.path.insert(0, str(project_root))
    
# Import from unified component system
try:
    from MetaMindIQTrain.core.unified_component_system import (
        Component, UI, ComponentFactory, get_stats, reset_stats
    )
    from MetaMindIQTrain.core.theme import Theme, get_theme, set_theme
except ImportError:
    # For direct execution or during development
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))
    from core.unified_component_system import (
        Component, UI, ComponentFactory, get_stats, reset_stats
    )
    from core.theme import Theme, get_theme, set_theme

# Configure logging
logger = logging.getLogger(__name__)

# Default colors
DEFAULT_COLORS = {
    "background": (30, 36, 44),      # #1e242c - Dark blue/gray from web client
    "cell_background": (40, 44, 52), # #282c34 - Darker gray for cells
    "text": (255, 255, 255),         # White text
    "primary": (0, 120, 255),        # #0078ff - Blue accent color
    "secondary": (80, 80, 200),      # Secondary accent
    "accent": (255, 149, 0),         # #ff9500 - Orange accent color
    "warning": (255, 225, 50),       # #ffe132 - Yellow warning
    "error": (255, 50, 50),          # #ff3232 - Red error/incorrect
    "success": (50, 255, 50),        # #32ff32 - Green success/correct
    "border": (100, 100, 160),       # Border color for components
    "highlight": (255, 220, 115),    # #ffdc73 - Highlight color
    "hover": (50, 56, 66),           # Hover state for interactive elements
    "cell_highlight": (60, 120, 255, 180), # Highlighted cell with alpha
}

class SurfaceCache:
    """Cache for rendered component surfaces with optimized LRU eviction and memory management."""
    
    def __init__(self, max_size=1000, ttl=10.0, max_memory_mb=64):
        """Initialize the surface cache.
        
        Args:
            max_size: Maximum number of surfaces in the cache
            ttl: Time-to-live for cached surfaces in seconds
            max_memory_mb: Maximum memory usage in MB
        """
        self.surfaces = OrderedDict()  # LRU implementation via OrderedDict
        self.max_size = max_size
        self.ttl = ttl
        self.max_memory = max_memory_mb * 1024 * 1024  # Convert to bytes
        self.current_memory = 0
        self.hits = 0
        self.misses = 0
        self.evictions = 0
        self.lock = threading.RLock()
        
    def get(self, component_hash: str) -> Optional[pygame.Surface]:
        """Get a cached surface for a component hash.
        
        Args:
            component_hash: Hash of the component
            
        Returns:
            Cached surface or None if not found
        """
        with self.lock:
            if component_hash in self.surfaces:
                surface, timestamp = self.surfaces[component_hash]
                
                # Check if expired
                if time.time() - timestamp > self.ttl:
                    # Remove expired surface and update memory usage
                    self._remove_entry(component_hash)
                    self.misses += 1
                    return None
                
                # Move to end of OrderedDict (most recently used)
                self.surfaces.move_to_end(component_hash)
                self.hits += 1
                
                # Return a reference - caller should not modify
                return surface
            
            self.misses += 1
            return None
    
    def set(self, component_hash: str, surface: pygame.Surface) -> None:
        """Add a surface to the cache with memory accounting.
        
        Args:
            component_hash: Hash of the component
            surface: Rendered surface
        """
        with self.lock:
            # Calculate surface memory usage
            surface_memory = self._calculate_surface_memory(surface)
            
            # Check if we need to make space
            self._ensure_space(surface_memory)
            
            # If this hash already exists, remove it first to update memory accounting
            if component_hash in self.surfaces:
                self._remove_entry(component_hash)
            
            # Add to cache
            self.surfaces[component_hash] = (surface.copy(), time.time())
            self.current_memory += surface_memory
    
    def clear(self) -> None:
        """Clear the cache."""
        with self.lock:
            self.surfaces.clear()
            self.current_memory = 0
    
    def clean_expired(self) -> int:
        """Remove expired entries from the cache.
        
        Returns:
            Number of entries removed
        """
        with self.lock:
            current_time = time.time()
            expired_hashes = [
                h for h, (_, timestamp) in self.surfaces.items()
                if current_time - timestamp > self.ttl
            ]
            
            for h in expired_hashes:
                self._remove_entry(h)
                
            return len(expired_hashes)
    
    def _ensure_space(self, needed_memory: int) -> None:
        """Ensure there's enough space for a new surface.
        
        Args:
            needed_memory: Memory required for the new surface
        """
        # Check size limit
        while len(self.surfaces) >= self.max_size and self.surfaces:
            # Remove oldest item (first in OrderedDict)
            oldest = next(iter(self.surfaces))
            self._remove_entry(oldest)
            self.evictions += 1
        
        # Check memory limit
        while self.current_memory + needed_memory > self.max_memory and self.surfaces:
            # Remove oldest item (first in OrderedDict)
            oldest = next(iter(self.surfaces))
            self._remove_entry(oldest)
            self.evictions += 1
    
    def _remove_entry(self, hash_key: str) -> None:
        """Remove an entry and update memory accounting.
        
        Args:
            hash_key: Hash of the component to remove
        """
        if hash_key in self.surfaces:
            surface, _ = self.surfaces[hash_key]
            memory_used = self._calculate_surface_memory(surface)
            del self.surfaces[hash_key]
            self.current_memory -= memory_used
    
    def _calculate_surface_memory(self, surface: pygame.Surface) -> int:
        """Calculate approximate memory usage of a surface.
        
        Args:
            surface: Surface to calculate memory for
            
        Returns:
            Approximate memory usage in bytes
        """
        width, height = surface.get_size()
        bits_per_pixel = surface.get_bitsize()
        bytes_per_pixel = bits_per_pixel // 8 if bits_per_pixel >= 8 else 1
        
        # Calculate bytes including any trailing padding
        row_bytes = width * bytes_per_pixel
        if row_bytes % 4 != 0:  # Align to 4-byte boundary (common in GPU memory)
            row_bytes = (row_bytes + 3) & ~3
            
        return row_bytes * height
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics.
        
        Returns:
            Dictionary with cache statistics
        """
        with self.lock:
            total = self.hits + self.misses
            hit_rate = self.hits / total if total > 0 else 0
            return {
                'size': len(self.surfaces),
                'max_size': self.max_size,
                'memory_used_mb': self.current_memory / (1024 * 1024),
                'max_memory_mb': self.max_memory / (1024 * 1024),
                'ttl': self.ttl,
                'hits': self.hits,
                'misses': self.misses,
                'evictions': self.evictions,
                'hit_rate': hit_rate
            }

class SurfacePool:
    """Pool for reusing pygame surfaces to reduce memory allocations."""
    
    def __init__(self, max_size=100):
        """Initialize the surface pool.
        
        Args:
            max_size: Maximum number of surfaces in the pool
        """
        self.surfaces = defaultdict(list)  # (width, height, flags) -> [surfaces]
        self.max_size = max_size
        self.allocations = 0
        self.reuses = 0
        self.lock = threading.RLock()
    
    def get(self, width: int, height: int, flags: int = 0) -> pygame.Surface:
        """Get a surface from the pool or create a new one.
        
        Args:
            width: Surface width
            height: Surface height
            flags: Surface flags
            
        Returns:
            A pygame Surface
        """
        with self.lock:
            key = (width, height, flags)
            
            if key in self.surfaces and self.surfaces[key]:
                # Reuse existing surface
                surface = self.surfaces[key].pop()
                surface.fill((0, 0, 0, 0) if flags & pygame.SRCALPHA else (0, 0, 0))
                self.reuses += 1
                return surface
            
            # Create new surface
            self.allocations += 1
            return pygame.Surface((width, height), flags)
    
    def release(self, surface: pygame.Surface) -> None:
        """Return a surface to the pool.
        
        Args:
            surface: Surface to return
        """
        with self.lock:
            if surface is None:
                return
                
            key = (surface.get_width(), surface.get_height(), surface.get_flags())
            
            # Only add to pool if we have space
            if len(self.surfaces[key]) < self.max_size:
                self.surfaces[key].append(surface)
    
    def clear(self) -> None:
        """Clear the pool."""
        with self.lock:
            self.surfaces.clear()
            
    def get_stats(self) -> Dict[str, Any]:
        """Get pool statistics.
        
        Returns:
            Dictionary with pool statistics
        """
        with self.lock:
            total_surfaces = sum(len(surfaces) for surfaces in self.surfaces.values())
            total_ops = self.allocations + self.reuses
            reuse_rate = self.reuses / total_ops if total_ops > 0 else 0
            return {
                'size': total_surfaces,
                'max_size': self.max_size,
                'allocations': self.allocations,
                'reuses': self.reuses,
                'reuse_rate': reuse_rate
            }

class RenderBatch:
    """Batch for similar rendering operations."""
    
    def __init__(self, renderer, batch_type):
        """Initialize a render batch.
        
        Args:
            renderer: Parent renderer
            batch_type: Type of batch (rect, circle, text, etc.)
        """
        self.renderer = renderer
        self.batch_type = batch_type
        self.items = []
        
    def add(self, component: Component) -> None:
        """Add a component to the batch.
        
        Args:
            component: Component to add
        """
        self.items.append(component)
        
    def render(self) -> None:
        """Render all components in the batch."""
        if not self.items:
            return
        
        # Choose appropriate rendering method based on type
        if self.batch_type == 'rect':
            self._render_rects()
        elif self.batch_type == 'circle':
            self._render_circles()
        elif self.batch_type == 'text':
            self._render_texts()
        else:
            # Fallback to individual rendering
            for component in self.items:
                self.renderer.render_component(component)
                
        # Clear the batch
        self.items.clear()
    
    def _render_rects(self) -> None:
        """Batch render rectangles."""
        # Group by color for efficiency
        color_groups = defaultdict(list)
        
        for component in self.items:
            color = tuple(component.style.get('backgroundColor', (0, 0, 0)))
            color_groups[color].append(component)
        
        # Render each color group
        for color, components in color_groups.items():
            rects = []
            for component in components:
                layout = component.layout
                rects.append(pygame.Rect(
                    layout['x'], layout['y'], layout['width'], layout['height']
                ))
            
            if rects:
                pygame.draw.rect(self.renderer.screen, color, rects)
    
    def _render_circles(self) -> None:
        """Batch render circles."""
        # Currently just iterates and renders individually
        # Could be optimized with OpenGL or similar for true batching
        for component in self.items:
            self.renderer.render_component(component)
    
    def _render_texts(self) -> None:
        """Batch render text components."""
        # Currently just iterates and renders individually
        # Text rendering is harder to batch efficiently in pygame
        for component in self.items:
            self.renderer.render_component(component)

class TransitionEffect:
    """Transition effect for smooth UI transitions between phases."""
    
    def __init__(self, duration=0.5, effect_type="fade", easing="ease_out_quad"):
        """Initialize a transition effect.
        
        Args:
            duration: Duration of the transition in seconds
            effect_type: Type of transition effect (fade, slide_left, slide_right, etc.)
            easing: Easing function to use (linear, ease_in_quad, ease_out_quad, etc.)
        """
        self.duration = duration
        self.effect_type = effect_type
        self.easing = easing
        self.start_time = None
        self.complete = False
        self.progress = 0.0
        self.from_surface = None
        self.to_surface = None
        self.is_active = False
    
    def start(self, from_surface, to_surface):
        """Start the transition.
        
        Args:
            from_surface: Surface to transition from
            to_surface: Surface to transition to
        """
        self.start_time = time.time()
        self.complete = False
        self.progress = 0.0
        self.from_surface = from_surface.copy() if from_surface else None
        self.to_surface = to_surface.copy() if to_surface else None
        self.is_active = True
    
    def update(self):
        """Update the transition progress.
        
        Returns:
            True if the transition is complete, False otherwise
        """
        if not self.is_active:
            return True
            
        current_time = time.time()
        elapsed = current_time - self.start_time
        
        # Calculate raw progress (0.0 to 1.0)
        raw_progress = min(1.0, elapsed / self.duration)
        
        # Apply easing function
        self.progress = self._apply_easing(raw_progress)
        
        # Check if complete
        if raw_progress >= 1.0:
            self.complete = True
            self.is_active = False
            return True
            
        return False
    
    def render(self, surface, rect):
        """Render the transition effect.
        
        Args:
            surface: Surface to render to
            rect: Rectangle to render in
        """
        if not self.is_active or not self.from_surface or not self.to_surface:
            return
            
        # Different rendering based on effect type
        if self.effect_type == "fade":
            # Crossfade between surfaces
            surface.blit(self.from_surface, rect.topleft)
            
            # Apply alpha to destination surface
            alpha = int(self.progress * 255)
            temp_surface = self.to_surface.copy()
            temp_surface.set_alpha(alpha)
            surface.blit(temp_surface, rect.topleft)
            
        elif self.effect_type == "slide_left":
            # Slide from right to left
            offset = int((1.0 - self.progress) * rect.width)
            surface.blit(self.from_surface, rect.topleft)
            surface.blit(self.to_surface, (rect.left - offset, rect.top))
            
        elif self.effect_type == "slide_right":
            # Slide from left to right
            offset = int((1.0 - self.progress) * rect.width)
            surface.blit(self.from_surface, rect.topleft)
            surface.blit(self.to_surface, (rect.left + offset, rect.top))
            
        elif self.effect_type == "zoom_in":
            # Zoom in effect
            surface.blit(self.from_surface, rect.topleft)
            
            # Calculate scaled size
            scale = self.progress
            scaled_width = int(rect.width * scale)
            scaled_height = int(rect.height * scale)
            
            if scaled_width > 0 and scaled_height > 0:
                scaled_surface = pygame.transform.smoothscale(
                    self.to_surface, (scaled_width, scaled_height)
                )
                
                # Center the scaled surface
                x = rect.left + (rect.width - scaled_width) // 2
                y = rect.top + (rect.height - scaled_height) // 2
                
                surface.blit(scaled_surface, (x, y))
    
    def _apply_easing(self, t):
        """Apply an easing function to the progress value.
        
        Args:
            t: Raw progress value (0.0 to 1.0)
            
        Returns:
            Eased progress value
        """
        if self.easing == "linear":
            return t
        elif self.easing == "ease_in_quad":
            return t * t
        elif self.easing == "ease_out_quad":
            return t * (2 - t)
        elif self.easing == "ease_in_out_quad":
            return 2 * t * t if t < 0.5 else -1 + (4 - 2 * t) * t
        else:
            # Default to ease_out_quad
            return t * (2 - t)

class UnifiedRenderer:
    """Unified renderer for the MetaMindIQTrain platform with pygame."""
    
    def __init__(self, screen_width=1440, screen_height=1024, title="MetaMindIQTrain"):
        """Initialize the renderer.
        
        Args:
            screen_width: Screen width
            screen_height: Screen height
            title: Window title
        """
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.title = title
        self.screen = None
        self.clock = None
        self.fps = 60
        self.running = False
        self.ui = None
        
        # Initialize optimizations
        self.surface_cache = SurfaceCache()
        self.surface_pool = SurfacePool()
        
        # Font cache
        self.fonts = {}  # (name, size) -> font
        
        # Rendering stats
        self.frame_count = 0
        self.render_time = 0
        self.start_time = 0
        
        # Batching
        self.batches = {
            'rect': RenderBatch(self, 'rect'),
            'circle': RenderBatch(self, 'circle'),
            'text': RenderBatch(self, 'text')
        }
        self.batch_enabled = True
        self.dirty_regions = []
        
        # Initialize with default theme if not already set
        if not get_theme():
            set_theme(Theme.default_theme(platform="pygame"))
            
        # Colors - use theme colors but keep legacy method for backward compatibility
        self.colors = get_theme().colors
        
        # Transition effect support
        self.transition = None
        self.transition_surface = None
    
    def initialize(self) -> bool:
        """Initialize pygame and the renderer.
        
        Returns:
            True if initialization was successful, False otherwise
        """
        try:
            # Initialize pygame
            pygame.init()
            
            # Create display
            self.screen = pygame.display.set_mode(
                (self.screen_width, self.screen_height)
            )
            pygame.display.set_caption(self.title)
            
            # Create clock for FPS management
            self.clock = pygame.time.Clock()
            
            # Create UI
            self.ui = UI(self.screen_width, self.screen_height)
            
            # Record start time
            self.start_time = time.time()
            
            # Set running flag
            self.running = True
            
            logger.info(f"Renderer initialized with resolution {self.screen_width}x{self.screen_height}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize renderer: {e}")
            return False
    
    def shutdown(self) -> None:
        """Shut down the renderer."""
        try:
            # Clean up resources
            self.surface_cache.clear()
            self.surface_pool.clear()
            
            # Quit pygame
            pygame.quit()
            
            logger.info("Renderer shut down")
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")
    
    def process_events(self) -> List[Dict[str, Any]]:
        """Process pygame events.
        
        Returns:
            List of event dictionaries
        """
        events = []
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                events.append({"type": "quit"})
                
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Find component at click position
                component = self.ui.find_component_at(event.pos[0], event.pos[1])
                events.append({
                    "type": "click",
                    "pos": event.pos,
                    "button": event.button,
                    "component_id": component.id if component else None
                })
                
            elif event.type == pygame.KEYDOWN:
                events.append({
                    "type": "keydown",
                    "key": event.key,
                    "unicode": event.unicode,
                    "mod": event.mod
                })
                
        return events
    
    def is_running(self) -> bool:
        """Check if the renderer is still running.
        
        Returns:
            True if running, False otherwise
        """
        return self.running
    
    def get_font(self, name=None, size=24) -> pygame.font.Font:
        """Get a font from the cache or create a new one.
        
        Args:
            name: Font name or path
            size: Font size
            
        Returns:
            pygame.font.Font instance
        """
        if name is None:
            name = pygame.font.get_default_font()
            
        key = (name, size)
        
        if key not in self.fonts:
            try:
                self.fonts[key] = pygame.font.Font(name, size)
            except:
                # Fallback to default font
                self.fonts[key] = pygame.font.SysFont("Arial", size)
                
        return self.fonts[key]
    
    def render(self, state: Dict[str, Any]) -> None:
        """Render the current state with optimized flow and transitions.
        
        Args:
            state: Current state dictionary
        """
        start_time = time.time()
        
        # Handle transition effects
        if self.transition and self.transition.is_active:
            # Render to the transition target instead of the screen
            original_screen = self.screen
            self.screen = self.transition_surface
            
            # Clear the transition target
            self.screen.fill(self.colors["background"])
        else:
            # Normal rendering to the screen
            self.screen.fill(self.colors["background"])
        
        # Update UI from state if needed
        if "ui" in state:
            self.update_ui_from_state(state["ui"])
        
        # Skip rendering if UI is not available
        if not self.ui:
            # Present the rendered frame
            pygame.display.flip()
            self.render_time = time.time() - start_time
            self.frame_count += 1
            return
        
        # Calculate layout if needed
        if not self.ui.layout_calculated:
            self.ui.calculate_layout()
        
        # Track dirty regions for optimized updates
        self.dirty_regions = []
        
        # Render UI components
        self.render_component_tree(self.ui.root)
        
        # Flush any remaining batches
        for batch in self.batches.values():
            batch.render()
        
        # Handle transition rendering
        if self.transition and self.transition.is_active:
            # Restore original screen
            self.screen = original_screen
            
            # Update transition
            self.transition.update()
            
            # Render transition effect
            rect = pygame.Rect(0, 0, self.screen_width, self.screen_height)
            self.transition.render(self.screen, rect)
            
            # Always flip the whole screen for transitions
            pygame.display.flip()
        else:
            # Present the rendered frame - either full flip or update specific regions
            if len(self.dirty_regions) > 5:  # If too many regions, just flip the whole screen
                pygame.display.flip()
            else:
                # Update only dirty regions if we have them
                if self.dirty_regions:
                    pygame.display.update(self.dirty_regions)
                else:
                    pygame.display.flip()
        
        # Update render stats
        self.render_time = time.time() - start_time
        self.frame_count += 1
        
        # Periodically clean the cache (less frequently for better performance)
        if self.frame_count % 300 == 0:
            self.surface_cache.clean_expired()
    
    def update_ui_from_state(self, ui_state: Dict[str, Any]) -> None:
        """Update the UI from a state dictionary.
        
        Args:
            ui_state: UI state dictionary
        """
        # For now, just recreate the UI from scratch
        # A more sophisticated implementation would diff and update
        self.ui.clear()
        
        if "components" in ui_state:
            for component_data in ui_state["components"]:
                component = create_component_tree(component_data)
                self.ui.add(component)
    
    def render_component_tree(self, component: Component) -> None:
        """Render a component and its children.
        
        Args:
            component: Root component to render
        """
        if not component.needs_render():
            # Component hasn't changed, use cached version
            return
        
        # Render the component
        self.render_component(component)
        
        # Render children
        for child in component.children:
            self.render_component_tree(child)
        
        # Mark component as clean
        component.mark_clean()
    
    def render_component(self, component: Component) -> None:
        """Render a single component.
        
        Args:
            component: Component to render
        """
        # Skip rendering if the component is outside the screen
        layout = component.layout
        screen_rect = pygame.Rect(0, 0, self.screen_width, self.screen_height)
        component_rect = pygame.Rect(layout['x'], layout['y'], layout['width'], layout['height'])
        if not screen_rect.colliderect(component_rect):
            return
        
        # Check for batching
        if self.batch_enabled and component.type in self.batches:
            self.batches[component.type].add(component)
            return
        
        # Add to dirty regions
        self.dirty_regions.append(component_rect)
        
        # Get component hash for caching
        component_hash = component.hash_for_rendering()
        
        # Try to get from cache
        cached_surface = self.surface_cache.get(component_hash)
        if cached_surface:
            # Use cached surface
            self.screen.blit(cached_surface, (component.layout['x'], component.layout['y']))
            return
        
        # Handle different component types
        if component.type == 'rect':
            self._render_rect(component)
        elif component.type == 'circle':
            self._render_circle(component)
        elif component.type == 'text':
            self._render_text(component)
        elif component.type == 'image':
            self._render_image(component)
        elif component.type == 'button':
            self._render_button(component)
        elif component.type == 'grid':
            self._render_grid(component)
        elif component.type == 'container':
            self._render_container(component)
        elif component.type == 'symbol_cell':
            self._render_symbol_cell(component)
        else:
            # Unknown component type - log warning
            logging.warning(f"Unknown component type: {component.type}")
    
    def _render_rect(self, component: Component) -> None:
        """Render a rectangle component.
        
        Args:
            component: Rectangle component
        """
        layout = component.layout
        bg_color = component.style.get('backgroundColor', self.colors["secondary"])
        border_width = component.style.get('borderWidth', 0)
        border_color = component.style.get('borderColor', self.colors["border"])
        border_radius = component.style.get('borderRadius', 0)
        
        rect = pygame.Rect(layout['x'], layout['y'], layout['width'], layout['height'])
        
        # Create a surface for caching
        flags = pygame.SRCALPHA if len(bg_color) == 4 and bg_color[3] < 255 else 0
        surface = self.surface_pool.get(layout['width'], layout['height'], flags)
        
        # Clear the surface
        if flags & pygame.SRCALPHA:
            surface.fill((0, 0, 0, 0))
        else:
            surface.fill((0, 0, 0))
        
        # Draw to the surface
        component_rect = pygame.Rect(0, 0, layout['width'], layout['height'])
        
        if border_radius > 0:
            # Draw with rounded corners
            pygame.draw.rect(surface, bg_color, component_rect, 0, border_radius)
            if border_width > 0:
                pygame.draw.rect(surface, border_color, component_rect, border_width, border_radius)
        else:
            # Draw without rounded corners
            pygame.draw.rect(surface, bg_color, component_rect, 0)
            if border_width > 0:
                pygame.draw.rect(surface, border_color, component_rect, border_width)
        
        # Draw to screen
        self.screen.blit(surface, (layout['x'], layout['y']))
        
        # Cache the surface
        self.surface_cache.set(component.hash_for_rendering(), surface)
        
        # Release the surface back to the pool
        self.surface_pool.release(surface)
    
    def _render_circle(self, component: Component) -> None:
        """Render a circle component.
        
        Args:
            component: Circle component
        """
        layout = component.layout
        radius = component.props.get('radius', min(layout['width'], layout['height']) // 2)
        bg_color = component.style.get('backgroundColor', self.colors["secondary"])
        border_width = component.style.get('borderWidth', 0)
        border_color = component.style.get('borderColor', self.colors["border"])
        
        # Position is adjusted to center of the circle
        center_x = layout['x'] + layout['width'] // 2
        center_y = layout['y'] + layout['height'] // 2
        
        # Create a surface for caching
        flags = pygame.SRCALPHA if len(bg_color) == 4 and bg_color[3] < 255 else 0
        surface = self.surface_pool.get(layout['width'], layout['height'], flags)
        
        # Clear the surface
        if flags & pygame.SRCALPHA:
            surface.fill((0, 0, 0, 0))
        else:
            surface.fill((0, 0, 0))
        
        # Draw to the surface
        center = (layout['width'] // 2, layout['height'] // 2)
        pygame.draw.circle(surface, bg_color, center, radius, 0)
        if border_width > 0:
            pygame.draw.circle(surface, border_color, center, radius, border_width)
        
        # Draw to screen
        self.screen.blit(surface, (layout['x'], layout['y']))
        
        # Cache the surface
        self.surface_cache.set(component.hash_for_rendering(), surface)
        
        # Release the surface back to the pool
        self.surface_pool.release(surface)
    
    def _render_text(self, component: Component) -> None:
        """Render a text component with enhanced quality and better web alignment.
        
        Args:
            component: Text component
        """
        layout = component.layout
        text = component.props.get('text', '')
        font_name = component.style.get('fontFamily', None)
        font_size = component.style.get('fontSize', 24)
        color = component.style.get('color', self.colors["text"])
        align = component.style.get('textAlign', 'left')
        bg_color = component.style.get('backgroundColor', None)
        padding = component.style.get('padding', 0)
        line_height = component.style.get('lineHeight', 1.2)
        font_weight = component.style.get('fontWeight', 'normal')
        
        # Get font with weight support
        if font_weight == 'bold':
            # Try to find a bold variant of the font
            bold_font_name = f"{font_name} Bold" if font_name else None
            font = self.get_font(bold_font_name, font_size)
        else:
            font = self.get_font(font_name, font_size)
        
        # Create a surface for the component
        flags = pygame.SRCALPHA
        surface = self.surface_pool.get(layout['width'], layout['height'], flags)
        surface.fill((0, 0, 0, 0))
        
        # Handle multi-line text
        if '\n' in text:
            lines = text.split('\n')
            line_surfaces = []
            line_heights = []
            
            # Render each line
            for line in lines:
                if not line.strip():  # Skip empty lines but preserve height
                    line_heights.append(font_size * line_height)
                    line_surfaces.append(None)
                    continue
                    
                line_surf = font.render(line, True, color)
                line_surfaces.append(line_surf)
                line_heights.append(line_surf.get_height() * line_height)
            
            total_height = sum(line_heights)
            
            # Position and draw each line
            y_offset = (layout['height'] - total_height) // 2 if align.endswith('middle') else padding
            
            for i, line_surf in enumerate(line_surfaces):
                if line_surf is None:
                    y_offset += line_heights[i]
                    continue
                    
                rect = line_surf.get_rect()
                
                if align.startswith('center'):
                    rect.centerx = layout['width'] // 2
                elif align.startswith('right'):
                    rect.right = layout['width'] - padding
                else:  # left
                    rect.left = padding
                
                rect.y = int(y_offset)
                
                # Draw to surface
                surface.blit(line_surf, rect)
                y_offset += line_heights[i]
        else:
            # Single line text - use standard rendering
            text_surface = font.render(text, True, color)
            text_rect = text_surface.get_rect()
            
            # Position text based on alignment
            if align == 'center':
                text_rect.center = (layout['width'] // 2, layout['height'] // 2)
            elif align == 'right':
                text_rect.midright = (layout['width'] - padding, layout['height'] // 2)
            else:  # left
                text_rect.midleft = (padding, layout['height'] // 2)
            
            # Draw background if specified
            if bg_color:
                bg_rect = text_rect.copy()
                bg_rect.inflate_ip(padding * 2, padding * 2)
                border_radius = component.style.get('borderRadius', 0)
                pygame.draw.rect(surface, bg_color, bg_rect, 0, border_radius)
            
            # Draw text
            surface.blit(text_surface, text_rect)
        
        # Apply hover effect if specified
        if component.props.get('hover', False):
            hover_color = component.style.get('hoverColor', self.colors["highlight"])
            hover_rect = pygame.Rect(0, 0, layout['width'], layout['height'])
            pygame.draw.rect(surface, hover_color, hover_rect, 1, component.style.get('borderRadius', 0))
        
        # Draw to screen
        self.screen.blit(surface, (layout['x'], layout['y']))
        
        # Cache the surface
        self.surface_cache.set(component.hash_for_rendering(), surface)
        
        # Release the surface back to the pool
        self.surface_pool.release(surface)
    
    def _render_image(self, component: Component) -> None:
        """Render an image component.
        
        Args:
            component: Image component
        """
        layout = component.layout
        image_src = component.props.get('src', '')
        
        # Load image
        try:
            image = pygame.image.load(image_src)
            
            # Scale image if needed
            if (image.get_width() != layout['width'] or
                image.get_height() != layout['height']):
                image = pygame.transform.smoothscale(
                    image, (layout['width'], layout['height'])
                )
            
            # Draw to screen
            self.screen.blit(image, (layout['x'], layout['y']))
            
        except Exception as e:
            logger.error(f"Failed to load image {image_src}: {e}")
            
            # Draw error placeholder
            rect = pygame.Rect(layout['x'], layout['y'], layout['width'], layout['height'])
            pygame.draw.rect(self.screen, self.colors["error"], rect, 2)
            
            # Draw X
            pygame.draw.line(
                self.screen, self.colors["error"],
                (layout['x'], layout['y']),
                (layout['x'] + layout['width'], layout['y'] + layout['height']), 2
            )
            pygame.draw.line(
                self.screen, self.colors["error"],
                (layout['x'], layout['y'] + layout['height']),
                (layout['x'] + layout['width'], layout['y']), 2
            )
    
    def _render_button(self, component: Component) -> None:
        """Render a button component with web-like styling and hover effects.
        
        Args:
            component: Button component
        """
        layout = component.layout
        text = component.props.get('text', '')
        bg_color = component.style.get('backgroundColor', self.colors["primary"])
        text_color = component.style.get('color', self.colors["text"])
        border_radius = component.style.get('borderRadius', 8)  # Increased default radius
        border_width = component.style.get('borderWidth', 0)
        border_color = component.style.get('borderColor', self.colors["border"])
        font_name = component.style.get('fontFamily', None)
        font_size = component.style.get('fontSize', 24)
        hover = component.props.get('hover', False)
        active = component.props.get('active', False)
        padding = component.style.get('padding', 10)
        shadow = component.style.get('boxShadow', True)
        
        # Create a surface for caching with room for shadow if needed
        flags = pygame.SRCALPHA
        shadow_offset = 4 if shadow else 0
        surface = self.surface_pool.get(
            layout['width'] + shadow_offset, 
            layout['height'] + shadow_offset, 
            flags
        )
        surface.fill((0, 0, 0, 0))
        
        # Apply effect based on state
        button_rect = pygame.Rect(0, 0, layout['width'], layout['height'])
        actual_bg_color = bg_color
        actual_border_color = border_color
        scale_factor = 1.0
        
        if active:
            # Active button - darker shade
            actual_bg_color = self._darken_color(bg_color, 0.2)
            actual_border_color = self._darken_color(border_color, 0.2)
        elif hover:
            # Hover effect - lighter shade
            actual_bg_color = self._lighten_color(bg_color, 0.1)
            actual_border_color = self._lighten_color(border_color, 0.1)
            scale_factor = 1.05  # Slight scale-up on hover
            
            # Recalculate button_rect with scale
            button_width = int(layout['width'] * scale_factor)
            button_height = int(layout['height'] * scale_factor)
            center_x = layout['width'] // 2
            center_y = layout['height'] // 2
            button_rect = pygame.Rect(
                center_x - button_width // 2,
                center_y - button_height // 2,
                button_width,
                button_height
            )
        
        # Draw shadow if enabled
        if shadow:
            shadow_rect = button_rect.copy()
            shadow_rect.x += 2
            shadow_rect.y += 2
            pygame.draw.rect(
                surface, 
                (0, 0, 0, 80),  # Semi-transparent black
                shadow_rect, 
                0, 
                border_radius
            )
        
        # Draw button background
        pygame.draw.rect(surface, actual_bg_color, button_rect, 0, border_radius)
        
        # Draw border if specified
        if border_width > 0:
            pygame.draw.rect(surface, actual_border_color, button_rect, border_width, border_radius)
        
        # Draw button text
        font = self.get_font(font_name, font_size)
        text_surface = font.render(text, True, text_color)
        text_rect = text_surface.get_rect(center=(
            button_rect.centerx, 
            button_rect.centery
        ))
        surface.blit(text_surface, text_rect)
        
        # Draw to screen, adjusted for shadow
        self.screen.blit(surface, (
            layout['x'] - (shadow_offset // 2), 
            layout['y'] - (shadow_offset // 2)
        ))
        
        # Cache the surface
        self.surface_cache.set(component.hash_for_rendering(), surface)
        
        # Release the surface back to the pool
        self.surface_pool.release(surface)
    
    def _lighten_color(self, color, amount=0.2):
        """Lighten a color.
        
        Args:
            color: RGB or RGBA color tuple
            amount: Amount to lighten (0-1)
            
        Returns:
            Lightened color tuple
        """
        r, g, b = color[:3]
        r = min(255, int(r + (255 - r) * amount))
        g = min(255, int(g + (255 - g) * amount))
        b = min(255, int(b + (255 - b) * amount))
        
        if len(color) > 3:
            return (r, g, b, color[3])
        return (r, g, b)
    
    def _darken_color(self, color, amount=0.2):
        """Darken a color.
        
        Args:
            color: RGB or RGBA color tuple
            amount: Amount to darken (0-1)
            
        Returns:
            Darkened color tuple
        """
        r, g, b = color[:3]
        r = max(0, int(r * (1 - amount)))
        g = max(0, int(g * (1 - amount)))
        b = max(0, int(b * (1 - amount)))
        
        if len(color) > 3:
            return (r, g, b, color[3])
        return (r, g, b)
    
    def _render_grid(self, component: Component) -> None:
        """Render a grid component.
        
        Args:
            component: Grid component
        """
        layout = component.layout
        rows = component.props.get('rows', 1)
        cols = component.props.get('cols', 1)
        line_color = component.style.get('borderColor', self.colors["border"])
        line_width = component.style.get('borderWidth', 1)
        bg_color = component.style.get('backgroundColor', None)
        
        # Create a surface for caching
        flags = pygame.SRCALPHA
        surface = self.surface_pool.get(layout['width'], layout['height'], flags)
        surface.fill((0, 0, 0, 0))
        
        # Draw background if specified
        if bg_color:
            pygame.draw.rect(
                surface, bg_color,
                pygame.Rect(0, 0, layout['width'], layout['height'])
            )
        
        # Calculate cell size
        cell_width = layout['width'] / cols
        cell_height = layout['height'] / rows
        
        # Draw grid lines
        for i in range(rows + 1):
            y = i * cell_height
            pygame.draw.line(
                surface, line_color,
                (0, y), (layout['width'], y), line_width
            )
        
        for i in range(cols + 1):
            x = i * cell_width
            pygame.draw.line(
                surface, line_color,
                (x, 0), (x, layout['height']), line_width
            )
        
        # Draw to screen
        self.screen.blit(surface, (layout['x'], layout['y']))
        
        # Cache the surface
        self.surface_cache.set(component.hash_for_rendering(), surface)
        
        # Release the surface back to the pool
        self.surface_pool.release(surface)
    
    def _render_container(self, component: Component) -> None:
        """Render a container component.
        
        Args:
            component: Container component
        """
        layout = component.layout
        bg_color = component.style.get('backgroundColor', None)
        border_width = component.style.get('borderWidth', 0)
        border_color = component.style.get('borderColor', self.colors["border"])
        border_radius = component.style.get('borderRadius', 0)
        
        # Only render if there's a background or border
        if not bg_color and border_width <= 0:
            return
        
        # Create a surface for caching
        flags = pygame.SRCALPHA
        surface = self.surface_pool.get(layout['width'], layout['height'], flags)
        surface.fill((0, 0, 0, 0))
        
        # Draw container
        container_rect = pygame.Rect(0, 0, layout['width'], layout['height'])
        
        if bg_color:
            pygame.draw.rect(surface, bg_color, container_rect, 0, border_radius)
        
        if border_width > 0:
            pygame.draw.rect(surface, border_color, container_rect, border_width, border_radius)
        
        # Draw to screen
        self.screen.blit(surface, (layout['x'], layout['y']))
        
        # Cache the surface
        self.surface_cache.set(component.hash_for_rendering(), surface)
        
        # Release the surface back to the pool
        self.surface_pool.release(surface)
    
    def _render_symbol_cell(self, component: Component) -> None:
        """Render a symbol cell component optimized for the symbol memory module.
        
        Args:
            component: Symbol cell component
        """
        layout = component.layout
        symbol = component.props.get('symbol', '')
        bg_color = component.style.get('backgroundColor', self.colors["cell_background"])
        color = component.style.get('color', self.colors["text"])
        border_width = component.style.get('borderWidth', 1)
        border_color = component.style.get('borderColor', self.colors["border"])
        border_radius = component.style.get('borderRadius', 8)
        highlighted = component.props.get('highlighted', False) 
        active = component.props.get('active', False)
        correct = component.props.get('correct', False)
        incorrect = component.props.get('incorrect', False)
        
        # Create a surface with alpha
        surface = self.surface_pool.get(layout['width'], layout['height'], pygame.SRCALPHA)
        surface.fill((0, 0, 0, 0))
        
        # Determine actual color based on state
        actual_bg_color = bg_color
        actual_border_color = border_color
        shadow_color = None
        
        if highlighted:
            actual_bg_color = self.colors["cell_highlight"]
            actual_border_color = self.colors["primary"]
            border_width = 2
            shadow_color = self.colors["primary"]
        elif active:
            actual_bg_color = self._lighten_color(bg_color, 0.2)
            actual_border_color = self.colors["primary"]
            border_width = 2
        elif correct:
            actual_bg_color = (50, 255, 50, 80)  # Semi-transparent green
            actual_border_color = self.colors["success"]
            border_width = 2
        elif incorrect:
            actual_bg_color = (255, 50, 50, 80)  # Semi-transparent red
            actual_border_color = self.colors["error"]
            border_width = 2
        
        # Draw cell rect
        cell_rect = pygame.Rect(0, 0, layout['width'], layout['height'])
        
        # Draw shadow if highlighted
        if shadow_color:
            shadow_surf = pygame.Surface((layout['width'], layout['height']), pygame.SRCALPHA)
            for offset in range(5, 0, -1):
                alpha = int(100 * (1 - offset/5))
                shadow_color_with_alpha = (*shadow_color[:3], alpha)
                pygame.draw.rect(
                    shadow_surf, 
                    shadow_color_with_alpha,
                    cell_rect.inflate(offset*2, offset*2), 
                    0, 
                    border_radius + offset
                )
            surface.blit(shadow_surf, (0, 0))
        
        # Draw background
        pygame.draw.rect(surface, actual_bg_color, cell_rect, 0, border_radius)
        
        # Draw border
        if border_width > 0:
            pygame.draw.rect(surface, actual_border_color, cell_rect, border_width, border_radius)
        
        # Draw symbol
        if symbol:
            font_size = min(layout['width'], layout['height']) // 2
            font = self.get_font(None, font_size)
            text_surface = font.render(symbol, True, color)
            text_rect = text_surface.get_rect(center=(layout['width']//2, layout['height']//2))
            surface.blit(text_surface, text_rect)
        
        # Draw to screen
        self.screen.blit(surface, (layout['x'], layout['y']))
        
        # Cache the surface
        self.surface_cache.set(component.hash_for_rendering(), surface)
        
        # Release the surface back to the pool
        self.surface_pool.release(surface)
    
    def set_batch_rendering(self, enabled: bool) -> None:
        """Enable or disable batch rendering.
        
        Args:
            enabled: Whether batch rendering should be enabled
        """
        self.batch_enabled = enabled
    
    def start_transition(self, effect_type="fade", duration=0.5, easing="ease_out_quad"):
        """Start a transition effect between UI states.
        
        Args:
            effect_type: Type of transition effect
            duration: Duration of the transition in seconds
            easing: Easing function to use
            
        Returns:
            True if transition started, False otherwise
        """
        # Only start if we have a screen
        if not self.screen:
            return False
        
        # Create transition effect
        self.transition = TransitionEffect(
            duration=duration,
            effect_type=effect_type,
            easing=easing
        )
        
        # Capture current screen
        from_surface = self.screen.copy()
        
        # Create a new surface for the target state
        to_surface = pygame.Surface(
            (self.screen_width, self.screen_height), 
            flags=self.screen.get_flags()
        )
        
        # Start the transition
        self.transition.start(from_surface, to_surface)
        
        # Save reference to the target surface
        self.transition_surface = to_surface
        
        return True
    
    def get_stats(self) -> Dict[str, Any]:
        """Get renderer statistics.
        
        Returns:
            Dictionary with renderer statistics
        """
        current_time = time.time()
        elapsed = current_time - self.start_time
        fps = self.frame_count / elapsed if elapsed > 0 else 0
        
        return {
            'fps': fps,
            'frame_count': self.frame_count,
            'render_time': self.render_time,
            'uptime': elapsed,
            'surface_cache': self.surface_cache.get_stats(),
            'surface_pool': self.surface_pool.get_stats(),
            'component_stats': get_stats()
        }
    
    def get_color(self, color_name=None, color_value=None):
        """Get a color from the theme system or use the provided color value.
        
        Args:
            color_name: Color name from theme
            color_value: Explicitly provided color value
            
        Returns:
            The resolved color as a tuple
        """
        if color_value is not None:
            return color_value
            
        if color_name:
            theme_colors = get_theme().colors
            return theme_colors.get(color_name, theme_colors.get("primary", (255, 255, 255)))
            
        return (255, 255, 255)  # Default to white if color not found
    
    def apply_theme(self, new_theme=None):
        """Apply a new theme to the renderer.
        
        Args:
            new_theme: Theme instance to apply, or None to use default
        """
        if new_theme is None:
            new_theme = Theme.default_theme(platform="pygame")
        
        set_theme(new_theme)
        
        # Update colors dictionary for backwards compatibility
        self.colors = get_theme().colors
        
        # Clear all caches as style properties may have changed
        self.surface_cache.clear()
        self.fonts.clear()
        
        # Mark entire screen as dirty
        self.mark_dirty(0, 0, self.screen_width, self.screen_height)
        
        logger.info("Applied new theme to renderer")


# Helper function for easy initialization
def create_renderer(width=1440, height=1024, title="MetaMindIQTrain") -> UnifiedRenderer:
    """Create and initialize a unified renderer.
    
    Args:
        width: Screen width
        height: Screen height
        title: Window title
        
    Returns:
        Initialized UnifiedRenderer instance
    """
    renderer = UnifiedRenderer(width, height, title)
    renderer.initialize()
    return renderer


# Example usage when run directly
if __name__ == "__main__":
    # Reset component stats
    reset_stats()
    
    # Create and initialize the renderer
    renderer = create_renderer(800, 600, "Unified Renderer Test")
    
    # Create a test UI
    ui = create_ui(800, 600)
    
    # Add some components
    container = ComponentFactory.container(
        x=100, y=100, width=600, height=400,
        backgroundColor=(40, 40, 60, 200),
        borderWidth=2,
        borderColor=(100, 100, 200),
        borderRadius=10
    )
    
    # Add a title
    title = ComponentFactory.text(
        text="Unified Renderer Test",
        x=20, y=20, width=560, height=40,
        color=(255, 255, 255),
        fontSize=32,
        textAlign='center'
    )
    container.add_child(title)
    
    # Add a button
    button = ComponentFactory.button(
        text="Click Me",
        x=250, y=300, width=100, height=40,
        backgroundColor=(60, 120, 255),
        color=(255, 255, 255),
        borderRadius=5
    )
    container.add_child(button)
    
    # Add a grid
    grid = ComponentFactory.grid(
        rows=5, cols=5,
        x=50, y=100, width=200, height=200,
        borderColor=(100, 100, 200),
        borderWidth=1
    )
    container.add_child(grid)
    
    # Add the container to the UI
    ui.add(container)
    
    # Use the UI in the renderer
    renderer.ui = ui
    
    # Main loop
    while renderer.is_running():
        # Process events
        events = renderer.process_events()
        
        # Render the UI
        renderer.render({})
        
        # Wait a bit
        pygame.time.delay(10)
    
    # Shutdown
    renderer.shutdown() 