"""Pattern-based prediction strategy.

Generates lottery number predictions using three pattern signals:
1. Decay-weighted pair frequency (most frequent co-occurring pairs seed games)
2. Consecutive number tendency (inject adjacent numbers based on historical rate)
3. Ending-digit distribution (complete games by sampling ending digits)

Per research decisions:
- D-01: Exponential decay weights for pair frequency
- D-02: Consecutive injection based on dynamic percentage
- D-03: Ending-digit completion uses per-machine digit distribution
- D-07: No two games share 4+ numbers (diversity constraint)
- D-08: Fallback to best candidate after MAX_DIVERSITY_ATTEMPTS
"""

import random
from collections import defaultdict
from itertools import combinations

from app.config import settings
from app.schemas.lottery import LotteryDraw
from app.strategies.base import PredictionStrategy


class PatternStrategy(PredictionStrategy):
    """Prediction strategy based on pattern analysis.

    Combines three signals: decay-weighted pair frequency, consecutive
    number tendency, and ending-digit distribution to generate diverse
    games that reflect observed patterns in historical draw data.
    """

    NUM_GAMES: int = 5
    NUMBERS_PER_GAME: int = 6
    MAX_OVERLAP: int = 3
    MAX_DIVERSITY_ATTEMPTS: int = 100
    MIN_WEIGHT_FLOOR: float = 0.001

    @property
    def name(self) -> str:
        return "pattern"

    @property
    def display_name(self) -> str:
        return "패턴 전략"

    def generate(
        self,
        draws: list[LotteryDraw],
        weighted_frequencies: dict[int, float],
    ) -> list[list[int]]:
        """Generate 5 diverse game sets using pattern analysis.

        Args:
            draws: Machine-filtered LotteryDraw list sorted by round_number ascending.
            weighted_frequencies: Dict mapping number (1-45) -> weighted frequency.

        Returns:
            List of 5 games, each with 6 unique sorted numbers in [1, 45].
        """
        if len(draws) < 2:
            # Not enough data for pattern analysis; fall back to weighted selection
            population = list(range(1, 46))
            weights = [
                max(weighted_frequencies.get(n, 0.0), self.MIN_WEIGHT_FLOOR)
                for n in population
            ]
            return self._generate_diverse_games_simple(population, weights)

        # Pre-compute pattern signals from draws
        pair_freq = self._compute_pair_frequencies(draws)
        consec_rate = self._compute_consecutive_rate(draws)
        digit_freq = self._compute_ending_digit_freq(draws)

        return self._generate_diverse_games(
            pair_freq, consec_rate, digit_freq, weighted_frequencies
        )

    # ------------------------------------------------------------------
    # Pattern signal computation
    # ------------------------------------------------------------------

    def _compute_pair_frequencies(
        self, draws: list[LotteryDraw]
    ) -> dict[tuple[int, int], float]:
        """Compute decay-weighted pair co-occurrence frequencies.

        For each draw, all C(6,2)=15 pairs get the draw's decay weight.
        Pairs that appear together more often in recent draws get higher scores.

        Args:
            draws: Sorted ascending by round_number.

        Returns:
            Dict mapping (a, b) -> weighted frequency where a < b.
        """
        n = len(draws)
        halflife = settings.DECAY_HALFLIFE
        pair_freq: dict[tuple[int, int], float] = defaultdict(float)

        for i, draw in enumerate(draws):
            weight = 0.5 ** ((n - 1 - i) / halflife)
            for pair in combinations(draw.numbers, 2):
                pair_freq[pair] += weight

        return dict(pair_freq)

    def _compute_consecutive_rate(self, draws: list[LotteryDraw]) -> float:
        """Compute the fraction of draws containing at least one consecutive pair.

        A consecutive pair is two numbers where |a - b| == 1.

        Args:
            draws: List of LotteryDraw objects.

        Returns:
            Float in [0, 1] representing the rate of consecutive occurrence.
        """
        if not draws:
            return 0.0

        count = 0
        for draw in draws:
            nums = draw.numbers
            for j in range(len(nums) - 1):
                if nums[j + 1] - nums[j] == 1:
                    count += 1
                    break  # Only count once per draw

        return count / len(draws)

    def _compute_ending_digit_freq(
        self, draws: list[LotteryDraw]
    ) -> dict[int, float]:
        """Compute decay-weighted ending-digit (number % 10) frequency.

        Args:
            draws: Sorted ascending by round_number.

        Returns:
            Dict mapping digit (0-9) -> weighted frequency.
        """
        n = len(draws)
        halflife = settings.DECAY_HALFLIFE
        digit_freq: dict[int, float] = defaultdict(float)

        for i, draw in enumerate(draws):
            weight = 0.5 ** ((n - 1 - i) / halflife)
            for num in draw.numbers:
                digit_freq[num % 10] += weight

        return dict(digit_freq)

    # ------------------------------------------------------------------
    # Game generation
    # ------------------------------------------------------------------

    def _generate_single_game(
        self,
        pair_freq: dict[tuple[int, int], float],
        consec_rate: float,
        digit_freq: dict[int, float],
        weighted_frequencies: dict[int, float],
    ) -> list[int]:
        """Generate one game using the three-signal pattern algorithm.

        Step 1: Pair seeding -- select 1-2 top pairs probabilistically.
        Step 2: Consecutive injection -- possibly add neighbor of a seeded number.
        Step 3: Ending-digit completion -- fill remaining slots via digit distribution.
        Step 4: Validation -- ensure 6 unique numbers in [1, 45], sorted.

        Args:
            pair_freq: Decay-weighted pair frequencies.
            consec_rate: Rate of draws with consecutive pairs.
            digit_freq: Decay-weighted ending-digit frequencies.
            weighted_frequencies: Per-number weighted frequencies for fallback.

        Returns:
            Sorted list of 6 unique numbers in [1, 45].
        """
        selected: set[int] = set()

        # Step 1: Pair seeding
        self._seed_from_pairs(selected, pair_freq)

        # Step 2: Consecutive injection
        self._inject_consecutive(selected, consec_rate)

        # Step 3: Ending-digit completion
        self._complete_by_ending_digit(selected, digit_freq, weighted_frequencies)

        # Step 4: Validation / fallback fill
        self._fill_remaining(selected, weighted_frequencies)

        result = sorted(selected)[:self.NUMBERS_PER_GAME]
        return result

    def _seed_from_pairs(
        self,
        selected: set[int],
        pair_freq: dict[tuple[int, int], float],
    ) -> None:
        """Select 1-2 top pairs weighted by frequency and add their numbers.

        Adds 2-4 numbers to the selected set.
        """
        if not pair_freq:
            return

        pairs = list(pair_freq.keys())
        weights = [pair_freq[p] for p in pairs]

        # Select 1-2 pairs probabilistically
        num_pairs = random.choice([1, 2])
        for _ in range(num_pairs):
            chosen = random.choices(pairs, weights=weights, k=1)[0]
            selected.add(chosen[0])
            selected.add(chosen[1])

    def _inject_consecutive(
        self,
        selected: set[int],
        consec_rate: float,
    ) -> None:
        """Possibly add a consecutive neighbor to one seeded number.

        Injection probability depends on the consecutive rate observed in draws:
        - If consec_rate > 0.5: 50% probability
        - Otherwise: 30% probability
        """
        if not selected:
            return

        injection_prob = 0.5 if consec_rate > 0.5 else 0.3
        if random.random() >= injection_prob:
            return

        # Pick a random seeded number and try +1 or -1
        base = random.choice(list(selected))
        candidates = []
        if base + 1 <= 45 and base + 1 not in selected:
            candidates.append(base + 1)
        if base - 1 >= 1 and base - 1 not in selected:
            candidates.append(base - 1)

        if candidates:
            selected.add(random.choice(candidates))

    def _complete_by_ending_digit(
        self,
        selected: set[int],
        digit_freq: dict[int, float],
        weighted_frequencies: dict[int, float],
    ) -> None:
        """Fill remaining slots using ending-digit distribution.

        For each remaining slot:
        1. Pick an ending digit weighted by digit_freq.
        2. Among numbers with that ending digit, pick one weighted by weighted_frequencies.
        3. Skip duplicates.
        """
        if len(selected) >= self.NUMBERS_PER_GAME:
            return

        # Build digit -> numbers mapping
        digit_to_numbers: dict[int, list[int]] = defaultdict(list)
        for n in range(1, 46):
            digit_to_numbers[n % 10].append(n)

        # Prepare digit weights
        digits = list(range(10))
        digit_weights = [max(digit_freq.get(d, 0.0), self.MIN_WEIGHT_FLOOR) for d in digits]

        attempts = 0
        max_attempts = 100
        while len(selected) < self.NUMBERS_PER_GAME and attempts < max_attempts:
            attempts += 1
            # Pick a digit
            chosen_digit = random.choices(digits, weights=digit_weights, k=1)[0]

            # Get available numbers with that ending digit
            candidates = [n for n in digit_to_numbers[chosen_digit] if n not in selected]
            if not candidates:
                continue

            # Pick a number weighted by weighted_frequencies
            cand_weights = [
                max(weighted_frequencies.get(c, 0.0), self.MIN_WEIGHT_FLOOR)
                for c in candidates
            ]
            pick = random.choices(candidates, weights=cand_weights, k=1)[0]
            selected.add(pick)

    def _fill_remaining(
        self,
        selected: set[int],
        weighted_frequencies: dict[int, float],
    ) -> None:
        """Fill any remaining slots using weighted frequency selection.

        Fallback mechanism to ensure exactly NUMBERS_PER_GAME numbers.
        """
        population = list(range(1, 46))
        while len(selected) < self.NUMBERS_PER_GAME:
            available = [n for n in population if n not in selected]
            if not available:
                break
            weights = [
                max(weighted_frequencies.get(n, 0.0), self.MIN_WEIGHT_FLOOR)
                for n in available
            ]
            pick = random.choices(available, weights=weights, k=1)[0]
            selected.add(pick)

    def _generate_diverse_games(
        self,
        pair_freq: dict[tuple[int, int], float],
        consec_rate: float,
        digit_freq: dict[int, float],
        weighted_frequencies: dict[int, float],
    ) -> list[list[int]]:
        """Generate NUM_GAMES games with diversity constraint.

        Uses MAX_DIVERSITY_ATTEMPTS per game, tracking the best candidate
        (lowest max overlap) as a fallback.

        Args:
            pair_freq: Decay-weighted pair frequencies.
            consec_rate: Consecutive pair rate.
            digit_freq: Ending-digit frequencies.
            weighted_frequencies: Per-number weighted frequencies.

        Returns:
            List of NUM_GAMES games.
        """
        games: list[list[int]] = []

        for _ in range(self.NUM_GAMES):
            best_candidate: list[int] | None = None
            best_max_overlap: int = self.NUMBERS_PER_GAME + 1

            for _attempt in range(self.MAX_DIVERSITY_ATTEMPTS):
                candidate = self._generate_single_game(
                    pair_freq, consec_rate, digit_freq, weighted_frequencies
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
                # After all attempts, use the best candidate found
                if best_candidate is not None:
                    games.append(best_candidate)

        return games

    def _generate_diverse_games_simple(
        self, population: list[int], weights: list[float]
    ) -> list[list[int]]:
        """Fallback for insufficient draw data -- simple weighted selection.

        Mirrors FrequencyStrategy's approach when pattern data is unavailable.
        """
        games: list[list[int]] = []

        for _ in range(self.NUM_GAMES):
            best_candidate: list[int] | None = None
            best_max_overlap: int = self.NUMBERS_PER_GAME + 1

            for _attempt in range(self.MAX_DIVERSITY_ATTEMPTS):
                selected: set[int] = set()
                while len(selected) < self.NUMBERS_PER_GAME:
                    pick = random.choices(population, weights=weights, k=1)[0]
                    selected.add(pick)
                candidate = sorted(selected)

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
