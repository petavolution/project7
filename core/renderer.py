#!/usr/bin/env python3
"""
Optimized Renderer System for MetaMindIQTrain

This module provides a highly optimized rendering system for the MetaMindIQTrain
platform, supporting multiple backend rendering engines while providing a 
consistent API for component rendering.
"""

import logging
import sys
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Tuple, Union

logger = logging.getLogger(__name__)

class RenderBackend(ABC):
    """Abstract base class for render backends."""
    
    @abstractmethod
    def initialize(self, width: int, height: int, title: str = "MetaMindIQTrain") -> bool:
        """Initialize the rendering backend.
        
        Args:
            width: Window width
            height: Window height
            title: Window title
            
        Returns:
            True if initialization was successful, False otherwise
        """
        pass
        
    @abstractmethod
    def clear(self, color: Tuple[int, int, int, int] = (0, 0, 0, 255)) -> None:
        """Clear the screen with the specified color.
        
        Args:
            color: RGBA color (default: black)
        """
        pass
        
    @abstractmethod
    def present(self) -> None:
        """Present the rendered frame to the screen."""
        pass
        
    @abstractmethod
    def shutdown(self) -> None:
        """Shut down the rendering backend."""
        pass
        
    @abstractmethod
    def is_running(self) -> bool:
        """Check if the rendering backend is still running.
        
        Returns:
            True if the backend is still running, False otherwise
        """
        pass
        
    @abstractmethod
    def process_events(self) -> List[Dict[str, Any]]:
        """Process input events.
        
        Returns:
            List of event dictionaries
        """
        pass
        
    @abstractmethod
    def draw_rectangle(self, x: int, y: int, width: int, height: int,
                      color: Tuple[int, int, int, int], filled: bool = True) -> None:
        """Draw a rectangle.

        Args:
            x: X coordinate
            y: Y coordinate
            width: Rectangle width
            height: Rectangle height
            color: Fill color (RGBA)
            filled: Whether to fill the rectangle (default True)
        """
        pass
        
    @abstractmethod
    def draw_rounded_rectangle(self, x: int, y: int, width: int, height: int,
                              color: Tuple[int, int, int, int], radius: int = 5,
                              border_color: Optional[Tuple[int, int, int, int]] = None,
                              border_width: int = 0) -> None:
        """Draw a rounded rectangle.
        
        Args:
            x: X coordinate
            y: Y coordinate
            width: Rectangle width
            height: Rectangle height
            color: Fill color (RGBA)
            radius: Corner radius
            border_color: Border color (RGBA) or None for no border
            border_width: Border width in pixels
        """
        pass
        
    @abstractmethod
    def draw_line(self, x1: int, y1: int, x2: int, y2: int, 
                 color: Tuple[int, int, int, int], thickness: int = 1) -> None:
        """Draw a line.
        
        Args:
            x1: Start X coordinate
            y1: Start Y coordinate
            x2: End X coordinate
            y2: End Y coordinate
            color: Line color (RGBA)
            thickness: Line thickness in pixels
        """
        pass
        
    @abstractmethod
    def draw_text(self, x: int, y: int, text: str, font_size: int = 16,
                 color: Tuple[int, int, int, int] = (255, 255, 255, 255),
                 align: str = "left", font_name: str = "default",
                 center_vertically: bool = False) -> Tuple[int, int]:
        """Draw text.
        
        Args:
            x: X coordinate
            y: Y coordinate
            text: Text to draw
            font_size: Font size in points
            color: Text color (RGBA)
            align: Text alignment ("left", "center", "right")
            font_name: Font name
            center_vertically: Whether to center the text vertically
            
        Returns:
            Tuple of (width, height) of the rendered text
        """
        pass
        
    @abstractmethod
    def draw_circle(self, x: int, y: int, radius: int,
                   color: Tuple[int, int, int, int],
                   border_color: Optional[Tuple[int, int, int, int]] = None,
                   border_width: int = 0, filled: bool = True) -> None:
        """Draw a circle.

        Args:
            x: Center X coordinate
            y: Center Y coordinate
            radius: Circle radius
            color: Fill color (RGBA)
            border_color: Border color (RGBA) or None for no border
            border_width: Border width in pixels
            filled: Whether to fill the circle (default True)
        """
        pass
        
    @abstractmethod
    def draw_image(self, x: int, y: int, image_path: str, 
                  width: Optional[int] = None, height: Optional[int] = None) -> None:
        """Draw an image.
        
        Args:
            x: X coordinate
            y: Y coordinate
            image_path: Path to the image file
            width: Target width (or None to use the image's width)
            height: Target height (or None to use the image's height)
        """
        pass

class PygameBackend(RenderBackend):
    """Pygame-based rendering backend with optimized performance."""
    
    def __init__(self):
        """Initialize the Pygame backend."""
        self.initialized = False
        self.running = False
        self.screen = None
        self.clock = None
        self.width = 800
        self.height = 600
        self.image_cache = {}
        self.font_cache = {}
        self.render_stats = {
            "frame_count": 0,
            "last_fps_update": 0,
            "fps": 0,
            "draw_calls": 0
        }
        
    def initialize(self, width: int, height: int, title: str = "MetaMindIQTrain") -> bool:
        """Initialize the Pygame backend with optimized settings."""
        try:
            import pygame
            pygame.init()
            
            # Set display flags for hardware acceleration
            flags = pygame.HWSURFACE | pygame.DOUBLEBUF
            
            self.width = width
            self.height = height
            self.screen = pygame.display.set_mode((width, height), flags)
            pygame.display.set_caption(title)
            
            self.clock = pygame.time.Clock()
            self.running = True
            self.initialized = True
            self.render_stats["last_fps_update"] = pygame.time.get_ticks()
            
            logger.info(f"Optimized Pygame backend initialized ({width}x{height})")
            return True
            
        except ImportError:
            logger.error("Pygame is not installed. Please install pygame to use this backend.")
            return False
        except Exception as e:
            logger.error(f"Error initializing Pygame backend: {e}")
            return False
    
    def clear(self, color: Tuple[int, int, int, int] = (0, 0, 0, 255)) -> None:
        """Clear the screen with the specified color using optimized fill."""
        if not self.initialized:
            return
            
        import pygame
        # Use the faster fill method without creating a new surface
        self.screen.fill(color[:3])
        self.render_stats["draw_calls"] += 1
        
    def present(self) -> None:
        """Present the rendered frame with FPS limiting and stats tracking."""
        if not self.initialized:
            return
            
        import pygame
        
        # Update frame counter and calculate FPS
        self.render_stats["frame_count"] += 1
        current_time = pygame.time.get_ticks()
        
        if current_time - self.render_stats["last_fps_update"] >= 1000:  # Update every second
            self.render_stats["fps"] = self.render_stats["frame_count"] * 1000 / (current_time - self.render_stats["last_fps_update"])
            self.render_stats["frame_count"] = 0
            self.render_stats["last_fps_update"] = current_time
            self.render_stats["draw_calls"] = 0
            
        # Flip the display with vsync
        pygame.display.flip()
        
        # Use clock.tick to maintain stable framerate
        self.clock.tick(60)
    
    def shutdown(self) -> None:
        """Shut down the Pygame backend."""
        if not self.initialized:
            return
            
        import pygame
        
        # Clear caches
        self.image_cache.clear()
        self.font_cache.clear()
        
        # Shut down pygame
        pygame.quit()
        
        self.running = False
        self.initialized = False
        logger.info("Pygame backend shut down")
    
    def is_running(self) -> bool:
        """Check if the Pygame backend is still running."""
        return self.running and self.initialized
    
    def process_events(self) -> List[Dict[str, Any]]:
        """Process input events from Pygame."""
        if not self.initialized:
            return []
            
        import pygame
        
        events = []
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                events.append({'type': 'quit'})
            elif event.type == pygame.MOUSEBUTTONDOWN:
                events.append({
                    'type': 'mouse_down',
                    'button': event.button,
                    'pos': event.pos
                })
            elif event.type == pygame.MOUSEBUTTONUP:
                events.append({
                    'type': 'mouse_up',
                    'button': event.button,
                    'pos': event.pos
                })
            elif event.type == pygame.MOUSEMOTION:
                events.append({
                    'type': 'mouse_move',
                    'pos': event.pos,
                    'rel': event.rel,
                    'buttons': event.buttons
                })
            elif event.type == pygame.KEYDOWN:
                events.append({
                    'type': 'key_down',
                    'key': event.key,
                    'unicode': event.unicode,
                    'mod': event.mod
                })
            elif event.type == pygame.KEYUP:
                events.append({
                    'type': 'key_up',
                    'key': event.key,
                    'mod': event.mod
                })
        
        return events

    def draw_rectangle(self, x: int, y: int, width: int, height: int,
                      color: Tuple[int, int, int, int], filled: bool = True) -> None:
        """Draw a rectangle with alpha support."""
        if not self.initialized:
            return

        import pygame

        if filled:
            # Handle alpha channel properly
            if len(color) > 3 and color[3] < 255:
                # Create a surface with per-pixel alpha
                surface = pygame.Surface((width, height), pygame.SRCALPHA)
                surface.fill(color)
                self.screen.blit(surface, (x, y))
            else:
                # Use the faster draw.rect for opaque rectangles
                pygame.draw.rect(self.screen, color[:3], (x, y, width, height))
        else:
            # Draw outline only
            pygame.draw.rect(self.screen, color[:3], (x, y, width, height), 1)

        self.render_stats["draw_calls"] += 1
    
    def draw_rounded_rectangle(self, x: int, y: int, width: int, height: int,
                              color: Tuple[int, int, int, int], radius: int = 5,
                              border_color: Optional[Tuple[int, int, int, int]] = None,
                              border_width: int = 0) -> None:
        """Draw a rounded rectangle using Pygame."""
        if not self.initialized:
            return
            
        import pygame
        
        # Draw the filled rounded rectangle
        rect = pygame.Rect(x, y, width, height)
        pygame.draw.rect(self.screen, color[:3], rect, 0, radius)
        
        # Draw the border if specified
        if border_color is not None and border_width > 0:
            pygame.draw.rect(self.screen, border_color[:3], rect, border_width, radius)
        
        self.render_stats["draw_calls"] += 1
    
    def draw_line(self, x1: int, y1: int, x2: int, y2: int, 
                 color: Tuple[int, int, int, int], thickness: int = 1) -> None:
        """Draw a line using Pygame."""
        if not self.initialized:
            return
            
        import pygame
        pygame.draw.line(self.screen, color[:3], (x1, y1), (x2, y2), thickness)
        self.render_stats["draw_calls"] += 1
    
    def draw_text(self, x: int, y: int, text: str, font_size: int = 16,
                 color: Tuple[int, int, int, int] = (255, 255, 255, 255),
                 align: str = "left", font_name: str = "default",
                 center_vertically: bool = False) -> Tuple[int, int]:
        """Draw text using Pygame."""
        if not self.initialized or not text:
            return (0, 0)
            
        import pygame
        
        # Get the font (or load it if not cached)
        font_key = f"{font_name}_{font_size}"
        if font_key not in self.font_cache:
            if font_name == "default":
                font = pygame.font.Font(None, font_size)
            else:
                try:
                    font = pygame.font.SysFont(font_name, font_size)
                except:
                    font = pygame.font.Font(None, font_size)
            self.font_cache[font_key] = font
        else:
            font = self.font_cache[font_key]
            
        # Render the text
        text_surface = font.render(text, True, color[:3])
        text_rect = text_surface.get_rect()
        
        # Apply alignment
        if align == "center":
            text_rect.centerx = x
        elif align == "right":
            text_rect.right = x
        else:  # left alignment
            text_rect.left = x
            
        # Apply vertical centering if requested
        if center_vertically:
            text_rect.centery = y
        else:
            text_rect.top = y
            
        # Draw the text
        self.screen.blit(text_surface, text_rect)
        self.render_stats["draw_calls"] += 1
        
        return (text_rect.width, text_rect.height)
    
    def draw_circle(self, x: int, y: int, radius: int,
                   color: Tuple[int, int, int, int],
                   border_color: Optional[Tuple[int, int, int, int]] = None,
                   border_width: int = 0, filled: bool = True) -> None:
        """Draw a circle using Pygame."""
        if not self.initialized:
            return

        import pygame

        if filled:
            # Draw filled circle
            pygame.draw.circle(self.screen, color[:3], (x, y), radius)
        else:
            # Draw outline only
            pygame.draw.circle(self.screen, color[:3], (x, y), radius, 1)

        # Draw border if specified
        if border_color is not None and border_width > 0:
            pygame.draw.circle(self.screen, border_color[:3], (x, y), radius, border_width)

        self.render_stats["draw_calls"] += 1
    
    def draw_image(self, x: int, y: int, image_path: str, 
                  width: Optional[int] = None, height: Optional[int] = None) -> None:
        """Draw an image using Pygame."""
        if not self.initialized:
            return
            
        import pygame
        
        # Load the image (or get from cache)
        if image_path not in self.image_cache:
            try:
                image = pygame.image.load(image_path)
                self.image_cache[image_path] = image
            except Exception as e:
                logger.error(f"Error loading image {image_path}: {e}")
                return
        else:
            image = self.image_cache[image_path]
            
        # Resize if requested
        if width is not None and height is not None:
            image = pygame.transform.scale(image, (width, height))
            
        # Draw the image
        self.screen.blit(image, (x, y))
        self.render_stats["draw_calls"] += 1

    # Draw specialized UI elements with batching for performance
    def draw_ui_element(self, element_type: str, rect: Tuple[int, int, int, int], 
                       color: Tuple[int, int, int, int], **kwargs):
        """Draw specialized UI elements with optimized rendering."""
        if not self.initialized:
            return
            
        import pygame
        
        x, y, width, height = rect
        
        if element_type == "button":
            # Draw a button with highlight, shadow, and text
            highlight = kwargs.get("highlight", False)
            text = kwargs.get("text", "")
            
            # Base button
            self.draw_rounded_rectangle(x, y, width, height, 
                                     color, 
                                     radius=kwargs.get("radius", 5),
                                     border_color=kwargs.get("border_color", None),
                                     border_width=kwargs.get("border_width", 1))
            
            # Draw text if provided
            if text:
                self.draw_text(
                    x + width // 2, 
                    y + height // 2,
                    text,
                    font_size=kwargs.get("font_size", 16),
                    color=kwargs.get("text_color", (255, 255, 255, 255)),
                    align="center",
                    center_vertically=True
                )
        
        elif element_type == "panel":
            # Draw a panel with optional shadow
            shadow = kwargs.get("shadow", False)
            
            if shadow:
                # Draw shadow first
                shadow_offset = kwargs.get("shadow_offset", 5)
                shadow_color = kwargs.get("shadow_color", (0, 0, 0, 128))
                self.draw_rounded_rectangle(
                    x + shadow_offset, 
                    y + shadow_offset, 
                    width, height, 
                    shadow_color, 
                    radius=kwargs.get("radius", 5)
                )
            
            # Draw the panel
            self.draw_rounded_rectangle(
                x, y, width, height,
                color,
                radius=kwargs.get("radius", 5),
                border_color=kwargs.get("border_color", None),
                border_width=kwargs.get("border_width", 1)
            )
        
        self.render_stats["draw_calls"] += 1
        
    def get_render_stats(self) -> Dict[str, Any]:
        """Get the current rendering statistics."""
        return self.render_stats.copy()

class WebGLBackend(RenderBackend):
    """WebGL-based rendering backend for web clients."""
    
    def __init__(self):
        """Initialize the WebGL backend."""
        self.initialized = False
        self.running = False
        self.width = 800
        self.height = 600
        
    def initialize(self, width: int, height: int, title: str = "MetaMindIQTrain") -> bool:
        """Initialize the WebGL backend.
        
        Args:
            width: Canvas width
            height: Canvas height
            title: Page title
            
        Returns:
            True if initialization was successful, False otherwise
        """
        try:
            # This is a placeholder for WebGL initialization
            # In a real implementation, this would integrate with a JavaScript bridge
            
            self.width = width
            self.height = height
            self.running = True
            self.initialized = True
            
            logger.info(f"WebGL backend initialized ({width}x{height})")
            return True
            
        except Exception as e:
            logger.error(f"Error initializing WebGL backend: {e}")
            return False
            
    # Implement other abstract methods with WebGL-specific implementations
    # For brevity, these are not fully implemented here but would be in a real implementation
    
    def clear(self, color: Tuple[int, int, int, int] = (0, 0, 0, 255)) -> None:
        """Clear the canvas with the specified color."""
        pass
        
    def present(self) -> None:
        """Present the rendered frame to the screen."""
        pass
        
    def shutdown(self) -> None:
        """Shut down the WebGL backend."""
        pass
        
    def is_running(self) -> bool:
        """Check if the WebGL backend is still running."""
        return self.running
        
    def process_events(self) -> List[Dict[str, Any]]:
        """Process input events."""
        return []
        
    def draw_rectangle(self, x: int, y: int, width: int, height: int,
                      color: Tuple[int, int, int, int], filled: bool = True) -> None:
        """Draw a rectangle."""
        pass
        
    def draw_rounded_rectangle(self, x: int, y: int, width: int, height: int,
                              color: Tuple[int, int, int, int], radius: int = 5,
                              border_color: Optional[Tuple[int, int, int, int]] = None,
                              border_width: int = 0) -> None:
        """Draw a rounded rectangle."""
        pass
        
    def draw_line(self, x1: int, y1: int, x2: int, y2: int, 
                 color: Tuple[int, int, int, int], thickness: int = 1) -> None:
        """Draw a line."""
        pass
        
    def draw_text(self, x: int, y: int, text: str, font_size: int = 16,
                 color: Tuple[int, int, int, int] = (255, 255, 255, 255),
                 align: str = "left", font_name: str = "default",
                 center_vertically: bool = False) -> Tuple[int, int]:
        """Draw text."""
        return (0, 0)
        
    def draw_circle(self, x: int, y: int, radius: int,
                   color: Tuple[int, int, int, int],
                   border_color: Optional[Tuple[int, int, int, int]] = None,
                   border_width: int = 0, filled: bool = True) -> None:
        """Draw a circle."""
        pass
        
    def draw_image(self, x: int, y: int, image_path: str, 
                  width: Optional[int] = None, height: Optional[int] = None) -> None:
        """Draw an image."""
        pass

class HeadlessBackend(RenderBackend):
    """Headless rendering backend for testing and server-side rendering."""
    
    def __init__(self):
        """Initialize the headless backend."""
        self.initialized = False
        self.running = False
        self.width = 800
        self.height = 600
        self.rendered_elements = []
        
    def initialize(self, width: int, height: int, title: str = "MetaMindIQTrain") -> bool:
        """Initialize the headless backend.
        
        Args:
            width: Virtual canvas width
            height: Virtual canvas height
            title: Ignored in headless mode
            
        Returns:
            True if initialization was successful
        """
        self.width = width
        self.height = height
        self.running = True
        self.initialized = True
        logger.info(f"Headless backend initialized ({width}x{height})")
        return True
        
    def clear(self, color: Tuple[int, int, int, int] = (0, 0, 0, 255)) -> None:
        """Clear the virtual canvas."""
        self.rendered_elements = []
        self.rendered_elements.append({
            'type': 'clear',
            'color': color
        })
        
    def present(self) -> None:
        """Virtual presentation (does nothing in headless mode)."""
        self.rendered_elements.append({'type': 'present'})
        
    def shutdown(self) -> None:
        """Shut down the headless backend."""
        self.running = False
        self.initialized = False
        self.rendered_elements = []
        logger.info("Headless backend shut down")
        
    def is_running(self) -> bool:
        """Check if the headless backend is still running."""
        return self.running
        
    def process_events(self) -> List[Dict[str, Any]]:
        """Process events (returns empty list in headless mode)."""
        return []
        
    def draw_rectangle(self, x: int, y: int, width: int, height: int,
                      color: Tuple[int, int, int, int], filled: bool = True) -> None:
        """Record a rectangle drawing in headless mode."""
        self.rendered_elements.append({
            'type': 'rectangle',
            'x': x,
            'y': y,
            'width': width,
            'height': height,
            'color': color,
            'filled': filled
        })
        
    def draw_rounded_rectangle(self, x: int, y: int, width: int, height: int,
                              color: Tuple[int, int, int, int], radius: int = 5,
                              border_color: Optional[Tuple[int, int, int, int]] = None,
                              border_width: int = 0) -> None:
        """Record a rounded rectangle drawing in headless mode."""
        self.rendered_elements.append({
            'type': 'rounded_rectangle',
            'x': x,
            'y': y,
            'width': width,
            'height': height,
            'color': color,
            'radius': radius,
            'border_color': border_color,
            'border_width': border_width
        })
        
    def draw_line(self, x1: int, y1: int, x2: int, y2: int, 
                 color: Tuple[int, int, int, int], thickness: int = 1) -> None:
        """Record a line drawing in headless mode."""
        self.rendered_elements.append({
            'type': 'line',
            'x1': x1,
            'y1': y1,
            'x2': x2,
            'y2': y2,
            'color': color,
            'thickness': thickness
        })
        
    def draw_text(self, x: int, y: int, text: str, font_size: int = 16,
                 color: Tuple[int, int, int, int] = (255, 255, 255, 255),
                 align: str = "left", font_name: str = "default",
                 center_vertically: bool = False) -> Tuple[int, int]:
        """Record a text drawing in headless mode."""
        # Simulate dimensions - not accurate but provides something
        text_width = len(text) * font_size * 0.6
        text_height = font_size * 1.2
        
        self.rendered_elements.append({
            'type': 'text',
            'x': x,
            'y': y,
            'text': text,
            'font_size': font_size,
            'color': color,
            'align': align,
            'font_name': font_name,
            'center_vertically': center_vertically
        })
        
        return (int(text_width), int(text_height))
        
    def draw_circle(self, x: int, y: int, radius: int,
                   color: Tuple[int, int, int, int],
                   border_color: Optional[Tuple[int, int, int, int]] = None,
                   border_width: int = 0, filled: bool = True) -> None:
        """Record a circle drawing in headless mode."""
        self.rendered_elements.append({
            'type': 'circle',
            'x': x,
            'y': y,
            'radius': radius,
            'color': color,
            'border_color': border_color,
            'border_width': border_width,
            'filled': filled
        })
        
    def draw_image(self, x: int, y: int, image_path: str, 
                  width: Optional[int] = None, height: Optional[int] = None) -> None:
        """Record an image drawing in headless mode."""
        self.rendered_elements.append({
            'type': 'image',
            'x': x,
            'y': y,
            'image_path': image_path,
            'width': width,
            'height': height
        })
        
    def get_rendered_elements(self) -> List[Dict[str, Any]]:
        """Get the list of rendered elements.
        
        This is useful for testing or generating serialized rendering instructions.
        
        Returns:
            List of dictionaries describing rendered elements
        """
        return self.rendered_elements.copy()

class Renderer:
    """Unified renderer with optimized rendering pipeline."""
    
    # Initialize singleton instance
    _instance = None
    
    @classmethod
    def get_instance(cls):
        """Get the singleton renderer instance."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        """Initialize the renderer."""
        self.backend = None
        self.backend_name = None
        self.width = 800
        self.height = 600
        self.initialized = False
        
        # For compatibility with test_renderer()
        self.batch_enabled = True
    
    def enable_batching(self, enabled: bool = True):
        """Enable or disable render batching for performance (stub for compatibility)."""
        self.batch_enabled = enabled
    
    def queue_render(self, render_type: str, *args, **kwargs):
        """Queue a render command (stub for compatibility)."""
        # Just execute immediately as a fallback
        if render_type == "rectangle":
            self.draw_rectangle(*args, **kwargs)
        elif render_type == "ui_element":
            element_type = args[0]
            rect = args[1]
            color = args[2]
            self.draw_ui_element(element_type, rect, color, **kwargs)
    
    def flush_queue(self):
        """Flush the render queue (stub for compatibility)."""
        pass
    
    def get_stats(self):
        """Get rendering statistics (stub for compatibility)."""
        if self.backend and hasattr(self.backend, 'get_render_stats'):
            return self.backend.get_render_stats()
        return {}
    
    def draw_ui_element(self, element_type: str, rect, color, **kwargs):
        """Draw a UI element (stub for compatibility)."""
        x, y, width, height = rect
        
        if element_type == "button":
            self.draw_rounded_rectangle(x, y, width, height, color, radius=5)
            
            # Draw text if provided
            if "text" in kwargs:
                self.draw_text(
                    x + width // 2, 
                    y + height // 2,
                    kwargs.get("text", ""),
                    color=kwargs.get("text_color", (255, 255, 255, 255)),
                    align="center",
                    center_vertically=True
                )

    def initialize(self, width: int, height: int, backend: str = "auto",
                  title: str = "MetaMindIQTrain") -> bool:
        """Initialize the renderer with specified backend.

        Args:
            width: Window width
            height: Window height
            backend: Renderer backend to use ('auto', 'pygame', 'webgl', 'headless')
            title: Window title

        Returns:
            True if initialization was successful, False otherwise
        """
        self.width = width
        self.height = height

        if backend == "auto":
            # Try backends in order: pygame, webgl, headless
            pygame_backend = PygameBackend()
            if pygame_backend.initialize(width, height, title):
                self.backend = pygame_backend
                self.backend_name = "pygame"
            else:
                webgl_backend = WebGLBackend()
                if webgl_backend.initialize(width, height, title):
                    self.backend = webgl_backend
                    self.backend_name = "webgl"
                else:
                    headless_backend = HeadlessBackend()
                    if headless_backend.initialize(width, height, title):
                        self.backend = headless_backend
                        self.backend_name = "headless"
                    else:
                        logger.error("All backends failed to initialize")
                        return False
        elif backend == "pygame":
            pygame_backend = PygameBackend()
            if pygame_backend.initialize(width, height, title):
                self.backend = pygame_backend
                self.backend_name = "pygame"
            else:
                return False
        elif backend == "webgl":
            webgl_backend = WebGLBackend()
            if webgl_backend.initialize(width, height, title):
                self.backend = webgl_backend
                self.backend_name = "webgl"
            else:
                return False
        elif backend == "headless":
            headless_backend = HeadlessBackend()
            if headless_backend.initialize(width, height, title):
                self.backend = headless_backend
                self.backend_name = "headless"
            else:
                return False
        else:
            logger.error(f"Unknown backend: {backend}")
            return False

        logger.info(f"Using renderer backend: {self.backend_name}")
        self.initialized = True
        return True

    def shutdown(self) -> None:
        """Shut down the renderer and active backend."""
        if self.backend:
            self.backend.shutdown()
            self.backend = None
            
    def clear(self, color: Tuple[int, int, int, int] = (0, 0, 0, 255)) -> None:
        """Clear the screen/canvas."""
        if self.backend:
            self.backend.clear(color)
            
    def present(self) -> None:
        """Present the rendered frame."""
        if self.backend:
            self.backend.present()
            
    def is_running(self) -> bool:
        """Check if the renderer is still running."""
        return self.backend and self.backend.is_running()
        
    def process_events(self) -> List[Dict[str, Any]]:
        """Process input events from the active backend.
        
        Returns:
            List of event dictionaries
        """
        if self.backend:
            return self.backend.process_events()
        return []
        
    def get_backend_name(self) -> Optional[str]:
        """Get the name of the active backend.
        
        Returns:
            Backend name or None if no backend is active
        """
        return self.backend_name
        
    # Forward drawing methods to the active backend
    
    def draw_rectangle(self, x: int, y: int, width: int, height: int,
                      color: Tuple[int, int, int, int], filled: bool = True) -> None:
        """Draw a rectangle."""
        if self.backend:
            self.backend.draw_rectangle(x, y, width, height, color, filled)
            
    def draw_rounded_rectangle(self, x: int, y: int, width: int, height: int,
                              color: Tuple[int, int, int, int], radius: int = 5,
                              border_color: Optional[Tuple[int, int, int, int]] = None,
                              border_width: int = 0) -> None:
        """Draw a rounded rectangle."""
        if self.backend:
            self.backend.draw_rounded_rectangle(
                x, y, width, height, color, radius, border_color, border_width
            )
            
    def draw_line(self, x1: int, y1: int, x2: int, y2: int,
                 color: Tuple[int, int, int, int], thickness: int = 1,
                 width: int = None) -> None:
        """Draw a line.

        Args:
            thickness: Line thickness in pixels (default 1)
            width: Alias for thickness (for compatibility)
        """
        if self.backend:
            line_width = width if width is not None else thickness
            self.backend.draw_line(x1, y1, x2, y2, color, line_width)
            
    def draw_text(self, x: int, y: int, text: str, font_size: int = 16,
                 color: Tuple[int, int, int, int] = (255, 255, 255, 255),
                 align: str = "left", font_name: str = "default",
                 center_vertically: bool = False) -> Tuple[int, int]:
        """Draw text.
        
        Returns:
            Tuple of (width, height) of the rendered text
        """
        if self.backend:
            return self.backend.draw_text(
                x, y, text, font_size, color, align, font_name, center_vertically
            )
        return (0, 0)
        
    def draw_circle(self, x: int, y: int, radius: int,
                   color: Tuple[int, int, int, int],
                   border_color: Optional[Tuple[int, int, int, int]] = None,
                   border_width: int = 0, filled: bool = True) -> None:
        """Draw a circle."""
        if self.backend:
            self.backend.draw_circle(x, y, radius, color, border_color, border_width, filled)
            
    def draw_image(self, x: int, y: int, image_path: str, 
                  width: Optional[int] = None, height: Optional[int] = None) -> None:
        """Draw an image."""
        if self.backend:
            self.backend.draw_image(x, y, image_path, width, height)
            
    def get_size(self) -> Tuple[int, int]:
        """Get the size of the rendering surface.
        
        Returns:
            Tuple of (width, height)
        """
        return (self.width, self.height)
            
    def render_component(self, component) -> None:
        """Render a component using its render method.
        
        Args:
            component: Component to render (must have a render method)
        """
        if hasattr(component, 'render') and callable(component.render):
            component.render(self)

# Singleton instance
_renderer_instance = None

def get_renderer() -> Renderer:
    """Get the singleton renderer instance.
    
    Returns:
        Renderer instance
    """
    global _renderer_instance
    if _renderer_instance is None:
        _renderer_instance = Renderer()
    return _renderer_instance 