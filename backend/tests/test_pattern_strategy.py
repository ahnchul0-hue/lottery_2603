"""Tests for PatternStrategy.

Tests cover:
- Game count and structure (5 games, 6 numbers each)
- Number validity (range 1-45, sorted, unique)
- Diversity constraint (no 4+ overlap between any pair)
- Pattern-based bias (repeated pairs appear more often in output)
- Strategy properties (name, display_name)
- PredictionStrategy subclass check
"""

import pytest

from app.schemas.lottery import LotteryDraw
from app.strategies.base import PredictionStrategy
from app.strategies.pattern import PatternStrategy


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
def paired_draws() -> list[LotteryDraw]:
    """Draws where the pair (6, 38) appears in 18 of 20 draws.

    This fixture enables testing that decay-weighted pair frequency
    biases the generated games toward numbers 6 and 38.
    """
    draws = []
    for i in range(20):
        if i < 18:
            # Pair (6, 38) present in most draws
            nums = sorted([6, 38, (i % 10) + 10, (i % 8) + 20, (i % 5) + 30, (i % 4) + 40])
        else:
            # Last 2 draws without the pair
            nums = sorted([1, 2, 3, 4, 5, 7])
        # Ensure uniqueness and correct count
        unique = sorted(set(nums))
        while len(unique) < 6:
            candidate = len(unique) + 35
            while candidate in unique:
                candidate += 1
            if candidate > 45:
                candidate = 1
                while candidate in unique:
                    candidate += 1
            unique.append(candidate)
            unique = sorted(unique)
        unique = unique[:6]
        draws.append(
            LotteryDraw(
                round_number=800 + i,
                machine="1호기",
                numbers=unique,
                odd_even_ratio="3:3",
                high_low_ratio="3:3",
                ac_value=7,
                tail_sum=15,
                total_sum=130,
            )
        )
    return draws


@pytest.fixture
def paired_weights() -> dict[int, float]:
    """Weights where numbers 6 and 38 have high frequency."""
    weights = {n: 1.0 for n in range(1, 46)}
    weights[6] = 50.0
    weights[38] = 50.0
    return weights


class TestPatternStrategyStructure:
    """Tests for game count and structure."""

    def test_generates_five_games(
        self, sample_draws: list[LotteryDraw], uniform_weights: dict[int, float]
    ):
        """PatternStrategy().generate() returns exactly 5 games."""
        strategy = PatternStrategy()
        games = strategy.generate(sample_draws, uniform_weights)
        assert len(games) == 5

    def test_each_game_has_six_numbers(
        self, sample_draws: list[LotteryDraw], uniform_weights: dict[int, float]
    ):
        """Every game has exactly 6 numbers."""
        strategy = PatternStrategy()
        games = strategy.generate(sample_draws, uniform_weights)
        for i, game in enumerate(games):
            assert len(game) == 6, f"Game {i} has {len(game)} numbers, expected 6"

    def test_numbers_in_valid_range(
        self, sample_draws: list[LotteryDraw], uniform_weights: dict[int, float]
    ):
        """All numbers in every game are between 1 and 45 inclusive."""
        strategy = PatternStrategy()
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
        strategy = PatternStrategy()
        games = strategy.generate(sample_draws, uniform_weights)
        for i, game in enumerate(games):
            assert game == sorted(game), f"Game {i} not sorted: {game}"

    def test_numbers_unique_within_game(
        self, sample_draws: list[LotteryDraw], uniform_weights: dict[int, float]
    ):
        """No duplicate numbers within any single game."""
        strategy = PatternStrategy()
        games = strategy.generate(sample_draws, uniform_weights)
        for i, game in enumerate(games):
            assert len(set(game)) == 6, f"Game {i} has duplicates: {game}"


class TestPatternStrategyDiversity:
    """Tests for diversity constraint between games."""

    def test_no_four_plus_overlap(
        self, sample_draws: list[LotteryDraw], uniform_weights: dict[int, float]
    ):
        """No pair of games shares 4 or more numbers."""
        strategy = PatternStrategy()
        games = strategy.generate(sample_draws, uniform_weights)
        for i in range(len(games)):
            for j in range(i + 1, len(games)):
                overlap = len(set(games[i]) & set(games[j]))
                assert overlap < 4, (
                    f"Games {i} and {j} share {overlap} numbers "
                    f"(max allowed: 3): {games[i]} & {games[j]}"
                )


class TestPatternStrategyBias:
    """Test that pair-frequency pattern biases output."""

    def test_repeated_pair_bias(
        self,
        paired_draws: list[LotteryDraw],
        paired_weights: dict[int, float],
    ):
        """With draws containing repeated pair (6, 38), those numbers should
        appear more often than numbers that never appear in pairs."""
        strategy = PatternStrategy()
        target_count = 0  # appearances of 6 or 38
        other_count = 0  # appearances of numbers 41-45

        for _ in range(20):
            games = strategy.generate(paired_draws, paired_weights)
            for game in games:
                for num in game:
                    if num in (6, 38):
                        target_count += 1
                    elif 41 <= num <= 45:
                        other_count += 1

        # Numbers 6 and 38 should appear substantially more often
        assert target_count > other_count, (
            f"Expected pair numbers 6,38 ({target_count}) to appear "
            f"more than 41-45 ({other_count}) with paired draws"
        )


class TestPatternStrategyProperties:
    """Tests for strategy name, display_name, and ABC compliance."""

    def test_name_property(self):
        """strategy.name == 'pattern'."""
        strategy = PatternStrategy()
        assert strategy.name == "pattern"

    def test_display_name_property(self):
        """strategy.display_name == '패턴 전략'."""
        strategy = PatternStrategy()
        assert strategy.display_name == "패턴 전략"

    def test_is_prediction_strategy_subclass(self):
        """PatternStrategy is a valid PredictionStrategy subclass."""
        strategy = PatternStrategy()
        assert isinstance(strategy, PredictionStrategy)
