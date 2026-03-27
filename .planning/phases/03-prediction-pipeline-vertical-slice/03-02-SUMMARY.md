---
phase: 03-prediction-pipeline-vertical-slice
plan: 02
subsystem: api
tags: [fastapi, endpoint, integration-test, vertical-slice, decay-engine, frequency-strategy]

# Dependency graph
requires:
  - phase: 03-prediction-pipeline-vertical-slice
    plan: 01
    provides: "FrequencyStrategy, PredictRequest/PredictResponse schemas, strategy registry"
  - phase: 02-decay-engine-and-weighting
    provides: "DecayEngine with compute_weighted_frequencies()"
provides:
  - "POST /api/predict endpoint returning 5 diverse game sets"
  - "DecayEngine initialized at startup in data_store"
  - "7 integration tests proving full vertical slice"
affects: [04-full-prediction-engine, 05-frontend-prediction-ui]

# Tech tracking
tech-stack:
  added: []
  patterns: [startup-singleton-in-data-store, sync-def-for-cpu-bound-endpoints]

key-files:
  created: []
  modified:
    - backend/app/main.py
    - backend/app/api/routes.py
    - backend/tests/test_api.py

key-decisions:
  - "DecayEngine singleton in data_store at startup -- avoids per-request instantiation"
  - "Sync def for predict endpoint -- CPU-bound random sampling, consistent with existing get_machine_data pattern"

patterns-established:
  - "Startup singleton: Stateless services initialized once in lifespan and stored in data_store"
  - "Error handling chain: loader check (503) -> machine validation (400) -> strategy lookup (400) -> engine check (503)"

requirements-completed: [PRED-01, PRED-06]

# Metrics
duration: 2min
completed: 2026-03-27
---

# Phase 03 Plan 02: API Predict Endpoint Summary

**POST /api/predict endpoint wiring DecayEngine + FrequencyStrategy into full vertical slice with 7 integration tests proving end-to-end pipeline**

## Performance

- **Duration:** 2 min
- **Started:** 2026-03-27T00:48:05Z
- **Completed:** 2026-03-27T00:49:58Z
- **Tasks:** 2
- **Files modified:** 3

## Accomplishments
- DecayEngine initialized once at startup and stored in data_store for all request handlers
- POST /api/predict endpoint accepts machine + strategy, returns 5 diverse game sets
- Complete vertical slice works: HTTP request -> data lookup -> decay weighting -> strategy execution -> valid predictions
- 7 new integration tests covering success, valid numbers, diversity, all machines, and error cases
- Full backend test suite green (42 tests, 0 failures)

## Task Commits

Each task was committed atomically:

1. **Task 1: Add DecayEngine to data_store lifespan** - `6d03163` (feat)
2. **Task 2: POST /api/predict endpoint + integration tests** - `3938156` (feat)

**Plan metadata:** pending (docs: complete plan)

## Files Created/Modified
- `backend/app/main.py` - Added DecayEngine import and initialization in lifespan
- `backend/app/api/routes.py` - Added POST /api/predict endpoint with full pipeline
- `backend/tests/test_api.py` - 7 new integration tests for predict endpoint

## Decisions Made
- DecayEngine singleton in data_store at startup -- avoids per-request instantiation (stateless with fixed halflife)
- Sync def for predict endpoint -- CPU-bound random sampling, consistent with existing get_machine_data pattern

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness
- Vertical slice complete: HTTP request -> data -> decay -> strategy -> response
- Ready for Phase 04: additional strategies (pattern, range, balance, composite) just need to be added to STRATEGY_MAP
- Frontend can now call POST /api/predict with machine + strategy parameters
- API error handling covers invalid machines (422 via Pydantic), invalid strategies (422 via Pydantic), and service unavailable (503)

## Self-Check: PASSED

- All 3 files verified present on disk
- Commit 6d03163 (Task 1) verified in git log
- Commit 3938156 (Task 2) verified in git log
- 42/42 tests pass in full suite

---
*Phase: 03-prediction-pipeline-vertical-slice*
*Completed: 2026-03-27*
