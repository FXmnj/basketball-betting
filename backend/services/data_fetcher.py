"""
API-Football Data Fetcher
Fetches real match data from API-Football (RapidAPI)
"""
import os
import aiohttp
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone, timedelta, date
from dataclasses import dataclass, asdict
import logging

logger = logging.getLogger(__name__)


@dataclass
class MatchFixture:
    external_id: str
    home_team_id: str
    home_team_name: str
    home_team_logo: str
    away_team_id: str
    away_team_name: str
    away_team_logo: str
    league_id: str
    league_name: str
    league_logo: str
    country: str
    season: str
    match_date: date
    kickoff: datetime
    status: str
    venue_name: str
    venue_city: str


class APIFootballFetcher:
    """
    Fetches data from API-Football (RapidAPI)
    
    To use:
    1. Get API key from https://www.api-football.com/ or https://rapidapi.com/api-sports/api/api-football
    2. Add to .env: API_FOOTBALL_KEY=your_key_here
    """
    
    def __init__(self):
        self.api_key = os.environ.get("API_FOOTBALL_KEY", "")
        self.base_url = "https://v3.football.api-sports.io"
        self.rapidapi_host = "v3.football.api-sports.io"
        
        # Cache for rate limiting
        self._cache = {}
        self._cache_ttl = 300  # 5 minutes
        
        # Priority leagues (top European leagues)
        self.priority_leagues = {
            "39": {"name": "Premier League", "country": "England", "priority": 10},
            "140": {"name": "La Liga", "country": "Spain", "priority": 9},
            "135": {"name": "Serie A", "country": "Italy", "priority": 8},
            "78": {"name": "Bundesliga", "country": "Germany", "priority": 7},
            "61": {"name": "Ligue 1", "country": "France", "priority": 6},
            "2": {"name": "Champions League", "country": "Europe", "priority": 10},
            "3": {"name": "Europa League", "country": "Europe", "priority": 8},
            "94": {"name": "Primeira Liga", "country": "Portugal", "priority": 5},
            "88": {"name": "Eredivisie", "country": "Netherlands", "priority": 5},
            "144": {"name": "Belgian Pro League", "country": "Belgium", "priority": 4},
            "203": {"name": "Super Lig", "country": "Turkey", "priority": 4},
            "179": {"name": "Scottish Premiership", "country": "Scotland", "priority": 4},
        }
    
    def is_configured(self) -> bool:
        """Check if API key is configured"""
        return bool(self.api_key) and self.api_key != "your_api_football_key_here"
    
    async def _make_request(
        self,
        endpoint: str,
        params: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Make authenticated request to API-Football"""
        if not self.is_configured():
            logger.warning("API-Football key not configured, using mock data")
            return {"response": []}
        
        url = f"{self.base_url}/{endpoint}"
        headers = {
            "x-apisports-key": self.api_key,
            "x-rapidapi-host": self.rapidapi_host
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data
                    else:
                        logger.error(f"API-Football error: {response.status}")
                        return {"response": [], "errors": {"status": response.status}}
        except Exception as e:
            logger.error(f"API-Football request failed: {e}")
            return {"response": [], "errors": {"message": str(e)}}
    
    async def fetch_daily_fixtures(
        self,
        target_date: date = None,
        league_ids: List[str] = None
    ) -> List[MatchFixture]:
        """
        Fetch fixtures for a specific date (defaults to today)
        
        Args:
            target_date: Date to fetch fixtures for (default: today)
            league_ids: Optional list of league IDs to filter
        """
        if target_date is None:
            target_date = datetime.now(timezone.utc).date()
        
        date_str = target_date.strftime("%Y-%m-%d")
        cache_key = f"fixtures_{date_str}"
        
        # Check cache
        if cache_key in self._cache:
            cached_time, cached_data = self._cache[cache_key]
            if (datetime.now(timezone.utc) - cached_time).seconds < self._cache_ttl:
                return cached_data
        
        # If not configured, return mock data
        if not self.is_configured():
            return self._generate_mock_fixtures(target_date)
        
        # Fetch from API
        params = {"date": date_str}
        if league_ids:
            # Need to make multiple requests for multiple leagues
            all_fixtures = []
            for league_id in league_ids:
                params["league"] = league_id
                data = await self._make_request("fixtures", params)
                all_fixtures.extend(data.get("response", []))
        else:
            data = await self._make_request("fixtures", params)
            all_fixtures = data.get("response", [])
        
        # Parse fixtures
        fixtures = []
        for match in all_fixtures:
            try:
                fixture = match.get("fixture", {})
                teams = match.get("teams", {})
                league = match.get("league", {})
                venue = fixture.get("venue", {})
                
                kickoff_str = fixture.get("date", "")
                kickoff = datetime.fromisoformat(kickoff_str.replace("Z", "+00:00"))
                
                fixtures.append(MatchFixture(
                    external_id=str(fixture.get("id", "")),
                    home_team_id=str(teams.get("home", {}).get("id", "")),
                    home_team_name=teams.get("home", {}).get("name", "Unknown"),
                    home_team_logo=teams.get("home", {}).get("logo", ""),
                    away_team_id=str(teams.get("away", {}).get("id", "")),
                    away_team_name=teams.get("away", {}).get("name", "Unknown"),
                    away_team_logo=teams.get("away", {}).get("logo", ""),
                    league_id=str(league.get("id", "")),
                    league_name=league.get("name", "Unknown"),
                    league_logo=league.get("logo", ""),
                    country=league.get("country", "Unknown"),
                    season=str(league.get("season", "2024")),
                    match_date=target_date,
                    kickoff=kickoff,
                    status=fixture.get("status", {}).get("short", "NS"),
                    venue_name=venue.get("name", ""),
                    venue_city=venue.get("city", "")
                ))
            except Exception as e:
                logger.error(f"Error parsing fixture: {e}")
                continue
        
        # Cache results
        self._cache[cache_key] = (datetime.now(timezone.utc), fixtures)
        
        return fixtures
    
    async def fetch_team_statistics(
        self,
        team_id: str,
        league_id: str,
        season: str = "2024"
    ) -> Dict[str, Any]:
        """Fetch detailed team statistics"""
        if not self.is_configured():
            return self._generate_mock_team_stats()
        
        params = {
            "team": team_id,
            "league": league_id,
            "season": season
        }
        
        data = await self._make_request("teams/statistics", params)
        
        if data.get("response"):
            stats = data["response"]
            return {
                "played": stats.get("fixtures", {}).get("played", {}).get("total", 0),
                "wins": stats.get("fixtures", {}).get("wins", {}).get("total", 0),
                "draws": stats.get("fixtures", {}).get("draws", {}).get("total", 0),
                "losses": stats.get("fixtures", {}).get("loses", {}).get("total", 0),
                "goals_for": stats.get("goals", {}).get("for", {}).get("total", {}).get("total", 0),
                "goals_against": stats.get("goals", {}).get("against", {}).get("total", {}).get("total", 0),
                "goals_for_avg": stats.get("goals", {}).get("for", {}).get("average", {}).get("total", "0"),
                "goals_against_avg": stats.get("goals", {}).get("against", {}).get("average", {}).get("total", "0"),
                "clean_sheets": stats.get("clean_sheet", {}).get("total", 0),
                "form": stats.get("form", ""),
                "home_wins": stats.get("fixtures", {}).get("wins", {}).get("home", 0),
                "home_draws": stats.get("fixtures", {}).get("draws", {}).get("home", 0),
                "home_losses": stats.get("fixtures", {}).get("loses", {}).get("home", 0),
                "away_wins": stats.get("fixtures", {}).get("wins", {}).get("away", 0),
                "away_draws": stats.get("fixtures", {}).get("draws", {}).get("away", 0),
                "away_losses": stats.get("fixtures", {}).get("loses", {}).get("away", 0),
            }
        
        return self._generate_mock_team_stats()
    
    async def fetch_head_to_head(
        self,
        team1_id: str,
        team2_id: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Fetch head-to-head history between two teams"""
        if not self.is_configured():
            return self._generate_mock_h2h()
        
        params = {"h2h": f"{team1_id}-{team2_id}", "last": limit}
        data = await self._make_request("fixtures/headtohead", params)
        
        h2h = []
        for match in data.get("response", []):
            fixture = match.get("fixture", {})
            teams = match.get("teams", {})
            goals = match.get("goals", {})
            
            h2h.append({
                "date": fixture.get("date", ""),
                "home_team": teams.get("home", {}).get("name", ""),
                "home_team_id": str(teams.get("home", {}).get("id", "")),
                "away_team": teams.get("away", {}).get("name", ""),
                "away_team_id": str(teams.get("away", {}).get("id", "")),
                "home_score": goals.get("home", 0),
                "away_score": goals.get("away", 0)
            })
        
        return h2h if h2h else self._generate_mock_h2h()
    
    async def fetch_odds(
        self,
        fixture_id: str,
        bookmaker: str = "8"  # Bet365 by default
    ) -> Dict[str, Any]:
        """Fetch betting odds for a fixture"""
        if not self.is_configured():
            return self._generate_mock_odds()
        
        params = {"fixture": fixture_id, "bookmaker": bookmaker}
        data = await self._make_request("odds", params)
        
        odds = {}
        for response in data.get("response", []):
            for bookmaker_data in response.get("bookmakers", []):
                for bet in bookmaker_data.get("bets", []):
                    bet_name = bet.get("name", "")
                    values = bet.get("values", [])
                    
                    if bet_name == "Match Winner":
                        for v in values:
                            if v.get("value") == "Home":
                                odds["home_win"] = float(v.get("odd", 2.0))
                            elif v.get("value") == "Draw":
                                odds["draw"] = float(v.get("odd", 3.5))
                            elif v.get("value") == "Away":
                                odds["away_win"] = float(v.get("odd", 3.0))
                    
                    elif bet_name == "Goals Over/Under":
                        for v in values:
                            val = v.get("value", "")
                            if "Over 2.5" in val:
                                odds["over_25"] = float(v.get("odd", 1.9))
                            elif "Under 2.5" in val:
                                odds["under_25"] = float(v.get("odd", 2.0))
                    
                    elif bet_name == "Both Teams Score":
                        for v in values:
                            if v.get("value") == "Yes":
                                odds["btts_yes"] = float(v.get("odd", 1.8))
                            elif v.get("value") == "No":
                                odds["btts_no"] = float(v.get("odd", 2.0))
        
        return odds if odds else self._generate_mock_odds()
    
    async def fetch_leagues(self) -> List[Dict[str, Any]]:
        """Fetch all available leagues"""
        if not self.is_configured():
            return self._get_priority_leagues()
        
        data = await self._make_request("leagues", {"current": "true"})
        
        leagues = []
        for item in data.get("response", []):
            league = item.get("league", {})
            country = item.get("country", {})
            
            leagues.append({
                "id": str(league.get("id", "")),
                "name": league.get("name", ""),
                "country": country.get("name", ""),
                "logo": league.get("logo", ""),
                "flag": country.get("flag", ""),
                "type": league.get("type", ""),
            })
        
        return leagues if leagues else self._get_priority_leagues()
    
    # ==================== MOCK DATA GENERATORS ====================
    def _generate_mock_fixtures(self, target_date: date) -> List[MatchFixture]:
        """Generate mock fixtures when API key is not available"""
        import random
        
        fixtures = []
        
        mock_matches = [
            # Premier League
            ("Manchester City", "Arsenal", "39", "Premier League", "England"),
            ("Liverpool", "Chelsea", "39", "Premier League", "England"),
            ("Manchester United", "Tottenham", "39", "Premier League", "England"),
            ("Newcastle", "Brighton", "39", "Premier League", "England"),
            # La Liga
            ("Real Madrid", "Barcelona", "140", "La Liga", "Spain"),
            ("Atletico Madrid", "Sevilla", "140", "La Liga", "Spain"),
            # Serie A
            ("Inter Milan", "AC Milan", "135", "Serie A", "Italy"),
            ("Juventus", "Napoli", "135", "Serie A", "Italy"),
            # Bundesliga
            ("Bayern Munich", "Borussia Dortmund", "78", "Bundesliga", "Germany"),
            ("RB Leipzig", "Leverkusen", "78", "Bundesliga", "Germany"),
            # Ligue 1
            ("PSG", "Monaco", "61", "Ligue 1", "France"),
            ("Lyon", "Marseille", "61", "Ligue 1", "France"),
        ]
        
        base_time = datetime.combine(target_date, datetime.min.time()).replace(
            hour=15, minute=0, tzinfo=timezone.utc
        )
        
        for i, (home, away, league_id, league_name, country) in enumerate(mock_matches):
            kickoff = base_time + timedelta(hours=random.randint(0, 6))
            
            fixtures.append(MatchFixture(
                external_id=f"mock_{target_date}_{i}",
                home_team_id=f"team_{home.lower().replace(' ', '_')}",
                home_team_name=home,
                home_team_logo=f"https://media.api-sports.io/football/teams/{100 + i}.png",
                away_team_id=f"team_{away.lower().replace(' ', '_')}",
                away_team_name=away,
                away_team_logo=f"https://media.api-sports.io/football/teams/{200 + i}.png",
                league_id=league_id,
                league_name=league_name,
                league_logo=f"https://media.api-sports.io/football/leagues/{league_id}.png",
                country=country,
                season="2024",
                match_date=target_date,
                kickoff=kickoff,
                status="NS",
                venue_name=f"{home} Stadium",
                venue_city=home.split()[0]
            ))
        
        return fixtures
    
    def _generate_mock_team_stats(self) -> Dict[str, Any]:
        """Generate mock team statistics"""
        import random
        
        played = random.randint(15, 25)
        wins = random.randint(5, 15)
        draws = random.randint(2, 8)
        losses = played - wins - draws
        
        return {
            "played": played,
            "wins": wins,
            "draws": draws,
            "losses": losses,
            "goals_for": random.randint(25, 60),
            "goals_against": random.randint(15, 45),
            "goals_for_avg": str(round(random.uniform(1.2, 2.2), 2)),
            "goals_against_avg": str(round(random.uniform(0.8, 1.6), 2)),
            "clean_sheets": random.randint(3, 12),
            "form": "".join(random.choices(["W", "D", "L"], k=5)),
            "home_wins": random.randint(3, 10),
            "home_draws": random.randint(1, 5),
            "home_losses": random.randint(0, 4),
            "away_wins": random.randint(2, 8),
            "away_draws": random.randint(1, 5),
            "away_losses": random.randint(1, 6),
        }
    
    def _generate_mock_h2h(self) -> List[Dict[str, Any]]:
        """Generate mock head-to-head data"""
        import random
        
        return [
            {
                "date": (datetime.now(timezone.utc) - timedelta(days=30 * i)).isoformat(),
                "home_team": "Team A",
                "home_team_id": "team_a",
                "away_team": "Team B",
                "away_team_id": "team_b",
                "home_score": random.randint(0, 4),
                "away_score": random.randint(0, 3)
            }
            for i in range(5)
        ]
    
    def _generate_mock_odds(self) -> Dict[str, Any]:
        """Generate mock betting odds"""
        import random
        
        return {
            "home_win": round(1.5 + random.uniform(0, 2.5), 2),
            "draw": round(3.0 + random.uniform(0, 1.5), 2),
            "away_win": round(2.0 + random.uniform(0, 4.0), 2),
            "over_25": round(1.7 + random.uniform(0, 0.5), 2),
            "under_25": round(2.0 + random.uniform(0, 0.5), 2),
            "btts_yes": round(1.7 + random.uniform(0, 0.4), 2),
            "btts_no": round(2.0 + random.uniform(0, 0.4), 2),
        }
    
    def _get_priority_leagues(self) -> List[Dict[str, Any]]:
        """Return priority leagues for mock data"""
        return [
            {
                "id": lid,
                "name": info["name"],
                "country": info["country"],
                "logo": f"https://media.api-sports.io/football/leagues/{lid}.png",
                "flag": "",
                "type": "League"
            }
            for lid, info in self.priority_leagues.items()
        ]
