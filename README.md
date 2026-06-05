# 🏀 CourtVision AI - NBA Basketball Analytics & Prediction Platform

> **Status:** Phase 1 Beta ✅ - Production-ready foundation with authentication, database, and responsive UI

![CourtVision AI](https://img.shields.io/badge/Version-1.0.0-blue?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)
![Node.js](https://img.shields.io/badge/Node.js-20+-brightgreen?style=flat-square)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-14+-blue?style=flat-square)
![Next.js](https://img.shields.io/badge/Next.js-15-black?style=flat-square)

A professional-grade NBA basketball analytics and game prediction platform built with cutting-edge web technologies. Phase 1 includes complete authentication, database architecture, and a responsive dark-themed dashboard with mock data.

## 🎯 Quick Start

### Prerequisites
- Node.js 20+
- PostgreSQL 14+
- Docker & Docker Compose (optional)

### Docker Setup (Recommended)
```bash
# Copy environment file
cp .env.example .env

# Start all services
docker-compose up -d

# Run migrations and seed data
docker-compose exec backend npx prisma migrate dev
docker-compose exec backend npm run seed

# Access the app
# Frontend: http://localhost:3000
# Backend: http://localhost:5000/api
```

### Traditional Setup

**Backend:**
```bash
cd backend
cp .env.example .env.local
npm install
npx prisma migrate dev
npm run seed
npm run dev
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

### Test Credentials
```
Email: user@courtvision.ai
Password: TestPassword123
```

## 🏆 Phase 1 Deliverables

### ✅ Complete Features
- **Authentication System** - Register, Login, JWT tokens, refresh mechanism
- **User Roles** - User, Premium, Admin with role-based access
- **Responsive UI** - Dark professional theme, mobile-optimized
- **Dashboard** - Teams browser, games viewer, user profile
- **Database Schema** - Complete NBA data models with Prisma ORM
- **Mock Data** - 10 teams, 30+ players, 20 games, injury tracking
- **API Routes** - Full RESTful API with validation
- **Docker Ready** - Production-grade containerization

### 📦 Tech Stack
| Component | Technology |
|-----------|-----------|
| Frontend | Next.js 15 + TypeScript + Tailwind CSS |
| Backend | Node.js + Express + TypeScript |
| Database | PostgreSQL + Prisma ORM |
| State | Zustand |
| UI | Dark theme + NBA colors + Responsive |
| Deployment | Docker + Docker Compose |

## 📁 Project Structure
```
Basketball betting/
├── backend/                # Express API
│   ├── src/
│   │   ├── index.ts       # Main app
│   │   ├── routes/        # API endpoints
│   │   ├── middleware/    # Auth, errors
│   │   └── seed.ts        # Mock data
│   ├── prisma/
│   │   └── schema.prisma  # Database schema
│   └── Dockerfile
├── frontend/              # Next.js app
│   ├── src/
│   │   ├── app/          # App Router
│   │   ├── components/   # React components
│   │   ├── lib/          # Utilities
│   │   └── stores/       # Zustand state
│   └── Dockerfile
├── docker-compose.yml
└── PHASE_1_DOCUMENTATION.md
```

## 🔌 API Endpoints

### Authentication
- `POST /api/auth/register` - Create account
- `POST /api/auth/login` - Login
- `GET /api/auth/profile` - Get user
- `PATCH /api/auth/profile` - Update profile

### Teams & Games
- `GET /api/teams` - All teams
- `GET /api/teams/:id` - Team details
- `GET /api/games` - All games
- `GET /api/teams/standings/current` - Standings

### Players
- `GET /api/players` - All players
- `GET /api/players/:id` - Player details

[📚 Full API Documentation](./PHASE_1_DOCUMENTATION.md#-api-endpoints)

## 🎨 Features Showcase

### 🔐 Authentication Flow
- Secure password hashing with bcryptjs
- JWT access & refresh tokens
- Automatic token refresh
- Protected routes

### 📊 Dashboard
- Real-time team and game data
- Win/loss records and standings
- Responsive grid layouts
- Mobile-optimized sidebar

### 🎯 User Management
- Profile editing
- Account roles display
- Subscription status
- Activity tracking

## 🚀 Development

```bash
# Backend development
cd backend
npm run dev

# Frontend development
cd frontend
npm run dev

# Database management
npx prisma studio                  # Visual editor
npx prisma migrate dev --name name # Create migration
npm run seed                       # Reseed data
```

## 🧪 Testing

### Manual API Testing
```bash
# Login
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@courtvision.ai","password":"TestPassword123"}'

# Get Teams
curl http://localhost:5000/api/teams
```

### Frontend Testing
1. Open http://localhost:3000
2. Use test credentials to login
3. Browse teams, games, and profile
4. Test mobile responsiveness

## 📊 Database Schema

**Users** - Authentication and profiles  
**Teams** - NBA team data and statistics  
**Players** - Player stats and information  
**Games** - Game results and details  
**Predictions** - AI game predictions  
**Injuries** - Player injury reports  

[📐 Full Schema Details](./PHASE_1_DOCUMENTATION.md#-database-schema-overview)

## 🔄 Phase 2 Roadmap

Phase 2 will add:
- ✨ Prediction engine with ML
- 🤖 OpenAI integration for analysis
- 📈 Advanced player analytics
- ⚡ Real-time live tracking
- 🏆 Leaderboards
- 💳 Stripe payments
- 📱 Mobile app

## 📖 Documentation

- [Phase 1 Full Documentation](./PHASE_1_DOCUMENTATION.md)
- [API Reference](./PHASE_1_DOCUMENTATION.md#-api-endpoints)
- [Database Schema](./PHASE_1_DOCUMENTATION.md#-database-schema-overview)
- [Troubleshooting](./PHASE_1_DOCUMENTATION.md#-troubleshooting)

## 🐛 Troubleshooting

**Port already in use:**
```bash
# Find and kill process on port 5000/3000
lsof -i :5000
kill -9 <PID>
```

**Database connection error:**
```bash
# Verify PostgreSQL running
psql -U courtvision -d courtvision_ai

# Reset database
npx prisma migrate reset
npm run seed
```

[More troubleshooting](./PHASE_1_DOCUMENTATION.md#-troubleshooting)

## 🔧 Environment Variables

See `.env.example` for all available variables:

```env
DATABASE_URL=postgresql://...
NODE_ENV=development
PORT=5000
JWT_SECRET=your-secret-key
NEXT_PUBLIC_API_URL=http://localhost:5000/api
```

## 📋 Checklist

### Phase 1 Completion ✅
- [x] User authentication system
- [x] Database schema
- [x] API endpoints
- [x] Frontend dashboard
- [x] Mock data
- [x] Docker configuration
- [x] Documentation
- [x] Responsive design

### Phase 2 (In Progress)
- [ ] Prediction engine
- [ ] OpenAI integration
- [ ] Live game tracking
- [ ] Advanced analytics
- [ ] Mobile app

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/your-feature`
3. Commit changes: `git commit -m "Add feature"`
4. Push to branch: `git push origin feature/your-feature`
5. Open Pull Request

## 📄 License

MIT License - See LICENSE file for details

## 💬 Support

For issues, questions, or feedback:
1. Check [Troubleshooting](./PHASE_1_DOCUMENTATION.md#-troubleshooting)
2. Review [Full Documentation](./PHASE_1_DOCUMENTATION.md)
3. Open GitHub Issue

---

<div align="center">

### 🏀 CourtVision AI - Professional NBA Analytics Platform

**Phase 1: Complete** ✅ | **Production Ready** 🚀

[📚 Full Documentation](./PHASE_1_DOCUMENTATION.md) • [🐛 Report Issue](https://github.com) • [⭐ Star us](https://github.com)

</div>
