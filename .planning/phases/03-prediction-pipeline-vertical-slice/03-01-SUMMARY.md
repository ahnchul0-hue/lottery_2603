---
phase: 03-prediction-pipeline-vertical-slice
plan: 01
subsystem: prediction
tags: [strategy-pattern, abc, frequency-analysis, weighted-random, pydantic, tdd]

# Dependency graph
requires:
  - phase: 02-decay-engine-and-weighting
    provides: "DecayEngine with compute_weighted_frequencies()"
provides:
  - "PredictionStrategy ABC with name, display_name, generate()"
  - "FrequencyStrategy implementation with weighted selection and diversity"
  - "Strategy registry STRATEGY_MAP with get_strategy() lookup"
  - "PredictRequest and PredictResponse Pydantic models"
affects: [03-02, 04-full-prediction-engine, 05-frontend-prediction-ui]

# Tech tracking
tech-stack:
  added: []
  patterns: [strategy-pattern-abc, weighted-random-selection, diversity-constraint]

key-files:
  created:
    - backend/app/strategies/base.py
    - backend/app/strategies/frequency.py
    - backend/app/strategies/__init__.py
    - backend/tests/test_frequency_strategy.py
  modified:
    - backend/app/schemas/lottery.py

key-decisions:
  - "Pure Python random.choices for weighted selection -- no numpy needed for 45-number population"
  - "MIN_WEIGHT_FLOOR=0.001 prevents zero-probability numbers while preserving weight ratios"
  - "MAX_OVERLAP=3 with 100 retry attempts for diversity, fallback to best candidate"

patterns-established:
  - "Strategy Pattern: PredictionStrategy ABC with name/display_name/generate() contract"
  - "Strategy Registry: STRATEGY_MAP dict + get_strategy() for lookup by name"
  - "Diversity Constraint: Retry loop with best-candidate fallback for game set generation"

requirements-completed: [PRED-01, PRED-06]

# Metrics
duration: 3min
completed: 2026-03-27
---

# Phase 03 Plan 01: Strategy ABC and FrequencyStrategy Summary

**PredictionStrategy ABC with FrequencyStrategy using weighted random.choices selection and diversity constraint (max 3 shared numbers between any game pair)**

## Performance

- **Duration:** 3 min
- **Started:** 2026-03-27T00:42:33Z
- **Completed:** 2026-03-27T00:45:31Z
- **Tasks:** 1 (TDD: RED-GREEN-REFACTOR)
- **Files modified:** 5

## Accomplishments
- PredictionStrategy ABC defines extensible interface for all 5 strategies (Phase 4 ready)
- FrequencyStrategy generates 5 diverse game sets from DecayEngine weighted frequencies
- Strategy registry with STRATEGY_MAP and get_strategy() for clean lookup by name
- PredictRequest/PredictResponse Pydantic schemas ready for API endpoint integration
- 11 unit tests covering game structure, diversity, weighted bias, properties, and registry

## Task Commits

Each task was committed atomically (TDD cycle):

1. **RED: Failing tests** - `2a88502` (test)
2. **GREEN: Implementation** - `241a99d` (feat)
3. **REFACTOR: No changes needed** - skipped (code already clean)

**Plan metadata:** pending (docs: complete plan)

_Note: TDD task with 2 commits (test -> feat). Refactor phase was a no-op._

## Files Created/Modified
- `backend/app/strategies/base.py` - PredictionStrategy ABC with abstract name, display_name, generate()
- `backend/app/strategies/frequency.py` - FrequencyStrategy with weighted selection and diversity constraint
- `backend/app/strategies/__init__.py` - Strategy registry STRATEGY_MAP and get_strategy()
- `backend/app/schemas/lottery.py` - Added PredictRequest and PredictResponse models
- `backend/tests/test_frequency_strategy.py` - 11 tests for strategy behavior, diversity, bias, registry

## Decisions Made
- Used pure Python `random.choices` for weighted selection -- numpy unnecessary for 45-number population
- Set `MIN_WEIGHT_FLOOR=0.001` to prevent zero-probability numbers while maintaining extreme weight ratios
- Diversity constraint `MAX_OVERLAP=3` with 100 retry attempts and best-candidate fallback ensures reliable diverse output
- Strategy `display_name` uses Korean ("빈도 전략") for UI consistency with the Korean-language application

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness
- Strategy ABC is ready for 4 additional strategies in Phase 4 (pattern, range, balance, composite)
- PredictRequest/PredictResponse schemas ready for API endpoint in Plan 03-02
- Strategy registry supports dynamic expansion via STRATEGY_MAP
- Full test suite green (35 tests, 0 failures)

## Self-Check: PASSED

- All 5 files verified present on disk
- Commit 2a88502 (RED) verified in git log
- Commit 241a99d (GREEN) verified in git log
- 35/35 tests pass in full suite

---
*Phase: 03-prediction-pipeline-vertical-slice*
*Completed: 2026-03-27*
