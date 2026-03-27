export function MachineCard({
  machineId,
  totalDraws,
  latestRound,
  isSelected,
  onSelect,
  isLoading,
}: {
  machineId: string
  totalDraws: number
  latestRound: number
  isSelected: boolean
  onSelect: () => void
  isLoading: boolean
}) {
  return (
    <button
      type="button"
      onClick={onSelect}
      className={`flex-1 p-4 rounded-xl border-2 bg-card transition-colors cursor-pointer ${
        isSelected
          ? 'border-accent shadow-md'
          : 'border-border hover:border-accent/50'
      }`}
    >
      <div className="text-2xl font-bold text-text-primary mb-2">
        {machineId}
      </div>
      {isLoading ? (
        <p className="text-text-secondary text-sm">로딩 중...</p>
      ) : (
        <div className="space-y-1 text-sm text-text-secondary">
          <p>추첨 횟수: {totalDraws}회</p>
          <p>최근 회차: {latestRound}회</p>
        </div>
      )}
    </button>
  )
}
