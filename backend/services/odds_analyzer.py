"""
Odds Movement Analysis
Tracks bookmaker odds and detects value bets and sharp money
"""
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timezone
import math


@dataclass
class OddsMovement:
    market: str
    opening_odds: float
    current_odds: float
    change_percent: float
    direction: str  # "shortening", "drifting", "stable"
    is_sharp_move: bool


@dataclass
class ValueBetResult:
    market: str
    selection: str
    model_prob: float
    bookmaker_prob: float
    edge: float
    odds: float
    confidence: str
    kelly_stake: float
    expected_value: float


class OddsAnalyzer:
    """
    Analyzes bookmaker odds to detect value bets and market movements.
    
    Features:
    - Track odds movement over time
    - Detect sharp money (informed betting)
    - Identify value bets (edge over bookmaker)
    - Calculate Kelly criterion stakes
    """
    
    def __init__(self):
        # Minimum edge thresholds for different confidence levels
        self.edge_thresholds = {
            "high": 0.08,     # 8%+ edge
            "medium": 0.05,   # 5-8% edge
            "low": 0.02       # 2-5% edge
        }
        
        # Bookmaker margin estimation
        self.typical_margin = 0.05  # 5% overround
        
        # Sharp movement threshold
        self.sharp_threshold = 0.10  # 10% probability change
    
    def odds_to_probability(self, odds: float) -> float:
        """Convert decimal odds to implied probability"""
        if odds <= 1:
            return 1.0
        return 1 / odds
    
    def probability_to_odds(self, prob: float) -> float:
        """Convert probability to decimal odds"""
        if prob <= 0:
            return 100.0
        return 1 / prob
    
    def calculate_overround(self, odds: Dict[str, float]) -> float:
        """
        Calculate bookmaker overround (margin).
        
        Overround = sum of implied probabilities - 1
        """
        total_prob = sum(
            self.odds_to_probability(o)
            for o in odds.values()
        )
        return total_prob - 1
    
    def remove_margin(
        self,
        odds: Dict[str, float],
        method: str = "multiplicative"
    ) -> Dict[str, float]:
        """
        Remove bookmaker margin to get true probabilities.
        """
        implied_probs = {
            k: self.odds_to_probability(v)
            for k, v in odds.items()
        }
        
        total = sum(implied_probs.values())
        
        if method == "multiplicative":
            # Equal margin distribution
            true_probs = {
                k: v / total
                for k, v in implied_probs.items()
            }
        else:
            # Simple normalization
            true_probs = implied_probs
        
        return true_probs
    
    def analyze_odds_movement(
        self,
        opening_odds: Dict[str, float],
        current_odds: Dict[str, float]
    ) -> List[OddsMovement]:
        """
        Analyze odds movement between opening and current.
        """
        movements = []
        
        for market in opening_odds:
            if market not in current_odds:
                continue
            
            open_prob = self.odds_to_probability(opening_odds[market])
            curr_prob = self.odds_to_probability(current_odds[market])
            
            change_percent = (curr_prob - open_prob) / max(open_prob, 0.01)
            
            if change_percent > 0.02:
                direction = "shortening"
            elif change_percent < -0.02:
                direction = "drifting"
            else:
                direction = "stable"
            
            is_sharp = abs(change_percent) >= self.sharp_threshold
            
            movements.append(OddsMovement(
                market=market,
                opening_odds=opening_odds[market],
                current_odds=current_odds[market],
                change_percent=round(change_percent * 100, 2),
                direction=direction,
                is_sharp_move=is_sharp
            ))
        
        return movements
    
    def detect_sharp_money(
        self,
        movements: List[OddsMovement]
    ) -> Optional[str]:
        """
        Detect if there's sharp money movement in the market.
        
        Returns the market direction if sharp money is detected.
        """
        sharp_moves = [m for m in movements if m.is_sharp_move]
        
        if not sharp_moves:
            return None
        
        # Find the strongest sharp move
        strongest = max(sharp_moves, key=lambda m: abs(m.change_percent))
        
        if strongest.direction == "shortening":
            return f"Sharp money on {strongest.market}"
        elif strongest.direction == "drifting":
            return f"Sharp money against {strongest.market}"
        
        return None
    
    def find_value_bets(
        self,
        model_probs: Dict[str, float],
        bookmaker_odds: Dict[str, float],
        min_edge: float = 0.02
    ) -> List[ValueBetResult]:
        """
        Find value bets by comparing model probabilities to bookmaker odds.
        
        Value bet = model_prob > bookmaker_implied_prob + margin
        """
        value_bets = []
        
        # Remove margin from bookmaker odds
        true_book_probs = self.remove_margin(bookmaker_odds)
        
        for market, model_prob in model_probs.items():
            if market not in bookmaker_odds:
                continue
            
            book_prob = true_book_probs.get(market, 0)
            odds = bookmaker_odds[market]
            
            # Calculate edge
            edge = model_prob - book_prob
            
            if edge < min_edge:
                continue
            
            # Determine confidence level
            if edge >= self.edge_thresholds["high"]:
                confidence = "high"
            elif edge >= self.edge_thresholds["medium"]:
                confidence = "medium"
            else:
                confidence = "low"
            
            # Calculate Kelly criterion stake
            kelly = self.kelly_criterion(model_prob, odds)
            
            # Expected value
            ev = (model_prob * (odds - 1)) - (1 - model_prob)
            
            # Market name to selection
            selection_map = {
                "home_win": "Home Win",
                "draw": "Draw",
                "away_win": "Away Win",
                "over_25": "Over 2.5 Goals",
                "under_25": "Under 2.5 Goals",
                "btts_yes": "Both Teams to Score",
                "btts_no": "Both Teams Not to Score"
            }
            
            value_bets.append(ValueBetResult(
                market=market,
                selection=selection_map.get(market, market),
                model_prob=round(model_prob * 100, 2),
                bookmaker_prob=round(book_prob * 100, 2),
                edge=round(edge * 100, 2),
                odds=odds,
                confidence=confidence,
                kelly_stake=round(kelly * 100, 2),
                expected_value=round(ev * 100, 2)
            ))
        
        # Sort by edge (highest first)
        value_bets.sort(key=lambda x: x.edge, reverse=True)
        
        return value_bets
    
    def kelly_criterion(
        self,
        prob: float,
        odds: float,
        fraction: float = 0.25
    ) -> float:
        """
        Calculate Kelly criterion stake.
        
        Kelly % = (bp - q) / b
        where:
            b = decimal odds - 1
            p = probability of winning
            q = probability of losing (1 - p)
        
        Args:
            prob: Estimated probability of winning
            odds: Decimal odds
            fraction: Fraction of Kelly to use (0.25 = quarter Kelly)
        """
        if odds <= 1 or prob <= 0 or prob >= 1:
            return 0
        
        b = odds - 1
        q = 1 - prob
        
        kelly = (b * prob - q) / b
        
        # Cap and apply fraction
        kelly = max(0, min(0.5, kelly * fraction))
        
        return kelly
    
    def calculate_expected_roi(
        self,
        value_bets: List[ValueBetResult],
        bankroll: float = 1000
    ) -> Dict[str, float]:
        """
        Calculate expected ROI from a set of value bets.
        """
        if not value_bets:
            return {"expected_roi": 0, "total_stake": 0, "expected_profit": 0}
        
        total_stake = 0
        expected_profit = 0
        
        for bet in value_bets:
            stake = bankroll * (bet.kelly_stake / 100)
            total_stake += stake
            expected_profit += stake * (bet.expected_value / 100)
        
        roi = expected_profit / total_stake if total_stake > 0 else 0
        
        return {
            "expected_roi": round(roi * 100, 2),
            "total_stake": round(total_stake, 2),
            "expected_profit": round(expected_profit, 2)
        }
    
    def compare_bookmakers(
        self,
        bookmaker_odds: Dict[str, Dict[str, float]]
    ) -> Dict[str, Dict]:
        """
        Compare odds across multiple bookmakers to find best prices.
        
        Args:
            bookmaker_odds: {bookmaker_name: {market: odds}}
        """
        best_odds = {}
        
        for bookmaker, odds in bookmaker_odds.items():
            for market, odd in odds.items():
                if market not in best_odds or odd > best_odds[market]["odds"]:
                    best_odds[market] = {
                        "odds": odd,
                        "bookmaker": bookmaker,
                        "implied_prob": round(self.odds_to_probability(odd) * 100, 2)
                    }
        
        return best_odds
    
    def get_fair_odds(
        self,
        model_probs: Dict[str, float]
    ) -> Dict[str, float]:
        """
        Calculate fair odds based on model probabilities.
        """
        return {
            market: round(self.probability_to_odds(prob), 2)
            for market, prob in model_probs.items()
            if prob > 0
        }
