import { GameRow } from './GameRow'
import { STRATEGY_LABELS } from '../types/lottery'

export function StrategySection({
  strategy,
  games,
}: {
  strategy: string
  games: number[][]
}) {
  const label = STRATEGY_LABELS[strategy] ?? strategy

  return (
    <section className="bg-card rounded-xl border border-border p-4">
      <h3 className="text-lg font-semibold text-text-primary mb-3">
        {label}
      </h3>
      <div className="space-y-2">
        {games.map((numbers, i) => (
          <GameRow key={i} numbers={numbers} gameIndex={i + 1} />
        ))}
      </div>
    </section>
  )
}
