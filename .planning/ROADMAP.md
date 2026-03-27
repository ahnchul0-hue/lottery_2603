# Roadmap: Lottery Predictor (호기별 로또 번호 예측 웹앱)

## Overview

This roadmap delivers a machine-specific lottery analysis web application in 9 phases, starting from project scaffolding and data infrastructure, through a vertical-slice proof of the prediction pipeline, expanding to all 5 strategies, then building the frontend UI layer, statistics dashboard, prediction history system, and finishing with UX polish. Each phase delivers a coherent, verifiable capability that builds on the previous one. The architecture follows React (Vite) + Python (FastAPI) with in-memory JSON data.

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

- [ ] **Phase 1: Foundation & Data Layer** - Project scaffolding, JSON data loading, validation, and CORS setup
- [ ] **Phase 2: Time Decay Engine** - Exponential decay weighting system with configurable halflife
- [ ] **Phase 3: Prediction Pipeline (Vertical Slice)** - Frequency strategy end-to-end through API to prove the pattern
- [ ] **Phase 4: Full Prediction Engine** - Remaining 4 strategies + 25-game orchestration with diversity constraints
- [ ] **Phase 5: Machine Selection & Prediction UI** - Frontend machine selector, prediction trigger, and result display
- [ ] **Phase 6: Statistics Dashboard** - Charts and analytics for machine-specific statistical analysis
- [ ] **Phase 7: Prediction History & Review** - Local storage of predictions, result comparison, and strategy performance tracking
- [ ] **Phase 8: UI/UX Polish** - Dark/light mode, loading states, disclaimers, and visual refinement
- [ ] **Phase 9: Integration & Hardening** - End-to-end testing, error handling, and edge case coverage

## Phase Details

### Phase 1: Foundation & Data Layer
**Goal**: A running backend and frontend that can load, validate, and serve lottery data filtered by machine number
**Depends on**: Nothing (first phase)
**Requirements**: INFRA-01, INFRA-02, INFRA-03, DATA-01, DATA-02
**Success Criteria** (what must be TRUE):
  1. Python FastAPI server starts on localhost and responds to health check
  2. React (Vite) frontend starts on localhost and renders a placeholder page
  3. Frontend can make a cross-origin request to backend without CORS errors
  4. Backend loads new_res.json at startup and returns data filtered by machine number (1/2/3) via API
  5. Invalid data entries (wrong number range, wrong count, unsorted) are rejected during load with clear error messages
**Plans**: 3 plans

Plans:
- [x] 01-01-PLAN.md — Backend scaffolding with uv, data loader, Pydantic validation, API endpoints, tests
- [x] 01-02-PLAN.md — Frontend scaffolding with Vite React TypeScript, Tailwind CSS v4, design tokens
- [x] 01-03-PLAN.md — Wire frontend to backend health endpoint, verify CORS end-to-end

### Phase 2: Time Decay Engine
**Goal**: A reusable time-decay weighting module that assigns exponentially decaying weights to historical draws
**Depends on**: Phase 1
**Requirements**: DECAY-01, DECAY-02
**Success Criteria** (what must be TRUE):
  1. Given a list of draws, the decay engine returns per-draw weights where the most recent draw has the highest weight
  2. The halflife parameter defaults to 30 and can be changed at the code level without modifying core logic
  3. Weight values follow an exponential decay curve (verifiable by plotting or spot-checking ratios between consecutive draws)
**Plans**: 1 plan

Plans:
- [x] 02-01-PLAN.md — TDD: DecayEngine class with exponential decay weighting, 8 test cases, config parameterization

### Phase 3: Prediction Pipeline (Vertical Slice)
**Goal**: One complete prediction strategy (Frequency) works end-to-end: API request with machine number returns 5 valid game sets
**Depends on**: Phase 2
**Requirements**: PRED-01, PRED-06
**Success Criteria** (what must be TRUE):
  1. POST /predict with machine=1 and strategy=frequency returns 5 game sets
  2. Each game set contains exactly 6 numbers in the 1-45 range, with no duplicates, in ascending order
  3. The frequency strategy applies time-decay weighted frequency counts to select numbers biased toward historically frequent numbers for the chosen machine
  4. The Strategy Pattern ABC is established so new strategies can be added by implementing a single interface
**Plans**: 2 plans

Plans:
- [x] 03-01-PLAN.md — TDD: Strategy Pattern ABC, FrequencyStrategy with weighted selection and diversity enforcement, Pydantic schemas
- [x] 03-02-PLAN.md — Wire POST /api/predict endpoint, add DecayEngine to lifespan, integration tests

### Phase 4: Full Prediction Engine
**Goal**: All 5 strategies produce 25 total games with guaranteed diversity across the full set
**Depends on**: Phase 3
**Requirements**: PRED-02, PRED-03, PRED-04, PRED-05, PRED-07
**Success Criteria** (what must be TRUE):
  1. Pattern strategy generates 5 games using pair frequency, consecutive number, and ending-digit patterns for the selected machine
  2. Range strategy generates 5 games reflecting the selected machine's number distribution across the 5 range buckets (1-9, 10-19, 20-29, 30-39, 40-45)
  3. Balance strategy generates 5 games reflecting the selected machine's odd/even and high/low ratio tendencies
  4. Composite strategy generates 5 games by combining weighted outputs from all 4 individual strategies
  5. No two games among the 25 are identical number sets
**Plans**: 3 plans

Plans:
- [x] 04-01-PLAN.md — PatternStrategy: pair frequency + consecutive injection + ending-digit completion (TDD)
- [x] 04-02-PLAN.md — RangeStrategy (zone distribution) + BalanceStrategy (odd/even + high/low) (TDD)
- [x] 04-03-PLAN.md — CompositeStrategy (weighted blend 40/20/20/20) + schema/registry wiring + API integration tests

### Phase 5: Machine Selection & Prediction UI
**Goal**: Users can select a machine, trigger prediction, and see all 25 games organized by strategy in a clean card layout
**Depends on**: Phase 4
**Requirements**: MACH-01, MACH-02, MACH-03, UI-01
**Success Criteria** (what must be TRUE):
  1. User sees three machine selection buttons (1호기 / 2호기 / 3호기) and can select one
  2. Upon selecting a machine, the total draw count and most recent draw round for that machine are displayed
  3. User clicks "번호 예측" and receives 25 games grouped into 5 strategy sections with 5 games each
  4. The upper area of the page has a clean, modern card-based layout showing machine selector and prediction results
**Plans**: 2 plans

Plans:
- [x] 05-01-PLAN.md — Install TanStack Query, types, API layer, hooks, and presentational components
- [x] 05-02-PLAN.md — MachineSelector + PredictionResults containers, rewrite App.tsx with full layout

### Phase 6: Statistics Dashboard
**Goal**: Users can view machine-specific statistical analysis through interactive charts and visualizations below the prediction area
**Depends on**: Phase 1 (data layer), Phase 5 (UI shell)
**Requirements**: DASH-01, DASH-02, DASH-03, DASH-04, DASH-05, DASH-06, UI-02
**Success Criteria** (what must be TRUE):
  1. A bar chart shows number frequency (1-45) for the selected machine
  2. Hot/Cold number lists display the top 10 most and least frequent numbers for the selected machine
  3. A heatmap grid (3x45) shows per-machine frequency deviation from expected values
  4. Charts display odd/even ratio, high/low ratio, range distribution, sum range, and AC value distribution for the selected machine
  5. The dashboard section is visually distinct from the prediction area with a data-analysis aesthetic
**Plans**: 3 plans
**UI hint**: yes

Plans:
- [x] 06-01-PLAN.md — Backend heatmap API + install Recharts + types + hooks + ChartCard wrapper
- [x] 06-02-PLAN.md — FrequencyBarChart + HotColdNumbers + HeatmapGrid + StatisticsDashboard container + App.tsx integration
- [x] 06-03-PLAN.md — RatioDistribution + RangeDistribution + SumAcDistribution + complete dashboard

### Phase 7: Prediction History & Review
**Goal**: Users can save predictions, compare them against actual results, track strategy performance, and receive AI-generated reflection memos fed back into future predictions
**Depends on**: Phase 5
**Requirements**: HIST-01, HIST-02, HIST-03, HIST-04, HIST-05, HIST-06, HIST-07
**Success Criteria** (what must be TRUE):
  1. Each prediction run can be saved locally with round number, machine, strategy, date, and all 25 game numbers
  2. User can enter actual winning numbers and see automatic comparison (match count per game, per-strategy hit rate)
  3. A strategy performance report shows which strategy has the best historical match rate
  4. Failed prediction analysis shows which numbers were missed and which were overestimated
  5. AI (Claude API) auto-generates reflection memos that are fed back into next predictions for the same machine
**Plans**: 3 plans
**UI hint**: yes

Plans:
- [x] 07-01-PLAN.md — Types, localStorage adapter, comparison utility, hooks (useHistoryStorage, useReflection)
- [x] 07-02-PLAN.md — Backend: install anthropic SDK, reflection schema/service, POST /api/reflect endpoint
- [x] 07-03-PLAN.md — All history UI components + HistorySection container + App.tsx integration

### Phase 8: UI/UX Polish
**Goal**: The application feels complete with theme support, loading feedback, and honest statistical framing
**Depends on**: Phase 5, Phase 6, Phase 7
**Requirements**: UI-03, UI-04, UI-05
**Success Criteria** (what must be TRUE):
  1. User can toggle between dark mode and light mode, and the preference persists across page reloads
  2. A loading animation is visible during prediction computation, and the UI does not freeze or appear broken
  3. A clear disclaimer is always visible stating this is an analysis tool, not a guarantee of winning
**Plans**: TBD
**UI hint**: yes

Plans:
- [ ] 08-01: TBD
- [ ] 08-02: TBD

### Phase 9: Integration & Hardening
**Goal**: The complete application handles edge cases gracefully and all features work together without regressions
**Depends on**: Phase 8
**Requirements**: (cross-cutting — validates all prior requirements work together)
**Success Criteria** (what must be TRUE):
  1. Switching machines rapidly does not cause stale data or UI glitches
  2. Backend returns meaningful error responses (not 500s) for invalid machine numbers, malformed requests, or missing data
  3. The full user flow (select machine -> predict -> view dashboard -> save history -> compare results -> write memo) completes without errors
**Plans**: TBD

Plans:
- [ ] 09-01: TBD
- [ ] 09-02: TBD

## Progress

**Execution Order:**
Phases execute in numeric order: 1 -> 2 -> 3 -> 4 -> 5 -> 6 -> 7 -> 8 -> 9

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Foundation & Data Layer | 3/3 | Complete | 2026-03-26 |
| 2. Time Decay Engine | 0/1 | Planned | - |
| 3. Prediction Pipeline (Vertical Slice) | 0/2 | Not started | - |
| 4. Full Prediction Engine | 0/3 | Planned | - |
| 5. Machine Selection & Prediction UI | 0/2 | Planned | - |
| 6. Statistics Dashboard | 0/3 | Planned | - |
| 7. Prediction History & Review | 1/3 | In Progress | - |
| 8. UI/UX Polish | 0/2 | Not started | - |
| 9. Integration & Hardening | 0/2 | Not started | - |
