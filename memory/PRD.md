# Football AI Prediction Platform - PRD v2.0

## Original Problem Statement
Build a professional AI-powered football prediction platform with:
- Daily matches from API-Football (or mock data)
- Predictions for ALL betting markets (FT WIN, HT WIN, HT Over, HT/FT, Goals, BTTS, Asian Handicap, Correct Score, Specials)
- Separated market predictions in frontend accordion UI
- Daily automated refresh via scheduler
- Only today's/future matches (no past matches)

## User Choices
- **Backend**: FastAPI (Python) - simpler, keeps ML and API together
- **Data Source**: API-Football (using mock data until API key provided)
- **UI Layout**: Accordion/collapsible sections per market
- **Automation**: Auto-refresh with APScheduler (6 AM UTC daily)

## User Personas
1. **Professional Sports Bettors**: Need accurate predictions with edge calculation
2. **Quantitative Analysts**: Interested in model performance
3. **Casual Bettors**: Want quick market overview

## Core Requirements (Static)
### Prediction Markets
1. **FT WIN**: Full-Time Winner (1X2)
2. **HT WIN**: Half-Time Winner
3. **HT OVER**: Half-Time Over/Under (0.5, 1.5)
4. **HT/FT**: Half-Time/Full-Time (9 combinations)
5. **Goals**: Over/Under 0.5, 1.5, 2.5, 3.5, 4.5, 5.5
6. **BTTS**: Both Teams To Score (Yes/No)
7. **Asian Handicap**: Dynamic line + alternative lines
8. **Correct Score**: Top 20 most likely scores
9. **Specials**: Clean sheets, win to nil, first to score, etc.

### Technical
- Predictions generated via Monte Carlo (10,000 simulations)
- Poisson goal model for expected goals
- Value bet detection with Kelly criterion
- Daily date filtering (no past matches)

## Architecture

### Backend (FastAPI/Python)
- `/api/daily-matches` - Today's fixtures
- `/api/daily-predictions` - All market predictions
- `/api/predictions/by-market/{market}` - Filter by market type
- `/api/value-bets` - Identified value bets
- `/api/matches/{id}` - Match detail
- `/api/matches/{id}/analysis` - AI analysis (GPT-5.2)
- `/api/admin/refresh-predictions` - Manual refresh trigger

### Services
- **APIFootballFetcher**: Fetches fixtures, stats, odds (mock if no key)
- **MarketPredictionsGenerator**: All 9 market predictions
- **DailyScheduler**: APScheduler for automation
- **AIAnalysisService**: GPT-5.2 match insights

### Frontend (React)
- Dark theme trading terminal aesthetic
- Accordion sections for each market
- League filtering
- Value bets sidebar
- Refresh button

### Database (MongoDB)
- `matches`: Fixture data with match_date
- `predictions`: All market predictions linked to match_id

## What's Been Implemented (Mar 2026)

### Backend
- ✅ All 9 prediction markets functional
- ✅ Monte Carlo simulation (10,000 runs)
- ✅ Value bet detection with Kelly criterion
- ✅ Daily scheduler with APScheduler
- ✅ API-Football integration (mock data mode)
- ✅ AI Analysis with GPT-5.2

### Frontend
- ✅ Accordion UI for all markets
- ✅ League filtering
- ✅ Value bets display
- ✅ Refresh functionality
- ✅ API configuration notice

### Testing Results
- Backend: 94% (17/18 tests passed)
- Frontend: 100% (all UI elements working)
- Overall: 97%

## Prioritized Backlog

### P0 (Critical)
- [ ] Real API-Football integration (requires API key)
- [ ] Real odds API integration

### P1 (High Priority)
- [ ] Historical prediction tracking
- [ ] Model accuracy calculation from results
- [ ] User accounts

### P2 (Medium Priority)
- [ ] More leagues coverage
- [ ] Mobile optimization
- [ ] Export to CSV

### P3 (Nice to Have)
- [ ] Telegram alerts
- [ ] Custom filters/watchlists
- [ ] Multi-language

## API-Football Setup Instructions

To use real match data:
1. Get API key from https://www.api-football.com/
2. Edit `/app/backend/.env`
3. Add: `API_FOOTBALL_KEY=your_key_here`
4. Restart backend: `sudo supervisorctl restart backend`

## Next Tasks
1. Obtain API-Football API key for real data
2. Implement historical tracking
3. Add model accuracy calculation from results
4. Consider Telegram bot for alerts

## Technical Notes
- **Data Status**: Currently using MOCKED data
- **AI Integration**: GPT-5.2 working via Emergent LLM Key
- **Scheduler**: APScheduler running at 6 AM UTC daily
- **Database**: MongoDB storing predictions with date_generated
