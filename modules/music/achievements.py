#!/usr/bin/env python3
"""
Achievements System for Music Training Modules

This module implements a gamification layer for music-related training modules
that includes achievements, progression tracking, and performance analytics.
"""

import logging
import json
import os
import time
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any
from pathlib import Path

# Configure logging
logger = logging.getLogger(__name__)

class Achievement:
    """
    Represents a single achievement that can be earned by the user.
    """
    
    def __init__(self, achievement_id, name, description, icon_name=None, 
                 category=None, points=10, hidden=False):
        """
        Initialize an achievement.
        
        Args:
            achievement_id: Unique identifier for the achievement
            name: Display name of the achievement
            description: Description of how to earn the achievement
            icon_name: Name of icon file (without path)
            category: Category for grouping achievements
            points: Points awarded for earning the achievement
            hidden: Whether the achievement is hidden until earned
        """
        self.id = achievement_id
        self.name = name
        self.description = description
        self.icon_name = icon_name or "default_achievement.png"
        self.category = category or "General"
        self.points = points
        self.hidden = hidden
        self.earned = False
        self.earned_date = None
        self.progress = 0
        self.max_progress = 100  # Percent
    
    def set_progress(self, current, maximum=None):
        """
        Update progress toward earning the achievement.
        
        Args:
            current: Current progress value
            maximum: Maximum progress value (optional)
        """
        if maximum is not None and maximum > 0:
            self.max_progress = maximum
            self.progress = min(current, maximum)
        else:
            self.progress = current
        
        # Check if achievement is earned
        if not self.earned and self.progress >= self.max_progress:
            self.earn()
    
    def earn(self):
        """Mark the achievement as earned."""
        if not self.earned:
            self.earned = True
            self.earned_date = datetime.now()
            logger.info(f"Achievement earned: {self.name}")
    
    def to_dict(self):
        """
        Convert achievement to a dictionary for serialization.
        
        Returns:
            dict: Dictionary representation of the achievement
        """
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'icon': self.icon_name,
            'category': self.category,
            'points': self.points,
            'hidden': self.hidden,
            'earned': self.earned,
            'earned_date': self.earned_date.isoformat() if self.earned_date else None,
            'progress': self.progress,
            'max_progress': self.max_progress
        }
    
    @classmethod
    def from_dict(cls, data):
        """
        Create an achievement from a dictionary.
        
        Args:
            data: Dictionary containing achievement data
            
        Returns:
            Achievement: New achievement instance
        """
        achievement = cls(
            achievement_id=data['id'],
            name=data['name'],
            description=data['description'],
            icon_name=data.get('icon'),
            category=data.get('category'),
            points=data.get('points', 10),
            hidden=data.get('hidden', False)
        )
        
        achievement.earned = data.get('earned', False)
        achievement.progress = data.get('progress', 0)
        achievement.max_progress = data.get('max_progress', 100)
        
        if data.get('earned_date'):
            try:
                achievement.earned_date = datetime.fromisoformat(data['earned_date'])
            except (ValueError, TypeError):
                achievement.earned_date = None
        
        return achievement


class PerformanceTracker:
    """
    Tracks user performance across multiple music training sessions.
    """
    
    def __init__(self):
        """Initialize the performance tracker."""
        self.total_sessions = 0
        self.total_time = 0  # In seconds
        self.correct_answers = 0
        self.total_answers = 0
        self.scores = []
        self.streaks = []
        self.module_history = {}  # Module ID -> Performance stats
        self.element_performance = {}  # Musical element -> Performance stats
        self.last_session_time = None
    
    def start_session(self, module_id):
        """
        Start a new training session.
        
        Args:
            module_id: ID of the module being used
        """
        self.total_sessions += 1
        self.last_session_time = time.time()
        
        # Initialize module history if needed
        if module_id not in self.module_history:
            self.module_history[module_id] = {
                'sessions': 0,
                'total_time': 0,
                'scores': [],
                'correct': 0,
                'total': 0
            }
        
        self.module_history[module_id]['sessions'] += 1
    
    def end_session(self, module_id, score):
        """
        End the current training session.
        
        Args:
            module_id: ID of the module being used
            score: Final score for the session
        """
        if self.last_session_time is not None:
            session_time = time.time() - self.last_session_time
            self.total_time += session_time
            
            # Update module history
            if module_id in self.module_history:
                self.module_history[module_id]['total_time'] += session_time
                self.module_history[module_id]['scores'].append(score)
            
            self.scores.append(score)
            self.last_session_time = None
    
    def record_answer(self, module_id, element_type, element_value, correct):
        """
        Record an answer to a music question.
        
        Args:
            module_id: ID of the module being used
            element_type: Type of musical element (e.g., 'scale', 'chord', 'interval')
            element_value: Specific value (e.g., 'major', 'minor7', 'perfect fifth')
            correct: Whether the answer was correct
        """
        # Update total counts
        self.total_answers += 1
        if correct:
            self.correct_answers += 1
        
        # Update module history
        if module_id in self.module_history:
            self.module_history[module_id]['total'] += 1
            if correct:
                self.module_history[module_id]['correct'] += 1
        
        # Update element performance
        element_key = f"{element_type}:{element_value}"
        if element_key not in self.element_performance:
            self.element_performance[element_key] = {
                'correct': 0,
                'total': 0,
                'last_seen': None
            }
        
        self.element_performance[element_key]['total'] += 1
        if correct:
            self.element_performance[element_key]['correct'] += 1
        self.element_performance[element_key]['last_seen'] = time.time()
    
    def record_streak(self, length):
        """
        Record a streak of correct answers.
        
        Args:
            length: Length of the streak
        """
        self.streaks.append(length)
    
    def get_accuracy(self, module_id=None, element_type=None):
        """
        Get accuracy statistics.
        
        Args:
            module_id: Optional module ID to filter by
            element_type: Optional element type to filter by
            
        Returns:
            float: Accuracy percentage
        """
        if module_id is not None:
            if module_id in self.module_history:
                stats = self.module_history[module_id]
                return (stats['correct'] / stats['total'] * 100) if stats['total'] > 0 else 0
            return 0
        
        if element_type is not None:
            filtered_elements = {k: v for k, v in self.element_performance.items() 
                               if k.startswith(f"{element_type}:")}
            
            total_correct = sum(e['correct'] for e in filtered_elements.values())
            total_attempts = sum(e['total'] for e in filtered_elements.values())
            
            return (total_correct / total_attempts * 100) if total_attempts > 0 else 0
        
        # Overall accuracy
        return (self.correct_answers / self.total_answers * 100) if self.total_answers > 0 else 0
    
    def get_weak_areas(self, limit=5):
        """
        Get the weakest areas that need improvement.
        
        Args:
            limit: Maximum number of weak areas to return
            
        Returns:
            list: List of (element_key, accuracy) tuples sorted by lowest accuracy
        """
        # Filter elements with at least 3 attempts
        elements = {k: v for k, v in self.element_performance.items() if v['total'] >= 3}
        
        # Calculate accuracy for each element
        element_accuracy = []
        for key, stats in elements.items():
            accuracy = (stats['correct'] / stats['total'] * 100) if stats['total'] > 0 else 0
            element_accuracy.append((key, accuracy))
        
        # Sort by accuracy (ascending)
        element_accuracy.sort(key=lambda x: x[1])
        
        return element_accuracy[:limit]
    
    def get_spaced_repetition_items(self, limit=5):
        """
        Get items due for spaced repetition review.
        
        Args:
            limit: Maximum number of items to return
            
        Returns:
            list: List of element keys due for review
        """
        now = time.time()
        due_items = []
        
        for key, stats in self.element_performance.items():
            # Skip items with fewer than 2 attempts
            if stats['total'] < 2:
                continue
            
            # Calculate accuracy
            accuracy = (stats['correct'] / stats['total'] * 100) if stats['total'] > 0 else 0
            
            # Calculate days since last seen
            days_since_last = 0
            if stats['last_seen'] is not None:
                days_since_last = (now - stats['last_seen']) / (24 * 3600)
            
            # Items are due sooner if accuracy is lower
            # Rough formula: 10 days per 20% accuracy
            due_days = (accuracy / 20) * 10
            
            # Item is due if it's been longer than due_days
            if days_since_last >= due_days:
                due_items.append((key, accuracy))
        
        # Sort by accuracy (ascending)
        due_items.sort(key=lambda x: x[1])
        
        return [item[0] for item in due_items[:limit]]
    
    def to_dict(self):
        """
        Convert tracker data to a dictionary for serialization.
        
        Returns:
            dict: Dictionary representation of the performance tracker
        """
        return {
            'total_sessions': self.total_sessions,
            'total_time': self.total_time,
            'correct_answers': self.correct_answers,
            'total_answers': self.total_answers,
            'scores': self.scores,
            'streaks': self.streaks,
            'module_history': self.module_history,
            'element_performance': self.element_performance
        }
    
    @classmethod
    def from_dict(cls, data):
        """
        Create a performance tracker from a dictionary.
        
        Args:
            data: Dictionary containing tracker data
            
        Returns:
            PerformanceTracker: New performance tracker instance
        """
        tracker = cls()
        
        tracker.total_sessions = data.get('total_sessions', 0)
        tracker.total_time = data.get('total_time', 0)
        tracker.correct_answers = data.get('correct_answers', 0)
        tracker.total_answers = data.get('total_answers', 0)
        tracker.scores = data.get('scores', [])
        tracker.streaks = data.get('streaks', [])
        tracker.module_history = data.get('module_history', {})
        tracker.element_performance = data.get('element_performance', {})
        
        return tracker


class MusicAchievementSystem:
    """
    Main achievement system for music training modules.
    """
    
    def __init__(self, save_dir=None):
        """
        Initialize the achievement system.
        
        Args:
            save_dir: Directory to save achievement data (optional)
        """
        self.achievements = {}
        self.performance = PerformanceTracker()
        self.user_points = 0
        self.user_level = 1
        self.unlocked_content = set()
        
        # Set save directory
        if save_dir is None:
            self.save_dir = Path.home() / ".MetaMindIQTrain" / "achievements"
        else:
            self.save_dir = Path(save_dir)
        
        # Create directory if it doesn't exist
        self.save_dir.mkdir(parents=True, exist_ok=True)
        
        # Register default achievements
        self._register_default_achievements()
        
        # Try to load existing data
        self.load()
    
    def _register_default_achievements(self):
        """Register default music-related achievements."""
        # Perfect rounds
        self.register_achievement(
            Achievement(
                "perfect_round_1",
                "Perfect Round",
                "Complete a training round with 100% accuracy",
                category="Performance",
                points=10
            )
        )
        
        self.register_achievement(
            Achievement(
                "perfect_round_5",
                "5x Perfect",
                "Complete 5 training rounds with 100% accuracy",
                category="Performance",
                points=25,
                hidden=True
            )
        )
        
        # Streaks
        self.register_achievement(
            Achievement(
                "streak_10",
                "10 Streak",
                "Correctly answer 10 questions in a row",
                category="Performance",
                points=10
            )
        )
        
        self.register_achievement(
            Achievement(
                "streak_25",
                "25 Streak",
                "Correctly answer 25 questions in a row",
                category="Performance",
                points=25
            )
        )
        
        self.register_achievement(
            Achievement(
                "streak_50",
                "50 Streak",
                "Correctly answer 50 questions in a row",
                category="Performance",
                points=50,
                hidden=True
            )
        )
        
        # Speed
        self.register_achievement(
            Achievement(
                "speed_demon",
                "Speed Demon",
                "Answer 10 questions correctly with an average time under 3 seconds",
                category="Performance",
                points=25
            )
        )
        
        # Music theory specific
        self.register_achievement(
            Achievement(
                "scale_master",
                "Scale Master",
                "Correctly identify 20 different scales",
                category="Music Theory",
                points=30
            )
        )
        
        self.register_achievement(
            Achievement(
                "chord_master",
                "Chord Master",
                "Correctly identify 20 different chord types",
                category="Music Theory",
                points=30
            )
        )
        
        self.register_achievement(
            Achievement(
                "interval_master",
                "Interval Master",
                "Correctly identify all interval types",
                category="Music Theory",
                points=35
            )
        )
        
        # Rhythm specific
        self.register_achievement(
            Achievement(
                "rhythm_novice",
                "Rhythm Novice",
                "Complete level 3 in PsychoacousticWizard",
                category="Rhythm",
                points=15
            )
        )
        
        self.register_achievement(
            Achievement(
                "rhythm_adept",
                "Rhythm Adept",
                "Complete level 7 in PsychoacousticWizard",
                category="Rhythm",
                points=30
            )
        )
        
        self.register_achievement(
            Achievement(
                "rhythm_master",
                "Rhythm Master",
                "Complete level 10 in PsychoacousticWizard",
                category="Rhythm",
                points=50,
                hidden=True
            )
        )
        
        # Combined achievements
        self.register_achievement(
            Achievement(
                "music_enthusiast",
                "Music Enthusiast",
                "Spend at least 1 hour in music training modules",
                category="Dedication",
                points=20
            )
        )
        
        self.register_achievement(
            Achievement(
                "music_devotee",
                "Music Devotee",
                "Spend at least 5 hours in music training modules",
                category="Dedication",
                points=40,
                hidden=True
            )
        )
        
        self.register_achievement(
            Achievement(
                "harmony_master",
                "Harmony Master",
                "Earn the Scale Master, Chord Master, and Interval Master achievements",
                category="Mastery",
                points=50,
                hidden=True
            )
        )
    
    def register_achievement(self, achievement):
        """
        Register a new achievement.
        
        Args:
            achievement: Achievement object to register
        """
        self.achievements[achievement.id] = achievement
    
    def get_achievements(self, category=None, earned_only=False, hidden=None):
        """
        Get achievements filtered by criteria.
        
        Args:
            category: Filter by category (optional)
            earned_only: Only include earned achievements
            hidden: Include hidden achievements (None=all, True=only hidden, False=no hidden)
            
        Returns:
            list: List of matching Achievement objects
        """
        filtered = []
        
        for achievement in self.achievements.values():
            # Filter by category
            if category is not None and achievement.category != category:
                continue
            
            # Filter by earned status
            if earned_only and not achievement.earned:
                continue
            
            # Filter by hidden status
            if hidden is not None and achievement.hidden != hidden:
                continue
            
            # Don't show hidden achievements that aren't earned
            if achievement.hidden and not achievement.earned and hidden is not True:
                continue
            
            filtered.append(achievement)
        
        return filtered
    
    def check_achievement_progress(self, module_id, game_stats=None):
        """
        Check for progress on achievements based on current stats.
        
        Args:
            module_id: ID of the current module
            game_stats: Dictionary of game statistics
            
        Returns:
            list: List of newly earned achievements
        """
        if game_stats is None:
            game_stats = {}
        
        newly_earned = []
        
        # Update specific achievements based on stats
        
        # Perfect rounds
        if game_stats.get('perfect_round', False):
            a1 = self.achievements.get("perfect_round_1")
            if a1 and not a1.earned:
                a1.earn()
                newly_earned.append(a1)
            
            a5 = self.achievements.get("perfect_round_5")
            if a5:
                perfect_rounds = game_stats.get('total_perfect_rounds', 0)
                a5.set_progress(perfect_rounds, 5)
                if a5.earned and a5 not in newly_earned:
                    newly_earned.append(a5)
        
        # Streaks
        current_streak = game_stats.get('current_streak', 0)
        max_streak = game_stats.get('max_streak', 0)
        
        streak_achievements = [
            ("streak_10", 10),
            ("streak_25", 25),
            ("streak_50", 50)
        ]
        
        for achievement_id, required_streak in streak_achievements:
            achievement = self.achievements.get(achievement_id)
            if achievement:
                achievement.set_progress(max_streak, required_streak)
                if achievement.earned and achievement not in newly_earned:
                    newly_earned.append(achievement)
        
        # Speed achievements
        if game_stats.get('speed_questions_correct', 0) >= 10 and game_stats.get('avg_answer_time', 999) <= 3:
            speed_achievement = self.achievements.get("speed_demon")
            if speed_achievement and not speed_achievement.earned:
                speed_achievement.earn()
                newly_earned.append(speed_achievement)
        
        # Module-specific achievements
        
        # Music Theory
        if module_id == "music_theory":
            # Scale Master
            scales_identified = game_stats.get('unique_scales_identified', 0)
            scale_achievement = self.achievements.get("scale_master")
            if scale_achievement:
                scale_achievement.set_progress(scales_identified, 20)
                if scale_achievement.earned and scale_achievement not in newly_earned:
                    newly_earned.append(scale_achievement)
            
            # Chord Master
            chords_identified = game_stats.get('unique_chords_identified', 0)
            chord_achievement = self.achievements.get("chord_master")
            if chord_achievement:
                chord_achievement.set_progress(chords_identified, 20)
                if chord_achievement.earned and chord_achievement not in newly_earned:
                    newly_earned.append(chord_achievement)
            
            # Interval Master
            intervals_identified = game_stats.get('unique_intervals_identified', 0)
            interval_achievement = self.achievements.get("interval_master")
            if interval_achievement:
                interval_achievement.set_progress(intervals_identified, 12)  # Assuming 12 interval types
                if interval_achievement.earned and interval_achievement not in newly_earned:
                    newly_earned.append(interval_achievement)
        
        # PsychoacousticWizard
        elif module_id == "psychoacoustic_wizard":
            current_level = game_stats.get('level', 1)
            
            rhythm_achievements = [
                ("rhythm_novice", 3),
                ("rhythm_adept", 7),
                ("rhythm_master", 10)
            ]
            
            for achievement_id, required_level in rhythm_achievements:
                achievement = self.achievements.get(achievement_id)
                if achievement:
                    achievement.set_progress(current_level, required_level)
                    if achievement.earned and achievement not in newly_earned:
                        newly_earned.append(achievement)
        
        # Check time-based achievements
        total_time_hours = self.performance.total_time / 3600  # Convert seconds to hours
        
        if total_time_hours >= 1:
            time_achievement = self.achievements.get("music_enthusiast")
            if time_achievement and not time_achievement.earned:
                time_achievement.earn()
                newly_earned.append(time_achievement)
        
        if total_time_hours >= 5:
            devotee_achievement = self.achievements.get("music_devotee")
            if devotee_achievement and not devotee_achievement.earned:
                devotee_achievement.earn()
                newly_earned.append(devotee_achievement)
        
        # Check combined achievements
        if (self.achievements.get("scale_master") and self.achievements.get("scale_master").earned and
            self.achievements.get("chord_master") and self.achievements.get("chord_master").earned and
            self.achievements.get("interval_master") and self.achievements.get("interval_master").earned):
            
            harmony_achievement = self.achievements.get("harmony_master")
            if harmony_achievement and not harmony_achievement.earned:
                harmony_achievement.earn()
                newly_earned.append(harmony_achievement)
        
        # Update total points
        self.update_points()
        
        # Check for unlocked content
        self.check_unlocks()
        
        return newly_earned
    
    def update_points(self):
        """Update total user points based on earned achievements."""
        self.user_points = sum(a.points for a in self.achievements.values() if a.earned)
        
        # Update level based on points
        # Simple level formula: level = points / 100 + 1, maxed at 10
        self.user_level = min(10, (self.user_points // 100) + 1)
    
    def check_unlocks(self):
        """Check for content unlocks based on points and achievements."""
        # Example unlocks based on points
        if self.user_points >= 50 and "advanced_scales" not in self.unlocked_content:
            self.unlocked_content.add("advanced_scales")
        
        if self.user_points >= 100 and "advanced_chords" not in self.unlocked_content:
            self.unlocked_content.add("advanced_chords")
        
        if self.user_points >= 150 and "jazz_modes" not in self.unlocked_content:
            self.unlocked_content.add("jazz_modes")
        
        # Special unlocks based on specific achievements
        if (self.achievements.get("rhythm_master") and 
            self.achievements.get("rhythm_master").earned and
            "advanced_rhythm_patterns" not in self.unlocked_content):
            self.unlocked_content.add("advanced_rhythm_patterns")
    
    def record_session_stats(self, module_id, stats):
        """
        Record statistics from a training session.
        
        Args:
            module_id: ID of the module
            stats: Dictionary of session statistics
        """
        # Update performance tracker
        self.performance.end_session(module_id, stats.get('score', 0))
        
        # Check for achievement progress
        return self.check_achievement_progress(module_id, stats)
    
    def save(self):
        """Save achievement and performance data to disk."""
        try:
            # Convert achievements to dictionary format
            achievements_data = {
                aid: achievement.to_dict() 
                for aid, achievement in self.achievements.items()
            }
            
            # Prepare full data
            data = {
                'achievements': achievements_data,
                'performance': self.performance.to_dict(),
                'user_points': self.user_points,
                'user_level': self.user_level,
                'unlocked_content': list(self.unlocked_content)
            }
            
            # Save to file
            file_path = self.save_dir / "music_achievements.json"
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.info(f"Saved achievement data to {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving achievement data: {e}")
            return False
    
    def load(self):
        """Load achievement and performance data from disk."""
        try:
            file_path = self.save_dir / "music_achievements.json"
            
            if not file_path.exists():
                logger.info("No achievement data file found, starting fresh")
                return False
            
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            # Load achievements
            achievements_data = data.get('achievements', {})
            for aid, a_data in achievements_data.items():
                if aid in self.achievements:
                    # Update existing achievement
                    achievement = self.achievements[aid]
                    achievement.earned = a_data.get('earned', False)
                    achievement.progress = a_data.get('progress', 0)
                    
                    if a_data.get('earned_date'):
                        try:
                            achievement.earned_date = datetime.fromisoformat(a_data['earned_date'])
                        except (ValueError, TypeError):
                            achievement.earned_date = None
            
            # Load performance data
            if 'performance' in data:
                self.performance = PerformanceTracker.from_dict(data['performance'])
            
            # Load other user data
            self.user_points = data.get('user_points', 0)
            self.user_level = data.get('user_level', 1)
            self.unlocked_content = set(data.get('unlocked_content', []))
            
            logger.info(f"Loaded achievement data from {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error loading achievement data: {e}")
            return False
    
    def get_performance_summary(self):
        """
        Get a summary of user performance.
        
        Returns:
            dict: Dictionary containing performance summary
        """
        # Calculate overall stats
        accuracy = self.performance.get_accuracy()
        total_time_mins = self.performance.total_time / 60
        avg_score = sum(self.performance.scores) / len(self.performance.scores) if self.performance.scores else 0
        max_streak = max(self.performance.streaks) if self.performance.streaks else 0
        
        # Get weak areas
        weak_areas = self.performance.get_weak_areas(3)
        
        # Get spaced repetition items
        spaced_items = self.performance.get_spaced_repetition_items(5)
        
        return {
            'user_level': self.user_level,
            'user_points': self.user_points,
            'total_sessions': self.performance.total_sessions,
            'total_time_mins': total_time_mins,
            'accuracy': accuracy,
            'avg_score': avg_score,
            'max_streak': max_streak,
            'earned_achievements': len([a for a in self.achievements.values() if a.earned]),
            'total_achievements': len(self.achievements),
            'weak_areas': weak_areas,
            'practice_recommendations': spaced_items,
            'unlocked_content': list(self.unlocked_content)
        }


# Simple testing code
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    # Create achievement system
    achievement_system = MusicAchievementSystem()
    
    # Print existing achievements
    print(f"Loaded {len(achievement_system.achievements)} achievements")
    print(f"User level: {achievement_system.user_level}")
    print(f"User points: {achievement_system.user_points}")
    
    # Simulate some activity
    achievement_system.performance.start_session("music_theory")
    achievement_system.performance.record_answer("music_theory", "scale", "major", True)
    achievement_system.performance.record_answer("music_theory", "scale", "minor", True)
    achievement_system.performance.record_answer("music_theory", "chord", "major", False)
    achievement_system.performance.record_streak(2)
    
    # Check for earned achievements
    stats = {
        'score': 80,
        'perfect_round': False,
        'current_streak': 2,
        'max_streak': 2,
        'unique_scales_identified': 2
    }
    
    newly_earned = achievement_system.record_session_stats("music_theory", stats)
    
    if newly_earned:
        print("\nNewly earned achievements:")
        for achievement in newly_earned:
            print(f"- {achievement.name}: {achievement.description}")
    
    # Print performance summary
    summary = achievement_system.get_performance_summary()
    print("\nPerformance Summary:")
    for key, value in summary.items():
        print(f"{key}: {value}")
    
    print("\nAchievements module successfully loaded!") 