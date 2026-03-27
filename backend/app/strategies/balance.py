"""Balance-based prediction strategy.

Generates lottery number predictions satisfying both odd/even AND
high/low ratio targets simultaneously, based on machine-specific
historical ratio profiles with time-decay weighting.

Per research decisions:
- D-05: Odd/even and high/low ratio targeting from machine profile
- D-06: Simultaneous satisfaction of both constraints via category partition
- D-07: No two games share 4+ numbers (diversity)
- D-08: Fallback to best candidate after MAX_DIVERSITY_ATTEMPTS
- D-10: MIN_WEIGHT_FLOOR prevents zero-probability numbers
"""

import random

from app.config import settings
from app.schemas.lottery import LotteryDraw
from app.strategies.base import PredictionStrategy

# Number space partitions (Korean lotto convention: Low=1-22, High=23-45)
ODD_LOW: list[int] = [n for n in range(1, 23) if n % 2 == 1]
# {1,3,5,7,9,11,13,15,17,19,21} = 11 numbers
ODD_HIGH: list[int] = [n for n in range(23, 46) if n % 2 == 1]
# {23,25,27,29,31,33,35,37,39,41,43,45} = 12 numbers
EVEN_LOW: list[int] = [n for n in range(1, 23) if n % 2 == 0]
# {2,4,6,8,10,12,14,16,18,20,22} = 11 numbers
EVEN_HIGH: list[int] = [n for n in range(23, 46) if n % 2 == 0]
# {24,26,28,30,32,34,36,38,40,42,44} = 11 numbers


def compute_category_counts(
    odd_count: int, even_count: int, high_count: int, low_count: int
) -> dict[str, int]:
    """Compute per-category counts satisfying both constraints simultaneously.

    Given target odd:even and high:low ratios, distributes 6 numbers into
    4 categories: odd_low, odd_high, even_low, even_high.

    Args:
        odd_count: Target number of odd numbers (from odd:even ratio).
        even_count: Target number of even numbers.
        high_count: Target number of high numbers (from high:low ratio).
        low_count: Target number of low numbers.

    Returns:
        Dict with keys odd_low, odd_high, even_low, even_high (all >= 0, sum == 6).
    """
    odd_high = min(odd_count, high_count)
    odd_low = odd_count - odd_high
    even_high = high_count - odd_high
    even_low = even_count - even_high
    if even_low < 0:
        adjustment = -even_low
        odd_high -= adjustment
        odd_low += adjustment
        even_high += adjustment
        even_low = 0
    return {
        "odd_low": odd_low,
        "odd_high": odd_high,
        "even_low": even_low,
        "even_high": even_high,
    }


class BalanceStrategy(PredictionStrategy):
    """Prediction strategy based on odd/even and high/low balance.

    Targets specific odd:even and high:low ratios derived from
    machine-specific historical data with time-decay weighting.
    Satisfies both constraints simultaneously via 4-category partition.
    """

    NUM_GAMES: int = 5
    NUMBERS_PER_GAME: int = 6
    MAX_OVERLAP: int = 3
    MAX_DIVERSITY_ATTEMPTS: int = 100
    MIN_WEIGHT_FLOOR: float = 0.001
    MAX_RATIO_ATTEMPTS: int = 50

    @property
    def name(self) -> str:
        return "balance"

    @property
    def display_name(self) -> str:
        return "밸런스 전략"

    def generate(
        self,
        draws: list[LotteryDraw],
        weighted_frequencies: dict[int, float],
    ) -> list[list[int]]:
        """Generate 5 diverse games satisfying odd/even and high/low targets.

        Algorithm:
        1. Build weighted frequency distributions of odd:even and high:low ratios
        2. For each game, probabilistically select target ratios
        3. Compute 4-category partition (odd_low, odd_high, even_low, even_high)
        4. Select numbers from each category weighted by weighted_frequencies
        5. Enforce diversity constraint across games

        Args:
            draws: Machine-filtered draws sorted by round_number ascending.
            weighted_frequencies: Dict mapping number (1-45) -> weighted frequency.

        Returns:
            List of 5 games, each with 6 unique sorted numbers in [1, 45].
        """
        oe_dist = self._build_ratio_distribution(draws, "odd_even")
        hl_dist = self._build_ratio_distribution(draws, "high_low")

        return self._generate_diverse_games(
            oe_dist, hl_dist, weighted_frequencies
        )

    def _build_ratio_distribution(
        self,
        draws: list[LotteryDraw],
        ratio_type: str,
    ) -> dict[tuple[int, int], float]:
        """Build weighted frequency distribution of a ratio type.

        Args:
            draws: Machine-filtered draws sorted ascending by round_number.
            ratio_type: Either "odd_even" or "high_low".

        Returns:
            Dict mapping (a, b) ratio tuple -> cumulative decay-weighted frequency.
        """
        n = len(draws)
        if n == 0:
            # Fallback to balanced 3:3
            return {(3, 3): 1.0}

        halflife = settings.DECAY_HALFLIFE
        decay_weights = [
            0.5 ** ((n - 1 - i) / halflife) for i in range(n)
        ]

        dist: dict[tuple[int, int], float] = {}
        for draw, dw in zip(draws, decay_weights):
            raw = (
                draw.odd_even_ratio if ratio_type == "odd_even"
                else draw.high_low_ratio
            )
            parts = raw.split(":")
            ratio_tuple = (int(parts[0]), int(parts[1]))
            dist[ratio_tuple] = dist.get(ratio_tuple, 0.0) + dw

        return dist

    def _sample_ratio(
        self, dist: dict[tuple[int, int], float]
    ) -> tuple[int, int]:
        """Probabilistically select a ratio from the distribution.

        Args:
            dist: Ratio -> weighted frequency mapping.

        Returns:
            Selected (a, b) ratio tuple.
        """
        ratios = list(dist.keys())
        weights = list(dist.values())
        return random.choices(ratios, weights=weights, k=1)[0]

    def _generate_single_game(
        self,
        oe_dist: dict[tuple[int, int], float],
        hl_dist: dict[tuple[int, int], float],
        weighted_frequencies: dict[int, float],
    ) -> list[int]:
        """Generate a single game satisfying odd/even and high/low targets.

        Retries up to MAX_RATIO_ATTEMPTS if the selected ratio combination
        produces infeasible category counts.

        Args:
            oe_dist: Odd/even ratio distribution.
            hl_dist: High/low ratio distribution.
            weighted_frequencies: Number -> weighted frequency mapping.

        Returns:
            Sorted list of 6 unique numbers in [1, 45].
        """
        for _ in range(self.MAX_RATIO_ATTEMPTS):
            odd_count, even_count = self._sample_ratio(oe_dist)
            high_count, low_count = self._sample_ratio(hl_dist)

            # Ensure they sum to 6
            if odd_count + even_count != 6 or high_count + low_count != 6:
                continue

            counts = compute_category_counts(
                odd_count, even_count, high_count, low_count
            )

            # Validate: all non-negative and sum == 6
            if any(v < 0 for v in counts.values()):
                continue
            if sum(counts.values()) != 6:
                continue

            # Check feasibility: each category has enough available numbers
            category_pools = {
                "odd_low": ODD_LOW,
                "odd_high": ODD_HIGH,
                "even_low": EVEN_LOW,
                "even_high": EVEN_HIGH,
            }
            feasible = all(
                counts[cat] <= len(category_pools[cat])
                for cat in counts
            )
            if not feasible:
                continue

            # Select numbers from each category
            selected: list[int] = []
            for cat_name, pool in category_pools.items():
                cat_count = counts[cat_name]
                if cat_count <= 0:
                    continue

                cat_weights = [
                    max(weighted_frequencies.get(n, 0.0), self.MIN_WEIGHT_FLOOR)
                    for n in pool
                ]

                picks: set[int] = set()
                safety = 0
                while len(picks) < cat_count and safety < 200:
                    pick = random.choices(pool, weights=cat_weights, k=1)[0]
                    picks.add(pick)
                    safety += 1

                selected.extend(picks)

            if len(selected) == self.NUMBERS_PER_GAME:
                return sorted(selected)

        # Ultimate fallback: random 6 numbers weighted by frequencies
        population = list(range(1, 46))
        weights = [
            max(weighted_frequencies.get(n, 0.0), self.MIN_WEIGHT_FLOOR)
            for n in population
        ]
        picked: set[int] = set()
        while len(picked) < self.NUMBERS_PER_GAME:
            p = random.choices(population, weights=weights, k=1)[0]
            picked.add(p)
        return sorted(picked)

    def _generate_diverse_games(
        self,
        oe_dist: dict[tuple[int, int], float],
        hl_dist: dict[tuple[int, int], float],
        weighted_frequencies: dict[int, float],
    ) -> list[list[int]]:
        """Generate NUM_GAMES games with diversity constraint.

        For each game, attempts up to MAX_DIVERSITY_ATTEMPTS candidates.
        Rejects any candidate sharing MAX_OVERLAP+1 or more numbers
        with any existing game. Tracks the best candidate (lowest
        max overlap) as a fallback.

        Args:
            oe_dist: Odd/even ratio distribution.
            hl_dist: High/low ratio distribution.
            weighted_frequencies: Number -> weighted frequency mapping.

        Returns:
            List of NUM_GAMES games.
        """
        games: list[list[int]] = []

        for _ in range(self.NUM_GAMES):
            best_candidate: list[int] | None = None
            best_max_overlap: int = self.NUMBERS_PER_GAME + 1

            for _attempt in range(self.MAX_DIVERSITY_ATTEMPTS):
                candidate = self._generate_single_game(
                    oe_dist, hl_dist, weighted_frequencies
                )

                # Check diversity against all existing games
                max_overlap = 0
                for existing in games:
                    overlap = len(set(candidate) & set(existing))
                    max_overlap = max(max_overlap, overlap)

                # Track best candidate
                if max_overlap < best_max_overlap:
                    best_max_overlap = max_overlap
                    best_candidate = candidate

                # Accept if overlap constraint satisfied
                if max_overlap <= self.MAX_OVERLAP:
                    games.append(candidate)
                    break
            else:
                if best_candidate is not None:
                    games.append(best_candidate)

        return games
