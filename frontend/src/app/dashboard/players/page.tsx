'use client';

export default function PlayersPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="heading-2 mb-2">👥 NBA Players</h1>
        <p className="text-dark-muted">Browse player statistics and performance</p>
      </div>

      <div className="court-card-lg text-center py-12">
        <div className="text-4xl mb-4">🏗️</div>
        <h2 className="heading-3 mb-2">Coming in Phase 2</h2>
        <p className="text-dark-muted mb-4">
          Player analysis and comparison tools are being built.
        </p>
        <p className="text-sm text-dark-muted">
          This feature will include:
        </p>
        <ul className="text-dark-muted text-sm mt-3 space-y-1">
          <li>📊 Detailed player statistics</li>
          <li>📈 Performance trends and comparisons</li>
          <li>⭐ Player ratings and rankings</li>
          <li>🏆 Career highlights</li>
        </ul>
      </div>
    </div>
  );
}
