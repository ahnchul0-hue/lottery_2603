import { LottoBall } from '../LottoBall'

export function HotColdNumbers({
  hot,
  cold,
}: {
  hot: number[]
  cold: number[]
}) {
  return (
    <div>
      <p className="text-sm text-text-secondary mb-2">
        자주 나온 번호 (상위 10개)
      </p>
      <div className="flex flex-wrap gap-2">
        {hot.map((num) => (
          <LottoBall key={num} number={num} />
        ))}
      </div>
      <p className="text-sm text-text-secondary mb-2 mt-4">
        적게 나온 번호 (하위 10개)
      </p>
      <div className="flex flex-wrap gap-2">
        {cold.map((num) => (
          <LottoBall key={num} number={num} />
        ))}
      </div>
    </div>
  )
}
