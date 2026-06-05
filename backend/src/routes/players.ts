import { Router, Request, Response, NextFunction } from 'express';
import { PrismaClient } from '@prisma/client';
import { authenticateToken } from '../middleware/auth';

const prisma = new PrismaClient();
const router = Router();

// Get all players
router.get('/', async (req: Request, res: Response, next: NextFunction) => {
  try {
    const { teamId, position, search } = req.query;

    const where: any = {};

    if (teamId) {
      where.teamId = parseInt(teamId as string);
    }

    if (position) {
      where.position = position;
    }

    if (search) {
      where.OR = [
        { firstName: { contains: search as string, mode: 'insensitive' } },
        { lastName: { contains: search as string, mode: 'insensitive' } },
      ];
    }

    const players = await prisma.player.findMany({
      where,
      include: { team: true },
      orderBy: { pointsPerGame: 'desc' },
    });

    res.json(players);
  } catch (error) {
    next(error);
  }
});

// Get player by ID
router.get('/:id', async (req: Request, res: Response, next: NextFunction) => {
  try {
    const player = await prisma.player.findUnique({
      where: { id: parseInt(req.params.id) },
      include: {
        team: true,
        injuries: {
          orderBy: { startDate: 'desc' },
        },
      },
    });

    if (!player) {
      res.status(404).json({ error: 'Player not found' });
      return;
    }

    res.json(player);
  } catch (error) {
    next(error);
  }
});

// Add player to watchlist
router.post('/:id/watchlist', authenticateToken, async (req: Request, res: Response, next: NextFunction) => {
  try {
    if (!req.user) {
      res.status(401).json({ error: 'Not authenticated' });
      return;
    }

    const playerId = parseInt(req.params.id);

    const watchlist = await prisma.watchlistPlayer.create({
      data: {
        userId: req.user.id,
        playerId,
      },
      include: { player: true },
    });

    res.json(watchlist);
  } catch (error) {
    next(error);
  }
});

// Remove player from watchlist
router.delete('/:id/watchlist', authenticateToken, async (req: Request, res: Response, next: NextFunction) => {
  try {
    if (!req.user) {
      res.status(401).json({ error: 'Not authenticated' });
      return;
    }

    const playerId = parseInt(req.params.id);

    await prisma.watchlistPlayer.deleteMany({
      where: {
        userId: req.user.id,
        playerId,
      },
    });

    res.json({ success: true });
  } catch (error) {
    next(error);
  }
});

// Get player stats leaders
router.get('/stats/leaders', async (req: Request, res: Response, next: NextFunction) => {
  try {
    const { stat = 'pointsPerGame', limit = 10 } = req.query;

    const orderBy: any = {};
    orderBy[stat as string] = 'desc';

    const leaders = await prisma.player.findMany({
      include: { team: true },
      orderBy,
      take: parseInt(limit as string),
    });

    res.json(leaders);
  } catch (error) {
    next(error);
  }
});

export default router;
