"""Tests for RangeStrategy.

Tests cover:
- Game count and structure (5 games, 6 numbers each)
- Number validity (range 1-45, sorted, unique)
- Diversity constraint (no 4+ overlap between any pair)
- round_to_sum helper (largest-remainder rounding)
- Zone-biased distribution (concentrated draws bias output)
- Strategy properties (name, display_name)
- PredictionStrategy subclass conformance
"""

import pytest

from app.schemas.lottery import LotteryDraw
from app.strategies.base import PredictionStrategy
from app.strategies.range import RangeStrategy, round_to_sum


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def sample_draws() -> list[LotteryDraw]:
    """Build 20 LotteryDraw objects with varied numbers across 1-45."""
    draws = []
    for i in range(20):
        base = (i * 7) % 40
        nums = sorted(set(
            [(base + j) % 45 + 1 for j in range(8)]
        ))[:6]
        while len(nums) < 6:
            candidate = (base + len(nums) + 10) % 45 + 1
            if candidate not in nums:
                nums.append(candidate)
            else:
                candidate = (candidate + 1) % 45 + 1
                if candidate not in nums:
                    nums.append(candidate)
        nums = sorted(nums[:6])
        draws.append(
            LotteryDraw(
                round_number=800 + i,
                machine="1호기",
                numbers=nums,
                odd_even_ratio="3:3",
                high_low_ratio="3:3",
                ac_value=7,
                tail_sum=15,
                total_sum=130,
            )
        )
    return draws


@pytest.fixture
def uniform_weights() -> dict[int, float]:
    """Uniform weights: all numbers equally likely."""
    return {n: 1.0 for n in range(1, 46)}


@pytest.fixture
def zone4_draws() -> list[LotteryDraw]:
    """Draws heavily concentrated in zone 30-39."""
    draws = []
    for i in range(30):
        # All 6 numbers in 30-39 zone
        nums = sorted([30, 31, 32, 33, 34, 35])
        if i % 3 == 0:
            nums = sorted([30, 32, 34, 36, 37, 38])
        elif i % 3 == 1:
            nums = sorted([31, 33, 35, 36, 38, 39])
        draws.append(
            LotteryDraw(
                round_number=900 + i,
                machine="2호기",
                numbers=nums,
                odd_even_ratio="3:3",
                high_low_ratio="3:3",
                ac_value=7,
                tail_sum=15,
                total_sum=200,
            )
        )
    return draws


@pytest.fixture
def zone4_weights() -> dict[int, float]:
    """Weights skewed toward zone 30-39."""
    weights = {}
    for n in range(1, 46):
        if 30 <= n <= 39:
            weights[n] = 50.0
        else:
            weights[n] = 0.001
    return weights


# ---------------------------------------------------------------------------
# TestRangeStrategyProperties
# ---------------------------------------------------------------------------

class TestRangeStrategyProperties:
    """Tests for strategy name and display_name properties."""

    def test_name(self):
        """RangeStrategy().name == 'range'."""
        assert RangeStrategy().name == "range"

    def test_display_name(self):
        """RangeStrategy().display_name == '구간 전략'."""
        assert RangeStrategy().display_name == "구간 전략"

    def test_is_prediction_strategy_subclass(self):
        """RangeStrategy is a valid PredictionStrategy subclass."""
        strategy = RangeStrategy()
        assert isinstance(strategy, PredictionStrategy)


# ---------------------------------------------------------------------------
# TestRangeStrategyStructure
# ---------------------------------------------------------------------------

class TestRangeStrategyStructure:
    """Tests for game count and structure."""

    def test_generates_five_games(
        self, sample_draws: list[LotteryDraw], uniform_weights: dict[int, float]
    ):
        """generate() returns exactly 5 games."""
        games = RangeStrategy().generate(sample_draws, uniform_weights)
        assert len(games) == 5

    def test_each_game_has_six_numbers(
        self, sample_draws: list[LotteryDraw], uniform_weights: dict[int, float]
    ):
        """Every game has exactly 6 numbers."""
        games = RangeStrategy().generate(sample_draws, uniform_weights)
        for i, game in enumerate(games):
            assert len(game) == 6, f"Game {i} has {len(game)} numbers"

    def test_numbers_in_valid_range(
        self, sample_draws: list[LotteryDraw], uniform_weights: dict[int, float]
    ):
        """All numbers in every game are between 1 and 45 inclusive."""
        games = RangeStrategy().generate(sample_draws, uniform_weights)
        for i, game in enumerate(games):
            for num in game:
                assert 1 <= num <= 45, (
                    f"Game {i} has number {num} outside [1, 45]"
                )

    def test_numbers_sorted_ascending(
        self, sample_draws: list[LotteryDraw], uniform_weights: dict[int, float]
    ):
        """Each game's numbers are sorted ascending."""
        games = RangeStrategy().generate(sample_draws, uniform_weights)
        for i, game in enumerate(games):
            assert game == sorted(game), f"Game {i} not sorted: {game}"

    def test_numbers_unique_within_game(
        self, sample_draws: list[LotteryDraw], uniform_weights: dict[int, float]
    ):
        """No duplicate numbers within any single game."""
        games = RangeStrategy().generate(sample_draws, uniform_weights)
        for i, game in enumerate(games):
            assert len(set(game)) == 6, f"Game {i} has duplicates: {game}"


# ---------------------------------------------------------------------------
# TestRangeStrategyDiversity
# ---------------------------------------------------------------------------

class TestRangeStrategyDiversity:
    """Tests for diversity constraint between games."""

    def test_no_four_plus_overlap(
        self, sample_draws: list[LotteryDraw], uniform_weights: dict[int, float]
    ):
        """No pair of games shares 4+ numbers."""
        games = RangeStrategy().generate(sample_draws, uniform_weights)
        for i in range(len(games)):
            for j in range(i + 1, len(games)):
                overlap = len(set(games[i]) & set(games[j]))
                assert overlap < 4, (
                    f"Games {i} and {j} share {overlap} numbers "
                    f"(max 3): {games[i]} & {games[j]}"
                )


# ---------------------------------------------------------------------------
# TestRoundToSum
# ---------------------------------------------------------------------------

class TestRoundToSum:
    """Tests for the largest-remainder rounding helper."""

    def test_basic_rounding(self):
        """round_to_sum([1.01, 1.25, 1.31, 1.57, 0.86]) == [1, 1, 1, 2, 1]."""
        result = round_to_sum([1.01, 1.25, 1.31, 1.57, 0.86])
        assert result == [1, 1, 1, 2, 1]

    def test_always_sums_to_target(self):
        """Output always sums to target (default 6)."""
        test_cases = [
            [1.2, 1.2, 1.2, 1.2, 1.2],
            [0.0, 0.0, 0.0, 0.0, 6.0],
            [3.0, 3.0, 0.0, 0.0, 0.0],
            [1.5, 1.5, 1.5, 1.5, 0.0],
        ]
        for ratios in test_cases:
            result = round_to_sum(ratios, target=6)
            assert sum(result) == 6, f"sum({result}) != 6 for ratios={ratios}"

    def test_all_non_negative(self):
        """All values in result are non-negative."""
        result = round_to_sum([0.1, 0.1, 0.1, 0.1, 5.6])
        assert all(v >= 0 for v in result)

    def test_custom_target(self):
        """round_to_sum with custom target."""
        result = round_to_sum([2.5, 2.5], target=5)
        assert sum(result) == 5


# ---------------------------------------------------------------------------
# TestRangeDistribution
# ---------------------------------------------------------------------------

class TestRangeDistribution:
    """Tests for zone-biased distribution."""

    def test_zone4_concentration(
        self, zone4_draws: list[LotteryDraw], zone4_weights: dict[int, float]
    ):
        """With draws concentrated in zone 30-39, generated games should
        have more numbers in 30-39 than in 1-9."""
        strategy = RangeStrategy()
        zone1_count = 0  # numbers in 1-9
        zone4_count = 0  # numbers in 30-39

        for _ in range(10):
            games = strategy.generate(zone4_draws, zone4_weights)
            for game in games:
                for num in game:
                    if 1 <= num <= 9:
                        zone1_count += 1
                    elif 30 <= num <= 39:
                        zone4_count += 1

        assert zone4_count > zone1_count, (
            f"Zone 30-39 ({zone4_count}) should appear more than "
            f"zone 1-9 ({zone1_count}) with concentrated draws"
        )
