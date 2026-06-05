"""
Monte Carlo Simulation for Match Prediction
Simulates matches 10,000 times to compute final probabilities
"""
import random
import math
from typing import Dict, List, Tuple
from dataclasses import dataclass
from collections import Counter


@dataclass
class SimulationResult:
    home_win_prob: float
    draw_prob: float
    away_win_prob: float
    avg_home_goals: float
    avg_away_goals: float
    avg_total_goals: float
    over_probabilities: Dict[str, float]
    btts_prob: float
    score_distribution: List[Dict]
    simulations_run: int
    confidence_interval: Dict[str, Tuple[float, float]]


class MonteCarloSimulator:
    """
    Monte Carlo simulation engine for football match predictions.
    
    Runs 10,000 simulations per match to generate robust
    probability distributions.
    """
    
    def __init__(self, default_simulations: int = 10000):
        self.default_simulations = default_simulations
        self.random_seed = None
    
    def set_seed(self, seed: int):
        """Set random seed for reproducibility"""
        self.random_seed = seed
        random.seed(seed)
    
    def simulate_goals(
        self,
        expected_goals: float,
        variance_factor: float = 1.0
    ) -> int:
        """
        Simulate number of goals using Poisson distribution.
        
        Args:
            expected_goals: Lambda parameter for Poisson
            variance_factor: Adjusts variance for more/less predictable teams
        """
        # Add some variance to expected goals
        adjusted_xg = max(0.1, expected_goals * (1 + random.gauss(0, 0.1 * variance_factor)))
        
        # Poisson simulation
        L = math.exp(-adjusted_xg)
        k = 0
        p = 1.0
        
        while p > L:
            k += 1
            p *= random.random()
        
        return k - 1
    
    def simulate_single_match(
        self,
        home_xg: float,
        away_xg: float,
        home_variance: float = 1.0,
        away_variance: float = 1.0
    ) -> Tuple[int, int]:
        """
        Simulate a single match and return scoreline.
        """
        home_goals = self.simulate_goals(home_xg, home_variance)
        away_goals = self.simulate_goals(away_xg, away_variance)
        
        return home_goals, away_goals
    
    def run_simulation(
        self,
        home_xg: float,
        away_xg: float,
        home_variance: float = 1.0,
        away_variance: float = 1.0,
        num_simulations: int = None
    ) -> SimulationResult:
        """
        Run full Monte Carlo simulation for a match.
        
        Args:
            home_xg: Expected goals for home team
            away_xg: Expected goals for away team
            home_variance: Variance factor for home team (>1 = more unpredictable)
            away_variance: Variance factor for away team
            num_simulations: Number of simulations to run
        
        Returns:
            SimulationResult with comprehensive probability distributions
        """
        n_sims = num_simulations or self.default_simulations
        
        home_wins = 0
        draws = 0
        away_wins = 0
        
        total_home_goals = 0
        total_away_goals = 0
        
        btts_count = 0
        over_counts = {
            "05": 0, "15": 0, "25": 0, "35": 0, "45": 0
        }
        
        score_counts = Counter()
        home_goal_counts = Counter()
        away_goal_counts = Counter()
        
        for _ in range(n_sims):
            home_goals, away_goals = self.simulate_single_match(
                home_xg, away_xg, home_variance, away_variance
            )
            
            total_home_goals += home_goals
            total_away_goals += away_goals
            total_goals = home_goals + away_goals
            
            # Outcome
            if home_goals > away_goals:
                home_wins += 1
            elif home_goals == away_goals:
                draws += 1
            else:
                away_wins += 1
            
            # BTTS
            if home_goals > 0 and away_goals > 0:
                btts_count += 1
            
            # Over/Under
            for line, key in [(0.5, "05"), (1.5, "15"), (2.5, "25"), (3.5, "35"), (4.5, "45")]:
                if total_goals > line:
                    over_counts[key] += 1
            
            # Score distribution
            score = f"{home_goals}-{away_goals}"
            score_counts[score] += 1
            home_goal_counts[home_goals] += 1
            away_goal_counts[away_goals] += 1
        
        # Calculate probabilities
        home_win_prob = home_wins / n_sims
        draw_prob = draws / n_sims
        away_win_prob = away_wins / n_sims
        
        avg_home = total_home_goals / n_sims
        avg_away = total_away_goals / n_sims
        
        btts_prob = btts_count / n_sims
        
        over_probs = {
            f"over_{k}": round(v / n_sims * 100, 2)
            for k, v in over_counts.items()
        }
        over_probs.update({
            f"under_{k}": round(100 - v / n_sims * 100, 2)
            for k, v in over_counts.items()
        })
        
        # Top 20 most likely scores
        top_scores = score_counts.most_common(20)
        score_distribution = [
            {
                "score": score,
                "home_goals": int(score.split("-")[0]),
                "away_goals": int(score.split("-")[1]),
                "probability": round(count / n_sims * 100, 2),
                "count": count
            }
            for score, count in top_scores
        ]
        
        # Calculate 95% confidence intervals
        confidence_interval = self._calculate_confidence_intervals(
            home_win_prob, draw_prob, away_win_prob, n_sims
        )
        
        return SimulationResult(
            home_win_prob=round(home_win_prob * 100, 2),
            draw_prob=round(draw_prob * 100, 2),
            away_win_prob=round(away_win_prob * 100, 2),
            avg_home_goals=round(avg_home, 2),
            avg_away_goals=round(avg_away, 2),
            avg_total_goals=round(avg_home + avg_away, 2),
            over_probabilities=over_probs,
            btts_prob=round(btts_prob * 100, 2),
            score_distribution=score_distribution,
            simulations_run=n_sims,
            confidence_interval=confidence_interval
        )
    
    def _calculate_confidence_intervals(
        self,
        home_prob: float,
        draw_prob: float,
        away_prob: float,
        n: int
    ) -> Dict[str, Tuple[float, float]]:
        """Calculate 95% confidence intervals using Wilson score interval"""
        def wilson_interval(p: float, n: int) -> Tuple[float, float]:
            if n == 0:
                return (0, 0)
            
            z = 1.96  # 95% confidence
            denominator = 1 + z**2/n
            
            center = (p + z**2/(2*n)) / denominator
            spread = z * math.sqrt((p*(1-p) + z**2/(4*n)) / n) / denominator
            
            lower = max(0, center - spread)
            upper = min(1, center + spread)
            
            return (round(lower * 100, 2), round(upper * 100, 2))
        
        return {
            "home_win": wilson_interval(home_prob, n),
            "draw": wilson_interval(draw_prob, n),
            "away_win": wilson_interval(away_prob, n)
        }
    
    def run_half_time_simulation(
        self,
        home_xg: float,
        away_xg: float,
        num_simulations: int = None
    ) -> Dict[str, float]:
        """
        Simulate half-time outcomes.
        
        Half-time xG is approximately 45-50% of full-time xG.
        """
        n_sims = num_simulations or self.default_simulations
        
        ht_home_xg = home_xg * 0.47
        ht_away_xg = away_xg * 0.47
        
        home_wins = 0
        draws = 0
        away_wins = 0
        over_05 = 0
        over_15 = 0
        
        for _ in range(n_sims):
            home_goals, away_goals = self.simulate_single_match(
                ht_home_xg, ht_away_xg, 1.1, 1.1  # Slightly higher variance for HT
            )
            
            total = home_goals + away_goals
            
            if home_goals > away_goals:
                home_wins += 1
            elif home_goals == away_goals:
                draws += 1
            else:
                away_wins += 1
            
            if total > 0.5:
                over_05 += 1
            if total > 1.5:
                over_15 += 1
        
        return {
            "home_win_prob": round(home_wins / n_sims * 100, 2),
            "draw_prob": round(draws / n_sims * 100, 2),
            "away_win_prob": round(away_wins / n_sims * 100, 2),
            "over_05_prob": round(over_05 / n_sims * 100, 2),
            "over_15_prob": round(over_15 / n_sims * 100, 2)
        }
    
    def run_asian_handicap_simulation(
        self,
        home_xg: float,
        away_xg: float,
        handicap_line: float,
        num_simulations: int = None
    ) -> Dict[str, float]:
        """
        Simulate Asian Handicap outcomes.
        
        Args:
            handicap_line: Handicap applied to home team
                          -1.5 means home team starts -1.5 goals
        """
        n_sims = num_simulations or self.default_simulations
        
        home_covers = 0
        pushes = 0
        away_covers = 0
        
        for _ in range(n_sims):
            home_goals, away_goals = self.simulate_single_match(
                home_xg, away_xg
            )
            
            # Apply handicap
            adjusted_home = home_goals + handicap_line
            
            if adjusted_home > away_goals:
                home_covers += 1
            elif adjusted_home == away_goals:
                pushes += 1
            else:
                away_covers += 1
        
        return {
            "home_covers_prob": round(home_covers / n_sims * 100, 2),
            "push_prob": round(pushes / n_sims * 100, 2),
            "away_covers_prob": round(away_covers / n_sims * 100, 2),
            "handicap_line": handicap_line
        }
    
    def aggregate_simulations(
        self,
        results: List[SimulationResult]
    ) -> SimulationResult:
        """
        Aggregate multiple simulation results (e.g., from different models).
        """
        if not results:
            raise ValueError("No simulation results to aggregate")
        
        n = len(results)
        total_sims = sum(r.simulations_run for r in results)
        
        return SimulationResult(
            home_win_prob=round(sum(r.home_win_prob for r in results) / n, 2),
            draw_prob=round(sum(r.draw_prob for r in results) / n, 2),
            away_win_prob=round(sum(r.away_win_prob for r in results) / n, 2),
            avg_home_goals=round(sum(r.avg_home_goals for r in results) / n, 2),
            avg_away_goals=round(sum(r.avg_away_goals for r in results) / n, 2),
            avg_total_goals=round(sum(r.avg_total_goals for r in results) / n, 2),
            over_probabilities=results[0].over_probabilities,  # Use first result's
            btts_prob=round(sum(r.btts_prob for r in results) / n, 2),
            score_distribution=results[0].score_distribution,
            simulations_run=total_sims,
            confidence_interval=results[0].confidence_interval
        )
