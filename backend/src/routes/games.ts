import { Router } from 'express';

const router = Router();

router.get('/', (req, res) => {
  res.json({ message: 'Games endpoint' });
});

export default router;
