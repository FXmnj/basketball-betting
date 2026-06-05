# 🧪 Phase 1 Testing Report & Instructions

## Testing Phase 1 - CourtVision AI

**Date:** June 5, 2026  
**Phase:** 1 Beta  
**Status:** Ready for Verification  

---

## 📋 Pre-Test Checklist

Before starting, verify you have:
- [ ] Node.js 20+ installed: `node --version`
- [ ] npm installed: `npm --version`
- [ ] PostgreSQL 14+ installed or Docker
- [ ] Project files downloaded/cloned
- [ ] Terminal ready

---

## 🚀 Test Setup - Choose One Option

### Option A: Docker Setup (Recommended - Fastest)

```bash
# 1. Navigate to project root
cd "c:\Users\USER\Documents\My Projects\Basketball betting"

# 2. Copy environment file
cp .env.example .env

# 3. Start all services
docker-compose up -d

# 4. Wait 30 seconds for services to start

# 5. Run migrations
docker-compose exec backend npx prisma migrate dev

# 6. Seed the database
docker-compose exec backend npm run seed

# 7. Check all services are running
docker-compose ps
```

**Expected Output:**
```
NAME                COMMAND             STATUS
courtvision-db      postgres...         Up (healthy)
courtvision-backend node dist/index.js  Up
courtvision-frontend next start         Up
```

### Option B: Traditional Setup

```bash
# Terminal 1: Backend Setup
cd backend
npm install
npx prisma migrate dev
npm run seed
npm run dev

# Expected: ✅ CourtVision AI Backend running on port 5000
```

```bash
# Terminal 2: Frontend Setup (in new terminal)
cd frontend
npm install
npm run dev

# Expected: ✅ Next.js app running on port 3000
```

---

## ✅ Test Section 1: Backend Health Check (2 minutes)

### Test 1.1: Health Endpoint
```bash
curl http://localhost:5000/api/health
```

**Expected Response:**
```json
{
  "status": "ok",
  "timestamp": "2026-06-05T..."
}
```

**Result:** ✅ / ❌

---

### Test 1.2: Check Database Connection
```bash
curl http://localhost:5000/api/teams
```

**Expected Response:**
- Array of teams
- First team: `{ "id": 1, "name": "Boston Celtics", "abbreviation": "BOS", ... }`
- Total count: 10 teams

**Result:** ✅ / ❌

---

## ✅ Test Section 2: Authentication (3 minutes)

### Test 2.1: User Registration
```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email":"testuser@test.com",
    "password":"TestPassword123",
    "firstName":"Test",
    "lastName":"User"
  }'
```

**Expected Response:**
```json
{
  "user": {
    "id": "...",
    "email": "testuser@test.com",
    "role": "USER"
  },
  "accessToken": "eyJ...",
  "refreshToken": "eyJ..."
}
```

**Result:** ✅ / ❌

**Note:** Copy the accessToken for next tests

---

### Test 2.2: User Login
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email":"user@courtvision.ai",
    "password":"TestPassword123"
  }'
```

**Expected Response:**
- User object
- accessToken
- refreshToken

**Result:** ✅ / ❌

---

### Test 2.3: Get Profile (Protected Route)
```bash
# Replace TOKEN with your accessToken from login
TOKEN="eyJ..."

curl http://localhost:5000/api/auth/profile \
  -H "Authorization: Bearer $TOKEN"
```

**Expected Response:**
```json
{
  "id": "...",
  "email": "user@courtvision.ai",
  "firstName": "Regular",
  "lastName": "User",
  "role": "USER",
  "isVerified": true
}
```

**Result:** ✅ / ❌

---

### Test 2.4: Invalid Token (Should Fail)
```bash
curl http://localhost:5000/api/auth/profile \
  -H "Authorization: Bearer invalid_token_here"
```

**Expected Response:**
```json
{
  "error": "Invalid token"
}
```

**Status Code:** 401

**Result:** ✅ / ❌

---

## ✅ Test Section 3: Data Endpoints (3 minutes)

### Test 3.1: Get All Teams
```bash
curl http://localhost:5000/api/teams | jq '.[0]'
```

**Expected:** Array with 10 teams, first one is Boston Celtics

**Result:** ✅ / ❌

---

### Test 3.2: Get Team by ID
```bash
curl http://localhost:5000/api/teams/1
```

**Expected:** 
```json
{
  "id": 1,
  "name": "Boston Celtics",
  "abbreviation": "BOS",
  "city": "Boston",
  "conference": "Eastern",
  "division": "Atlantic",
  "wins": 5,
  "losses": 2,
  "players": [...],
  "homeGames": [...],
  "awayGames": [...]
}
```

**Result:** ✅ / ❌

---

### Test 3.3: Get All Games
```bash
curl http://localhost:5000/api/games | jq '.[0]'
```

**Expected:** Array with 20 games

**Result:** ✅ / ❌

---

### Test 3.4: Get Game by ID
```bash
curl http://localhost:5000/api/games/1
```

**Expected:**
```json
{
  "id": 1,
  "homeTeamId": 1,
  "awayTeamId": 2,
  "homeScore": 112,
  "awayScore": 107,
  "status": "Final",
  "gameDate": "2024-11-01T19:30:00.000Z"
}
```

**Result:** ✅ / ❌

---

### Test 3.5: Get Team Statistics
```bash
curl http://localhost:5000/api/teams/1/stats
```

**Expected:**
```json
{
  "teamId": 1,
  "teamName": "Boston Celtics",
  "wins": 5,
  "losses": 2,
  "avgOffensiveRating": 118.5,
  "avgDefensiveRating": 112.3,
  "netRating": 6.2,
  "conference": "Eastern"
}
```

**Result:** ✅ / ❌

---

### Test 3.6: Get Standings
```bash
curl http://localhost:5000/api/teams/standings/current
```

**Expected:** All 10 teams ordered by conference and wins

**Result:** ✅ / ❌

---

## ✅ Test Section 4: Frontend - Pages & Navigation (5 minutes)

### Test 4.1: Home Page
1. Open http://localhost:3000 in browser
2. Verify you see:
   - [ ] "CourtVision AI" logo
   - [ ] Welcome message
   - [ ] 3 feature cards (Analytics, AI Predictions, Live Updates)
   - [ ] "Get Started Free" button
   - [ ] Login link

**Result:** ✅ / ❌

---

### Test 4.2: Register Page
1. Click "Get Started Free" button
2. Should navigate to /auth/register
3. Verify form has:
   - [ ] First Name field
   - [ ] Last Name field
   - [ ] Email field
   - [ ] Password field
   - [ ] Confirm Password field
   - [ ] "Create Account" button

4. Try invalid password (less than 8 chars):
   - [ ] Should show error message

5. Fill valid form:
   ```
   First Name: Test
   Last Name: User
   Email: testuser@test.com
   Password: TestPassword123
   Confirm: TestPassword123
   ```
6. Click "Create Account"
   - [ ] Should redirect to dashboard

**Result:** ✅ / ❌

---

### Test 4.3: Login Page
1. Logout if already logged in
2. Navigate to http://localhost:3000/auth/login
3. Verify form has:
   - [ ] Email field
   - [ ] Password field
   - [ ] Login button
   - [ ] Demo credentials button

4. Try with wrong credentials:
   - [ ] Should show error

5. Use demo credentials:
   ```
   Email: user@courtvision.ai
   Password: TestPassword123
   ```
6. Click "Login"
   - [ ] Should redirect to dashboard

**Result:** ✅ / ❌

---

### Test 4.4: Dashboard Page
After logging in, verify:
- [ ] Welcome message shows user name
- [ ] 4 stat cards visible (Teams, Games, Upcoming, Completed)
- [ ] Stat values populated:
  - Teams: 10
  - Games: 20
  - Upcoming: > 0
  - Completed: > 0
- [ ] Teams grid showing 10 teams
- [ ] Upcoming games section populated
- [ ] Recent results section populated
- [ ] Sidebar visible with navigation

**Result:** ✅ / ❌

---

### Test 4.5: Teams Page
1. Click "Teams" in sidebar
2. Navigate to /dashboard/teams
3. Verify:
   - [ ] All 10 teams visible
   - [ ] Filter buttons present (All, Eastern, Western)
   - [ ] Each team card shows:
     - Abbreviation
     - Name
     - Record (wins-losses)
     - Win percentage
   
4. Test filters:
   - [ ] Click "Eastern Conference" → shows only eastern teams
   - [ ] Click "Western Conference" → shows only western teams
   - [ ] Click "All Teams" → shows all 10

**Result:** ✅ / ❌

---

### Test 4.6: Games Page
1. Click "Games" in sidebar
2. Navigate to /dashboard/games
3. Verify:
   - [ ] Games list visible
   - [ ] Status filter buttons present (All, Upcoming, Live, Final)
   - [ ] Each game shows:
     - Home team abbreviation
     - Away team abbreviation
     - Status or score
     - Game date

4. Test filters:
   - [ ] Filter by "Final" → shows completed games only
   - [ ] Filter by "Scheduled" → shows upcoming games only

**Result:** ✅ / ❌

---

### Test 4.7: Profile Page
1. Click "Profile" in sidebar
2. Navigate to /dashboard/profile
3. Verify:
   - [ ] Email displayed
   - [ ] Role displayed (should be USER)
   - [ ] Account status shown (Verified and Active)
   - [ ] Edit form with:
     - First Name field
     - Last Name field
     - Save button

4. Edit profile:
   - [ ] Change First Name
   - [ ] Click Save
   - [ ] Should see success message

**Result:** ✅ / ❌

---

### Test 4.8: Logout
1. Click Logout button (in sidebar)
2. Should redirect to home page
3. Try to access /dashboard directly
   - [ ] Should redirect to /auth/login

**Result:** ✅ / ❌

---

## ✅ Test Section 5: Responsive Design (2 minutes)

### Test 5.1: Desktop (1920x1080)
1. Open http://localhost:3000
2. Verify:
   - [ ] Sidebar visible on left
   - [ ] Content area wide
   - [ ] All elements properly spaced
   - [ ] No horizontal scrollbar

**Result:** ✅ / ❌

---

### Test 5.2: Tablet (768x1024)
1. Open DevTools (F12)
2. Toggle Device Toolbar
3. Select iPad
4. Verify:
   - [ ] Sidebar toggles with hamburger menu
   - [ ] Content adapts to width
   - [ ] No horizontal scrollbar
   - [ ] All buttons clickable

**Result:** ✅ / ❌

---

### Test 5.3: Mobile (375x667)
1. Select iPhone SE in DevTools
2. Verify:
   - [ ] Sidebar collapsed by default
   - [ ] Hamburger menu visible
   - [ ] Content full width
   - [ ] All text readable
   - [ ] Buttons properly sized
   - [ ] Forms inputs usable

**Result:** ✅ / ❌

---

## ✅ Test Section 6: Database Verification (2 minutes)

### Test 6.1: Open Prisma Studio
```bash
cd backend
npx prisma studio
```

Opens at http://localhost:5555

Verify in Prisma Studio:
- [ ] Users table: 3 records (admin, premium, user)
- [ ] Teams table: 10 records
- [ ] Players table: 30+ records
- [ ] Games table: 20 records
- [ ] Injuries table: 2 records

**Result:** ✅ / ❌

---

### Test 6.2: Query Database Directly (Optional)
```bash
psql -U courtvision -d courtvision_ai

-- Count each table
SELECT COUNT(*) FROM "User";
SELECT COUNT(*) FROM "Team";
SELECT COUNT(*) FROM "Player";
SELECT COUNT(*) FROM "Game";
SELECT COUNT(*) FROM "Injury";
```

**Expected:**
```
User: 3
Team: 10
Player: 30+
Game: 20
Injury: 2
```

**Result:** ✅ / ❌

---

## ✅ Test Section 7: Error Handling (2 minutes)

### Test 7.1: Invalid Login
1. Go to login page
2. Enter: email@test.com / wrongpassword
3. Should show: "Invalid credentials" error

**Result:** ✅ / ❌

---

### Test 7.2: Invalid Token
```bash
curl http://localhost:5000/api/auth/profile \
  -H "Authorization: Bearer invalid"
```

Should return: 401 Unauthorized

**Result:** ✅ / ❌

---

### Test 7.3: Missing Required Fields
```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com"}'
```

Should return: 400 Bad Request error

**Result:** ✅ / ❌

---

## 📊 Test Results Summary

### Backend Tests (7 tests)
| Test | Status | Notes |
|------|--------|-------|
| Health Check | ✅/❌ | |
| Get Teams | ✅/❌ | |
| Get Games | ✅/❌ | |
| Register User | ✅/❌ | |
| Login User | ✅/❌ | |
| Protected Route | ✅/❌ | |
| Team Stats | ✅/❌ | |

### Frontend Tests (8 tests)
| Test | Status | Notes |
|------|--------|-------|
| Home Page | ✅/❌ | |
| Register Page | ✅/❌ | |
| Login Page | ✅/❌ | |
| Dashboard | ✅/❌ | |
| Teams Page | ✅/❌ | |
| Games Page | ✅/❌ | |
| Profile Page | ✅/❌ | |
| Logout | ✅/❌ | |

### Responsive Design (3 tests)
| Test | Status | Notes |
|------|--------|-------|
| Desktop | ✅/❌ | |
| Tablet | ✅/❌ | |
| Mobile | ✅/❌ | |

### Database Tests (2 tests)
| Test | Status | Notes |
|------|--------|-------|
| Prisma Studio | ✅/❌ | |
| Data Counts | ✅/❌ | |

### Error Handling (3 tests)
| Test | Status | Notes |
|------|--------|-------|
| Invalid Login | ✅/❌ | |
| Invalid Token | ✅/❌ | |
| Missing Fields | ✅/❌ | |

**Total Tests:** 23  
**Passed:** __/23  
**Failed:** __/23  

---

## 🎯 Final Verification

### All Tests Pass? ✅
If all 23 tests passed above, Phase 1 is **PRODUCTION READY**.

### Some Tests Failed? ❌
1. Check the Troubleshooting section in PHASE_1_DOCUMENTATION.md
2. Review error messages in terminal
3. Check docker-compose logs: `docker-compose logs -f`

---

## 🛠️ Troubleshooting Quick Links

| Error | Solution |
|-------|----------|
| Port already in use | Kill process: `lsof -i :5000` |
| Database error | Reset: `npx prisma migrate reset` |
| Frontend won't connect | Check NEXT_PUBLIC_API_URL in .env |
| Docker fails | Check: `docker-compose logs` |
| Services won't start | Wait 30 sec and try: `docker-compose ps` |

---

## 📝 Test Notes

**Date Tested:** ___________  
**Tester Name:** ___________  
**Environment:** Docker / Traditional  
**Issues Found:** ___________  
**Overall Status:** ✅ Pass / ❌ Fail  

---

## ✅ Phase 1 Testing Complete

When all tests pass, you can:
1. ✅ Confirm Phase 1 is complete
2. 🚀 Deploy to production
3. 🔮 Begin Phase 2 development

---

**Testing Guide Version:** 1.0  
**Last Updated:** June 5, 2026
