#!/usr/bin/env python3
"""
Adaptive Training System

This module implements an advanced adaptive difficulty system that analyzes user performance
across all training modules to create personalized cognitive development paths. It uses
machine learning techniques to identify cognitive strengths and weaknesses, then tailors
training parameters to maximize neuroplasticity and skill development.
"""

import logging
import numpy as np
from typing import Dict, Any, List, Optional
import json
import time
from collections import defaultdict

logger = logging.getLogger(__name__)

class CognitiveProfile:
    """User cognitive profile with strengths, weaknesses, and development trajectory."""
    
    def __init__(self, user_id: str):
        """Initialize a cognitive profile.
        
        Args:
            user_id: Unique identifier for the user
        """
        self.user_id = user_id
        self.domain_scores = {
            "working_memory": 0.5,
            "pattern_recognition": 0.5,
            "cognitive_flexibility": 0.5,
            "processing_speed": 0.5,
            "peripheral_vision": 0.5,
            "synesthetic_ability": 0.5,
            "quantum_thinking": 0.5,
            "neural_integration": 0.5
        }
        self.domain_improvement_rates = defaultdict(list)
        self.created_at = time.time()
        self.last_updated = time.time()
        self.total_training_time = 0
        self.module_preferences = {}
        self.recommended_modules = []
        
    def update_domain_score(self, domain: str, score: float) -> None:
        """Update the score for a cognitive domain.
        
        Args:
            domain: The cognitive domain to update
            score: The new score (0.0 to 1.0)
        """
        if domain in self.domain_scores:
            old_score = self.domain_scores[domain]
            
            # Record improvement rate (can be negative)
            improvement = score - old_score
            self.domain_improvement_rates[domain].append((time.time(), improvement))
            
            # Update score with slight smoothing to avoid wild fluctuations
            self.domain_scores[domain] = old_score * 0.3 + score * 0.7
            
            # Cap at valid range
            self.domain_scores[domain] = max(0.0, min(1.0, self.domain_scores[domain]))
            
        else:
            # New domain
            self.domain_scores[domain] = score
            
        self.last_updated = time.time()
        
    def get_cognitive_fingerprint(self) -> List[float]:
        """Get a normalized vector representing the cognitive profile.
        
        Returns:
            Normalized vector of cognitive domain scores
        """
        values = list(self.domain_scores.values())
        norm = np.linalg.norm(values)
        if norm > 0:
            return [v / norm for v in values]
        return values
        
    def get_weakest_domains(self, limit: int = 3) -> List[str]:
        """Get the weakest cognitive domains.
        
        Args:
            limit: Maximum number of domains to return
            
        Returns:
            List of domain names, ordered from weakest to strongest
        """
        return [domain for domain, _ in 
                sorted(self.domain_scores.items(), key=lambda x: x[1])[:limit]]
                
    def get_strongest_domains(self, limit: int = 3) -> List[str]:
        """Get the strongest cognitive domains.
        
        Args:
            limit: Maximum number of domains to return
            
        Returns:
            List of domain names, ordered from strongest to weakest
        """
        return [domain for domain, _ in 
                sorted(self.domain_scores.items(), key=lambda x: x[1], reverse=True)[:limit]]

    def serialize(self) -> Dict[str, Any]:
        """Serialize the cognitive profile to a dictionary.
        
        Returns:
            Dictionary representation of the profile
        """
        return {
            "user_id": self.user_id,
            "domain_scores": self.domain_scores,
            "created_at": self.created_at,
            "last_updated": self.last_updated,
            "total_training_time": self.total_training_time,
            "module_preferences": self.module_preferences,
            "recommended_modules": self.recommended_modules
        }
        
    @classmethod
    def deserialize(cls, data: Dict[str, Any]) -> 'CognitiveProfile':
        """Create a cognitive profile from a dictionary.
        
        Args:
            data: Dictionary containing profile data
            
        Returns:
            Instantiated cognitive profile
        """
        profile = cls(data["user_id"])
        profile.domain_scores = data["domain_scores"]
        profile.created_at = data.get("created_at", time.time())
        profile.last_updated = data.get("last_updated", time.time())
        profile.total_training_time = data.get("total_training_time", 0)
        profile.module_preferences = data.get("module_preferences", {})
        profile.recommended_modules = data.get("recommended_modules", [])
        return profile


class AdaptiveSystem:
    """Advanced adaptive system for personalizing cognitive training."""
    
    def __init__(self):
        """Initialize the adaptive system."""
        self.profiles = {}
        self.module_domain_map = {
            "symbol_memory": ["working_memory", "pattern_recognition"],
            "expand_vision": ["peripheral_vision", "processing_speed"],
            "morph_matrix": ["pattern_recognition", "cognitive_flexibility"],
            "neural_flow": ["neural_integration", "processing_speed"],
            "quantum_memory": ["quantum_thinking", "working_memory", "cognitive_flexibility"],
            "synesthetic_training": ["synesthetic_ability", "cognitive_flexibility"]
        }
        logger.info("Adaptive system initialized")
        
    def get_profile(self, user_id: str) -> CognitiveProfile:
        """Get a user's cognitive profile, creating it if it doesn't exist.
        
        Args:
            user_id: The user ID
            
        Returns:
            The user's cognitive profile
        """
        if user_id not in self.profiles:
            self.profiles[user_id] = CognitiveProfile(user_id)
            logger.info(f"Created new cognitive profile for user {user_id}")
            
        return self.profiles[user_id]
        
    def process_module_results(self, user_id: str, module_id: str, 
                              results: Dict[str, Any]) -> None:
        """Process results from a training module and update the user's profile.
        
        Args:
            user_id: The user ID
            module_id: The module ID
            results: Dictionary containing performance results
        """
        profile = self.get_profile(user_id)
        
        # Update training time
        profile.total_training_time += results.get("duration", 0)
        
        # Update module preferences
        if module_id not in profile.module_preferences:
            profile.module_preferences[module_id] = 0
        profile.module_preferences[module_id] += 1
        
        # Calculate normalized score from results (0.0 to 1.0)
        normalized_score = self._calculate_normalized_score(results)
        
        # Update all cognitive domains associated with this module
        if module_id in self.module_domain_map:
            for domain in self.module_domain_map[module_id]:
                domain_weight = 1.0 / len(self.module_domain_map[module_id])
                domain_score = normalized_score * domain_weight
                profile.update_domain_score(domain, domain_score)
                
        logger.debug(f"Updated cognitive profile for user {user_id} based on {module_id} results")
        
    def generate_training_recommendations(self, user_id: str, count: int = 3) -> List[str]:
        """Generate personalized module recommendations.
        
        Args:
            user_id: The user ID
            count: Number of recommendations to generate
            
        Returns:
            List of recommended module IDs
        """
        profile = self.get_profile(user_id)
        
        # Get weakest domains that need the most improvement
        weak_domains = profile.get_weakest_domains()
        
        # Get modules that train those domains
        recommended_modules = []
        for domain in weak_domains:
            for module_id, domains in self.module_domain_map.items():
                if domain in domains and module_id not in recommended_modules:
                    recommended_modules.append(module_id)
                    if len(recommended_modules) >= count:
                        break
            if len(recommended_modules) >= count:
                break
                
        # If we need more recommendations, add most effective modules based on improvement rates
        if len(recommended_modules) < count:
            # Sort modules by effectiveness (improvement per time spent)
            # This would require more sophisticated analysis of historical data
            all_modules = list(self.module_domain_map.keys())
            remaining_modules = [m for m in all_modules if m not in recommended_modules]
            recommended_modules.extend(remaining_modules[:count - len(recommended_modules)])
            
        # Update profile with recommendations
        profile.recommended_modules = recommended_modules
        
        return recommended_modules
        
    def generate_adaptive_parameters(self, user_id: str, module_id: str) -> Dict[str, Any]:
        """Generate adaptive parameters for a training module.
        
        Args:
            user_id: The user ID
            module_id: The module ID
            
        Returns:
            Dictionary of parameter adjustments
        """
        profile = self.get_profile(user_id)
        
        # Get relevant domain scores for this module
        relevant_domains = self.module_domain_map.get(module_id, [])
        if not relevant_domains:
            return {}
            
        domain_scores = [profile.domain_scores[domain] for domain in relevant_domains 
                        if domain in profile.domain_scores]
        
        if not domain_scores:
            return {}
            
        # Calculate average domain score as the basis for adaptations
        avg_score = sum(domain_scores) / len(domain_scores)
        
        # Generate module-specific adaptations
        params = self._generate_module_specific_adaptations(module_id, avg_score)
        
        logger.debug(f"Generated adaptive parameters for user {user_id}, module {module_id}")
        
        return params
        
    def _calculate_normalized_score(self, results: Dict[str, Any]) -> float:
        """Calculate a normalized score from module results.
        
        Args:
            results: Dictionary containing performance results
            
        Returns:
            Normalized score between 0.0 and 1.0
        """
        # Extract relevant metrics
        score = results.get("score", 0)
        max_score = results.get("max_score", 100)
        accuracy = results.get("accuracy", 0.0)
        completion_rate = results.get("completion_rate", 0.0)
        level_reached = results.get("level", 1)
        
        # Calculate normalized score components
        score_component = min(1.0, score / max_score) if max_score > 0 else 0.0
        accuracy_component = min(1.0, accuracy)
        completion_component = min(1.0, completion_rate)
        level_component = min(1.0, level_reached / 10.0)  # Assume level 10 is "mastery"
        
        # Weighted combination
        normalized_score = (
            score_component * 0.4 +
            accuracy_component * 0.3 +
            completion_component * 0.1 +
            level_component * 0.2
        )
        
        return normalized_score
        
    def _generate_module_specific_adaptations(self, module_id: str, avg_score: float) -> Dict[str, Any]:
        """Generate module-specific parameter adaptations.
        
        Args:
            module_id: The module ID
            avg_score: Average domain score (0.0 to 1.0)
            
        Returns:
            Dictionary of parameter adjustments
        """
        # Base difficulty is inverse of score (lower score = easier settings)
        # but we ensure it's not too easy or too hard
        base_difficulty = 0.2 + (avg_score * 0.6)  # Range: 0.2 to 0.8
        
        # Common parameters
        params = {
            "difficulty_factor": base_difficulty,
            "adaptive_timing": True,
            "challenge_rate": 0.5 + (avg_score * 0.5),  # Higher score = faster progression
        }
        
        # Module-specific parameters
        if module_id == "symbol_memory":
            return {
                **params,
                "grid_size": max(3, min(8, int(3 + (avg_score * 5)))),
                "symbol_complexity": max(1, min(3, int(1 + (avg_score * 2.5)))),
                "memory_duration": max(500, int(2000 - (avg_score * 1000))),
            }
        elif module_id == "expand_vision":
            return {
                **params,
                "distance_factor": 0.15 + (avg_score * 0.35),
                "number_range": max(10, int(10 + (avg_score * 40))),
                "display_duration": max(500, int(2000 - (avg_score * 1300))),
            }
        elif module_id == "morph_matrix":
            return {
                **params,
                "matrix_size": max(3, min(8, int(3 + (avg_score * 5)))),
                "transform_count": max(1, min(5, int(1 + (avg_score * 4)))),
                "pattern_complexity": max(1, min(3, int(1 + (avg_score * 2)))),
            }
        elif module_id == "neural_flow":
            return {
                **params,
                "node_count": max(5, min(25, int(5 + (avg_score * 20)))),
                "connection_density": 0.2 + (avg_score * 0.5),
                "pulse_speed": 0.5 + (avg_score * 1.5),
            }
        elif module_id == "quantum_memory":
            return {
                **params,
                "quantum_states": max(3, min(8, int(3 + (avg_score * 5)))),
                "entanglement_factor": 0.1 + (avg_score * 0.5),
                "superposition_count": max(2, min(4, int(2 + (avg_score * 2)))),
            }
        elif module_id == "synesthetic_training":
            return {
                **params,
                "association_count": max(3, min(12, int(3 + (avg_score * 9)))),
                "sense_modalities": max(2, min(5, int(2 + (avg_score * 3)))),
                "recall_time": max(5, int(15 - (avg_score * 8))),
            }
        
        return params 