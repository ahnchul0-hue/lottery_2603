# Research Summary: Lottery Predictor (호기별 로또 번호 예측 웹앱)

**Domain:** Statistical analysis web application for Korean Lotto 6/45 machine-specific number selection
**Researched:** 2026-03-26
**Overall confidence:** HIGH

## Executive Summary

This project is a two-tier web application: a React (Vite) frontend for machine selection and result display, and a Python (FastAPI) backend that performs statistical analysis on 417 historical lottery draws split across 3 drawing machines. The core value proposition is machine-specific analysis with time-decay weighting -- most lottery tools treat all draws as one pool, while this tool segments by the physical machine used.

The technology stack is well-established and current. React 19.2 + Vite 8 + TypeScript 6 for frontend, FastAPI 0.135 + Pandas 3.0 + NumPy 2.4 + SciPy 1.17 for backend. All versions verified against official sources as of March 2026. No exotic dependencies, no version conflicts. The frontend uses Recharts 3.8 for data visualization and TanStack Query 5.95 for API state management. The backend uses the Strategy Pattern to implement 5 independent prediction strategies that each produce 5 game sets (25 total).

The architecture is straightforward: monorepo with two processes communicating over REST. No database needed -- 417 JSON records load into memory at startup. The main technical decision is time-decay weighting, where exponential decay via `pandas.DataFrame.ewm()` is the recommended approach with a configurable halflife parameter.

The most critical pitfall is statistical honesty. The project's own chi-square analysis showed no statistically significant difference between machines. The app must frame itself as an "analysis-informed selection tool" rather than a "prediction engine." With only ~140 draws per machine and 45 possible numbers, any observed "machine bias" is likely statistical noise amplified by multiple comparisons. The strategies must include randomization and diversity constraints to avoid producing correlated, repetitive outputs.

## Key Findings

**Stack:** React 19.2 + Vite 8 + TypeScript 6 + Tailwind 4 | FastAPI 0.135 + Pandas 3.0 + NumPy 2.4 + SciPy 1.17. All current, all HIGH confidence. Use uv (not pip) for Python package management.

**Architecture:** Monorepo, two-process (React frontend + FastAPI backend), REST API, in-memory data, Strategy Pattern for 5 prediction engines. No database.

**Critical pitfall:** Statistical honesty -- lottery draws are independent events. Frame as "analysis" not "prediction." Enforce diversity across the 25 generated number sets. Apply Bonferroni correction when reporting per-machine biases.

## Implications for Roadmap

Based on research, suggested phase structure:

1. **Foundation** - Project scaffolding + data layer + time decay engine
   - Addresses: Backend/frontend scaffold, JSON data loading, CORS config, Pydantic schemas, decay weighting utility
   - Avoids: CORS misconfiguration (Pitfall #7), NumPy serialization (Pitfall #5), async/sync mismatch (Pitfall #12)
   - Rationale: Everything depends on being able to load, filter, and weight lottery data. Build this before any analysis logic.

2. **Analysis Engine (Vertical Slice)** - First strategy end-to-end
   - Addresses: Strategy Pattern ABC, Frequency Strategy, PredictionEngine orchestrator, POST /predict endpoint
   - Avoids: Monolithic strategy function (Anti-Pattern #2), hardcoded decay parameters (Anti-Pattern #4)
   - Rationale: Prove the full pipeline (API call -> strategy -> validated result) with one strategy before building four more.

3. **Full Prediction System** - Remaining 4 strategies + integration
   - Addresses: Pattern, Range, Balance, Composite strategies. Full 25-game output.
   - Avoids: Confirmation bias / correlated strategies (Pitfall #3), overfitting (Pitfall #2)
   - Rationale: Build remaining strategies following the pattern proven in Phase 2. Add diversity constraints.

4. **Frontend UI** - Machine selector + prediction display + number balls
   - Addresses: MachineSelector, PredictButton, PredictionResults, StrategySection, GameCard, NumberBall components
   - Avoids: Dashboard information overload (Pitfall #6), chart performance (Pitfall #8)
   - Rationale: Vertical slice -- user can select machine, click predict, see all 25 games with styled number balls.

5. **Statistics Dashboard** - Charts + analytics below prediction results
   - Addresses: Stats API endpoint, FrequencyChart, StatsOverview, PatternDisplay, heatmap
   - Avoids: Dashboard overload (Pitfall #6), SVG performance (Pitfall #8)
   - Rationale: Dashboard is independent of prediction flow and can be built in parallel after Phase 3.

6. **Polish + Methodology** - Disclaimers, responsive layout, error handling, methodology documentation
   - Addresses: Disclaimer text, responsive mobile layout, loading/error states, methodology disclosure
   - Avoids: Gambler's fallacy framing (Pitfall #1), machine independence issue (Pitfall #11)
   - Rationale: Honest framing and UX polish after core functionality works.

**Phase ordering rationale:**
- Data layer first because every feature depends on it
- One strategy end-to-end before all strategies to validate the pattern and API contract
- Backend analysis before frontend display because the API response shape drives the UI
- Dashboard last because it is independent of the prediction flow
- Polish last because disclaimers and styling should not block functional development

**Research flags for phases:**
- Phase 2-3: Needs methodology research (time decay parameters, strategy weights, diversity constraints). The `/loop` 20-iteration analysis specified in PROJECT.md should happen here.
- Phase 5: May need chart library evaluation if pair heatmaps push Recharts to performance limits
- Phase 1, 4, 6: Standard patterns, unlikely to need additional research

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | All versions verified against PyPI/npm/official releases as of 2026-03-26. No version conflicts identified. |
| Features | MEDIUM-HIGH | Table stakes well-defined. Strategy algorithms need methodology research before implementation. |
| Architecture | HIGH | Standard React + FastAPI patterns. Strategy Pattern is textbook fit for multi-algorithm analysis. |
| Pitfalls | HIGH | Statistical pitfalls well-documented in literature. Integration pitfalls (CORS, NumPy serialization) are the most commonly reported FastAPI+React issues. |

## Gaps to Address

- **Time decay parameter tuning**: halflife=50 is a reasonable default but should be validated via backtesting against held-out data during Phase 2 methodology research
- **Composite strategy weights**: The 30/25/20/25 split between strategies is arbitrary. Needs empirical evaluation.
- **Diversity constraints**: Exact algorithm for enforcing diversity across 25 number sets not yet designed. Minimum Hamming distance? Unique number count threshold?
- **Pandas 3.0 breaking changes**: Major version. The `ewm()` API is stable, but other pandas patterns may have changed. Verify during implementation.
- **Data update mechanism**: Static JSON will go stale within weeks. A simple update script or documented manual process is needed but not designed yet.
