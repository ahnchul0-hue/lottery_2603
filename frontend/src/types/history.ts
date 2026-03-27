// TypeScript types for prediction history system (D-04 storage schema)

export type GameComparison = {
  strategy: string;
  gameIndex: number;
  predicted: number[];
  matchedNumbers: number[];
  matchCount: number;
};

export type StrategyHitRate = {
  strategy: string;
  avgMatches: number;
  bestMatch: number;
  totalGames: number;
};

export type ComparisonResult = {
  games: GameComparison[];
  strategyHitRates: StrategyHitRate[];
  missedNumbers: number[];
  overestimatedNumbers: number[];
};

export type SavedPrediction = {
  id: string;
  roundNumber: number;
  machine: string;
  date: string;
  predictions: {
    strategy: string;
    games: number[][];
  }[];
  actualNumbers?: number[];
  comparison?: ComparisonResult;
  aiReflection?: string;
};
