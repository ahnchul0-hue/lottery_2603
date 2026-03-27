export function AiReflection({
  reflection,
  isLoading,
  error,
  onGenerate,
}: {
  reflection?: string;
  isLoading: boolean;
  error?: string;
  onGenerate: () => void;
}) {
  if (reflection) {
    return (
      <div className="bg-surface rounded-lg p-4 mt-4">
        <h4 className="text-base font-bold text-text-primary mb-2">AI 반성 메모</h4>
        <p className="text-sm text-text-primary leading-relaxed whitespace-pre-wrap">
          {reflection}
        </p>
      </div>
    );
  }

  return (
    <div className="mt-4">
      <button
        onClick={onGenerate}
        disabled={isLoading}
        className="px-4 py-2 bg-accent text-white rounded-lg hover:bg-accent/90 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
      >
        {isLoading ? 'AI 분석 중...' : 'AI 분석 생성'}
      </button>
      {error && (
        <p className="text-sm text-destructive mt-2">
          AI 분석을 생성할 수 없습니다. API 키를 확인하세요.
        </p>
      )}
    </div>
  );
}
