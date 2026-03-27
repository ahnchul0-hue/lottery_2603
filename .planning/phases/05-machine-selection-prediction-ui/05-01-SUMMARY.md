---
phase: 05-machine-selection-prediction-ui
plan: 01
subsystem: ui
tags: [react, tanstack-query, typescript, tailwind, lotto-ball-color]

# Dependency graph
requires:
  - phase: 04-full-prediction-engine
    provides: POST /api/predict endpoint with 5 strategies, GET /api/data endpoint
provides:
  - TypeScript interfaces matching backend Pydantic schemas (LotteryDraw, MachineDataResponse, PredictResponse, MachineInfo)
  - API fetch layer (fetchMachineData, fetchPrediction) using native fetch
  - Lotto ball color mapping (D-06) and number formatting (D-07)
  - TanStack React Query provider with default staleTime and retry config
  - useMachineInfo hook (useQuery for GET /api/data)
  - usePrediction hook (useMutation with Promise.all over 5 strategies)
  - 4 presentational components (LottoBall, GameRow, StrategySection, MachineCard)
affects: [05-02-PLAN, 06-statistics-dashboard, 08-ui-ux-polish]

# Tech tracking
tech-stack:
  added: ["@tanstack/react-query ^5.x"]
  patterns: ["useQuery for read data", "useMutation for prediction trigger", "Promise.all for parallel API calls", "inline style for dynamic colors (Tailwind-purge safe)", "type exports for verbatimModuleSyntax compliance"]

key-files:
  created:
    - frontend/src/types/lottery.ts
    - frontend/src/lib/api.ts
    - frontend/src/lib/lottoBallColor.ts
    - frontend/src/hooks/useMachineInfo.ts
    - frontend/src/hooks/usePrediction.ts
    - frontend/src/components/LottoBall.tsx
    - frontend/src/components/GameRow.tsx
    - frontend/src/components/StrategySection.tsx
    - frontend/src/components/MachineCard.tsx
  modified:
    - frontend/package.json
    - frontend/src/main.tsx

key-decisions:
  - "Used `export type` for interfaces to comply with verbatimModuleSyntax=true and erasableSyntaxOnly=true"
  - "Used inline style={{ backgroundColor }} for LottoBall instead of Tailwind arbitrary values to avoid purge issues"
  - "Set staleTime=Infinity on useMachineInfo since machine data is static within a session"
  - "usePrediction uses Promise.all for parallel 5-strategy fetching (not sequential)"

patterns-established:
  - "Type-only imports via `import type` for all interface/type usage"
  - "Native fetch wrapper pattern with error handling and typed returns"
  - "useQuery with queryKey array for cache identity"
  - "useMutation for user-triggered POST operations"

requirements-completed: [MACH-01, MACH-02, MACH-03, UI-01]

# Metrics
duration: 4min
completed: 2026-03-27
---

# Phase 5 Plan 1: Machine Selection & Prediction UI Building Blocks Summary

**TanStack React Query integration with TypeScript types, API layer, custom hooks (useMachineInfo + usePrediction), and 4 presentational components (LottoBall, GameRow, StrategySection, MachineCard) with D-06 color coding and Korean UI text**

## Performance

- **Duration:** 4 min
- **Started:** 2026-03-27T02:02:40Z
- **Completed:** 2026-03-27T02:35:14Z
- **Tasks:** 2
- **Files modified:** 11

## Accomplishments
- Installed TanStack React Query and wrapped App in QueryClientProvider with sensible defaults
- Created TypeScript interfaces that exactly mirror backend Pydantic schemas (LotteryDraw, MachineDataResponse, PredictResponse) plus client-side MachineInfo convenience type
- Built API fetch layer using native fetch with proper error handling and Content-Type headers
- Created 4 reusable presentational components with Korean UI text, D-06 lotto ball colors, and D-08 bilingual strategy labels

## Task Commits

Each task was committed atomically:

1. **Task 1: Install TanStack Query, create types, API layer, and utility functions** - `ef6c02f` (feat)
2. **Task 2: Create custom hooks and all presentational components** - `70e9fb4` (feat)

## Files Created/Modified
- `frontend/src/types/lottery.ts` - TypeScript interfaces matching backend schemas + MACHINE_IDS, STRATEGIES, STRATEGY_LABELS constants
- `frontend/src/lib/api.ts` - API_BASE, fetchMachineData, fetchPrediction using native fetch
- `frontend/src/lib/lottoBallColor.ts` - getLottoBallColor (D-06 color bands) and formatNumber (D-07 zero-pad)
- `frontend/src/hooks/useMachineInfo.ts` - useQuery hook for machine metadata with staleTime=Infinity
- `frontend/src/hooks/usePrediction.ts` - useMutation hook with Promise.all over 5 strategies
- `frontend/src/components/LottoBall.tsx` - Colored circle with inline backgroundColor and 2-digit number
- `frontend/src/components/GameRow.tsx` - Game label + 6 LottoBalls in flex row
- `frontend/src/components/StrategySection.tsx` - Strategy header (bilingual) + 5 GameRows in card
- `frontend/src/components/MachineCard.tsx` - Machine selection button with draw count, latest round, selected state
- `frontend/package.json` - Added @tanstack/react-query dependency
- `frontend/src/main.tsx` - Added QueryClientProvider wrapping App

## Decisions Made
- Used `export type` for all interfaces to comply with `verbatimModuleSyntax=true` and `erasableSyntaxOnly=true` compiler options
- Used inline `style={{ backgroundColor }}` for LottoBall instead of Tailwind arbitrary values to avoid CSS purge issues
- Set `staleTime: Infinity` on useMachineInfo since machine draw data is static within a session
- usePrediction fires all 5 strategy requests in parallel via `Promise.all` for faster response

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness
- All building blocks ready for Plan 05-02 to compose MachineSelector + PredictionResults containers and rewrite App.tsx
- Components export clean interfaces that Plan 02 can import directly
- Hooks are ready to wire into the page layout with machine selection state

## Self-Check: PASSED

All 9 created files verified on disk. Both commit hashes (ef6c02f, 70e9fb4) verified in git log.

---
*Phase: 05-machine-selection-prediction-ui*
*Completed: 2026-03-27*
