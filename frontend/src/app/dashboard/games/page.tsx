'use client';

import { useEffect, useState } from 'react';
import { api } from '@/lib/api';

interface Game {
  id: number;
  homeTeam: { abbreviation: string; name: string };
  awayTeam: { abbreviation: string; name: string };
  homeScore?: number;
  awayScore?: number;
  status: string;
  gameDate: string;
  season: number;
}

export default function GamesPage() {
  const [games, setGames] = useState<Game[]>([]);
  const [loading, setLoading] = useState(true);
  const [filterStatus, setFilterStatus] = useState<string | null>(null);

  useEffect(() => {
    const fetchGames = async () => {
      try {
        const response = await api.games.getAll();
        setGames(response.data.sort((a: Game, b: Game) =>
          new Date(b.gameDate).getTime() - new Date(a.gameDate).getTime()
        ));
      } catch (error) {
        console.error('Failed to fetch games:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchGames();
  }, []);

  const statuses = ['Scheduled', 'InProgress', 'Final'];
  const displayedGames = filterStatus
    ? games.filter((g) => g.status === filterStatus)
    : games;

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="heading-2 mb-2">🎮 NBA Games</h1>
        <p className="text-dark-muted">View all NBA games and scores</p>
      </div>

      {/* Status Filter */}
      <div className="flex flex-wrap gap-2">
        <button
          onClick={() => setFilterStatus(null)}
          className={`px-4 py-2 rounded-lg ${
            filterStatus === null
              ? 'bg-nba-accent text-white'
              : 'bg-dark-surface border border-dark-border text-dark-text'
          }`}
        >
          All Games
        </button>
        {statuses.map((status) => (
          <button
            key={status}
            onClick={() => setFilterStatus(status)}
            className={`px-4 py-2 rounded-lg ${
              filterStatus === status
                ? 'bg-nba-accent text-white'
                : 'bg-dark-surface border border-dark-border text-dark-text'
            }`}
          >
            {status === 'InProgress' ? '🔴 Live' : status === 'Final' ? '✅ Final' : '📅 ' + status}
          </button>
        ))}
      </div>

      {/* Games List */}
      {loading ? (
        <div className="text-center py-12 text-dark-muted">Loading games...</div>
      ) : displayedGames.length === 0 ? (
        <div className="text-center py-12 text-dark-muted">No games found</div>
      ) : (
        <div className="space-y-3">
          {displayedGames.map((game) => (
            <div key={game.id} className="court-card hover:border-nba-accent transition-colors">
              <div className="flex items-center justify-between gap-4">
                {/* Home Team */}
                <div className="flex-1 text-left">
                  <p className="font-bold text-white">{game.homeTeam.abbreviation}</p>
                  <p className="text-xs text-dark-muted">{game.homeTeam.name}</p>
                  {game.status === 'Final' && (
                    <p className="text-lg font-bold text-nba-gold mt-1">{game.homeScore}</p>
                  )}
                </div>

                {/* Status / Score */}
                <div className="text-center px-4 py-2 bg-dark-hover rounded-lg min-w-[80px]">
                  {game.status === 'Final' ? (
                    <>
                      <p className="text-xs text-dark-muted font-bold">Final</p>
                      <p className="text-sm text-dark-muted">{game.homeScore} - {game.awayScore}</p>
                    </>
                  ) : game.status === 'InProgress' ? (
                    <>
                      <p className="text-xs text-red-400 font-bold animate-pulse">LIVE</p>
                      <p className="text-sm text-dark-muted">In Progress</p>
                    </>
                  ) : (
                    <>
                      <p className="text-xs text-dark-muted">Upcoming</p>
                      <p className="text-xs text-dark-muted font-medium">{formatDate(game.gameDate)}</p>
                    </>
                  )}
                </div>

                {/* Away Team */}
                <div className="flex-1 text-right">
                  <p className="font-bold text-white">{game.awayTeam.abbreviation}</p>
                  <p className="text-xs text-dark-muted">{game.awayTeam.name}</p>
                  {game.status === 'Final' && (
                    <p className="text-lg font-bold text-blue-400 mt-1">{game.awayScore}</p>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
