# Phase 4: Full Prediction Engine - Research

**Researched:** 2026-03-27
**Domain:** Lottery number prediction strategies (Pattern, Range, Balance, Composite) + diversity enforcement
**Confidence:** HIGH

## Summary

Phase 4 extends the prediction engine from 1 strategy (Frequency, built in Phase 3) to 5 strategies producing 25 total games. The existing `PredictionStrategy` ABC, `FrequencyStrategy` reference implementation, `DecayEngine`, and `DataLoader` are all proven and stable (42 tests pass). Each new strategy follows the identical `generate(draws, weighted_frequencies) -> list[list[int]]` interface.

The core technical challenge is not the ABC pattern (already established) but the **algorithmic design** of each strategy: how Pattern combines pair frequency, consecutive numbers, and ending-digit patterns; how Range maps float ratios to integer counts summing to 6; how Balance simultaneously satisfies odd/even and high/low constraints; and how Composite merges scores from 4 heterogeneous strategies into a single weight vector. Real data analysis (included below) provides the per-machine statistical profiles that each strategy must consume.

**Primary recommendation:** Implement strategies in dependency order: Pattern -> Range -> Balance -> Composite (last, since it depends on all 4). Each strategy gets its own file, registers in `STRATEGY_MAP`, and the `PredictRequest.strategy` Literal type expands to include all 5 names. Diversity enforcement reuses the existing `_generate_diverse_games` pattern (4+ overlap rejection, 100 retry limit).

<user_constraints>

## User Constraints (from CONTEXT.md)

### Locked Decisions
- **D-01:** Pattern Strategy algorithm is Claude's Discretion -- combine pair frequency, consecutive numbers, ending-digit patterns
- **D-02:** Use per-machine frequent pairs: 1호기(6,38), 2호기(7,19), 3호기(13,33) etc.
- **D-03:** Range Strategy: per-machine range ratios -> per-range number count -> random within range
- **D-04:** Range rounding: round ratios so they sum to exactly 6
- **D-05:** Balance Strategy: reflect per-machine odd/even + high/low ratio tendencies
- **D-06:** Balance must satisfy odd/even AND high/low simultaneously
- **D-07:** Composite weights: Frequency 40% / Pattern 20% / Range 20% / Balance 20%
- **D-08:** Composite merges per-number scores via weighted average -> probability -> selection
- **D-09:** Composite implemented last (depends on all 4 strategies)
- **D-10:** Within-strategy diversity only: 4+ overlap rejection (same as Phase 3)
- **D-11:** Cross-strategy diversity is natural (different algorithms)

### Claude's Discretion
- Pattern Strategy concrete algorithm design
- Balance Strategy method for simultaneous odd/even + high/low satisfaction
- Composite Strategy exact score integration method
- Test strategy for each new strategy (unit tests)

### Deferred Ideas (OUT OF SCOPE)
None -- discussion stayed within phase scope

</user_constraints>

<phase_requirements>

## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| PRED-02 | Pattern strategy: pair frequency + consecutive + ending-digit patterns -> 5 games | Algorithm design detailed in Architecture Patterns section; per-machine pair/consecutive/ending-digit data analyzed |
| PRED-03 | Range strategy: 5-zone distribution matching machine profile -> 5 games | Per-machine range distribution data computed; rounding algorithm specified |
| PRED-04 | Balance strategy: odd/even + high/low ratio targeting -> 5 games | Per-machine ratio distributions analyzed; constraint-satisfaction approach documented |
| PRED-05 | Composite strategy: weighted combination (40/20/20/20) of all 4 -> 5 games | Score normalization and weighted-average approach documented |
| PRED-07 | No identical games among 25 total | Within-strategy diversity via existing 4+ overlap pattern; cross-strategy natural diversity |

</phase_requirements>

## Standard Stack

### Core (Already Installed -- No New Dependencies)

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Python | 3.13 | Runtime | Already in use |
| FastAPI | >=0.135.2 | API framework | Already in use |
| Pydantic | >=2.12.5 | Schema validation | Already in use |
| random (stdlib) | -- | Weighted selection | `random.choices` established in FrequencyStrategy |
| collections (stdlib) | -- | Counter for pair/digit analysis | Standard lib, no install needed |
| itertools (stdlib) | -- | combinations for pair generation | Standard lib, no install needed |

### No New Dependencies Required

Phase 4 is pure Python algorithmic work. All strategies use `random.choices` for weighted selection (established pattern from Phase 3). Statistical analysis (pair counting, range bucketing, ratio parsing) uses only stdlib `collections.Counter` and basic math. No numpy, pandas, or external libraries needed.

## Architecture Patterns

### Recommended Project Structure (Changes from Phase 3)
```
backend/app/strategies/
├── __init__.py          # MODIFY: add 4 new strategies to STRATEGY_MAP
├── base.py              # UNCHANGED: PredictionStrategy ABC
├── frequency.py         # UNCHANGED: reference implementation
├── pattern.py           # NEW: PatternStrategy
├── range.py             # NEW: RangeStrategy
├── balance.py           # NEW: BalanceStrategy
└── composite.py         # NEW: CompositeStrategy

backend/app/schemas/
└── lottery.py           # MODIFY: expand PredictRequest.strategy Literal

backend/tests/
├── conftest.py          # MODIFY: add shared fixtures for new strategies
├── test_pattern_strategy.py    # NEW
├── test_range_strategy.py      # NEW
├── test_balance_strategy.py    # NEW
├── test_composite_strategy.py  # NEW
└── test_api.py          # MODIFY: add tests for new strategy endpoints
```

### Pattern 1: PatternStrategy Algorithm

**What:** Generates numbers using three pattern signals from machine-specific historical data: (1) frequent pairs, (2) consecutive number tendency, (3) ending-digit distribution.

**Algorithm (Claude's Discretion recommendation):**

```python
class PatternStrategy(PredictionStrategy):
    """
    Step 1: PAIR SEEDING
    - Count all pair frequencies from draws, weighted by decay weights
    - Select 1-2 pairs probabilistically (weighted by pair frequency)
    - This seeds 2-4 numbers per game

    Step 2: CONSECUTIVE INJECTION
    - If machine has >50% consecutive draws (1호기: 57.5%, 3호기: 55.1%),
      with 50% probability, add a consecutive neighbor to one seeded number
    - If 2호기 (42.6%), lower injection probability to 30%

    Step 3: ENDING-DIGIT COMPLETION
    - For remaining slots (to reach 6), compute per-machine ending-digit
      frequency distribution
    - For each slot, pick an ending digit weighted by machine's digit freq,
      then pick a specific number with that ending digit (weighted by
      weighted_frequencies from DecayEngine)

    Step 4: VALIDATION
    - Ensure 6 unique numbers, range [1,45], sorted ascending
    - If duplicates from pair+consecutive, regenerate conflicting numbers
    """
```

**Per-machine pair data (top 5, verified from actual data):**
- 1호기: (6,38)=8, (31,41)=7, (21,30)=7, (10,38)=7, (12,26)=7
- 2호기: (7,19)=8, (1,28)=7, (7,9)=7, (28,42)=7, (11,17)=7
- 3호기: (13,33)=7, (33,38)=7, (21,35)=7, (14,15)=7, (35,36)=7

**Per-machine ending-digit distribution (verified):**
- 1호기: digits 1-4 slightly favored (88,90,93,86), digits 7-9 lower (72,71,64)
- 2호기: digit 8 highest (91), digit 0 lowest (60), fairly even otherwise
- 3호기: digit 3 highest (113), digit 5 second (108), digit 8 lowest (70)

**Per-machine consecutive tendency:**
- 1호기: 57.5% of draws contain consecutive numbers
- 2호기: 42.6% (lowest)
- 3호기: 55.1%

**When to use:** Called for `strategy="pattern"`.

### Pattern 2: RangeStrategy Algorithm

**What:** Distributes numbers across 5 zones matching machine's historical distribution.

**Algorithm:**

```python
class RangeStrategy(PredictionStrategy):
    """
    Step 1: COMPUTE ZONE RATIOS
    - Count numbers per zone from draws (weighted by decay weights)
    - Zones: 1-9, 10-19, 20-29, 30-39, 40-45
    - Normalize to per-game counts (total must be 6)

    Step 2: ROUND TO INTEGER COUNTS (D-04)
    - Use largest-remainder method:
      a. Floor all ratios
      b. Sum floored values (will be <= 6)
      c. Distribute remaining slots to zones with largest fractional parts
    - This guarantees sum == 6 with minimal rounding distortion

    Step 3: RANDOM SELECTION WITHIN ZONES
    - For each zone with count > 0:
      Pick count numbers randomly from that zone
      (optional: weight by weighted_frequencies for within-zone bias)

    Step 4: ASSEMBLE AND VALIDATE
    - Combine all zone picks, sort ascending
    - Ensure 6 unique numbers in [1, 45]
    """
```

**Per-machine zone distribution (verified, as numbers per 6-number game):**

| Zone | 1호기 | 2호기 | 3호기 |
|------|-------|-------|-------|
| 1-9 (9 nums) | 1.01 | 1.21 | 1.11 |
| 10-19 (10 nums) | 1.25 | 1.46 | 1.48 |
| 20-29 (10 nums) | 1.31 | 1.38 | 1.24 |
| 30-39 (10 nums) | 1.57 | 1.25 | 1.41 |
| 40-45 (6 nums) | 0.86 | 0.71 | 0.76 |

**Example rounding (1호기):** ratios [1.01, 1.25, 1.31, 1.57, 0.86] -> floors [1, 1, 1, 1, 0] = 4 -> need 2 more -> largest remainders: 0.86 (zone 40-45), 0.57 (zone 30-39) -> final [1, 1, 1, 2, 1] = 6

**Important:** Zone ratios should be computed dynamically from weighted data (using decay weights), not hardcoded from the averages above. The averages above are for illustration only.

### Pattern 3: BalanceStrategy Algorithm

**What:** Generates numbers satisfying both odd/even and high/low ratio targets simultaneously.

**Algorithm:**

```python
class BalanceStrategy(PredictionStrategy):
    """
    Step 1: DETERMINE TARGET RATIOS
    - From machine's historical draws, compute weighted distribution of
      odd/even ratios (e.g., "3:3" = 33%, "4:2" = 25%, "2:4" = 22%)
    - Probabilistically select a target odd:even ratio (weighted by frequency)
    - Similarly select a target high:low ratio
    - "High" = 23-45, "Low" = 1-22 (standard Korean lotto convention)

    Step 2: PARTITION NUMBER SPACE
    - 4 categories: odd-low, odd-high, even-low, even-high
      - odd-low: {1,3,5,7,9,11,13,15,17,19,21} (11 numbers)
      - odd-high: {23,25,27,29,31,33,35,37,39,41,43,45} (12 numbers)
      - even-low: {2,4,6,8,10,12,14,16,18,20,22} (11 numbers)
      - even-high: {24,26,28,30,32,34,36,38,40,42,44} (11 numbers)

    Step 3: COMPUTE CATEGORY COUNTS
    - Given target odd:even = a:b and high:low = c:d where a+b=6, c+d=6:
      odd_count = a, even_count = b, high_count = c, low_count = d
      odd_low = max(0, odd_count - high_count) ... solve via constraint satisfaction
      Actually: odd_high = min(odd_count, high_count), solve remaining 3 cells
      Use: odd_low = odd_count - odd_high, even_high = high_count - odd_high,
           even_low = 6 - odd_low - odd_high - even_high
      Must verify all >= 0; if not, resample ratios

    Step 4: SELECT NUMBERS
    - From each category, select the required count
    - Weight by weighted_frequencies for machine-specific bias

    Step 5: VALIDATE
    - 6 unique numbers, sorted, range [1, 45]
    """
```

**Per-machine odd/even distribution (verified, most common ratios):**
- 1호기: 3:3 (33%), 4:2 (25%), 2:4 (22%), 5:1 (9%), 1:5 (7%)
- 2호기: 4:2 (31%), 3:3 (29%), 2:4 (26%), 1:5 (7%), 5:1 (7%)
- 3호기: 3:3 (30%), 4:2 (27%), 2:4 (18%), 5:1 (14%), 1:5 (6%)

**Per-machine high/low distribution (verified):**
- 1호기: 3:3 (35%), 4:2 (28%), 2:4 (19%), 5:1 (13%), 1:5 (3%)
- 2호기: 4:2 (26%), 3:3 (25%), 2:4 (23%), 1:5 (13%), 5:1 (10%)
- 3호기: 3:3 (34%), 4:2 (26%), 2:4 (24%), 1:5 (7%), 5:1 (5%)

**High/Low boundary clarification:** Need to verify the exact cutoff. Standard Korean lotto convention uses 1-22 = low, 23-45 = high (22 low numbers, 23 high numbers). This is consistent with the data where "3:3" is the most common high/low ratio.

### Pattern 4: CompositeStrategy Algorithm

**What:** Merges scoring from all 4 strategies into unified weights.

**Algorithm:**

```python
class CompositeStrategy(PredictionStrategy):
    """
    Step 1: COLLECT PER-NUMBER SCORES FROM EACH STRATEGY
    - frequency_scores: weighted_frequencies directly (already dict[int, float])
    - pattern_scores: combine pair co-occurrence score + ending-digit score
    - range_scores: expected zone density per number (zone ratio / zone size)
    - balance_scores: probability of selection given combined ratio distributions

    Step 2: NORMALIZE EACH SCORE SET
    - Each strategy's scores -> normalize to sum=1.0 (probability distribution)
    - This ensures each strategy contributes on the same scale

    Step 3: WEIGHTED AVERAGE (D-07, D-08)
    - composite_score[n] = 0.40 * freq_norm[n]
                         + 0.20 * pattern_norm[n]
                         + 0.20 * range_norm[n]
                         + 0.20 * balance_norm[n]

    Step 4: PROBABILISTIC SELECTION
    - Use composite_scores as weights in random.choices (same as FrequencyStrategy)
    - Apply MIN_WEIGHT_FLOOR to prevent zero-probability numbers

    Step 5: DIVERSITY + VALIDATION
    - Same _generate_diverse_games pattern
    """
```

**Key design point:** The Composite strategy does NOT instantiate or call other strategies' `generate()` methods. Instead, it computes its own per-number scores using the same data signals (weighted frequencies, pair frequencies, zone distributions, balance ratios) and combines them into a single weight vector. This avoids circular dependencies and keeps each strategy independent.

### Pattern 5: Reusing Diversity Enforcement

**What:** All 4 new strategies reuse the `_generate_diverse_games` / `_select_unique` pattern from FrequencyStrategy.

**Options:**
1. **Composition (recommended):** Extract `_generate_diverse_games` and `_select_unique` into a shared mixin or utility, or have each strategy subclass from a `WeightedSelectionMixin` that provides these methods.
2. **Copy-paste:** Each strategy re-implements the diversity loop. Less DRY but simpler.
3. **Base class method:** Move `_generate_diverse_games` to `PredictionStrategy` base class. This changes the existing ABC contract.

**Recommendation:** Option 1 -- create a helper mixin or simply have Pattern/Balance/Composite call a shared utility. Range strategy has a different selection method (zone-based), so it handles diversity independently with the same overlap-check logic.

### Anti-Patterns to Avoid

- **Instantiating other strategies inside CompositeStrategy.generate():** Creates coupling and prevents independent testing. Instead, Composite computes its own scores.
- **Hardcoding statistical values:** Per-machine pair frequencies, range ratios, etc. must be computed from the `draws` parameter, not hardcoded from research data above.
- **Modifying PredictionStrategy ABC:** The ABC is stable. New strategies must conform to the existing `generate(draws, weighted_frequencies)` signature without changes.
- **Ignoring the weighted_frequencies parameter:** All strategies should incorporate decay-weighted frequencies, not just raw counts, to honor the time-decay architecture.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Weighted random selection | Custom probability math | `random.choices(population, weights=weights, k=1)` | Proven in FrequencyStrategy, handles edge cases |
| Integer rounding to fixed sum | Manual round() + adjust | Largest-remainder method (Hamilton's method) | Guaranteed correct sum, minimal distortion, ~10 lines |
| Pair frequency counting | Nested loops | `itertools.combinations(nums, 2)` + `Counter` | Cleaner, standard pattern |
| Overlap checking | Custom comparison | `len(set(a) & set(b))` | Already established in FrequencyStrategy |

## Common Pitfalls

### Pitfall 1: Range Rounding Doesn't Sum to 6
**What goes wrong:** Naive `round()` on zone ratios can produce sums of 5 or 7 instead of 6.
**Why it happens:** [1.01, 1.25, 1.31, 1.57, 0.86] rounds to [1, 1, 1, 2, 1] = 6 (lucky case), but [1.49, 1.49, 1.49, 1.49, 0.04] rounds to [1, 1, 1, 1, 0] = 4.
**How to avoid:** Use largest-remainder method: floor all, distribute deficit to highest fractional remainders.
**Warning signs:** Assert `sum(zone_counts) == 6` in every code path.

### Pitfall 2: Balance Constraint Infeasibility
**What goes wrong:** Random selection of odd:even = 5:1 AND high:low = 1:5 is infeasible because odd-low only has 11 numbers and you need 5 odd + 5 low, meaning at least 4 odd-low numbers, but also at most 1 high number total and at most 1 even number total, so odd_high = 0, even_high = 0, even_low = 1, odd_low = 5... but odd_low has only 11 numbers, this works. However, extreme cases like 6:0 odd with 0:6 high requires 6 odd-high numbers, and odd-high has 12, so it works. Actually the real infeasibility is: odd_high = min(odd, high). If odd + high > 6 + odd_high, then odd_low + even_high + even_low < 0. The constraint is: `odd_low = odd - odd_high >= 0` AND `even_high = high - odd_high >= 0` AND `even_low = 6 - odd_low - odd_high - even_high >= 0`. When odd=5, high=5: odd_high = min(5,5)=5, odd_low=0, even_high=0, even_low=1. Valid. When odd=6, high=0: odd_high=0, odd_low=6, even_high=0, even_low=0. Valid (need 6 odd-low numbers). All combinations of valid odd:even and high:low ratios are actually feasible. But the NUMBER POOL might be too small (e.g., need 6 odd-low from pool of 11 -- fine, but what if we also need specific weighted numbers and diversity?).
**How to avoid:** Validate category counts before selection. If infeasible, resample target ratios. Add retry loop with fallback.
**Warning signs:** Empty category pools, selection loops hanging.

### Pitfall 3: Composite Score Scale Mismatch
**What goes wrong:** Frequency scores might range [0.001, 5.0] while range scores range [0.01, 0.3]. Without normalization, the 40% weight on frequency completely dominates.
**How to avoid:** Normalize each strategy's score vector to sum=1.0 BEFORE applying weights. This makes each strategy contribute proportionally regardless of raw scale.
**Warning signs:** Composite output looking identical to frequency output.

### Pitfall 4: Pattern Strategy Pair Weighting Without Decay
**What goes wrong:** Counting raw pair frequencies treats round 800 and round 1216 equally, contradicting the time-decay architecture.
**How to avoid:** When counting pair frequencies, weight each draw's contribution by its decay weight. The `draws` list is ordered oldest-to-newest, and `weighted_frequencies` already reflects decay. For pairs, compute: `pair_freq[(a,b)] += decay_weight_for_draw`.
**Warning signs:** Pattern strategy ignoring the `weighted_frequencies` parameter entirely.

### Pitfall 5: PredictRequest Literal Type Not Updated
**What goes wrong:** `PredictRequest.strategy: Literal["frequency"]` blocks new strategies with 422 validation errors.
**How to avoid:** Expand to `Literal["frequency", "pattern", "range", "balance", "composite"]`.
**Warning signs:** API returning 422 for valid strategy names.

## Code Examples

### Largest-Remainder Rounding (for RangeStrategy)

```python
def round_to_sum(ratios: list[float], target: int = 6) -> list[int]:
    """Round float ratios to integers that sum to target.

    Uses largest-remainder method (Hamilton's method).
    Example: [1.01, 1.25, 1.31, 1.57, 0.86] -> [1, 1, 1, 2, 1]
    """
    floors = [int(r) for r in ratios]
    remainders = [r - f for r, f in zip(ratios, floors)]
    deficit = target - sum(floors)

    # Distribute deficit to indices with largest remainders
    indices_by_remainder = sorted(range(len(remainders)),
                                   key=lambda i: remainders[i],
                                   reverse=True)
    for i in range(deficit):
        floors[indices_by_remainder[i]] += 1

    return floors
```

### Weighted Pair Frequency Computation (for PatternStrategy)

```python
from collections import Counter
from itertools import combinations

def compute_weighted_pair_frequencies(
    draws: list[LotteryDraw],
    decay_weights: list[float],
) -> dict[tuple[int, int], float]:
    """Compute decay-weighted pair frequencies.

    Args:
        draws: Machine-filtered draws, oldest first.
        decay_weights: Parallel decay weights (same length as draws).

    Returns:
        Dict mapping (a, b) tuple (a < b) -> weighted frequency.
    """
    pair_freq: dict[tuple[int, int], float] = Counter()
    for draw, weight in zip(draws, decay_weights):
        for pair in combinations(draw.numbers, 2):
            pair_freq[pair] += weight
    return dict(pair_freq)
```

### Score Normalization (for CompositeStrategy)

```python
def normalize_scores(scores: dict[int, float]) -> dict[int, float]:
    """Normalize score dict to sum to 1.0 (probability distribution).

    Applies MIN_WEIGHT_FLOOR before normalizing.
    """
    MIN_FLOOR = 0.001
    floored = {n: max(s, MIN_FLOOR) for n, s in scores.items()}
    total = sum(floored.values())
    return {n: s / total for n, s in floored.items()}
```

### Balance Category Count Computation

```python
def compute_category_counts(
    odd_count: int, even_count: int,
    high_count: int, low_count: int
) -> dict[str, int]:
    """Compute counts for 4 categories: odd-low, odd-high, even-low, even-high.

    Returns dict with guaranteed non-negative values summing to 6.
    Raises ValueError if constraints are infeasible.
    """
    # Maximize odd-high overlap, then distribute remainder
    odd_high = min(odd_count, high_count)
    odd_low = odd_count - odd_high
    even_high = high_count - odd_high
    even_low = even_count - even_high

    if even_low < 0:
        # Reduce odd_high to make room
        adjustment = -even_low
        odd_high -= adjustment
        odd_low += adjustment
        even_high += adjustment
        even_low = 0

    counts = {
        "odd_low": odd_low,
        "odd_high": odd_high,
        "even_low": even_low,
        "even_high": even_high,
    }

    assert all(v >= 0 for v in counts.values()), f"Negative count: {counts}"
    assert sum(counts.values()) == 6, f"Sum != 6: {counts}"
    return counts
```

## Per-Machine Statistical Profiles (Reference Data)

**These values are derived from actual data analysis. Strategies must compute them dynamically from `draws`, not hardcode them.**

### Zone Distribution (numbers per 6-number game)

| Zone | 1호기 | 2호기 | 3호기 | Expected (uniform) |
|------|-------|-------|-------|-------------------|
| 1-9 (9/45) | 1.01 | 1.21 | 1.11 | 1.20 |
| 10-19 (10/45) | 1.25 | 1.46 | 1.48 | 1.33 |
| 20-29 (10/45) | 1.31 | 1.38 | 1.24 | 1.33 |
| 30-39 (10/45) | 1.57 | 1.25 | 1.41 | 1.33 |
| 40-45 (6/45) | 0.86 | 0.71 | 0.76 | 0.80 |

### Odd/Even Ratios (top 3 per machine)

| Ratio | 1호기 | 2호기 | 3호기 |
|-------|-------|-------|-------|
| 3:3 | 33% | 29% | 30% |
| 4:2 | 25% | 31% | 27% |
| 2:4 | 22% | 26% | 18% |

### High/Low Ratios (top 3 per machine)

| Ratio | 1호기 | 2호기 | 3호기 |
|-------|-------|-------|-------|
| 3:3 | 35% | 25% | 34% |
| 4:2 | 28% | 26% | 26% |
| 2:4 | 19% | 23% | 24% |

### High/Low Boundary

Standard Korean Lotto convention: **Low = 1-22, High = 23-45** (22 low numbers, 23 high numbers). This is confirmed by the data distributions where "3:3" is the modal ratio, consistent with a near-50/50 split.

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Single generate() for all strategies | Strategy Pattern ABC (Phase 3) | Phase 3 | Each strategy is independent, testable |
| Raw frequency counts | Decay-weighted frequencies via DecayEngine | Phase 2 | All strategies get recency-biased data |
| numpy/pandas for computation | Pure Python random.choices + stdlib | Phase 3 decision | No serialization issues, sufficient for 417 records |

## Open Questions

1. **Decay weights for pair/range/balance computation**
   - What we know: `weighted_frequencies` is passed to all strategies (dict[int, float] mapping number -> weighted freq). DecayEngine also provides `compute_weights(draws)` -> per-draw weights.
   - What's unclear: Pattern/Range/Balance need per-draw weights (not per-number weights) to compute weighted pair frequencies, weighted zone distributions, and weighted ratio distributions. The current signature only passes `weighted_frequencies` (per-number).
   - Recommendation: Strategies can recompute per-draw weights internally using the same formula (`0.5^((n-1-i)/halflife)`), or we pass them as additional context. Simplest: each strategy that needs per-draw weights instantiates `DecayEngine` or receives it via constructor injection. **Since DecayEngine is a singleton in data_store and halflife is in config, strategies can import it directly or compute weights from `len(draws)` and config.DECAY_HALFLIFE.**

2. **Composite score for Pattern/Range/Balance**
   - What we know: Composite needs a per-number (1-45) score from each strategy.
   - What's unclear: Pattern, Range, and Balance generate games via different mechanisms (constraint-based), not via simple per-number scoring.
   - Recommendation: Each strategy implements a `compute_scores(draws, weighted_frequencies) -> dict[int, float]` helper that returns per-number affinity scores, even though `generate()` uses a different mechanism. Composite calls these score methods. Alternatively, Composite computes its own scores using the same data signals each strategy uses. **Recommend the latter (Composite computes its own scores) to avoid coupling.**

## Integration Points

### Files to Modify

| File | Change | Why |
|------|--------|-----|
| `backend/app/schemas/lottery.py` | Expand `PredictRequest.strategy` Literal to include all 5 strategy names | Enable API to accept new strategies |
| `backend/app/strategies/__init__.py` | Import and register 4 new strategies in STRATEGY_MAP | Enable `get_strategy()` to find them |

### Files to Create

| File | Content |
|------|---------|
| `backend/app/strategies/pattern.py` | PatternStrategy class |
| `backend/app/strategies/range.py` | RangeStrategy class |
| `backend/app/strategies/balance.py` | BalanceStrategy class |
| `backend/app/strategies/composite.py` | CompositeStrategy class |
| `backend/tests/test_pattern_strategy.py` | Unit tests for PatternStrategy |
| `backend/tests/test_range_strategy.py` | Unit tests for RangeStrategy |
| `backend/tests/test_balance_strategy.py` | Unit tests for BalanceStrategy |
| `backend/tests/test_composite_strategy.py` | Unit tests for CompositeStrategy |

### Files Unchanged

| File | Why |
|------|-----|
| `backend/app/strategies/base.py` | ABC is stable, no interface changes needed |
| `backend/app/strategies/frequency.py` | Reference implementation, untouched |
| `backend/app/services/decay_engine.py` | Already provides everything needed |
| `backend/app/services/data_loader.py` | Already provides machine-filtered LotteryDraw lists |
| `backend/app/api/routes.py` | Strategy lookup via STRATEGY_MAP already handles new strategies dynamically |

**Note on routes.py:** The predict endpoint already uses `get_strategy(request.strategy)` which looks up from STRATEGY_MAP. Adding new strategies to STRATEGY_MAP is sufficient. However, `PredictRequest.strategy` Literal validation will reject unknown names, so the schema MUST be updated.

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest 9.0.2 + pytest-asyncio 1.3.0 |
| Config file | `backend/pyproject.toml` [tool.pytest.ini_options] |
| Quick run command | `cd backend && .venv/bin/python -m pytest -x -q` |
| Full suite command | `cd backend && .venv/bin/python -m pytest -v` |

### Phase Requirements -> Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| PRED-02 | Pattern strategy generates 5 valid games | unit | `.venv/bin/python -m pytest tests/test_pattern_strategy.py -x` | Wave 0 |
| PRED-02 | Pattern uses pair frequencies from data | unit | `.venv/bin/python -m pytest tests/test_pattern_strategy.py::TestPatternBias -x` | Wave 0 |
| PRED-03 | Range strategy generates 5 valid games | unit | `.venv/bin/python -m pytest tests/test_range_strategy.py -x` | Wave 0 |
| PRED-03 | Range zone distribution matches machine profile | unit | `.venv/bin/python -m pytest tests/test_range_strategy.py::TestRangeDistribution -x` | Wave 0 |
| PRED-04 | Balance strategy generates 5 valid games | unit | `.venv/bin/python -m pytest tests/test_balance_strategy.py -x` | Wave 0 |
| PRED-04 | Balance satisfies odd/even + high/low constraints | unit | `.venv/bin/python -m pytest tests/test_balance_strategy.py::TestBalanceConstraints -x` | Wave 0 |
| PRED-05 | Composite generates 5 valid games with weighted blend | unit | `.venv/bin/python -m pytest tests/test_composite_strategy.py -x` | Wave 0 |
| PRED-07 | No identical games within each strategy (4+ overlap) | unit | Per-strategy diversity tests | Wave 0 |
| PRED-07 | All 5 strategies accessible via API | integration | `.venv/bin/python -m pytest tests/test_api.py -x` | Modify existing |
| ALL | All strategies return valid 6-number sets | unit | `.venv/bin/python -m pytest -x -q` | Wave 0 |

### Sampling Rate
- **Per task commit:** `cd backend && .venv/bin/python -m pytest -x -q` (~0.2s)
- **Per wave merge:** `cd backend && .venv/bin/python -m pytest -v` (~0.3s)
- **Phase gate:** Full suite green before `/gsd:verify-work`

### Wave 0 Gaps
- [ ] `backend/tests/test_pattern_strategy.py` -- covers PRED-02
- [ ] `backend/tests/test_range_strategy.py` -- covers PRED-03
- [ ] `backend/tests/test_balance_strategy.py` -- covers PRED-04
- [ ] `backend/tests/test_composite_strategy.py` -- covers PRED-05
- [ ] Update `backend/tests/test_api.py` -- add tests for pattern/range/balance/composite endpoints

Existing test infrastructure (pytest, conftest.py with async client, test_frequency_strategy.py pattern) is fully adequate. No framework installation or configuration needed.

## Sources

### Primary (HIGH confidence)
- `backend/app/strategies/base.py` -- PredictionStrategy ABC contract (verified by reading)
- `backend/app/strategies/frequency.py` -- Reference implementation with diversity enforcement (verified by reading)
- `backend/app/strategies/__init__.py` -- Strategy registry pattern (verified by reading)
- `backend/app/services/decay_engine.py` -- DecayEngine API (verified by reading)
- `backend/app/schemas/lottery.py` -- PredictRequest Literal type, LotteryDraw fields (verified by reading)
- `new_res.json` -- Actual lottery data analysis (417 records, per-machine statistics computed via Python)

### Secondary (MEDIUM confidence)
- `.planning/research/ARCHITECTURE.md` -- Strategy Pattern design, data flow
- `.planning/research/FEATURES.md` -- Strategy generation specifications
- `.planning/research/PITFALLS.md` -- Confirmation bias, diversity concerns

### Tertiary (LOW confidence)
- Hamilton's method / largest-remainder rounding: well-established mathematical technique, no verification needed

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH -- no new dependencies, reusing established patterns
- Architecture: HIGH -- ABC pattern proven in Phase 3, each strategy is independent
- Algorithm design: MEDIUM-HIGH -- Pattern strategy algorithm is novel (Claude's discretion), but follows established weighted-selection patterns
- Pitfalls: HIGH -- identified from actual data analysis and code review

**Research date:** 2026-03-27
**Valid until:** Indefinite (algorithms are project-specific, not library-dependent)
