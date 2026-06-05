# GitHub Container Registry Deployment Guide

## Overview
This project is configured to automatically build and push Docker images to GitHub Container Registry (GHCR) whenever you push to the `main` or `develop` branches.

**Your GHCR Images:**
- Backend: `ghcr.io/Forexbase/basketball-betting-backend`
- Frontend: `ghcr.io/Forexbase/basketball-betting-frontend`

## Setup Instructions

### Step 1: Initialize Git Repository
If you haven't already pushed to GitHub, do this:

```bash
cd "c:\Users\USER\Documents\My Projects\Basketball betting"
git init
git add .
git commit -m "Initial commit: Basketball betting application"
git branch -M main
git remote add origin https://github.com/Forexbase/basketball-betting.git
git push -u origin main
```

### Step 2: GitHub Actions Workflow
The workflow file (`.github/workflows/docker-publish.yml`) is already created and will:
- Automatically trigger on pushes to `main` or `develop` branches
- Build both backend and frontend Docker images
- Push images to GHCR with tags:
  - `main` (for main branch commits)
  - `develop` (for develop branch commits)
  - `vX.X.X` (for version tags)
  - `sha-xxxxx` (for specific commit SHA)

### Step 3: Pull and Run Images Locally
Once images are published to GHCR, pull them with:

```bash
# Backend
docker pull ghcr.io/Forexbase/basketball-betting-backend:main

# Frontend
docker pull ghcr.io/Forexbase/basketball-betting-frontend:main
```

### Step 4: Deploy Using docker-compose.ghcr.yml
Run the entire application from GHCR images:

```bash
docker-compose -f docker-compose.ghcr.yml up -d
```

**Access the application:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:5000

## Image Tags Explained

| Tag | When Built | Use Case |
|-----|-----------|----------|
| `main` | Push to main branch | Production deployments |
| `develop` | Push to develop branch | Development/staging |
| `vX.X.X` | Git tag created | Release versions |
| `sha-xxxxx` | Any push | Specific commit reference |

## Environment Variables
For production deployment, set these environment variables:

```bash
JWT_SECRET=your-production-jwt-secret
OPENAI_API_KEY=your-openai-api-key
REDIS_URL=redis://your-redis-instance:6379  # Optional
```

Update `docker-compose.ghcr.yml` with production values before deploying.

## Accessing Private Images
If you make the repository private, you'll need to authenticate:

```bash
echo $GITHUB_TOKEN | docker login ghcr.io -u Forexbase --password-stdin
```

Where `GITHUB_TOKEN` is a Personal Access Token with `read:packages` permission.

## Pushing Code to GitHub

After making changes locally:

```bash
git add .
git commit -m "Your commit message"
git push origin main
```

The GitHub Actions workflow will automatically:
1. Build the Docker images
2. Run tests (if configured)
3. Push to GHCR
4. Tag with appropriate version

## Next Steps

1. **Push to GitHub** - All files are ready, just push the code
2. **Monitor Actions** - Go to https://github.com/Forexbase/basketball-betting/actions to watch builds
3. **Deploy When Ready** - Use docker-compose.ghcr.yml to deploy anywhere Docker runs

## Troubleshooting

**Images not pushing?**
- Ensure your GitHub repository is created at https://github.com/Forexbase/basketball-betting
- Check Actions are enabled in repository settings
- Verify the workflow file is in `.github/workflows/`

**Authentication errors?**
- GitHub Actions uses `GITHUB_TOKEN` automatically
- For manual pushes, create a PAT with `write:packages` scope

**Slow builds?**
- First build takes longer due to layer creation
- Subsequent builds use cache and are faster
- Consider using `latest` tag for faster deployments

