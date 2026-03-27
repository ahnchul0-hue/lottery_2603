---
phase: 04-full-prediction-engine
plan: 01
subsystem: prediction
tags: [pattern-strategy, pair-frequency, consecutive-injection, ending-digit, decay-weights, tdd]

requires:
  - phase: 03-prediction-pipeline-vertical-slice
    provides: PredictionStrategy ABC, FrequencyStrategy reference, DecayEngine, strategy registry
provides:
  - PatternStrategy class with 3-signal pattern algorithm
  - Pattern strategy registered in STRATEGY_MAP
  - PredictRequest schema expanded to accept "pattern"
affects: [04-02, 04-03, 05-frontend-prediction-ui]

tech-stack:
  added: [itertools.combinations]
  patterns: [3-signal pattern generation, pair-frequency seeding, consecutive injection, ending-digit completion]

key-files:
  created:
    - backend/app/strategies/pattern.py
    - backend/tests/test_pattern_strategy.py
  modified:
    - backend/app/strategies/__init__.py
    - backend/app/schemas/lottery.py

key-decisions:
  - "Pure Python pair frequency with itertools.combinations -- no numpy needed for 15 pairs per draw"
  - "Dynamic consecutive injection probability (50% if rate > 0.5, else 30%) based on historical data"
  - "Ending-digit completion uses two-stage weighted selection: digit first, then number within digit"

patterns-established:
  - "3-signal pattern strategy: pair seeding -> consecutive injection -> ending-digit completion -> fallback fill"
  - "Decay weights computed inline (same formula as DecayEngine) to avoid coupling pair computation to DecayEngine instance"

requirements-completed: [PRED-02]

duration: 4min
completed: 2026-03-27
---

# Phase 04 Plan 01: PatternStrategy Summary

**PatternStrategy combining decay-weighted pair frequency, consecutive injection, and ending-digit completion for diverse 5-game generation**

## Performance

- **Duration:** 4 min
- **Started:** 2026-03-27T01:25:23Z
- **Completed:** 2026-03-27T01:29:00Z
- **Tasks:** 1 (TDD: RED -> GREEN -> REFACTOR)
- **Files modified:** 4

## Accomplishments
- Implemented PatternStrategy with 3-signal algorithm: pair seeding, consecutive injection, ending-digit completion
- All 10 unit tests pass covering structure, diversity, bias, and property assertions
- Full backend test suite green (66 tests)
- Strategy registered in STRATEGY_MAP and PredictRequest schema expanded

## Task Commits

Each task was committed atomically (TDD phases):

1. **Task 1 RED: Failing tests for PatternStrategy** - `a6ebadf` (test)
2. **Task 1 GREEN: Implement PatternStrategy** - `d5d6093` (feat)
3. **Task 1 REFACTOR: Register in strategy map and schema** - `3256c45` (refactor)

## Files Created/Modified
- `backend/app/strategies/pattern.py` - PatternStrategy with 3-signal pattern algorithm (pair frequency, consecutive injection, ending-digit completion)
- `backend/tests/test_pattern_strategy.py` - 10 unit tests covering structure, diversity, bias, and properties
- `backend/app/strategies/__init__.py` - Added PatternStrategy to STRATEGY_MAP
- `backend/app/schemas/lottery.py` - Expanded PredictRequest.strategy Literal to include "pattern"

## Decisions Made
- Used inline decay weight computation (same formula as DecayEngine: `0.5^((n-1-i)/halflife)`) rather than importing DecayEngine for pair weights. This avoids tight coupling while maintaining identical decay behavior.
- Two-stage ending-digit completion: first pick a digit weighted by historical digit frequency, then pick a specific number with that digit weighted by number frequency. This naturally reproduces observed digit distribution patterns.
- Consecutive injection probability is dynamic: 50% when historical consecutive rate > 50%, 30% otherwise. Per research data, 1호기=57.5% and 3호기=55.1% will get 50%, while 2호기=42.6% will get 30%.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 2 - Missing Critical] Registered PatternStrategy in strategy map and schema**
- **Found during:** Task 1 REFACTOR phase
- **Issue:** Plan specified creating the class but not registering it in STRATEGY_MAP or updating PredictRequest schema
- **Fix:** Added PatternStrategy to __init__.py STRATEGY_MAP and expanded PredictRequest.strategy Literal
- **Files modified:** backend/app/strategies/__init__.py, backend/app/schemas/lottery.py
- **Verification:** Full test suite passes (66 tests)
- **Committed in:** 3256c45

---

**Total deviations:** 1 auto-fixed (1 missing critical)
**Impact on plan:** Essential for strategy to be usable via the predict API. No scope creep.

## Issues Encountered
- Pre-existing `test_balance_strategy.py` imports non-existent `BalanceStrategy`, causing `pytest -x` collection failure. This is out of scope (future plan). Tests run successfully when ignoring that file. Logged to `deferred-items.md`.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- PatternStrategy is complete and registered, ready for use by frontend UI
- BalanceStrategy and CompositeStrategy remain for plans 04-02 and 04-03
- Full test suite is green (66 tests, ignoring pre-existing test_balance_strategy.py)

---
*Phase: 04-full-prediction-engine*
*Completed: 2026-03-27*
