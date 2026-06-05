"""
Expected Goals (xG) Model
Estimates shot quality and team expected goals based on shot characteristics
"""
import math
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import random


@dataclass
class ShotData:
    distance: float  # meters from goal
    angle: float  # degrees
    body_part: str  # "foot", "head", "other"
    assist_type: str  # "through_ball", "cross", "set_piece", "none"
    is_big_chance: bool
    defensive_pressure: float  # 0-1 scale
    goalkeeper_position: str  # "central", "advanced", "out_of_position"


@dataclass
class XGResult:
    shot_xg: float
    cumulative_xg: float
    shot_count: int
    on_target_xg: float


class ExpectedGoalsModel:
    """
    Expected Goals model using logistic regression principles.
    
    xG = P(goal | shot characteristics)
    
    Based on historical shot data analysis.
    """
    
    def __init__(self):
        # Base xG coefficients (simplified model)
        self.base_xg = 0.1  # Base probability
        
        # Distance decay factor
        self.distance_coef = -0.05
        
        # Angle factor (wider angle = higher xG)
        self.angle_coef = 0.02
        
        # Body part factors
        self.body_part_factors = {
            "foot": 1.0,
            "head": 0.85,
            "other": 0.5
        }
        
        # Assist type factors
        self.assist_factors = {
            "through_ball": 1.3,
            "cross": 0.9,
            "set_piece": 1.1,
            "corner": 0.95,
            "free_kick": 1.2,
            "penalty": 7.6,  # ~76% conversion rate
            "none": 1.0
        }
        
        # Defensive pressure reduction
        self.pressure_factor = -0.3
        
        # Goalkeeper position factors
        self.gk_factors = {
            "central": 1.0,
            "advanced": 0.85,
            "out_of_position": 1.5
        }
    
    def calculate_shot_xg(self, shot: ShotData) -> float:
        """
        Calculate xG for a single shot using logistic model.
        """
        # Base xG adjusted for distance
        # xG decreases exponentially with distance
        distance_factor = math.exp(self.distance_coef * shot.distance)
        
        # Angle factor (wider angles = higher xG)
        angle_factor = min(1.5, max(0.3, shot.angle / 45.0))
        
        # Get multiplicative factors
        body_part_factor = self.body_part_factors.get(shot.body_part, 1.0)
        assist_factor = self.assist_factors.get(shot.assist_type, 1.0)
        gk_factor = self.gk_factors.get(shot.goalkeeper_position, 1.0)
        
        # Big chance bonus
        big_chance_factor = 1.8 if shot.is_big_chance else 1.0
        
        # Defensive pressure penalty
        pressure_factor = 1.0 + (self.pressure_factor * shot.defensive_pressure)
        
        # Calculate final xG
        xg = (
            self.base_xg *
            distance_factor *
            angle_factor *
            body_part_factor *
            assist_factor *
            gk_factor *
            big_chance_factor *
            pressure_factor
        )
        
        # Ensure xG is in valid range
        return min(0.99, max(0.01, xg))
    
    def calculate_match_xg(
        self,
        home_shots: List[ShotData],
        away_shots: List[ShotData]
    ) -> Tuple[XGResult, XGResult]:
        """
        Calculate cumulative xG for both teams from their shots.
        """
        home_xg = 0.0
        away_xg = 0.0
        home_on_target_xg = 0.0
        away_on_target_xg = 0.0
        
        for shot in home_shots:
            shot_xg = self.calculate_shot_xg(shot)
            home_xg += shot_xg
            if shot.is_big_chance or shot_xg > 0.15:
                home_on_target_xg += shot_xg
        
        for shot in away_shots:
            shot_xg = self.calculate_shot_xg(shot)
            away_xg += shot_xg
            if shot.is_big_chance or shot_xg > 0.15:
                away_on_target_xg += shot_xg
        
        return (
            XGResult(
                shot_xg=home_xg / len(home_shots) if home_shots else 0,
                cumulative_xg=home_xg,
                shot_count=len(home_shots),
                on_target_xg=home_on_target_xg
            ),
            XGResult(
                shot_xg=away_xg / len(away_shots) if away_shots else 0,
                cumulative_xg=away_xg,
                shot_count=len(away_shots),
                on_target_xg=away_on_target_xg
            )
        )
    
    def estimate_team_xg(
        self,
        attack_strength: float,
        opponent_defense: float,
        is_home: bool,
        league_avg_shots: float = 12.0,
        league_avg_xg: float = 1.3
    ) -> float:
        """
        Estimate team xG based on strength ratings.
        Used when shot data is not available.
        """
        home_factor = 1.1 if is_home else 0.9
        
        # Expected shots
        expected_shots = league_avg_shots * attack_strength * home_factor
        
        # xG per shot based on defense quality
        xg_per_shot = (league_avg_xg / league_avg_shots) * (1.0 / opponent_defense)
        
        # Calculate total xG
        total_xg = expected_shots * xg_per_shot
        
        return round(max(0.1, min(5.0, total_xg)), 2)
    
    def generate_simulated_shots(
        self,
        team_attack: float,
        opponent_defense: float,
        expected_shots: int = 12
    ) -> List[ShotData]:
        """
        Generate simulated shot data for Monte Carlo simulations.
        """
        shots = []
        quality_factor = team_attack / opponent_defense
        
        for _ in range(expected_shots):
            # Generate shot characteristics based on team quality
            distance = max(5, 35 - (quality_factor * 5) + random.gauss(0, 8))
            angle = min(90, max(10, 45 + random.gauss(0, 15)))
            
            # Body part distribution
            body_parts = ["foot", "foot", "foot", "head", "other"]
            body_part = random.choice(body_parts)
            
            # Assist type distribution
            assist_types = ["through_ball", "cross", "set_piece", "none", "none"]
            assist_type = random.choice(assist_types)
            
            # Big chance probability based on team quality
            is_big_chance = random.random() < (0.15 * quality_factor)
            
            # Defensive pressure
            pressure = random.uniform(0.2, 0.8)
            
            # GK position
            gk_positions = ["central", "central", "advanced", "out_of_position"]
            gk_pos = random.choice(gk_positions)
            
            shots.append(ShotData(
                distance=distance,
                angle=angle,
                body_part=body_part,
                assist_type=assist_type,
                is_big_chance=is_big_chance,
                defensive_pressure=pressure,
                goalkeeper_position=gk_pos
            ))
        
        return shots
    
    def xg_to_goals_probability(
        self,
        xg: float,
        max_goals: int = 6
    ) -> Dict[int, float]:
        """
        Convert xG to goal probability distribution using Poisson.
        """
        probs = {}
        for goals in range(max_goals + 1):
            probs[goals] = (math.exp(-xg) * (xg ** goals)) / math.factorial(goals)
        return probs
    
    def calculate_team_xg_stats(
        self,
        matches_data: List[Dict]
    ) -> Dict[str, float]:
        """
        Calculate aggregated xG statistics for a team.
        
        Args:
            matches_data: List of match data with xG values
            
        Returns:
            Dictionary with xG for, xG against, xG difference, etc.
        """
        xg_for = []
        xg_against = []
        
        for match in matches_data:
            xg_for.append(match.get("xg_for", 0))
            xg_against.append(match.get("xg_against", 0))
        
        if not xg_for:
            return {
                "avg_xg_for": 0,
                "avg_xg_against": 0,
                "xg_difference": 0,
                "xg_per_shot": 0
            }
        
        avg_xg_for = sum(xg_for) / len(xg_for)
        avg_xg_against = sum(xg_against) / len(xg_against)
        
        return {
            "avg_xg_for": round(avg_xg_for, 2),
            "avg_xg_against": round(avg_xg_against, 2),
            "xg_difference": round(avg_xg_for - avg_xg_against, 2),
            "total_xg_for": round(sum(xg_for), 2),
            "total_xg_against": round(sum(xg_against), 2)
        }
