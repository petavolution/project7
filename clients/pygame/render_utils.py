#!/usr/bin/env python3
"""
Render Utilities for MetaMindIQTrain Pygame Client

This module contains reusable rendering utilities:
- SurfaceCache: LRU cache for rendered surfaces
- SurfacePool: Pool for reusing pygame surfaces
- RenderBatch: Batch similar rendering operations
- TransitionEffect: Smooth UI transitions
"""

import pygame
import time
import threading
import logging
from typing import Dict, List, Any, Optional
from collections import defaultdict, OrderedDict

logger = logging.getLogger(__name__)


class SurfaceCache:
    """Cache for rendered component surfaces with LRU eviction and memory management."""

    def __init__(self, max_size=1000, ttl=10.0, max_memory_mb=64):
        """Initialize the surface cache.

        Args:
            max_size: Maximum number of surfaces in the cache
            ttl: Time-to-live for cached surfaces in seconds
            max_memory_mb: Maximum memory usage in MB
        """
        self.surfaces = OrderedDict()
        self.max_size = max_size
        self.ttl = ttl
        self.max_memory = max_memory_mb * 1024 * 1024
        self.current_memory = 0
        self.hits = 0
        self.misses = 0
        self.evictions = 0
        self.lock = threading.RLock()

    def get(self, component_hash: str) -> Optional[pygame.Surface]:
        """Get a cached surface for a component hash."""
        with self.lock:
            if component_hash in self.surfaces:
                surface, timestamp = self.surfaces[component_hash]

                if time.time() - timestamp > self.ttl:
                    self._remove_entry(component_hash)
                    self.misses += 1
                    return None

                self.surfaces.move_to_end(component_hash)
                self.hits += 1
                return surface

            self.misses += 1
            return None

    def set(self, component_hash: str, surface: pygame.Surface) -> None:
        """Add a surface to the cache with memory accounting."""
        with self.lock:
            surface_memory = self._calculate_surface_memory(surface)
            self._ensure_space(surface_memory)

            if component_hash in self.surfaces:
                self._remove_entry(component_hash)

            self.surfaces[component_hash] = (surface.copy(), time.time())
            self.current_memory += surface_memory

    def clear(self) -> None:
        """Clear the cache."""
        with self.lock:
            self.surfaces.clear()
            self.current_memory = 0

    def clean_expired(self) -> int:
        """Remove expired entries from the cache."""
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
        """Ensure there's enough space for a new surface."""
        while len(self.surfaces) >= self.max_size and self.surfaces:
            oldest = next(iter(self.surfaces))
            self._remove_entry(oldest)
            self.evictions += 1

        while self.current_memory + needed_memory > self.max_memory and self.surfaces:
            oldest = next(iter(self.surfaces))
            self._remove_entry(oldest)
            self.evictions += 1

    def _remove_entry(self, hash_key: str) -> None:
        """Remove an entry and update memory accounting."""
        if hash_key in self.surfaces:
            surface, _ = self.surfaces[hash_key]
            memory_used = self._calculate_surface_memory(surface)
            del self.surfaces[hash_key]
            self.current_memory -= memory_used

    def _calculate_surface_memory(self, surface: pygame.Surface) -> int:
        """Calculate approximate memory usage of a surface."""
        width, height = surface.get_size()
        bits_per_pixel = surface.get_bitsize()
        bytes_per_pixel = bits_per_pixel // 8 if bits_per_pixel >= 8 else 1
        row_bytes = width * bytes_per_pixel
        if row_bytes % 4 != 0:
            row_bytes = (row_bytes + 3) & ~3
        return row_bytes * height

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
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
        """Initialize the surface pool."""
        self.surfaces = defaultdict(list)
        self.max_size = max_size
        self.allocations = 0
        self.reuses = 0
        self.lock = threading.RLock()

    def get(self, width: int, height: int, flags: int = 0) -> pygame.Surface:
        """Get a surface from the pool or create a new one."""
        with self.lock:
            key = (width, height, flags)

            if key in self.surfaces and self.surfaces[key]:
                surface = self.surfaces[key].pop()
                surface.fill((0, 0, 0, 0) if flags & pygame.SRCALPHA else (0, 0, 0))
                self.reuses += 1
                return surface

            self.allocations += 1
            return pygame.Surface((width, height), flags)

    def release(self, surface: pygame.Surface) -> None:
        """Return a surface to the pool."""
        with self.lock:
            if surface is None:
                return
            key = (surface.get_width(), surface.get_height(), surface.get_flags())
            if len(self.surfaces[key]) < self.max_size:
                self.surfaces[key].append(surface)

    def clear(self) -> None:
        """Clear the pool."""
        with self.lock:
            self.surfaces.clear()

    def get_stats(self) -> Dict[str, Any]:
        """Get pool statistics."""
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
        """Initialize a render batch."""
        self.renderer = renderer
        self.batch_type = batch_type
        self.items = []

    def add(self, component) -> None:
        """Add a component to the batch."""
        self.items.append(component)

    def render(self) -> None:
        """Render all components in the batch."""
        if not self.items:
            return

        if self.batch_type == 'rect':
            self._render_rects()
        elif self.batch_type == 'circle':
            self._render_circles()
        elif self.batch_type == 'text':
            self._render_texts()
        else:
            for component in self.items:
                self.renderer.render_component(component)

        self.items.clear()

    def _render_rects(self) -> None:
        """Batch render rectangles."""
        color_groups = defaultdict(list)

        for component in self.items:
            color = tuple(component.style.get('backgroundColor', (0, 0, 0)))
            color_groups[color].append(component)

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
        for component in self.items:
            self.renderer.render_component(component)

    def _render_texts(self) -> None:
        """Batch render text components."""
        for component in self.items:
            self.renderer.render_component(component)


class TransitionEffect:
    """Transition effect for smooth UI transitions between phases."""

    def __init__(self, duration=0.5, effect_type="fade", easing="ease_out_quad"):
        """Initialize a transition effect."""
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
        """Start the transition."""
        self.start_time = time.time()
        self.complete = False
        self.progress = 0.0
        self.from_surface = from_surface.copy() if from_surface else None
        self.to_surface = to_surface.copy() if to_surface else None
        self.is_active = True

    def update(self):
        """Update the transition progress. Returns True if complete."""
        if not self.is_active:
            return True

        current_time = time.time()
        elapsed = current_time - self.start_time
        raw_progress = min(1.0, elapsed / self.duration)
        self.progress = self._apply_easing(raw_progress)

        if raw_progress >= 1.0:
            self.complete = True
            self.is_active = False
            return True

        return False

    def render(self, surface, rect):
        """Render the transition effect."""
        if not self.is_active or not self.from_surface or not self.to_surface:
            return

        if self.effect_type == "fade":
            surface.blit(self.from_surface, rect.topleft)
            alpha = int(self.progress * 255)
            temp_surface = self.to_surface.copy()
            temp_surface.set_alpha(alpha)
            surface.blit(temp_surface, rect.topleft)

        elif self.effect_type == "slide_left":
            offset = int((1.0 - self.progress) * rect.width)
            surface.blit(self.from_surface, rect.topleft)
            surface.blit(self.to_surface, (rect.left - offset, rect.top))

        elif self.effect_type == "slide_right":
            offset = int((1.0 - self.progress) * rect.width)
            surface.blit(self.from_surface, rect.topleft)
            surface.blit(self.to_surface, (rect.left + offset, rect.top))

        elif self.effect_type == "zoom_in":
            surface.blit(self.from_surface, rect.topleft)
            scale = self.progress
            scaled_width = int(rect.width * scale)
            scaled_height = int(rect.height * scale)

            if scaled_width > 0 and scaled_height > 0:
                scaled_surface = pygame.transform.smoothscale(
                    self.to_surface, (scaled_width, scaled_height)
                )
                x = rect.left + (rect.width - scaled_width) // 2
                y = rect.top + (rect.height - scaled_height) // 2
                surface.blit(scaled_surface, (x, y))

    def _apply_easing(self, t):
        """Apply an easing function to the progress value."""
        if self.easing == "linear":
            return t
        elif self.easing == "ease_in_quad":
            return t * t
        elif self.easing == "ease_out_quad":
            return t * (2 - t)
        elif self.easing == "ease_in_out_quad":
            return 2 * t * t if t < 0.5 else -1 + (4 - 2 * t) * t
        else:
            return t * (2 - t)


# Color manipulation utilities
def lighten_color(color, amount=0.2):
    """Lighten a color by the specified amount (0-1)."""
    r, g, b = color[:3]
    r = min(255, int(r + (255 - r) * amount))
    g = min(255, int(g + (255 - g) * amount))
    b = min(255, int(b + (255 - b) * amount))

    if len(color) > 3:
        return (r, g, b, color[3])
    return (r, g, b)


def darken_color(color, amount=0.2):
    """Darken a color by the specified amount (0-1)."""
    r, g, b = color[:3]
    r = max(0, int(r * (1 - amount)))
    g = max(0, int(g * (1 - amount)))
    b = max(0, int(b * (1 - amount)))

    if len(color) > 3:
        return (r, g, b, color[3])
    return (r, g, b)
