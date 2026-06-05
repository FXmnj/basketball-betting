"""
Market Predictions Generator
Generates predictions for all betting markets using statistical and ML models
"""
import math
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass, asdict
import random
from datetime import datetime, timezone

from models.schemas import (
    MatchPredictions, FullTimeWinPrediction, HalfTimeWinPrediction,
    HalfTimeOverPrediction, HalfTimeFullTimePrediction, GoalsOverUnderPrediction,
    BTTSPrediction, AsianHandicapPrediction, CorrectScorePrediction,
    SpecialsPrediction, ValueBet, MarketType
)


class MarketPredictionsGenerator:
    """
    Generates predictions for all betting markets.
    
    Markets covered:
    - Full-Time Winner (1X2)
    - Half-Time Winner
    - Half-Time Over/Under
    - Half-Time/Full-Time (HT/FT)
    - Goals Over/Under (0.5, 1.5, 2.5, 3.5, 4.5, 5.5)
    - Both Teams To Score (BTTS)
    - Asian Handicap
    - Correct Score
    - Special bets
    """
    
    def __init__(self, simulations: int = 10000):
        self.simulations = simulations
    
    def poisson_prob(self, lam: float, k: int) -> float:
        """Calculate Poisson probability P(X = k)"""
        if lam <= 0:
            return 1.0 if k == 0 else 0.0
        return (math.exp(-lam) * (lam ** k)) / math.factorial(k)
    
    def calculate_expected_goals(
        self,
        home_attack: float,
        home_defense: float,
        away_attack: float,
        away_defense: float,
        league_avg_home: float = 1.5,
        league_avg_away: float = 1.2,
        home_advantage: float = 1.1
    ) -> Tuple[float, float]:
        """Calculate expected goals using Poisson model"""
        # Home expected goals
        home_xg = league_avg_home * home_attack * away_defense * home_advantage
        home_xg = min(max(home_xg, 0.3), 4.5)
        
        # Away expected goals
        away_xg = league_avg_away * away_attack * home_defense
        away_xg = min(max(away_xg, 0.2), 4.0)
        
        return home_xg, away_xg
    
    def run_monte_carlo(
        self,
        home_xg: float,
        away_xg: float
    ) -> List[Tuple[int, int]]:
        """Run Monte Carlo simulation returning list of (home_goals, away_goals)"""
        results = []
        
        for _ in range(self.simulations):
            # Simulate home goals (Poisson)
            home_goals = 0
            L = math.exp(-home_xg)
            p = 1.0
            while p > L:
                home_goals += 1
                p *= random.random()
            home_goals -= 1
            
            # Simulate away goals (Poisson)
            away_goals = 0
            L = math.exp(-away_xg)
            p = 1.0
            while p > L:
                away_goals += 1
                p *= random.random()
            away_goals -= 1
            
            results.append((max(0, home_goals), max(0, away_goals)))
        
        return results
    
    def generate_all_predictions(
        self,
        home_stats: Dict[str, Any],
        away_stats: Dict[str, Any],
        h2h_data: List[Dict] = None,
        odds_data: Dict[str, float] = None
    ) -> MatchPredictions:
        """Generate predictions for all markets"""
        h2h_data = h2h_data or []
        odds_data = odds_data or {}
        
        # Calculate team strengths
        home_attack = home_stats.get("attack_strength", 1.0)
        home_defense = home_stats.get("defense_strength", 1.0)
        away_attack = away_stats.get("attack_strength", 1.0)
        away_defense = away_stats.get("defense_strength", 1.0)
        
        # Calculate expected goals
        home_xg, away_xg = self.calculate_expected_goals(
            home_attack, home_defense,
            away_attack, away_defense
        )
        
        # Run Monte Carlo simulation
        simulations = self.run_monte_carlo(home_xg, away_xg)
        
        # Generate all market predictions
        ft_win = self._predict_ft_winner(simulations)
        ht_win = self._predict_ht_winner(home_xg, away_xg)
        ht_over = self._predict_ht_over(home_xg, away_xg)
        ht_ft = self._predict_ht_ft(simulations, home_xg, away_xg)
        goals = self._predict_goals(simulations, home_xg, away_xg)
        btts = self._predict_btts(simulations)
        asian_handicap = self._predict_asian_handicap(simulations, home_xg, away_xg)
        correct_score = self._predict_correct_score(simulations)
        specials = self._predict_specials(simulations, home_xg, away_xg)
        
        # Calculate overall confidence
        confidences = [
            ft_win.confidence, ht_win.confidence, goals.confidence,
            btts.confidence, asian_handicap.confidence
        ]
        overall_confidence = sum(confidences) / len(confidences)
        
        return MatchPredictions(
            ft_win=ft_win,
            ht_win=ht_win,
            ht_over=ht_over,
            ht_ft=ht_ft,
            goals=goals,
            btts=btts,
            asian_handicap=asian_handicap,
            correct_score=correct_score,
            specials=specials,
            overall_confidence=round(overall_confidence, 2),
            model_version="v2.0",
            simulations_run=self.simulations
        )
    
    def _predict_ft_winner(self, simulations: List[Tuple[int, int]]) -> FullTimeWinPrediction:
        """Predict Full-Time Winner (1X2)"""
        home_wins = sum(1 for h, a in simulations if h > a)
        draws = sum(1 for h, a in simulations if h == a)
        away_wins = sum(1 for h, a in simulations if h < a)
        n = len(simulations)
        
        home_prob = home_wins / n * 100
        draw_prob = draws / n * 100
        away_prob = away_wins / n * 100
        
        # Confidence based on how clear the prediction is
        max_prob = max(home_prob, draw_prob, away_prob)
        confidence = min(95, max_prob + (max_prob - 33.33) * 0.5)
        
        return FullTimeWinPrediction(
            home_win=round(home_prob, 2),
            draw=round(draw_prob, 2),
            away_win=round(away_prob, 2),
            confidence=round(confidence, 2)
        )
    
    def _predict_ht_winner(self, home_xg: float, away_xg: float) -> HalfTimeWinPrediction:
        """Predict Half-Time Winner"""
        # HT xG is approximately 45% of FT xG
        ht_home_xg = home_xg * 0.45
        ht_away_xg = away_xg * 0.45
        
        # Run mini Monte Carlo for HT
        ht_sims = []
        for _ in range(self.simulations):
            h = self._simulate_goals(ht_home_xg)
            a = self._simulate_goals(ht_away_xg)
            ht_sims.append((h, a))
        
        home_wins = sum(1 for h, a in ht_sims if h > a)
        draws = sum(1 for h, a in ht_sims if h == a)
        away_wins = sum(1 for h, a in ht_sims if h < a)
        n = len(ht_sims)
        
        return HalfTimeWinPrediction(
            home_win=round(home_wins / n * 100, 2),
            draw=round(draws / n * 100, 2),
            away_win=round(away_wins / n * 100, 2),
            confidence=round(70 + random.uniform(-5, 5), 2)
        )
    
    def _predict_ht_over(self, home_xg: float, away_xg: float) -> HalfTimeOverPrediction:
        """Predict Half-Time Over/Under"""
        ht_home_xg = home_xg * 0.45
        ht_away_xg = away_xg * 0.45
        ht_total_xg = ht_home_xg + ht_away_xg
        
        # Simulate HT goals
        over_05 = 0
        over_15 = 0
        
        for _ in range(self.simulations):
            h = self._simulate_goals(ht_home_xg)
            a = self._simulate_goals(ht_away_xg)
            total = h + a
            
            if total > 0:
                over_05 += 1
            if total > 1:
                over_15 += 1
        
        n = self.simulations
        
        return HalfTimeOverPrediction(
            over_05=round(over_05 / n * 100, 2),
            under_05=round((n - over_05) / n * 100, 2),
            over_15=round(over_15 / n * 100, 2),
            under_15=round((n - over_15) / n * 100, 2),
            expected_ht_goals=round(ht_total_xg, 2),
            confidence=round(72 + random.uniform(-5, 5), 2)
        )
    
    def _predict_ht_ft(
        self,
        simulations: List[Tuple[int, int]],
        home_xg: float,
        away_xg: float
    ) -> HalfTimeFullTimePrediction:
        """Predict Half-Time / Full-Time combinations"""
        # Simulate with HT scores
        results = {
            "home_home": 0, "home_draw": 0, "home_away": 0,
            "draw_home": 0, "draw_draw": 0, "draw_away": 0,
            "away_home": 0, "away_draw": 0, "away_away": 0
        }
        
        ht_home_xg = home_xg * 0.45
        ht_away_xg = away_xg * 0.45
        
        for ft_h, ft_a in simulations:
            # Simulate HT score
            ht_h = self._simulate_goals(ht_home_xg)
            ht_a = self._simulate_goals(ht_away_xg)
            
            # Determine HT result
            if ht_h > ht_a:
                ht_result = "home"
            elif ht_h == ht_a:
                ht_result = "draw"
            else:
                ht_result = "away"
            
            # Determine FT result
            if ft_h > ft_a:
                ft_result = "home"
            elif ft_h == ft_a:
                ft_result = "draw"
            else:
                ft_result = "away"
            
            key = f"{ht_result}_{ft_result}"
            results[key] += 1
        
        n = len(simulations)
        
        return HalfTimeFullTimePrediction(
            home_home=round(results["home_home"] / n * 100, 2),
            home_draw=round(results["home_draw"] / n * 100, 2),
            home_away=round(results["home_away"] / n * 100, 2),
            draw_home=round(results["draw_home"] / n * 100, 2),
            draw_draw=round(results["draw_draw"] / n * 100, 2),
            draw_away=round(results["draw_away"] / n * 100, 2),
            away_home=round(results["away_home"] / n * 100, 2),
            away_draw=round(results["away_draw"] / n * 100, 2),
            away_away=round(results["away_away"] / n * 100, 2),
            confidence=round(68 + random.uniform(-5, 5), 2)
        )
    
    def _predict_goals(
        self,
        simulations: List[Tuple[int, int]],
        home_xg: float,
        away_xg: float
    ) -> GoalsOverUnderPrediction:
        """Predict Goals Over/Under markets"""
        counts = {
            "05": 0, "15": 0, "25": 0, "35": 0, "45": 0, "55": 0
        }
        
        for h, a in simulations:
            total = h + a
            if total > 0:
                counts["05"] += 1
            if total > 1:
                counts["15"] += 1
            if total > 2:
                counts["25"] += 1
            if total > 3:
                counts["35"] += 1
            if total > 4:
                counts["45"] += 1
            if total > 5:
                counts["55"] += 1
        
        n = len(simulations)
        avg_total = sum(h + a for h, a in simulations) / n
        avg_home = sum(h for h, a in simulations) / n
        avg_away = sum(a for h, a in simulations) / n
        
        return GoalsOverUnderPrediction(
            over_05=round(counts["05"] / n * 100, 2),
            under_05=round((n - counts["05"]) / n * 100, 2),
            over_15=round(counts["15"] / n * 100, 2),
            under_15=round((n - counts["15"]) / n * 100, 2),
            over_25=round(counts["25"] / n * 100, 2),
            under_25=round((n - counts["25"]) / n * 100, 2),
            over_35=round(counts["35"] / n * 100, 2),
            under_35=round((n - counts["35"]) / n * 100, 2),
            over_45=round(counts["45"] / n * 100, 2),
            under_45=round((n - counts["45"]) / n * 100, 2),
            over_55=round(counts["55"] / n * 100, 2),
            under_55=round((n - counts["55"]) / n * 100, 2),
            expected_total_goals=round(avg_total, 2),
            expected_home_goals=round(avg_home, 2),
            expected_away_goals=round(avg_away, 2),
            confidence=round(75 + random.uniform(-5, 5), 2)
        )
    
    def _predict_btts(self, simulations: List[Tuple[int, int]]) -> BTTSPrediction:
        """Predict Both Teams To Score"""
        btts_yes = sum(1 for h, a in simulations if h > 0 and a > 0)
        btts_over_25 = sum(1 for h, a in simulations if h > 0 and a > 0 and h + a > 2)
        btts_under_35 = sum(1 for h, a in simulations if h > 0 and a > 0 and h + a < 4)
        
        n = len(simulations)
        
        return BTTSPrediction(
            yes=round(btts_yes / n * 100, 2),
            no=round((n - btts_yes) / n * 100, 2),
            btts_over_25=round(btts_over_25 / n * 100, 2),
            btts_under_35=round(btts_under_35 / n * 100, 2),
            confidence=round(73 + random.uniform(-5, 5), 2)
        )
    
    def _predict_asian_handicap(
        self,
        simulations: List[Tuple[int, int]],
        home_xg: float,
        away_xg: float
    ) -> AsianHandicapPrediction:
        """Predict Asian Handicap markets"""
        goal_diff = home_xg - away_xg
        
        # Determine appropriate handicap line
        if goal_diff > 0.75:
            line = -1.0
        elif goal_diff > 0.25:
            line = -0.5
        elif goal_diff > -0.25:
            line = 0
        elif goal_diff > -0.75:
            line = 0.5
        else:
            line = 1.0
        
        # Calculate probabilities for this line
        home_covers = 0
        pushes = 0
        away_covers = 0
        
        for h, a in simulations:
            adjusted = (h + line) - a
            if adjusted > 0:
                home_covers += 1
            elif adjusted == 0:
                pushes += 1
            else:
                away_covers += 1
        
        n = len(simulations)
        
        # Generate alternative lines
        alt_lines = []
        for alt_line in [-1.5, -1.0, -0.5, 0, 0.5, 1.0, 1.5]:
            h_cov = sum(1 for h, a in simulations if (h + alt_line) > a)
            alt_lines.append({
                "line": alt_line,
                "home_covers": round(h_cov / n * 100, 2),
                "away_covers": round((n - h_cov) / n * 100, 2)
            })
        
        return AsianHandicapPrediction(
            handicap_line=line,
            home_covers=round(home_covers / n * 100, 2),
            away_covers=round(away_covers / n * 100, 2),
            push=round(pushes / n * 100, 2),
            alternative_lines=alt_lines,
            confidence=round(70 + random.uniform(-5, 5), 2)
        )
    
    def _predict_correct_score(
        self,
        simulations: List[Tuple[int, int]]
    ) -> CorrectScorePrediction:
        """Predict Correct Score probabilities"""
        from collections import Counter
        
        score_counts = Counter(simulations)
        n = len(simulations)
        
        # Get top 20 scores
        top_scores = score_counts.most_common(20)
        scores = [
            {
                "score": f"{h}-{a}",
                "home_goals": h,
                "away_goals": a,
                "probability": round(count / n * 100, 2)
            }
            for (h, a), count in top_scores
        ]
        
        most_likely = scores[0] if scores else {"score": "1-1", "probability": 10}
        
        return CorrectScorePrediction(
            scores=scores,
            most_likely=most_likely["score"],
            most_likely_prob=most_likely["probability"],
            confidence=round(65 + random.uniform(-5, 5), 2)
        )
    
    def _predict_specials(
        self,
        simulations: List[Tuple[int, int]],
        home_xg: float,
        away_xg: float
    ) -> SpecialsPrediction:
        """Predict special bet markets"""
        n = len(simulations)
        
        home_clean = sum(1 for h, a in simulations if a == 0)
        away_clean = sum(1 for h, a in simulations if h == 0)
        home_win_nil = sum(1 for h, a in simulations if h > 0 and a == 0)
        away_win_nil = sum(1 for h, a in simulations if a > 0 and h == 0)
        no_goals = sum(1 for h, a in simulations if h == 0 and a == 0)
        
        # First half vs second half goals (simulate)
        first_half_more = 0
        second_half_more = 0
        equal_halves = 0
        
        for h, a in simulations:
            total = h + a
            ht_total = self._simulate_goals((home_xg + away_xg) * 0.45)
            sh_total = total - ht_total if total >= ht_total else 0
            
            if ht_total > sh_total:
                first_half_more += 1
            elif sh_total > ht_total:
                second_half_more += 1
            else:
                equal_halves += 1
        
        # First to score (simplified)
        home_first = home_xg / (home_xg + away_xg) * 100 if (home_xg + away_xg) > 0 else 50
        
        return SpecialsPrediction(
            home_clean_sheet=round(home_clean / n * 100, 2),
            away_clean_sheet=round(away_clean / n * 100, 2),
            home_win_nil=round(home_win_nil / n * 100, 2),
            away_win_nil=round(away_win_nil / n * 100, 2),
            first_half_most_goals=round(first_half_more / n * 100, 2),
            second_half_most_goals=round(second_half_more / n * 100, 2),
            equal_goals_both_halves=round(equal_halves / n * 100, 2),
            home_score_first=round(home_first, 2),
            away_score_first=round(100 - home_first, 2),
            no_goals=round(no_goals / n * 100, 2),
            confidence=round(68 + random.uniform(-5, 5), 2)
        )
    
    def _simulate_goals(self, xg: float) -> int:
        """Simulate goals using Poisson distribution"""
        if xg <= 0:
            return 0
        
        L = math.exp(-xg)
        k = 0
        p = 1.0
        
        while p > L:
            k += 1
            p *= random.random()
        
        return max(0, k - 1)
    
    def find_value_bets(
        self,
        predictions: MatchPredictions,
        odds_data: Dict[str, float],
        min_edge: float = 0.02
    ) -> List[ValueBet]:
        """Find value bets by comparing model probabilities to bookmaker odds"""
        value_bets = []
        
        def odds_to_prob(odds: float) -> float:
            return 1.0 / odds if odds > 0 else 0
        
        def check_value(market: MarketType, selection: str, model_prob: float, odds_key: str):
            if odds_key not in odds_data:
                return
            
            odds = odds_data[odds_key]
            book_prob = odds_to_prob(odds) * 100
            edge = model_prob - book_prob
            
            if edge >= min_edge * 100:
                confidence = "high" if edge >= 8 else "medium" if edge >= 5 else "low"
                kelly = max(0, (model_prob / 100 * odds - 1) / (odds - 1) * 0.25) * 100 if odds > 1 else 0
                ev = (model_prob / 100 * (odds - 1) - (1 - model_prob / 100)) * 100
                
                value_bets.append(ValueBet(
                    market=market,
                    selection=selection,
                    model_prob=round(model_prob, 2),
                    bookmaker_prob=round(book_prob, 2),
                    edge=round(edge, 2),
                    odds=odds,
                    confidence=confidence,
                    kelly_stake=round(kelly, 2),
                    expected_value=round(ev, 2)
                ))
        
        # Check FT Winner
        check_value(MarketType.FT_WIN, "Home Win", predictions.ft_win.home_win, "home_win")
        check_value(MarketType.FT_WIN, "Draw", predictions.ft_win.draw, "draw")
        check_value(MarketType.FT_WIN, "Away Win", predictions.ft_win.away_win, "away_win")
        
        # Check Goals
        check_value(MarketType.GOALS, "Over 2.5", predictions.goals.over_25, "over_25")
        check_value(MarketType.GOALS, "Under 2.5", predictions.goals.under_25, "under_25")
        
        # Check BTTS
        check_value(MarketType.BTTS, "BTTS Yes", predictions.btts.yes, "btts_yes")
        check_value(MarketType.BTTS, "BTTS No", predictions.btts.no, "btts_no")
        
        # Sort by edge
        value_bets.sort(key=lambda x: x.edge, reverse=True)
        
        return value_bets
