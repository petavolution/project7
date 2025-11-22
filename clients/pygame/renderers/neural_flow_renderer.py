#!/usr/bin/env python3
"""
Specialized renderer for the Neural Flow module.

This renderer extends the enhanced generic renderer with specialized
visualization for the Neural Flow training module, which enhances
cognitive processing and neural pathway development.
"""

import pygame
import logging
import math
import random
from typing import Dict, Any, List, Tuple, Optional

# Import the enhanced generic renderer
from .enhanced_generic_renderer import EnhancedGenericRenderer

logger = logging.getLogger(__name__)

class NeuralFlowRenderer(EnhancedGenericRenderer):
    """Specialized renderer for the Neural Flow module."""
    
    def __init__(self, screen, module_id="neural_flow", config=None, colors=None, fonts=None, width=None, height=None):
        """Initialize the Neural Flow renderer.
        
        Args:
            screen: Pygame screen surface
            module_id: ID of the module (default: 'neural_flow')
            config: Optional configuration dictionary
            colors: Optional color scheme dictionary
            fonts: Optional fonts dictionary
            width: Optional screen width
            height: Optional screen height
        """
        # Call parent constructor
        super().__init__(screen, module_id, config, colors, fonts, width, height)
        
        # Apply Neural Flow specific colors
        self._apply_neural_flow_colors()
        
        # Initialize neural flow paths
        self.neural_paths = []
        self.active_paths = []
        self.pulsing_nodes = []
        self.particles = []
        
        # Initialize animation timers
        self.animation_timer = 0
        self.last_spawn_time = 0
        self.spawn_interval = 1000  # milliseconds
        
        # Performance settings
        self.max_particles = 200
        self.max_paths = 15
        
    def _apply_neural_flow_colors(self):
        """Apply color scheme specific to Neural Flow module."""
        neural_colors = {
            'neural_bg': (5, 10, 25),  # Very dark background for neural visualization
            'neural_node': (80, 140, 240),  # Bright blue nodes
            'neural_path': (40, 70, 120, 150),  # Semi-transparent path
            'neural_pulse': (140, 200, 255),  # Brighter pulse
            'neural_active': (120, 220, 255),  # Active path color
            'neural_particle': (200, 230, 255),  # Bright particles
            'focus_point': (255, 255, 255),  # White focus point
            'target_node': (255, 180, 80),  # Target node in orange
            'success_node': (120, 255, 140),  # Success node in green
            'error_node': (255, 100, 100),  # Error node in red
            'info_text': (180, 220, 250),  # Light blue for information text
        }
        
        # Update the colors dictionary
        self.colors.update(neural_colors)
        
        # Store these colors for future reference
        self.neural_flow_colors = neural_colors
    
    def render(self, state):
        """Render the Neural Flow module based on its state.
        
        Args:
            state: Current module state containing the neural flow information
                  
        Returns:
            List of rendered components for potential interaction
        """
        # Clear the screen with the background color
        self.screen.fill(self.colors['neural_bg'])
        
        # Set up layout if not already done
        if not self.layout:
            self._setup_layout()
        
        # Apply module-specific colors
        self._apply_neural_flow_colors()
        
        # Get content area dimensions
        content_rect = self.layout.get('content_rect')
        if content_rect:
            content_width = content_rect.width
            content_height = content_rect.height
            center_x = content_rect.centerx
            center_y = content_rect.centery
        else:
            content_width = self.width * 0.8
            content_height = self.height * 0.8
            center_x = self.width // 2
            center_y = self.height // 2
        
        # Extract state information
        phase = state.get('phase', 'preparation')
        level = state.get('level', 1)
        score = state.get('score', 0)
        target_nodes = state.get('target_nodes', [])
        active_nodes = state.get('active_nodes', [])
        success_nodes = state.get('success_nodes', [])
        error_nodes = state.get('error_nodes', [])
        message = state.get('message', 'Focus on the neural flow')
        
        # Update animation timer
        self.animation_timer += state.get('delta_time', 16)  # Default to 16ms if not provided
        
        # Generate or update neural paths if needed
        if not self.neural_paths or state.get('regenerate_paths', False):
            self._generate_neural_paths(center_x, center_y, content_width, content_height, level)
        
        # Update neural flow animations
        self._update_animations(state)
        
        # Draw neural network background
        self._draw_neural_network(center_x, center_y, content_width, content_height)
        
        # Draw message
        if message:
            message_font = self.fonts['medium']
            message_surf = message_font.render(message, True, self.colors['info_text'])
            message_rect = message_surf.get_rect(center=(center_x, self.height * 0.1))
            self.screen.blit(message_surf, message_rect)
        
        # Draw target nodes
        for node in target_nodes:
            pos = node.get('position', (0, 0))
            radius = node.get('radius', 10)
            pygame.draw.circle(
                self.screen,
                self.colors['target_node'],
                pos,
                radius,
                3
            )
        
        # Draw active nodes
        for node in active_nodes:
            pos = node.get('position', (0, 0))
            radius = node.get('radius', 8)
            pulse = math.sin(self.animation_timer / 200) * 2 + radius
            pygame.draw.circle(
                self.screen,
                self.colors['neural_active'],
                pos,
                int(pulse)
            )
        
        # Draw success nodes
        for node in success_nodes:
            pos = node.get('position', (0, 0))
            radius = node.get('radius', 8)
            pygame.draw.circle(
                self.screen,
                self.colors['success_node'],
                pos,
                radius
            )
        
        # Draw error nodes
        for node in error_nodes:
            pos = node.get('position', (0, 0))
            radius = node.get('radius', 8)
            pygame.draw.circle(
                self.screen,
                self.colors['error_node'],
                pos,
                radius
            )
        
        # Draw UI chrome (score, level, etc.)
        self._render_ui_chrome(state)
        
        # Draw particles
        for particle in self.particles:
            alpha = int(255 * (particle['life'] / particle['max_life']))
            color = self.colors['neural_particle']
            color_with_alpha = (color[0], color[1], color[2], alpha)
            
            size = particle['size'] * (particle['life'] / particle['max_life'])
            
            if size > 0:
                surface = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
                pygame.draw.circle(
                    surface,
                    color_with_alpha,
                    (size, size),
                    size
                )
                self.screen.blit(surface, (particle['x'] - size, particle['y'] - size))
        
        # Return interactive components for potential interaction
        return self._create_interactive_components(target_nodes, active_nodes)
        
    def _generate_neural_paths(self, center_x, center_y, width, height, level):
        """Generate neural paths based on level.
        
        Args:
            center_x: Center X position
            center_y: Center Y position
            width: Content width
            height: Content height
            level: Current level
        """
        # Clear existing paths
        self.neural_paths = []
        
        # Number of nodes increases with level
        num_nodes = min(20 + level * 5, 100)
        
        # Create nodes
        nodes = []
        for i in range(num_nodes):
            angle = random.random() * 2 * math.pi
            distance = random.random() * min(width, height) * 0.45
            x = center_x + math.cos(angle) * distance
            y = center_y + math.sin(angle) * distance
            
            # Add some randomness to node sizes based on distance from center
            size = random.randint(3, 8)
            if distance < min(width, height) * 0.15:
                size = random.randint(6, 12)  # Larger nodes near center
            
            nodes.append({
                'x': x,
                'y': y,
                'size': size,
                'connections': []
            })
        
        # Connect nodes - more connections at higher levels
        max_connections = min(3 + level // 2, 8)
        for i, node in enumerate(nodes):
            # Each node connects to 1-max_connections other nodes
            num_connections = random.randint(1, max_connections)
            
            # Find closest nodes
            distances = []
            for j, other_node in enumerate(nodes):
                if i != j:
                    dist = math.sqrt((node['x'] - other_node['x'])**2 + (node['y'] - other_node['y'])**2)
                    distances.append((dist, j))
            
            # Sort by distance and connect to closest
            distances.sort()
            for k in range(min(num_connections, len(distances))):
                connection_idx = distances[k][1]
                
                # Avoid duplicate connections
                if connection_idx not in node['connections']:
                    node['connections'].append(connection_idx)
                    
                    # Add path
                    self.neural_paths.append({
                        'start': (node['x'], node['y']),
                        'end': (nodes[connection_idx]['x'], nodes[connection_idx]['y']),
                        'start_node': i,
                        'end_node': connection_idx,
                        'active': False,
                        'pulse_pos': 0.0,
                        'pulse_speed': random.uniform(0.02, 0.1),
                        'thickness': random.randint(1, 3)
                    })
        
        # Store nodes
        self.nodes = nodes
        
        # Set a few random paths as initially active
        num_active = min(3 + level // 3, len(self.neural_paths))
        active_indices = random.sample(range(len(self.neural_paths)), num_active)
        for idx in active_indices:
            self.neural_paths[idx]['active'] = True
            self.active_paths.append(idx)
    
    def _update_animations(self, state):
        """Update all animations for the neural flow visualization.
        
        Args:
            state: Current module state
        """
        # Update pulse positions on active paths
        for idx in self.active_paths:
            path = self.neural_paths[idx]
            path['pulse_pos'] += path['pulse_speed']
            if path['pulse_pos'] > 1.0:
                path['pulse_pos'] = 0.0
                
                # Sometimes spawn particles at the end node
                if random.random() < 0.3:
                    self._spawn_particles(path['end'][0], path['end'][1], 3, 5)
        
        # Update pulsing nodes
        for i in range(len(self.pulsing_nodes) - 1, -1, -1):
            node = self.pulsing_nodes[i]
            node['life'] -= 1
            if node['life'] <= 0:
                self.pulsing_nodes.pop(i)
        
        # Update particles
        for i in range(len(self.particles) - 1, -1, -1):
            particle = self.particles[i]
            particle['life'] -= 1
            if particle['life'] <= 0:
                self.particles.pop(i)
            else:
                # Update position
                particle['x'] += particle['dx']
                particle['y'] += particle['dy']
                
                # Apply gravity/drag
                particle['dy'] += 0.05
                particle['dx'] *= 0.98
                particle['dy'] *= 0.98
        
        # Spawn new particles occasionally
        current_time = pygame.time.get_ticks()
        if current_time - self.last_spawn_time > self.spawn_interval and len(self.active_paths) > 0:
            # Pick a random active path
            path_idx = random.choice(self.active_paths)
            path = self.neural_paths[path_idx]
            
            # Calculate position along the path
            pos = path['pulse_pos']
            x = path['start'][0] + (path['end'][0] - path['start'][0]) * pos
            y = path['start'][1] + (path['end'][1] - path['start'][1]) * pos
            
            # Spawn particles
            self._spawn_particles(x, y, 2, 5)
            
            self.last_spawn_time = current_time
    
    def _spawn_particles(self, x, y, min_count, max_count):
        """Spawn particles at a position.
        
        Args:
            x: X position
            y: Y position
            min_count: Minimum number of particles
            max_count: Maximum number of particles
        """
        # Check if we can spawn more particles
        if len(self.particles) >= self.max_particles:
            return
            
        count = random.randint(min_count, max_count)
        for _ in range(count):
            # Random velocity
            speed = random.uniform(0.5, 2.0)
            angle = random.uniform(0, 2 * math.pi)
            dx = math.cos(angle) * speed
            dy = math.sin(angle) * speed
            
            # Random size and life
            size = random.uniform(1, 3)
            life = random.randint(20, 60)
            
            # Add particle
            self.particles.append({
                'x': x,
                'y': y,
                'dx': dx,
                'dy': dy,
                'size': size,
                'life': life,
                'max_life': life
            })
    
    def _draw_neural_network(self, center_x, center_y, width, height):
        """Draw the neural network visualization.
        
        Args:
            center_x: Center X position
            center_y: Center Y position
            width: Content width
            height: Content height
        """
        # Draw all paths
        for path in self.neural_paths:
            if path['active']:
                color = self.colors['neural_path']
                # Draw the main path
                pygame.draw.line(
                    self.screen,
                    color,
                    path['start'],
                    path['end'],
                    path['thickness']
                )
                
                # Draw the pulse
                pulse_x = path['start'][0] + (path['end'][0] - path['start'][0]) * path['pulse_pos']
                pulse_y = path['start'][1] + (path['end'][1] - path['start'][1]) * path['pulse_pos']
                
                # Pulse size pulsates
                pulse_size = 3 + math.sin(self.animation_timer / 100) * 2
                
                pygame.draw.circle(
                    self.screen,
                    self.colors['neural_pulse'],
                    (pulse_x, pulse_y),
                    pulse_size
                )
            else:
                # Draw inactive paths with a more subtle color
                color = (self.colors['neural_path'][0] // 2, 
                         self.colors['neural_path'][1] // 2, 
                         self.colors['neural_path'][2] // 2, 
                         self.colors['neural_path'][3] // 2)
                pygame.draw.line(
                    self.screen,
                    color,
                    path['start'],
                    path['end'],
                    1
                )
        
        # Draw all nodes
        for node in self.nodes:
            pygame.draw.circle(
                self.screen,
                self.colors['neural_node'],
                (node['x'], node['y']),
                node['size']
            )
    
    def _create_interactive_components(self, target_nodes, active_nodes):
        """Create interactive components for the neural flow visualization.
        
        Args:
            target_nodes: List of target nodes
            active_nodes: List of active nodes
            
        Returns:
            List of interactive components
        """
        interactive_components = []
        
        # Add target nodes as interactive
        for i, node in enumerate(target_nodes):
            pos = node.get('position', (0, 0))
            radius = node.get('radius', 10)
            
            interactive_components.append({
                'type': 'circle',
                'id': f'target_node_{i}',
                'position': pos,
                'radius': radius,
                'action': 'activate_node',
                'data': {'node_id': node.get('id', i)}
            })
        
        # Add active nodes as interactive
        for i, node in enumerate(active_nodes):
            pos = node.get('position', (0, 0))
            radius = node.get('radius', 8)
            
            interactive_components.append({
                'type': 'circle',
                'id': f'active_node_{i}',
                'position': pos,
                'radius': radius,
                'action': 'deactivate_node',
                'data': {'node_id': node.get('id', i)}
            })
        
        return interactive_components
    
    def _render_ui_chrome(self, state):
        """Render UI chrome elements like score, level, title bar, etc.
        
        Args:
            state: Current module state
        """
        # Extract state information
        score = state.get('score', 0)
        level = state.get('level', 1)
        module_name = state.get('module_name', self.module_info.get('name', 'Neural Flow'))
        
        # Draw module name in top center
        title_font = self.fonts.get('title', self.fonts['large'])
        title_surf = title_font.render(module_name, True, self.colors['text'])
        title_rect = title_surf.get_rect(center=(self.width // 2, 30))
        self.screen.blit(title_surf, title_rect)
        
        # Draw score on top left
        score_text = f"Score: {score}"
        score_font = self.fonts.get('medium', self.fonts['medium'])
        score_surf = score_font.render(score_text, True, self.colors['text'])
        self.screen.blit(score_surf, (20, 20))
        
        # Draw level on top right
        level_text = f"Level: {level}"
        level_font = self.fonts.get('medium', self.fonts['medium'])
        level_surf = level_font.render(level_text, True, self.colors['text'])
        level_rect = level_surf.get_rect(topright=(self.width - 20, 20))
        self.screen.blit(level_surf, level_rect)
        
        # Draw phase indicator
        phase = state.get('phase', 'preparation')
        phase_text = f"Phase: {phase.capitalize()}"
        phase_font = self.fonts.get('medium', self.fonts['medium'])
        phase_surf = phase_font.render(phase_text, True, self.colors['text'])
        phase_rect = phase_surf.get_rect(bottomleft=(20, self.height - 20))
        self.screen.blit(phase_surf, phase_rect) 