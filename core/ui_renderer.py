"""
UI Renderer Module

This module provides a UIRenderer class that handles rendering UI components
with proper scaling based on screen resolution and configuration settings.
"""

import pygame
from pathlib import Path
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from core import config

class UIRenderer:
    """
    Handles rendering of UI components with proper scaling based on configuration.
    """
    
    def __init__(self, screen, width=None, height=None):
        """
        Initialize the UI renderer.
        
        Args:
            screen: pygame screen surface to render on
            width: Optional screen width (uses config default if None)
            height: Optional screen height (uses config default if None)
        """
        self.screen = screen
        
        # Set dimensions from parameters or config
        if width is None or height is None:
            self.width, self.height = config.get_resolution()
        else:
            self.width, self.height = width, height
        
        # Initialize fonts
        self._init_fonts()
    
    def _init_fonts(self):
        """Initialize font objects based on config settings."""
        self.fonts = {}
        
        for font_key, font_settings in config.FONTS.items():
            name = font_settings["name"]
            size = config.calc_font_size(font_settings["size_factor"], self.height)
            self.fonts[font_key] = pygame.font.SysFont(name, size)
    
    def render_layout(self):
        """Render the basic layout with header, content and footer areas."""
        # Fill background
        self.screen.fill(config.COLORS["background"])
        
        # Render header area
        header_rect = pygame.Rect(*config.get_header_rect(self.width, self.height))
        pygame.draw.rect(self.screen, config.COLORS["header_bg"], header_rect)
        pygame.draw.rect(self.screen, config.COLORS["grid_border"], header_rect, 1)
        
        # Render content area
        content_rect = pygame.Rect(*config.get_content_rect(self.width, self.height))
        pygame.draw.rect(self.screen, config.COLORS["content_bg"], content_rect)
        pygame.draw.rect(self.screen, config.COLORS["grid_border"], content_rect, 1)
        
        # Render footer area
        footer_rect = pygame.Rect(*config.get_footer_rect(self.width, self.height))
        pygame.draw.rect(self.screen, config.COLORS["footer_bg"], footer_rect)
        pygame.draw.rect(self.screen, config.COLORS["grid_border"], footer_rect, 1)
    
    def render_header(self, title, description=None):
        """
        Render the header with title and optional description.
        
        Args:
            title: Title text to display
            description: Optional description text
        """
        # Get header dimensions
        header_rect = config.get_header_rect(self.width, self.height)
        
        # Render title
        title_y = config.percent_h(config.UI_LAYOUT["header"]["title"]["y_position"], self.height)
        self.render_text(
            title, 
            (self.width // 2, title_y), 
            font_key="title", 
            color=config.COLORS["text"]
        )
        
        # Render description if provided
        if description:
            desc_y = config.percent_h(config.UI_LAYOUT["header"]["description"]["y_position"], self.height)
            self.render_text(
                description, 
                (self.width // 2, desc_y), 
                font_key="regular", 
                color=config.COLORS["text_secondary"]
            )
    
    def render_footer_buttons(self, buttons):
        """
        Render buttons in the footer area.
        
        Args:
            buttons: List of button dictionaries with 'text' and 'action' keys
        """
        # Get button positions
        button_positions = config.get_centered_button_positions(
            len(buttons), self.width, self.height
        )
        
        # Render each button
        for i, (btn_info, position) in enumerate(zip(buttons, button_positions)):
            x, y, width, height = position
            
            # Create button rect
            btn_rect = pygame.Rect(x, y, width, height)
            
            # Determine button state and appearance
            is_active = btn_info.get("active", True)
            is_hover = btn_rect.collidepoint(pygame.mouse.get_pos()) and is_active
            
            if is_hover:
                color = config.COLORS["button_hover"]
            elif is_active:
                color = config.COLORS["button"]
            else:
                color = config.COLORS["button_active"]
            
            # Draw button
            pygame.draw.rect(self.screen, color, btn_rect)
            pygame.draw.rect(self.screen, config.COLORS["grid_border"], btn_rect, 2)
            
            # Draw button text
            text_color = config.COLORS["button_text"] if is_active else config.COLORS["text_secondary"]
            self.render_text(
                btn_info["text"],
                (x + width // 2, y + height // 2),
                font_key="button",
                color=text_color
            )
            
            # Store button info for click handling
            btn_info["rect"] = btn_rect
    
    def render_text(self, text, position, font_key="regular", color=None, align="center"):
        """
        Render text at the specified position with the given font and color.
        
        Args:
            text: Text to render
            position: (x, y) position to render at
            font_key: Font key from config ("title", "regular", "small", "button")
            color: Text color (uses config default if None)
            align: Text alignment ("center", "left", "right")
        """
        if not text:
            return
        
        # Use default color if none specified
        if color is None:
            color = config.COLORS["text"]
        
        # Get font
        font = self.fonts.get(font_key, self.fonts["regular"])
        
        # Render text
        text_surface = font.render(str(text), True, color)
        
        # Position based on alignment
        text_rect = text_surface.get_rect()
        if align == "center":
            text_rect.center = position
        elif align == "left":
            text_rect.midleft = position
        elif align == "right":
            text_rect.midright = position
        
        # Draw text
        self.screen.blit(text_surface, text_rect)
        
        return text_rect
    
    def render_rect(self, rect, color, border_color=None, border_width=0):
        """
        Render a rectangle with optional border.
        
        Args:
            rect: pygame.Rect or (x, y, width, height) tuple
            color: Fill color
            border_color: Border color (optional)
            border_width: Border width (0 for no border)
        """
        if not isinstance(rect, pygame.Rect):
            rect = pygame.Rect(*rect)
        
        pygame.draw.rect(self.screen, color, rect)
        
        if border_color and border_width > 0:
            pygame.draw.rect(self.screen, border_color, rect, border_width)
    
    def render_styled_button(self, text, rect, action=None, is_highlighted=False, is_disabled=False):
        """
        Render a styled button matching HTML/CSS appearance.
        
        Args:
            text: Button text
            rect: Button rectangle (x, y, width, height)
            action: Button action identifier
            is_highlighted: Whether the button is highlighted (hovered or selected)
            is_disabled: Whether the button is disabled
        
        Returns:
            pygame.Rect of the rendered button
        """
        # Get styling from config
        theme = config.UI_THEME
        button_style = theme["components"]["button"]
        
        # Calculate hover effect (scale if highlighted)
        scale = button_style["hover_scale"] if is_highlighted else 1.0
        
        # Determine colors based on state
        if is_disabled:
            bg_color = theme["colors"]["bg_dark"]
            text_color = theme["colors"]["text_dark"]
        else:
            bg_color = theme["colors"]["primary"]
            text_color = theme["colors"]["text_light"]
        
        # Create button rectangle
        if not isinstance(rect, pygame.Rect):
            x, y, width, height = rect
            rect = pygame.Rect(x, y, width, height)
        else:
            x, y, width, height = rect.x, rect.y, rect.width, rect.height
        
        # Apply scale if highlighted
        if scale > 1.0:
            # Calculate scaled dimensions
            scaled_width = int(width * scale)
            scaled_height = int(height * scale)
            
            # Center the scaled button on the original position
            x_offset = (scaled_width - width) // 2
            y_offset = (scaled_height - height) // 2
            
            scaled_rect = pygame.Rect(x - x_offset, y - y_offset, scaled_width, scaled_height)
            rect = scaled_rect
        
        # Draw button with rounded corners
        border_radius = button_style["border_radius"]
        
        # Draw shadow if enabled
        if button_style.get("shadow", False) and not is_disabled:
            shadow_color = (0, 0, 0, 128)  # Semi-transparent black
            shadow_offset = 4  # Shadow offset in pixels
            shadow_rect = pygame.Rect(rect.x + shadow_offset//2, 
                                     rect.y + shadow_offset, 
                                     rect.width, 
                                     rect.height)
            pygame.draw.rect(self.screen, shadow_color, shadow_rect, 
                           border_radius=border_radius)
        
        # Draw button background
        pygame.draw.rect(self.screen, bg_color, rect, border_radius=border_radius)
        
        # Draw button border
        border_color = theme["colors"]["border"]
        pygame.draw.rect(self.screen, border_color, rect, 1, border_radius=border_radius)
        
        # Render text
        font_key = "button"
        self.render_text_with_shadow(text, rect.center, font_key, text_color)
        
        return rect
    
    def render_text_with_shadow(self, text, position, font_key="regular", color=None, shadow=True):
        """
        Render text with optional drop shadow for better visibility.
        
        Args:
            text: Text to render
            position: Position (x, y) to render at
            font_key: Font key from config
            color: Text color
            shadow: Whether to add a shadow
            
        Returns:
            pygame.Rect of the rendered text
        """
        if not text:
            return None
        
        # Use default color if none specified
        if color is None:
            color = config.UI_THEME["colors"]["text_light"]
        
        # Get font
        font = self.fonts.get(font_key, self.fonts["regular"])
        
        # Render text with shadow
        if shadow:
            # Render shadow text (offset slightly and in black)
            shadow_surf = font.render(str(text), True, (0, 0, 0, 160))
            shadow_rect = shadow_surf.get_rect(center=(position[0] + 2, position[1] + 2))
            self.screen.blit(shadow_surf, shadow_rect)
        
        # Render main text
        text_surf = font.render(str(text), True, color)
        text_rect = text_surf.get_rect(center=position)
        self.screen.blit(text_surf, text_rect)
        
        return text_rect
    
    def render_phase_indicator(self, text, phase_type=None):
        """
        Render a phase indicator matching HTML/CSS styling.
        
        Args:
            text: Indicator text
            phase_type: Phase type ('memorize', 'recall', 'feedback', etc.)
        
        Returns:
            pygame.Rect of the rendered indicator
        """
        # Get styling from config
        theme = config.UI_THEME
        indicator_style = theme["components"]["phase_indicator"]
        
        # Determine background color based on phase
        if phase_type == "memorize":
            bg_color = theme["colors"]["primary"]
        elif phase_type == "recall":
            bg_color = theme["colors"]["secondary"]
        elif phase_type == "feedback_correct":
            bg_color = theme["colors"]["success"]
        elif phase_type == "feedback_incorrect":
            bg_color = theme["colors"]["error"]
        elif phase_type == "feedback":
            # For backward compatibility
            if "Correct" in text:
                bg_color = theme["colors"]["success"]
            elif "Incorrect" in text:
                bg_color = theme["colors"]["error"]
            else:
                bg_color = theme["colors"]["success"]
        else:
            bg_color = theme["colors"]["bg_dark"]
        
        # Apply opacity
        bg_color_with_alpha = (*bg_color[:3], int(255 * indicator_style["bg_opacity"]))
        
        # Calculate position (centered, top of content area)
        content_rect = config.get_content_rect(self.width, self.height)
        x = self.width // 2
        y = content_rect[1] + 50  # Moved down 20 pixels (from original value of 30)
        
        # Render text to get dimensions
        font = self.fonts["regular"]
        text_surf = font.render(str(text), True, theme["colors"]["text_light"])
        text_width, text_height = text_surf.get_size()
        
        # Add padding - increase for more space around text
        padding_x, padding_y = indicator_style["padding"]
        padding_x = int(padding_x * 3.5)  # 250% more horizontal padding (wider)
        padding_y = int(padding_y * 1.8)  # 80% more vertical padding (shorter)
        
        rect_width = text_width + padding_x * 2
        rect_height = text_height + padding_y * 2
        
        # Draw rounded rectangle
        rect = pygame.Rect(x - rect_width//2, y - rect_height//2, rect_width, rect_height)
        border_radius = indicator_style["border_radius"]
        
        # Create surface with alpha for the background
        indicator_surf = pygame.Surface((rect_width, rect_height), pygame.SRCALPHA)
        pygame.draw.rect(indicator_surf, bg_color_with_alpha, 
                       (0, 0, rect_width, rect_height), 
                       border_radius=border_radius)
        self.screen.blit(indicator_surf, rect)
        
        # Render text
        text_rect = text_surf.get_rect(center=(x, y))
        self.screen.blit(text_surf, text_rect)
        
        return rect
    
    def render_styled_grid_cell(self, rect, color, symbol=None, is_highlighted=False, style=None, symbol_color=None):
        """
        Render a styled grid cell matching HTML/CSS styling.
        
        Args:
            rect: Cell rectangle (x, y, width, height)
            color: Cell background color
            symbol: Optional symbol to display in the cell
            is_highlighted: Whether the cell is highlighted
            style: Optional override for cell style
            symbol_color: Optional color for the symbol (for multi-modal cognitive enhancement)
            
        Returns:
            pygame.Rect of the rendered cell
        """
        # Get styling from config
        theme = config.UI_THEME
        cell_style = style or theme["components"]["grid_cell"]
        
        # Get module-specific settings to handle font size preservation
        module_settings = config.MODULE_SETTINGS.get("symbol_memory", {})
        preserve_font_size = module_settings.get("preserve_font_size", True)
        original_visual_scale = module_settings.get("visual_scale", 1.0)
        symbol_size_factor = module_settings.get("symbol_size_factor", 0.48)  # Use config or default to 0.48 (0.6 × 0.8)
        
        # Apply highlight effect (scale if highlighted)
        scale = cell_style["hover_scale"] if is_highlighted else 1.0
        
        # Create cell rectangle
        if not isinstance(rect, pygame.Rect):
            x, y, width, height = rect
            rect = pygame.Rect(x, y, width, height)
        else:
            x, y, width, height = rect.x, rect.y, rect.width, rect.height
        
        # Store original dimensions for font size calculation
        original_width, original_height = width, height
        if preserve_font_size and original_visual_scale < 1.0:
            # Calculate what the original size would have been before scaling
            original_width = int(width / original_visual_scale)
            original_height = int(height / original_visual_scale)
        
        # Apply scale if highlighted
        if scale > 1.0 and is_highlighted:
            # Calculate scaled dimensions
            scaled_width = int(width * scale)
            scaled_height = int(height * scale)
            
            # Center the scaled cell on the original position
            x_offset = (scaled_width - width) // 2
            y_offset = (scaled_height - height) // 2
            
            scaled_rect = pygame.Rect(x - x_offset, y - y_offset, scaled_width, scaled_height)
            rect = scaled_rect
        
        # Draw shadow if enabled
        if cell_style.get("shadow", False):
            shadow_color = (0, 0, 0, 100)  # Semi-transparent black
            shadow_size = cell_style.get("shadow_size", 4)
            shadow_rect = pygame.Rect(rect.x + shadow_size//2, 
                                     rect.y + shadow_size, 
                                     rect.width, 
                                     rect.height)
            pygame.draw.rect(self.screen, shadow_color, shadow_rect, 
                           border_radius=cell_style["border_radius"])
        
        # Draw cell background
        cell_bg_color = color
        if is_highlighted:
            # Use brighter color for highlighted cells
            cell_bg_color = theme["colors"]["primary"]
        
        # Draw rounded rectangle
        border_radius = cell_style["border_radius"]
        pygame.draw.rect(self.screen, cell_bg_color, rect, border_radius=border_radius)
        
        # Draw border
        border_color = theme["colors"]["border"]
        border_width = cell_style["border_width"]
        pygame.draw.rect(self.screen, border_color, rect, border_width, 
                       border_radius=border_radius)
        
        # Draw symbol if provided
        if symbol:
            # Calculate font size based on original cell dimensions and symbol size factor
            font_size = int(min(original_width, original_height) * symbol_size_factor)
            symbol_font = pygame.font.SysFont("arial", font_size)
            
            # Determine symbol color - use provided color or fallback to default
            if symbol_color:
                # Use the provided color for multi-modal cognitive enhancement
                text_color = symbol_color
            else:
                # Fallback to default text color
                text_color = theme["colors"]["text_light"]
            
            # Create a temporary surface to measure the exact symbol dimensions
            symbol_surf = symbol_font.render(str(symbol), True, text_color)
            symbol_width, symbol_height = symbol_surf.get_size()
            
            # Calculate exact center coordinates with a slight downward adjustment
            center_x = rect.x + rect.width // 2 + int(font_size * 0.03)  # Reduce right offset to move symbol left
            center_y = rect.y + rect.height // 2 + int(font_size * 0.06)  # Maintain vertical position
            
            # Create a precise rect for the symbol position
            symbol_rect = symbol_surf.get_rect(center=(center_x, center_y))
            
            # Blit the symbol to the screen at the exact center position
            self.screen.blit(symbol_surf, symbol_rect)
        
        return rect
    
    def render_components(self, components):
        """
        Render a list of UI components.
        
        Args:
            components: List of component dictionaries
        """
        for comp in components:
            comp_type = comp.get("type", "")
            
            if comp_type == "text":
                self._render_text_component(comp)
            elif comp_type == "rect":
                self._render_rect_component(comp)
            elif comp_type == "button":
                self._render_button_component(comp)
            elif comp_type == "grid":
                self._render_grid_component(comp)
            elif comp_type == "matrix":
                self._render_matrix_component(comp)
            elif comp_type == "circle":
                self._render_circle_component(comp)
    
    def _render_text_component(self, comp):
        """Render a text component."""
        text = comp.get("text", "")
        position = comp.get("position", [0, 0])
        font_key = comp.get("font_key", "regular")
        color = comp.get("color", config.COLORS["text"])
        align = comp.get("align", "center")
        
        # Scale position if given as percentages
        if comp.get("use_percent", False):
            position = (
                config.percent_w(position[0], self.width),
                config.percent_h(position[1], self.height)
            )
        
        self.render_text(text, position, font_key, color, align)
    
    def _render_rect_component(self, comp):
        """Render a rectangle component."""
        position = comp.get("position", [0, 0])
        size = comp.get("size", [100, 100])
        color = comp.get("color", config.COLORS["grid_bg"])
        border_color = comp.get("border_color", config.COLORS["grid_border"])
        border_width = comp.get("border_width", 1)
        
        # Scale rect if given as percentages
        if comp.get("use_percent", False):
            rect = config.percent_rect(
                position[0], position[1], size[0], size[1],
                self.width, self.height
            )
        else:
            rect = (position[0], position[1], size[0], size[1])
        
        self.render_rect(rect, color, border_color, border_width)
    
    def _render_button_component(self, comp):
        """Render a button component."""
        position = comp.get("position", [0, 0])
        size = comp.get("size", [100, 40])
        text = comp.get("text", "")
        active = comp.get("active", True)
        
        # Scale if given as percentages
        if comp.get("use_percent", False):
            position = (
                config.percent_w(position[0], self.width),
                config.percent_h(position[1], self.height)
            )
            size = (
                config.percent_w(size[0], self.width),
                config.percent_h(size[1], self.height)
            )
        
        # Determine colors based on state
        is_hover = pygame.Rect(position[0], position[1], size[0], size[1]).collidepoint(pygame.mouse.get_pos())
        
        if not active:
            color = config.COLORS["button_active"]
            text_color = config.COLORS["text_secondary"]
        elif is_hover:
            color = config.COLORS["button_hover"]
            text_color = config.COLORS["button_text"]
        else:
            color = config.COLORS["button"]
            text_color = config.COLORS["button_text"]
        
        # Draw button
        rect = pygame.Rect(position[0], position[1], size[0], size[1])
        pygame.draw.rect(self.screen, color, rect)
        pygame.draw.rect(self.screen, config.COLORS["grid_border"], rect, 2)
        
        # Draw text
        if text:
            self.render_text(
                text,
                (position[0] + size[0] // 2, position[1] + size[1] // 2),
                font_key="button",
                color=text_color
            )
        
        # Store rect for click detection
        comp["rect"] = rect
    
    def _render_grid_component(self, comp):
        """Render a grid component."""
        position = comp.get("position", [0, 0])
        size = comp.get("size", [300, 300])
        grid_size = comp.get("grid_size", 3)
        cells = comp.get("cells", [])
        
        # Scale if given as percentages
        if comp.get("use_percent", False):
            position = (
                config.percent_w(position[0], self.width),
                config.percent_h(position[1], self.height)
            )
            size = (
                config.percent_w(size[0], self.width),
                config.percent_h(size[1], self.height)
            )
        
        # Draw grid background
        rect = pygame.Rect(position[0], position[1], size[0], size[1])
        pygame.draw.rect(self.screen, config.COLORS["grid_bg"], rect)
        pygame.draw.rect(self.screen, config.COLORS["grid_border"], rect, 2)
        
        # Calculate cell size
        cell_width = size[0] / grid_size
        cell_height = size[1] / grid_size
        
        # Draw grid lines
        for i in range(1, grid_size):
            # Vertical lines
            x = position[0] + i * cell_width
            pygame.draw.line(
                self.screen, 
                config.COLORS["grid_border"],
                (x, position[1]),
                (x, position[1] + size[1]),
                1
            )
            
            # Horizontal lines
            y = position[1] + i * cell_height
            pygame.draw.line(
                self.screen, 
                config.COLORS["grid_border"],
                (position[0], y),
                (position[0] + size[0], y),
                1
            )
        
        # Draw cell contents
        for cell in cells:
            cell_x = cell.get("x", 0)
            cell_y = cell.get("y", 0)
            text = cell.get("text", "")
            color = cell.get("color", config.COLORS["text"])
            
            if cell_x < grid_size and cell_y < grid_size:
                # Calculate cell position
                x = position[0] + cell_x * cell_width + cell_width / 2
                y = position[1] + cell_y * cell_height + cell_height / 2
                
                # Draw text
                self.render_text(text, (x, y), font_key="regular", color=color)
    
    def _render_matrix_component(self, comp):
        """Render a matrix component."""
        position = comp.get("position", [0, 0])
        size = comp.get("size", [150, 150])
        matrix = comp.get("matrix", [])
        selected = comp.get("selected", False)
        
        # Scale if given as percentages
        if comp.get("use_percent", False):
            position = (
                config.percent_w(position[0], self.width),
                config.percent_h(position[1], self.height)
            )
            size = (
                config.percent_w(size[0], self.width),
                config.percent_h(size[1], self.height)
            )
        
        # Skip if no matrix data
        if not matrix:
            return
        
        # Get matrix dimensions
        matrix_size = len(matrix)
        cell_width = size[0] / matrix_size
        cell_height = size[1] / matrix_size
        
        # Draw cells
        for y in range(matrix_size):
            for x in range(matrix_size):
                # Get cell value
                cell_value = 0
                if y < len(matrix) and x < len(matrix[y]):
                    cell_value = matrix[y][x]
                
                # Calculate cell position
                cell_x = position[0] + x * cell_width
                cell_y = position[1] + y * cell_height
                
                # Draw cell
                cell_rect = pygame.Rect(cell_x, cell_y, cell_width + 1, cell_height + 1)
                cell_color = config.COLORS["cell_on"] if cell_value == 1 else config.COLORS["cell_off"]
                pygame.draw.rect(self.screen, cell_color, cell_rect)
                pygame.draw.rect(self.screen, config.COLORS["grid_border"], cell_rect, 1)
    
    def _render_circle_component(self, comp):
        """Render a circle component."""
        position = comp.get("position", [0, 0])
        radius = comp.get("radius", 30)
        color = comp.get("color", config.COLORS["primary"])
        border_color = comp.get("border_color", config.COLORS["grid_border"])
        border_width = comp.get("border_width", 0)
        
        # Scale if given as percentages
        if comp.get("use_percent", False):
            position = (
                config.percent_w(position[0], self.width),
                config.percent_h(position[1], self.height)
            )
            radius = int(config.percent_h(radius, self.height))
        
        # Draw circle
        pygame.draw.circle(self.screen, color, position, radius)
        
        # Draw border if needed
        if border_width > 0:
            pygame.draw.circle(self.screen, border_color, position, radius, border_width)
    
    def handle_button_click(self, components, pos):
        """
        Check if any buttons were clicked and trigger their actions.
        
        Args:
            components: List of component dictionaries
            pos: Mouse position (x, y)
            
        Returns:
            Clicked button component or None
        """
        for comp in components:
            if comp.get("type") == "button" and comp.get("active", True):
                if "rect" in comp and comp["rect"].collidepoint(pos):
                    return comp
        return None 