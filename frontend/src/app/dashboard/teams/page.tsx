'use client';

import { useEffect, useState } from 'react';
import { api } from '@/lib/api';

interface Team {
  id: number;
  name: string;
  abbreviation: string;
  city: string;
  conference: string;
  wins: number;
  losses: number;
  primaryColor?: string;
  secondaryColor?: string;
}

export default function TeamsPage() {
  const [teams, setTeams] = useState<Team[]>([]);
  const [loading, setLoading] = useState(true);
  const [filteredConference, setFilteredConference] = useState<string | null>(null);

  useEffect(() => {
    const fetchTeams = async () => {
      try {
        const response = await api.teams.getAll();
        setTeams(response.data);
      } catch (error) {
        console.error('Failed to fetch teams:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchTeams();
  }, []);

  const displayedTeams = filteredConference
    ? teams.filter((t) => t.conference === filteredConference)
    : teams;

  const conferences = ['Eastern', 'Western'];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="heading-2 mb-2">🏀 NBA Teams</h1>
        <p className="text-dark-muted">Browse all NBA teams and their statistics</p>
      </div>

      {/* Conference Filter */}
      <div className="flex gap-2">
        <button
          onClick={() => setFilteredConference(null)}
          className={`px-4 py-2 rounded-lg ${
            filteredConference === null
              ? 'bg-nba-accent text-white'
              : 'bg-dark-surface border border-dark-border text-dark-text'
          }`}
        >
          All Teams
        </button>
        {conferences.map((conf) => (
          <button
            key={conf}
            onClick={() => setFilteredConference(conf)}
            className={`px-4 py-2 rounded-lg ${
              filteredConference === conf
                ? 'bg-nba-accent text-white'
                : 'bg-dark-surface border border-dark-border text-dark-text'
            }`}
          >
            {conf} Conference
          </button>
        ))}
      </div>

      {/* Teams Grid */}
      {loading ? (
        <div className="text-center py-12 text-dark-muted">Loading teams...</div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {displayedTeams.map((team) => (
            <div
              key={team.id}
              className="court-card hover:border-nba-accent cursor-pointer"
            >
              <div className="flex items-start justify-between mb-3">
                <div>
                  <p className="heading-4 mb-1">{team.abbreviation}</p>
                  <p className="text-dark-muted text-sm">{team.name}</p>
                </div>
                <div className="text-right">
                  <p className="text-xs text-dark-muted">Record</p>
                  <p className="heading-4 text-nba-gold">{team.wins}-{team.losses}</p>
                </div>
              </div>

              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-dark-muted">City:</span>
                  <span className="text-dark-text font-medium">{team.city}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-dark-muted">Conference:</span>
                  <span className="text-dark-text font-medium">{team.conference}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-dark-muted">Win %:</span>
                  <span className="text-nba-gold font-medium">
                    {((team.wins / (team.wins + team.losses)) * 100).toFixed(1)}%
                  </span>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
