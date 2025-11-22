#!/usr/bin/env python3
"""
Morph Matrix Renderer

This module provides a renderer for the MorphMatrix module of MetaMindIQTrain.
It handles displaying matrices and allows users to identify rotated vs. modified patterns.
"""

import pygame
import time
import math
from pygame import gfxdraw

from MetaMindIQTrain.clients.pygame.renderers.base_renderer import BaseRenderer
from MetaMindIQTrain.config import calculate_sizes
from MetaMindIQTrain.modules.morph_matrix import MorphMatrix

class MorphMatrixRenderer(BaseRenderer):
    """Renderer for the MorphMatrix module."""
    
    def __init__(self, screen, title_font, regular_font, small_font):
        """Initialize the renderer with screen and fonts."""
        super().__init__(screen, title_font, regular_font, small_font)
        
        # Calculate sizes based on screen dimensions
        self.screen_width = self.screen.get_width()
        self.screen_height = self.screen.get_height()
        self.sizes = calculate_sizes(self.screen_width, self.screen_height)
        
        # Use dark theme colors from base renderer
        self.WHITE = self.colors['text_highlight']
        self.BLACK = (0, 0, 0)
        self.BLUE = self.colors['light_blue']
        self.DARK_BLUE = self.colors['dark_blue']
        self.LIGHT_BLUE = self.colors['accent']
        self.GREEN = self.colors['correct']
        self.RED = self.colors['incorrect']
        self.YELLOW = (255, 255, 0, 128)  # Yellow with transparency
        self.SELECTED_COLOR = (60, 180, 100, 100)  # Green with transparency
        self.GRAY = self.colors['gray']
        self.GRAY_LIGHT = self.colors['gray_light']
        self.GRAY_MEDIUM = (120, 120, 140)
        
        # Background color for content area - use the dark theme
        self.BG_COLOR = self.colors['content_bg']
        
        # Button dimensions based on screen size
        button_width = self.percent_x(0.15)  # 15% of screen width
        button_height = self.percent_y(0.06)  # 6% of screen height
        button_spacing = self.percent_x(0.05)  # 5% of screen width
        
        # Position buttons in the footer area
        footer_center_x = self.footer_rect.centerx
        footer_center_y = self.footer_rect.centery
        
        # Create buttons
        self.buttons = [
            {
                'text': 'Check Answers',
                'action': 'check',
                'rect': pygame.Rect(
                    footer_center_x - button_width // 2,
                    footer_center_y - button_height // 2,
                    button_width,
                    button_height
                ),
                'color': self.DARK_BLUE,
                'hover_color': self.LIGHT_BLUE,
                'text_color': self.WHITE,
                'visible': True
            },
            {
                'text': 'Start Challenge',
                'action': 'start_challenge',
                'rect': pygame.Rect(
                    footer_center_x - button_width * 1.5 - button_spacing,
                    footer_center_y - button_height // 2,
                    button_width * 1.5,
                    button_height
                ),
                'color': self.DARK_BLUE,
                'hover_color': self.LIGHT_BLUE,
                'text_color': self.WHITE,
                'visible': True
            },
            {
                'text': 'Reset Level',
                'action': 'reset_level',
                'rect': pygame.Rect(
                    footer_center_x + button_spacing,
                    footer_center_y - button_height // 2,
                    button_width,
                    button_height
                ),
                'color': self.DARK_BLUE,
                'hover_color': self.LIGHT_BLUE,
                'text_color': self.WHITE,
                'visible': True
            },
            {
                'text': 'Advance Level',
                'action': 'advance_level',
                'rect': pygame.Rect(
                    footer_center_x + button_width + button_spacing * 2,
                    footer_center_y - button_height // 2,
                    button_width,
                    button_height
                ),
                'color': self.DARK_BLUE,
                'hover_color': self.LIGHT_BLUE,
                'text_color': self.WHITE,
                'visible': True
            }
        ]
    
    def render(self, state):
        """Render the pattern recognition module.
        
        Args:
            state: Module state dictionary
        """
        # Draw standard layout (clears screen, draws sections using dark theme)
        self.draw_standard_layout(state)
        
        # Fill content area with dark background
        pygame.draw.rect(self.screen, self.BG_COLOR, self.content_rect)
        
        # Get the clusters from the state
        clusters = state.get('clusters', [])
        show_feedback = state.get('show_feedback', False)
        
        # Get score and level from state
        score = state.get('score', 0)
        level = state.get('level', 1)
        
        # Create a subtle grid background for the content area
        self._draw_grid_background()
        
        # Display title text at top with minimal vertical space
        title_text = "Pattern Recognition"
        title_surface = self.regular_font.render(title_text, True, self.LIGHT_BLUE)
        title_rect = title_surface.get_rect(centerx=self.content_rect.centerx, top=self.content_rect.top + 1)  # Reduced to absolute minimum
        self.screen.blit(title_surface, title_rect)
        
        # Ultra-minimal instructions
        instructions = "Select rotations of the original (blue) pattern"  # Further shortened
        instructions_surface = self.small_font.render(instructions, True, self.colors['text_highlight'])
        instructions_rect = instructions_surface.get_rect(centerx=self.content_rect.centerx, top=title_rect.bottom - 1)  # Overlap slightly
        self.screen.blit(instructions_surface, instructions_rect)
        
        # Calculate positions for clusters if they don't have positions
        if clusters and 'position' not in clusters[0]:
            self._calculate_cluster_positions(clusters)
            
        # Draw all patterns (including original)
        for cluster in clusters:
            # Only the cluster explicitly marked as original should be featured
            is_featured = cluster.get('is_original', False)
            self._draw_matrix(cluster, is_featured=is_featured, show_feedback=show_feedback)
            
        # If in feedback mode, show results
        if show_feedback:
            self._draw_feedback(state)
            
        # Display level information in the top-right corner with minimal margin
        level_text = f"Level: {level}"
        level_surface = self.small_font.render(level_text, True, self.colors['text_primary'])
        level_rect = level_surface.get_rect(right=self.content_rect.right - 5, top=self.content_rect.top + 2)  # Minimal margins
        self.screen.blit(level_surface, level_rect)
        
        # Display score in the top-left corner with minimal margin
        score_text = f"Score: {score}"
        score_surface = self.small_font.render(score_text, True, self.colors['text_primary'])
        score_rect = score_surface.get_rect(left=self.content_rect.left + 5, top=self.content_rect.top + 2)  # Minimal margins
        self.screen.blit(score_surface, score_rect)
    
    def _draw_grid_background(self):
        """Draw a subtle grid background in the content area for visual guidance."""
        # Create a semi-transparent surface for the grid
        grid_surface = pygame.Surface((self.content_rect.width, self.content_rect.height), pygame.SRCALPHA)
        
        # Draw subtle gradient background
        for y in range(self.content_rect.height):
            alpha = 15 + int(y / self.content_rect.height * 10)  # Increase opacity slightly toward bottom
            pygame.draw.line(
                grid_surface,
                (40, 60, 100, alpha),
                (0, y),
                (self.content_rect.width, y)
            )
        
        # Draw grid lines with tighter spacing
        grid_spacing_x = self.content_rect.width / 8  # Increased grid density (was /6)
        grid_spacing_y = self.content_rect.height / 6  # Increased grid density (was /5)
        
        # Vertical lines
        for i in range(1, 8):  # Increased number of lines (was 1,6)
            x = i * grid_spacing_x
            pygame.draw.line(
                grid_surface,
                (60, 80, 120, 15),  # Very subtle blue color
                (x, 0),
                (x, self.content_rect.height),
                1
            )
        
        # Horizontal lines
        for i in range(1, 6):  # Increased number of lines (was 1,5)
            y = i * grid_spacing_y
            pygame.draw.line(
                grid_surface,
                (60, 80, 120, 15),  # Very subtle blue color
                (0, y),
                (self.content_rect.width, y),
                1
            )
        
        # Apply the grid to the content area
        self.screen.blit(grid_surface, self.content_rect)
    
    def _calculate_cluster_positions(self, clusters):
        """Calculate positions for clusters in a 3x2 rectangular grid layout.
        
        Args:
            clusters: List of cluster dictionaries
        """
        if not clusters:
            return
            
        # Add index to all clusters if not already present and reset is_original flag
        for i, cluster in enumerate(clusters):
            cluster['index'] = i
            # Reset any original markings, we'll set it correctly below
            cluster['is_original'] = False
                
        # Get pattern size details
        pattern_size = clusters[0].get('size', 5)
        cell_width = MorphMatrix.CELL_WIDTH
        cell_height = MorphMatrix.CELL_HEIGHT
        pattern_width = pattern_size * cell_width + 2
        pattern_height = pattern_size * cell_height + 2
        
        # Ultra-compact grid - nearly using entire screen
        grid_width = self.content_rect.width * 0.98  # Almost entire content width (from 96%)
        
        # Adjust grid height with minimal vertical gaps (more extreme aspect ratio)
        grid_height = grid_width * 0.55  # Reduce vertical spacing by using a flatter aspect ratio
        
        # Position grid extremely high with minimal top margin
        grid_x = self.content_rect.centerx - grid_width / 2
        grid_y = self.content_rect.top + self.percent_y(0.04)  # Minimal 4% top margin
        
        # Calculate cell dimensions for ultra-tight 3x2 grid with minimal spacing
        cell_width = grid_width / 3
        cell_height = grid_height / 2
        
        # Calculate positions for all patterns with minimal spacing
        positions = []
        for row in range(2):
            for col in range(3):
                pos_x = grid_x + (col + 0.5) * cell_width
                pos_y = grid_y + (row + 0.5) * cell_height
                positions.append((pos_x, pos_y))
        
        # Mark the first cluster (index 0) as the original and place it in the middle of the top row
        original_cluster = clusters[0]
        original_cluster['is_original'] = True
        original_cluster['position'] = positions[1]  # Index 1 = middle of top row
        
        # Assign positions to remaining clusters
        non_original_positions = positions.copy()
        non_original_positions.pop(1)  # Remove the middle top position
        
        non_original_clusters = clusters[1:]  # All clusters except the original
        
        # Assign positions to non-original clusters
        for i, cluster in enumerate(non_original_clusters):
            if i < len(non_original_positions):
                cluster['position'] = non_original_positions[i]
            else:
                # Fallback position (should rarely happen)
                cluster['position'] = (self.content_rect.centerx, self.content_rect.centery)
    
    def _draw_matrix(self, cluster, is_featured=False, show_feedback=False):
        """Draw a single matrix pattern.
        
        Args:
            cluster: Dictionary containing matrix pattern data
            is_featured: Whether this pattern is being featured (original pattern)
            show_feedback: Whether to show feedback highlighting
        """
        matrix = cluster.get('matrix', [])
        if not matrix:
            return
            
        pos = cluster.get('position', (0, 0))
        size = cluster.get('size', 5)
        is_selected = cluster.get('is_selected', False)
        is_original = is_featured  # Use only the is_featured flag to determine if this is the original
        is_modified = cluster.get('is_modified', False)
        is_correct = cluster.get('is_correct', None)  # Only used in feedback mode
        
        # Calculate dimensions
        cell_width = MorphMatrix.CELL_WIDTH
        cell_height = MorphMatrix.CELL_HEIGHT
        pattern_width = size * cell_width + 2
        pattern_height = size * cell_height + 2
        
        # Create a rect for the entire matrix
        matrix_rect = pygame.Rect(
            pos[0] - pattern_width/2, 
            pos[1] - pattern_height/2, 
            pattern_width, 
            pattern_height
        )
        
        # Minimal padding for ultra-compact layout
        box_padding = 6  # Further reduced from 10px for ultra-tight layout
        box_rect = pygame.Rect(
            matrix_rect.left - box_padding,
            matrix_rect.top - box_padding,
            matrix_rect.width + box_padding * 2,
            matrix_rect.height + box_padding * 2 + 16  # Reduced from 20px for minimal label space
        )
        
        # Create a rounded background with improved gradient
        box_surface = pygame.Surface((box_rect.width, box_rect.height), pygame.SRCALPHA)
        
        # Enhanced gradient background with stronger contrast
        for y in range(box_rect.height):
            alpha = 25 - int(y / box_rect.height * 15)  # Slightly reduced gradient for cleaner look
            color = (40, 60, 100, alpha)
            pygame.draw.line(box_surface, color, (0, y), (box_rect.width, y))
        
        # Determine box border color based on state with improved contrast
        if is_original:
            box_border_color = (100, 160, 255, 140)  # Brighter blue for original
        elif is_selected:
            box_border_color = (80, 200, 120, 140)  # Brighter green for selected
        elif show_feedback and is_correct is not None:
            if is_correct:
                box_border_color = (80, 200, 120, 140)  # Brighter green for correct
            else:
                box_border_color = (220, 80, 80, 140)  # Brighter red for incorrect
        else:
            box_border_color = (120, 120, 140, 70)  # Lighter gray for normal
        
        # Draw box border with minimal outline for compact display
        pygame.draw.rect(
            box_surface,
            box_border_color,
            pygame.Rect(0, 0, box_rect.width, box_rect.height),
            1,  # Reduced to 1px border for ultra-compact look
            border_radius=4  # Reduced from 6px for minimal style
        )
        
        # Apply the box surface
        self.screen.blit(box_surface, box_rect)
        
        # Create minimal highlight background for selected items
        if is_selected and not is_original:
            # Create a highlight surface with transparency
            highlight_rect = pygame.Rect(
                matrix_rect.left - 2,  # Further reduced from -3px
                matrix_rect.top - 2,   # Further reduced from -3px
                matrix_rect.width + 4, # Further reduced from +6px
                matrix_rect.height + 4 # Further reduced from +6px
            )
            highlight_surf = pygame.Surface((highlight_rect.width, highlight_rect.height), pygame.SRCALPHA)
            
            # Gradient fill for better visual effect
            for y in range(highlight_rect.height):
                alpha = 90 - int(y / highlight_rect.height * 30)
                color = (60, 180, 100, alpha)
                pygame.draw.line(highlight_surf, color, (0, y), (highlight_rect.width, y))
                
            self.screen.blit(highlight_surf, (highlight_rect.x, highlight_rect.y))
        
        # Draw matrix background with improved contrast gradient
        matrix_bg = pygame.Surface((matrix_rect.width, matrix_rect.height), pygame.SRCALPHA)
        for y in range(matrix_rect.height):
            # Create stronger gradient from top to bottom
            intensity = 1.0 - (y / matrix_rect.height * 0.15)  # Increased contrast
            bg_color = (int(255 * intensity), int(255 * intensity), int(255 * intensity))
            pygame.draw.line(matrix_bg, bg_color, (0, y), (matrix_rect.width, y))
        self.screen.blit(matrix_bg, (matrix_rect.x, matrix_rect.y))
        
        # Determine border color and width based on state
        if is_original:
            # Original pattern has minimal but visible blue glow
            border_color = self.BLUE
            border_width = 2  # Reduced from 3px for compact look
            
            # Draw special glow effect with minimal footprint
            glow_surface = pygame.Surface((pattern_width + 24, pattern_height + 24), pygame.SRCALPHA)  # Reduced from +30px
            
            # Create fewer glow layers for compact but visible effect
            for offset in range(10, 3, -2):  # Reduced range and layers
                alpha = 255 - (offset * 20)  # Faster alpha decay
                blue_glow = (120, 180, 255, alpha)
                pygame.draw.rect(
                    glow_surface,
                    blue_glow, 
                    pygame.Rect(12-offset, 12-offset, pattern_width+offset*2, pattern_height+offset*2),
                    1,  # Reduced to 1px border
                    border_radius=2  # Minimal border radius
                )
            
            # Position the glow effect
            glow_rect = glow_surface.get_rect(center=pos)
            self.screen.blit(glow_surface, glow_rect)
            
        elif show_feedback:
            # In feedback mode, minimal but clear indicators
            if is_correct is True:
                border_color = self.GREEN
                border_width = 1  # Reduced to 1px
            elif is_correct is False:
                border_color = self.RED
                border_width = 1  # Reduced to 1px
            else:
                border_color = self.GRAY
                border_width = 1  # Already 1px
        elif is_selected:
            # Selected but not original - minimal green border
            border_color = self.GREEN
            border_width = 1  # Reduced to 1px
        else:
            # Regular pattern - minimal border
            border_color = (180, 180, 200)
            border_width = 1  # Already 1px
            
        # Draw border with minimal glow for ultra-compact look
        for offset in range(border_width, 0, -1):
            alpha = 220 if offset == border_width else 120
            glow_color = (*border_color[:3], alpha)
            border_rect = pygame.Rect(
                matrix_rect.left - offset,
                matrix_rect.top - offset,
                matrix_rect.width + offset * 2,
                matrix_rect.height + offset * 2
            )
            pygame.draw.rect(self.screen, glow_color, border_rect, 1)
        
        # Draw each cell with improved contrast
        for row in range(size):
            for col in range(size):
                # Calculate position for this cell
                cell_x = matrix_rect.left + 1 + col * cell_width
                cell_y = matrix_rect.top + 1 + row * cell_height
                
                # Create cell rect
                cell_rect = pygame.Rect(
                    cell_x, cell_y,
                    cell_width, cell_height
                )
                
                # Set color based on cell value with improved contrast
                if row < len(matrix) and col < len(matrix[row]):
                    if matrix[row][col] == 1:
                        # Draw filled cells with minimal 3D effect
                        pygame.draw.rect(self.screen, (20, 20, 20), cell_rect)  # Darker base
                        inner_rect = cell_rect.inflate(-1, -1)  # Minimal 3D effect
                        pygame.draw.rect(self.screen, self.BLACK, inner_rect)  # Black top
                    else:
                        # Enhanced checker pattern for "0" cells
                        if (row + col) % 2 == 0:
                            pygame.draw.rect(self.screen, (230, 230, 230), cell_rect)  # Slightly brighter
                        else:
                            pygame.draw.rect(self.screen, (250, 250, 250), cell_rect)  # Almost white
        
        # Draw ultra-compact label below the matrix
        label_y = matrix_rect.bottom + 6  # Further reduced from 8px
        
        # Different label for original pattern - keep text minimal
        if is_original:
            label_text = "ORIGINAL"  # Shortened from "ORIGINAL PATTERN"
            label_color = (120, 180, 255)
        elif show_feedback:
            # Label text based on feedback state
            if is_modified:
                label_text = "Modified"
            else:
                label_text = "Rotation"  # Shortened from "Exact Rotation"
                
            # Use brighter colors in feedback mode
            if is_correct is True:
                label_color = (100, 220, 140)
            elif is_correct is False:
                label_color = (255, 100, 100)
            else:
                label_color = self.colors['text_primary']
        else:
            # Regular pattern label - ultra compact
            if is_selected:
                label_text = f"#{cluster.get('index', 0)} ✓"  # Ultra short format
                label_color = (100, 220, 140)
            else:
                label_text = f"#{cluster.get('index', 0)}"  # Ultra short format
                label_color = self.colors['text_highlight']
        
        # Render and display the label
        label_surface = self.small_font.render(label_text, True, label_color)
        label_rect = label_surface.get_rect(centerx=pos[0], centery=label_y)
        self.screen.blit(label_surface, label_rect)
        
        # For the original pattern, add a minimal indicator above
        if is_original:
            indicator_y = matrix_rect.top - 8  # Further reduced from -10px
            indicator_surface = pygame.Surface((12, 12), pygame.SRCALPHA)  # Further reduced from (16, 16)
            pygame.draw.polygon(
                indicator_surface,
                (120, 180, 255, 220),
                [(6, 0), (12, 12), (0, 12)]
            )
            indicator_rect = indicator_surface.get_rect(centerx=pos[0], bottom=matrix_rect.top - 1)  # Reduced from -2px
            self.screen.blit(indicator_surface, indicator_rect)
    
    def _draw_feedback(self, state):
        """Draw feedback when answers are checked.
        
        Args:
            state: Module state dictionary
        """
        # Get result from state
        num_correct = state.get('num_correct', 0)
        total_selections = state.get('total_selections', 0)
        num_rotations = state.get('num_rotations', 0)
        
        # Create a smaller, more compact overlay for the feedback
        feedback_rect = pygame.Rect(
            self.content_rect.centerx - self.percent_x(0.25),  # Reduced width (from 0.4)
            self.content_rect.top + self.percent_y(0.5),
            self.percent_x(0.5),  # Smaller width (from 0.8)
            self.percent_y(0.15)   # Reduced height (from 0.25)
        )
        
        # Draw feedback background with gradient and rounded corners
        # Create the surface with transparency
        overlay = pygame.Surface((feedback_rect.width, feedback_rect.height), pygame.SRCALPHA)
        
        # Draw gradient background
        for y in range(feedback_rect.height):
            alpha = 180 - int(y / feedback_rect.height * 60)  # Less intense gradient
            pygame.draw.line(
                overlay,
                (20, 30, 60, alpha),
                (0, y),
                (feedback_rect.width, y)
            )
            
        # Draw border
        pygame.draw.rect(
            overlay,
            (100, 160, 255, 160),  # Slightly more transparent
            pygame.Rect(0, 0, feedback_rect.width, feedback_rect.height),
            2,  # Thinner border (from 3)
            border_radius=8  # Smaller radius (from 10)
        )
        
        # Apply overlay
        self.screen.blit(overlay, feedback_rect)
        
        # Determine simplified feedback text based on performance
        if num_correct == num_rotations and total_selections == num_rotations:
            # Perfect score
            result_text = "Perfect! All rotations identified."
            result_color = self.GREEN
            
            # Add a smaller visual reward for perfect score
            star_points = []
            center_x = feedback_rect.centerx
            center_y = feedback_rect.top - 10  # Closer to top (from -15)
            outer_radius = 10  # Smaller star (from 15)
            inner_radius = 5  # Smaller star (from 7)
            for i in range(10):  # 5-pointed star has 10 vertices
                angle = math.pi/2 + i * math.pi/5
                radius = outer_radius if i % 2 == 0 else inner_radius
                x = center_x + radius * math.cos(angle)
                y = center_y + radius * math.sin(angle)
                star_points.append((x, y))
            
            # Draw the star
            pygame.draw.polygon(self.screen, self.GREEN, star_points)
            
        elif num_correct == total_selections:
            # Correct but incomplete - shorter text
            result_text = f"Found {num_correct}/{num_rotations} rotations"
            result_color = (255, 200, 50)  # Yellow-orange
        else:
            # Some mistakes - shorter text
            result_text = f"Score: {num_correct}/{total_selections} correct"
            result_color = self.RED
        
        # Draw result text - centered in the overlay
        result_surface = self.small_font.render(result_text, True, result_color)  # Use small font instead of regular
        result_rect = result_surface.get_rect(centerx=feedback_rect.centerx, centery=feedback_rect.centery)
        self.screen.blit(result_surface, result_rect) 