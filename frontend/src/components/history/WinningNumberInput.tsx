import { useRef, useState, useCallback } from 'react';

export function WinningNumberInput({
  onSubmit,
}: {
  onSubmit: (numbers: number[]) => void;
}) {
  const [values, setValues] = useState<string[]>(Array(6).fill(''));
  const inputRefs = useRef<(HTMLInputElement | null)[]>([]);

  const handleChange = useCallback((index: number, value: string) => {
    const cleaned = value.replace(/\D/g, '');
    const num = parseInt(cleaned, 10);
    if (cleaned && (num < 1 || num > 45)) return;

    setValues(prev => {
      const next = [...prev];
      next[index] = cleaned;
      return next;
    });

    // Auto-advance: 2 digits or single digit > 4 (can't be prefix of valid number)
    if (cleaned.length === 2 || (cleaned.length === 1 && num > 4)) {
      inputRefs.current[index + 1]?.focus();
    }
  }, []);

  const handleKeyDown = useCallback((index: number, e: React.KeyboardEvent) => {
    if (e.key === 'Backspace' && values[index] === '' && index > 0) {
      inputRefs.current[index - 1]?.focus();
    }
  }, [values]);

  const numbers = values.map(v => parseInt(v, 10)).filter(n => !isNaN(n) && n >= 1 && n <= 45);
  const isValid = numbers.length === 6 && new Set(numbers).size === 6;

  const handleSubmit = () => {
    if (!isValid) return;
    onSubmit([...numbers].sort((a, b) => a - b));
    setValues(Array(6).fill(''));
  };

  return (
    <div>
      <p className="text-sm font-bold text-text-primary mb-2">실제 당첨번호 입력</p>
      <div className="flex items-center gap-2 flex-wrap">
        {Array.from({ length: 6 }, (_, i) => (
          <input
            key={i}
            ref={el => { inputRefs.current[i] = el; }}
            type="text"
            inputMode="numeric"
            maxLength={2}
            value={values[i]}
            onChange={e => handleChange(i, e.target.value)}
            onKeyDown={e => handleKeyDown(i, e)}
            className="w-12 h-12 text-center border border-border rounded-lg text-lg font-bold focus:border-accent focus:outline-none"
            placeholder="1-45"
          />
        ))}
        <button
          onClick={handleSubmit}
          disabled={!isValid}
          className="px-4 py-2 bg-accent text-white font-bold rounded-lg hover:bg-accent/90 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          번호 비교
        </button>
      </div>
    </div>
  );
}
