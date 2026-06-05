"""
Machine Learning Ensemble for Match Prediction
Combines XGBoost, Random Forest, Neural Network, and Logistic Regression
"""
import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import random
import math


@dataclass
class ModelPrediction:
    home_win_prob: float
    draw_prob: float
    away_win_prob: float
    confidence: float
    model_name: str


@dataclass
class EnsemblePrediction:
    home_win_prob: float
    draw_prob: float
    away_win_prob: float
    confidence: float
    model_contributions: Dict[str, float]
    feature_importance: Dict[str, float]


class MLEnsemble:
    """
    Ensemble machine learning model combining multiple algorithms.
    
    Models:
    - XGBoost (gradient boosting)
    - Random Forest (bagging)
    - Neural Network (deep learning)
    - Logistic Regression (baseline)
    
    Final prediction is weighted average based on model performance.
    """
    
    def __init__(self):
        # Model weights based on typical performance
        self.model_weights = {
            "xgboost": 0.35,
            "random_forest": 0.30,
            "neural_network": 0.25,
            "logistic_regression": 0.10
        }
        
        # Feature names for interpretability
        self.feature_names = [
            "home_attack_strength",
            "home_defense_strength",
            "away_attack_strength",
            "away_defense_strength",
            "home_form_score",
            "away_form_score",
            "home_xg_for",
            "home_xg_against",
            "away_xg_for",
            "away_xg_against",
            "h2h_home_wins",
            "h2h_draws",
            "h2h_away_wins",
            "home_goals_scored_avg",
            "home_goals_conceded_avg",
            "away_goals_scored_avg",
            "away_goals_conceded_avg",
            "league_home_win_rate",
            "league_draw_rate",
            "league_avg_goals",
            "odds_implied_home",
            "odds_implied_draw",
            "odds_implied_away",
            "home_position",
            "away_position",
            "importance_factor"
        ]
        
        # Simulated feature importance (would be learned from training)
        self.feature_importance = {
            "home_attack_strength": 0.12,
            "away_defense_strength": 0.11,
            "home_form_score": 0.09,
            "home_xg_for": 0.08,
            "odds_implied_home": 0.08,
            "away_attack_strength": 0.07,
            "home_defense_strength": 0.06,
            "away_xg_for": 0.06,
            "h2h_home_wins": 0.05,
            "home_position": 0.05,
            "away_position": 0.05,
            "league_home_win_rate": 0.04,
            "other": 0.14
        }
    
    def prepare_features(
        self,
        home_stats: Dict,
        away_stats: Dict,
        h2h_data: Dict,
        league_stats: Dict,
        odds_data: Dict
    ) -> np.ndarray:
        """
        Prepare feature vector for prediction.
        """
        features = [
            home_stats.get("attack_strength", 1.0),
            home_stats.get("defense_strength", 1.0),
            away_stats.get("attack_strength", 1.0),
            away_stats.get("defense_strength", 1.0),
            home_stats.get("form_score", 50),
            away_stats.get("form_score", 50),
            home_stats.get("xg_for", 1.5),
            home_stats.get("xg_against", 1.2),
            away_stats.get("xg_for", 1.3),
            away_stats.get("xg_against", 1.4),
            h2h_data.get("home_wins", 0),
            h2h_data.get("draws", 0),
            h2h_data.get("away_wins", 0),
            home_stats.get("goals_scored_avg", 1.5),
            home_stats.get("goals_conceded_avg", 1.2),
            away_stats.get("goals_scored_avg", 1.3),
            away_stats.get("goals_conceded_avg", 1.4),
            league_stats.get("home_win_rate", 0.45),
            league_stats.get("draw_rate", 0.25),
            league_stats.get("avg_goals", 2.7),
            odds_data.get("implied_home", 0.4),
            odds_data.get("implied_draw", 0.28),
            odds_data.get("implied_away", 0.32),
            home_stats.get("position", 10),
            away_stats.get("position", 10),
            1.0  # Importance factor (could be cup final, relegation battle, etc.)
        ]
        
        return np.array(features)
    
    def _sigmoid(self, x: float) -> float:
        """Sigmoid activation function"""
        return 1 / (1 + math.exp(-max(-500, min(500, x))))
    
    def _softmax(self, scores: List[float]) -> List[float]:
        """Softmax function for probability normalization"""
        max_score = max(scores)
        exp_scores = [math.exp(s - max_score) for s in scores]
        total = sum(exp_scores)
        return [e / total for e in exp_scores]
    
    def predict_xgboost(
        self,
        features: np.ndarray
    ) -> ModelPrediction:
        """
        Simulated XGBoost prediction.
        
        In production, this would use a trained XGBoost model.
        """
        # Weighted feature combination (simulating gradient boosting)
        home_score = (
            features[0] * 0.3 +  # home attack
            (1 / features[3]) * 0.2 +  # away defense weakness
            features[4] * 0.01 +  # home form
            features[6] * 0.15 +  # home xG
            features[20] * 0.15 +  # odds implied home
            random.gauss(0, 0.02)  # Model uncertainty
        )
        
        draw_score = (
            0.25 +
            (1 - abs(features[0] - features[2])) * 0.1 +  # Similar attack strengths
            features[21] * 0.12 +  # odds implied draw
            random.gauss(0, 0.02)
        )
        
        away_score = (
            features[2] * 0.25 +  # away attack
            (1 / features[1]) * 0.15 +  # home defense weakness
            features[5] * 0.01 +  # away form
            features[8] * 0.12 +  # away xG
            features[22] * 0.15 +  # odds implied away
            random.gauss(0, 0.02)
        )
        
        probs = self._softmax([home_score, draw_score, away_score])
        
        return ModelPrediction(
            home_win_prob=probs[0],
            draw_prob=probs[1],
            away_win_prob=probs[2],
            confidence=0.75 + random.uniform(-0.05, 0.05),
            model_name="xgboost"
        )
    
    def predict_random_forest(
        self,
        features: np.ndarray
    ) -> ModelPrediction:
        """
        Simulated Random Forest prediction.
        """
        # Simulate multiple decision trees
        n_trees = 100
        home_votes = 0
        draw_votes = 0
        away_votes = 0
        
        for _ in range(n_trees):
            # Random feature subset (simulating tree randomness)
            home_strength = features[0] * (1 + random.uniform(-0.1, 0.1))
            away_strength = features[2] * (1 + random.uniform(-0.1, 0.1))
            form_diff = (features[4] - features[5]) / 100
            
            combined = home_strength - away_strength + form_diff
            
            if combined > 0.15:
                home_votes += 1
            elif combined < -0.1:
                away_votes += 1
            else:
                draw_votes += 1
        
        total = home_votes + draw_votes + away_votes
        
        return ModelPrediction(
            home_win_prob=home_votes / total,
            draw_prob=draw_votes / total,
            away_win_prob=away_votes / total,
            confidence=0.70 + random.uniform(-0.05, 0.05),
            model_name="random_forest"
        )
    
    def predict_neural_network(
        self,
        features: np.ndarray
    ) -> ModelPrediction:
        """
        Simulated Neural Network prediction.
        """
        # Simulated hidden layer computation
        hidden = [
            self._sigmoid(features[0] * 0.5 + features[6] * 0.3 - features[7] * 0.2),
            self._sigmoid(features[2] * 0.5 + features[8] * 0.3 - features[9] * 0.2),
            self._sigmoid((features[4] - features[5]) * 0.02),
            self._sigmoid(features[20] - 0.3),
            self._sigmoid(features[22] - 0.3),
        ]
        
        # Output layer
        home_score = hidden[0] * 0.4 + hidden[2] * 0.3 + hidden[3] * 0.3
        away_score = hidden[1] * 0.4 - hidden[2] * 0.3 + hidden[4] * 0.3
        draw_score = 0.25 + (1 - abs(hidden[0] - hidden[1])) * 0.2
        
        probs = self._softmax([home_score, draw_score, away_score])
        
        return ModelPrediction(
            home_win_prob=probs[0],
            draw_prob=probs[1],
            away_win_prob=probs[2],
            confidence=0.68 + random.uniform(-0.05, 0.05),
            model_name="neural_network"
        )
    
    def predict_logistic_regression(
        self,
        features: np.ndarray
    ) -> ModelPrediction:
        """
        Simulated Logistic Regression prediction.
        """
        # Linear combination of features
        home_logit = (
            0.5 +
            features[0] * 0.3 +
            features[4] * 0.005 -
            features[3] * 0.2 +
            features[20] * 0.4
        )
        
        away_logit = (
            -0.2 +
            features[2] * 0.3 +
            features[5] * 0.005 -
            features[1] * 0.2 +
            features[22] * 0.4
        )
        
        draw_logit = (
            -0.5 +
            features[21] * 0.5 +
            (1 - abs(features[0] - features[2])) * 0.3
        )
        
        probs = self._softmax([home_logit, draw_logit, away_logit])
        
        return ModelPrediction(
            home_win_prob=probs[0],
            draw_prob=probs[1],
            away_win_prob=probs[2],
            confidence=0.65 + random.uniform(-0.05, 0.05),
            model_name="logistic_regression"
        )
    
    def ensemble_predict(
        self,
        home_stats: Dict,
        away_stats: Dict,
        h2h_data: Dict = None,
        league_stats: Dict = None,
        odds_data: Dict = None
    ) -> EnsemblePrediction:
        """
        Run ensemble prediction combining all models.
        """
        h2h_data = h2h_data or {}
        league_stats = league_stats or {}
        odds_data = odds_data or {}
        
        # Prepare features
        features = self.prepare_features(
            home_stats, away_stats, h2h_data, league_stats, odds_data
        )
        
        # Get predictions from each model
        predictions = {
            "xgboost": self.predict_xgboost(features),
            "random_forest": self.predict_random_forest(features),
            "neural_network": self.predict_neural_network(features),
            "logistic_regression": self.predict_logistic_regression(features)
        }
        
        # Weighted ensemble
        home_prob = 0
        draw_prob = 0
        away_prob = 0
        total_weight = 0
        
        model_contributions = {}
        
        for model_name, pred in predictions.items():
            weight = self.model_weights[model_name] * pred.confidence
            
            home_prob += pred.home_win_prob * weight
            draw_prob += pred.draw_prob * weight
            away_prob += pred.away_win_prob * weight
            total_weight += weight
            
            model_contributions[model_name] = weight
        
        # Normalize
        home_prob /= total_weight
        draw_prob /= total_weight
        away_prob /= total_weight
        
        # Ensure they sum to 1
        total = home_prob + draw_prob + away_prob
        home_prob /= total
        draw_prob /= total
        away_prob /= total
        
        # Ensemble confidence is weighted average of model confidences
        avg_confidence = sum(
            p.confidence * self.model_weights[m]
            for m, p in predictions.items()
        )
        
        return EnsemblePrediction(
            home_win_prob=round(home_prob * 100, 2),
            draw_prob=round(draw_prob * 100, 2),
            away_win_prob=round(away_prob * 100, 2),
            confidence=round(avg_confidence, 2),
            model_contributions={
                k: round(v / total_weight * 100, 2)
                for k, v in model_contributions.items()
            },
            feature_importance=self.feature_importance
        )
    
    def get_model_performance_metrics(self) -> Dict[str, Dict]:
        """
        Return simulated model performance metrics.
        """
        return {
            "xgboost": {
                "accuracy": 0.52,
                "log_loss": 0.98,
                "brier_score": 0.21,
                "roi": 3.2
            },
            "random_forest": {
                "accuracy": 0.50,
                "log_loss": 1.01,
                "brier_score": 0.22,
                "roi": 1.8
            },
            "neural_network": {
                "accuracy": 0.49,
                "log_loss": 1.03,
                "brier_score": 0.23,
                "roi": 0.5
            },
            "logistic_regression": {
                "accuracy": 0.47,
                "log_loss": 1.05,
                "brier_score": 0.24,
                "roi": -1.2
            },
            "ensemble": {
                "accuracy": 0.54,
                "log_loss": 0.95,
                "brier_score": 0.20,
                "roi": 4.5
            }
        }
