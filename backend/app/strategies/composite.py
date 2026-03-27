"""Composite prediction strategy.

Generates lottery number predictions by blending four scoring signals:
1. Frequency scores (40%) -- weighted number frequencies from DecayEngine
2. Pattern scores (20%) -- pair co-occurrence + ending-digit affinity
3. Range scores (20%) -- zone density based on historical zone distribution
4. Balance scores (20%) -- odd/even x high/low category fitness

Per research decisions:
- D-07: Weights frequency=0.40, pattern=0.20, range=0.20, balance=0.20
- D-08: Score normalization with MIN_WEIGHT_FLOOR prevents zero-probability
- D-10: No two games share 4+ numbers (diversity constraint)
- D-11: Probabilistic selection from composite score distribution
"""

import random
from collections import defaultdict
from itertools import combinations

from app.config import settings
from app.schemas.lottery import LotteryDraw
from app.strategies.base import PredictionStrategy

# Zone definitions matching range strategy convention
ZONES: list[tuple[int, int]] = [
    (1, 9),    # Zone 1: 9 numbers
    (10, 19),  # Zone 2: 10 numbers
    (20, 29),  # Zone 3: 10 numbers
    (30, 39),  # Zone 4: 10 numbers
    (40, 45),  # Zone 5: 6 numbers
]


def normalize_scores(scores: dict[int, float]) -> dict[int, float]:
    """Normalize a score dict so values sum to 1.0.

    Applies MIN_WEIGHT_FLOOR to prevent zero-probability entries
    before normalizing.

    Args:
        scores: Dict mapping number -> raw score.

    Returns:
        Dict mapping number -> normalized score (sum ~1.0).
    """
    MIN_FLOOR = 0.001
    floored = {n: max(s, MIN_FLOOR) for n, s in scores.items()}
    total = sum(floored.values())
    if total == 0:
        # Uniform fallback
        count = len(floored)
        return {n: 1.0 / count for n in floored} if count > 0 else {}
    return {n: s / total for n, s in floored.items()}


class CompositeStrategy(PredictionStrategy):
    """Prediction strategy blending all four scoring signals.

    Combines frequency (40%), pattern (20%), range (20%), and
    balance (20%) scores into a single composite weight per number,
    then uses probabilistic selection with diversity constraint.
    """

    NUM_GAMES: int = 5
    NUMBERS_PER_GAME: int = 6
    MAX_OVERLAP: int = 3
    MAX_DIVERSITY_ATTEMPTS: int = 100
    MIN_WEIGHT_FLOOR: float = 0.001

    # Composite weights per D-07
    FREQ_WEIGHT: float = 0.40
    PATTERN_WEIGHT: float = 0.20
    RANGE_WEIGHT: float = 0.20
    BALANCE_WEIGHT: float = 0.20

    @property
    def name(self) -> str:
        return "composite"

    @property
    def display_name(self) -> str:
        return "종합 전략"

    def generate(
        self,
        draws: list[LotteryDraw],
        weighted_frequencies: dict[int, float],
    ) -> list[list[int]]:
        """Generate 5 diverse games by blending 4 scoring signals.

        Algorithm:
        1. Compute frequency scores (from weighted_frequencies)
        2. Compute pattern scores (pair affinity + ending-digit)
        3. Compute range scores (zone density)
        4. Compute balance scores (odd/even x high/low category fitness)
        5. Normalize each to sum=1.0
        6. Weighted average: 0.40*freq + 0.20*pattern + 0.20*range + 0.20*balance
        7. Probabilistic selection with diversity constraint

        Args:
            draws: Machine-filtered draws sorted by round_number ascending.
            weighted_frequencies: Dict mapping number (1-45) -> weighted frequency.

        Returns:
            List of 5 games, each with 6 unique sorted numbers in [1, 45].
        """
        numbers = list(range(1, 46))

        # Step 1: Frequency scores
        freq_scores = {n: weighted_frequencies.get(n, 0.0) for n in numbers}

        # Step 2: Pattern scores
        pattern_scores = self._compute_pattern_scores(draws, numbers)

        # Step 3: Range scores
        range_scores = self._compute_range_scores(draws, numbers)

        # Step 4: Balance scores
        balance_scores = self._compute_balance_scores(draws, numbers)

        # Step 5: Normalize each
        freq_norm = normalize_scores(freq_scores)
        pattern_norm = normalize_scores(pattern_scores)
        range_norm = normalize_scores(range_scores)
        balance_norm = normalize_scores(balance_scores)

        # Step 6: Weighted average
        composite_scores = {}
        for n in numbers:
            composite_scores[n] = (
                self.FREQ_WEIGHT * freq_norm[n]
                + self.PATTERN_WEIGHT * pattern_norm[n]
                + self.RANGE_WEIGHT * range_norm[n]
                + self.BALANCE_WEIGHT * balance_norm[n]
            )

        # Step 7: Probabilistic selection
        population = numbers
        weights = [composite_scores[n] for n in population]
        return self._generate_diverse_games(population, weights)

    # ------------------------------------------------------------------
    # Score computation methods
    # ------------------------------------------------------------------

    def _compute_pattern_scores(
        self,
        draws: list[LotteryDraw],
        numbers: list[int],
    ) -> dict[int, float]:
        """Compute per-number pattern affinity scores.

        Combines:
        - Pair score: Sum of decay-weighted pair frequencies involving number n
        - Ending-digit score: Decay-weighted frequency of n's ending digit

        Args:
            draws: Machine-filtered draws sorted ascending.
            numbers: List of numbers 1-45.

        Returns:
            Dict mapping number -> pattern score.
        """
        n_draws = len(draws)
        halflife = settings.DECAY_HALFLIFE

        # Compute pair frequencies
        pair_freq: dict[tuple[int, int], float] = defaultdict(float)
        digit_freq: dict[int, float] = defaultdict(float)

        for i, draw in enumerate(draws):
            weight = 0.5 ** ((n_draws - 1 - i) / halflife) if n_draws > 0 else 1.0
            for pair in combinations(draw.numbers, 2):
                pair_freq[pair] += weight
            for num in draw.numbers:
                digit_freq[num % 10] += weight

        # Per-number pattern score
        scores: dict[int, float] = {}
        for n in numbers:
            # Pair score: sum of pair frequencies involving n
            pair_score = 0.0
            for (a, b), freq in pair_freq.items():
                if a == n or b == n:
                    pair_score += freq

            # Ending-digit score
            ending_digit_score = digit_freq.get(n % 10, 0.0)

            scores[n] = pair_score + ending_digit_score

        return scores

    def _compute_range_scores(
        self,
        draws: list[LotteryDraw],
        numbers: list[int],
    ) -> dict[int, float]:
        """Compute per-number range scores based on zone density.

        For each number n, score = (zone's weighted count) / (zone size).
        This gives each number in the same zone an equal share of that
        zone's statistical weight.

        Args:
            draws: Machine-filtered draws sorted ascending.
            numbers: List of numbers 1-45.

        Returns:
            Dict mapping number -> range score.
        """
        n_draws = len(draws)
        halflife = settings.DECAY_HALFLIFE

        # Compute zone weighted totals
        zone_totals = [0.0] * len(ZONES)
        for i, draw in enumerate(draws):
            weight = 0.5 ** ((n_draws - 1 - i) / halflife) if n_draws > 0 else 1.0
            for num in draw.numbers:
                for z_idx, (z_start, z_end) in enumerate(ZONES):
                    if z_start <= num <= z_end:
                        zone_totals[z_idx] += weight
                        break

        # Compute zone sizes
        zone_sizes = [z_end - z_start + 1 for z_start, z_end in ZONES]

        # Per-number: zone_density = zone_total / zone_size
        scores: dict[int, float] = {}
        for n in numbers:
            for z_idx, (z_start, z_end) in enumerate(ZONES):
                if z_start <= n <= z_end:
                    scores[n] = zone_totals[z_idx] / zone_sizes[z_idx] if zone_sizes[z_idx] > 0 else 0.0
                    break

        return scores

    def _compute_balance_scores(
        self,
        draws: list[LotteryDraw],
        numbers: list[int],
    ) -> dict[int, float]:
        """Compute per-number balance-fitness scores.

        For each number n, determines its category (odd/even x high/low)
        and scores it by how often that category appears in the draws'
        ratio distributions, weighted by decay.

        Categories:
        - odd_low: odd numbers in [1, 22]
        - odd_high: odd numbers in [23, 45]
        - even_low: even numbers in [1, 22]
        - even_high: even numbers in [23, 45]

        Args:
            draws: Machine-filtered draws sorted ascending.
            numbers: List of numbers 1-45.

        Returns:
            Dict mapping number -> balance score.
        """
        n_draws = len(draws)
        halflife = settings.DECAY_HALFLIFE

        # Count decay-weighted category appearances across draws
        category_weights: dict[str, float] = defaultdict(float)
        for i, draw in enumerate(draws):
            weight = 0.5 ** ((n_draws - 1 - i) / halflife) if n_draws > 0 else 1.0
            for num in draw.numbers:
                cat = self._get_category(num)
                category_weights[cat] += weight

        # Per-number: score = weight of its category
        scores: dict[int, float] = {}
        for n in numbers:
            cat = self._get_category(n)
            scores[n] = category_weights.get(cat, 0.0)

        return scores

    @staticmethod
    def _get_category(n: int) -> str:
        """Classify a number into one of 4 categories.

        Args:
            n: Number in [1, 45].

        Returns:
            Category string: 'odd_low', 'odd_high', 'even_low', or 'even_high'.
        """
        is_odd = n % 2 == 1
        is_low = n <= 22
        if is_odd and is_low:
            return "odd_low"
        elif is_odd and not is_low:
            return "odd_high"
        elif not is_odd and is_low:
            return "even_low"
        else:
            return "even_high"

    # ------------------------------------------------------------------
    # Selection and diversity
    # ------------------------------------------------------------------

    def _select_unique(
        self, population: list[int], weights: list[float]
    ) -> list[int]:
        """Select 6 unique numbers using weighted random selection.

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

                max_overlap = 0
                for existing in games:
                    overlap = len(set(candidate) & set(existing))
                    max_overlap = max(max_overlap, overlap)

                if max_overlap < best_max_overlap:
                    best_max_overlap = max_overlap
                    best_candidate = candidate

                if max_overlap <= self.MAX_OVERLAP:
                    games.append(candidate)
                    break
            else:
                if best_candidate is not None:
                    games.append(best_candidate)

        return games
