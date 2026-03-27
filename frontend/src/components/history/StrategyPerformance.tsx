import type { SavedPrediction } from '../../types/history';
import { STRATEGY_LABELS } from '../../types/lottery';

export function StrategyPerformance({ entries }: { entries: SavedPrediction[] }) {
  const withComparison = entries.filter(e => e.comparison);
  if (withComparison.length === 0) return null;

  // Aggregate across all entries with comparisons
  const strategyStats = new Map<string, { totalMatches: number; totalGames: number; best: number }>();

  for (const entry of withComparison) {
    if (!entry.comparison) continue;
    for (const hr of entry.comparison.strategyHitRates) {
      const stats = strategyStats.get(hr.strategy) ?? { totalMatches: 0, totalGames: 0, best: 0 };
      // avgMatches * totalGames gives total matches for that entry's strategy
      stats.totalMatches += hr.avgMatches * hr.totalGames;
      stats.totalGames += hr.totalGames;
      stats.best = Math.max(stats.best, hr.bestMatch);
      strategyStats.set(hr.strategy, stats);
    }
  }

  const rows = Array.from(strategyStats.entries()).map(([strategy, stats]) => ({
    strategy,
    label: STRATEGY_LABELS[strategy] ?? strategy,
    avgMatches: Math.round((stats.totalMatches / stats.totalGames) * 10) / 10,
    bestMatch: stats.best,
    totalPredictions: withComparison.length,
  }));

  const bestAvg = Math.max(...rows.map(r => r.avgMatches));

  return (
    <div className="bg-card rounded-xl border border-border p-4">
      <h3 className="text-base font-bold text-text-primary mb-4">전략별 성과</h3>
      <table className="w-full text-sm">
        <thead>
          <tr className="bg-surface text-text-secondary font-bold">
            <th className="py-2 px-4 text-left">전략</th>
            <th className="py-2 px-4 text-right">평균 일치</th>
            <th className="py-2 px-4 text-right">최고 적중</th>
            <th className="py-2 px-4 text-right">예측 횟수</th>
          </tr>
        </thead>
        <tbody>
          {rows.map(row => (
            <tr
              key={row.strategy}
              className={`border-b border-border ${row.avgMatches === bestAvg ? 'bg-accent/5 font-bold' : ''}`}
            >
              <td className="py-2 px-4">{row.label}</td>
              <td className="py-2 px-4 text-right">{row.avgMatches}</td>
              <td className="py-2 px-4 text-right">{row.bestMatch}</td>
              <td className="py-2 px-4 text-right">{row.totalPredictions}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
