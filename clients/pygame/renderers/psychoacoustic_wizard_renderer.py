#!/usr/bin/env python3
"""
PsychoacousticWizard PyGame Renderer

This module provides the PyGame-specific rendering for the PsychoacousticWizard
training module, visualizing the note highway, rhythm elements and handling audio playback.
"""

import pygame
import time
import math
import random
import logging
from typing import Dict, Any, Tuple, List, Optional

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False
    print("Warning: numpy not available, audio synthesis will be limited")

# Import base renderer
try:
    from .music_components_renderer import MusicComponentsRenderer
except ImportError:
    # When running directly
    import sys
    from pathlib import Path
    project_root = Path(__file__).parents[3]
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    from MetaMindIQTrain.clients.pygame.renderers.music_components_renderer import MusicComponentsRenderer

# Configure logging
logger = logging.getLogger(__name__)

class PsychoacousticWizardRenderer(MusicComponentsRenderer):
    """PyGame renderer for the PsychoacousticWizard module."""
    
    def __init__(self, screen, session_manager, module, config=None):
        """Initialize the renderer.
        
        Args:
            screen: PyGame screen surface to render to
            session_manager: SessionManager instance
            module: Training module instance
            config: Optional configuration dictionary
        """
        super().__init__(screen, session_manager, module, config)
        
        # Rhythm game specific state
        self.note_highway = []  # List of notes to hit
        self.hit_line_pos = self.height * 0.75  # Y-position of the hit line
        self.highway_speed = 200  # Speed of notes in pixels per second
        self.last_update = time.time()
        
        # Visual effects
        self.particles = []
        self.last_hit_time = 0
        self.last_combo_milestone = 0
        
        # Game state
        self.combo = 0
        self.crowd_energy = 0
        self.score = 0
        self.level = 1
        
        # Register rhythm-specific achievements
        self.register_rhythm_achievements()
    
    def register_module_specific_achievements(self):
        """Register rhythm-specific achievements."""
        self.register_rhythm_achievements()
    
    def register_rhythm_achievements(self):
        """Register achievements specific to rhythm games."""
        # Already handled by the base MusicAchievementSystem
        pass
        
    def render(self):
        """Render the current state of the PsychoacousticWizard module."""
        if not hasattr(self.module, 'note_highway'):
            return super().render()
            
        # Get screen dimensions
        width, height = self.screen.get_size()
        
        # Clear screen with gradient background
        self.draw_gradient_background()
        
        # Draw title
        title = "Psychoacoustic Wizard"
        if hasattr(self.module, 'level'):
            title += f" - Level {self.module.level}"
        self.draw_title(title)
        
        # Draw score and combo
        self.draw_stats()
        
        # Draw note highway
        self.draw_note_highway()
        
        # Draw crowd energy meter
        self.draw_crowd_energy()
        
        # Draw keyboard
        keyboard_width = self.keyboard.white_key_width * len(self.keyboard.get_key_data()['white_keys'])
        self.render_piano_keyboard(self.width // 2 - keyboard_width // 2, self.height - 150)
        
        # Draw waveform visualization
        if hasattr(self.module, 'audio_buffer') and self.module.audio_buffer is not None:
            self.render_waveform(self.width // 2 - self.waveform.width // 2, 100, self.module.audio_buffer)
        
        # Draw particles
        self.update_particles()
        self.draw_particles()
        
        # Draw feedback and achievement notifications
        self.render_feedback()
        self.render_achievement_notification()
    
    def draw_gradient_background(self):
        """Draw a gradient background based on crowd energy."""
        # Energy affects color
        energy_factor = self.module.crowd_energy / 100 if hasattr(self.module, 'crowd_energy') else 0
        
        # Base color: deep blue to purple
        color1 = (20, 20, 40)  # Dark blue
        color2 = (60, 20, 80)  # Purple
        
        # Energy accent: add red as energy increases
        if energy_factor > 0.5:
            color2 = (
                min(255, int(60 + (energy_factor - 0.5) * 2 * 195)),  # More red as energy increases
                max(0, int(20 - (energy_factor - 0.5) * 40)),         # Less green
                min(255, int(80 + (energy_factor - 0.5) * 2 * 100))   # More blue
            )
        
        # Draw gradient
        rect = pygame.Rect(0, 0, self.width, self.height)
        pygame.draw.rect(self.screen, color1, rect)
        
        # Create gradient by drawing lines with gradually changing color
        for i in range(self.height):
            # Calculate interpolation factor
            f = i / self.height
            
            # Interpolate colors
            r = int(color1[0] * (1-f) + color2[0] * f)
            g = int(color1[1] * (1-f) + color2[1] * f)
            b = int(color1[2] * (1-f) + color2[2] * f)
            
            # Draw line
            pygame.draw.line(self.screen, (r,g,b), (0, i), (self.width, i))
    
    def draw_stats(self):
        """Draw score, combo, and other stats."""
        # Draw combo
        if hasattr(self.module, 'combo_multiplier'):
            combo_text = f"Combo: {self.module.combo_multiplier}x"
            combo_color = (255, 255, 255)
            
            # Color combo based on value
            if self.module.combo_multiplier >= 8:
                combo_color = (255, 215, 0)  # Gold
            elif self.module.combo_multiplier >= 4:
                combo_color = (0, 255, 200)  # Teal
            
            combo_surf = self.title_font.render(combo_text, True, combo_color)
            combo_rect = combo_surf.get_rect(midtop=(self.width // 2, 80))
            self.screen.blit(combo_surf, combo_rect)
        
        # Draw score
        if hasattr(self.module, 'score'):
            score_text = f"Score: {self.module.score}"
            score_surf = self.note_font.render(score_text, True, (255, 255, 255))
            self.screen.blit(score_surf, (20, 80))
        
        # Draw tempo
        if hasattr(self.module, 'tempo'):
            tempo_text = f"Tempo: {self.module.tempo} BPM"
            tempo_surf = self.note_font.render(tempo_text, True, (255, 255, 255))
            self.screen.blit(tempo_surf, (self.width - tempo_surf.get_width() - 20, 80))
    
    def draw_note_highway(self):
        """Draw the note highway with upcoming notes to hit."""
        if not hasattr(self.module, 'note_highway'):
            return
            
        # Define highway dimensions
        highway_width = self.width * 0.8
        highway_height = self.height * 0.5
        highway_x = self.width // 2 - highway_width // 2
        highway_y = self.height * 0.25
        
        # Draw highway background
        highway_rect = pygame.Rect(highway_x, highway_y, highway_width, highway_height)
        pygame.draw.rect(self.screen, (20, 20, 30), highway_rect)
        pygame.draw.rect(self.screen, (100, 100, 120), highway_rect, 2)
        
        # Draw horizontal guide lines
        note_lanes = 7  # Number of white keys to show
        lane_height = highway_height / note_lanes
        
        for i in range(1, note_lanes):
            line_y = highway_y + i * lane_height
            pygame.draw.line(self.screen, (50, 50, 70), 
                           (highway_x, line_y), 
                           (highway_x + highway_width, line_y), 1)
        
        # Draw the hit line
        hit_line_y = highway_y + highway_height * 0.8
        pygame.draw.line(self.screen, (255, 255, 255), 
                        (highway_x, hit_line_y), 
                        (highway_x + highway_width, hit_line_y), 3)
        
        # Draw each note in the highway
        for note in self.module.note_highway:
            # Calculate note position based on time until hit
            time_until_hit = note['time'] - self.module.game_time
            y_offset = time_until_hit * self.highway_speed
            note_y = hit_line_y - y_offset
            
            # Skip notes that are off the highway
            if note_y < highway_y or note_y > highway_y + highway_height:
                continue
            
            # Note color based on pitch
            note_color = self.note_colors.get(note['pitch'][0], (200, 200, 200))
            
            # Determine lane based on pitch
            # For simplicity, we map C-B to lanes 0-6
            note_name = note['pitch'][0]
            note_idx = "CDEFGAB".index(note_name) if note_name in "CDEFGAB" else 0
            note_x = highway_x + (note_idx / 7) * highway_width + highway_width / 14
            
            # Draw the note
            note_size = 30
            if note['duration'] > 0.5:
                # Draw as sustained note (rectangle)
                note_duration_pixels = note['duration'] * self.highway_speed
                note_rect = pygame.Rect(note_x - note_size/2, note_y - note_duration_pixels, 
                                     note_size, note_duration_pixels)
                pygame.draw.rect(self.screen, note_color, note_rect, 0, 5)
                pygame.draw.rect(self.screen, (255, 255, 255), note_rect, 2, 5)
            else:
                # Draw as regular note (circle)
                pygame.draw.circle(self.screen, note_color, (int(note_x), int(note_y)), note_size//2)
                pygame.draw.circle(self.screen, (255, 255, 255), (int(note_x), int(note_y)), note_size//2, 2)
    
    def draw_crowd_energy(self):
        """Draw the crowd energy meter."""
        if not hasattr(self.module, 'crowd_energy'):
            return
            
        # Draw energy meter on the right side
        meter_width = 30
        meter_height = self.height * 0.4
        meter_x = self.width - meter_width - 20
        meter_y = 120
        
        # Draw background
        meter_bg_rect = pygame.Rect(meter_x, meter_y, meter_width, meter_height)
        pygame.draw.rect(self.screen, (40, 40, 50), meter_bg_rect, 0, 5)
        
        # Draw fill based on energy level
        energy_height = (self.module.crowd_energy / 100) * meter_height
        energy_rect = pygame.Rect(meter_x, meter_y + meter_height - energy_height, 
                               meter_width, energy_height)
        
        # Color changes with energy level
        if self.module.crowd_energy < 30:
            energy_color = (150, 50, 50)  # Red
        elif self.module.crowd_energy < 70:
            energy_color = (200, 200, 50)  # Yellow
        else:
            energy_color = (50, 200, 50)  # Green
        
        pygame.draw.rect(self.screen, energy_color, energy_rect, 0, 5)
        
        # Draw outline
        pygame.draw.rect(self.screen, (150, 150, 170), meter_bg_rect, 2, 5)
        
        # Draw "Crowd Energy" label
        energy_label = self.small_font.render("Crowd", True, (200, 200, 220))
        energy_label2 = self.small_font.render("Energy", True, (200, 200, 220))
        
        self.screen.blit(energy_label, (meter_x - 5, meter_y - 40))
        self.screen.blit(energy_label2, (meter_x - 8, meter_y - 20))
    
    def create_particles(self, x, y, color, count=10):
        """Create particle effects.
        
        Args:
            x: X position to create particles at
            y: Y position to create particles at
            color: Particle color
            count: Number of particles to create
        """
        for _ in range(count):
            # Random velocity
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(50, 200)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            
            # Random size and lifetime
            size = random.uniform(2, 8)
            lifetime = random.uniform(0.5, 1.5)
            
            # Create the particle
            particle = {
                'x': x,
                'y': y,
                'vx': vx,
                'vy': vy,
                'color': color,
                'size': size,
                'lifetime': lifetime,
                'age': 0
            }
            
            self.particles.append(particle)
    
    def update_particles(self):
        """Update particle effects."""
        current_time = time.time()
        dt = min(0.05, current_time - self.last_update)  # Cap to avoid huge jumps
        self.last_update = current_time
        
        # Update each particle
        for particle in self.particles[:]:
            # Update position
            particle['x'] += particle['vx'] * dt
            particle['y'] += particle['vy'] * dt
            
            # Add gravity
            particle['vy'] += 400 * dt  # Gravity
            
            # Age the particle
            particle['age'] += dt
            
            # Remove if expired
            if particle['age'] >= particle['lifetime']:
                self.particles.remove(particle)
    
    def draw_particles(self):
        """Draw all active particles."""
        for particle in self.particles:
            # Calculate alpha based on age
            alpha = 255 * (1 - particle['age'] / particle['lifetime'])
            
            # Create color with alpha
            color = particle['color']
            color_with_alpha = (color[0], color[1], color[2], int(alpha))
            
            # Draw the particle
            size = int(particle['size'] * (1 - particle['age'] / particle['lifetime'] * 0.5))
            
            # Create a small surface for the particle with alpha
            particle_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            pygame.draw.circle(particle_surf, color_with_alpha, (size, size), size)
            
            # Blit the particle
            self.screen.blit(particle_surf, (particle['x'] - size, particle['y'] - size))
    
    def handle_event(self, event):
        """Handle pygame events.
        
        Args:
            event: PyGame event
            
        Returns:
            bool: True if the event was handled
        """
        if event.type == pygame.KEYDOWN:
            # Handle note key presses
            if event.key in [pygame.K_a, pygame.K_s, pygame.K_d, pygame.K_f, pygame.K_g, pygame.K_h, pygame.K_j]:
                # Map keys to note names
                key_to_note = {
                    pygame.K_a: "C4",
                    pygame.K_s: "D4",
                    pygame.K_d: "E4",
                    pygame.K_f: "F4",
                    pygame.K_g: "G4",
                    pygame.K_h: "A4",
                    pygame.K_j: "B4"
                }
                
                note = key_to_note[event.key]
                
                # Send note hit to module
                if hasattr(self.module, 'handle_note_hit'):
                    self.module.handle_note_hit(note[0])
                
                # Play the note
                self.play_note(note)
                
                # Create particle effect
                note_color = self.note_colors.get(note[0], (200, 200, 200))
                self.create_particles(self.width // 2, self.hit_line_pos, note_color, 15)
                
                # Update combo display
                if hasattr(self.module, 'combo_multiplier') and self.module.combo_multiplier > 0:
                    if self.module.combo_multiplier % 4 == 0 and self.module.combo_multiplier > self.last_combo_milestone:
                        self.last_combo_milestone = self.module.combo_multiplier
                        self.show_feedback(f"Combo x{self.module.combo_multiplier}!", True)
                
                return True
        
        return super().handle_event(event)
    
    def update(self, dt):
        """Update game state.
        
        Args:
            dt: Time delta in seconds
        """
        super().update(dt)
        
        # Check for missed notes
        if hasattr(self.module, 'note_highway') and hasattr(self.module, 'game_time'):
            for note in self.module.note_highway[:]:
                time_until_hit = note['time'] - self.module.game_time
                
                # If note should have been hit but wasn't
                if time_until_hit < -0.2:
                    # Send miss notification to module
                    if hasattr(self.module, 'handle_note_miss'):
                        self.module.handle_note_miss(note)
                    
                    # Show feedback
                    self.show_feedback("Miss!", False)
                    
                    # Reset combo milestone
                    self.last_combo_milestone = 0

# Register renderer
def register_renderer():
    return {
        'id': 'psychoacoustic_wizard',
        'renderer_class': PsychoacousticWizardRenderer
    }