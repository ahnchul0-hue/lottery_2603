import type { ComparisonResult } from '../../types/history';
import { STRATEGY_LABELS } from '../../types/lottery';

function getMatchBg(matchCount: number): string {
  if (matchCount >= 5) return 'bg-success/20 font-bold';
  if (matchCount >= 3) return 'bg-success/10';
  if (matchCount >= 1) return 'bg-accent/5';
  return '';
}

export function ComparisonTable({ comparison }: { comparison: ComparisonResult }) {
  const strategies = [...new Set(comparison.games.map(g => g.strategy))];

  return (
    <div>
      <h4 className="text-base font-bold text-text-primary mb-2">비교 결과</h4>
      <table className="w-full text-sm text-text-primary">
        <thead>
          <tr className="bg-surface text-text-secondary font-bold">
            <th className="py-2 px-2 text-left">전략</th>
            <th className="py-2 px-2 text-center">게임</th>
            <th className="py-2 px-2 text-left">예측 번호</th>
            <th className="py-2 px-2 text-right font-mono">일치</th>
            <th className="py-2 px-2 text-left">일치 번호</th>
          </tr>
        </thead>
        {strategies.map(strategy => {
          const strategyGames = comparison.games.filter(g => g.strategy === strategy);
          const hitRate = comparison.strategyHitRates.find(r => r.strategy === strategy);
          const label = STRATEGY_LABELS[strategy] ?? strategy;

          return (
            <tbody key={strategy}>
              {strategyGames.map(game => (
                <tr key={`${strategy}-${game.gameIndex}`} className={getMatchBg(game.matchCount)}>
                  <td className="py-2 px-2">{game.gameIndex === 1 ? label : ''}</td>
                  <td className="py-2 px-2 text-center">{game.gameIndex}</td>
                  <td className="py-2 px-2">{game.predicted.join(', ')}</td>
                  <td className="py-2 px-2 text-right font-mono">{game.matchCount}</td>
                  <td className="py-2 px-2">{game.matchedNumbers.join(', ')}</td>
                </tr>
              ))}
              {hitRate && (
                <tr className="font-bold border-t-2 border-border">
                  <td className="py-2 px-2">{label} 적중률</td>
                  <td className="py-2 px-2" />
                  <td className="py-2 px-2" />
                  <td className="py-2 px-2 text-right font-mono">{hitRate.avgMatches}</td>
                  <td className="py-2 px-2" />
                </tr>
              )}
            </tbody>
          );
        })}
      </table>
    </div>
  );
}
