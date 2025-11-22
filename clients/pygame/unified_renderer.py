#!/usr/bin/env python3
"""
Unified Pygame Renderer for MetaMindIQTrain

High-performance renderer with surface caching, batch rendering,
and efficient state management.
"""

import pygame
import time
import logging
from typing import Dict, List, Any, Optional
import sys
from pathlib import Path

# Add project root to path for imports
if __name__ == "__main__":
    project_root = Path(__file__).parent.parent.parent
    sys.path.insert(0, str(project_root))

# Import render utilities
from MetaMindIQTrain.clients.pygame.render_utils import (
    SurfaceCache, SurfacePool, RenderBatch, TransitionEffect,
    lighten_color, darken_color
)

# Import component system
try:
    from MetaMindIQTrain.core.unified_component_system import (
        Component, UI, ComponentFactory, get_stats, reset_stats
    )
    from MetaMindIQTrain.core.theme import Theme, get_theme, set_theme
except ImportError:
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))
    from core.unified_component_system import (
        Component, UI, ComponentFactory, get_stats, reset_stats
    )
    from core.theme import Theme, get_theme, set_theme

logger = logging.getLogger(__name__)

# Default color palette
DEFAULT_COLORS = {
    "background": (30, 36, 44),
    "cell_background": (40, 44, 52),
    "text": (255, 255, 255),
    "primary": (0, 120, 255),
    "secondary": (80, 80, 200),
    "accent": (255, 149, 0),
    "warning": (255, 225, 50),
    "error": (255, 50, 50),
    "success": (50, 255, 50),
    "border": (100, 100, 160),
    "highlight": (255, 220, 115),
    "hover": (50, 56, 66),
    "cell_highlight": (60, 120, 255, 180),
}


class UnifiedRenderer:
    """Unified renderer for MetaMindIQTrain with pygame."""

    def __init__(self, screen_width=1440, screen_height=1024, title="MetaMindIQTrain"):
        """Initialize the renderer."""
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
        self.fonts = {}

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

        # Initialize theme
        if not get_theme():
            set_theme(Theme.default_theme(platform="pygame"))

        self.colors = get_theme().colors

        # Transition support
        self.transition = None
        self.transition_surface = None

    def initialize(self) -> bool:
        """Initialize pygame and the renderer."""
        try:
            pygame.init()
            self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
            pygame.display.set_caption(self.title)
            self.clock = pygame.time.Clock()
            self.ui = UI(self.screen_width, self.screen_height)
            self.start_time = time.time()
            self.running = True
            logger.info(f"Renderer initialized: {self.screen_width}x{self.screen_height}")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize renderer: {e}")
            return False

    def shutdown(self) -> None:
        """Shut down the renderer."""
        try:
            self.surface_cache.clear()
            self.surface_pool.clear()
            pygame.quit()
            logger.info("Renderer shut down")
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")

    def process_events(self) -> List[Dict[str, Any]]:
        """Process pygame events."""
        events = []
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                events.append({"type": "quit"})
            elif event.type == pygame.MOUSEBUTTONDOWN:
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
        """Check if the renderer is still running."""
        return self.running

    def get_font(self, name=None, size=24) -> pygame.font.Font:
        """Get a font from cache or create new one."""
        if name is None:
            name = pygame.font.get_default_font()

        key = (name, size)
        if key not in self.fonts:
            try:
                self.fonts[key] = pygame.font.Font(name, size)
            except:
                self.fonts[key] = pygame.font.SysFont("Arial", size)

        return self.fonts[key]

    def render(self, state: Dict[str, Any]) -> None:
        """Render the current state."""
        start_time = time.time()

        # Handle transitions
        if self.transition and self.transition.is_active:
            original_screen = self.screen
            self.screen = self.transition_surface
            self.screen.fill(self.colors["background"])
        else:
            self.screen.fill(self.colors["background"])

        # Update UI from state
        if "ui" in state:
            self.update_ui_from_state(state["ui"])

        if not self.ui:
            pygame.display.flip()
            self.render_time = time.time() - start_time
            self.frame_count += 1
            return

        # Calculate layout
        if not self.ui.layout_calculated:
            self.ui.calculate_layout()

        self.dirty_regions = []

        # Render component tree
        self.render_component_tree(self.ui.root)

        # Flush batches
        for batch in self.batches.values():
            batch.render()

        # Handle transition rendering
        if self.transition and self.transition.is_active:
            self.screen = original_screen
            self.transition.update()
            rect = pygame.Rect(0, 0, self.screen_width, self.screen_height)
            self.transition.render(self.screen, rect)
            pygame.display.flip()
        else:
            if len(self.dirty_regions) > 5:
                pygame.display.flip()
            elif self.dirty_regions:
                pygame.display.update(self.dirty_regions)
            else:
                pygame.display.flip()

        self.render_time = time.time() - start_time
        self.frame_count += 1

        # Periodic cache cleanup
        if self.frame_count % 300 == 0:
            self.surface_cache.clean_expired()

    def update_ui_from_state(self, ui_state: Dict[str, Any]) -> None:
        """Update UI from a state dictionary."""
        self.ui.clear()
        if "components" in ui_state:
            for component_data in ui_state["components"]:
                component = create_component_tree(component_data)
                self.ui.add(component)

    def render_component_tree(self, component: Component) -> None:
        """Render a component and its children."""
        if not component.needs_render():
            return

        self.render_component(component)

        for child in component.children:
            self.render_component_tree(child)

        component.mark_clean()

    def render_component(self, component: Component) -> None:
        """Render a single component."""
        layout = component.layout
        screen_rect = pygame.Rect(0, 0, self.screen_width, self.screen_height)
        component_rect = pygame.Rect(layout['x'], layout['y'], layout['width'], layout['height'])

        if not screen_rect.colliderect(component_rect):
            return

        if self.batch_enabled and component.type in self.batches:
            self.batches[component.type].add(component)
            return

        self.dirty_regions.append(component_rect)

        # Try cache first
        component_hash = component.hash_for_rendering()
        cached_surface = self.surface_cache.get(component_hash)
        if cached_surface:
            self.screen.blit(cached_surface, (layout['x'], layout['y']))
            return

        # Render based on component type
        render_method = getattr(self, f'_render_{component.type}', None)
        if render_method:
            render_method(component)
        else:
            logger.warning(f"Unknown component type: {component.type}")

    def _render_rect(self, component: Component) -> None:
        """Render a rectangle component."""
        layout = component.layout
        bg_color = component.style.get('backgroundColor', self.colors["secondary"])
        border_width = component.style.get('borderWidth', 0)
        border_color = component.style.get('borderColor', self.colors["border"])
        border_radius = component.style.get('borderRadius', 0)

        flags = pygame.SRCALPHA if len(bg_color) == 4 and bg_color[3] < 255 else 0
        surface = self.surface_pool.get(layout['width'], layout['height'], flags)

        if flags & pygame.SRCALPHA:
            surface.fill((0, 0, 0, 0))
        else:
            surface.fill((0, 0, 0))

        rect = pygame.Rect(0, 0, layout['width'], layout['height'])

        if border_radius > 0:
            pygame.draw.rect(surface, bg_color, rect, 0, border_radius)
            if border_width > 0:
                pygame.draw.rect(surface, border_color, rect, border_width, border_radius)
        else:
            pygame.draw.rect(surface, bg_color, rect, 0)
            if border_width > 0:
                pygame.draw.rect(surface, border_color, rect, border_width)

        self.screen.blit(surface, (layout['x'], layout['y']))
        self.surface_cache.set(component.hash_for_rendering(), surface)
        self.surface_pool.release(surface)

    def _render_circle(self, component: Component) -> None:
        """Render a circle component."""
        layout = component.layout
        radius = component.props.get('radius', min(layout['width'], layout['height']) // 2)
        bg_color = component.style.get('backgroundColor', self.colors["secondary"])
        border_width = component.style.get('borderWidth', 0)
        border_color = component.style.get('borderColor', self.colors["border"])

        flags = pygame.SRCALPHA if len(bg_color) == 4 and bg_color[3] < 255 else 0
        surface = self.surface_pool.get(layout['width'], layout['height'], flags)

        if flags & pygame.SRCALPHA:
            surface.fill((0, 0, 0, 0))
        else:
            surface.fill((0, 0, 0))

        center = (layout['width'] // 2, layout['height'] // 2)
        pygame.draw.circle(surface, bg_color, center, radius, 0)
        if border_width > 0:
            pygame.draw.circle(surface, border_color, center, radius, border_width)

        self.screen.blit(surface, (layout['x'], layout['y']))
        self.surface_cache.set(component.hash_for_rendering(), surface)
        self.surface_pool.release(surface)

    def _render_text(self, component: Component) -> None:
        """Render a text component."""
        layout = component.layout
        text = component.props.get('text', '')
        font_name = component.style.get('fontFamily', None)
        font_size = component.style.get('fontSize', 24)
        color = component.style.get('color', self.colors["text"])
        align = component.style.get('textAlign', 'left')
        bg_color = component.style.get('backgroundColor', None)
        padding = component.style.get('padding', 0)
        line_height = component.style.get('lineHeight', 1.2)

        font = self.get_font(font_name, font_size)
        surface = self.surface_pool.get(layout['width'], layout['height'], pygame.SRCALPHA)
        surface.fill((0, 0, 0, 0))

        if '\n' in text:
            lines = text.split('\n')
            y_offset = padding

            for line in lines:
                if not line.strip():
                    y_offset += font_size * line_height
                    continue

                line_surf = font.render(line, True, color)
                rect = line_surf.get_rect()

                if align == 'center':
                    rect.centerx = layout['width'] // 2
                elif align == 'right':
                    rect.right = layout['width'] - padding
                else:
                    rect.left = padding

                rect.y = int(y_offset)
                surface.blit(line_surf, rect)
                y_offset += font_size * line_height
        else:
            text_surface = font.render(text, True, color)
            text_rect = text_surface.get_rect()

            if align == 'center':
                text_rect.center = (layout['width'] // 2, layout['height'] // 2)
            elif align == 'right':
                text_rect.midright = (layout['width'] - padding, layout['height'] // 2)
            else:
                text_rect.midleft = (padding, layout['height'] // 2)

            if bg_color:
                bg_rect = text_rect.inflate(padding * 2, padding * 2)
                border_radius = component.style.get('borderRadius', 0)
                pygame.draw.rect(surface, bg_color, bg_rect, 0, border_radius)

            surface.blit(text_surface, text_rect)

        self.screen.blit(surface, (layout['x'], layout['y']))
        self.surface_cache.set(component.hash_for_rendering(), surface)
        self.surface_pool.release(surface)

    def _render_image(self, component: Component) -> None:
        """Render an image component."""
        layout = component.layout
        image_src = component.props.get('src', '')

        try:
            image = pygame.image.load(image_src)
            if image.get_width() != layout['width'] or image.get_height() != layout['height']:
                image = pygame.transform.smoothscale(image, (layout['width'], layout['height']))
            self.screen.blit(image, (layout['x'], layout['y']))
        except Exception as e:
            logger.error(f"Failed to load image {image_src}: {e}")
            rect = pygame.Rect(layout['x'], layout['y'], layout['width'], layout['height'])
            pygame.draw.rect(self.screen, self.colors["error"], rect, 2)

    def _render_button(self, component: Component) -> None:
        """Render a button component."""
        layout = component.layout
        text = component.props.get('text', '')
        bg_color = component.style.get('backgroundColor', self.colors["primary"])
        text_color = component.style.get('color', self.colors["text"])
        border_radius = component.style.get('borderRadius', 8)
        border_width = component.style.get('borderWidth', 0)
        border_color = component.style.get('borderColor', self.colors["border"])
        font_size = component.style.get('fontSize', 24)
        hover = component.props.get('hover', False)
        active = component.props.get('active', False)

        surface = self.surface_pool.get(layout['width'] + 4, layout['height'] + 4, pygame.SRCALPHA)
        surface.fill((0, 0, 0, 0))

        button_rect = pygame.Rect(0, 0, layout['width'], layout['height'])
        actual_bg_color = bg_color

        if active:
            actual_bg_color = darken_color(bg_color, 0.2)
        elif hover:
            actual_bg_color = lighten_color(bg_color, 0.1)

        # Shadow
        shadow_rect = button_rect.copy()
        shadow_rect.x += 2
        shadow_rect.y += 2
        pygame.draw.rect(surface, (0, 0, 0, 80), shadow_rect, 0, border_radius)

        # Button
        pygame.draw.rect(surface, actual_bg_color, button_rect, 0, border_radius)
        if border_width > 0:
            pygame.draw.rect(surface, border_color, button_rect, border_width, border_radius)

        # Text
        font = self.get_font(None, font_size)
        text_surface = font.render(text, True, text_color)
        text_rect = text_surface.get_rect(center=button_rect.center)
        surface.blit(text_surface, text_rect)

        self.screen.blit(surface, (layout['x'] - 2, layout['y'] - 2))
        self.surface_cache.set(component.hash_for_rendering(), surface)
        self.surface_pool.release(surface)

    def _render_grid(self, component: Component) -> None:
        """Render a grid component."""
        layout = component.layout
        rows = component.props.get('rows', 1)
        cols = component.props.get('cols', 1)
        line_color = component.style.get('borderColor', self.colors["border"])
        line_width = component.style.get('borderWidth', 1)
        bg_color = component.style.get('backgroundColor', None)

        surface = self.surface_pool.get(layout['width'], layout['height'], pygame.SRCALPHA)
        surface.fill((0, 0, 0, 0))

        if bg_color:
            pygame.draw.rect(surface, bg_color, pygame.Rect(0, 0, layout['width'], layout['height']))

        cell_width = layout['width'] / cols
        cell_height = layout['height'] / rows

        for i in range(rows + 1):
            y = i * cell_height
            pygame.draw.line(surface, line_color, (0, y), (layout['width'], y), line_width)

        for i in range(cols + 1):
            x = i * cell_width
            pygame.draw.line(surface, line_color, (x, 0), (x, layout['height']), line_width)

        self.screen.blit(surface, (layout['x'], layout['y']))
        self.surface_cache.set(component.hash_for_rendering(), surface)
        self.surface_pool.release(surface)

    def _render_container(self, component: Component) -> None:
        """Render a container component."""
        layout = component.layout
        bg_color = component.style.get('backgroundColor', None)
        border_width = component.style.get('borderWidth', 0)
        border_color = component.style.get('borderColor', self.colors["border"])
        border_radius = component.style.get('borderRadius', 0)

        if not bg_color and border_width <= 0:
            return

        surface = self.surface_pool.get(layout['width'], layout['height'], pygame.SRCALPHA)
        surface.fill((0, 0, 0, 0))

        rect = pygame.Rect(0, 0, layout['width'], layout['height'])

        if bg_color:
            pygame.draw.rect(surface, bg_color, rect, 0, border_radius)
        if border_width > 0:
            pygame.draw.rect(surface, border_color, rect, border_width, border_radius)

        self.screen.blit(surface, (layout['x'], layout['y']))
        self.surface_cache.set(component.hash_for_rendering(), surface)
        self.surface_pool.release(surface)

    def _render_symbol_cell(self, component: Component) -> None:
        """Render a symbol cell for memory modules."""
        layout = component.layout
        symbol = component.props.get('symbol', '')
        bg_color = component.style.get('backgroundColor', self.colors["cell_background"])
        color = component.style.get('color', self.colors["text"])
        border_width = component.style.get('borderWidth', 1)
        border_color = component.style.get('borderColor', self.colors["border"])
        border_radius = component.style.get('borderRadius', 8)
        highlighted = component.props.get('highlighted', False)
        correct = component.props.get('correct', False)
        incorrect = component.props.get('incorrect', False)

        surface = self.surface_pool.get(layout['width'], layout['height'], pygame.SRCALPHA)
        surface.fill((0, 0, 0, 0))

        actual_bg_color = bg_color
        actual_border_color = border_color

        if highlighted:
            actual_bg_color = self.colors["cell_highlight"]
            actual_border_color = self.colors["primary"]
            border_width = 2
        elif correct:
            actual_bg_color = (50, 255, 50, 80)
            actual_border_color = self.colors["success"]
            border_width = 2
        elif incorrect:
            actual_bg_color = (255, 50, 50, 80)
            actual_border_color = self.colors["error"]
            border_width = 2

        rect = pygame.Rect(0, 0, layout['width'], layout['height'])
        pygame.draw.rect(surface, actual_bg_color, rect, 0, border_radius)
        if border_width > 0:
            pygame.draw.rect(surface, actual_border_color, rect, border_width, border_radius)

        if symbol:
            font_size = min(layout['width'], layout['height']) // 2
            font = self.get_font(None, font_size)
            text_surface = font.render(symbol, True, color)
            text_rect = text_surface.get_rect(center=(layout['width'] // 2, layout['height'] // 2))
            surface.blit(text_surface, text_rect)

        self.screen.blit(surface, (layout['x'], layout['y']))
        self.surface_cache.set(component.hash_for_rendering(), surface)
        self.surface_pool.release(surface)

    def set_batch_rendering(self, enabled: bool) -> None:
        """Enable or disable batch rendering."""
        self.batch_enabled = enabled

    def start_transition(self, effect_type="fade", duration=0.5, easing="ease_out_quad"):
        """Start a transition effect."""
        if not self.screen:
            return False

        self.transition = TransitionEffect(duration, effect_type, easing)
        from_surface = self.screen.copy()
        to_surface = pygame.Surface((self.screen_width, self.screen_height), self.screen.get_flags())
        self.transition.start(from_surface, to_surface)
        self.transition_surface = to_surface
        return True

    def get_stats(self) -> Dict[str, Any]:
        """Get renderer statistics."""
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

    def apply_theme(self, new_theme=None):
        """Apply a new theme to the renderer."""
        if new_theme is None:
            new_theme = Theme.default_theme(platform="pygame")

        set_theme(new_theme)
        self.colors = get_theme().colors
        self.surface_cache.clear()
        self.fonts.clear()
        logger.info("Applied new theme to renderer")


def create_renderer(width=1440, height=1024, title="MetaMindIQTrain") -> UnifiedRenderer:
    """Create and initialize a unified renderer."""
    renderer = UnifiedRenderer(width, height, title)
    renderer.initialize()
    return renderer


def create_component_tree(data: Dict[str, Any]) -> Component:
    """Create a component tree from serialized data."""
    component = ComponentFactory.create(data.get('type', 'container'), **data)
    for child_data in data.get('children', []):
        child = create_component_tree(child_data)
        component.add_child(child)
    return component
