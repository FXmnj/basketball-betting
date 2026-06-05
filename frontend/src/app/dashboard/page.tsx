'use client';

import { useEffect, useState } from 'react';
import { api } from '@/lib/api';
import { useAuthStore } from '@/stores/authStore';

interface Team {
  id: number;
  name: string;
  abbreviation: string;
  city: string;
  conference: string;
  wins: number;
  losses: number;
}

interface Game {
  id: number;
  homeTeam: Team;
  awayTeam: Team;
  homeScore?: number;
  awayScore?: number;
  status: string;
  gameDate: string;
}

export default function DashboardPage() {
  const { user } = useAuthStore();
  const [teams, setTeams] = useState<Team[]>([]);
  const [games, setGames] = useState<Game[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const [teamsRes, gamesRes] = await Promise.all([
          api.teams.getAll(),
          api.games.getAll(),
        ]);

        setTeams(teamsRes.data);
        setGames(gamesRes.data);
      } catch (err: any) {
        console.error('Dashboard data fetch error:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const upcomingGames = games.filter((g) => g.status === 'Scheduled').slice(0, 5);
  const finalGames = games.filter((g) => g.status === 'Final').slice(0, 5);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <div className="text-4xl mb-4">🏀</div>
          <p className="text-dark-muted">Loading CourtVision...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Welcome Banner */}
      <div className="court-card-lg bg-gradient-to-r from-nba-accent/10 to-nba-gold/10 border-nba-accent/20">
        <h1 className="heading-2 mb-2">Welcome back, {user?.firstName || 'Player'}! 👋</h1>
        <p className="text-dark-muted">
          Explore NBA teams, live games, and AI-powered predictions. Phase 1 Beta - More features coming soon!
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="court-card">
          <div className="text-3xl mb-2">🏀</div>
          <p className="text-dark-muted text-sm">Total Teams</p>
          <p className="text-2xl font-bold text-nba-accent">{teams.length}</p>
        </div>
        <div className="court-card">
          <div className="text-3xl mb-2">🎮</div>
          <p className="text-dark-muted text-sm">Total Games</p>
          <p className="text-2xl font-bold text-nba-gold">{games.length}</p>
        </div>
        <div className="court-card">
          <div className="text-3xl mb-2">📊</div>
          <p className="text-dark-muted text-sm">Upcoming Games</p>
          <p className="text-2xl font-bold text-blue-400">{upcomingGames.length}</p>
        </div>
        <div className="court-card">
          <div className="text-3xl mb-2">✅</div>
          <p className="text-dark-muted text-sm">Completed Games</p>
          <p className="text-2xl font-bold text-green-400">{finalGames.length}</p>
        </div>
      </div>

      {/* Teams Overview */}
      <div className="court-card-lg">
        <h2 className="heading-3 mb-4">NBA Teams</h2>
        {teams.length === 0 ? (
          <p className="text-dark-muted">Loading teams...</p>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-3">
            {teams.slice(0, 10).map((team) => (
              <div key={team.id} className="bg-dark-hover p-3 rounded-lg">
                <p className="font-bold text-white">{team.abbreviation}</p>
                <p className="text-xs text-dark-muted mb-2">{team.name}</p>
                <p className="text-sm">
                  <span className="text-green-400">{team.wins}W</span>
                  <span className="text-dark-muted mx-1">-</span>
                  <span className="text-red-400">{team.losses}L</span>
                </p>
              </div>
            ))}
          </div>
        )}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Upcoming Games */}
        <div className="court-card-lg">
          <h2 className="heading-3 mb-4">📅 Upcoming Games</h2>
          {upcomingGames.length === 0 ? (
            <p className="text-dark-muted">No upcoming games</p>
          ) : (
            <div className="space-y-3">
              {upcomingGames.map((game) => (
                <div key={game.id} className="bg-dark-hover p-3 rounded-lg">
                  <div className="flex justify-between items-center">
                    <div className="flex-1">
                      <p className="font-bold">{game.homeTeam.abbreviation}</p>
                      <p className="text-xs text-dark-muted">{game.homeTeam.name}</p>
                    </div>
                    <div className="text-center px-4">
                      <p className="text-xs text-dark-muted">vs</p>
                    </div>
                    <div className="flex-1 text-right">
                      <p className="font-bold">{game.awayTeam.abbreviation}</p>
                      <p className="text-xs text-dark-muted">{game.awayTeam.name}</p>
                    </div>
                  </div>
                  <p className="text-xs text-dark-muted mt-2">
                    {new Date(game.gameDate).toLocaleDateString()}
                  </p>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Recent Final Games */}
        <div className="court-card-lg">
          <h2 className="heading-3 mb-4">✅ Recent Results</h2>
          {finalGames.length === 0 ? (
            <p className="text-dark-muted">No completed games</p>
          ) : (
            <div className="space-y-3">
              {finalGames.map((game) => (
                <div key={game.id} className="bg-dark-hover p-3 rounded-lg">
                  <div className="flex justify-between items-center">
                    <div className="flex-1">
                      <p className="font-bold">{game.homeTeam.abbreviation}</p>
                      <p className="text-sm text-nba-gold">{game.homeScore}</p>
                    </div>
                    <div className="text-center px-4">
                      <p className="text-xs text-dark-muted">Final</p>
                    </div>
                    <div className="flex-1 text-right">
                      <p className="font-bold">{game.awayTeam.abbreviation}</p>
                      <p className="text-sm text-blue-400">{game.awayScore}</p>
                    </div>
                  </div>
                  <p className="text-xs text-dark-muted mt-2">
                    {new Date(game.gameDate).toLocaleDateString()}
                  </p>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Features Coming Soon */}
      <div className="court-card-lg border-yellow-600/50 border-2">
        <h3 className="heading-4 mb-2">🚀 Phase 2 Features Coming Soon</h3>
        <ul className="text-dark-muted text-sm space-y-1">
          <li>✨ Advanced prediction engine with detailed analysis</li>
          <li>📈 AI-powered insights and recommendations</li>
          <li>⚡ Real-time live game tracking</li>
          <li>💬 Natural language analysis from OpenAI</li>
          <li>🎯 Player performance analysis and impact metrics</li>
        </ul>
      </div>
    </div>
  );
}
