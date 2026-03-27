"""Frequency-based prediction strategy.

Generates lottery number predictions weighted by DecayEngine's
weighted frequencies. Higher-frequency numbers are more likely
to be selected, with a diversity constraint ensuring game variety.

Per research decisions:
- D-01: random.choices with weighted selection
- D-02: 6 unique numbers per game
- D-03: Numbers sorted ascending
- D-07: No two games share 4+ numbers (diversity)
- D-08: Fallback to best candidate after MAX_DIVERSITY_ATTEMPTS
- D-10: MIN_WEIGHT_FLOOR prevents zero-probability numbers
"""

import random

from app.schemas.lottery import LotteryDraw
from app.strategies.base import PredictionStrategy


class FrequencyStrategy(PredictionStrategy):
    """Prediction strategy based on weighted number frequencies.

    Generates NUM_GAMES games, each with NUMBERS_PER_GAME unique numbers.
    Selection is biased by weighted frequencies from DecayEngine.
    Diversity constraint ensures no two games share MAX_OVERLAP or more numbers.
    """

    NUM_GAMES: int = 5
    NUMBERS_PER_GAME: int = 6
    MAX_OVERLAP: int = 3
    MAX_DIVERSITY_ATTEMPTS: int = 100
    MIN_WEIGHT_FLOOR: float = 0.001

    @property
    def name(self) -> str:
        return "frequency"

    @property
    def display_name(self) -> str:
        return "빈도 전략"

    def generate(
        self,
        draws: list[LotteryDraw],
        weighted_frequencies: dict[int, float],
    ) -> list[list[int]]:
        """Generate 5 diverse game sets using weighted frequency selection.

        Args:
            draws: Machine-filtered draws (unused directly, available for subclasses).
            weighted_frequencies: Dict mapping number (1-45) -> weighted frequency.

        Returns:
            List of 5 games, each with 6 unique sorted numbers in [1, 45].
        """
        population = list(range(1, 46))
        weights = [
            max(weighted_frequencies.get(n, 0.0), self.MIN_WEIGHT_FLOOR)
            for n in population
        ]
        return self._generate_diverse_games(population, weights)

    def _select_unique(
        self, population: list[int], weights: list[float]
    ) -> list[int]:
        """Select 6 unique numbers using weighted random selection.

        Uses random.choices in a loop to collect unique numbers,
        respecting the weight distribution.

        Args:
            population: List of candidate numbers (1-45).
            weights: Corresponding weights for each number.

        Returns:
            Sorted list of 6 unique numbers.
        """
        selected: set[int] = set()
        while len(selected) < self.NUMBERS_PER_GAME:
            pick = random.choices(population, weights=weights, k=1)[0]
            selected.add(pick)
        return sorted(selected)

    def _generate_diverse_games(
        self, population: list[int], weights: list[float]
    ) -> list[list[int]]:
        """Generate NUM_GAMES games with diversity constraint.

        For each game, attempts up to MAX_DIVERSITY_ATTEMPTS candidates.
        Rejects any candidate sharing MAX_OVERLAP+1 or more numbers
        with any existing game. Tracks the best candidate (lowest
        max overlap) as a fallback.

        Args:
            population: List of candidate numbers (1-45).
            weights: Corresponding weights for each number.

        Returns:
            List of NUM_GAMES games.
        """
        games: list[list[int]] = []

        for _ in range(self.NUM_GAMES):
            best_candidate: list[int] | None = None
            best_max_overlap: int = self.NUMBERS_PER_GAME + 1

            for _attempt in range(self.MAX_DIVERSITY_ATTEMPTS):
                candidate = self._select_unique(population, weights)

                # Check diversity against all existing games
                max_overlap = 0
                for existing in games:
                    overlap = len(set(candidate) & set(existing))
                    max_overlap = max(max_overlap, overlap)

                # Track best candidate (lowest max overlap)
                if max_overlap < best_max_overlap:
                    best_max_overlap = max_overlap
                    best_candidate = candidate

                # Accept if overlap constraint satisfied
                if max_overlap <= self.MAX_OVERLAP:
                    games.append(candidate)
                    break
            else:
                # After all attempts, use the best candidate found
                if best_candidate is not None:
                    games.append(best_candidate)

        return games
