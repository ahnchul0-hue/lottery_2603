---
phase: 09-integration-hardening
plan: 01
subsystem: api, testing
tags: [fastapi, pytest, httpx, error-handling, korean-i18n, integration-tests]

requires:
  - phase: 07-history-reflection
    provides: Reflect endpoint and ReflectRequest schema
  - phase: 06-statistics-dashboard
    provides: Heatmap endpoint and statistics service

provides:
  - Hardened error handling with Korean messages across all 5 API endpoints
  - Comprehensive integration test suite (27 test cases) for full API surface
  - Full user flow test validating end-to-end API interaction

affects: [09-02, frontend-error-handling]

tech-stack:
  added: []
  patterns: [per-endpoint Korean error messages, integration test with parametrize]

key-files:
  created:
    - backend/tests/test_integration.py
  modified:
    - backend/app/api/routes.py

key-decisions:
  - "Per-endpoint Korean error messages instead of global exception handler for explicit control"
  - "ReflectRequest.machine remains str (not Literal) since it passes through to AI prompt"
  - "Direct settings mutation for API key test instead of monkeypatch for simplicity"

patterns-established:
  - "Korean error messages: '유효하지 않은 호기입니다', '유효하지 않은 전략입니다', 'API 키 미설정'"
  - "Integration test structure: per-section grouping by endpoint with Korean docstrings"

requirements-completed: []

duration: 3min
completed: 2026-03-27
---

# Phase 09 Plan 01: Backend Error Hardening + Integration Tests Summary

**Korean error messages on all 5 endpoints plus 27-case integration test suite covering health/data/predict/heatmap/reflect happy and error paths**

## Performance

- **Duration:** 3 min
- **Started:** 2026-03-27T08:15:01Z
- **Completed:** 2026-03-27T08:18:01Z
- **Tasks:** 2
- **Files modified:** 2

## Accomplishments
- Replaced all English error messages with Korean equivalents across routes.py (5 endpoints, 7 error paths)
- Created 21 test functions (27 test cases with parametrize) covering all 5 API endpoints
- Full user flow tests validate sequential health -> data -> predict -> heatmap interaction
- Zero regressions: all 147 tests pass (37 test_api.py + 27 test_integration.py + 83 other)

## Task Commits

Each task was committed atomically:

1. **Task 1: Harden backend error responses with Korean messages** - `713c68e` (feat)
2. **Task 2: Create comprehensive integration test suite** - `68dd6ea` (test)

## Files Created/Modified
- `backend/app/api/routes.py` - Korean error messages for all 5 endpoints (400/422/502/503 responses)
- `backend/tests/test_integration.py` - 27-case integration test suite with Korean docstrings

## Decisions Made
- Per-endpoint Korean error messages instead of global exception handler -- gives explicit control over each error path
- ReflectRequest.machine stays as `str` type (not Literal-gated) since it passes through to AI prompt
- Used direct settings mutation for API key test rather than monkeypatch -- simpler, equally effective with try/finally cleanup

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered
- Circular import prevents standalone `from app.api.routes import router` verification -- used AST parse check instead. This is a known pattern in the project (circular import resolves at runtime through uvicorn/pytest).

## Known Stubs

None - no stubs or placeholder data in this plan's changes.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness
- Backend API surface fully tested and hardened with user-friendly Korean error messages
- Ready for 09-02 (frontend race condition handling) which depends on backend error responses
- All 147 backend tests pass cleanly

---
*Phase: 09-integration-hardening*
*Completed: 2026-03-27*
