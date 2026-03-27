import { getLottoBallColor, formatNumber } from '../lib/lottoBallColor'

export function LottoBall({ number }: { number: number }) {
  return (
    <span
      className="inline-flex items-center justify-center w-10 h-10 rounded-full text-sm font-bold text-white shadow-sm"
      style={{ backgroundColor: getLottoBallColor(number) }}
    >
      {formatNumber(number)}
    </span>
  )
}
