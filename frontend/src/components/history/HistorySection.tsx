import type { SavedPrediction } from '../../types/history';
import { StrategyPerformance } from './StrategyPerformance';
import { HistoryTable } from './HistoryTable';

export function HistorySection({
  entries,
  onUpdateEntry,
}: {
  entries: SavedPrediction[];
  onUpdateEntry: (id: string, patch: Partial<SavedPrediction>) => void;
}) {
  return (
    <div className="space-y-6">
      <StrategyPerformance entries={entries} />
      <HistoryTable entries={entries} onUpdateEntry={onUpdateEntry} />
    </div>
  );
}
