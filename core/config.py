"""
Configuration Module

A simplified configuration module for MetaMindIQTrain platform using Pydantic for type validation.
"""

import os
import json
import logging
from typing import Dict, Any, Optional, List, Union
from pathlib import Path
from pydantic import BaseModel, Field, validator

# Set up logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DatabaseConfig(BaseModel):
    """Database configuration."""
    type: str = "csv"  # "csv" or "mongodb"
    csv_dir: str = "data"
    mongodb_uri: Optional[str] = None
    mongodb_db: str = "metamind"

class ServerConfig(BaseModel):
    """Server configuration."""
    host: str = "0.0.0.0"
    port: int = 5000
    debug: bool = False
    cors_allowed_origins: List[str] = ["*"]
    static_folder: str = "static"
    
    # Performance settings
    worker_threads: int = 4
    message_queue_url: Optional[str] = None
    
    @validator('port')
    def port_must_be_valid(cls, v):
        if not (1024 <= v <= 65535):
            raise ValueError('Port must be between 1024 and 65535')
        return v

class LoggingConfig(BaseModel):
    """Logging configuration."""
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file: Optional[str] = None

class ModuleConfig(BaseModel):
    """Module configuration."""
    default_parameters: Dict[str, Any] = Field(default_factory=dict)
    cache_size: int = 100
    disable_metrics: bool = False

class AppConfig(BaseModel):
    """Application configuration."""
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    server: ServerConfig = Field(default_factory=ServerConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    modules: Dict[str, ModuleConfig] = Field(default_factory=dict)

# Global configuration
config = AppConfig()

def load_config(config_path: Optional[Union[str, Path]] = None, 
                env_prefix: str = "METAMIND_") -> AppConfig:
    """Load configuration from file and environment variables.
    
    Args:
        config_path: Path to configuration file
        env_prefix: Prefix for environment variables
        
    Returns:
        Loaded configuration
    """
    global config
    
    # Start with default config
    config = AppConfig()
    
    # Load from file if provided
    if config_path:
        try:
            config_path = Path(config_path)
            if config_path.exists():
                with open(config_path, 'r') as f:
                    file_config = json.load(f)
                
                # Update config with file values
                config = AppConfig.parse_obj(file_config)
                logger.info(f"Loaded configuration from {config_path}")
            else:
                logger.warning(f"Configuration file not found: {config_path}")
        except Exception as e:
            logger.error(f"Error loading configuration file: {str(e)}")
    
    # Override with environment variables
    _load_from_env(env_prefix)
    
    # Set up logging based on config
    _setup_logging()
    
    return config

def _load_from_env(prefix: str) -> None:
    """Load configuration from environment variables.
    
    Args:
        prefix: Environment variable prefix
    """
    # Server settings
    if f"{prefix}HOST" in os.environ:
        config.server.host = os.environ[f"{prefix}HOST"]
    
    if f"{prefix}PORT" in os.environ:
        try:
            config.server.port = int(os.environ[f"{prefix}PORT"])
        except ValueError:
            logger.error(f"Invalid port number: {os.environ[f'{prefix}PORT']}")
    
    if f"{prefix}DEBUG" in os.environ:
        config.server.debug = os.environ[f"{prefix}DEBUG"].lower() in ("true", "1", "yes")
    
    # Database settings
    if f"{prefix}DB_TYPE" in os.environ:
        config.database.type = os.environ[f"{prefix}DB_TYPE"]
    
    if f"{prefix}DB_CSV_DIR" in os.environ:
        config.database.csv_dir = os.environ[f"{prefix}DB_CSV_DIR"]
    
    if f"{prefix}DB_MONGODB_URI" in os.environ:
        config.database.mongodb_uri = os.environ[f"{prefix}DB_MONGODB_URI"]
    
    if f"{prefix}DB_MONGODB_DB" in os.environ:
        config.database.mongodb_db = os.environ[f"{prefix}DB_MONGODB_DB"]
    
    # Logging settings
    if f"{prefix}LOG_LEVEL" in os.environ:
        config.logging.level = os.environ[f"{prefix}LOG_LEVEL"]
    
    if f"{prefix}LOG_FILE" in os.environ:
        config.logging.file = os.environ[f"{prefix}LOG_FILE"]

def _setup_logging() -> None:
    """Set up logging based on configuration."""
    log_level = getattr(logging, config.logging.level.upper(), logging.INFO)
    
    handlers = []
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(config.logging.format))
    handlers.append(console_handler)
    
    # File handler if specified
    if config.logging.file:
        try:
            file_handler = logging.FileHandler(config.logging.file)
            file_handler.setFormatter(logging.Formatter(config.logging.format))
            handlers.append(file_handler)
        except Exception as e:
            logger.error(f"Failed to set up log file: {str(e)}")
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Remove existing handlers and add new ones
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    for handler in handlers:
        root_logger.addHandler(handler)
    
    logger.info(f"Logging configured with level {config.logging.level}")

def get_module_config(module_id: str) -> ModuleConfig:
    """Get configuration for a specific module.
    
    Args:
        module_id: Module identifier
        
    Returns:
        Module configuration
    """
    if module_id in config.modules:
        return config.modules[module_id]
    else:
        # Return default module config
        return ModuleConfig()

# Display settings
DISPLAY_CONFIG = {
    "default_width": 1440,
    "default_height": 1024,
    "min_width": 800,
    "min_height": 600,
    "fullscreen": False,
    "vsync": True,
    "fps_limit": 60
}

# UI layout settings (all values in percentage of screen size)
UI_LAYOUT = {
    # Header section (top area with title and description)
    "header": {
        "height": 15,  # 15% of screen height
        "padding": 2,  # padding inside the header (percentage)
        "title": {
            "y_position": 5,  # 5% from top
            "font_size_factor": 0.035  # title font size relative to screen height
        },
        "description": {
            "y_position": 10,  # 10% from top
            "font_size_factor": 0.02  # description font size relative to screen height
        }
    },
    
    # Content area (middle section with the main training module content)
    "content": {
        "y_start": 15,  # Starts after header (15% from top)
        "height": 70,   # 70% of screen height
        "padding": 2,   # padding inside content area (percentage)
        "font_size_factor": 0.018  # default font size relative to screen height
    },
    
    # Footer section (bottom area with controls and interaction buttons)
    "footer": {
        "height": 15,   # 15% of screen height
        "y_start": 85,  # Starts at 85% from top
        "padding": 2,   # padding inside footer (percentage)
        "button": {
            "width": 15,   # button width in percentage of screen width
            "height": 8,   # button height in percentage of screen height
            "font_size_factor": 0.022  # button font size relative to screen height
        }
    }
}

# Color scheme
COLORS = {
    "background": (240, 240, 240),
    "header_bg": (230, 230, 240),
    "content_bg": (235, 235, 235),
    "footer_bg": (230, 230, 240),
    "text": (20, 20, 20),
    "text_secondary": (70, 70, 70),
    "primary": (60, 120, 200),
    "secondary": (100, 180, 255),
    "accent": (255, 180, 0),
    "success": (0, 180, 0),
    "error": (200, 0, 0),
    "button": (210, 210, 210),
    "button_hover": (190, 190, 190),
    "button_active": (170, 170, 170),
    "button_text": (20, 20, 20),
    "grid_border": (100, 100, 100),
    "grid_bg": (220, 220, 220),
    "cell_on": (50, 50, 200),
    "cell_off": (230, 230, 230)
}

# UI Theme settings to match HTML/CSS implementations
UI_THEME = {
    # Match colors from HTML/CSS stylesheets
    "colors": {
        "primary": (50, 152, 255),      # Blue for primary elements (#3298ff)
        "secondary": (255, 149, 0),     # Orange for secondary elements (#ff9500)
        "success": (50, 255, 50),       # Green for correct answers (#32ff32)
        "error": (255, 50, 50),         # Red for incorrect answers (#ff3232)
        "focus": (255, 82, 82),         # Red for focus points (#ff5252)
        "bg_dark": (30, 36, 44),        # Dark background (#1e242c)
        "bg_light": (40, 44, 52),       # Lighter background (#282c34)
        "card_bg": (40, 44, 52),        # Card background (#282c34)
        "card_hover": (50, 56, 66),     # Card hover state (#323842)
        "text_light": (255, 255, 255),  # Light text (#ffffff)
        "text_dark": (170, 187, 204),   # Dark/muted text (#aabbcc)
        "border": (74, 85, 104),        # Border color (#4a5568)
        "vision_bg": (15, 20, 30)       # Special background for expand vision (#0F141E)
    },
    
    # Component styling to match HTML/CSS
    "components": {
        "button": {
            "border_radius": 8,
            "padding": [10, 20],
            "hover_scale": 1.05,
            "transition_time": 0.2,
            "shadow": True
        },
        "grid_cell": {
            "border_radius": 8,
            "border_width": 1,
            "hover_scale": 1.05,
            "shadow": True
        },
        "phase_indicator": {
            "border_radius": 20,
            "padding": [10, 20],
            "bg_opacity": 0.2,
            "pulse_animation": True
        },
        "symbol_cell": {
            "border_radius": 8,
            "shadow_size": 4
        },
        "pattern_container": {
            "border_radius": 10,
            "padding": [20, 20],
            "original_border_width": 3,
            "normal_border_width": 1
        },
        "focus_point": {
            "radius": 5,
            "pulse_animation": True
        }
    },
    
    # Animation timing to match CSS transitions
    "animations": {
        "transition_time": 0.3,
        "pulse_duration": 2.0,
        "fade_time": 0.5
    },
    
    # Screen layouts
    "layouts": {
        "symbol_memory": {
            "grid_margin": 5,  # percent of screen
            "grid_padding": 2,  # percent of screen
            "cell_margin": 1.5  # percent of cell size
        },
        "morph_matrix": {
            "pattern_margin": 4,  # percent of screen
            "pattern_padding": 2,  # percent of pattern size
            "cell_margin": 1      # percent of cell size
        },
        "expand_vision": {
            "oval_width_factor": 0.7,  # percent of content width
            "oval_height_factor": 0.7,  # percent of content height
            "number_size_factor": 0.04  # font size relative to screen height
        }
    }
}

# Font settings
FONTS = {
    "title": {
        "name": "arial",
        "size_factor": 0.035  # relative to screen height
    },
    "regular": {
        "name": "arial",
        "size_factor": 0.018  # relative to screen height
    },
    "small": {
        "name": "arial",
        "size_factor": 0.014  # relative to screen height
    },
    "button": {
        "name": "arial",
        "size_factor": 0.022  # relative to screen height
    }
}

# Module-specific settings
MODULE_SETTINGS = {
    "symbol_memory": {
        "grid_size_factor": 0.6,  # Grid size relative to content area height
        "symbol_size_factor": 0.48,  # Symbol size relative to cell size (0.6 × 0.8 = 80% of original size)
        "visual_scale": 0.7,  # Scale down all visual elements to 70%
        "preserve_font_size": True  # Keep font sizes the same
    },
    "morph_matrix": {
        "matrix_size_factor": 0.25,  # Matrix size relative to content width
        "grid_layout": [3, 2]  # 3 columns, 2 rows for patterns
    },
    "expand_vision": {
        "grid_size_factor": 0.7,  # Grid size relative to content area height
        "focus_radius_default": 2  # Default radius of visible area
    }
}

# Utility functions for resolution and scaling
def get_resolution():
    """Get the configured resolution as a tuple (width, height)."""
    return (DISPLAY_CONFIG["default_width"], DISPLAY_CONFIG["default_height"])

def calc_font_size(factor, height=None):
    """Calculate font size based on screen height and factor."""
    if height is None:
        height = DISPLAY_CONFIG["default_height"]
    return int(height * factor)

def percent_w(percent, width=None):
    """Convert percentage of screen width to pixels."""
    if width is None:
        width = DISPLAY_CONFIG["default_width"]
    return int(width * percent / 100)

def percent_h(percent, height=None):
    """Convert percentage of screen height to pixels."""
    if height is None:
        height = DISPLAY_CONFIG["default_height"]
    return int(height * percent / 100)

def percent_rect(x_percent, y_percent, width_percent, height_percent, 
                screen_width=None, screen_height=None):
    """Convert percentage rectangle to pixel values."""
    if screen_width is None:
        screen_width = DISPLAY_CONFIG["default_width"]
    if screen_height is None:
        screen_height = DISPLAY_CONFIG["default_height"]
        
    return (
        int(screen_width * x_percent / 100),
        int(screen_height * y_percent / 100),
        int(screen_width * width_percent / 100),
        int(screen_height * height_percent / 100)
    )

def get_content_rect(screen_width=None, screen_height=None):
    """Get the content area rectangle as (x, y, width, height)."""
    if screen_width is None:
        screen_width = DISPLAY_CONFIG["default_width"]
    if screen_height is None:
        screen_height = DISPLAY_CONFIG["default_height"]
    
    # Get values from UI_LAYOUT
    content_y_start = UI_LAYOUT["content"]["y_start"]
    content_height = UI_LAYOUT["content"]["height"]
    padding = UI_LAYOUT["content"]["padding"]
    
    # Calculate the rectangle
    x = percent_w(padding, screen_width)
    y = percent_h(content_y_start, screen_height)
    width = percent_w(100 - 2 * padding, screen_width)
    height = percent_h(content_height, screen_height)
    
    return (x, y, width, height)

def get_header_rect(screen_width=None, screen_height=None):
    """Get the header area rectangle as (x, y, width, height)."""
    if screen_width is None:
        screen_width = DISPLAY_CONFIG["default_width"]
    if screen_height is None:
        screen_height = DISPLAY_CONFIG["default_height"]
    
    # Get values from UI_LAYOUT
    header_height = UI_LAYOUT["header"]["height"]
    padding = UI_LAYOUT["header"]["padding"]
    
    # Calculate the rectangle
    x = percent_w(padding, screen_width)
    y = percent_h(padding, screen_height)
    width = percent_w(100 - 2 * padding, screen_width)
    height = percent_h(header_height - 2 * padding, screen_height)
    
    return (x, y, width, height)

def get_footer_rect(screen_width=None, screen_height=None):
    """Get the footer area rectangle as (x, y, width, height)."""
    if screen_width is None:
        screen_width = DISPLAY_CONFIG["default_width"]
    if screen_height is None:
        screen_height = DISPLAY_CONFIG["default_height"]
    
    # Get values from UI_LAYOUT
    footer_y_start = UI_LAYOUT["footer"]["y_start"]
    footer_height = UI_LAYOUT["footer"]["height"]
    padding = UI_LAYOUT["footer"]["padding"]
    
    # Calculate the rectangle
    x = percent_w(padding, screen_width)
    y = percent_h(footer_y_start + padding, screen_height)
    width = percent_w(100 - 2 * padding, screen_width)
    height = percent_h(footer_height - 2 * padding, screen_height)
    
    return (x, y, width, height)

def get_centered_button_positions(num_buttons, screen_width=None, screen_height=None):
    """
    Get a list of positions for horizontally centered buttons in the footer.
    Returns a list of (x, y, width, height) tuples.
    """
    if screen_width is None:
        screen_width = DISPLAY_CONFIG["default_width"]
    if screen_height is None:
        screen_height = DISPLAY_CONFIG["default_height"]
    
    footer_rect = get_footer_rect(screen_width, screen_height)
    footer_x, footer_y, footer_width, footer_height = footer_rect
    
    button_width_percent = UI_LAYOUT["footer"]["button"]["width"]
    button_height_percent = UI_LAYOUT["footer"]["button"]["height"]
    
    button_width = percent_w(button_width_percent, screen_width)
    button_height = percent_h(button_height_percent, screen_height)
    
    # Calculate total width needed for all buttons with spacing
    spacing = button_width // 2  # Space between buttons
    total_width_needed = (num_buttons * button_width) + ((num_buttons - 1) * spacing)
    
    # Calculate start X for first button to center the group
    start_x = footer_x + (footer_width - total_width_needed) // 2
    y = footer_y + (footer_height - button_height) // 2
    
    positions = []
    for i in range(num_buttons):
        x = start_x + (i * (button_width + spacing))
        positions.append((x, y, button_width, button_height))
    
    return positions 