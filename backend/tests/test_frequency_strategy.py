"""Tests for FrequencyStrategy and strategy registry.

Tests cover:
- Game count and structure (5 games, 6 numbers each)
- Number validity (range 1-45, sorted, unique)
- Diversity constraint (no 4+ overlap between any pair)
- Weighted selection bias (skewed frequencies bias output)
- Strategy properties (name, display_name)
- Registry (get_strategy valid/invalid)
"""

import pytest

from app.schemas.lottery import LotteryDraw
from app.strategies import get_strategy
from app.strategies.base import PredictionStrategy
from app.strategies.frequency import FrequencyStrategy


@pytest.fixture
def sample_draws() -> list[LotteryDraw]:
    """Build 20 LotteryDraw objects with varied numbers across 1-45."""
    draws = []
    for i in range(20):
        # Create varied but valid 6-number combinations
        base = (i * 7) % 40  # shift base to get variety
        nums = sorted(set(
            [(base + j) % 45 + 1 for j in range(8)]
        ))[:6]
        # Ensure exactly 6 unique numbers in range 1-45
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
def skewed_weights() -> dict[int, float]:
    """Heavily skewed: numbers 1-6 have weight 100.0, rest have 0.001."""
    return {n: 100.0 if n <= 6 else 0.001 for n in range(1, 46)}


class TestFrequencyStrategyGameStructure:
    """Tests for game count and structure."""

    def test_strategy_generates_five_games(
        self, sample_draws: list[LotteryDraw], uniform_weights: dict[int, float]
    ):
        """FrequencyStrategy().generate() returns exactly 5 games."""
        strategy = FrequencyStrategy()
        games = strategy.generate(sample_draws, uniform_weights)
        assert len(games) == 5

    def test_each_game_has_six_numbers(
        self, sample_draws: list[LotteryDraw], uniform_weights: dict[int, float]
    ):
        """Every game in result has exactly 6 numbers."""
        strategy = FrequencyStrategy()
        games = strategy.generate(sample_draws, uniform_weights)
        for i, game in enumerate(games):
            assert len(game) == 6, f"Game {i} has {len(game)} numbers, expected 6"

    def test_numbers_in_valid_range(
        self, sample_draws: list[LotteryDraw], uniform_weights: dict[int, float]
    ):
        """All numbers in every game are between 1 and 45 inclusive."""
        strategy = FrequencyStrategy()
        games = strategy.generate(sample_draws, uniform_weights)
        for i, game in enumerate(games):
            for num in game:
                assert 1 <= num <= 45, (
                    f"Game {i} has number {num} outside range [1, 45]"
                )

    def test_numbers_sorted_ascending(
        self, sample_draws: list[LotteryDraw], uniform_weights: dict[int, float]
    ):
        """Each game's numbers are sorted ascending."""
        strategy = FrequencyStrategy()
        games = strategy.generate(sample_draws, uniform_weights)
        for i, game in enumerate(games):
            assert game == sorted(game), (
                f"Game {i} not sorted: {game}"
            )

    def test_numbers_unique_within_game(
        self, sample_draws: list[LotteryDraw], uniform_weights: dict[int, float]
    ):
        """No duplicate numbers within any single game."""
        strategy = FrequencyStrategy()
        games = strategy.generate(sample_draws, uniform_weights)
        for i, game in enumerate(games):
            assert len(set(game)) == 6, (
                f"Game {i} has duplicates: {game}"
            )


class TestFrequencyStrategyDiversity:
    """Tests for diversity constraint between games."""

    def test_diversity_no_four_plus_overlap(
        self, sample_draws: list[LotteryDraw], uniform_weights: dict[int, float]
    ):
        """For any pair of games, set intersection size is less than 4."""
        strategy = FrequencyStrategy()
        games = strategy.generate(sample_draws, uniform_weights)
        for i in range(len(games)):
            for j in range(i + 1, len(games)):
                overlap = len(set(games[i]) & set(games[j]))
                assert overlap < 4, (
                    f"Games {i} and {j} share {overlap} numbers "
                    f"(max allowed: 3): {games[i]} & {games[j]}"
                )


class TestFrequencyStrategyBias:
    """Test that weighted selection actually biases output."""

    def test_weighted_selection_bias(
        self, sample_draws: list[LotteryDraw], skewed_weights: dict[int, float]
    ):
        """With skewed weights (1-6 = 100.0, rest = 0.001), numbers 1-6
        should appear significantly more than numbers 40-45."""
        strategy = FrequencyStrategy()
        low_count = 0   # appearances of numbers 1-6
        high_count = 0   # appearances of numbers 40-45

        for _ in range(10):
            games = strategy.generate(sample_draws, skewed_weights)
            for game in games:
                for num in game:
                    if 1 <= num <= 6:
                        low_count += 1
                    elif 40 <= num <= 45:
                        high_count += 1

        # With weight ratio 100000:1, low numbers should dominate
        assert low_count > high_count, (
            f"Expected numbers 1-6 ({low_count}) to appear more than "
            f"40-45 ({high_count}) with skewed weights"
        )


class TestStrategyProperties:
    """Tests for strategy name and display_name properties."""

    def test_strategy_name_property(self):
        """strategy.name == 'frequency'."""
        strategy = FrequencyStrategy()
        assert strategy.name == "frequency"

    def test_strategy_display_name(self):
        """strategy.display_name == '빈도 전략'."""
        strategy = FrequencyStrategy()
        assert strategy.display_name == "빈도 전략"


class TestStrategyRegistry:
    """Tests for strategy registry and get_strategy."""

    def test_get_strategy_valid(self):
        """get_strategy('frequency') returns a FrequencyStrategy instance."""
        strategy = get_strategy("frequency")
        assert isinstance(strategy, FrequencyStrategy)
        assert isinstance(strategy, PredictionStrategy)

    def test_get_strategy_invalid(self):
        """get_strategy('nonexistent') raises KeyError."""
        with pytest.raises(KeyError, match="nonexistent"):
            get_strategy("nonexistent")
