# Phase 3: Prediction Pipeline (Vertical Slice) - Research

**Researched:** 2026-03-26
**Domain:** Strategy Pattern implementation, probabilistic number selection, FastAPI endpoint integration
**Confidence:** HIGH

## Summary

Phase 3 implements the first complete prediction pipeline: a FrequencyStrategy that uses DecayEngine's weighted frequencies to generate 5 diverse game sets of 6 numbers each, exposed via POST /api/predict. This phase establishes the Strategy Pattern ABC that all subsequent strategies (Phase 4) will follow.

The core technical challenge is the number selection algorithm: converting DecayEngine's weighted frequencies (dict[int, float]) into probabilistic number selection via `random.choices`, handling duplicate rejection, and enforcing inter-game diversity (4+ overlap triggers regeneration). The existing codebase provides solid foundations -- DecayEngine, DataLoader, LotteryDraw schema, and the data_store lifespan pattern -- all of which the prediction pipeline will compose without modification.

**Primary recommendation:** Build in this order: (1) Strategy ABC + validators in `backend/app/strategies/`, (2) FrequencyStrategy implementation, (3) Pydantic request/response schemas, (4) POST /api/predict route wired to data_store, (5) unit + integration tests. Keep the prediction orchestration logic minimal in Phase 3 -- just FrequencyStrategy -- since Phase 4 will add the full PredictionEngine orchestrator.

<user_constraints>

## User Constraints (from CONTEXT.md)

### Locked Decisions
- **D-01:** Probabilistic selection -- DecayEngine's weighted frequencies converted to probabilities, then `random.choices(population, weights, k=6)` for number selection
- **D-02:** Duplicate handling -- choices returns with replacement, so repeat selection until 6 unique numbers obtained (or use non-replacement approach)
- **D-03:** Results always sorted ascending
- **D-04:** POST /api/predict -- JSON body: `{"machine": "1호기", "strategy": "frequency"}`
- **D-05:** Response format: `{"games": [[3,7,15,23,31,42], ...], "strategy": "frequency", "machine": "1호기"}`
- **D-06:** Invalid machine/strategy returns 400 error
- **D-07:** Diversity: new game with 4+ same numbers as existing game triggers regeneration. Max 100 attempts
- **D-08:** After 100 attempts without diversity, use most diverse result available
- **D-09:** ABC (Abstract Base Class) for PredictionStrategy interface -- `generate(draws, weights) -> list[list[int]]`
- **D-10:** FrequencyStrategy is the first concrete implementation
- **D-11:** Strategy module location: `backend/app/strategies/`

### Claude's Discretion
- Strategy ABC exact method signature details
- Test strategy (unit + API integration)
- Pydantic request/response model design

### Deferred Ideas (OUT OF SCOPE)
None -- discussion stayed within phase scope

</user_constraints>

<phase_requirements>

## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| PRED-01 | Frequency strategy -- apply time-decay weighted frequency to generate 5 games per machine | DecayEngine.compute_weighted_frequencies() provides dict[int, float]; random.choices with these weights performs probabilistic selection; diversity enforcement via overlap check |
| PRED-06 | Each game set contains exactly 6 numbers in 1-45 range, no duplicates, ascending order | LotteryDraw.validate_numbers() already validates this exact constraint; reuse same validation logic in strategy output |

</phase_requirements>

## Standard Stack

### Core (already installed)
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| FastAPI | >=0.135.2 | REST API framework | Already in pyproject.toml, provides Pydantic integration |
| Pydantic | >=2.12.5 | Request/response validation | Already in pyproject.toml, enforces API contracts |
| Python stdlib `random` | 3.13 | Probabilistic number selection | `random.choices(population, weights, k)` -- no external dependency needed |
| Python stdlib `abc` | 3.13 | Strategy Pattern ABC | `ABC`, `abstractmethod` for strategy interface |

### Supporting (already installed for testing)
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| pytest | 9.0.2 | Test framework | Unit tests for strategy, integration tests for API |
| pytest-asyncio | >=1.3.0 | Async test support | API integration tests via httpx |
| httpx | >=0.28.1 | Async HTTP client for tests | Test client for FastAPI endpoints |
| ruff | >=0.15.7 | Linting + formatting | Pre-commit quality checks |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| `random.choices` loop | `numpy.random.choice(replace=False)` | numpy adds dependency for trivial operation; stdlib random is sufficient for 45-number population |
| Manual duplicate loop | `random.sample` with custom weights | `random.sample` does not support weights; would need to implement weighted reservoir sampling |
| Simple overlap count | Jaccard distance | Overlap count (set intersection) is simpler and matches D-07 directly |

**No new installations required.** All dependencies are already in `pyproject.toml`.

## Architecture Patterns

### Recommended Project Structure (new files for Phase 3)
```
backend/app/
├── strategies/
│   ├── __init__.py          # Registry: STRATEGY_MAP dict
│   ├── base.py              # PredictionStrategy ABC
│   └── frequency.py         # FrequencyStrategy
├── schemas/
│   └── lottery.py           # Add PredictRequest, PredictResponse (extend existing)
├── services/
│   ├── data_loader.py       # UNCHANGED
│   └── decay_engine.py      # UNCHANGED
├── api/
│   └── routes.py            # Add POST /api/predict endpoint
├── config.py                # UNCHANGED
└── main.py                  # Add DecayEngine to data_store in lifespan
```

### Pattern 1: Strategy Pattern ABC

**What:** Abstract base class defining the interface all prediction strategies must implement. Each strategy is a standalone class that receives weighted draw data and returns 5 game sets.

**When to use:** Always -- this is the core extensibility pattern. Phase 4 adds 4 more strategies by implementing the same ABC.

**Why:** Open/Closed principle. Adding a new strategy requires zero changes to the API, route handler, or orchestration code.

```python
# backend/app/strategies/base.py
from abc import ABC, abstractmethod
from app.schemas.lottery import LotteryDraw


class PredictionStrategy(ABC):
    """Base class for all prediction strategies."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Strategy identifier (e.g., 'frequency')."""
        ...

    @property
    @abstractmethod
    def display_name(self) -> str:
        """Korean display name (e.g., '빈도 전략')."""
        ...

    @abstractmethod
    def generate(
        self,
        draws: list[LotteryDraw],
        weighted_frequencies: dict[int, float],
    ) -> list[list[int]]:
        """
        Generate 5 game sets from historical draws and weighted frequencies.

        Args:
            draws: Machine-filtered draws sorted by round_number ascending.
            weighted_frequencies: Dict mapping number (1-45) -> weighted frequency
                                  from DecayEngine.compute_weighted_frequencies().

        Returns:
            List of exactly 5 games. Each game is a sorted list of 6 unique
            integers in range [1, 45].
        """
        ...
```

**Key design choice:** The ABC receives `weighted_frequencies: dict[int, float]` rather than raw weights. This is because:
1. DecayEngine already computes this (no duplicated work)
2. FrequencyStrategy uses frequencies directly as selection weights
3. Phase 4 strategies can ignore frequencies and use raw draws if needed

### Pattern 2: Weighted Unique Number Selection

**What:** Select 6 unique numbers from 1-45 using weighted probabilities. `random.choices` selects WITH replacement, so a loop is needed to collect 6 unique numbers.

**When to use:** Inside FrequencyStrategy.generate() for each game.

```python
import random

def select_unique_weighted(
    population: list[int],
    weights: list[float],
    k: int = 6,
    max_attempts: int = 1000,
) -> list[int]:
    """Select k unique numbers via weighted sampling without replacement.

    Uses random.choices (with replacement) in a loop, discarding duplicates,
    until k unique numbers are collected.

    Returns:
        Sorted list of k unique numbers.

    Raises:
        RuntimeError: If max_attempts exceeded without collecting k unique numbers.
    """
    selected: set[int] = set()
    attempts = 0
    while len(selected) < k and attempts < max_attempts:
        pick = random.choices(population, weights=weights, k=1)[0]
        selected.add(pick)
        attempts += 1
    if len(selected) < k:
        raise RuntimeError(f"Could not select {k} unique numbers in {max_attempts} attempts")
    return sorted(selected)
```

**Important note on `random.choices` behavior:** It selects WITH replacement (same number can appear multiple times in a single call). Calling `random.choices(pop, weights, k=6)` can return `[3, 3, 7, 15, 15, 42]`. The decision D-02 explicitly addresses this: loop until 6 unique numbers are obtained.

**Alternative approach (also valid):** Call `random.choices(pop, weights, k=1)` in a loop, removing picked numbers from the pool after each selection. This changes the probability distribution slightly (conditional probabilities) but ensures uniqueness in exactly 6 calls.

### Pattern 3: Inter-Game Diversity Enforcement

**What:** After generating each new game, check overlap with all previously generated games. If any existing game shares 4+ numbers with the new game, regenerate.

**When to use:** In the generate() method, wrapping the number selection in a diversity loop.

```python
def _has_sufficient_diversity(new_game: list[int], existing_games: list[list[int]]) -> bool:
    """Check that new_game shares fewer than 4 numbers with every existing game."""
    new_set = set(new_game)
    for existing in existing_games:
        overlap = len(new_set & set(existing))
        if overlap >= 4:
            return False
    return True

def generate_diverse_games(
    population: list[int],
    weights: list[float],
    num_games: int = 5,
    max_diversity_attempts: int = 100,
) -> list[list[int]]:
    """Generate num_games diverse game sets."""
    games: list[list[int]] = []
    for _ in range(num_games):
        best_game = None
        best_min_distance = -1  # track "most diverse" fallback
        for attempt in range(max_diversity_attempts):
            candidate = select_unique_weighted(population, weights)
            if _has_sufficient_diversity(candidate, games):
                games.append(candidate)
                break
            # Track best fallback (D-08)
            min_overlap = min(
                (len(set(candidate) & set(g)) for g in games),
                default=0,
            )
            if best_game is None or min_overlap < best_min_distance:
                best_min_distance = min_overlap
                best_game = candidate
        else:
            # D-08: max attempts exceeded, use most diverse candidate
            games.append(best_game if best_game else candidate)
    return games
```

### Pattern 4: Strategy Registry

**What:** A simple dict mapping strategy name strings to strategy class instances. Used by the route handler to look up the requested strategy.

**When to use:** In `strategies/__init__.py` -- single source of truth for available strategies.

```python
# backend/app/strategies/__init__.py
from app.strategies.frequency import FrequencyStrategy

# Registry: strategy name -> instance
STRATEGY_MAP: dict[str, "PredictionStrategy"] = {
    "frequency": FrequencyStrategy(),
}

def get_strategy(name: str) -> "PredictionStrategy":
    """Look up strategy by name. Raises KeyError if not found."""
    if name not in STRATEGY_MAP:
        raise KeyError(f"Unknown strategy: {name}. Available: {list(STRATEGY_MAP.keys())}")
    return STRATEGY_MAP[name]
```

### Pattern 5: API Endpoint Wired to data_store

**What:** The POST /api/predict endpoint accesses DataLoader and DecayEngine from `data_store` (initialized in lifespan), looks up the strategy, and returns results.

**When to use:** In `routes.py` for the new prediction endpoint.

```python
# In routes.py (addition)
@router.post("/predict", response_model=PredictResponse)
def predict_numbers(request: PredictRequest):
    """Generate prediction numbers using specified strategy.

    Uses sync def (not async def) because number generation
    involves CPU-bound random sampling.
    """
    loader = data_store.get("loader")
    if loader is None:
        raise HTTPException(status_code=503, detail="Data not loaded")

    try:
        draws = loader.get_draws_for_machine(request.machine)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    try:
        strategy = get_strategy(request.strategy)
    except KeyError as e:
        raise HTTPException(status_code=400, detail=str(e))

    decay_engine = data_store.get("decay_engine")
    weighted_freq = decay_engine.compute_weighted_frequencies(draws)
    games = strategy.generate(draws, weighted_freq)

    return PredictResponse(
        games=games,
        strategy=request.strategy,
        machine=request.machine,
    )
```

### Pattern 6: Extending data_store Lifespan

**What:** Add DecayEngine to the existing data_store dict during lifespan startup. This avoids creating a new DecayEngine instance per request.

```python
# In main.py lifespan (modified)
@asynccontextmanager
async def lifespan(app: FastAPI):
    loader = DataLoader(settings.DATA_PATH)
    loader.load_and_validate()
    data_store["loader"] = loader
    data_store["decay_engine"] = DecayEngine()
    print(f"Loaded {loader.total_records} lottery records")
    yield
    data_store.clear()
```

### Anti-Patterns to Avoid

- **Deterministic top-N selection:** Never pick the 6 highest-frequency numbers. This produces the same game every time and defeats the purpose. Use probabilistic selection (random.choices).
- **Recomputing weighted frequencies per game:** Compute once per request, pass to strategy. The frequencies do not change between games in a single request.
- **Creating PredictionEngine orchestrator in Phase 3:** Phase 3 only needs FrequencyStrategy. A full orchestrator (iterating over all strategies) belongs in Phase 4. Keep the route handler simple for now.
- **Importing from strategies in main.py:** Keep imports clean. The route handler imports from strategies, not main.py. The data_store pattern keeps dependency injection simple.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Weighted random selection | Custom probability distribution sampler | `random.choices(population, weights, k=1)` in a loop | stdlib is battle-tested, handles edge cases (zero weights, normalization) |
| Number validation (6 unique, 1-45, sorted) | New validator function | Reuse logic from `LotteryDraw.validate_numbers()` field_validator | Already tested and proven in Phase 1 |
| JSON serialization of int lists | Custom encoder | Pydantic response model with `list[list[int]]` | Pydantic handles native Python int serialization automatically |
| API request validation | Manual if/else checks | Pydantic `PredictRequest` with `Literal["frequency"]` for strategy, `Literal["1호기", "2호기", "3호기"]` for machine | FastAPI returns 422 automatically for invalid inputs |

**Key insight:** The number validation logic already exists in `LotteryDraw.validate_numbers()`. Extract or reuse that validation pattern for strategy output, rather than writing new validation code.

## Common Pitfalls

### Pitfall 1: random.choices Returns Duplicates
**What goes wrong:** Developer calls `random.choices(range(1,46), weights=freq_weights, k=6)` expecting 6 unique numbers. Gets `[7, 7, 15, 23, 31, 42]` because choices selects WITH replacement.
**Why it happens:** The function name suggests it picks "choices" (plural), leading to the assumption it handles uniqueness. It does not.
**How to avoid:** Always wrap in a uniqueness loop as shown in Pattern 2. Test with a heavily skewed weight distribution (one number with 99% weight) to force duplicates.
**Warning signs:** Tests pass with uniform weights but fail with skewed weights.

### Pitfall 2: Zero-Weight Numbers Block Selection
**What goes wrong:** If a number (e.g., 45) never appeared in the filtered draws, its weighted frequency is 0.0. `random.choices` assigns it zero probability -- it can never be selected. With extreme decay (halflife=10), many numbers might have near-zero weights, reducing the effective population below 6.
**Why it happens:** DecayEngine returns 0.0 for unseen numbers. Aggressive decay shrinks the effective pool.
**How to avoid:** Add a minimum floor weight (e.g., `max(freq, 0.001)`) to ensure all 45 numbers have some chance of selection. This also improves diversity. Alternatively, document that with default halflife=30, this is unlikely to be a problem (134 draws per machine covers most numbers).
**Warning signs:** `select_unique_weighted` hitting max_attempts on machines with less data.

### Pitfall 3: Diversity Loop Never Terminates
**What goes wrong:** With heavily skewed weights, most generated games look similar. The diversity check (4+ overlap = reject) rejects nearly every candidate, hitting the 100-attempt limit for every game after the first.
**Why it happens:** When 6-8 numbers dominate the weights, most random samples include 4+ of these dominant numbers.
**How to avoid:** D-08 handles this (use most diverse fallback after 100 attempts). But also consider: the floor weight from Pitfall 2 prevention naturally increases diversity. Test with a pathological frequency distribution where 6 numbers have 99% of total weight.
**Warning signs:** Logs showing consistent 100-attempt exhaustion.

### Pitfall 4: data_store Circular Import
**What goes wrong:** `routes.py` imports `data_store` from `main.py`. If `main.py` also imports from `routes.py` (for router registration), a circular import occurs.
**Why it happens:** The current codebase already has this pattern (`from app.main import data_store` in routes.py, `from app.api.routes import router` in main.py with a late import). It works because the main.py import of routes is at module bottom (`# noqa: E402`).
**How to avoid:** Maintain the existing late-import pattern. Do NOT move the router import to the top of main.py. When adding strategy imports in routes.py, import from `strategies/__init__.py`, not from `main.py`.
**Warning signs:** `ImportError: cannot import name 'data_store' from partially initialized module`.

### Pitfall 5: Sync def vs Async def for Prediction Endpoint
**What goes wrong:** Declaring the prediction endpoint as `async def` while `random.choices` and DecayEngine computations run synchronously blocks the event loop.
**Why it happens:** Developer follows async-first thinking without considering that random number generation is CPU-bound.
**How to avoid:** Use `def` (not `async def`) for the predict endpoint, matching the existing pattern in `get_machine_data`. FastAPI runs sync endpoints in a thread pool automatically.
**Warning signs:** This is already the established pattern -- `get_machine_data` uses `def`, `health_check` uses `async def`.

## Code Examples

### Pydantic Request/Response Models

```python
# Extend backend/app/schemas/lottery.py
from typing import Literal

class PredictRequest(BaseModel):
    machine: Literal["1호기", "2호기", "3호기"]
    strategy: Literal["frequency"]  # Phase 4 expands this Literal

class PredictResponse(BaseModel):
    games: list[list[int]]  # 5 games, each 6 sorted unique numbers
    strategy: str
    machine: str
```

**Note on D-05 response format:** The locked decision specifies `{"games": [[3,7,15,23,31,42], ...], "strategy": "frequency", "machine": "1호기"}`. The Pydantic model matches this exactly. Do NOT add extra fields (timestamp, metadata) in Phase 3 -- keep it minimal.

### FrequencyStrategy Core Logic

```python
# backend/app/strategies/frequency.py
import random
from app.strategies.base import PredictionStrategy
from app.schemas.lottery import LotteryDraw

class FrequencyStrategy(PredictionStrategy):
    NUM_GAMES = 5
    NUMBERS_PER_GAME = 6
    MAX_OVERLAP = 3          # 4+ overlap triggers regeneration (D-07)
    MAX_DIVERSITY_ATTEMPTS = 100
    MIN_WEIGHT_FLOOR = 0.001  # Prevent zero-probability numbers

    @property
    def name(self) -> str:
        return "frequency"

    @property
    def display_name(self) -> str:
        return "빈도 전략"

    def generate(
        self,
        draws: list[LotteryDraw],
        weighted_frequencies: dict[int, float],
    ) -> list[list[int]]:
        population = list(range(1, 46))
        weights = [
            max(weighted_frequencies.get(n, 0.0), self.MIN_WEIGHT_FLOOR)
            for n in population
        ]
        return self._generate_diverse_games(population, weights)

    def _select_unique(self, population: list[int], weights: list[float]) -> list[int]:
        selected: set[int] = set()
        while len(selected) < self.NUMBERS_PER_GAME:
            pick = random.choices(population, weights=weights, k=1)[0]
            selected.add(pick)
        return sorted(selected)

    def _generate_diverse_games(
        self, population: list[int], weights: list[float]
    ) -> list[list[int]]:
        games: list[list[int]] = []
        for _ in range(self.NUM_GAMES):
            best_candidate = None
            best_max_overlap = self.NUMBERS_PER_GAME  # worst case
            for attempt in range(self.MAX_DIVERSITY_ATTEMPTS):
                candidate = self._select_unique(population, weights)
                max_overlap = max(
                    (len(set(candidate) & set(g)) for g in games),
                    default=0,
                )
                if max_overlap <= self.MAX_OVERLAP:
                    games.append(candidate)
                    break
                if max_overlap < best_max_overlap:
                    best_max_overlap = max_overlap
                    best_candidate = candidate
            else:
                # D-08 fallback
                games.append(best_candidate if best_candidate else candidate)
        return games
```

### Validation Helper (reuse existing pattern)

```python
# backend/app/strategies/base.py or a shared utils module
def validate_game(game: list[int]) -> None:
    """Validate a single game: 6 unique numbers, 1-45, sorted ascending.

    Reuses the same rules as LotteryDraw.validate_numbers().
    Raises ValueError on invalid game.
    """
    if len(game) != 6:
        raise ValueError(f"Expected 6 numbers, got {len(game)}")
    if any(n < 1 or n > 45 for n in game):
        raise ValueError(f"Numbers must be 1-45, got {game}")
    if game != sorted(game):
        raise ValueError(f"Numbers must be sorted ascending, got {game}")
    if len(set(game)) != 6:
        raise ValueError(f"Numbers must be unique, got {game}")
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| `random.sample(population, k)` uniform | `random.choices(population, weights, k)` weighted | Python 3.6+ | Enables weighted selection; requires duplicate handling |
| Pydantic v1 `@validator` | Pydantic v2 `@field_validator` + `@classmethod` | Pydantic v2 (2023) | Already adopted in existing LotteryDraw schema |
| `@app.on_event("startup")` | `@asynccontextmanager` lifespan | FastAPI 0.100+ | Already adopted in existing main.py |

**Deprecated/outdated:**
- `random.sample` does not support weights. Cannot be used for weighted selection.
- Pydantic v1 validator syntax -- project already uses v2 correctly.

## Open Questions

1. **Floor weight value (MIN_WEIGHT_FLOOR)**
   - What we know: Numbers with 0.0 frequency can never be selected. A floor prevents this.
   - What's unclear: Optimal floor value. 0.001 is reasonable but arbitrary.
   - Recommendation: Use 0.001 as default. This gives unseen numbers roughly 0.001/sum(all_weights) probability -- negligible but non-zero. Can be tuned later.

2. **Strategy Literal type expansion**
   - What we know: Phase 3 uses `Literal["frequency"]`. Phase 4 adds 4 more strategies.
   - What's unclear: Should we define a `StrategyName = Literal["frequency", "pattern", "range", "balance", "composite"]` now or expand later?
   - Recommendation: Define only `Literal["frequency"]` in Phase 3. Phase 4 expands the type. YAGNI.

3. **DecayEngine as singleton vs per-request**
   - What we know: DecayEngine is stateless (halflife is fixed at startup). Can be shared.
   - What's unclear: Should it live in data_store or be created per-request?
   - Recommendation: Add to data_store in lifespan (Pattern 6). Avoids repeated instantiation and reads settings once.

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest 9.0.2 + pytest-asyncio |
| Config file | `backend/pyproject.toml` [tool.pytest.ini_options] |
| Quick run command | `cd backend && uv run pytest tests/ -x -q` |
| Full suite command | `cd backend && uv run pytest tests/ -v` |

### Phase Requirements -> Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| PRED-01 | FrequencyStrategy generates 5 games using weighted frequencies | unit | `cd backend && uv run pytest tests/test_frequency_strategy.py -x` | Wave 0 |
| PRED-01 | POST /api/predict returns 5 games for frequency strategy | integration | `cd backend && uv run pytest tests/test_api.py::test_predict_frequency -x` | Wave 0 |
| PRED-06 | Each game has 6 unique numbers, 1-45, ascending | unit | `cd backend && uv run pytest tests/test_frequency_strategy.py::test_game_validity -x` | Wave 0 |
| PRED-06 | API response games pass number validation | integration | `cd backend && uv run pytest tests/test_api.py::test_predict_response_valid_numbers -x` | Wave 0 |
| D-07 | Inter-game diversity: no 4+ overlap between games | unit | `cd backend && uv run pytest tests/test_frequency_strategy.py::test_diversity -x` | Wave 0 |
| D-06 | Invalid machine/strategy returns 400 | integration | `cd backend && uv run pytest tests/test_api.py::test_predict_invalid_params -x` | Wave 0 |

### Sampling Rate
- **Per task commit:** `cd backend && uv run pytest tests/ -x -q`
- **Per wave merge:** `cd backend && uv run pytest tests/ -v`
- **Phase gate:** Full suite green before `/gsd:verify-work`

### Wave 0 Gaps
- [ ] `backend/tests/test_frequency_strategy.py` -- covers PRED-01, PRED-06, D-07 (unit tests for strategy logic)
- [ ] New test functions in `backend/tests/test_api.py` -- covers PRED-01, PRED-06, D-06 (integration tests for POST /predict)
- [ ] No framework install needed -- pytest already configured and working

## Sources

### Primary (HIGH confidence)
- `backend/app/services/decay_engine.py` -- Verified DecayEngine.compute_weighted_frequencies() returns dict[int, float] with keys 1-45
- `backend/app/services/data_loader.py` -- Verified DataLoader.get_draws_for_machine() returns list[LotteryDraw] sorted by round_number ascending
- `backend/app/schemas/lottery.py` -- Verified LotteryDraw.validate_numbers() enforces 6 unique, 1-45, sorted ascending
- `backend/app/main.py` -- Verified data_store dict pattern and lifespan context manager
- `backend/app/api/routes.py` -- Verified existing patterns: sync def for CPU-bound, async def for lightweight, data_store access
- Python 3.13 `random.choices` -- Verified: selects WITH replacement, supports weights parameter
- `.planning/phases/03-prediction-pipeline-vertical-slice/03-CONTEXT.md` -- All 11 locked decisions

### Secondary (MEDIUM confidence)
- `.planning/research/ARCHITECTURE.md` -- Strategy Pattern design, project structure, data flow
- `.planning/research/FEATURES.md` -- Frequency strategy methodology description
- `.planning/research/PITFALLS.md` -- Diversity issues, zero-weight edge cases, gambler's fallacy framing

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH -- all libraries already installed, no new dependencies
- Architecture: HIGH -- extends established patterns (data_store, routes, schemas) with verified code
- Pitfalls: HIGH -- `random.choices` behavior verified empirically, diversity edge cases documented in PITFALLS.md

**Research date:** 2026-03-26
**Valid until:** 2026-04-26 (stable domain, no external dependency changes expected)
