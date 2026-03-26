import pytest

from app.config import settings
from app.schemas.lottery import LotteryDraw
from app.services.decay_engine import DecayEngine


def make_draws(n: int) -> list[LotteryDraw]:
    """Generate n dummy LotteryDraw objects with sequential round numbers."""
    return [
        LotteryDraw(
            round_number=800 + i,
            machine="1호기",
            numbers=[1, 2, 3, 4, 5, 6],
            odd_even_ratio="3:3",
            high_low_ratio="3:3",
            ac_value=5,
            tail_sum=21,
            total_sum=21,
        )
        for i in range(n)
    ]


def test_newest_draw_highest_weight():
    """Newest draw (last) has weight 1.0, oldest (first) has weight < 1.0."""
    engine = DecayEngine(halflife=30)
    draws = make_draws(100)
    weights = engine.compute_weights(draws)

    assert len(weights) == 100
    assert weights[-1] == pytest.approx(1.0)
    assert weights[0] < 1.0


def test_weights_monotonically_increasing():
    """Weights increase monotonically from oldest to newest."""
    engine = DecayEngine(halflife=30)
    draws = make_draws(100)
    weights = engine.compute_weights(draws)

    for i in range(1, len(weights)):
        assert weights[i] >= weights[i - 1], (
            f"weights[{i}]={weights[i]} < weights[{i - 1}]={weights[i - 1]}"
        )


def test_halflife_gives_half_weight():
    """Weight at exactly one halflife distance is 0.5, two halflives is 0.25."""
    engine = DecayEngine(halflife=30)
    draws = make_draws(100)
    weights = engine.compute_weights(draws)

    # 30 positions back from newest (index -31)
    assert weights[-31] == pytest.approx(0.5, rel=1e-4)
    # 60 positions back from newest (index -61) = two halflives
    assert weights[-61] == pytest.approx(0.25, rel=1e-4)


def test_weighted_frequencies_all_numbers():
    """Output dict has keys exactly {1..45}, all values are float >= 0."""
    engine = DecayEngine(halflife=30)
    draws = make_draws(50)
    freq = engine.compute_weighted_frequencies(draws)

    assert set(freq.keys()) == set(range(1, 46))
    assert all(isinstance(v, float) for v in freq.values())
    assert all(v >= 0.0 for v in freq.values())
    # Number 1 appears in every draw's [1,2,3,4,5,6]
    assert freq[1] > 0.0
    # Number 45 never appears in dummy data
    assert freq[45] == 0.0


def test_weighted_frequency_total():
    """Total weighted frequency equals 6 * sum(weights)."""
    engine = DecayEngine(halflife=30)
    draws = make_draws(80)
    freq = engine.compute_weighted_frequencies(draws)
    weights = engine.compute_weights(draws)

    assert sum(freq.values()) == pytest.approx(6 * sum(weights), rel=1e-6)


def test_default_halflife_from_config():
    """DecayEngine() with no args uses settings.DECAY_HALFLIFE == 30."""
    engine = DecayEngine()

    assert engine.halflife == 30
    assert engine.halflife == settings.DECAY_HALFLIFE


def test_custom_halflife():
    """Faster halflife produces steeper decay than slower halflife."""
    engine_fast = DecayEngine(halflife=10)
    engine_slow = DecayEngine(halflife=50)
    draws = make_draws(100)

    weights_fast = engine_fast.compute_weights(draws)
    weights_slow = engine_slow.compute_weights(draws)

    # Fastest decay = smallest oldest weight
    assert weights_fast[0] < weights_slow[0]
    # Newest always 1.0 regardless of halflife
    assert weights_fast[-1] == pytest.approx(1.0)
    assert weights_slow[-1] == pytest.approx(1.0)


def test_integration_with_data_loader():
    """DecayEngine works end-to-end with real lottery data from DataLoader."""
    from app.services.data_loader import DataLoader

    loader = DataLoader(settings.DATA_PATH)
    loader.load_and_validate()
    draws = loader.get_draws_for_machine("1호기")

    engine = DecayEngine(halflife=30)
    freq = engine.compute_weighted_frequencies(draws)

    assert set(freq.keys()) == set(range(1, 46))
    assert all(isinstance(v, float) for v in freq.values())
    assert sum(freq.values()) > 0

    weights = engine.compute_weights(draws)
    assert sum(freq.values()) == pytest.approx(6 * sum(weights), rel=1e-6)
