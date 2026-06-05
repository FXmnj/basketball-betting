# CourtVision AI - Phase 1 Documentation

## 🏀 Project Overview

**CourtVision AI** is a production-ready NBA basketball analytics and prediction platform built with a modern, scalable architecture. Phase 1 focuses on core authentication, database setup, and a responsive UI dashboard with mock data.

**Current Status:** Phase 1 Beta - Fully Functional

### Tech Stack
- **Frontend:** Next.js 15 (App Router) + TypeScript + Tailwind CSS
- **Backend:** Node.js + Express + TypeScript
- **Database:** PostgreSQL + Prisma ORM
- **Authentication:** JWT with HttpOnly Refresh Tokens
- **State Management:** Zustand
- **Deployment:** Docker-ready

---

## 📋 Phase 1 Features (Implemented)

### ✅ Authentication System
- User registration with validation
- Secure login with JWT tokens
- Profile management
- Role-based access control (User, Premium, Admin)
- Refresh token mechanism for security

### ✅ Database Schema
- User model with roles and subscriptions
- Team model with statistics
- Player model with performance metrics
- Game model with detailed stats
- Injury tracking
- Prediction records
- Favorite teams and watchlist

### ✅ Responsive UI
- Professional dark theme with NBA colors
- Sidebar navigation
- Dashboard with key metrics
- Teams browser
- Games viewer
- User profile settings
- Mobile-responsive design

### ✅ Mock Data
- 10 NBA teams with accurate data
- 30+ players with stats
- 20 sample games with scores
- 2 injury records
- 3 test user accounts

---

## 🚀 Quick Start Guide

### Prerequisites
- Node.js 20+
- PostgreSQL 14+
- Docker & Docker Compose (optional)

### Setup Instructions

#### Option 1: Traditional Setup

**1. Clone and Install Backend**
```bash
cd backend
npm install
```

**2. Set Up Environment Variables**
```bash
cp .env.example .env.local
```

Update `.env.local` with your database credentials:
```
DATABASE_URL="postgresql://user:password@localhost:5432/courtvision_ai"
NODE_ENV=development
PORT=5000
FRONTEND_URL=http://localhost:3000
JWT_SECRET=your-super-secret-jwt-key-change-in-production
JWT_REFRESH_SECRET=your-super-secret-refresh-key-change-in-production
```

**3. Set Up Database**
```bash
npx prisma migrate dev --name init
npm run seed
```

**4. Start Backend**
```bash
npm run dev
```

Backend will be running on `http://localhost:5000`

**5. Set Up Frontend**
```bash
cd frontend
npm install
```

**6. Start Frontend**
```bash
npm run dev
```

Frontend will be running on `http://localhost:3000`

#### Option 2: Docker Setup (Recommended)

**1. Create Root .env File**
```bash
cp .env.example .env
```

**2. Start All Services**
```bash
docker-compose up -d
```

**3. Run Database Migrations**
```bash
docker-compose exec backend npx prisma migrate dev
docker-compose exec backend npm run seed
```

**4. Access Application**
- Frontend: http://localhost:3000
- Backend: http://localhost:5000/api
- Database: localhost:5432

---

## 🔐 Test Credentials

```
Admin Account:
Email: admin@courtvision.ai
Password: TestPassword123

Premium Account:
Email: premium@courtvision.ai
Password: TestPassword123

Regular User:
Email: user@courtvision.ai
Password: TestPassword123
```

---

## 📁 Project Structure

```
Basketball betting/
├── backend/
│   ├── src/
│   │   ├── index.ts              # Main Express app
│   │   ├── middleware/           # Auth, error handling
│   │   ├── routes/               # API endpoints
│   │   ├── services/             # Business logic
│   │   └── seed.ts               # Database seeding
│   ├── prisma/
│   │   └── schema.prisma         # Database schema
│   ├── package.json
│   ├── tsconfig.json
│   └── Dockerfile
│
├── frontend/
│   ├── src/
│   │   ├── app/                  # Next.js app directory
│   │   │   ├── auth/             # Login, Register pages
│   │   │   ├── dashboard/        # Protected routes
│   │   │   ├── layout.tsx        # Root layout
│   │   │   ├── globals.css       # Global styles
│   │   │   └── page.tsx          # Home page
│   │   ├── components/           # Reusable components
│   │   ├── lib/                  # Utilities (API client, etc)
│   │   ├── stores/               # Zustand stores
│   │   └── types/                # TypeScript types
│   ├── package.json
│   ├── tsconfig.json
│   ├── tailwind.config.js
│   └── Dockerfile
│
├── docker-compose.yml
├── README.md
└── Phase1_Documentation.md
```

---

## 🔌 API Endpoints

### Authentication
- `POST /api/auth/register` - Create new account
- `POST /api/auth/login` - Login
- `POST /api/auth/refresh` - Refresh access token
- `GET /api/auth/profile` - Get user profile
- `PATCH /api/auth/profile` - Update profile
- `POST /api/auth/logout` - Logout

### Teams
- `GET /api/teams` - Get all teams
- `GET /api/teams/:id` - Get team details
- `GET /api/teams/:id/stats` - Get team statistics
- `GET /api/teams/standings/current` - Get standings

### Games
- `GET /api/games` - Get all games
- `GET /api/games/:id` - Get game details
- `GET /api/games?status=Scheduled` - Get upcoming games
- `GET /api/games?status=Final` - Get finished games

### Players
- `GET /api/players` - Get all players
- `GET /api/players/:id` - Get player details

### Predictions (Requires Auth)
- `POST /api/predictions` - Create prediction
- `GET /api/predictions/user` - Get user predictions

---

## 🧪 Testing

### Manual API Testing

**Using cURL:**
```bash
# Login
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@courtvision.ai","password":"TestPassword123"}'

# Get Teams
curl http://localhost:5000/api/teams

# Get Games
curl http://localhost:5000/api/games
```

**Using Postman:**
- Import the API endpoints
- Set Base URL: `http://localhost:5000/api`
- Use Bearer token authentication for protected routes

### Frontend Testing

1. Navigate to http://localhost:3000
2. Click "Sign Up" for new account
3. Or use test credentials to login
4. Browse teams, games, and profile
5. Test responsive design by resizing browser

---

## 📊 Database Schema Overview

```sql
-- Users with roles
CREATE TABLE "User" (
  id String PRIMARY KEY
  email String UNIQUE NOT NULL
  password String NOT NULL
  role UserRole (USER, PREMIUM, ADMIN)
  isVerified Boolean DEFAULT false
  ...
)

-- Teams
CREATE TABLE "Team" (
  id Int PRIMARY KEY
  name String UNIQUE
  abbreviation String UNIQUE
  city String
  conference String (Eastern, Western)
  wins Int
  losses Int
  ...
)

-- Games
CREATE TABLE "Game" (
  id Int PRIMARY KEY
  homeTeamId Int (FK: Team)
  awayTeamId Int (FK: Team)
  homeScore Int
  awayScore Int
  status String (Scheduled, InProgress, Final)
  ...
)

-- Predictions
CREATE TABLE "Prediction" (
  id Int PRIMARY KEY
  userId String (FK: User)
  gameId Int (FK: Game)
  projectedScore Int
  winProbability Float
  confidenceScore Float
  reasoning String (JSON)
  ...
)
```

---

## 🔍 Key Components

### Frontend Authentication Flow
1. User enters credentials on login/register page
2. Credentials sent to backend via API
3. Backend validates and returns JWT tokens
4. Tokens stored in localStorage
5. API client automatically adds token to requests
6. Dashboard shows only if authenticated

### State Management (Zustand)
- `authStore`: User state, login/logout, profile management
- Persists auth data in localStorage
- Automatic token refresh on 401 errors

### API Client (Axios)
- Configured with automatic JWT injection
- Handles token refresh automatically
- Provides typed endpoints

---

## 🎨 UI/UX Features

- **Dark Professional Theme** - NBA-inspired color scheme
- **Responsive Layout** - Works on mobile, tablet, desktop
- **Accessibility** - Proper semantic HTML, keyboard navigation
- **Real-time Feedback** - Loading states, error messages, toast notifications
- **Intuitive Navigation** - Sidebar menu with collapsible mobile view

---

## 🚦 Development Workflow

```bash
# Start backend in watch mode
cd backend
npm run dev

# Start frontend in watch mode
cd frontend
npm run dev

# Database management
npx prisma studio          # Open Prisma Studio
npx prisma migrate dev     # Create migration
npm run seed              # Re-seed database

# Run tests
npm run test              # Run test suite
```

---

## 🔄 Phase 2 Roadmap

Phase 2 will include:
- ✨ Advanced prediction engine with detailed reasoning
- 🤖 OpenAI integration for natural language insights
- 📊 Player analysis and comparison tools
- ⚡ Real-time live game tracking
- 🏆 Leaderboards and rankings
- 💬 Community predictions
- 📱 Mobile app (React Native)
- 🔔 Push notifications
- 💳 Stripe payments integration

---

## 🐛 Troubleshooting

**Backend won't start:**
```bash
# Check if port 5000 is in use
lsof -i :5000
# If so, kill the process or use different port
```

**Database connection error:**
```bash
# Verify PostgreSQL is running
psql -U courtvision -d courtvision_ai

# Check DATABASE_URL format
# Should be: postgresql://user:password@host:port/dbname
```

**Frontend API errors:**
```bash
# Check CORS settings in backend
# Check NEXT_PUBLIC_API_URL environment variable
# Verify backend is running on http://localhost:5000
```

**Database migration issues:**
```bash
# Reset database (WARNING: Deletes all data)
npx prisma migrate reset

# Or manually:
npx prisma db push --skip-generate
npm run seed
```

---

## 📝 Environment Variables Reference

**Backend (.env.local)**
```
DATABASE_URL              # PostgreSQL connection string
NODE_ENV                  # development, production
PORT                      # Server port (default: 5000)
FRONTEND_URL              # Frontend app URL
JWT_SECRET                # JWT signing key
JWT_REFRESH_SECRET        # Refresh token key
OPENAI_API_KEY            # For Phase 2 AI features
```

**Frontend (.env.local)**
```
NEXT_PUBLIC_API_URL       # Backend API base URL
NODE_ENV                  # development, production
```

---

## 📖 Additional Resources

- [Next.js Documentation](https://nextjs.org/docs)
- [Express.js Guide](https://expressjs.com/)
- [Prisma Documentation](https://www.prisma.io/docs/)
- [Tailwind CSS](https://tailwindcss.com/docs)
- [Zustand Store](https://github.com/pmndrs/zustand)

---

## 🤝 Contributing

For Phase 2 features and improvements, follow this workflow:
1. Create feature branch: `git checkout -b feature/feature-name`
2. Commit changes: `git commit -m "Add feature"`
3. Push to branch: `git push origin feature/feature-name`
4. Open Pull Request

---

## 📄 License

MIT License - See LICENSE file for details

---

## 👨‍💻 Support

For issues or questions, please check:
1. Troubleshooting section above
2. GitHub Issues
3. Documentation files

---

**CourtVision AI** - Professional NBA Analytics Platform | Phase 1 Beta ✅

**Last Updated:** June 2024
**Version:** 1.0.0
