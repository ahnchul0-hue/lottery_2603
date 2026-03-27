import { LottoBall } from './LottoBall'

export function GameRow({
  numbers,
  gameIndex,
}: {
  numbers: number[]
  gameIndex: number
}) {
  return (
    <div className="flex items-center gap-3">
      <span className="text-text-secondary text-sm w-16 shrink-0">
        Game {gameIndex}
      </span>
      <div className="flex items-center gap-2">
        {numbers.map((num, i) => (
          <LottoBall key={i} number={num} />
        ))}
      </div>
    </div>
  )
}
