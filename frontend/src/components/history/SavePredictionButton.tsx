import { useState } from 'react';

export function SavePredictionButton({
  onSave,
  disabled,
}: {
  onSave: (roundNumber: number) => void;
  disabled: boolean;
}) {
  const [roundNumber, setRoundNumber] = useState('');
  const [saved, setSaved] = useState(false);

  const handleSave = () => {
    const num = parseInt(roundNumber, 10);
    if (isNaN(num) || num < 800 || num > 9999) return;
    onSave(num);
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
    setRoundNumber('');
  };

  return (
    <div className="flex items-center gap-3 mt-4 justify-end">
      <label className="text-sm text-text-secondary">회차 번호:</label>
      <input
        type="number"
        min={800}
        max={9999}
        value={roundNumber}
        onChange={e => setRoundNumber(e.target.value)}
        placeholder="예: 1216"
        className="w-24 h-10 px-4 border border-border rounded-lg text-sm text-right"
      />
      <button
        onClick={handleSave}
        disabled={disabled || !roundNumber || saved}
        className="px-6 py-2 bg-accent text-white font-bold rounded-lg hover:bg-accent/90 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
      >
        {saved ? '저장 완료' : '예측 저장'}
      </button>
    </div>
  );
}
