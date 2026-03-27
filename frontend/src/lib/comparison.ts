import type { ComparisonResult, GameComparison, StrategyHitRate } from '../types/history';

export function comparePredictions(
  predictions: { strategy: string; games: number[][] }[],
  actualNumbers: number[],
): ComparisonResult {
  const actualSet = new Set(actualNumbers);
  const games: GameComparison[] = [];

  for (const pred of predictions) {
    for (let i = 0; i < pred.games.length; i++) {
      const matched = pred.games[i].filter(n => actualSet.has(n));
      games.push({
        strategy: pred.strategy,
        gameIndex: i + 1,
        predicted: pred.games[i],
        matchedNumbers: matched,
        matchCount: matched.length,
      });
    }
  }

  // Strategy hit rates: group by strategy, compute avg and best
  const strategyMap = new Map<string, { total: number; count: number; best: number }>();
  for (const g of games) {
    const entry = strategyMap.get(g.strategy) ?? { total: 0, count: 0, best: 0 };
    entry.total += g.matchCount;
    entry.count += 1;
    entry.best = Math.max(entry.best, g.matchCount);
    strategyMap.set(g.strategy, entry);
  }

  const strategyHitRates: StrategyHitRate[] = Array.from(strategyMap.entries()).map(
    ([strategy, { total, count, best }]) => ({
      strategy,
      avgMatches: Math.round((total / count) * 10) / 10,
      bestMatch: best,
      totalGames: count,
    }),
  );

  // Missed numbers: in actual but not predicted by ANY game
  const allPredicted = new Set(games.flatMap(g => g.predicted));
  const missedNumbers = actualNumbers.filter(n => !allPredicted.has(n));

  // Overestimated: predicted in 50%+ of games but not in actual
  const predCounts = new Map<number, number>();
  for (const g of games) {
    for (const n of g.predicted) {
      predCounts.set(n, (predCounts.get(n) ?? 0) + 1);
    }
  }
  const threshold = games.length * 0.5;
  const overestimatedNumbers = Array.from(predCounts.entries())
    .filter(([n, count]) => count >= threshold && !actualSet.has(n))
    .map(([n]) => n)
    .sort((a, b) => a - b);

  return { games, strategyHitRates, missedNumbers, overestimatedNumbers };
}
