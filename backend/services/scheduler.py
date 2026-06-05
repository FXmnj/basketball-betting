"""
Daily Scheduler Service
Handles automated daily prediction generation
"""
import asyncio
from datetime import datetime, timezone, date, timedelta
from typing import List, Dict, Any
import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

logger = logging.getLogger(__name__)


class DailyScheduler:
    """
    Schedules daily tasks for:
    1. Fetching today's matches from API-Football
    2. Generating predictions for all markets
    3. Storing results in database
    4. Cleaning up old predictions
    """
    
    def __init__(self, db, data_fetcher, prediction_generator):
        self.db = db
        self.data_fetcher = data_fetcher
        self.prediction_generator = prediction_generator
        self.scheduler = AsyncIOScheduler()
        self._is_running = False
    
    def start(self):
        """Start the scheduler"""
        if self._is_running:
            return
        
        # Schedule daily prediction refresh at 6:00 AM UTC
        self.scheduler.add_job(
            self.daily_prediction_job,
            CronTrigger(hour=6, minute=0),
            id="daily_predictions",
            name="Daily Predictions Generator",
            replace_existing=True
        )
        
        # Schedule cleanup at midnight UTC
        self.scheduler.add_job(
            self.cleanup_old_predictions,
            CronTrigger(hour=0, minute=0),
            id="cleanup_old",
            name="Cleanup Old Predictions",
            replace_existing=True
        )
        
        # Schedule hourly refresh for live updates
        self.scheduler.add_job(
            self.hourly_refresh_job,
            CronTrigger(minute=0),  # Every hour
            id="hourly_refresh",
            name="Hourly Match Refresh",
            replace_existing=True
        )
        
        self.scheduler.start()
        self._is_running = True
        logger.info("Daily scheduler started")
    
    def stop(self):
        """Stop the scheduler"""
        if self.scheduler.running:
            self.scheduler.shutdown()
        self._is_running = False
        logger.info("Daily scheduler stopped")
    
    async def daily_prediction_job(self):
        """Main daily job to generate all predictions"""
        logger.info("Starting daily prediction job...")
        
        try:
            today = datetime.now(timezone.utc).date()
            
            # Fetch today's fixtures
            fixtures = await self.data_fetcher.fetch_daily_fixtures(today)
            logger.info(f"Fetched {len(fixtures)} fixtures for {today}")
            
            # Process each fixture
            for fixture in fixtures:
                await self._process_fixture(fixture)
            
            logger.info(f"Daily prediction job completed. Processed {len(fixtures)} matches.")
            
        except Exception as e:
            logger.error(f"Daily prediction job failed: {e}")
    
    async def hourly_refresh_job(self):
        """Hourly job to refresh predictions for upcoming matches"""
        logger.info("Starting hourly refresh job...")
        
        try:
            today = datetime.now(timezone.utc).date()
            
            # Get matches starting in next 3 hours
            now = datetime.now(timezone.utc)
            three_hours_later = now + timedelta(hours=3)
            
            # Fetch and update predictions for upcoming matches
            fixtures = await self.data_fetcher.fetch_daily_fixtures(today)
            
            upcoming = [
                f for f in fixtures
                if f.status == "NS" and f.kickoff <= three_hours_later
            ]
            
            for fixture in upcoming:
                await self._process_fixture(fixture)
            
            logger.info(f"Hourly refresh completed. Updated {len(upcoming)} matches.")
            
        except Exception as e:
            logger.error(f"Hourly refresh job failed: {e}")
    
    async def cleanup_old_predictions(self):
        """Remove predictions older than 7 days"""
        logger.info("Starting cleanup job...")
        
        try:
            cutoff_date = datetime.now(timezone.utc) - timedelta(days=7)
            
            # Delete old predictions
            result = await self.db.predictions.delete_many({
                "date_generated": {"$lt": cutoff_date}
            })
            
            # Delete old matches
            old_date = (datetime.now(timezone.utc).date() - timedelta(days=7)).isoformat()
            match_result = await self.db.matches.delete_many({
                "match_date": {"$lt": old_date}
            })
            
            logger.info(f"Cleanup completed. Deleted {result.deleted_count} predictions, {match_result.deleted_count} matches.")
            
        except Exception as e:
            logger.error(f"Cleanup job failed: {e}")
    
    async def _process_fixture(self, fixture):
        """Process a single fixture and generate predictions"""
        from dataclasses import asdict
        
        try:
            # Fetch team statistics
            home_stats = await self.data_fetcher.fetch_team_statistics(
                fixture.home_team_id, fixture.league_id
            )
            away_stats = await self.data_fetcher.fetch_team_statistics(
                fixture.away_team_id, fixture.league_id
            )
            
            # Fetch H2H
            h2h = await self.data_fetcher.fetch_head_to_head(
                fixture.home_team_id, fixture.away_team_id
            )
            
            # Fetch odds
            odds = await self.data_fetcher.fetch_odds(fixture.external_id)
            
            # Prepare team stats for prediction
            home_data = self._prepare_team_data(home_stats)
            away_data = self._prepare_team_data(away_stats)
            
            # Generate predictions
            predictions = self.prediction_generator.generate_all_predictions(
                home_data, away_data, h2h, odds
            )
            
            # Find value bets
            value_bets = self.prediction_generator.find_value_bets(predictions, odds)
            
            # Store match in database
            match_doc = {
                "id": str(fixture.external_id),
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
                "season": fixture.season,
                "match_date": fixture.match_date.isoformat(),
                "kickoff": fixture.kickoff.isoformat(),
                "status": fixture.status,
                "venue_name": fixture.venue_name,
                "venue_city": fixture.venue_city,
                "home_form": home_stats.get("form", ""),
                "away_form": away_stats.get("form", ""),
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
            
            await self.db.matches.update_one(
                {"external_id": fixture.external_id},
                {"$set": match_doc},
                upsert=True
            )
            
            # Store prediction
            prediction_doc = {
                "match_id": str(fixture.external_id),
                "external_match_id": fixture.external_id,
                "match_date": fixture.match_date.isoformat(),
                "date_generated": datetime.now(timezone.utc).isoformat(),
                "predictions": predictions.model_dump(),
                "value_bets": [vb.model_dump() for vb in value_bets],
                "data_quality": "complete" if self.data_fetcher.is_configured() else "mock"
            }
            
            await self.db.predictions.update_one(
                {"match_id": str(fixture.external_id)},
                {"$set": prediction_doc},
                upsert=True
            )
            
            logger.debug(f"Processed fixture: {fixture.home_team_name} vs {fixture.away_team_name}")
            
        except Exception as e:
            logger.error(f"Error processing fixture {fixture.external_id}: {e}")
    
    def _prepare_team_data(self, stats: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare team data for prediction model"""
        played = stats.get("played", 0)
        wins = stats.get("wins", 0)
        goals_for = stats.get("goals_for", 0)
        goals_against = stats.get("goals_against", 0)
        
        # Calculate attack/defense strength
        if played > 0:
            avg_for = goals_for / played
            avg_against = goals_against / played
            
            # Relative to league average (1.5 goals per game)
            attack_strength = avg_for / 1.5 if avg_for > 0 else 0.8
            defense_strength = avg_against / 1.2 if avg_against > 0 else 1.0
        else:
            attack_strength = 1.0
            defense_strength = 1.0
        
        return {
            "attack_strength": min(max(attack_strength, 0.5), 2.0),
            "defense_strength": min(max(defense_strength, 0.5), 2.0),
            "form": stats.get("form", ""),
            "played": played,
            "wins": wins,
            "goals_for_avg": stats.get("goals_for_avg", "1.5"),
            "goals_against_avg": stats.get("goals_against_avg", "1.2")
        }
    
    async def trigger_manual_refresh(self, target_date: date = None):
        """Manually trigger prediction refresh"""
        if target_date is None:
            target_date = datetime.now(timezone.utc).date()
        
        logger.info(f"Manual refresh triggered for {target_date}")
        
        fixtures = await self.data_fetcher.fetch_daily_fixtures(target_date)
        
        for fixture in fixtures:
            await self._process_fixture(fixture)
        
        return len(fixtures)
