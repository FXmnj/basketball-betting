"""
Player Impact Model
Calculates how individual players affect team performance
"""
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import math


@dataclass
class PlayerImpact:
    player_id: str
    player_name: str
    position: str
    impact_score: float
    attack_impact: float
    defense_impact: float
    creativity_impact: float
    is_key_player: bool


@dataclass
class TeamAdjustment:
    attack_adjustment: float
    defense_adjustment: float
    overall_adjustment: float
    missing_players: List[str]
    reasoning: str


class PlayerImpactModel:
    """
    Model to calculate player impact on team performance.
    
    Uses player statistics to determine how much a team's
    attack and defense ratings change with/without specific players.
    """
    
    def __init__(self):
        # Position weights for different impact types
        self.position_attack_weights = {
            "forward": 0.9,
            "attacking_mid": 0.7,
            "winger": 0.6,
            "central_mid": 0.4,
            "defensive_mid": 0.2,
            "fullback": 0.3,
            "centerback": 0.1,
            "goalkeeper": 0.0
        }
        
        self.position_defense_weights = {
            "forward": 0.1,
            "attacking_mid": 0.2,
            "winger": 0.3,
            "central_mid": 0.4,
            "defensive_mid": 0.7,
            "fullback": 0.6,
            "centerback": 0.9,
            "goalkeeper": 0.95
        }
        
        # Stat importance weights
        self.attack_stat_weights = {
            "goals": 0.35,
            "assists": 0.25,
            "xg": 0.20,
            "xa": 0.10,
            "shots_on_target": 0.05,
            "key_passes": 0.05
        }
        
        self.defense_stat_weights = {
            "tackles": 0.25,
            "interceptions": 0.25,
            "clean_sheets": 0.20,
            "blocks": 0.15,
            "clearances": 0.10,
            "saves": 0.05
        }
    
    def normalize_position(self, position: str) -> str:
        """Normalize position string to standard format"""
        position = position.lower().strip()
        
        position_map = {
            "st": "forward", "cf": "forward", "striker": "forward",
            "lw": "winger", "rw": "winger", "winger": "winger",
            "cam": "attacking_mid", "am": "attacking_mid",
            "cm": "central_mid", "midfielder": "central_mid",
            "cdm": "defensive_mid", "dm": "defensive_mid",
            "lb": "fullback", "rb": "fullback", "wb": "fullback",
            "cb": "centerback", "defender": "centerback",
            "gk": "goalkeeper", "keeper": "goalkeeper"
        }
        
        return position_map.get(position, "central_mid")
    
    def calculate_player_impact(
        self,
        player_stats: Dict,
        team_stats: Dict,
        position: str
    ) -> PlayerImpact:
        """
        Calculate individual player's impact score.
        
        Args:
            player_stats: Player's statistics
            team_stats: Team's overall statistics
            position: Player's position
        """
        norm_position = self.normalize_position(position)
        
        # Calculate attack impact
        attack_impact = 0.0
        for stat, weight in self.attack_stat_weights.items():
            player_val = player_stats.get(stat, 0)
            team_val = team_stats.get(f"total_{stat}", 1)
            if team_val > 0:
                contribution = player_val / team_val
                attack_impact += contribution * weight
        
        attack_impact *= self.position_attack_weights.get(norm_position, 0.5)
        
        # Calculate defense impact
        defense_impact = 0.0
        for stat, weight in self.defense_stat_weights.items():
            player_val = player_stats.get(stat, 0)
            team_val = team_stats.get(f"total_{stat}", 1)
            if team_val > 0:
                contribution = player_val / team_val
                defense_impact += contribution * weight
        
        defense_impact *= self.position_defense_weights.get(norm_position, 0.5)
        
        # Creativity impact (assists + key passes)
        creativity_impact = (
            player_stats.get("assists", 0) * 0.5 +
            player_stats.get("key_passes", 0) * 0.02 +
            player_stats.get("xa", 0) * 0.3
        )
        
        # Overall impact score (0-100 scale)
        minutes_factor = min(1.0, player_stats.get("minutes_played", 0) / 2500)
        overall_impact = (
            (attack_impact * 0.4 + defense_impact * 0.4 + creativity_impact * 0.2) *
            100 * minutes_factor
        )
        
        is_key_player = overall_impact > 15 or attack_impact > 0.25 or defense_impact > 0.25
        
        return PlayerImpact(
            player_id=player_stats.get("id", ""),
            player_name=player_stats.get("name", "Unknown"),
            position=norm_position,
            impact_score=round(overall_impact, 2),
            attack_impact=round(attack_impact, 3),
            defense_impact=round(defense_impact, 3),
            creativity_impact=round(creativity_impact, 3),
            is_key_player=is_key_player
        )
    
    def calculate_team_adjustment(
        self,
        missing_players: List[PlayerImpact],
        returning_players: List[PlayerImpact],
        base_attack: float = 1.0,
        base_defense: float = 1.0
    ) -> TeamAdjustment:
        """
        Calculate team strength adjustment based on missing/returning players.
        """
        attack_adjustment = 0.0
        defense_adjustment = 0.0
        missing_names = []
        
        # Subtract impact of missing players
        for player in missing_players:
            attack_adjustment -= player.attack_impact * 0.5
            defense_adjustment -= player.defense_impact * 0.5
            missing_names.append(player.player_name)
        
        # Add impact of returning players
        for player in returning_players:
            attack_adjustment += player.attack_impact * 0.4
            defense_adjustment += player.defense_impact * 0.4
        
        # Apply adjustments
        adjusted_attack = base_attack * (1 + attack_adjustment)
        adjusted_defense = base_defense * (1 - defense_adjustment)  # Lower is better for defense
        
        # Cap adjustments
        adjusted_attack = max(0.5, min(1.5, adjusted_attack))
        adjusted_defense = max(0.5, min(1.5, adjusted_defense))
        
        overall_adjustment = (adjusted_attack / base_attack + adjusted_defense / base_defense) / 2
        
        reasoning = ""
        if missing_players:
            key_missing = [p.player_name for p in missing_players if p.is_key_player]
            if key_missing:
                reasoning = f"Missing key players: {', '.join(key_missing[:3])}"
            else:
                reasoning = f"Missing {len(missing_players)} player(s)"
        
        return TeamAdjustment(
            attack_adjustment=round(adjusted_attack / base_attack, 3),
            defense_adjustment=round(adjusted_defense / base_defense, 3),
            overall_adjustment=round(overall_adjustment, 3),
            missing_players=missing_names,
            reasoning=reasoning
        )
    
    def rank_players_by_impact(
        self,
        players: List[PlayerImpact]
    ) -> List[PlayerImpact]:
        """Rank players by their impact score"""
        return sorted(players, key=lambda p: p.impact_score, reverse=True)
    
    def get_key_players(
        self,
        players: List[PlayerImpact],
        top_n: int = 5
    ) -> List[PlayerImpact]:
        """Get top N most impactful players"""
        ranked = self.rank_players_by_impact(players)
        return ranked[:top_n]
    
    def calculate_lineup_strength(
        self,
        lineup_players: List[PlayerImpact],
        all_squad_players: List[PlayerImpact]
    ) -> Dict[str, float]:
        """
        Calculate lineup strength compared to full squad.
        """
        if not all_squad_players:
            return {"lineup_strength": 1.0, "attack_strength": 1.0, "defense_strength": 1.0}
        
        total_squad_impact = sum(p.impact_score for p in all_squad_players)
        lineup_impact = sum(p.impact_score for p in lineup_players)
        
        total_squad_attack = sum(p.attack_impact for p in all_squad_players)
        lineup_attack = sum(p.attack_impact for p in lineup_players)
        
        total_squad_defense = sum(p.defense_impact for p in all_squad_players)
        lineup_defense = sum(p.defense_impact for p in lineup_players)
        
        return {
            "lineup_strength": round(lineup_impact / max(total_squad_impact, 1), 3),
            "attack_strength": round(lineup_attack / max(total_squad_attack, 1), 3),
            "defense_strength": round(lineup_defense / max(total_squad_defense, 1), 3)
        }
    
    def estimate_player_impact_without_data(
        self,
        position: str,
        is_regular_starter: bool,
        is_captain: bool = False,
        is_top_scorer: bool = False
    ) -> float:
        """
        Estimate player impact when detailed stats aren't available.
        """
        norm_position = self.normalize_position(position)
        
        # Base impact by position
        position_base = {
            "forward": 0.20,
            "attacking_mid": 0.18,
            "winger": 0.15,
            "central_mid": 0.14,
            "defensive_mid": 0.16,
            "fullback": 0.12,
            "centerback": 0.17,
            "goalkeeper": 0.20
        }
        
        base = position_base.get(norm_position, 0.15)
        
        if is_regular_starter:
            base *= 1.3
        if is_captain:
            base *= 1.2
        if is_top_scorer:
            base *= 1.4
        
        return round(min(0.5, base), 3)
