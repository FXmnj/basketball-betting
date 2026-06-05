"""
Enhanced Pydantic models for Football AI Prediction Platform
With separated prediction markets and proper date handling
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone, date
import uuid
from enum import Enum


# ==================== ENUMS ====================
class MatchStatus(str, Enum):
    SCHEDULED = "NS"
    LIVE = "LIVE"
    FIRST_HALF = "1H"
    HALFTIME = "HT"
    SECOND_HALF = "2H"
    FINISHED = "FT"
    POSTPONED = "PST"
    CANCELLED = "CANC"
    ABANDONED = "ABD"


class MarketType(str, Enum):
    FT_WIN = "ft_win"  # Full-Time Winner (1X2)
    HT_WIN = "ht_win"  # Half-Time Winner
    HT_OVER = "ht_over"  # Half-Time Over/Under
    HT_FT = "ht_ft"  # Half-Time/Full-Time
    GOALS = "goals"  # Goals Over/Under
    BTTS = "btts"  # Both Teams To Score
    ASIAN_HANDICAP = "asian_handicap"
    CORRECT_SCORE = "correct_score"
    SPECIALS = "specials"


# ==================== BASE MODELS ====================
class BaseDBModel(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# ==================== TEAM MODELS ====================
class TeamStats(BaseModel):
    played: int = 0
    wins: int = 0
    draws: int = 0
    losses: int = 0
    goals_for: int = 0
    goals_against: int = 0
    goal_difference: int = 0
    points: int = 0
    clean_sheets: int = 0
    xg_for: float = 0.0
    xg_against: float = 0.0
    home_wins: int = 0
    home_draws: int = 0
    home_losses: int = 0
    away_wins: int = 0
    away_draws: int = 0
    away_losses: int = 0


class TeamStrength(BaseModel):
    attack_home: float = 1.0
    attack_away: float = 1.0
    defense_home: float = 1.0
    defense_away: float = 1.0
    overall_rating: float = 50.0


class Team(BaseDBModel):
    name: str
    short_name: str
    logo_url: Optional[str] = None
    league_id: str
    league_name: str
    country: str
    stats: TeamStats = Field(default_factory=TeamStats)
    strength: TeamStrength = Field(default_factory=TeamStrength)
    form: str = ""
    external_id: Optional[str] = None


# ==================== PREDICTION MARKET MODELS ====================
class FullTimeWinPrediction(BaseModel):
    """1X2 - Full Time Winner"""
    home_win: float = 0.0
    draw: float = 0.0
    away_win: float = 0.0
    confidence: float = 0.0


class HalfTimeWinPrediction(BaseModel):
    """Half-Time Winner"""
    home_win: float = 0.0
    draw: float = 0.0
    away_win: float = 0.0
    confidence: float = 0.0


class HalfTimeOverPrediction(BaseModel):
    """Half-Time Over/Under"""
    over_05: float = 0.0
    under_05: float = 0.0
    over_15: float = 0.0
    under_15: float = 0.0
    expected_ht_goals: float = 0.0
    confidence: float = 0.0


class HalfTimeFullTimePrediction(BaseModel):
    """HT/FT - Half-Time / Full-Time Result"""
    home_home: float = 0.0  # Home leading at HT, Home wins
    home_draw: float = 0.0  # Home leading at HT, Draw at FT
    home_away: float = 0.0  # Home leading at HT, Away wins
    draw_home: float = 0.0  # Draw at HT, Home wins
    draw_draw: float = 0.0  # Draw at HT, Draw at FT
    draw_away: float = 0.0  # Draw at HT, Away wins
    away_home: float = 0.0  # Away leading at HT, Home wins
    away_draw: float = 0.0  # Away leading at HT, Draw at FT
    away_away: float = 0.0  # Away leading at HT, Away wins
    confidence: float = 0.0


class GoalsOverUnderPrediction(BaseModel):
    """Goals Over/Under Markets"""
    over_05: float = 0.0
    under_05: float = 0.0
    over_15: float = 0.0
    under_15: float = 0.0
    over_25: float = 0.0
    under_25: float = 0.0
    over_35: float = 0.0
    under_35: float = 0.0
    over_45: float = 0.0
    under_45: float = 0.0
    over_55: float = 0.0
    under_55: float = 0.0
    expected_total_goals: float = 0.0
    expected_home_goals: float = 0.0
    expected_away_goals: float = 0.0
    confidence: float = 0.0


class BTTSPrediction(BaseModel):
    """Both Teams To Score"""
    yes: float = 0.0
    no: float = 0.0
    btts_over_25: float = 0.0  # BTTS & Over 2.5
    btts_under_35: float = 0.0  # BTTS & Under 3.5
    confidence: float = 0.0


class AsianHandicapPrediction(BaseModel):
    """Asian Handicap Markets"""
    handicap_line: float = 0.0
    home_covers: float = 0.0
    away_covers: float = 0.0
    push: float = 0.0
    alternative_lines: List[Dict[str, Any]] = []
    confidence: float = 0.0


class CorrectScorePrediction(BaseModel):
    """Correct Score Probabilities"""
    scores: List[Dict[str, Any]] = []  # [{"score": "2-1", "probability": 12.5}, ...]
    most_likely: str = "1-1"
    most_likely_prob: float = 0.0
    confidence: float = 0.0


class SpecialsPrediction(BaseModel):
    """Other Special Bets"""
    home_clean_sheet: float = 0.0
    away_clean_sheet: float = 0.0
    home_win_nil: float = 0.0
    away_win_nil: float = 0.0
    first_half_most_goals: float = 0.0
    second_half_most_goals: float = 0.0
    equal_goals_both_halves: float = 0.0
    home_score_first: float = 0.0
    away_score_first: float = 0.0
    no_goals: float = 0.0
    confidence: float = 0.0


# ==================== FULL PREDICTION MODEL ====================
class MatchPredictions(BaseModel):
    """Complete prediction for all markets"""
    ft_win: FullTimeWinPrediction = Field(default_factory=FullTimeWinPrediction)
    ht_win: HalfTimeWinPrediction = Field(default_factory=HalfTimeWinPrediction)
    ht_over: HalfTimeOverPrediction = Field(default_factory=HalfTimeOverPrediction)
    ht_ft: HalfTimeFullTimePrediction = Field(default_factory=HalfTimeFullTimePrediction)
    goals: GoalsOverUnderPrediction = Field(default_factory=GoalsOverUnderPrediction)
    btts: BTTSPrediction = Field(default_factory=BTTSPrediction)
    asian_handicap: AsianHandicapPrediction = Field(default_factory=AsianHandicapPrediction)
    correct_score: CorrectScorePrediction = Field(default_factory=CorrectScorePrediction)
    specials: SpecialsPrediction = Field(default_factory=SpecialsPrediction)
    overall_confidence: float = 0.0
    model_version: str = "v2.0"
    simulations_run: int = 10000


# ==================== VALUE BET MODEL ====================
class ValueBet(BaseModel):
    market: MarketType
    selection: str
    model_prob: float
    bookmaker_prob: float
    edge: float
    odds: float
    confidence: str  # "high", "medium", "low"
    kelly_stake: float = 0.0
    expected_value: float = 0.0


# ==================== MATCH MODEL ====================
class Match(BaseDBModel):
    # Core match info
    external_id: str  # API-Football fixture ID
    home_team_id: str
    home_team_name: str
    home_team_logo: Optional[str] = None
    away_team_id: str
    away_team_name: str
    away_team_logo: Optional[str] = None
    
    # League info
    league_id: str
    league_name: str
    league_logo: Optional[str] = None
    country: str
    season: str = "2024"
    
    # Date/Time - IMPORTANT for filtering
    match_date: date  # Date only (for filtering today's matches)
    kickoff: datetime  # Full datetime
    timezone: str = "UTC"
    
    # Status
    status: MatchStatus = MatchStatus.SCHEDULED
    elapsed_time: Optional[int] = None
    
    # Scores (for live/finished matches)
    home_score: Optional[int] = None
    away_score: Optional[int] = None
    ht_home_score: Optional[int] = None
    ht_away_score: Optional[int] = None
    
    # Team form
    home_form: str = ""
    away_form: str = ""
    
    # Venue
    venue_name: Optional[str] = None
    venue_city: Optional[str] = None


# ==================== PREDICTION RECORD ====================
class PredictionRecord(BaseDBModel):
    """Stored prediction with date tracking"""
    match_id: str  # Reference to Match.id
    external_match_id: str  # API-Football fixture ID
    match_date: date
    date_generated: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    # All market predictions
    predictions: MatchPredictions = Field(default_factory=MatchPredictions)
    
    # Value bets identified
    value_bets: List[ValueBet] = []
    
    # AI Analysis (optional)
    ai_analysis: Optional[str] = None
    ai_insights: List[str] = []
    
    # Metadata
    data_quality: str = "complete"  # "complete", "partial", "limited"
    is_stale: bool = False


# ==================== LEAGUE MODEL ====================
class League(BaseDBModel):
    external_id: str
    name: str
    country: str
    logo_url: Optional[str] = None
    flag_url: Optional[str] = None
    season: str = "2024"
    is_active: bool = True
    priority: int = 0  # Higher = more important


# ==================== API RESPONSE MODELS ====================
class DailyMatchResponse(BaseModel):
    """Response for /api/daily-matches"""
    date: str
    total_matches: int
    matches: List[Dict[str, Any]]
    leagues: List[str]


class DailyPredictionResponse(BaseModel):
    """Response for /api/daily-predictions"""
    date: str
    total_predictions: int
    last_updated: str
    predictions: List[Dict[str, Any]]


class MarketPredictionResponse(BaseModel):
    """Response grouped by market type"""
    market_type: MarketType
    market_name: str
    predictions: List[Dict[str, Any]]


class MatchDetailResponse(BaseModel):
    """Full match detail with all predictions"""
    match: Dict[str, Any]
    predictions: Dict[str, Any]
    value_bets: List[Dict[str, Any]]
    ai_analysis: Optional[str]


# ==================== REQUEST MODELS ====================
class GeneratePredictionsRequest(BaseModel):
    match_ids: Optional[List[str]] = None
    force_refresh: bool = False


class AIAnalysisRequest(BaseModel):
    match_id: str
    include_stats: bool = True
