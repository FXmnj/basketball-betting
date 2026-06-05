# Basketball Betting - GitHub & GHCR Deployment

## Quick Start for Windows Users

### Option 1: Push to GitHub (One-Time Setup)
```powershell
cd "c:\Users\USER\Documents\My Projects\Basketball betting"

# Initialize git if not done
git init
git config user.name "Your Name"
git config user.email "your.email@example.com"

# Add all files
git add .
git commit -m "Initial commit: Basketball betting application"

# Create repository on GitHub first at: https://github.com/Forexbase/basketball-betting
# Then push:
git branch -M main
git remote add origin https://github.com/Forexbase/basketball-betting.git
git push -u origin main
```

### Option 2: Deploy from GHCR Images (After Push)
```powershell
cd "c:\Users\USER\Documents\My Projects\Basketball betting"

# Pull latest images from GHCR
docker compose -f docker-compose.ghcr.yml pull

# Start containers
docker compose -f docker-compose.ghcr.yml up -d

# View logs
docker compose -f docker-compose.ghcr.yml logs -f backend

# Stop when done
docker compose -f docker-compose.ghcr.yml down
```

### Option 3: Update Code & Redeploy
```powershell
cd "c:\Users\USER\Documents\My Projects\Basketball betting"

# Make your changes to the code...

# Commit and push
git add .
git commit -m "Your commit message"
git push origin main

# Wait for GitHub Actions to build (watch at: https://github.com/Forexbase/basketball-betting/actions)
# Then redeploy:
docker compose -f docker-compose.ghcr.yml pull
docker compose -f docker-compose.ghcr.yml up -d
```

## What Happens Automatically

When you `git push`:
1. ✅ GitHub Actions workflow triggers
2. ✅ Docker images build (backend + frontend)
3. ✅ Images pushed to GHCR
4. ✅ Ready to deploy anywhere with docker-compose

## Access Your Application
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:5000
- **Database**: localhost:5432

## Manage Your Images
```powershell
# List local GHCR images
docker images | findstr "basketball-betting"

# View available tags on GHCR
docker search ghcr.io/Forexbase/basketball-betting

# Remove old images
docker rmi ghcr.io/Forexbase/basketball-betting-backend:old-tag
```
