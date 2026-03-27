"""Tests for BalanceStrategy.

Tests cover:
- Game count and structure (5 games, 6 numbers each)
- Number validity (range 1-45, sorted, unique)
- Diversity constraint (no 4+ overlap between any pair)
- compute_category_counts helper (simultaneous odd/even + high/low)
- Balance-biased output (skewed draws bias output)
- Strategy properties (name, display_name)
- PredictionStrategy subclass conformance
"""

import pytest

from app.schemas.lottery import LotteryDraw
from app.strategies.balance import BalanceStrategy, compute_category_counts
from app.strategies.base import PredictionStrategy


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
def odd_biased_draws() -> list[LotteryDraw]:
    """Draws consistently showing 4:2 odd:even ratio."""
    draws = []
    for i in range(30):
        # 4 odd, 2 even numbers
        if i % 3 == 0:
            nums = sorted([1, 3, 5, 7, 2, 4])
        elif i % 3 == 1:
            nums = sorted([9, 11, 13, 15, 6, 8])
        else:
            nums = sorted([17, 19, 21, 23, 10, 12])
        draws.append(
            LotteryDraw(
                round_number=900 + i,
                machine="2호기",
                numbers=nums,
                odd_even_ratio="4:2",
                high_low_ratio="3:3",
                ac_value=7,
                tail_sum=15,
                total_sum=130,
            )
        )
    return draws


@pytest.fixture
def odd_biased_weights() -> dict[int, float]:
    """Weights slightly favoring odd numbers."""
    weights = {}
    for n in range(1, 46):
        if n % 2 == 1:
            weights[n] = 5.0
        else:
            weights[n] = 1.0
    return weights


# ---------------------------------------------------------------------------
# TestBalanceStrategyProperties
# ---------------------------------------------------------------------------

class TestBalanceStrategyProperties:
    """Tests for strategy name and display_name properties."""

    def test_name(self):
        """BalanceStrategy().name == 'balance'."""
        assert BalanceStrategy().name == "balance"

    def test_display_name(self):
        """BalanceStrategy().display_name == '밸런스 전략'."""
        assert BalanceStrategy().display_name == "밸런스 전략"

    def test_is_prediction_strategy_subclass(self):
        """BalanceStrategy is a valid PredictionStrategy subclass."""
        strategy = BalanceStrategy()
        assert isinstance(strategy, PredictionStrategy)


# ---------------------------------------------------------------------------
# TestBalanceStrategyStructure
# ---------------------------------------------------------------------------

class TestBalanceStrategyStructure:
    """Tests for game count and structure."""

    def test_generates_five_games(
        self, sample_draws: list[LotteryDraw], uniform_weights: dict[int, float]
    ):
        """generate() returns exactly 5 games."""
        games = BalanceStrategy().generate(sample_draws, uniform_weights)
        assert len(games) == 5

    def test_each_game_has_six_numbers(
        self, sample_draws: list[LotteryDraw], uniform_weights: dict[int, float]
    ):
        """Every game has exactly 6 numbers."""
        games = BalanceStrategy().generate(sample_draws, uniform_weights)
        for i, game in enumerate(games):
            assert len(game) == 6, f"Game {i} has {len(game)} numbers"

    def test_numbers_in_valid_range(
        self, sample_draws: list[LotteryDraw], uniform_weights: dict[int, float]
    ):
        """All numbers in every game are between 1 and 45 inclusive."""
        games = BalanceStrategy().generate(sample_draws, uniform_weights)
        for i, game in enumerate(games):
            for num in game:
                assert 1 <= num <= 45, (
                    f"Game {i} has number {num} outside [1, 45]"
                )

    def test_numbers_sorted_ascending(
        self, sample_draws: list[LotteryDraw], uniform_weights: dict[int, float]
    ):
        """Each game's numbers are sorted ascending."""
        games = BalanceStrategy().generate(sample_draws, uniform_weights)
        for i, game in enumerate(games):
            assert game == sorted(game), f"Game {i} not sorted: {game}"

    def test_numbers_unique_within_game(
        self, sample_draws: list[LotteryDraw], uniform_weights: dict[int, float]
    ):
        """No duplicate numbers within any single game."""
        games = BalanceStrategy().generate(sample_draws, uniform_weights)
        for i, game in enumerate(games):
            assert len(set(game)) == 6, f"Game {i} has duplicates: {game}"


# ---------------------------------------------------------------------------
# TestBalanceStrategyDiversity
# ---------------------------------------------------------------------------

class TestBalanceStrategyDiversity:
    """Tests for diversity constraint between games."""

    def test_no_four_plus_overlap(
        self, sample_draws: list[LotteryDraw], uniform_weights: dict[int, float]
    ):
        """No pair of games shares 4+ numbers."""
        games = BalanceStrategy().generate(sample_draws, uniform_weights)
        for i in range(len(games)):
            for j in range(i + 1, len(games)):
                overlap = len(set(games[i]) & set(games[j]))
                assert overlap < 4, (
                    f"Games {i} and {j} share {overlap} numbers "
                    f"(max 3): {games[i]} & {games[j]}"
                )


# ---------------------------------------------------------------------------
# TestBalanceConstraints (compute_category_counts)
# ---------------------------------------------------------------------------

class TestBalanceConstraints:
    """Tests for category count computation."""

    def test_balanced_3_3_3_3(self):
        """compute_category_counts(3, 3, 3, 3) returns all non-negative summing to 6."""
        result = compute_category_counts(3, 3, 3, 3)
        assert all(v >= 0 for v in result.values()), f"Negative value in {result}"
        total = sum(result.values())
        assert total == 6, f"Sum {total} != 6 for {result}"

    def test_extreme_5_1_1_5(self):
        """compute_category_counts(5, 1, 1, 5) returns valid non-negative counts summing to 6."""
        result = compute_category_counts(5, 1, 1, 5)
        assert all(v >= 0 for v in result.values()), f"Negative value in {result}"
        total = sum(result.values())
        assert total == 6, f"Sum {total} != 6 for {result}"

    def test_all_odd_high(self):
        """compute_category_counts(6, 0, 6, 0) returns valid counts."""
        result = compute_category_counts(6, 0, 6, 0)
        assert all(v >= 0 for v in result.values())
        assert sum(result.values()) == 6

    def test_all_even_low(self):
        """compute_category_counts(0, 6, 0, 6) returns valid counts."""
        result = compute_category_counts(0, 6, 0, 6)
        assert all(v >= 0 for v in result.values())
        assert sum(result.values()) == 6

    def test_returns_correct_keys(self):
        """Result has keys: odd_low, odd_high, even_low, even_high."""
        result = compute_category_counts(3, 3, 3, 3)
        assert set(result.keys()) == {"odd_low", "odd_high", "even_low", "even_high"}


# ---------------------------------------------------------------------------
# TestBalanceBias
# ---------------------------------------------------------------------------

class TestBalanceBias:
    """Tests for balance-biased output."""

    def test_odd_bias(
        self,
        odd_biased_draws: list[LotteryDraw],
        odd_biased_weights: dict[int, float],
    ):
        """With draws consistently 4:2 odd:even, generated games should
        lean toward more odd numbers than even numbers."""
        strategy = BalanceStrategy()
        odd_count = 0
        even_count = 0

        for _ in range(10):
            games = strategy.generate(odd_biased_draws, odd_biased_weights)
            for game in games:
                for num in game:
                    if num % 2 == 1:
                        odd_count += 1
                    else:
                        even_count += 1

        assert odd_count > even_count, (
            f"Expected odd ({odd_count}) > even ({even_count}) "
            f"with 4:2 odd:even biased draws"
        )
