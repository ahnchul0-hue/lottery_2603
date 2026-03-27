import type { ComparisonResult } from '../../types/history';

export function FailureAnalysis({ comparison }: { comparison: ComparisonResult }) {
  if (comparison.missedNumbers.length === 0 && comparison.overestimatedNumbers.length === 0) {
    return null;
  }

  return (
    <div className="bg-card rounded-xl border border-border p-4 mt-4">
      <h4 className="text-base font-bold text-text-primary mb-4">실패 분석</h4>
      {comparison.missedNumbers.length > 0 && (
        <div className="mb-3">
          <span className="text-sm font-bold text-text-primary">누락 번호: </span>
          <span className="text-sm text-text-secondary">
            {comparison.missedNumbers.join(', ')}
          </span>
        </div>
      )}
      {comparison.overestimatedNumbers.length > 0 && (
        <div>
          <span className="text-sm font-bold text-text-primary">과대평가 번호: </span>
          <span className="text-sm text-text-secondary">
            {comparison.overestimatedNumbers.join(', ')}
          </span>
        </div>
      )}
    </div>
  );
}
