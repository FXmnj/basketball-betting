import { Router, Request, Response, NextFunction } from 'express';
import { PrismaClient } from '@prisma/client';
import { authenticateToken } from '../middleware/auth';

const prisma = new PrismaClient();
const router = Router();

// Get all teams
router.get('/', async (req: Request, res: Response, next: NextFunction) => {
  try {
    const teams = await prisma.team.findMany({
      orderBy: { conference: 'asc' },
    });
    res.json(teams);
  } catch (error) {
    next(error);
  }
});

// Get team by ID
router.get('/:id', async (req: Request, res: Response, next: NextFunction) => {
  try {
    const team = await prisma.team.findUnique({
      where: { id: parseInt(req.params.id) },
      include: {
        players: true,
        homeGames: {
          take: 10,
          orderBy: { gameDate: 'desc' },
        },
        awayGames: {
          take: 10,
          orderBy: { gameDate: 'desc' },
        },
      },
    });

    if (!team) {
      res.status(404).json({ error: 'Team not found' });
      return;
    }

    res.json(team);
  } catch (error) {
    next(error);
  }
});

// Get team standings
router.get('/standings/all', async (req: Request, res: Response, next: NextFunction) => {
  try {
    const teams = await prisma.team.findMany({
      select: {
        id: true,
        name: true,
        abbreviation: true,
        city: true,
        conference: true,
        wins: true,
        losses: true,
      },
      orderBy: [{ conference: 'asc' }, { wins: 'desc' }],
    });

    res.json(teams);
  } catch (error) {
    next(error);
  }
});

// Add team to favorites
router.post('/:id/favorite', authenticateToken, async (req: Request, res: Response, next: NextFunction) => {
  try {
    if (!req.user) {
      res.status(401).json({ error: 'Not authenticated' });
      return;
    }

    const teamId = parseInt(req.params.id);

    const favorite = await prisma.favoriteTeam.create({
      data: {
        userId: req.user.id,
        teamId,
      },
      include: { team: true },
    });

    res.json(favorite);
  } catch (error) {
    next(error);
  }
});

// Remove team from favorites
router.delete('/:id/favorite', authenticateToken, async (req: Request, res: Response, next: NextFunction) => {
  try {
    if (!req.user) {
      res.status(401).json({ error: 'Not authenticated' });
      return;
    }

    const teamId = parseInt(req.params.id);

    await prisma.favoriteTeam.deleteMany({
      where: {
        userId: req.user.id,
        teamId,
      },
    });

    res.json({ success: true });
  } catch (error) {
    next(error);
  }
});

export default router;
