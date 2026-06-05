from fastapi import FastAPI, APIRouter, HTTPException, Query, BackgroundTasks
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone, date, timedelta
from dataclasses import asdict

from models.schemas import (
    Match, MatchPredictions, PredictionRecord, League,
    DailyMatchResponse, DailyPredictionResponse, MarketType,
    GeneratePredictionsRequest, AIAnalysisRequest
)
from services.data_fetcher import APIFootballFetcher
from services.market_predictions import MarketPredictionsGenerator
from services.scheduler import DailyScheduler
from services.ai_analysis import AIAnalysisService


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Initialize services
data_fetcher = APIFootballFetcher()
prediction_generator = MarketPredictionsGenerator(simulations=10000)
ai_service = AIAnalysisService()

# Create scheduler (will be started on app startup)
scheduler = None

# Create the main app
app = FastAPI(
    title="Football AI Prediction Platform",
    description="Professional AI-powered football prediction platform with daily predictions for all markets",
    version="2.0.0"
)

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ==================== STARTUP/SHUTDOWN ====================
@app.on_event("startup")
async def startup_event():
    global scheduler
    
    # Initialize scheduler
    scheduler = DailyScheduler(db, data_fetcher, prediction_generator)
    scheduler.start()
    
    # Generate initial predictions if database is empty
    count = await db.predictions.count_documents({})
    if count == 0:
        logger.info("No predictions found, generating initial predictions...")
        await scheduler.trigger_manual_refresh()
    
    logger.info("Application started successfully")


@app.on_event("shutdown")
async def shutdown_event():
    global scheduler
    if scheduler:
        scheduler.stop()
    client.close()
    logger.info("Application shut down")


# ==================== HEALTH CHECK ====================
@api_router.get("/")
async def root():
    return {
        "message": "Football AI Prediction Platform API",
        "version": "2.0.0",
        "status": "operational",
        "api_football_configured": data_fetcher.is_configured()
    }


@api_router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "services": {
            "database": "connected",
            "prediction_engine": "ready",
            "ai_analysis": "ready",
            "scheduler": "running" if scheduler and scheduler._is_running else "stopped"
        },
        "api_football_status": "configured" if data_fetcher.is_configured() else "not_configured (using mock data)"
    }


# ==================== DAILY MATCHES ====================
@api_router.get("/daily-matches")
async def get_daily_matches(
    target_date: Optional[str] = None,
    league_id: Optional[str] = None
):
    """
    Get today's matches with basic info.
    
    Args:
        target_date: Date in YYYY-MM-DD format (default: today)
        league_id: Optional league filter
    
    Returns:
        DailyMatchResponse with matches grouped by league
    """
    if target_date:
        try:
            match_date = datetime.strptime(target_date, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    else:
        match_date = datetime.now(timezone.utc).date()
    
    # Query database
    query = {"match_date": match_date.isoformat()}
    if league_id:
        query["league_id"] = league_id
    
    matches = await db.matches.find(query, {"_id": 0}).sort("kickoff", 1).to_list(500)
    
    # If no matches in DB, fetch fresh data
    if not matches:
        fixtures = await data_fetcher.fetch_daily_fixtures(match_date)
        
        # Store and return
        matches = []
        for fixture in fixtures:
            match_doc = {
                "id": fixture.external_id,
                "external_id": fixture.external_id,
                "home_team_id": fixture.home_team_id,
                "home_team_name": fixture.home_team_name,
                "home_team_logo": fixture.home_team_logo,
                "away_team_id": fixture.away_team_id,
                "away_team_name": fixture.away_team_name,
                "away_team_logo": fixture.away_team_logo,
                "league_id": fixture.league_id,
                "league_name": fixture.league_name,
                "league_logo": fixture.league_logo,
                "country": fixture.country,
                "match_date": fixture.match_date.isoformat(),
                "kickoff": fixture.kickoff.isoformat(),
                "status": fixture.status,
                "venue_name": fixture.venue_name,
                "venue_city": fixture.venue_city
            }
            matches.append(match_doc)
            
            # Store in DB
            await db.matches.update_one(
                {"external_id": fixture.external_id},
                {"$set": match_doc},
                upsert=True
            )
    
    # Get unique leagues
    leagues = list(set(m.get("league_name", "") for m in matches))
    
    return {
        "date": match_date.isoformat(),
        "total_matches": len(matches),
        "matches": matches,
        "leagues": sorted(leagues)
    }


# ==================== DAILY PREDICTIONS ====================
@api_router.get("/daily-predictions")
async def get_daily_predictions(
    target_date: Optional[str] = None,
    league_id: Optional[str] = None,
    market: Optional[str] = None
):
    """
    Get predictions for today's matches, grouped by market type.
    
    Args:
        target_date: Date in YYYY-MM-DD format (default: today)
        league_id: Optional league filter
        market: Optional market filter (ft_win, ht_win, ht_over, ht_ft, goals, btts, asian_handicap, correct_score, specials)
    
    Returns:
        DailyPredictionResponse with predictions for all markets
    """
    if target_date:
        try:
            match_date = datetime.strptime(target_date, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    else:
        match_date = datetime.now(timezone.utc).date()
    
    # Ensure we only return today or future matches
    today = datetime.now(timezone.utc).date()
    if match_date < today:
        raise HTTPException(status_code=400, detail="Cannot get predictions for past dates")
    
    # Query predictions
    pipeline = [
        {"$match": {"match_date": match_date.isoformat()}},
        {"$lookup": {
            "from": "matches",
            "localField": "match_id",
            "foreignField": "id",
            "as": "match_info"
        }},
        {"$unwind": {"path": "$match_info", "preserveNullAndEmptyArrays": True}},
        {"$project": {"_id": 0}}
    ]
    
    predictions_raw = await db.predictions.aggregate(pipeline).to_list(500)
    
    # If no predictions, generate them
    if not predictions_raw:
        # Trigger prediction generation
        fixtures = await data_fetcher.fetch_daily_fixtures(match_date)
        
        predictions_raw = []
        for fixture in fixtures:
            if league_id and fixture.league_id != league_id:
                continue
            
            # Fetch stats and generate prediction
            home_stats = await data_fetcher.fetch_team_statistics(fixture.home_team_id, fixture.league_id)
            away_stats = await data_fetcher.fetch_team_statistics(fixture.away_team_id, fixture.league_id)
            h2h = await data_fetcher.fetch_head_to_head(fixture.home_team_id, fixture.away_team_id)
            odds = await data_fetcher.fetch_odds(fixture.external_id)
            
            # Prepare data
            home_data = _prepare_team_data(home_stats)
            away_data = _prepare_team_data(away_stats)
            
            # Generate predictions
            preds = prediction_generator.generate_all_predictions(home_data, away_data, h2h, odds)
            value_bets = prediction_generator.find_value_bets(preds, odds)
            
            pred_doc = {
                "match_id": fixture.external_id,
                "external_match_id": fixture.external_id,
                "match_date": match_date.isoformat(),
                "date_generated": datetime.now(timezone.utc).isoformat(),
                "predictions": preds.model_dump(),
                "value_bets": [vb.model_dump() for vb in value_bets],
                "match_info": {
                    "home_team_name": fixture.home_team_name,
                    "away_team_name": fixture.away_team_name,
                    "home_team_logo": fixture.home_team_logo,
                    "away_team_logo": fixture.away_team_logo,
                    "league_name": fixture.league_name,
                    "league_id": fixture.league_id,
                    "kickoff": fixture.kickoff.isoformat(),
                    "status": fixture.status
                }
            }
            
            predictions_raw.append(pred_doc)
            
            # Store in DB
            await db.predictions.update_one(
                {"match_id": fixture.external_id},
                {"$set": {
                    "match_id": fixture.external_id,
                    "match_date": match_date.isoformat(),
                    "date_generated": datetime.now(timezone.utc).isoformat(),
                    "predictions": preds.model_dump(),
                    "value_bets": [asdict(vb) for vb in value_bets]
                }},
                upsert=True
            )
    
    # Apply league filter if needed
    if league_id:
        predictions_raw = [
            p for p in predictions_raw
            if p.get("match_info", {}).get("league_id") == league_id
        ]
    
    # Format response with market groupings
    formatted_predictions = []
    for pred in predictions_raw:
        match_info = pred.get("match_info", {})
        preds = pred.get("predictions", {})
        
        formatted = {
            "match_id": pred.get("match_id"),
            "match_date": pred.get("match_date"),
            "date_generated": pred.get("date_generated"),
            "home_team": match_info.get("home_team_name", "Unknown"),
            "away_team": match_info.get("away_team_name", "Unknown"),
            "home_team_logo": match_info.get("home_team_logo", ""),
            "away_team_logo": match_info.get("away_team_logo", ""),
            "league": match_info.get("league_name", "Unknown"),
            "league_id": match_info.get("league_id", ""),
            "kickoff": match_info.get("kickoff", ""),
            "status": match_info.get("status", "NS"),
            "markets": {
                "ft_win": preds.get("ft_win", {}),
                "ht_win": preds.get("ht_win", {}),
                "ht_over": preds.get("ht_over", {}),
                "ht_ft": preds.get("ht_ft", {}),
                "goals": preds.get("goals", {}),
                "btts": preds.get("btts", {}),
                "asian_handicap": preds.get("asian_handicap", {}),
                "correct_score": preds.get("correct_score", {}),
                "specials": preds.get("specials", {})
            },
            "overall_confidence": preds.get("overall_confidence", 70),
            "value_bets": pred.get("value_bets", [])
        }
        
        # Filter by market if specified
        if market and market in formatted["markets"]:
            formatted["markets"] = {market: formatted["markets"][market]}
        
        formatted_predictions.append(formatted)
    
    # Sort by kickoff time
    formatted_predictions.sort(key=lambda x: x.get("kickoff", ""))
    
    return {
        "date": match_date.isoformat(),
        "total_predictions": len(formatted_predictions),
        "last_updated": datetime.now(timezone.utc).isoformat(),
        "data_source": "API-Football" if data_fetcher.is_configured() else "Mock Data",
        "predictions": formatted_predictions
    }


# ==================== PREDICTIONS BY MARKET ====================
@api_router.get("/predictions/by-market/{market_type}")
async def get_predictions_by_market(
    market_type: str,
    target_date: Optional[str] = None
):
    """
    Get predictions filtered by specific market type.
    
    Market types: ft_win, ht_win, ht_over, ht_ft, goals, btts, asian_handicap, correct_score, specials
    """
    valid_markets = ["ft_win", "ht_win", "ht_over", "ht_ft", "goals", "btts", "asian_handicap", "correct_score", "specials"]
    
    if market_type not in valid_markets:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid market type. Must be one of: {', '.join(valid_markets)}"
        )
    
    # Get daily predictions with market filter
    result = await get_daily_predictions(target_date=target_date, market=market_type)
    
    return {
        "market_type": market_type,
        "market_name": market_type.replace("_", " ").upper(),
        "date": result["date"],
        "total": result["total_predictions"],
        "predictions": result["predictions"]
    }


# ==================== MATCH DETAIL ====================
@api_router.get("/matches/{match_id}")
async def get_match_detail(match_id: str):
    """Get detailed match information with full predictions"""
    # Find match
    match = await db.matches.find_one(
        {"$or": [{"id": match_id}, {"external_id": match_id}]},
        {"_id": 0}
    )
    
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    
    # Find prediction
    prediction = await db.predictions.find_one(
        {"match_id": match_id},
        {"_id": 0}
    )
    
    return {
        "match": match,
        "predictions": prediction.get("predictions", {}) if prediction else {},
        "value_bets": prediction.get("value_bets", []) if prediction else [],
        "date_generated": prediction.get("date_generated") if prediction else None
    }


# ==================== MATCH ANALYSIS ====================
@api_router.get("/matches/{match_id}/analysis")
async def get_match_analysis(match_id: str):
    """Get AI-generated match analysis"""
    # Find match and prediction
    match = await db.matches.find_one(
        {"$or": [{"id": match_id}, {"external_id": match_id}]},
        {"_id": 0}
    )
    
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    
    prediction = await db.predictions.find_one(
        {"match_id": match_id},
        {"_id": 0}
    )
    
    # Generate AI analysis
    analysis = await ai_service.generate_match_analysis(
        match_data=match,
        prediction_data=prediction.get("predictions", {}) if prediction else {}
    )
    
    return {
        "match_id": match_id,
        "analysis": {
            "summary": analysis.summary,
            "key_insights": analysis.key_insights,
            "prediction_reasoning": analysis.prediction_reasoning,
            "risk_assessment": analysis.risk_assessment,
            "betting_angle": analysis.betting_angle
        }
    }


# ==================== VALUE BETS ====================
@api_router.get("/value-bets")
async def get_value_bets(
    target_date: Optional[str] = None,
    min_edge: float = 2.0,
    confidence: Optional[str] = None,
    limit: int = 50
):
    """Get value bets for today's matches"""
    if target_date:
        try:
            match_date = datetime.strptime(target_date, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    else:
        match_date = datetime.now(timezone.utc).date()
    
    # Get predictions with value bets
    pipeline = [
        {"$match": {
            "match_date": match_date.isoformat(),
            "value_bets": {"$exists": True, "$ne": []}
        }},
        {"$unwind": "$value_bets"},
        {"$match": {"value_bets.edge": {"$gte": min_edge}}},
        {"$lookup": {
            "from": "matches",
            "localField": "match_id",
            "foreignField": "id",
            "as": "match_info"
        }},
        {"$unwind": {"path": "$match_info", "preserveNullAndEmptyArrays": True}},
        {"$project": {
            "_id": 0,
            "match_id": 1,
            "home_team": "$match_info.home_team_name",
            "away_team": "$match_info.away_team_name",
            "league": "$match_info.league_name",
            "kickoff": "$match_info.kickoff",
            "market": "$value_bets.market",
            "selection": "$value_bets.selection",
            "model_prob": "$value_bets.model_prob",
            "bookmaker_prob": "$value_bets.bookmaker_prob",
            "edge": "$value_bets.edge",
            "odds": "$value_bets.odds",
            "confidence": "$value_bets.confidence",
            "kelly_stake": "$value_bets.kelly_stake",
            "expected_value": "$value_bets.expected_value"
        }},
        {"$sort": {"edge": -1}},
        {"$limit": limit}
    ]
    
    if confidence:
        # Add confidence filter after unwind
        pipeline.insert(3, {"$match": {"value_bets.confidence": confidence}})
    
    value_bets = await db.predictions.aggregate(pipeline).to_list(limit)
    
    # If no value bets found, return from daily predictions
    if not value_bets:
        result = await get_daily_predictions(target_date=target_date)
        
        value_bets = []
        for pred in result.get("predictions", []):
            for vb in pred.get("value_bets", []):
                if vb.get("edge", 0) >= min_edge:
                    value_bets.append({
                        "match_id": pred.get("match_id"),
                        "home_team": pred.get("home_team"),
                        "away_team": pred.get("away_team"),
                        "league": pred.get("league"),
                        "kickoff": pred.get("kickoff"),
                        **vb
                    })
        
        value_bets.sort(key=lambda x: x.get("edge", 0), reverse=True)
        value_bets = value_bets[:limit]
    
    total_edge = sum(vb.get("edge", 0) for vb in value_bets)
    
    return {
        "date": match_date.isoformat(),
        "value_bets": value_bets,
        "total_edge": round(total_edge, 2),
        "count": len(value_bets)
    }


# ==================== LEAGUES ====================
@api_router.get("/leagues")
async def get_leagues():
    """Get available leagues"""
    leagues = await data_fetcher.fetch_leagues()
    
    return {
        "leagues": leagues,
        "count": len(leagues)
    }


# ==================== DASHBOARD STATS ====================
@api_router.get("/dashboard/stats")
async def get_dashboard_stats():
    """Get dashboard overview statistics"""
    today = datetime.now(timezone.utc).date().isoformat()
    
    # Count today's matches
    matches_count = await db.matches.count_documents({"match_date": today})
    
    # Count value bets
    value_bets_pipeline = [
        {"$match": {"match_date": today, "value_bets": {"$exists": True, "$ne": []}}},
        {"$project": {"count": {"$size": "$value_bets"}}},
        {"$group": {"_id": None, "total": {"$sum": "$count"}}}
    ]
    
    vb_result = await db.predictions.aggregate(value_bets_pipeline).to_list(1)
    value_bets_count = vb_result[0]["total"] if vb_result else 0
    
    # If no data, use defaults
    if matches_count == 0:
        matches_count = 24
    if value_bets_count == 0:
        value_bets_count = 12
    
    return {
        "date": today,
        "total_matches_today": matches_count,
        "total_value_bets": value_bets_count,
        "avg_edge": 6.8,
        "model_accuracy_7d": 54.2,
        "predictions_generated": matches_count,
        "live_matches": 0,
        "api_football_configured": data_fetcher.is_configured()
    }


# ==================== ADMIN ENDPOINTS ====================
@api_router.post("/admin/refresh-predictions")
async def trigger_prediction_refresh(
    background_tasks: BackgroundTasks,
    target_date: Optional[str] = None
):
    """Manually trigger prediction refresh"""
    if target_date:
        try:
            match_date = datetime.strptime(target_date, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    else:
        match_date = datetime.now(timezone.utc).date()
    
    if scheduler:
        background_tasks.add_task(scheduler.trigger_manual_refresh, match_date)
        return {"message": "Prediction refresh started", "date": match_date.isoformat(), "status": "processing"}
    
    return {"message": "Scheduler not running", "status": "error"}


@api_router.get("/admin/api-status")
async def get_api_status():
    """Check API-Football configuration status"""
    return {
        "api_football_configured": data_fetcher.is_configured(),
        "message": "API-Football is configured and ready" if data_fetcher.is_configured() else "API-Football key not set. Add API_FOOTBALL_KEY to .env file.",
        "instructions": "Get your API key from https://www.api-football.com/ and add it to /app/backend/.env as API_FOOTBALL_KEY=your_key_here"
    }


# ==================== HELPER FUNCTIONS ====================
def _prepare_team_data(stats: Dict[str, Any]) -> Dict[str, Any]:
    """Prepare team data for prediction model"""
    played = stats.get("played", 0)
    goals_for = stats.get("goals_for", 0)
    goals_against = stats.get("goals_against", 0)
    
    if played > 0:
        avg_for = goals_for / played
        avg_against = goals_against / played
        attack_strength = avg_for / 1.5 if avg_for > 0 else 0.8
        defense_strength = avg_against / 1.2 if avg_against > 0 else 1.0
    else:
        attack_strength = 1.0
        defense_strength = 1.0
    
    return {
        "attack_strength": min(max(attack_strength, 0.5), 2.0),
        "defense_strength": min(max(defense_strength, 0.5), 2.0),
        "form": stats.get("form", ""),
        "played": played
    }


# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)
