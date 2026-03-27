import type { HeatmapRow } from '../../types/statistics'

function deviationToColor(dev: number): string {
  const clamped = Math.max(-1, Math.min(1, dev))
  if (clamped >= 0) {
    const factor = Math.round(255 * (1 - clamped))
    return `rgb(255, ${factor}, ${factor})`
  }
  const abs = Math.abs(clamped)
  const factor = Math.round(255 * (1 - abs))
  return `rgb(${factor}, ${factor}, 255)`
}

const NUMBERS = Array.from({ length: 45 }, (_, i) => i + 1)

export function HeatmapGrid({
  data,
  selectedMachine,
}: {
  data: HeatmapRow[]
  selectedMachine: string
}) {
  if (data.length === 0) {
    return (
      <p className="text-sm text-text-secondary text-center py-4">
        히트맵 데이터를 불러올 수 없습니다. 백엔드 서버를 확인하세요.
      </p>
    )
  }

  return (
    <div>
      <div className="overflow-x-auto">
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'auto repeat(45, 1fr)',
            gap: 0,
            minWidth: 600,
          }}
        >
          {/* Header row */}
          <div />
          {NUMBERS.map((num) => (
            <div
              key={`h-${num}`}
              className="text-[10px] text-text-secondary text-center"
            >
              {num}
            </div>
          ))}

          {/* Machine rows */}
          {data.map((row) => {
            const isSelected = row.machine === selectedMachine
            return (
              <div key={row.machine} className="contents">
                <div
                  className={`text-xs font-bold pr-1 flex items-center ${
                    isSelected ? 'text-accent' : 'text-text-primary'
                  }`}
                >
                  {row.machine}
                </div>
                {NUMBERS.map((num) => {
                  const dev = row.deviations[String(num)] ?? 0
                  return (
                    <div
                      key={`${row.machine}-${num}`}
                      className={`border border-border ${
                        isSelected
                          ? 'outline outline-2 outline-accent'
                          : ''
                      }`}
                      style={{
                        backgroundColor: deviationToColor(dev),
                        height: 24,
                      }}
                      title={`${row.machine} - ${num}번: 편차 ${(dev * 100).toFixed(1)}%`}
                    />
                  )
                })}
              </div>
            )
          })}
        </div>
      </div>

      {/* Legend */}
      <div className="flex items-center gap-4 mt-3 text-xs text-text-secondary">
        <div className="flex items-center gap-1">
          <div
            className="inline-block border border-border"
            style={{
              width: 16,
              height: 16,
              backgroundColor: 'rgb(255, 100, 100)',
            }}
          />
          <span>편중 (빨강)</span>
        </div>
        <div className="flex items-center gap-1">
          <div
            className="inline-block border border-border"
            style={{
              width: 16,
              height: 16,
              backgroundColor: 'rgb(255, 255, 255)',
            }}
          />
          <span>기대치 (흰색)</span>
        </div>
        <div className="flex items-center gap-1">
          <div
            className="inline-block border border-border"
            style={{
              width: 16,
              height: 16,
              backgroundColor: 'rgb(100, 100, 255)',
            }}
          />
          <span>부족 (파랑)</span>
        </div>
      </div>
    </div>
  )
}
