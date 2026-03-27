---
phase: 06-statistics-dashboard
plan: 01
subsystem: api, ui
tags: [recharts, fastapi, pydantic, tanstack-query, react-hooks, statistics, heatmap]

# Dependency graph
requires:
  - phase: 01-foundation
    provides: "DataLoader, data_store, LotteryDraw schema, API routing, Tailwind theme"
  - phase: 05-machine-selection-prediction-ui
    provides: "fetchMachineData, useMachineInfo, StrategySection card pattern, lottery types"
provides:
  - "GET /api/statistics/heatmap endpoint returning 3x45 deviation data"
  - "useStatistics hook computing 8 stat categories from draws array"
  - "useHeatmapData TanStack Query hook for heatmap API"
  - "Statistics TypeScript types (NumberFrequency, StatisticsResult, etc.)"
  - "ChartCard wrapper component for dashboard chart sections"
  - "Recharts installed and available in frontend"
affects: [06-02-PLAN, 06-03-PLAN]

# Tech tracking
tech-stack:
  added: [recharts ^3.8.1]
  patterns: [frontend statistics computation via useMemo, heatmap deviation API]

key-files:
  created:
    - backend/app/schemas/statistics.py
    - backend/app/services/statistics_service.py
    - frontend/src/types/statistics.ts
    - frontend/src/hooks/useStatistics.ts
    - frontend/src/hooks/useHeatmapData.ts
    - frontend/src/components/dashboard/ChartCard.tsx
  modified:
    - backend/app/api/routes.py
    - frontend/src/lib/api.ts
    - frontend/package.json

key-decisions:
  - "Heatmap endpoint returns all 3 machines in one response (no machine parameter)"
  - "useStatistics uses cascaded useMemo for frequency -> hot/cold derivation"
  - "staleTime: Infinity for heatmap data (static dataset)"

patterns-established:
  - "Statistics computation in frontend via useMemo from cached draws array"
  - "ChartCard with bg-card rounded-xl border border-border p-4 and text-base font-bold title"
  - "Backend statistics service returns plain dicts, Pydantic validates at endpoint layer"

requirements-completed: [DASH-03, DASH-05]

# Metrics
duration: 3min
completed: 2026-03-27
---

# Phase 06 Plan 01: Statistics Dashboard Data Layer Summary

**Backend heatmap API with 3x45 deviation computation, Recharts install, useStatistics hook computing 8 stat categories via useMemo, and ChartCard wrapper**

## Performance

- **Duration:** 3 min
- **Started:** 2026-03-27T04:19:56Z
- **Completed:** 2026-03-27T04:22:26Z
- **Tasks:** 2
- **Files modified:** 9

## Accomplishments
- Backend heatmap endpoint computes per-machine per-number frequency deviation ((actual-expected)/expected) for all 3 machines (134/136/147 draws)
- Frontend useStatistics hook computes frequency, hot/cold, odd/even, high/low, zone, sum, and AC distributions from draws array
- Recharts ^3.8.1 installed and bundled (build passes, 230KB JS output)
- ChartCard wrapper provides consistent dashboard card styling for Plan 02/03 chart components

## Task Commits

Each task was committed atomically:

1. **Task 1: Backend heatmap API endpoint with Pydantic schemas and service** - `be88ea7` (feat)
2. **Task 2: Install Recharts, create statistics types, hooks, API function, and ChartCard** - `3073032` (feat)

## Files Created/Modified
- `backend/app/schemas/statistics.py` - HeatmapRow and HeatmapResponse Pydantic schemas
- `backend/app/services/statistics_service.py` - compute_heatmap_data service
- `backend/app/api/routes.py` - Added GET /api/statistics/heatmap endpoint
- `frontend/src/types/statistics.ts` - 8 TypeScript types for chart data shapes
- `frontend/src/hooks/useStatistics.ts` - Frontend statistics computation via cascaded useMemo
- `frontend/src/hooks/useHeatmapData.ts` - TanStack Query hook for heatmap API
- `frontend/src/components/dashboard/ChartCard.tsx` - Shared card wrapper for chart sections
- `frontend/src/lib/api.ts` - Added fetchHeatmapData function
- `frontend/package.json` - Added recharts ^3.8.1 dependency

## Decisions Made
- Heatmap endpoint returns all 3 machines in one response (no machine query parameter) because the heatmap displays all 3 rows simultaneously
- useStatistics uses cascaded useMemo: frequency depends on draws, hotNumbers/coldNumbers depend on frequency, other distributions depend on draws directly
- staleTime: Infinity for heatmap data since dataset is static (same pattern as useMachineInfo)
- Sum distribution uses 20-unit bins (21-40, 41-60, etc.) to match standard lottery sum analysis ranges

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered
None

## User Setup Required
None - no external service configuration required.

## Known Stubs
None - all data paths are wired to real computation (useStatistics from draws array, useHeatmapData from backend API).

## Next Phase Readiness
- All data hooks and types ready for Plan 02 (frequency bar chart, ratio charts, zone chart, sum/AC charts)
- Heatmap API ready for Plan 03 (heatmap grid component)
- ChartCard wrapper ready for consistent chart container styling
- Recharts available in node_modules for chart rendering

## Self-Check: PASSED

- All 9 files verified present on disk
- Both commit hashes (be88ea7, 3073032) verified in git log
- TypeScript compilation: zero errors
- Frontend build: passes (230KB JS output)
- Backend heatmap service: returns 3 rows with 45 deviations each

---
*Phase: 06-statistics-dashboard*
*Completed: 2026-03-27*
