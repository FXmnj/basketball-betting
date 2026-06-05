'use client';

export default function PredictionsPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="heading-2 mb-2">🤖 AI Predictions</h1>
        <p className="text-dark-muted">Game predictions and analysis</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="court-card-lg border-yellow-600/50 border-2">
          <div className="text-4xl mb-4">🚀</div>
          <h2 className="heading-3 mb-2">Prediction Engine</h2>
          <p className="text-dark-muted text-sm mb-4">
            Phase 2 will include our advanced prediction engine with:
          </p>
          <ul className="text-dark-muted text-sm space-y-1">
            <li>✨ Win probability calculations</li>
            <li>📊 Score projections</li>
            <li>🎯 Confidence scoring</li>
            <li>💭 Detailed reasoning</li>
            <li>🤖 AI analysis</li>
          </ul>
        </div>

        <div className="court-card-lg border-blue-600/50 border-2">
          <div className="text-4xl mb-4">📊</div>
          <h2 className="heading-3 mb-2">Key Metrics</h2>
          <p className="text-dark-muted text-sm mb-4">
            Predictions will use these NBA metrics:
          </p>
          <ul className="text-dark-muted text-sm space-y-1">
            <li>📈 Offensive Rating (ORtg)</li>
            <li>🛡️ Defensive Rating (DRtg)</li>
            <li>⚡ Pace of Play</li>
            <li>🏠 Home Court Advantage</li>
            <li>😴 Rest Days</li>
            <li>🤕 Injury Impact</li>
          </ul>
        </div>
      </div>

      <div className="court-card-lg">
        <h2 className="heading-3 mb-4">Example Prediction Output (Phase 2)</h2>
        <div className="bg-dark-bg/50 p-4 rounded-lg font-mono text-sm space-y-3">
          <div className="text-nba-gold">Celtics vs Knicks - November 1, 2024</div>
          
          <div className="border-t border-dark-border pt-3">
            <div className="text-nba-accent">Prediction: Celtics 112 - Knicks 107</div>
            <div className="text-green-400 mt-2">Win Probability: 67%</div>
            <div className="text-blue-400">Confidence Score: 82%</div>
          </div>

          <div className="border-t border-dark-border pt-3 text-dark-muted">
            <div className="font-bold mb-2">Reasoning:</div>
            <div className="space-y-1 text-xs">
              <div>• Celtics have +7.3 Net Rating advantage</div>
              <div>• Knicks on back-to-back (rest disadvantage)</div>
              <div>• Celtics home court (+3-4 pts)</div>
              <div>• Celtics have better recent form (7-1 last 8)</div>
              <div>• Knicks missing key center Porzingis</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
