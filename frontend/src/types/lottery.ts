// TypeScript interfaces matching backend Pydantic schemas exactly

export type LotteryDraw = {
  round_number: number;
  machine: string;
  numbers: number[];
  odd_even_ratio: string;
  high_low_ratio: string;
  ac_value: number;
  tail_sum: number;
  total_sum: number;
};

export type MachineDataResponse = {
  machine: string;
  total_draws: number;
  draws: LotteryDraw[];
};

export type PredictResponse = {
  games: number[][];
  strategy: string;
  machine: string;
};

// Client-side convenience type derived from MachineDataResponse
export type MachineInfo = {
  machine: string;
  totalDraws: number;
  latestRound: number;
};

// Runtime constants
export const MACHINE_IDS = ['1호기', '2호기', '3호기'] as const;

export const STRATEGIES = [
  'frequency',
  'pattern',
  'range',
  'balance',
  'composite',
] as const;

export const STRATEGY_LABELS: Record<string, string> = {
  frequency: 'Frequency (빈도)',
  pattern: 'Pattern (패턴)',
  range: 'Range (구간)',
  balance: 'Balance (밸런스)',
  composite: 'Composite (종합)',
};
