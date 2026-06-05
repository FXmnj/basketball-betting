"""
Poisson Goal Model for Football Match Prediction
Estimates expected goals using team attack/defense strengths and league averages
"""
import math
from typing import Dict, List, Tuple
from dataclasses import dataclass


@dataclass
class PoissonResult:
    expected_home_goals: float
    expected_away_goals: float
    home_win_prob: float
    draw_prob: float
    away_win_prob: float
    score_probabilities: List[Dict]
    goal_probabilities: Dict[str, Dict[int, float]]


class PoissonGoalModel:
    """
    Poisson distribution model for predicting football match outcomes.
    
    Formula:
    λ_home = league_avg_home_goals × home_attack_strength × away_defense_weakness
    λ_away = league_avg_away_goals × away_attack_strength × home_defense_weakness
    """
    
    def __init__(self, max_goals: int = 8):
        self.max_goals = max_goals
    
    @staticmethod
    def poisson_probability(lambda_val: float, k: int) -> float:
        """Calculate Poisson probability P(X = k) given lambda"""
        if lambda_val <= 0:
            return 1.0 if k == 0 else 0.0
        return (math.exp(-lambda_val) * (lambda_val ** k)) / math.factorial(k)
    
    def calculate_expected_goals(
        self,
        home_attack: float,
        home_defense: float,
        away_attack: float,
        away_defense: float,
        league_avg_home_goals: float = 1.5,
        league_avg_away_goals: float = 1.2,
        home_advantage: float = 1.1
    ) -> Tuple[float, float]:
        """
        Calculate expected goals for home and away teams.
        
        Args:
            home_attack: Home team's attacking strength (>1 = above average)
            home_defense: Home team's defensive strength (<1 = stronger defense)
            away_attack: Away team's attacking strength
            away_defense: Away team's defensive strength
            league_avg_home_goals: League average goals for home teams
            league_avg_away_goals: League average goals for away teams
            home_advantage: Home field advantage multiplier
        
        Returns:
            Tuple of (expected_home_goals, expected_away_goals)
        """
        # Expected home goals
        lambda_home = (
            league_avg_home_goals * 
            home_attack * 
            away_defense * 
            home_advantage
        )
        
        # Expected away goals
        lambda_away = (
            league_avg_away_goals * 
            away_attack * 
            home_defense
        )
        
        # Cap expected goals at reasonable limits
        lambda_home = min(max(lambda_home, 0.1), 5.0)
        lambda_away = min(max(lambda_away, 0.1), 5.0)
        
        return lambda_home, lambda_away
    
    def calculate_goal_probabilities(
        self,
        lambda_home: float,
        lambda_away: float
    ) -> Dict[str, Dict[int, float]]:
        """Calculate probability distribution for each team's goals"""
        home_probs = {}
        away_probs = {}
        
        for goals in range(self.max_goals + 1):
            home_probs[goals] = self.poisson_probability(lambda_home, goals)
            away_probs[goals] = self.poisson_probability(lambda_away, goals)
        
        return {"home": home_probs, "away": away_probs}
    
    def calculate_match_outcome_probabilities(
        self,
        goal_probs: Dict[str, Dict[int, float]]
    ) -> Tuple[float, float, float]:
        """Calculate home win, draw, and away win probabilities"""
        home_win_prob = 0.0
        draw_prob = 0.0
        away_win_prob = 0.0
        
        for home_goals in range(self.max_goals + 1):
            for away_goals in range(self.max_goals + 1):
                prob = goal_probs["home"][home_goals] * goal_probs["away"][away_goals]
                
                if home_goals > away_goals:
                    home_win_prob += prob
                elif home_goals == away_goals:
                    draw_prob += prob
                else:
                    away_win_prob += prob
        
        # Normalize probabilities
        total = home_win_prob + draw_prob + away_win_prob
        if total > 0:
            home_win_prob /= total
            draw_prob /= total
            away_win_prob /= total
        
        return home_win_prob, draw_prob, away_win_prob
    
    def calculate_score_probabilities(
        self,
        goal_probs: Dict[str, Dict[int, float]],
        top_n: int = 20
    ) -> List[Dict]:
        """Calculate probabilities for specific scorelines"""
        score_probs = []
        
        for home_goals in range(self.max_goals + 1):
            for away_goals in range(self.max_goals + 1):
                prob = goal_probs["home"][home_goals] * goal_probs["away"][away_goals]
                score_probs.append({
                    "score": f"{home_goals}-{away_goals}",
                    "home_goals": home_goals,
                    "away_goals": away_goals,
                    "probability": round(prob * 100, 2)
                })
        
        # Sort by probability and return top N
        score_probs.sort(key=lambda x: x["probability"], reverse=True)
        return score_probs[:top_n]
    
    def calculate_over_under_probabilities(
        self,
        goal_probs: Dict[str, Dict[int, float]]
    ) -> Dict[str, float]:
        """Calculate over/under probabilities for various goal lines"""
        results = {}
        
        for line in [0.5, 1.5, 2.5, 3.5, 4.5]:
            over_prob = 0.0
            
            for home_goals in range(self.max_goals + 1):
                for away_goals in range(self.max_goals + 1):
                    total = home_goals + away_goals
                    prob = goal_probs["home"][home_goals] * goal_probs["away"][away_goals]
                    
                    if total > line:
                        over_prob += prob
            
            results[f"over_{str(line).replace('.', '')}"] = round(over_prob * 100, 2)
            results[f"under_{str(line).replace('.', '')}"] = round((1 - over_prob) * 100, 2)
        
        return results
    
    def calculate_btts_probability(
        self,
        goal_probs: Dict[str, Dict[int, float]]
    ) -> float:
        """Calculate Both Teams To Score probability"""
        btts_prob = 0.0
        
        for home_goals in range(1, self.max_goals + 1):
            for away_goals in range(1, self.max_goals + 1):
                btts_prob += goal_probs["home"][home_goals] * goal_probs["away"][away_goals]
        
        return round(btts_prob * 100, 2)
    
    def predict(
        self,
        home_attack: float,
        home_defense: float,
        away_attack: float,
        away_defense: float,
        league_avg_home_goals: float = 1.5,
        league_avg_away_goals: float = 1.2,
        home_advantage: float = 1.1
    ) -> PoissonResult:
        """
        Full Poisson prediction for a match.
        
        Returns comprehensive prediction including:
        - Expected goals
        - Match outcome probabilities
        - Score probabilities
        - Goal distribution
        """
        # Calculate expected goals
        lambda_home, lambda_away = self.calculate_expected_goals(
            home_attack, home_defense,
            away_attack, away_defense,
            league_avg_home_goals, league_avg_away_goals,
            home_advantage
        )
        
        # Calculate goal probabilities
        goal_probs = self.calculate_goal_probabilities(lambda_home, lambda_away)
        
        # Calculate match outcomes
        home_win, draw, away_win = self.calculate_match_outcome_probabilities(goal_probs)
        
        # Calculate score probabilities
        score_probs = self.calculate_score_probabilities(goal_probs)
        
        return PoissonResult(
            expected_home_goals=round(lambda_home, 2),
            expected_away_goals=round(lambda_away, 2),
            home_win_prob=round(home_win * 100, 2),
            draw_prob=round(draw * 100, 2),
            away_win_prob=round(away_win * 100, 2),
            score_probabilities=score_probs,
            goal_probabilities=goal_probs
        )
