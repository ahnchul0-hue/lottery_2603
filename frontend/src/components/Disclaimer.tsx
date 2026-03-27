export function Disclaimer() {
  return (
    <footer className="mt-12 pb-8 text-center">
      <div className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-card border border-border">
        <svg
          xmlns="http://www.w3.org/2000/svg"
          className="w-4 h-4 text-text-secondary shrink-0"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
          strokeWidth={2}
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
          />
        </svg>
        <p className="text-xs text-text-secondary">
          본 서비스는 통계 분석 도구이며, 당첨을 보장하지 않습니다. 로또는 완전한 확률 게임입니다.
        </p>
      </div>
    </footer>
  )
}
