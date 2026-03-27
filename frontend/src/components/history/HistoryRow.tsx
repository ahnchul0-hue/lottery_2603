import { useState } from 'react';
import type { SavedPrediction } from '../../types/history';
import { comparePredictions } from '../../lib/comparison';
import { WinningNumberInput } from './WinningNumberInput';
import { ComparisonTable } from './ComparisonTable';
import { FailureAnalysis } from './FailureAnalysis';
import { AiReflection } from './AiReflection';
import { useReflection } from '../../hooks/useReflection';

export function HistoryRow({
  entry,
  onUpdate,
  allEntries,
}: {
  entry: SavedPrediction;
  onUpdate: (patch: Partial<SavedPrediction>) => void;
  allEntries: SavedPrediction[];
}) {
  const [expanded, setExpanded] = useState(false);
  const reflection = useReflection();

  const bestMatch = entry.comparison
    ? Math.max(...entry.comparison.games.map(g => g.matchCount))
    : null;

  const handleCompare = (actualNumbers: number[]) => {
    const comparison = comparePredictions(entry.predictions, actualNumbers);
    onUpdate({ actualNumbers, comparison });
  };

  const handleGenerateReflection = () => {
    if (!entry.comparison) return;

    // D-14: Only same-machine past reflections
    const pastReflections = allEntries
      .filter(e => e.machine === entry.machine && e.aiReflection && e.id !== entry.id)
      .slice(0, 3)
      .map(e => e.aiReflection!);

    reflection.mutate(
      {
        machine: entry.machine,
        roundNumber: entry.roundNumber,
        comparisonData: entry.comparison,
        pastReflections: pastReflections.length > 0 ? pastReflections : undefined,
      },
      {
        onSuccess: (text) => {
          onUpdate({ aiReflection: text });
        },
      },
    );
  };

  return (
    <>
      <tr
        onClick={() => setExpanded(!expanded)}
        className="border-b border-border cursor-pointer hover:bg-surface transition-colors"
      >
        <td className="py-2 px-4 text-right">{entry.roundNumber}</td>
        <td className="py-2 px-4 text-center">{entry.machine}</td>
        <td className="py-2 px-4">{entry.date}</td>
        <td className="py-2 px-4 text-center">{bestMatch !== null ? bestMatch : '-'}</td>
        <td className="py-2 px-4 text-center">{entry.aiReflection ? 'O' : '-'}</td>
      </tr>
      {expanded && (
        <tr>
          <td colSpan={5} className="p-4 border-b border-border border-l-4 border-l-accent">
            {!entry.comparison && (
              <WinningNumberInput onSubmit={handleCompare} />
            )}
            {entry.comparison && (
              <>
                <ComparisonTable comparison={entry.comparison} />
                <FailureAnalysis comparison={entry.comparison} />
                <AiReflection
                  reflection={entry.aiReflection}
                  isLoading={reflection.isPending}
                  error={reflection.isError ? reflection.error.message : undefined}
                  onGenerate={handleGenerateReflection}
                />
              </>
            )}
            {!entry.comparison && (
              <p className="text-sm text-text-secondary mt-2">
                당첨번호를 입력하면 비교 결과가 표시됩니다
              </p>
            )}
          </td>
        </tr>
      )}
    </>
  );
}
