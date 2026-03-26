---
phase: 01-foundation-data-layer
plan: 01
subsystem: api
tags: [fastapi, pydantic, uv, python, data-loading, validation, cors]

# Dependency graph
requires:
  - phase: none
    provides: greenfield project
provides:
  - FastAPI backend running on localhost:8000
  - DataLoader class loading/validating 417 lottery records from new_res.json
  - Pydantic LotteryDraw model with field validators (range, count, sort, uniqueness)
  - GET /api/health and GET /api/data?machine= endpoints
  - CORS configured for http://localhost:5173
  - Per-machine pre-filtered data cache (1호기:134, 2호기:136, 3호기:147)
affects: [01-02-PLAN, 01-03-PLAN, 02-time-decay-engine, 03-vertical-slice]

# Tech tracking
tech-stack:
  added: [fastapi 0.135.2, pydantic 2.12.5, uvicorn 0.42.0, uv, pytest 9.0.2, pytest-asyncio 1.3.0, httpx 0.28.1, ruff 0.15.7]
  patterns: [asynccontextmanager lifespan, module-level data_store dict, sync def for CPU-bound endpoints, Pydantic field_validator]

key-files:
  created:
    - backend/app/main.py
    - backend/app/config.py
    - backend/app/schemas/lottery.py
    - backend/app/services/data_loader.py
    - backend/app/api/routes.py
    - backend/tests/test_data_loader.py
    - backend/tests/test_api.py
    - backend/tests/conftest.py
    - backend/pyproject.toml
    - backend/data/new_res.json
  modified: []

key-decisions:
  - "Used asynccontextmanager lifespan pattern (not deprecated on_event) for data loading"
  - "Sync def for /api/data endpoint to prepare for future CPU-bound NumPy work"
  - "Pre-filter data by machine at startup into _by_machine dict for O(1) lookups"
  - "Manually invoke lifespan in test conftest.py for proper data initialization"

patterns-established:
  - "Lifespan pattern: asynccontextmanager loads data into module-level data_store dict"
  - "Validation pattern: Pydantic field_validator with clear error messages"
  - "Test pattern: httpx AsyncClient with ASGITransport + manual lifespan invocation"
  - "Route pattern: async for lightweight endpoints, sync for CPU-bound"

requirements-completed: [INFRA-01, DATA-01, DATA-02]

# Metrics
duration: 5min
completed: 2026-03-26
---

# Phase 01 Plan 01: Foundation Data Layer Summary

**FastAPI backend with uv project scaffolding, Pydantic-validated DataLoader for 417 lottery records, and machine-filtered REST API endpoints with 16 passing tests**

## Performance

- **Duration:** 5 min
- **Started:** 2026-03-26T13:13:48Z
- **Completed:** 2026-03-26T13:18:53Z
- **Tasks:** 2
- **Files modified:** 17

## Accomplishments
- Initialized uv Python project with FastAPI and Pydantic dependencies
- Created DataLoader that loads, validates, and pre-filters 417 lottery records by machine (1호기:134, 2호기:136, 3호기:147)
- Built Pydantic LotteryDraw model with comprehensive field validators (count, range, sort order, uniqueness)
- Wired FastAPI app with lifespan data loading, CORS for localhost:5173, health and data endpoints
- All 16 tests pass: 11 data loader unit tests + 5 API integration tests

## Task Commits

Each task was committed atomically:

1. **Task 1: Initialize backend project with uv and create data layer** - `17a47b4` (feat)
2. **Task 2: Create FastAPI app with lifespan, routes, CORS, and tests** - `59ad17b` (feat)

## Files Created/Modified
- `backend/pyproject.toml` - Project config with FastAPI, Pydantic, dev dependencies, pytest config
- `backend/app/main.py` - FastAPI app with asynccontextmanager lifespan and CORS
- `backend/app/config.py` - Settings class with DATA_PATH, CORS_ORIGINS, PORT
- `backend/app/schemas/lottery.py` - LotteryDraw, HealthResponse, MachineDataResponse Pydantic models
- `backend/app/services/data_loader.py` - DataLoader class with load_and_validate and machine filtering
- `backend/app/api/routes.py` - GET /api/health and GET /api/data endpoints
- `backend/data/new_res.json` - Copy of lottery data (417 records)
- `backend/tests/conftest.py` - Test fixtures with lifespan-aware AsyncClient
- `backend/tests/test_data_loader.py` - 11 unit tests for data loading and validation
- `backend/tests/test_api.py` - 5 integration tests for API endpoints and CORS
- `backend/.gitignore` - Python cache and venv exclusions

## Decisions Made
- Used asynccontextmanager lifespan (not deprecated on_event) per locked decision D-05
- Used sync def for /api/data endpoint per Pitfall #12 (future CPU-bound NumPy work)
- Manually invoked lifespan in conftest.py since httpx ASGITransport does not auto-trigger FastAPI lifespan events
- Added .gitignore for __pycache__ directories generated during test runs

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Fixed test conftest.py lifespan invocation**
- **Found during:** Task 2 (test execution)
- **Issue:** httpx AsyncClient with ASGITransport does not automatically trigger FastAPI lifespan events, causing data_store to be empty and health check to return data_loaded=False
- **Fix:** Wrapped the AsyncClient fixture in `async with lifespan(app):` to manually invoke the lifespan context manager before tests
- **Files modified:** backend/tests/conftest.py
- **Verification:** All 16 tests pass
- **Committed in:** 59ad17b (Task 2 commit)

**2. [Rule 2 - Missing Critical] Added backend .gitignore**
- **Found during:** Task 2 (commit staging)
- **Issue:** __pycache__ directories created during test runs were showing as untracked files
- **Fix:** Created backend/.gitignore with standard Python exclusions
- **Files modified:** backend/.gitignore
- **Verification:** git status no longer shows __pycache__ directories
- **Committed in:** 59ad17b (Task 2 commit)

---

**Total deviations:** 2 auto-fixed (1 blocking, 1 missing critical)
**Impact on plan:** Both fixes necessary for correct test execution and clean repository. No scope creep.

## Issues Encountered
None beyond the auto-fixed deviations above.

## User Setup Required
None - no external service configuration required.

## Known Stubs
None - all data sources are wired and functional.

## Next Phase Readiness
- Backend foundation complete: FastAPI running, data loaded and validated, endpoints responding
- Ready for Plan 01-02 (React frontend scaffolding) and Plan 01-03 (frontend-backend integration)
- DataLoader and machine-filtered data available for Phase 02 (time decay engine)

---
*Phase: 01-foundation-data-layer*
*Completed: 2026-03-26*
