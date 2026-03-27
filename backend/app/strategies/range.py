"""Range-based prediction strategy.

Generates lottery number predictions distributed across 5 number zones
based on machine-specific zone frequency profiles with time-decay weighting.

Per research decisions:
- D-03: Zone distribution matching machine profile
- D-04: Largest-remainder rounding (Hamilton's method) ensures zone counts sum to 6
- D-07: No two games share 4+ numbers (diversity)
- D-08: Fallback to best candidate after MAX_DIVERSITY_ATTEMPTS
- D-10: MIN_WEIGHT_FLOOR prevents zero-probability numbers
"""

import random

from app.config import settings
from app.schemas.lottery import LotteryDraw
from app.strategies.base import PredictionStrategy

# Zone definitions: (start, end) inclusive
ZONES: list[tuple[int, int]] = [
    (1, 9),    # Zone 1: 9 numbers
    (10, 19),  # Zone 2: 10 numbers
    (20, 29),  # Zone 3: 10 numbers
    (30, 39),  # Zone 4: 10 numbers
    (40, 45),  # Zone 5: 6 numbers
]


def round_to_sum(ratios: list[float], target: int = 6) -> list[int]:
    """Round floating ratios to integers that sum exactly to target.

    Uses largest-remainder method (Hamilton's method):
    1. Floor all ratios
    2. Compute deficit = target - sum(floors)
    3. Distribute deficit to zones with largest fractional remainders

    Args:
        ratios: Floating-point zone ratios (should sum to ~target).
        target: Required integer sum (default 6 for 6 numbers per game).

    Returns:
        List of integers summing to exactly target.
    """
    floors = [int(r) for r in ratios]
    remainders = [r - f for r, f in zip(ratios, floors)]
    deficit = target - sum(floors)
    indices_by_remainder = sorted(
        range(len(remainders)), key=lambda i: remainders[i], reverse=True
    )
    for i in range(deficit):
        floors[indices_by_remainder[i]] += 1
    return floors


class RangeStrategy(PredictionStrategy):
    """Prediction strategy based on zone distribution.

    Distributes numbers across 5 zones ([1-9], [10-19], [20-29],
    [30-39], [40-45]) matching the machine's historical zone profile.
    Uses largest-remainder rounding to ensure exactly 6 numbers per game.
    """

    NUM_GAMES: int = 5
    NUMBERS_PER_GAME: int = 6
    MAX_OVERLAP: int = 3
    MAX_DIVERSITY_ATTEMPTS: int = 100
    MIN_WEIGHT_FLOOR: float = 0.001

    @property
    def name(self) -> str:
        return "range"

    @property
    def display_name(self) -> str:
        return "구간 전략"

    def generate(
        self,
        draws: list[LotteryDraw],
        weighted_frequencies: dict[int, float],
    ) -> list[list[int]]:
        """Generate 5 diverse games with zone-distributed numbers.

        Algorithm:
        1. Compute zone ratios from machine draws with time-decay weighting
        2. Round to integer counts using largest-remainder method
        3. Select numbers within each zone weighted by weighted_frequencies
        4. Enforce diversity constraint across games

        Args:
            draws: Machine-filtered draws sorted by round_number ascending.
            weighted_frequencies: Dict mapping number (1-45) -> weighted frequency.

        Returns:
            List of 5 games, each with 6 unique sorted numbers in [1, 45].
        """
        zone_counts = self._compute_zone_counts(draws)
        return self._generate_diverse_games(
            zone_counts, weighted_frequencies
        )

    def _compute_zone_counts(self, draws: list[LotteryDraw]) -> list[int]:
        """Compute per-zone integer counts from machine draw history.

        Step 1: Weight each draw by exponential decay.
        Step 2: Count how many numbers per draw fall in each zone.
        Step 3: Normalize so total = 6.0 and round using Hamilton's method.

        Args:
            draws: Machine-filtered draws sorted ascending by round_number.

        Returns:
            List of 5 integers summing to 6 (one per zone).
        """
        n = len(draws)
        if n == 0:
            # Fallback: uniform distribution across zones
            return round_to_sum([1.2, 1.2, 1.2, 1.2, 1.2])

        halflife = settings.DECAY_HALFLIFE
        # Compute per-draw decay weights (newest last = highest weight)
        decay_weights = [
            0.5 ** ((n - 1 - i) / halflife) for i in range(n)
        ]

        zone_weighted_totals = [0.0] * len(ZONES)

        for draw, dw in zip(draws, decay_weights):
            for number in draw.numbers:
                for z_idx, (z_start, z_end) in enumerate(ZONES):
                    if z_start <= number <= z_end:
                        zone_weighted_totals[z_idx] += dw
                        break

        # Normalize so totals sum to 6.0
        total = sum(zone_weighted_totals)
        if total == 0:
            return round_to_sum([1.2, 1.2, 1.2, 1.2, 1.2])

        ratios = [
            (zwt / total) * self.NUMBERS_PER_GAME
            for zwt in zone_weighted_totals
        ]

        return round_to_sum(ratios, target=self.NUMBERS_PER_GAME)

    def _generate_single_game(
        self,
        zone_counts: list[int],
        weighted_frequencies: dict[int, float],
    ) -> list[int]:
        """Generate a single game respecting zone counts.

        For each zone with count > 0, selects that many numbers
        from the zone weighted by weighted_frequencies. Handles
        edge case where a zone has fewer available numbers than needed
        by borrowing from an adjacent zone.

        Args:
            zone_counts: Integer count per zone (sums to 6).
            weighted_frequencies: Dict mapping number -> weighted frequency.

        Returns:
            Sorted list of 6 unique numbers in [1, 45].
        """
        selected: list[int] = []
        overflow: int = 0  # numbers that couldn't fit in their zone

        for z_idx, (z_start, z_end) in enumerate(ZONES):
            count = zone_counts[z_idx] + overflow
            overflow = 0
            if count <= 0:
                continue

            # Build zone population and weights
            zone_numbers = list(range(z_start, z_end + 1))
            # Exclude already-selected numbers
            available = [n for n in zone_numbers if n not in selected]
            if not available:
                overflow += count
                continue

            # Limit count to available numbers
            actual_count = min(count, len(available))
            overflow += count - actual_count

            zone_weights = [
                max(weighted_frequencies.get(n, 0.0), self.MIN_WEIGHT_FLOOR)
                for n in available
            ]

            # Weighted selection of unique numbers within zone
            picks: set[int] = set()
            safety = 0
            while len(picks) < actual_count and safety < 200:
                pick = random.choices(available, weights=zone_weights, k=1)[0]
                picks.add(pick)
                safety += 1

            selected.extend(picks)

        # Handle any remaining overflow by picking from any unused number
        if len(selected) < self.NUMBERS_PER_GAME:
            all_numbers = list(range(1, 46))
            remaining = [n for n in all_numbers if n not in selected]
            remaining_weights = [
                max(weighted_frequencies.get(n, 0.0), self.MIN_WEIGHT_FLOOR)
                for n in remaining
            ]
            while len(selected) < self.NUMBERS_PER_GAME and remaining:
                pick = random.choices(
                    remaining, weights=remaining_weights, k=1
                )[0]
                if pick not in selected:
                    selected.append(pick)

        return sorted(selected[: self.NUMBERS_PER_GAME])

    def _generate_diverse_games(
        self,
        zone_counts: list[int],
        weighted_frequencies: dict[int, float],
    ) -> list[list[int]]:
        """Generate NUM_GAMES games with diversity constraint.

        For each game, attempts up to MAX_DIVERSITY_ATTEMPTS candidates.
        Rejects any candidate sharing MAX_OVERLAP+1 or more numbers
        with any existing game. Tracks the best candidate (lowest
        max overlap) as a fallback.

        Args:
            zone_counts: Integer count per zone (sums to 6).
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
                    zone_counts, weighted_frequencies
                )

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
