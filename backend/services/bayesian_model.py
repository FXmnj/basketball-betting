"""
Bayesian Updating System for Dynamic Prediction Adjustment
Updates predictions when new information arrives (injuries, lineups, odds changes)
"""
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import math


@dataclass
class BayesianUpdate:
    prior_prob: float
    likelihood: float
    posterior_prob: float
    update_reason: str
    confidence_change: float


class BayesianUpdater:
    """
    Bayesian probability updater for adjusting match predictions
    based on new information.
    
    Posterior ∝ Prior × Likelihood
    """
    
    def __init__(self):
        # Impact factors for different types of updates
        self.impact_factors = {
            "key_player_injury": 0.85,  # Reduces team's effective strength
            "minor_player_injury": 0.95,
            "key_player_return": 1.15,
            "lineup_strong": 1.08,
            "lineup_weak": 0.92,
            "form_improving": 1.05,
            "form_declining": 0.95,
            "weather_home_advantage": 1.03,
            "weather_away_advantage": 0.97,
            "odds_sharp_move_home": 1.10,
            "odds_sharp_move_away": 0.90,
            "odds_sharp_move_draw": 1.05,
            "h2h_home_dominant": 1.08,
            "h2h_away_dominant": 0.92,
            "h2h_balanced": 1.0,
            "motivation_high": 1.06,
            "motivation_low": 0.94,
        }
    
    def calculate_posterior(
        self,
        prior: float,
        likelihood: float
    ) -> float:
        """
        Calculate posterior probability using Bayes' theorem.
        
        P(A|B) = P(B|A) × P(A) / P(B)
        
        Simplified: Posterior ∝ Prior × Likelihood
        """
        # Ensure prior is valid
        prior = max(0.01, min(0.99, prior))
        
        # Calculate unnormalized posterior
        posterior = prior * likelihood
        
        # Normalize to valid probability range
        posterior = max(0.01, min(0.99, posterior))
        
        return posterior
    
    def normalize_probabilities(
        self,
        home_prob: float,
        draw_prob: float,
        away_prob: float
    ) -> Tuple[float, float, float]:
        """Normalize three probabilities to sum to 1"""
        total = home_prob + draw_prob + away_prob
        
        if total <= 0:
            return 0.33, 0.34, 0.33
        
        return (
            home_prob / total,
            draw_prob / total,
            away_prob / total
        )
    
    def update_for_injury(
        self,
        prior_probs: Dict[str, float],
        team: str,  # "home" or "away"
        player_importance: float,  # 0-1 scale
        is_injury: bool = True
    ) -> Dict[str, BayesianUpdate]:
        """
        Update predictions based on player injury/return.
        
        Args:
            prior_probs: {"home_win": 0.5, "draw": 0.25, "away_win": 0.25}
            team: Which team is affected
            player_importance: How important the player is (0-1)
            is_injury: True for injury, False for return from injury
        """
        updates = {}
        
        # Calculate likelihood based on player importance
        if is_injury:
            base_impact = 0.85 if player_importance > 0.7 else 0.95
            impact_factor = base_impact ** player_importance
        else:
            base_impact = 1.15 if player_importance > 0.7 else 1.05
            impact_factor = base_impact ** player_importance
        
        home_prior = prior_probs.get("home_win", 0.4)
        draw_prior = prior_probs.get("draw", 0.3)
        away_prior = prior_probs.get("away_win", 0.3)
        
        if team == "home":
            # Home team affected
            home_likelihood = impact_factor
            away_likelihood = 2.0 - impact_factor  # Inverse effect
            draw_likelihood = 1.0 + (1.0 - impact_factor) * 0.5
        else:
            # Away team affected
            away_likelihood = impact_factor
            home_likelihood = 2.0 - impact_factor
            draw_likelihood = 1.0 + (1.0 - impact_factor) * 0.5
        
        # Calculate posteriors
        home_post = self.calculate_posterior(home_prior, home_likelihood)
        draw_post = self.calculate_posterior(draw_prior, draw_likelihood)
        away_post = self.calculate_posterior(away_prior, away_likelihood)
        
        # Normalize
        home_post, draw_post, away_post = self.normalize_probabilities(
            home_post, draw_post, away_post
        )
        
        reason = f"{'Injury to' if is_injury else 'Return of'} key {team} player"
        
        updates["home_win"] = BayesianUpdate(
            prior_prob=home_prior,
            likelihood=home_likelihood,
            posterior_prob=home_post,
            update_reason=reason,
            confidence_change=(home_post - home_prior) * 100
        )
        
        updates["draw"] = BayesianUpdate(
            prior_prob=draw_prior,
            likelihood=draw_likelihood,
            posterior_prob=draw_post,
            update_reason=reason,
            confidence_change=(draw_post - draw_prior) * 100
        )
        
        updates["away_win"] = BayesianUpdate(
            prior_prob=away_prior,
            likelihood=away_likelihood,
            posterior_prob=away_post,
            update_reason=reason,
            confidence_change=(away_post - away_prior) * 100
        )
        
        return updates
    
    def update_for_odds_movement(
        self,
        prior_probs: Dict[str, float],
        opening_odds: Dict[str, float],
        current_odds: Dict[str, float],
        sharp_threshold: float = 0.10
    ) -> Dict[str, BayesianUpdate]:
        """
        Update predictions based on odds movement (detecting sharp money).
        
        Sharp money = significant odds movement indicating informed betting
        """
        updates = {}
        
        # Calculate implied probabilities from odds
        def odds_to_prob(odds: float) -> float:
            return 1.0 / odds if odds > 0 else 0
        
        # Calculate movement
        home_movement = (
            odds_to_prob(current_odds.get("home_win", 2.0)) -
            odds_to_prob(opening_odds.get("home_win", 2.0))
        )
        draw_movement = (
            odds_to_prob(current_odds.get("draw", 3.5)) -
            odds_to_prob(opening_odds.get("draw", 3.5))
        )
        away_movement = (
            odds_to_prob(current_odds.get("away_win", 4.0)) -
            odds_to_prob(opening_odds.get("away_win", 4.0))
        )
        
        # Detect sharp movement
        movements = {"home_win": home_movement, "draw": draw_movement, "away_win": away_movement}
        sharp_direction = None
        max_movement = 0
        
        for outcome, movement in movements.items():
            if abs(movement) > abs(max_movement):
                max_movement = movement
                if abs(movement) >= sharp_threshold:
                    sharp_direction = outcome
        
        # Apply Bayesian update based on sharp money
        for outcome in ["home_win", "draw", "away_win"]:
            prior = prior_probs.get(outcome, 0.33)
            
            if sharp_direction == outcome and max_movement > 0:
                likelihood = self.impact_factors["odds_sharp_move_home"]
            elif sharp_direction and sharp_direction != outcome and max_movement > 0:
                likelihood = 0.95  # Slight reduction
            else:
                likelihood = 1.0 + movements.get(outcome, 0)
            
            posterior = self.calculate_posterior(prior, likelihood)
            
            updates[outcome] = BayesianUpdate(
                prior_prob=prior,
                likelihood=likelihood,
                posterior_prob=posterior,
                update_reason=f"Odds movement {'(sharp money detected)' if sharp_direction else ''}",
                confidence_change=(posterior - prior) * 100
            )
        
        # Normalize posteriors
        home_post, draw_post, away_post = self.normalize_probabilities(
            updates["home_win"].posterior_prob,
            updates["draw"].posterior_prob,
            updates["away_win"].posterior_prob
        )
        
        updates["home_win"].posterior_prob = home_post
        updates["draw"].posterior_prob = draw_post
        updates["away_win"].posterior_prob = away_post
        
        return updates
    
    def update_for_lineup(
        self,
        prior_probs: Dict[str, float],
        home_lineup_strength: float,  # 0-1 scale
        away_lineup_strength: float
    ) -> Dict[str, BayesianUpdate]:
        """
        Update predictions based on announced lineups.
        """
        updates = {}
        
        # Calculate relative strength difference
        strength_diff = home_lineup_strength - away_lineup_strength
        
        # Calculate likelihoods
        if strength_diff > 0.1:
            home_likelihood = 1.0 + strength_diff * 0.5
            away_likelihood = 1.0 - strength_diff * 0.4
            draw_likelihood = 1.0 - abs(strength_diff) * 0.2
        elif strength_diff < -0.1:
            home_likelihood = 1.0 + strength_diff * 0.4
            away_likelihood = 1.0 - strength_diff * 0.5
            draw_likelihood = 1.0 - abs(strength_diff) * 0.2
        else:
            home_likelihood = 1.0
            away_likelihood = 1.0
            draw_likelihood = 1.1  # Evenly matched = more likely draw
        
        for outcome, likelihood in [
            ("home_win", home_likelihood),
            ("draw", draw_likelihood),
            ("away_win", away_likelihood)
        ]:
            prior = prior_probs.get(outcome, 0.33)
            posterior = self.calculate_posterior(prior, likelihood)
            
            updates[outcome] = BayesianUpdate(
                prior_prob=prior,
                likelihood=likelihood,
                posterior_prob=posterior,
                update_reason="Lineup announcement",
                confidence_change=(posterior - prior) * 100
            )
        
        # Normalize
        home_post, draw_post, away_post = self.normalize_probabilities(
            updates["home_win"].posterior_prob,
            updates["draw"].posterior_prob,
            updates["away_win"].posterior_prob
        )
        
        updates["home_win"].posterior_prob = home_post
        updates["draw"].posterior_prob = draw_post
        updates["away_win"].posterior_prob = away_post
        
        return updates
    
    def update_for_recent_form(
        self,
        prior_probs: Dict[str, float],
        home_form: str,  # e.g., "WWDLW"
        away_form: str
    ) -> Dict[str, BayesianUpdate]:
        """
        Update predictions based on recent form (last 5 matches).
        """
        def form_to_score(form: str) -> float:
            """Convert form string to numerical score"""
            score = 0
            weights = [0.3, 0.25, 0.2, 0.15, 0.1]  # Recent matches weighted more
            
            for i, result in enumerate(form[:5]):
                if i >= len(weights):
                    break
                if result == 'W':
                    score += 3 * weights[i]
                elif result == 'D':
                    score += 1 * weights[i]
            
            return score / sum(weights[:len(form[:5])])
        
        home_form_score = form_to_score(home_form) if home_form else 1.5
        away_form_score = form_to_score(away_form) if away_form else 1.5
        
        # Normalize to likelihood
        avg_score = (home_form_score + away_form_score) / 2
        home_form_factor = home_form_score / avg_score if avg_score > 0 else 1.0
        away_form_factor = away_form_score / avg_score if avg_score > 0 else 1.0
        
        updates = {}
        
        likelihoods = {
            "home_win": 0.9 + home_form_factor * 0.2,
            "draw": 1.0,
            "away_win": 0.9 + away_form_factor * 0.2
        }
        
        for outcome, likelihood in likelihoods.items():
            prior = prior_probs.get(outcome, 0.33)
            posterior = self.calculate_posterior(prior, likelihood)
            
            updates[outcome] = BayesianUpdate(
                prior_prob=prior,
                likelihood=likelihood,
                posterior_prob=posterior,
                update_reason=f"Form update: Home {home_form}, Away {away_form}",
                confidence_change=(posterior - prior) * 100
            )
        
        # Normalize
        home_post, draw_post, away_post = self.normalize_probabilities(
            updates["home_win"].posterior_prob,
            updates["draw"].posterior_prob,
            updates["away_win"].posterior_prob
        )
        
        updates["home_win"].posterior_prob = home_post
        updates["draw"].posterior_prob = draw_post
        updates["away_win"].posterior_prob = away_post
        
        return updates
    
    def apply_multiple_updates(
        self,
        prior_probs: Dict[str, float],
        updates: List[Dict[str, BayesianUpdate]]
    ) -> Dict[str, float]:
        """
        Apply multiple Bayesian updates sequentially.
        """
        current_probs = prior_probs.copy()
        
        for update_dict in updates:
            for outcome in ["home_win", "draw", "away_win"]:
                if outcome in update_dict:
                    current_probs[outcome] = update_dict[outcome].posterior_prob
        
        # Final normalization
        total = sum(current_probs.values())
        return {k: v / total for k, v in current_probs.items()}
