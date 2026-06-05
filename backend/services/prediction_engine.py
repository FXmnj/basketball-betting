"""
Main Prediction Engine
Orchestrates all prediction models to generate final predictions
"""
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
import asyncio

from .poisson_model import PoissonGoalModel
from .bayesian_model import BayesianUpdater
from .xg_model import ExpectedGoalsModel
from .player_impact import PlayerImpactModel
from .monte_carlo import MonteCarloSimulator
from .ml_ensemble import MLEnsemble
from .odds_analyzer import OddsAnalyzer


@dataclass
class FullPrediction:
    match_id: str
    home_team: str
    away_team: str
    home_win_prob: float
    draw_prob: float
    away_win_prob: float
    expected_home_goals: float
    expected_away_goals: float
    over_under_probs: Dict[str, float]
    btts_prob: float
    score_probabilities: List[Dict]
    ht_prediction: Dict[str, float]
    asian_handicap: Dict[str, float]
    value_bets: List[Dict]
    confidence: float
    model_breakdown: Dict[str, Dict]
    generated_at: str


class PredictionEngine:
    """
    Main prediction engine that combines all models.
    
    Pipeline:
    1. Poisson model for base goal expectations
    2. ML Ensemble for probability refinement
    3. Monte Carlo for simulation-based probabilities
    4. Bayesian updates for new information
    5. Odds analysis for value bet detection
    """
    
    def __init__(self):
        self.poisson = PoissonGoalModel()
        self.bayesian = BayesianUpdater()
        self.xg_model = ExpectedGoalsModel()
        self.player_impact = PlayerImpactModel()
        self.monte_carlo = MonteCarloSimulator(default_simulations=10000)
        self.ml_ensemble = MLEnsemble()
        self.odds_analyzer = OddsAnalyzer()
    
    def generate_prediction(
        self,
        match_id: str,
        home_team: Dict,
        away_team: Dict,
        league_stats: Dict = None,
        h2h_data: List = None,
        odds_data: Dict = None,
        injuries: Dict = None
    ) -> FullPrediction:
        """
        Generate comprehensive prediction for a match.
        """
        league_stats = league_stats or {
            "avg_home_goals": 1.5,
            "avg_away_goals": 1.2,
            "home_win_rate": 0.45,
            "draw_rate": 0.27,
            "away_win_rate": 0.28
        }
        h2h_data = h2h_data or []
        odds_data = odds_data or {}
        injuries = injuries or {"home": [], "away": []}
        
        # Step 1: Calculate team strengths
        home_attack = home_team.get("attack_strength", 1.0)
        home_defense = home_team.get("defense_strength", 1.0)
        away_attack = away_team.get("attack_strength", 1.0)
        away_defense = away_team.get("defense_strength", 1.0)
        
        # Step 2: Poisson prediction
        poisson_result = self.poisson.predict(
            home_attack=home_attack,
            home_defense=home_defense,
            away_attack=away_attack,
            away_defense=away_defense,
            league_avg_home_goals=league_stats.get("avg_home_goals", 1.5),
            league_avg_away_goals=league_stats.get("avg_away_goals", 1.2)
        )
        
        # Step 3: xG-based estimates
        home_xg = self.xg_model.estimate_team_xg(
            attack_strength=home_attack,
            opponent_defense=away_defense,
            is_home=True,
            league_avg_xg=league_stats.get("avg_home_goals", 1.5)
        )
        
        away_xg = self.xg_model.estimate_team_xg(
            attack_strength=away_attack,
            opponent_defense=home_defense,
            is_home=False,
            league_avg_xg=league_stats.get("avg_away_goals", 1.2)
        )
        
        # Step 4: ML Ensemble prediction
        home_stats = {
            "attack_strength": home_attack,
            "defense_strength": home_defense,
            "form_score": self._form_to_score(home_team.get("form", "")),
            "xg_for": home_team.get("xg_for", home_xg),
            "xg_against": home_team.get("xg_against", 1.2),
            "goals_scored_avg": home_team.get("goals_scored_avg", 1.5),
            "goals_conceded_avg": home_team.get("goals_conceded_avg", 1.2),
            "position": home_team.get("position", 10)
        }
        
        away_stats = {
            "attack_strength": away_attack,
            "defense_strength": away_defense,
            "form_score": self._form_to_score(away_team.get("form", "")),
            "xg_for": away_team.get("xg_for", away_xg),
            "xg_against": away_team.get("xg_against", 1.4),
            "goals_scored_avg": away_team.get("goals_scored_avg", 1.3),
            "goals_conceded_avg": away_team.get("goals_conceded_avg", 1.4),
            "position": away_team.get("position", 10)
        }
        
        # H2H data processing
        h2h_stats = self._process_h2h(h2h_data, home_team.get("name", ""), away_team.get("name", ""))
        
        # Odds to implied probabilities
        odds_implied = {}
        if odds_data:
            if odds_data.get("home_win"):
                odds_implied["implied_home"] = 1 / odds_data["home_win"]
            if odds_data.get("draw"):
                odds_implied["implied_draw"] = 1 / odds_data["draw"]
            if odds_data.get("away_win"):
                odds_implied["implied_away"] = 1 / odds_data["away_win"]
        
        ml_result = self.ml_ensemble.ensemble_predict(
            home_stats=home_stats,
            away_stats=away_stats,
            h2h_data=h2h_stats,
            league_stats=league_stats,
            odds_data=odds_implied
        )
        
        # Step 5: Monte Carlo simulation
        avg_home_xg = (poisson_result.expected_home_goals + home_xg) / 2
        avg_away_xg = (poisson_result.expected_away_goals + away_xg) / 2
        
        mc_result = self.monte_carlo.run_simulation(
            home_xg=avg_home_xg,
            away_xg=avg_away_xg
        )
        
        # Step 6: Combine model outputs (weighted average)
        final_home_prob = (
            poisson_result.home_win_prob * 0.25 +
            ml_result.home_win_prob * 0.40 +
            mc_result.home_win_prob * 0.35
        )
        
        final_draw_prob = (
            poisson_result.draw_prob * 0.25 +
            ml_result.draw_prob * 0.40 +
            mc_result.draw_prob * 0.35
        )
        
        final_away_prob = (
            poisson_result.away_win_prob * 0.25 +
            ml_result.away_win_prob * 0.40 +
            mc_result.away_win_prob * 0.35
        )
        
        # Normalize
        total = final_home_prob + final_draw_prob + final_away_prob
        final_home_prob = round(final_home_prob / total * 100, 2)
        final_draw_prob = round(final_draw_prob / total * 100, 2)
        final_away_prob = round(final_away_prob / total * 100, 2)
        
        # Step 7: Bayesian updates for injuries
        if injuries.get("home") or injuries.get("away"):
            priors = {
                "home_win": final_home_prob / 100,
                "draw": final_draw_prob / 100,
                "away_win": final_away_prob / 100
            }
            
            for injury in injuries.get("home", []):
                updates = self.bayesian.update_for_injury(
                    priors, "home", injury.get("importance", 0.5), True
                )
                priors = {k: v.posterior_prob for k, v in updates.items()}
            
            for injury in injuries.get("away", []):
                updates = self.bayesian.update_for_injury(
                    priors, "away", injury.get("importance", 0.5), True
                )
                priors = {k: v.posterior_prob for k, v in updates.items()}
            
            final_home_prob = round(priors["home_win"] * 100, 2)
            final_draw_prob = round(priors["draw"] * 100, 2)
            final_away_prob = round(priors["away_win"] * 100, 2)
        
        # Step 8: Over/Under and BTTS
        over_under = self.poisson.calculate_over_under_probabilities(
            poisson_result.goal_probabilities
        )
        
        btts_prob = self.poisson.calculate_btts_probability(
            poisson_result.goal_probabilities
        )
        
        # Step 9: Half-time prediction
        ht_prediction = self.monte_carlo.run_half_time_simulation(
            avg_home_xg, avg_away_xg
        )
        
        # Step 10: Asian Handicap
        asian_handicap = self._calculate_asian_handicap(
            avg_home_xg, avg_away_xg
        )
        
        # Step 11: Value bets detection
        value_bets = []
        if odds_data:
            model_probs = {
                "home_win": final_home_prob / 100,
                "draw": final_draw_prob / 100,
                "away_win": final_away_prob / 100,
                "over_25": over_under.get("over_25", 50) / 100,
                "btts_yes": btts_prob / 100
            }
            
            book_odds = {
                "home_win": odds_data.get("home_win", 2.0),
                "draw": odds_data.get("draw", 3.5),
                "away_win": odds_data.get("away_win", 4.0),
                "over_25": odds_data.get("over_25", 1.9),
                "btts_yes": odds_data.get("btts_yes", 1.8)
            }
            
            value_bets_result = self.odds_analyzer.find_value_bets(
                model_probs, book_odds
            )
            value_bets = [asdict(vb) for vb in value_bets_result]
        
        # Calculate overall confidence
        confidence = round(ml_result.confidence * 100, 2)
        
        # Model breakdown
        model_breakdown = {
            "poisson": {
                "home_win": poisson_result.home_win_prob,
                "draw": poisson_result.draw_prob,
                "away_win": poisson_result.away_win_prob,
                "expected_home_goals": poisson_result.expected_home_goals,
                "expected_away_goals": poisson_result.expected_away_goals
            },
            "ml_ensemble": {
                "home_win": ml_result.home_win_prob,
                "draw": ml_result.draw_prob,
                "away_win": ml_result.away_win_prob,
                "confidence": ml_result.confidence,
                "model_contributions": ml_result.model_contributions
            },
            "monte_carlo": {
                "home_win": mc_result.home_win_prob,
                "draw": mc_result.draw_prob,
                "away_win": mc_result.away_win_prob,
                "simulations": mc_result.simulations_run,
                "confidence_interval": mc_result.confidence_interval
            }
        }
        
        return FullPrediction(
            match_id=match_id,
            home_team=home_team.get("name", "Home"),
            away_team=away_team.get("name", "Away"),
            home_win_prob=final_home_prob,
            draw_prob=final_draw_prob,
            away_win_prob=final_away_prob,
            expected_home_goals=round(avg_home_xg, 2),
            expected_away_goals=round(avg_away_xg, 2),
            over_under_probs=over_under,
            btts_prob=btts_prob,
            score_probabilities=mc_result.score_distribution[:15],
            ht_prediction=ht_prediction,
            asian_handicap=asian_handicap,
            value_bets=value_bets,
            confidence=confidence,
            model_breakdown=model_breakdown,
            generated_at=datetime.now(timezone.utc).isoformat()
        )
    
    def _form_to_score(self, form: str) -> float:
        """Convert form string to numerical score (0-100)"""
        if not form:
            return 50.0
        
        score = 0
        weights = [0.3, 0.25, 0.2, 0.15, 0.1]
        
        for i, result in enumerate(form[:5]):
            if i >= len(weights):
                break
            if result == 'W':
                score += 100 * weights[i]
            elif result == 'D':
                score += 50 * weights[i]
            elif result == 'L':
                score += 0
        
        return round(score / sum(weights[:len(form[:5])]) if form[:5] else 50, 2)
    
    def _process_h2h(
        self,
        h2h_data: List,
        home_team: str,
        away_team: str
    ) -> Dict:
        """Process head-to-head data"""
        if not h2h_data:
            return {"home_wins": 0, "draws": 0, "away_wins": 0}
        
        home_wins = 0
        draws = 0
        away_wins = 0
        
        for match in h2h_data[:10]:
            if match.get("home_team") == home_team:
                if match.get("home_score", 0) > match.get("away_score", 0):
                    home_wins += 1
                elif match.get("home_score", 0) == match.get("away_score", 0):
                    draws += 1
                else:
                    away_wins += 1
            else:
                # Reverse roles
                if match.get("home_score", 0) > match.get("away_score", 0):
                    away_wins += 1
                elif match.get("home_score", 0) == match.get("away_score", 0):
                    draws += 1
                else:
                    home_wins += 1
        
        return {"home_wins": home_wins, "draws": draws, "away_wins": away_wins}
    
    def _calculate_asian_handicap(
        self,
        home_xg: float,
        away_xg: float
    ) -> Dict:
        """Calculate Asian Handicap line and probabilities"""
        goal_diff = home_xg - away_xg
        
        # Determine appropriate handicap line
        if goal_diff > 0.75:
            handicap = -1.0
        elif goal_diff > 0.25:
            handicap = -0.5
        elif goal_diff > -0.25:
            handicap = 0
        elif goal_diff > -0.75:
            handicap = 0.5
        else:
            handicap = 1.0
        
        # Run simulation for handicap
        ah_result = self.monte_carlo.run_asian_handicap_simulation(
            home_xg, away_xg, handicap
        )
        
        return ah_result
    
    def batch_predict(
        self,
        matches: List[Dict]
    ) -> List[FullPrediction]:
        """
        Generate predictions for multiple matches.
        """
        predictions = []
        
        for match in matches:
            try:
                prediction = self.generate_prediction(
                    match_id=match.get("id", ""),
                    home_team=match.get("home_team", {}),
                    away_team=match.get("away_team", {}),
                    league_stats=match.get("league_stats"),
                    h2h_data=match.get("h2h_data"),
                    odds_data=match.get("odds_data"),
                    injuries=match.get("injuries")
                )
                predictions.append(prediction)
            except Exception as e:
                print(f"Error predicting match {match.get('id')}: {e}")
                continue
        
        return predictions
