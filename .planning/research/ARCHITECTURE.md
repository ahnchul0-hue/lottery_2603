# Architecture Patterns

**Domain:** Lottery prediction web application (machine-specific number analysis)
**Researched:** 2026-03-26
**Confidence:** HIGH (established patterns applied to specific domain)

## Recommended Architecture

**Monorepo, Two-Process Full Stack**: React (Vite) frontend and Python (FastAPI) backend in a single repository, communicating over HTTP REST. No database -- analysis runs against a static JSON file loaded into memory at startup.

```
Lottery_2603/
├── backend/                    # Python FastAPI analysis engine
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py             # FastAPI app entry, CORS, lifespan
│   │   ├── config.py           # Settings (data path, decay params)
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   └── routes.py       # API endpoints
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   ├── request.py      # PredictionRequest schema
│   │   │   └── response.py     # PredictionResponse, GameResult, Stats schemas
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── data_loader.py  # JSON loading + machine filtering
│   │   │   ├── prediction_engine.py  # Orchestrator: runs strategies, collects results
│   │   │   └── stats_service.py      # Statistics computation for dashboard
│   │   ├── strategies/
│   │   │   ├── __init__.py
│   │   │   ├── base.py         # ABC: PredictionStrategy
│   │   │   ├── frequency.py    # FrequencyStrategy
│   │   │   ├── pattern.py      # PatternStrategy
│   │   │   ├── range.py        # RangeStrategy
│   │   │   ├── balance.py      # BalanceStrategy
│   │   │   └── composite.py    # CompositeStrategy (weighted average of above 4)
│   │   └── utils/
│   │       ├── __init__.py
│   │       ├── decay.py        # Time decay weighting functions
│   │       └── validators.py   # Lotto number validation (6 unique, 1-45, sorted)
│   ├── requirements.txt
│   └── pyproject.toml
├── frontend/                   # React + Vite UI
│   ├── src/
│   │   ├── main.jsx
│   │   ├── App.jsx
│   │   ├── api/
│   │   │   └── client.js       # Axios/fetch wrapper for backend calls
│   │   ├── components/
│   │   │   ├── layout/
│   │   │   │   ├── Header.jsx
│   │   │   │   └── Footer.jsx
│   │   │   ├── prediction/
│   │   │   │   ├── MachineSelector.jsx    # 1호기/2호기/3호기 buttons
│   │   │   │   ├── PredictButton.jsx      # Trigger prediction
│   │   │   │   ├── StrategySection.jsx    # One strategy's 5 games
│   │   │   │   ├── GameCard.jsx           # Single game (6 numbers + bonus)
│   │   │   │   ├── NumberBall.jsx         # Styled number ball
│   │   │   │   └── PredictionResults.jsx  # All 5 strategies container
│   │   │   └── dashboard/
│   │   │       ├── StatsOverview.jsx      # Machine-level summary stats
│   │   │       ├── FrequencyChart.jsx     # Bar chart of number frequencies
│   │   │       ├── PatternDisplay.jsx     # Common pairs, consecutive patterns
│   │   │       └── DashboardPanel.jsx     # Dashboard container
│   │   ├── hooks/
│   │   │   ├── usePrediction.js    # Prediction API call + state
│   │   │   └── useStats.js         # Stats API call + state
│   │   ├── utils/
│   │   │   └── formatters.js       # Number/ratio display helpers
│   │   └── styles/
│   │       └── index.css           # Global styles + CSS custom properties
│   ├── index.html
│   ├── vite.config.js
│   └── package.json
├── new_res.json                # Data source (stays at root, backend reads it)
└── README.md
```

## Component Boundaries

### Backend Components

| Component | Responsibility | Communicates With | Input | Output |
|-----------|---------------|-------------------|-------|--------|
| `api/routes.py` | HTTP request handling, validation | `prediction_engine`, `stats_service` | HTTP requests | JSON responses |
| `schemas/` | Data shape contracts (Pydantic) | Used by `routes`, `services` | -- | Type validation |
| `services/data_loader.py` | Load JSON, filter by machine, cache in memory | `strategies/*`, `stats_service` | `new_res.json` path | Filtered draw records |
| `services/prediction_engine.py` | Orchestrate all 5 strategies, collect 25 games | `strategies/*`, `data_loader` | Machine ID | `PredictionResponse` |
| `services/stats_service.py` | Compute dashboard statistics | `data_loader` | Machine ID | Stats object |
| `strategies/base.py` | ABC defining strategy interface | Implemented by concrete strategies | -- | Contract only |
| `strategies/frequency.py` | Number frequency analysis + time decay | `data_loader`, `utils/decay` | Filtered draws | 5 game sets |
| `strategies/pattern.py` | Pair frequency, consecutive patterns, trailing digits | `data_loader`, `utils/decay` | Filtered draws | 5 game sets |
| `strategies/range.py` | Range bucket distribution (1-9, 10-19, etc.) | `data_loader`, `utils/decay` | Filtered draws | 5 game sets |
| `strategies/balance.py` | Odd/even and high/low ratio balancing | `data_loader`, `utils/decay` | Filtered draws | 5 game sets |
| `strategies/composite.py` | Weighted blend of all 4 strategies' scores | All other strategies | Filtered draws | 5 game sets |
| `utils/decay.py` | Exponential time decay weight computation | Used by all strategies | Round number, latest round | Weight float |
| `utils/validators.py` | Validate lotto number sets (6 unique, 1-45) | Used by strategies | Number set | Bool/raise |

### Frontend Components

| Component | Responsibility | Communicates With | Props In | Renders |
|-----------|---------------|-------------------|----------|---------|
| `App.jsx` | Layout shell, top-level state | All children | -- | Page structure |
| `MachineSelector.jsx` | Machine selection UI | Parent via callback | `selected`, `onSelect` | 3 toggle buttons |
| `PredictButton.jsx` | Trigger prediction request | Parent via callback | `onClick`, `loading` | Button with loading state |
| `PredictionResults.jsx` | Container for all 5 strategy results | `StrategySection` | `predictions[]` | 5 strategy sections |
| `StrategySection.jsx` | One strategy header + 5 game cards | `GameCard` | `strategy`, `games[]` | Strategy name + cards |
| `GameCard.jsx` | Single game display (6 balls) | `NumberBall` | `numbers[]`, `gameIndex` | Row of number balls |
| `NumberBall.jsx` | Styled individual number | -- | `number` | Colored circle |
| `DashboardPanel.jsx` | Stats dashboard container | Chart components | `stats` | Charts + tables |
| `FrequencyChart.jsx` | Bar chart of number frequencies | -- | `frequencies[]` | Bar chart |
| `StatsOverview.jsx` | Summary statistics cards | -- | `stats` | Stat cards |
| `PatternDisplay.jsx` | Common pairs, patterns | -- | `patterns` | Pattern list/table |

### Boundary Rules

1. **Frontend never computes predictions.** All analysis logic lives in Python. The frontend is purely display + interaction.
2. **Strategies never call the API layer.** They receive filtered data and return number sets. No HTTP awareness.
3. **Data loader is the single source of truth.** All data access goes through `data_loader.py`. No strategy reads JSON directly.
4. **Pydantic schemas are the API contract.** Both request validation and response serialization use typed schemas. The frontend mirrors these shapes.

## Data Flow

### Primary Flow: Prediction Generation

```
User clicks "번호 예측"
        │
        ▼
┌─────────────────┐     POST /api/predict          ┌──────────────────┐
│  React Frontend  │ ──────────────────────────────▶│  FastAPI Backend  │
│  (usePrediction) │     { machine: "1호기" }       │  (routes.py)      │
└─────────────────┘                                 └────────┬─────────┘
        ▲                                                    │
        │                                                    ▼
        │                                           ┌──────────────────┐
        │                                           │ prediction_engine│
        │                                           │  .predict()      │
        │                                           └────────┬─────────┘
        │                                                    │
        │                                    ┌───────────────┼───────────────┐
        │                                    ▼               ▼               ▼
        │                              ┌──────────┐   ┌──────────┐   ┌──────────┐
        │                              │ Strategy1 │   │ Strategy2 │   │ ...      │
        │                              │ .generate │   │ .generate │   │ Strategy5│
        │                              │ (5 games) │   │ (5 games) │   │ (5 games)│
        │                              └─────┬─────┘   └─────┬─────┘   └─────┬────┘
        │                                    │               │               │
        │                                    ▼               ▼               ▼
        │                              ┌─────────────────────────────────────────┐
        │                              │         data_loader (cached)            │
        │                              │   new_res.json → filter by machine     │
        │                              │   → apply time decay weights           │
        │                              └────────────────────────────────────────┘
        │
        │      Response: PredictionResponse
        │      { machine, strategies: [
        │          { name, description, games: [
        │              { numbers: [6 ints], metadata }
        │          ] } x5
        │      ] }
        └──────────────────────────────────────────────────────────────────────
```

### Secondary Flow: Statistics Dashboard

```
User selects machine (or page load)
        │
        ▼
┌─────────────────┐     GET /api/stats/{machine}    ┌──────────────────┐
│  React Frontend  │ ──────────────────────────────▶│  stats_service    │
│  (useStats)      │                                │  .get_stats()     │
└─────────────────┘                                 └────────┬─────────┘
        ▲                                                    │
        │                                                    ▼
        │                                           ┌──────────────────┐
        │                                           │  data_loader     │
        │                                           │  (cached filter) │
        │                                           └──────────────────┘
        │
        │      Response: MachineStats
        │      { machine, total_draws, number_frequencies,
        │        common_pairs, odd_even_distribution,
        │        high_low_distribution, range_distribution,
        │        ac_distribution, recent_trend }
        └──────────────────────────────────────────────────────────
```

### Data Shape: `new_res.json` Record

```json
{
  "회차": 800,
  "호기": "2호기",
  "1등_당첨번호": [1, 4, 10, 12, 28, 45],
  "홀짝_비율": "2:4",
  "고저_비율": "2:4",
  "AC값": 5,
  "끝수합": 20,
  "총합": 100
}
```

All 417 records follow this shape. The data loader reads them once at startup, then caches machine-filtered views.

## API Design

### Endpoints

```
POST /api/predict
  Request:  { "machine": "1호기" }
  Response: PredictionResponse (see below)

GET  /api/stats/{machine}
  Response: MachineStats (see below)

GET  /api/health
  Response: { "status": "ok", "data_loaded": true, "total_records": 417 }
```

### Pydantic Schemas

```python
# request.py
class PredictionRequest(BaseModel):
    machine: Literal["1호기", "2호기", "3호기"]

# response.py
class GameResult(BaseModel):
    numbers: list[int]          # 6 sorted numbers, 1-45
    metadata: dict | None = None  # Optional: confidence scores, source weights

class StrategyResult(BaseModel):
    name: str                   # e.g. "빈도 전략"
    description: str            # Korean description of approach
    games: list[GameResult]     # Exactly 5 games

class PredictionResponse(BaseModel):
    machine: str
    generated_at: datetime
    strategies: list[StrategyResult]  # Exactly 5 strategies

class MachineStats(BaseModel):
    machine: str
    total_draws: int
    number_frequencies: dict[int, float]   # number -> weighted frequency
    common_pairs: list[tuple[int, int]]
    odd_even_distribution: dict[str, int]  # "2:4" -> count
    high_low_distribution: dict[str, int]
    range_distribution: dict[str, int]     # "1-9" -> count
    ac_distribution: dict[int, int]        # AC value -> count
    recent_draws: list[dict]               # Last 10 draws for trend display
```

## Patterns to Follow

### Pattern 1: Strategy Pattern for Analysis Engines

**What:** Each of the 5 prediction strategies is an independent class implementing a common ABC interface. The prediction engine iterates over all registered strategies without knowing their internals.

**When:** Always -- this is the core architectural pattern for the analysis engine.

**Why:** Adding or modifying a strategy requires zero changes to the orchestrator, API, or frontend. Open/Closed principle.

```python
# strategies/base.py
from abc import ABC, abstractmethod
from typing import List

class PredictionStrategy(ABC):
    """Base class for all prediction strategies."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Korean display name for the strategy."""
        ...

    @property
    @abstractmethod
    def description(self) -> str:
        """Korean description of the approach."""
        ...

    @abstractmethod
    def generate(self, draws: list[dict], weights: list[float]) -> list[list[int]]:
        """
        Generate 5 game sets from weighted historical draws.

        Args:
            draws: Filtered draw records for the selected machine,
                   ordered from oldest to newest.
            weights: Parallel array of time-decay weights (same length as draws).
                     weights[-1] is highest (most recent draw).

        Returns:
            List of 5 games, each game is a sorted list of 6 integers (1-45).
        """
        ...
```

```python
# services/prediction_engine.py
class PredictionEngine:
    def __init__(self, strategies: list[PredictionStrategy], data_loader: DataLoader):
        self.strategies = strategies
        self.data_loader = data_loader

    def predict(self, machine: str) -> PredictionResponse:
        draws = self.data_loader.get_draws_for_machine(machine)
        weights = compute_decay_weights(len(draws))

        results = []
        for strategy in self.strategies:
            games = strategy.generate(draws, weights)
            # Validate each game
            for game in games:
                validate_lotto_numbers(game)
            results.append(StrategyResult(
                name=strategy.name,
                description=strategy.description,
                games=[GameResult(numbers=g) for g in games]
            ))

        return PredictionResponse(
            machine=machine,
            generated_at=datetime.now(),
            strategies=results
        )
```

### Pattern 2: Exponential Time Decay Weighting

**What:** Recent draws receive exponentially higher weight than older draws. Implemented as a standalone utility function that all strategies consume.

**When:** Applied to every strategy's analysis. The weight array is computed once per prediction request and passed to all strategies.

**Why:** The project requirement specifies time-decay weighting to reflect that recent patterns are more predictive. Using exponential decay (not linear) gives meaningful differentiation between recent and old draws without completely ignoring history.

```python
# utils/decay.py
import numpy as np

def compute_decay_weights(n: int, half_life: int = 50) -> list[float]:
    """
    Compute exponential decay weights for n draws.

    The most recent draw (index n-1) gets the highest weight.
    Weight halves every `half_life` draws into the past.

    Args:
        n: Number of draws.
        half_life: Number of draws for weight to halve.
                   50 means a draw from 50 rounds ago has half
                   the weight of the most recent draw.

    Returns:
        List of n floats, normalized so they sum to 1.0.
        Index 0 = oldest draw (lowest weight).
        Index n-1 = newest draw (highest weight).
    """
    decay_rate = np.log(2) / half_life
    positions = np.arange(n)  # 0, 1, 2, ..., n-1
    raw_weights = np.exp(decay_rate * positions)
    normalized = raw_weights / raw_weights.sum()
    return normalized.tolist()
```

**half_life=50 rationale:** With ~140 draws per machine, a half_life of 50 means:
- Most recent draw: weight ~1.0 (relative)
- 50 draws ago: weight ~0.5 (relative)
- 100 draws ago: weight ~0.25 (relative)
- This balances recency bias with sufficient historical coverage.

The half_life parameter should be configurable and is a key decision that the methodology research phase should finalize.

### Pattern 3: Data Loader with In-Memory Cache

**What:** Load JSON once at application startup, pre-compute per-machine filtered views, and serve from memory.

**When:** At FastAPI lifespan startup event. The data never changes at runtime (static JSON file).

**Why:** 417 records is small enough to hold entirely in memory. Pre-filtering by machine avoids repeated work on every request.

```python
# services/data_loader.py
import json
from functools import lru_cache

class DataLoader:
    def __init__(self, data_path: str):
        with open(data_path, 'r', encoding='utf-8') as f:
            raw = json.load(f)
        self.metadata = raw["metadata"]
        self.all_draws = raw["lottery_data"]
        # Pre-filter by machine
        self._by_machine: dict[str, list[dict]] = {}
        for machine in ["1호기", "2호기", "3호기"]:
            self._by_machine[machine] = [
                d for d in self.all_draws if d["호기"] == machine
            ]

    def get_draws_for_machine(self, machine: str) -> list[dict]:
        """Return draws filtered for the given machine, ordered by round number."""
        return sorted(self._by_machine[machine], key=lambda d: d["회차"])

    def get_all_draws(self) -> list[dict]:
        return self.all_draws
```

### Pattern 4: Custom Hooks for API State Management (Frontend)

**What:** React custom hooks encapsulate API calls, loading state, and error handling. Components receive clean data.

**When:** For every API interaction (predictions, stats).

**Why:** Separates data-fetching concerns from display concerns. Components stay purely presentational.

```javascript
// hooks/usePrediction.js
import { useState, useCallback } from 'react';
import { fetchPredictions } from '../api/client';

export function usePrediction() {
  const [predictions, setPredictions] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const predict = useCallback(async (machine) => {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchPredictions(machine);
      setPredictions(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  return { predictions, loading, error, predict };
}
```

### Pattern 5: Component Composition for 5x5 Grid

**What:** The 25-game display is structured as a two-level composition: 5 StrategySections each containing 5 GameCards.

**When:** Rendering prediction results.

**Why:** Matches the domain model (5 strategies x 5 games). Each level handles its own concern.

```
PredictionResults
├── StrategySection (빈도 전략)
│   ├── GameCard (Game 1: 6 balls)
│   ├── GameCard (Game 2: 6 balls)
│   ├── GameCard (Game 3: 6 balls)
│   ├── GameCard (Game 4: 6 balls)
│   └── GameCard (Game 5: 6 balls)
├── StrategySection (패턴 전략)
│   └── ... 5 GameCards
├── StrategySection (구간 전략)
│   └── ... 5 GameCards
├── StrategySection (홀짝밸런스 전략)
│   └── ... 5 GameCards
└── StrategySection (종합 전략)
    └── ... 5 GameCards
```

## Anti-Patterns to Avoid

### Anti-Pattern 1: Analysis Logic in the Frontend
**What:** Computing predictions or statistics in JavaScript.
**Why bad:** Python has numpy/pandas for numerical work. Duplicating analysis logic across two languages guarantees drift. The frontend should never import statistical functions.
**Instead:** All computation in Python. Frontend is display-only.

### Anti-Pattern 2: Monolithic Strategy Function
**What:** One giant function with if/elif branches for each strategy.
**Why bad:** Adding or modifying a strategy requires editing a massive function. Untestable in isolation. Violates Open/Closed and Single Responsibility.
**Instead:** Strategy Pattern with ABC base class. Each strategy is independently testable.

### Anti-Pattern 3: Direct JSON File Access from Strategies
**What:** Each strategy opens and parses `new_res.json` independently.
**Why bad:** Repeated I/O, no caching, no single point of change for data location or format.
**Instead:** DataLoader singleton loaded at startup, passed via dependency injection.

### Anti-Pattern 4: Hardcoded Decay Parameters
**What:** Embedding decay half-life or alpha directly in strategy code.
**Why bad:** The methodology research phase may change these values. Updating requires editing multiple strategy files.
**Instead:** Decay parameters in `config.py`. Weights computed once per request and passed to strategies.

### Anti-Pattern 5: Fetching Stats on Every Render
**What:** Dashboard re-fetching statistics every time a component re-renders.
**Why bad:** Data is static (does not change between page loads). Wastes network calls.
**Instead:** Fetch stats once when machine is selected. Use state to cache results.

### Anti-Pattern 6: Over-Engineering State Management
**What:** Adding Redux, Zustand, or Context for this scale of app.
**Why bad:** This app has exactly two pieces of state: prediction results and stats data. No shared state between unrelated components. A global store adds complexity for zero benefit.
**Instead:** Component-level useState + custom hooks. If two components need the same data, lift state to their common parent (App.jsx).

## Scalability Considerations

This is a localhost-only application with static data. Scalability concerns are minimal, but good patterns still matter for maintainability.

| Concern | Current (417 records) | If Data Grows (1000+ records) | If Multi-User |
|---------|----------------------|-------------------------------|---------------|
| Data Loading | In-memory, instant | Still fine up to ~50K records | Add read-only caching |
| Prediction Compute | <100ms per request | Still <500ms with numpy | Background job queue |
| Frontend Rendering | 25 cards, trivial | Same 25 cards (output is fixed) | No change |
| API Concurrency | Single user, no concern | Single user, no concern | Add connection pooling |

## Suggested Build Order

Build order follows dependency chains. Each layer depends only on layers above it.

```
Phase 1: Foundation (no dependencies)
├── 1a. Backend: data_loader.py + config.py + new_res.json parsing
├── 1b. Backend: utils/decay.py + utils/validators.py
├── 1c. Backend: schemas/ (Pydantic models)
└── 1d. Frontend: project scaffold (Vite + React) + api/client.js stub

Phase 2: Analysis Engine (depends on Phase 1a, 1b)
├── 2a. strategies/base.py (ABC interface)
├── 2b. strategies/frequency.py (simplest strategy, proves the pattern)
├── 2c. services/prediction_engine.py (orchestrator with just frequency)
└── 2d. Backend: api/routes.py POST /predict (wired to engine)
    → At this point: one strategy works end-to-end through the API

Phase 3: Vertical Slice (depends on Phase 1d, 2d)
├── 3a. Frontend: MachineSelector + PredictButton
├── 3b. Frontend: hooks/usePrediction.js
├── 3c. Frontend: PredictionResults + StrategySection + GameCard + NumberBall
└── 3d. Integration: full click-to-results flow with 1 strategy
    → At this point: user can select machine, click predict, see 1 strategy's 5 games

Phase 4: Remaining Strategies (depends on Phase 2a, 2b pattern)
├── 4a. strategies/pattern.py
├── 4b. strategies/range.py
├── 4c. strategies/balance.py
└── 4d. strategies/composite.py (depends on 4a-4c)
    → At this point: full 25-game prediction working

Phase 5: Dashboard (depends on Phase 1a)
├── 5a. Backend: services/stats_service.py
├── 5b. Backend: GET /api/stats/{machine} endpoint
├── 5c. Frontend: hooks/useStats.js
└── 5d. Frontend: DashboardPanel + charts (FrequencyChart, StatsOverview, PatternDisplay)
    → At this point: full application complete

Phase 6: Polish
├── 6a. UI styling, responsive layout, number ball colors
├── 6b. Loading states, error handling, edge cases
└── 6c. Strategy description text, methodology documentation
```

### Build Order Rationale

1. **Data first:** Everything depends on being able to load and filter lottery data. Build this before anything else.
2. **One strategy end-to-end before all strategies:** Prove the Strategy Pattern works with one concrete implementation (frequency, the simplest). This validates the ABC interface, the engine orchestrator, and the API contract before investing in 4 more strategies.
3. **Vertical slice before horizontal expansion:** Get one complete user flow (select machine -> click predict -> see results) working before adding more strategies or the dashboard. This catches integration issues early.
4. **Dashboard last:** It is independent of prediction flow and uses the same data loader. Adding it after predictions are working avoids scope creep in the core flow.
5. **Polish last:** Styling and error handling are important but should not block functional development.

### Key Dependency Chain

```
new_res.json
    └── data_loader.py
            ├── decay.py
            │       └── strategies/* (all 5)
            │               └── prediction_engine.py
            │                       └── routes.py (POST /predict)
            │                               └── usePrediction.js
            │                                       └── PredictionResults.jsx
            └── stats_service.py
                    └── routes.py (GET /stats/{machine})
                            └── useStats.js
                                    └── DashboardPanel.jsx
```

Two independent branches after `data_loader`: predictions and stats. They can be built in parallel after Phase 3.

## Technology Rationale

| Choice | Why | Alternative Considered |
|--------|-----|----------------------|
| FastAPI over Flask | Auto-generated OpenAPI docs, native Pydantic integration, async-ready, type hints | Flask works fine but requires manual schema validation |
| Pydantic schemas | Type-safe API contracts, auto-serialization, self-documenting | Marshmallow (more verbose, less integrated with FastAPI) |
| numpy for decay computation | Vectorized operations on arrays, standard for numerical Python | Pure Python math (slower for larger arrays, less readable) |
| No database | 417 static records, read-only, fits in memory | SQLite (unnecessary overhead for read-only static data) |
| No global state manager (React) | Only 2 data sources, no cross-cutting state | Redux/Zustand (over-engineering for this scope) |
| CSS custom properties over CSS-in-JS | Simpler, no runtime cost, good for theming number ball colors | styled-components (adds dependency for minimal benefit) |
| Vite over CRA | Faster dev server, native ESM, actively maintained | CRA is deprecated as of 2023 |

## Sources

- [FastAPI Official Template](https://fastapi.tiangolo.com/project-generation/) -- Full stack project structure reference
- [FastAPI Project Structure Guide](https://www.zestminds.com/blog/fastapi-project-structure/) -- Production architecture patterns
- [Strategy Pattern in Python (Refactoring Guru)](https://refactoring.guru/design-patterns/strategy/python/example) -- Strategy pattern implementation
- [Strategy Pattern in Python (Auth0)](https://auth0.com/blog/strategy-design-pattern-in-python/) -- ABC-based strategy approach
- [FastAPI Nested Pydantic Models](https://fastapi.tiangolo.com/tutorial/body-nested-models/) -- Schema design for complex responses
- [Pandas EWMA Documentation](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.ewm.html) -- Exponential decay reference
- [FastAPI + React Best Practices](https://github.com/zhanymkanov/fastapi-best-practices) -- Project organization patterns
- [Python ABC Module](https://docs.python.org/3/library/abc.html) -- Abstract base class implementation
