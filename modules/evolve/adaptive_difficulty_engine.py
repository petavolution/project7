#!/usr/bin/env python3
"""
Adaptive Difficulty Engine for MetaMindIQTrain modules

This module provides a dynamic difficulty adjustment system that analyzes
user performance metrics and adjusts task complexity accordingly. It enables
cognitive training modules to deliver an optimal challenge level tailored
to individual user capabilities.

Key features:
1. Real-time performance analysis
2. Multi-factor adjustment criteria
3. Progressive difficulty scaling
4. Performance history tracking
5. Weighted metric evaluation
"""

from typing import Dict, List, Any, Tuple, Optional, Union, Set
import math
import time

class AdaptiveDifficultyEngine:
    """Engine for dynamically adjusting task complexity based on user performance metrics.
    
    This class provides a sophisticated algorithm for analyzing performance data
    such as accuracy, reaction time, and completion rate to determine the optimal
    difficulty level for a cognitive training task. It maintains a performance
    history to smooth adjustments and prevent rapid oscillations in difficulty.
    """

    def __init__(self):
        """Initialize the adaptive difficulty engine with default parameters."""
        # Core difficulty settings
        self.current_level = 1
        self.min_level = 1
        self.max_level = 10
        
        # Target performance parameters
        self.target_accuracy = 0.75  # Target accuracy (75%)
        self.target_reaction_time = 1.0  # Target reaction time in seconds
        self.target_completion_rate = 0.8  # Target task completion rate (80%)
        
        # Weight factors for different metrics
        self.accuracy_weight = 0.5   # Weight for accuracy in calculation
        self.speed_weight = 0.3      # Weight for reaction time in calculation
        self.completion_weight = 0.2  # Weight for completion rate
        
        # Thresholds for different difficulty changes
        self.large_increase_threshold = 0.9  # Accuracy above 90% -> increase by 2
        self.increase_threshold = 0.8        # Accuracy above 80% -> increase by 1
        self.decrease_threshold = 0.6        # Accuracy below 60% -> decrease by 1
        self.large_decrease_threshold = 0.4  # Accuracy below 40% -> decrease by 2
        
        # Performance history for smoothing
        self.performance_history = []
        self.history_max_size = 5  # Keep track of last 5 performance metrics
        
        # Timing values
        self.last_adjustment_time = time.time()
        self.min_adjustment_interval = 10.0  # Minimum seconds between adjustments

    def analyze_performance_metrics(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze user performance metrics to determine appropriate difficulty adjustment.
        
        Args:
            metrics: Dictionary containing performance metrics like accuracy and reaction time
            
        Returns:
            Dictionary with analysis results including recommended difficulty change
        """
        # Extract key metrics with defaults if not present
        correct = metrics.get("correct_selections", 0)
        incorrect = metrics.get("incorrect_selections", 0)
        total = correct + incorrect
        
        # Calculate accuracy
        accuracy = correct / total if total > 0 else 0.0
        
        # Calculate reaction time score (lower is better)
        avg_reaction_time = metrics.get("average_reaction_time", 0.0)
        reaction_time_score = 1.0
        if avg_reaction_time > 0:
            # Convert reaction time to a score between 0 and 1
            # Assuming 2000ms (2s) as the upper bound for slow reactions
            # and 500ms (0.5s) as the lower bound for fast reactions
            normalized_rt = max(0, min(1, (2000 - avg_reaction_time * 1000) / 1500))
            reaction_time_score = normalized_rt
        
        # Calculate completion rate
        targets_found = metrics.get("total_targets_found", 0)
        targets_total = targets_found + metrics.get("targets_missed", 0)
        completion_rate = targets_found / targets_total if targets_total > 0 else 0.0
        
        # Calculate overall performance score
        performance_score = (
            accuracy * self.accuracy_weight +
            reaction_time_score * self.speed_weight +
            completion_rate * self.completion_weight
        )
        
        return {
            "accuracy": accuracy,
            "reaction_time_score": reaction_time_score,
            "completion_rate": completion_rate,
            "performance_score": performance_score,
            "difficulty_change": self._calculate_difficulty_change(accuracy, performance_score, completion_rate)
        }

    def _calculate_difficulty_change(self, accuracy: float, performance_score: float, 
                                    completion_rate: float = 0.0) -> int:
        """Calculate the recommended difficulty level change based on performance metrics.
        
        Args:
            accuracy: User's current accuracy rate (0.0 to 1.0)
            performance_score: Overall performance score (0.0 to 1.0)
            completion_rate: Task completion rate (0.0 to 1.0)
            
        Returns:
            Integer representing the recommended difficulty change (-2 to +2)
        """
        # Check if accuracy is significantly off target
        if accuracy >= self.large_increase_threshold and completion_rate > self.target_completion_rate:
            return 2  # Large increase in difficulty
        elif accuracy >= self.increase_threshold and completion_rate >= self.target_completion_rate * 0.9:
            return 1  # Small increase in difficulty
        elif accuracy <= self.large_decrease_threshold or completion_rate < self.target_completion_rate * 0.5:
            return -2  # Large decrease in difficulty
        elif accuracy <= self.decrease_threshold or completion_rate < self.target_completion_rate * 0.7:
            return -1  # Small decrease in difficulty
        
        # If accuracy is within acceptable range, check overall performance
        if 0.65 <= accuracy <= 0.85:
            if performance_score >= 0.8:
                return 1  # Small increase based on good overall performance
            elif performance_score <= 0.4:
                return -1  # Small decrease based on poor overall performance
                
        return 0  # No change needed

    def adjust_task_complexity(self, level: int) -> Dict[str, Any]:
        """Calculate task complexity parameters for a given difficulty level.
        
        Args:
            level: Difficulty level (1-10)
            
        Returns:
            Dictionary with complexity parameters for the specified level
        """
        # Clamp level to valid range
        level = max(self.min_level, min(self.max_level, level))
        
        # Calculate parameters for the given level
        transformation_speed = 0.5 + (level * 0.1)  # Speed increases with level
        complexity = max(1, level // 2)  # Number of transformations at once
        distractor_diversity = min(5, level // 3 + 1)  # Variety of shapes up to 5
        target_count = min(10, 2 + (level // 2))  # Number of targets to find
        grid_size = min(7, 4 + (level // 3))  # Grid size increases with difficulty
        
        return {
            "level": level,
            "transformation_speed": transformation_speed,
            "complexity": complexity,
            "distractor_diversity": distractor_diversity,
            "target_count": target_count,
            "grid_size": grid_size
        }

    def update_difficulty_level(self, performance_data: Dict[str, Any]) -> int:
        """Update the difficulty level based on performance data.
        
        Args:
            performance_data: Dictionary containing performance metrics
            
        Returns:
            Updated difficulty level
        """
        # Check if enough time has passed since last adjustment
        current_time = time.time()
        if current_time - self.last_adjustment_time < self.min_adjustment_interval:
            return self.current_level
            
        # Add performance data to history
        analysis = self.analyze_performance_metrics(performance_data)
        self.performance_history.append(analysis)
        
        # Trim history if needed
        if len(self.performance_history) > self.history_max_size:
            self.performance_history.pop(0)
        
        # Calculate average difficulty change based on recent performance
        if not self.performance_history:
            return self.current_level
            
        # Weight recent performance more heavily
        total_weight = 0
        weighted_change = 0
        
        for i, perf in enumerate(self.performance_history):
            # More recent entries have higher weight
            weight = (i + 1) / sum(range(1, len(self.performance_history) + 1))
            weighted_change += perf["difficulty_change"] * weight
            total_weight += weight
        
        # Calculate weighted average change
        avg_change = weighted_change / total_weight if total_weight > 0 else 0
        
        # Round to nearest integer (can be negative)
        change = round(avg_change)
        
        # Update current level
        new_level = max(self.min_level, min(self.max_level, self.current_level + change))
        self.current_level = new_level
        
        # Record adjustment time
        self.last_adjustment_time = current_time
        
        return new_level
        
    def compute_difficulty_adjustment(self, accuracy: float, avg_reaction_time: float, 
                                      targets_per_minute: float) -> int:
        """Compute a difficulty adjustment based on direct performance metrics.
        
        This is a simplified interface for modules to get a quick difficulty
        adjustment without needing to track full performance history.
        
        Args:
            accuracy: User's accuracy rate (0.0 to 1.0)
            avg_reaction_time: Average reaction time in seconds
            targets_per_minute: Rate of target identification
            
        Returns:
            Integer representing the recommended difficulty change (-2 to +2)
        """
        # Check if enough time has passed since last adjustment
        current_time = time.time()
        if current_time - self.last_adjustment_time < self.min_adjustment_interval:
            return 0
            
        # Convert reaction time to score (faster is better)
        rt_score = max(0.0, min(1.0, (3.0 - avg_reaction_time) / 2.5)) if avg_reaction_time > 0 else 0.5
        
        # Convert targets per minute to completion rate score
        # Assuming 20 targets per minute is excellent, 5 is minimum acceptable
        completion_score = min(1.0, targets_per_minute / 20.0) if targets_per_minute > 0 else 0.0
        
        # Synthesize metrics into format for analysis
        metrics = {
            "correct_selections": int(100 * accuracy) if accuracy > 0 else 0,
            "incorrect_selections": int(100 * (1 - accuracy)) if accuracy > 0 else 0,
            "average_reaction_time": avg_reaction_time,
            "total_targets_found": int(targets_per_minute),
            "targets_missed": max(0, 20 - int(targets_per_minute))
        }
        
        # Get analysis
        analysis = self.analyze_performance_metrics(metrics)
        
        # Record adjustment time
        self.last_adjustment_time = current_time
        
        return analysis["difficulty_change"] 