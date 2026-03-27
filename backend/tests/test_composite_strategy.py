"""Tests for CompositeStrategy.

Tests cover:
- Game count and structure (5 games, 6 numbers each)
- Number validity (range 1-45, sorted, unique)
- Diversity constraint (no 4+ overlap between any pair)
- Normalize scores helper (sum ~1.0, floor applied)
- Blending effect (output differs from pure frequency-only)
- Strategy properties (name, display_name)
- ABC compliance (PredictionStrategy subclass)
"""

import pytest

from app.schemas.lottery import LotteryDraw
from app.strategies.base import PredictionStrategy
from app.strategies.composite import CompositeStrategy, normalize_scores


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
def skewed_weights() -> dict[int, float]:
    """Heavily skewed: numbers 1-6 have weight 100.0, rest have 0.001."""
    return {n: 100.0 if n <= 6 else 0.001 for n in range(1, 46)}


class TestCompositeStrategyProperties:
    """Tests for strategy name and display_name properties."""

    def test_strategy_name_property(self):
        """strategy.name == 'composite'."""
        strategy = CompositeStrategy()
        assert strategy.name == "composite"

    def test_strategy_display_name(self):
        """strategy.display_name == '종합 전략'."""
        strategy = CompositeStrategy()
        assert strategy.display_name == "종합 전략"

    def test_is_prediction_strategy_subclass(self):
        """CompositeStrategy is a valid PredictionStrategy subclass."""
        strategy = CompositeStrategy()
        assert isinstance(strategy, PredictionStrategy)


class TestCompositeStrategyStructure:
    """Tests for game count and structure."""

    def test_generates_five_games(
        self, sample_draws: list[LotteryDraw], uniform_weights: dict[int, float]
    ):
        """generate() returns exactly 5 games."""
        strategy = CompositeStrategy()
        games = strategy.generate(sample_draws, uniform_weights)
        assert len(games) == 5

    def test_each_game_has_six_numbers(
        self, sample_draws: list[LotteryDraw], uniform_weights: dict[int, float]
    ):
        """Every game has exactly 6 numbers."""
        strategy = CompositeStrategy()
        games = strategy.generate(sample_draws, uniform_weights)
        for i, game in enumerate(games):
            assert len(game) == 6, f"Game {i} has {len(game)} numbers, expected 6"

    def test_numbers_in_valid_range(
        self, sample_draws: list[LotteryDraw], uniform_weights: dict[int, float]
    ):
        """All numbers in every game are between 1 and 45 inclusive."""
        strategy = CompositeStrategy()
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
        strategy = CompositeStrategy()
        games = strategy.generate(sample_draws, uniform_weights)
        for i, game in enumerate(games):
            assert game == sorted(game), f"Game {i} not sorted: {game}"

    def test_numbers_unique_within_game(
        self, sample_draws: list[LotteryDraw], uniform_weights: dict[int, float]
    ):
        """No duplicate numbers within any single game."""
        strategy = CompositeStrategy()
        games = strategy.generate(sample_draws, uniform_weights)
        for i, game in enumerate(games):
            assert len(set(game)) == 6, f"Game {i} has duplicates: {game}"


class TestCompositeStrategyDiversity:
    """Tests for diversity constraint between games."""

    def test_no_four_plus_overlap(
        self, sample_draws: list[LotteryDraw], uniform_weights: dict[int, float]
    ):
        """For any pair of games, set intersection size is at most 3."""
        strategy = CompositeStrategy()
        games = strategy.generate(sample_draws, uniform_weights)
        for i in range(len(games)):
            for j in range(i + 1, len(games)):
                overlap = len(set(games[i]) & set(games[j]))
                assert overlap <= 3, (
                    f"Games {i} and {j} share {overlap} numbers "
                    f"(max allowed: 3): {games[i]} & {games[j]}"
                )


class TestNormalizeScores:
    """Tests for the normalize_scores helper function."""

    def test_normalized_sum_is_one(self):
        """Normalized scores sum to approximately 1.0."""
        scores = {1: 5.0, 2: 3.0, 3: 2.0}
        result = normalize_scores(scores)
        assert abs(sum(result.values()) - 1.0) < 1e-9

    def test_floor_applied_to_zeros(self):
        """Zero-valued scores get floored to MIN_WEIGHT_FLOOR."""
        scores = {1: 10.0, 2: 0.0, 3: 5.0}
        result = normalize_scores(scores)
        assert result[2] > 0.0  # floor prevents zero

    def test_all_45_numbers(self):
        """Works correctly for all 45 numbers."""
        scores = {n: float(n) for n in range(1, 46)}
        result = normalize_scores(scores)
        assert len(result) == 45
        assert abs(sum(result.values()) - 1.0) < 1e-9

    def test_preserves_relative_ordering(self):
        """Higher input scores produce higher normalized values."""
        scores = {1: 10.0, 2: 1.0, 3: 5.0}
        result = normalize_scores(scores)
        assert result[1] > result[3] > result[2]


class TestCompositeBlending:
    """Test that composite strategy is not identical to pure frequency."""

    def test_output_differs_from_pure_frequency_under_skew(
        self, sample_draws: list[LotteryDraw], skewed_weights: dict[int, float]
    ):
        """With extreme frequency skew (1-6 weighted 100x), composite output
        still shows some diversity (not all games identical to frequency-only).

        We run multiple iterations and check that at least one game includes
        a number outside 1-6, demonstrating that pattern/range/balance signals
        contribute to the output.
        """
        strategy = CompositeStrategy()
        found_non_low = False
        for _ in range(20):
            games = strategy.generate(sample_draws, skewed_weights)
            for game in games:
                for num in game:
                    if num > 6:
                        found_non_low = True
                        break
                if found_non_low:
                    break
            if found_non_low:
                break
        assert found_non_low, (
            "Expected at least one number > 6 across 20 runs with composite strategy, "
            "but all numbers were 1-6. Blending effect not observed."
        )
