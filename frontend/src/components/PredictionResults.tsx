import type { PredictResponse } from '../types/lottery'
import { StrategySection } from './StrategySection'

export function PredictionResults({
  results,
}: {
  results: PredictResponse[]
}) {
  return (
    <section>
      <h2 className="text-lg font-bold text-text-primary mb-4">예측 결과</h2>
      <div className="space-y-4">
        {results.map((result) => (
          <StrategySection
            key={result.strategy}
            strategy={result.strategy}
            games={result.games}
          />
        ))}
      </div>
    </section>
  )
}
