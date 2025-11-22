import logging
import time
from enum import Enum
from typing import Dict, List, Any, Tuple, Optional, Union, Callable

# Try to import theme system
try:
    from . import theme
except ImportError:
    # For direct execution or during development
    import sys
    import os
    from pathlib import Path
    current_dir = Path(__file__).parent
    if str(current_dir) not in sys.path:
        sys.path.insert(0, str(current_dir))
    import theme

class UnifiedRenderer:
    """Base class for all renderers with shared functionality."""
    
    def __init__(self, width=800, height=600, target_fps=60, platform="unknown"):
        """Initialize the renderer.
        
        Args:
            width: Screen width
            height: Screen height
            target_fps: Target frames per second
            platform: Platform identifier (pygame, web, etc.)
        """
        self.width = width
        self.height = height
        self.target_fps = target_fps
        self.platform = platform
        self.components = []
        self.dirty_regions = []
        self.event_listeners = {}
        self.transition_effects = {}
        self.active_transitions = []
        
        # Initialize with default theme based on platform
        if not theme.get_theme():
            theme.set_theme(theme.Theme.default_theme(platform))
        
        # Cached surfaces for performance
        self._cached_surfaces = {}
        self._surface_cache_limit = 100
        
        # Tracks when surface caches should be invalidated
        self._component_last_updated = {}
        
        # Performance metrics
        self.frame_times = []
        self.render_times = []
        self.max_frame_times = 100  # Keep last 100 frames for metrics
        
        # FPS calculation
        self.last_fps_time = time.time()
        self.frame_count = 0
        self.current_fps = 0
        
        logging.info(f"Initialized {self.__class__.__name__} ({width}x{height}, {target_fps} FPS)")
    
    def apply_theme(self, new_theme=None):
        """Apply a new theme to the renderer.
        
        Args:
            new_theme: Theme instance to apply, or None to use default
        """
        if new_theme is None:
            new_theme = theme.Theme.default_theme(self.platform)
        
        theme.set_theme(new_theme)
        
        # Clear all caches as style properties may have changed
        self._cached_surfaces = {}
        self._component_last_updated = {}
        
        # Mark entire screen as dirty
        self.mark_dirty(0, 0, self.width, self.height)
        
        logging.info(f"Applied new theme to renderer")
    
    # ... existing code ... 