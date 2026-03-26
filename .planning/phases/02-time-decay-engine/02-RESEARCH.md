# Phase 2: Time Decay Engine - Research

**Researched:** 2026-03-26
**Domain:** Exponential decay weighting for lottery number frequency analysis
**Confidence:** HIGH

## Summary

Phase 2 implements an independent decay engine module (`backend/app/services/decay_engine.py`) that accepts a list of `LotteryDraw` objects from DataLoader and returns a dictionary mapping each number (1-45) to its time-decay-weighted frequency. The formula is locked: `weight = 0.5^(draws_since / halflife)` with halflife defaulting to 30.

The implementation is straightforward pure Python math. No additional dependencies (numpy, pandas) are required -- the `**` operator handles the exponential computation. The project currently has Python 3.13 with FastAPI and Pydantic only; numpy/pandas are NOT installed. Adding them solely for this formula would be unnecessary overhead.

**Primary recommendation:** Implement as a class with a `compute_weighted_frequencies(draws: list[LotteryDraw]) -> dict[int, float]` method. Use pure Python math. Add `DECAY_HALFLIFE: int = 30` to `config.py`. Write comprehensive unit tests covering the decay curve shape, edge cases, and integration with DataLoader.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- **D-01:** Exponential decay function: `weight = 0.5 ^ (draws_since / halflife)`
- **D-02:** halflife default = **30** (aggressive -- ~7 months of data has 50% weight)
- **D-03:** halflife is parameterized via `config.py` as `DECAY_HALFLIFE`
- **D-04:** Decay weights apply to **number frequency (1-45) only**, not other stats
- **D-05:** Other statistics (odd/even, high/low, range, total, AC value) keep simple ratios -- no decay
- **D-06:** Independent module at `backend/app/services/decay_engine.py`
- **D-07:** DataLoader -> DecayEngine pipeline (DataLoader provides input, DecayEngine computes weights)
- **D-08:** Input: machine-filtered `LotteryDraw` list; Output: `dict[int, float]` mapping number -> weighted frequency

### Claude's Discretion
- DecayEngine: class vs function-based design
- Test strategy (unit test scope)
- numpy usage (pure Python is also viable)

### Deferred Ideas (OUT OF SCOPE)
- None -- discussion stayed within phase scope
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| DECAY-01 | Apply exponential decay weights: most recent draw = highest weight, older draws = lower weight | Locked formula `0.5^(draws_since/halflife)` verified mathematically. With halflife=30 and 134 draws (1hoogi), oldest draw gets 4.6% weight relative to newest. Effective sample size ~79 draws. |
| DECAY-02 | Halflife defaults to 30, adjustable at code level without modifying core logic | Parameterize via `Settings.DECAY_HALFLIFE` in config.py. DecayEngine reads from settings. Note: REQUIREMENTS.md says default=50 but CONTEXT.md decision D-02 locks it to 30 -- CONTEXT.md takes precedence. |
</phase_requirements>

## Standard Stack

### Core (No New Dependencies Needed)

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Python stdlib (math) | 3.13 | `0.5 ** (draws_since / halflife)` computation | Pure Python `**` operator handles this trivially. No numpy/pandas needed for scalar exponentiation over ~140 items. |
| Pydantic | >=2.12.5 | Already installed; type validation for input/output | DecayEngine input uses existing `LotteryDraw` schema. |
| pytest | >=9.0.2 | Already installed as dev dependency | Unit tests for decay curve verification. |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Pure Python `**` | numpy vectorized ops | numpy is NOT installed. Adding a 25MB dependency for `0.5 ** x` on 134 items is unjustified. If Phase 3+ needs numpy for strategy math, DecayEngine can remain pure Python -- it returns a simple dict. |
| Pure Python `**` | pandas `ewm()` | pandas ewm() uses a different decay formula (exponentially weighted moving average, not the user's specified `0.5^(t/h)`). The user locked a specific formula -- pandas ewm would give different results. |

**Key insight:** The user's formula `weight = 0.5^(draws_since / halflife)` is NOT the same as pandas ewm. Pandas ewm computes a moving average with decay; the user wants per-draw weights applied to number frequency counting. Pure Python matches the locked decision exactly.

## Architecture Patterns

### Recommended Module Location
```
backend/app/
├── config.py              # Add DECAY_HALFLIFE = 30
├── services/
│   ├── data_loader.py     # Existing -- provides LotteryDraw lists
│   └── decay_engine.py    # NEW -- compute weighted number frequencies
└── tests/
    ├── test_data_loader.py   # Existing
    └── test_decay_engine.py  # NEW -- decay curve and frequency tests
```

### Pattern: Class-Based DecayEngine (Recommended)

**What:** A `DecayEngine` class that takes halflife as constructor parameter and exposes a `compute_weighted_frequencies` method.

**Why class over functions:** Consistent with existing `DataLoader` class pattern. Constructor captures configuration (halflife), methods operate on data. Enables clean dependency injection and testability (inject custom halflife in tests without touching config).

**Interface design:**

```python
# backend/app/services/decay_engine.py
from app.schemas.lottery import LotteryDraw


class DecayEngine:
    """Compute time-decay-weighted number frequencies from lottery draws."""

    def __init__(self, halflife: int = 30):
        self.halflife = halflife

    def compute_weights(self, draws: list[LotteryDraw]) -> list[float]:
        """
        Compute per-draw decay weights.

        draws must be sorted by round_number ascending (oldest first).
        Returns weights in same order (oldest=lowest, newest=highest).
        Weights are NOT normalized -- they are raw decay values.
        """
        n = len(draws)
        if n == 0:
            return []
        # draws_since: newest draw = 0, oldest = n-1
        return [0.5 ** ((n - 1 - i) / self.halflife) for i in range(n)]

    def compute_weighted_frequencies(
        self, draws: list[LotteryDraw]
    ) -> dict[int, float]:
        """
        Compute weighted frequency for each number 1-45.

        Args:
            draws: Machine-filtered LotteryDraw list, sorted by round_number asc.

        Returns:
            dict mapping number (1-45) -> weighted frequency (float).
            Numbers that never appeared have value 0.0.
        """
        weights = self.compute_weights(draws)
        freq: dict[int, float] = {n: 0.0 for n in range(1, 46)}

        for draw, weight in zip(draws, weights):
            for number in draw.numbers:
                freq[number] += weight

        return freq
```

**Why this interface:**
1. `compute_weights()` is public -- Phase 3 strategies receive the weight array directly (as shown in ARCHITECTURE.md's `generate(draws, weights)` signature).
2. `compute_weighted_frequencies()` is the primary output for Phase 2 verification -- returns the weighted number frequency dict.
3. Numbers 1-45 are pre-initialized to 0.0 so consumers always get a complete dict.

### Integration with DataLoader

```python
# Usage pattern (will be wired in Phase 3):
from app.services.data_loader import DataLoader
from app.services.decay_engine import DecayEngine
from app.config import settings

loader = DataLoader(settings.DATA_PATH)
loader.load_and_validate()

engine = DecayEngine(halflife=settings.DECAY_HALFLIFE)
draws = loader.get_draws_for_machine("1호기")
weighted_freq = engine.compute_weighted_frequencies(draws)
# weighted_freq: {1: 2.34, 2: 1.87, ..., 45: 3.12}
```

### Config Addition

```python
# backend/app/config.py -- add one field
class Settings:
    DATA_PATH: Path = Path(__file__).parent.parent / "data" / "new_res.json"
    CORS_ORIGINS: list[str] = ["http://localhost:5173"]
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DECAY_HALFLIFE: int = 30  # NEW: draws for weight to halve
```

### Anti-Patterns to Avoid

- **Using pandas ewm() for this formula:** The user specified `0.5^(t/h)`, which is a simple power function. Pandas ewm computes a different weighted moving average. Do not conflate the two.
- **Normalizing weights to sum to 1.0:** The architecture document shows normalized weights, but for frequency counting, raw weights are more intuitive. Each number's weighted frequency is a direct sum of draw weights. Normalization can happen downstream if needed (e.g., converting to probabilities).
- **Importing numpy just for this:** The computation is `0.5 ** (x / 30)` over at most 147 items. A list comprehension is clear, fast, and dependency-free.
- **Hardcoding halflife=30 in the engine:** Use the constructor parameter with default. Tests can inject different values; config.py controls the production default.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Exponential decay math | Custom numpy-based decay framework | Python `**` operator | 134 items, scalar math. A list comprehension is 5 lines. |
| Number frequency counting | pandas groupby + value_counts | Simple dict accumulation loop | No pandas installed. A `for draw, weight in zip(...)` loop is clearer for this case. |
| Data validation | Custom validation for LotteryDraw input | Existing Pydantic `LotteryDraw` schema | Already validated at load time by DataLoader. DecayEngine trusts its input. |

**Key insight:** This phase is a small, focused mathematical module. The entire implementation is ~40 lines of pure Python. Resist the urge to add dependencies or over-engineer.

## Common Pitfalls

### Pitfall 1: draws_since Index Direction
**What goes wrong:** Confusing whether `draws_since=0` means the oldest or newest draw. If the direction is wrong, old draws get HIGH weight and new draws get LOW weight -- the exact opposite of the requirement.
**Why it happens:** DataLoader returns draws sorted ascending by round_number (oldest first, index 0). The decay formula needs `draws_since` relative to the newest draw.
**How to avoid:** For draw at index `i` in an ascending-sorted list of length `n`: `draws_since = n - 1 - i`. The newest draw (index n-1) gets `draws_since=0`, weight=1.0. The oldest (index 0) gets `draws_since=n-1`.
**Warning signs:** Unit test showing the first element has weight 1.0 and last element has a small weight -- that means oldest=highest, which is wrong.

### Pitfall 2: REQUIREMENTS.md vs CONTEXT.md Halflife Discrepancy
**What goes wrong:** REQUIREMENTS.md specifies `DECAY-02: halflife default 50`. CONTEXT.md decision D-02 locks halflife to 30. Using the wrong default leads to incorrect decay behavior.
**Why it happens:** The user changed the halflife during discussion (from the research-recommended 50 to a more aggressive 30).
**How to avoid:** CONTEXT.md decisions take precedence. Default halflife = **30**. After implementation, update REQUIREMENTS.md to reflect the decision.
**Warning signs:** Config showing halflife=50 instead of 30.

### Pitfall 3: Empty Draw List Edge Case
**What goes wrong:** If a machine has 0 draws (not the case in current data, but defensive coding), the engine divides by zero or returns unexpected results.
**How to avoid:** Return empty list from `compute_weights([])` and `{n: 0.0 for n in range(1, 46)}` from `compute_weighted_frequencies([])`. Both are valid "zero information" responses.

### Pitfall 4: NumPy Type Leaking into Return Value
**What goes wrong:** If numpy is later used in the computation, `numpy.float64` types in the returned dict break JSON serialization (see PITFALLS.md Pitfall 5).
**How to avoid:** Use pure Python math. Return native `float` values. If numpy is ever introduced, add `.item()` or `float()` conversion at the boundary.
**Warning signs:** `TypeError: Object of type float64 is not JSON serializable` in later phases.

### Pitfall 5: Aggressive Decay Reducing Effective Sample Size
**What goes wrong:** With halflife=30, for 1hoogi (134 draws), effective sample size drops to ~79. For pattern analysis in Phase 3, this may not be enough for reliable pair frequencies.
**Why it happens:** The user intentionally chose aggressive decay (D-02). This is a known tradeoff, not a bug.
**How to avoid:** Document the effective sample size in code comments. Phase 3 strategies should be aware that weighted N < raw N. Consider logging effective N when DecayEngine is used.

## Code Examples

### Core Decay Computation (Verified Mathematically)

```python
# Weight formula: 0.5^(draws_since / halflife)
# For halflife=30, 1호기 (134 draws):
#
# draws_since=0   (newest): weight = 0.5^(0/30)   = 1.0000
# draws_since=10           : weight = 0.5^(10/30)  = 0.7937
# draws_since=30           : weight = 0.5^(30/30)  = 0.5000
# draws_since=50           : weight = 0.5^(50/30)  = 0.3150
# draws_since=90           : weight = 0.5^(90/30)  = 0.1250
# draws_since=133 (oldest): weight = 0.5^(133/30)  = 0.0463
#
# Sum of raw weights: ~41.8
# Effective sample size: ~79.1 draws (out of 134)

def compute_weights(n: int, halflife: int = 30) -> list[float]:
    """Pure Python weight computation, no external deps."""
    return [0.5 ** ((n - 1 - i) / halflife) for i in range(n)]
```

### Weighted Frequency Accumulation

```python
# Given draws sorted ascending by round_number (DataLoader guarantee)
weights = engine.compute_weights(draws)
freq = {n: 0.0 for n in range(1, 46)}

for draw, weight in zip(draws, weights):
    for number in draw.numbers:  # 6 numbers per draw
        freq[number] += weight

# Result: {1: 2.34, 2: 1.87, ..., 45: 3.12}
# Higher values = number appeared more in recent (heavily-weighted) draws
```

### Test: Verify Exponential Decay Curve

```python
def test_weights_follow_exponential_decay():
    """Weights must follow w = 0.5^(draws_since / halflife)."""
    engine = DecayEngine(halflife=30)
    draws = make_dummy_draws(n=100)  # 100 sequential draws
    weights = engine.compute_weights(draws)

    # Newest draw (last) should have weight 1.0
    assert weights[-1] == pytest.approx(1.0)

    # Draw 30 positions back should have weight 0.5
    assert weights[-31] == pytest.approx(0.5, rel=1e-4)

    # Draw 60 positions back should have weight 0.25
    assert weights[-61] == pytest.approx(0.25, rel=1e-4)

    # Weights should be monotonically increasing
    for i in range(1, len(weights)):
        assert weights[i] >= weights[i - 1]
```

### Test: Integration with Real DataLoader

```python
def test_weighted_frequencies_with_real_data(loader):
    """DecayEngine produces valid weighted frequencies from real data."""
    engine = DecayEngine(halflife=30)
    draws = loader.get_draws_for_machine("1호기")
    freq = engine.compute_weighted_frequencies(draws)

    # All 45 numbers present in result
    assert set(freq.keys()) == set(range(1, 46))

    # All values are non-negative floats
    assert all(isinstance(v, float) and v >= 0.0 for v in freq.values())

    # At least some numbers have non-zero frequency
    assert sum(freq.values()) > 0

    # Total weighted frequency should be close to 6 * sum_of_weights
    # (6 numbers per draw, each contributes its weight)
    weights = engine.compute_weights(draws)
    expected_total = 6 * sum(weights)
    assert sum(freq.values()) == pytest.approx(expected_total, rel=1e-6)
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| STACK.md recommended pandas `ewm()` with halflife=50 | User locked `0.5^(t/h)` with halflife=30, pure Python | Phase 2 discussion (2026-03-26) | No pandas dependency needed. Different formula than ewm. More aggressive decay. |
| ARCHITECTURE.md showed `utils/decay.py` with numpy | CONTEXT.md locked `services/decay_engine.py` as independent module | Phase 2 discussion (2026-03-26) | Module location changed. Class-based service, not utility function. |

**Deprecated/outdated guidance from earlier research:**
- STACK.md's `pandas ewm()` recommendation: Superseded by user's explicit formula choice
- ARCHITECTURE.md's `utils/decay.py` location: Superseded by CONTEXT.md D-06 (`services/decay_engine.py`)
- ARCHITECTURE.md's numpy dependency: Not needed; pure Python suffices
- REQUIREMENTS.md halflife=50 default: Overridden by CONTEXT.md D-02 (halflife=30)

## Open Questions

1. **Should REQUIREMENTS.md be updated to reflect halflife=30?**
   - What we know: REQUIREMENTS.md says halflife=50, CONTEXT.md locks halflife=30
   - What's unclear: Whether to update REQUIREMENTS.md now or at phase completion
   - Recommendation: Update REQUIREMENTS.md DECAY-02 to say halflife=30 as part of this phase's implementation

2. **Should `compute_weights()` normalize weights to sum to 1.0?**
   - What we know: ARCHITECTURE.md shows normalized weights. But for frequency counting, raw weights produce more interpretable results (weighted frequency = sum of weights for draws containing that number).
   - What's unclear: Whether Phase 3 strategies expect normalized or raw weights
   - Recommendation: Keep raw weights in `compute_weights()`. Add an optional `normalize=False` parameter. Phase 3 strategies can normalize if needed via the `generate(draws, weights)` interface.

3. **Should DecayEngine be instantiated at startup (lifespan) or per-request?**
   - What we know: DecayEngine is lightweight (just stores halflife). Config does not change at runtime.
   - What's unclear: Whether to mirror DataLoader's lifespan pattern
   - Recommendation: Instantiate in lifespan alongside DataLoader and store in `data_store`. This keeps the pattern consistent and allows future halflife changes without restart (if config becomes dynamic).

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest >=9.0.2 with pytest-asyncio |
| Config file | `backend/pyproject.toml` ([tool.pytest.ini_options]) |
| Quick run command | `cd backend && uv run pytest tests/test_decay_engine.py -x -q` |
| Full suite command | `cd backend && uv run pytest -x -q` |

### Phase Requirements -> Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| DECAY-01 | Newest draw gets highest weight, weights follow `0.5^(t/h)` curve | unit | `uv run pytest tests/test_decay_engine.py::test_newest_draw_highest_weight -x` | Wave 0 |
| DECAY-01 | Weights are monotonically increasing (oldest to newest) | unit | `uv run pytest tests/test_decay_engine.py::test_weights_monotonically_increasing -x` | Wave 0 |
| DECAY-01 | Weight at halflife distance equals 0.5 | unit | `uv run pytest tests/test_decay_engine.py::test_halflife_gives_half_weight -x` | Wave 0 |
| DECAY-01 | Weighted frequencies cover all 45 numbers | unit | `uv run pytest tests/test_decay_engine.py::test_weighted_frequencies_all_numbers -x` | Wave 0 |
| DECAY-01 | Weighted frequency total equals 6 * sum(weights) | unit | `uv run pytest tests/test_decay_engine.py::test_weighted_frequency_total -x` | Wave 0 |
| DECAY-02 | Default halflife is 30 (from config) | unit | `uv run pytest tests/test_decay_engine.py::test_default_halflife_from_config -x` | Wave 0 |
| DECAY-02 | Custom halflife changes decay rate without modifying core logic | unit | `uv run pytest tests/test_decay_engine.py::test_custom_halflife -x` | Wave 0 |
| DECAY-01 | Integration: DataLoader -> DecayEngine produces valid output | integration | `uv run pytest tests/test_decay_engine.py::test_integration_with_data_loader -x` | Wave 0 |

### Sampling Rate
- **Per task commit:** `cd backend && uv run pytest tests/test_decay_engine.py -x -q`
- **Per wave merge:** `cd backend && uv run pytest -x -q`
- **Phase gate:** Full suite green before `/gsd:verify-work`

### Wave 0 Gaps
- [ ] `backend/tests/test_decay_engine.py` -- covers DECAY-01, DECAY-02 (8 test cases above)
- No new fixtures needed -- can reuse existing `loader` fixture from `test_data_loader.py` (or import from conftest)
- No framework install needed -- pytest is already configured and working (16 tests collected)

## Sources

### Primary (HIGH confidence)
- `backend/app/services/data_loader.py` -- Verified DataLoader interface: `get_draws_for_machine()` returns `list[LotteryDraw]` sorted ascending by `round_number`
- `backend/app/schemas/lottery.py` -- Verified LotteryDraw schema: `round_number: int`, `numbers: list[int]` (6 sorted, 1-45)
- `backend/app/config.py` -- Verified Settings class: simple class attributes, no Pydantic BaseSettings
- `backend/pyproject.toml` -- Verified dependencies: Python 3.13, FastAPI, Pydantic, pytest (NO numpy/pandas)
- Mathematical verification: `0.5^(133/30) = 0.0463`, effective N ~79.1 for 134 draws at halflife=30

### Secondary (MEDIUM confidence)
- `.planning/research/ARCHITECTURE.md` -- Strategy Pattern interface shows `generate(draws, weights)` -- DecayEngine's `compute_weights()` feeds this
- `.planning/research/PITFALLS.md` -- NumPy serialization pitfall (#5) reinforces pure Python choice
- `.planning/research/STACK.md` -- Documented pandas ewm approach, now superseded by user's explicit formula

### Tertiary (LOW confidence)
- None -- all findings verified against existing code and mathematical proof

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH -- no new dependencies needed, verified against pyproject.toml
- Architecture: HIGH -- follows existing DataLoader class pattern, locked decisions from CONTEXT.md
- Pitfalls: HIGH -- index direction and halflife discrepancy verified empirically
- Formula correctness: HIGH -- mathematically verified with Python computation

**Research date:** 2026-03-26
**Valid until:** 2026-04-26 (stable -- pure Python math does not change)
