import type { SavedPrediction } from '../../types/history';
import { HistoryRow } from './HistoryRow';

export function HistoryTable({
  entries,
  onUpdateEntry,
}: {
  entries: SavedPrediction[];
  onUpdateEntry: (id: string, patch: Partial<SavedPrediction>) => void;
}) {
  if (entries.length === 0) {
    return (
      <div className="text-center py-8">
        <p className="text-base font-bold text-text-primary">저장된 예측이 없습니다</p>
        <p className="text-sm text-text-secondary mt-2">
          예측 결과를 저장하면 이력이 여기에 표시됩니다
        </p>
      </div>
    );
  }

  return (
    <table className="w-full text-sm text-text-primary">
      <thead>
        <tr className="bg-surface text-text-secondary font-bold">
          <th className="py-2 px-4 text-right">회차</th>
          <th className="py-2 px-4 text-center">호기</th>
          <th className="py-2 px-4 text-left">날짜</th>
          <th className="py-2 px-4 text-center">최고 적중</th>
          <th className="py-2 px-4 text-center">반성</th>
        </tr>
      </thead>
      <tbody>
        {entries.map(entry => (
          <HistoryRow
            key={entry.id}
            entry={entry}
            onUpdate={(patch) => onUpdateEntry(entry.id, patch)}
            allEntries={entries}
          />
        ))}
      </tbody>
    </table>
  );
}
