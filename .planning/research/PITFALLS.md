# Domain Pitfalls

**Domain:** Lottery prediction/analysis web application (Korean Lotto 6/45 hoogi-based)
**Researched:** 2026-03-26
**Dataset:** 417 draws, rounds 800-1216, 3 machines (1hoogi: 134, 2hoogi: 136, 3hoogi: 147)

---

## Critical Pitfalls

Mistakes that undermine the entire project's credibility or cause fundamental design failures.

### Pitfall 1: Gambler's Fallacy Baked Into the Algorithm

**What goes wrong:** The core premise -- "recent winning numbers are more likely to appear again" -- is the textbook gambler's fallacy (or its inverse, the hot-hand fallacy). Lottery draws are independent events by design. Each draw's outcome has zero causal relationship with previous draws. Building time-decay weighting that assumes recent numbers are "more likely" creates a prediction engine built on a statistical falsehood.

**Why it happens:** Human brains are wired for pattern recognition (apophenia). When we see number 10 appear 2.9x more than expected on machine 1, we assume a causal mechanism. But the project's own chi-square test already confirmed: there is no statistically significant difference in number distribution between machines (p > 0.05 with 174-draw sample).

**Consequences:**
- Users trust predictions that have no mathematical basis beyond random selection
- If backtested honestly, predictions will perform no better than random
- Credibility destruction if anyone with statistics knowledge reviews the methodology

**Prevention:**
- Frame the entire app as "analysis-informed number selection" not "prediction"
- Time-decay weighting should be framed as "recency preference" (a user-chosen strategy), not as a probabilistic model
- Include honest methodology disclosure: "Lottery draws are independent events. This tool applies statistical patterns as selection heuristics, not probability predictions."
- Never display "probability" or "likelihood" percentages next to generated numbers

**Detection (warning signs):**
- Any documentation or UI copy that uses words like "predicted", "likely", "probability of winning"
- Backend code that returns confidence scores alongside number sets
- Absence of disclaimers on the results page

**Phase mapping:** Phase 1 (Foundation) -- establish the framing and disclaimer language before any algorithm work begins. This is an architectural decision, not a cosmetic one.

**Confidence:** HIGH -- supported by extensive academic literature on lottery independence and gambler's fallacy.

### Pitfall 2: Overfitting to a Small, Machine-Split Sample

**What goes wrong:** The dataset has 417 total draws split across 3 machines (~134-147 per machine). When analyzing per-machine patterns across 45 possible numbers, each number appears roughly 18-20 times per machine on average. Finding that number 10 appears "2.9x more than expected" on machine 1 is likely noise, not signal. With 45 numbers tested per machine, you expect ~2-3 numbers to appear statistically significant at p < 0.05 purely by chance (multiple comparisons problem).

**Why it happens:** No correction for multiple hypothesis testing. When you test 45 numbers across 3 machines (135 comparisons), the probability of finding at least one "significant" result by pure chance is approximately 1 - (0.95)^135 = 99.9%. You will always find "patterns."

**Consequences:**
- Strategies built on spurious patterns that disappear with new data
- Pair frequencies (e.g., "1hoogi favors 22,38") are especially unreliable -- with C(45,2) = 990 possible pairs per machine, any pair analysis on ~134 draws is pure noise
- Users develop false confidence in machine-specific "tendencies"

**Prevention:**
- Apply Bonferroni correction or FDR (Benjamini-Hochberg) when reporting per-machine number biases. With 45 tests per machine, significance threshold becomes 0.05/45 = 0.0011 instead of 0.05
- Report effect sizes alongside p-values -- a number appearing 2.9x more than expected sounds dramatic but may be +5 occurrences over 134 draws
- Add sample size warnings in the dashboard: "Based on N=134 draws. Minimum recommended sample: 500+ per machine for reliable frequency analysis."
- Treat all per-machine patterns as "observed tendencies" not "machine characteristics"

**Detection (warning signs):**
- Per-machine frequency tables without confidence intervals
- Pair/pattern analysis without multiple comparison correction
- Any claim of "machine X favors number Y" without effect size context

**Phase mapping:** Phase 2 (Analysis Engine) -- implement statistical corrections before building strategy algorithms. The analysis engine must produce honest statistics, not marketing-friendly ones.

**Confidence:** HIGH -- standard statistical methodology. The project's own chi-square test already confirmed no significant inter-machine differences.

### Pitfall 3: Confirmation Bias in Strategy Design

**What goes wrong:** The 5 strategies (frequency, pattern, interval, odd-even balance, composite) are designed to find patterns. In random data, they WILL find patterns. The composite strategy that combines all four others will amplify any spurious signals because all four strategies are mining the same small dataset. This is not "ensemble learning" -- it is correlated noise amplification.

**Why it happens:** Each strategy looks at the same underlying data through a slightly different lens. If number 10 is over-represented on machine 1 (by random chance), the frequency strategy picks it up. The interval strategy notices "10-19 range is hot." The pattern strategy finds pairs containing 10. The composite strategy then heavily weights number 10 because "multiple independent strategies agree" -- but they are not independent.

**Consequences:**
- The composite strategy produces less diverse numbers, not more reliable ones
- Certain numbers cluster across all 25 games instead of providing genuine variety
- The "5 strategies for diversity" promise is broken

**Prevention:**
- Enforce diversity constraints across strategies: minimum Hamming distance between number sets from different strategies
- Add a randomization component to each strategy (e.g., weighted random sampling rather than deterministic top-N selection)
- The composite strategy should detect and discount correlated signals across strategies
- Consider making at least one strategy purely random as a control/baseline

**Detection (warning signs):**
- Multiple strategies consistently recommending the same numbers for a given machine
- Composite strategy output looking nearly identical to frequency strategy output
- Less than 30 unique numbers across all 25 games (should be 35+ for genuine diversity)

**Phase mapping:** Phase 2-3 (Analysis Engine and Strategy Implementation) -- build diversity metrics and test them before shipping.

**Confidence:** HIGH -- direct consequence of analyzing correlated views of the same small dataset.

---

## Moderate Pitfalls

Issues that cause significant rework, poor UX, or technical debt.

### Pitfall 4: Time Decay Weighting -- Wrong Function, Wrong Parameters

**What goes wrong:** The choice of decay function (exponential, linear, polynomial) and decay rate dramatically changes which numbers get recommended. Too aggressive decay (e.g., half-life of 10 draws) effectively ignores 90%+ of the already-small dataset. Too gentle decay (half-life of 200 draws) makes it indistinguishable from uniform weighting. There is no "correct" decay rate because there is no underlying causal mechanism to calibrate against.

**Why it happens:** Developers pick a decay function (usually exponential) and a rate constant without empirical justification. The function "feels right" but is never validated.

**Consequences:**
- Aggressive decay: analysis effectively uses only 30-50 recent draws per machine, making sample size problems from Pitfall 2 dramatically worse
- Gentle decay: no observable difference from unweighted analysis, making the feature appear broken
- Wrong function shape: linear decay punishes old data too harshly at the boundary; step-function decay creates artificial discontinuities

**Prevention:**
- Implement decay as a user-configurable parameter with sensible defaults, not a hardcoded constant
- Provide visualization of the decay curve so users understand what "recency weighting" means in practice
- Default to moderate exponential decay with half-life of ~100 draws (roughly 2 years of data), ensuring at least 200+ effective draws per machine
- Show "effective sample size" alongside results: if decay reduces 134 draws to an effective N of 25, display that prominently
- Validate by backtesting: do decayed predictions outperform unweighted predictions on held-out data?

**Detection (warning signs):**
- Effective sample size dropping below 50 per machine after weighting
- Decay rate chosen without any backtesting or sensitivity analysis
- No UI control or visibility into decay parameters

**Phase mapping:** Phase 2 (Analysis Engine) -- decay function selection should be a researched, configurable decision with visualization, not an implementation detail.

**Confidence:** MEDIUM -- the optimal approach depends on user preferences, but the pitfalls of extreme parameterization are well-documented in time-series analysis.

### Pitfall 5: NumPy/Pandas Type Serialization Breaking the API

**What goes wrong:** Python's NumPy and Pandas use specialized numeric types (numpy.int64, numpy.float64) that are NOT JSON-serializable. FastAPI's default JSON encoder silently fails or throws `TypeError: Object of type int64 is not JSON serializable`. The insidious part: this error often manifests as a CORS error in the browser because the backend crashes before sending CORS headers, making it appear to be a frontend configuration problem.

**Why it happens:** Any statistical computation using NumPy/Pandas returns NumPy types by default. Developers test with print() or logging (which auto-converts) but never test the JSON serialization path until integration.

**Consequences:**
- API returns 500 errors that look like CORS errors in the browser
- Hours of debugging CORS configuration when the problem is in the backend
- Intermittent failures when some code paths return Python int vs numpy.int64

**Prevention:**
- Create a custom JSON encoder or Pydantic model that handles NumPy types from day one:
  ```python
  class NumpyEncoder(json.JSONEncoder):
      def default(self, obj):
          if isinstance(obj, np.integer): return int(obj)
          if isinstance(obj, np.floating): return float(obj)
          if isinstance(obj, np.ndarray): return obj.tolist()
          return super().default(obj)
  ```
- Use Pydantic response models for all FastAPI endpoints -- Pydantic handles type coercion automatically
- Add integration tests that verify JSON serialization of every endpoint response
- Convert all NumPy types to Python native types at the boundary between analysis code and API code

**Detection (warning signs):**
- CORS errors in the browser that persist despite correct CORS configuration
- API endpoints that work in unit tests but fail in integration
- Inconsistent behavior depending on which code path is executed

**Phase mapping:** Phase 1 (Foundation) -- set up Pydantic response models and the custom encoder before writing any analysis endpoints.

**Confidence:** HIGH -- this is one of the most commonly reported FastAPI + NumPy integration issues.

### Pitfall 6: Dashboard Information Overload

**What goes wrong:** With 3 machines, 45 numbers, 5 strategies, frequency distributions, pair analysis, AC values, odd-even ratios, interval distributions, and time-series charts, the temptation is to show everything. Data-heavy dashboards that display all available statistics overwhelm users and obscure the actual purpose (selecting lottery numbers).

**Why it happens:** Developers who enjoy data analysis build dashboards for themselves, not for casual lottery players. Every statistic feels important when you built it.

**Consequences:**
- Users cannot find the generated numbers among the sea of charts
- Cognitive overload leads to decision paralysis (the opposite of the app's purpose)
- Slow page loads from rendering dozens of charts simultaneously
- Mobile experience is unusable

**Prevention:**
- Apply progressive disclosure: top section shows ONLY the 25 generated number sets. Dashboard is below the fold or on a separate tab
- Limit the main view to 5 visualizations maximum
- Use the "5-second test": if a user cannot find their predicted numbers within 5 seconds, the UI has failed
- Group statistics into collapsible sections: "Quick Stats" (always visible), "Deep Analysis" (collapsed by default)
- Implement lazy loading for charts below the fold

**Detection (warning signs):**
- More than 7 distinct chart components on the initial view
- No clear visual hierarchy between results and analytics
- Page load time exceeding 2 seconds
- Users need to scroll to find their generated numbers

**Phase mapping:** Phase 3 (Frontend/UI) -- wireframe the information hierarchy before building any chart components. The results card must be designed first.

**Confidence:** HIGH -- well-documented UX principle across dashboard design literature.

### Pitfall 7: CORS Misconfiguration Between React Dev Server and FastAPI

**What goes wrong:** React's Vite dev server runs on localhost:5173, FastAPI runs on localhost:8000. Browsers enforce same-origin policy. Common mistakes: using `*` for allow_origins (breaks if credentials are needed later), mixing `localhost` and `127.0.0.1` (browsers treat them as different origins), adding CORS middleware after route definitions (middleware order matters in FastAPI).

**Why it happens:** CORS works fine in production when both are served from the same origin. Developers only encounter issues during development with separate servers, then "fix" it with overly permissive settings that mask real problems.

**Consequences:**
- Blocked requests during development
- False sense of security with wildcard origins
- Production deployment breaks if CORS settings were development-only hacks

**Prevention:**
- Configure CORS explicitly in FastAPI from the start:
  ```python
  app.add_middleware(
      CORSMiddleware,
      allow_origins=["http://localhost:5173"],  # Vite default
      allow_methods=["GET", "POST"],
      allow_headers=["*"],
  )
  ```
- Add CORS middleware BEFORE all route definitions
- Use environment-based origin configuration (dev vs prod)
- Test CORS with actual browser requests, not just curl/Postman (which ignore CORS)

**Detection (warning signs):**
- `Access-Control-Allow-Origin` errors in browser console
- Requests working in Postman but failing in the browser
- Using `allow_origins=["*"]` as a permanent solution

**Phase mapping:** Phase 1 (Foundation) -- CORS configuration is part of project scaffolding, not an afterthought.

**Confidence:** HIGH -- most commonly reported React + FastAPI integration issue.

### Pitfall 8: SVG-Based Chart Performance with Per-Number Frequency Data

**What goes wrong:** Recharts (the most popular React charting library) renders via SVG. Each data point creates a DOM node. When rendering frequency histograms for 45 numbers across 3 machines, with tooltips, animations, and hover states, the DOM node count grows quickly. Combined with React's re-rendering on state changes (e.g., switching machines), this causes visible jank and slow transitions.

**Why it happens:** Recharts handles typical charts (5-20 data points) well. But lottery analysis dashboards often need: 45-bar frequency histograms, time-series of 400+ draws, heatmaps of number pairs (45x45), and multiple synchronized charts.

**Consequences:**
- Visible lag when switching between machines (re-rendering all charts)
- Memory issues on mobile devices
- Animation stuttering that makes the app feel unpolished

**Prevention:**
- Use React.memo and useMemo aggressively for chart components
- Downsample time-series data for overview charts (show every 10th draw), with drill-down for full resolution
- Consider a Canvas-based library (ECharts via echarts-for-react) if pair heatmaps or large time-series are needed
- Lazy-load charts that are below the fold
- Disable animations on mobile or when rendering >100 data points
- Pre-compute all statistics on the backend; the frontend should only render, not calculate

**Detection (warning signs):**
- Chart rendering taking >200ms (measure with React DevTools Profiler)
- Lighthouse performance score dropping below 70
- Visible layout shift when charts load (CLS > 0.1)

**Phase mapping:** Phase 3 (Frontend/UI) -- choose charting library based on actual data volume requirements. Profile early with realistic data.

**Confidence:** MEDIUM -- dataset is moderate (417 draws, 45 numbers), so this only becomes critical if pair/heatmap visualizations are included.

---

## Minor Pitfalls

Issues that cause friction or tech debt but are easily fixable.

### Pitfall 9: Hardcoded Korean Text Blocking Future Localization

**What goes wrong:** All UI text, strategy names, error messages, and data labels are hardcoded in Korean throughout components. If the project ever needs English support or if a non-Korean speaker contributes, the codebase becomes inaccessible.

**Prevention:**
- Create a constants/labels file from the start, even if only Korean:
  ```typescript
  const LABELS = {
    machine: { 1: '1호기', 2: '2호기', 3: '3호기' },
    strategies: { frequency: '빈도 전략', pattern: '패턴 전략', ... }
  }
  ```
- Use semantic variable names in English for code, Korean only in display strings

**Phase mapping:** Phase 3 (Frontend/UI) -- establish the pattern before building components.

**Confidence:** LOW -- this is a nice-to-have for a localhost-only personal tool, but good practice.

### Pitfall 10: No Data Update Path

**What goes wrong:** The app uses a static `new_res.json` file with rounds 800-1216. New lottery draws happen weekly. Without a mechanism to update the data file, the app becomes stale within weeks.

**Prevention:**
- Design the data loading to be file-path configurable, not hardcoded
- Document the data format clearly so manual updates are straightforward
- Consider a simple script that appends new draw data to the JSON file
- Validate new data entries against schema before merging (round number sequence, 6 numbers in range 1-45, valid machine ID)

**Detection (warning signs):**
- File path hardcoded in multiple locations
- No data validation on load
- No documentation of how to add new draw data

**Phase mapping:** Phase 1 (Foundation) -- data loading architecture should accommodate updates from the start.

**Confidence:** HIGH -- the dataset will go stale immediately after deployment.

### Pitfall 11: Ignoring the Statistical Elephant -- Machine Independence

**What goes wrong:** The project's own preliminary analysis showed chi-square tests found NO statistically significant difference between machines. Yet the entire app is built on the premise that machines have distinct characteristics. This creates a cognitive dissonance: the science says machines are interchangeable, but the UX says "choose your machine for personalized predictions."

**Prevention:**
- Acknowledge this honestly in the methodology section
- Frame machine selection as "filter by machine" (a user preference) rather than "machines have unique prediction profiles"
- Consider showing the chi-square result in the dashboard as a transparency measure
- Offer a "combined analysis" option that pools all machine data (effectively more statistical power with N=417 instead of ~140)

**Detection (warning signs):**
- UI language implying machines have inherent biases
- No mention of the chi-square independence result anywhere in the app
- Combined/all-machines analysis option absent

**Phase mapping:** Phase 2-3 (Analysis Engine and UI) -- the framing should be established early and reflected in both backend logic and frontend copy.

**Confidence:** HIGH -- the project's own data supports this conclusion.

### Pitfall 12: Async/Sync Mismatch in FastAPI with NumPy Computation

**What goes wrong:** FastAPI is async by default. NumPy/Pandas computations are CPU-bound and synchronous. Declaring analysis endpoints as `async def` while running CPU-bound NumPy code inside them blocks the event loop, preventing other requests from being served.

**Prevention:**
- Use regular `def` (not `async def`) for endpoints that do heavy computation -- FastAPI will run them in a thread pool automatically
- Or use `run_in_executor` for CPU-bound work inside async endpoints
- For this project's data size (417 entries), computation is fast enough that this is unlikely to be noticeable, but the pattern should be correct from the start

**Detection (warning signs):**
- Frontend showing loading spinners for 2+ seconds on simple requests
- Multiple simultaneous requests queuing instead of parallelizing
- `async def` endpoints calling NumPy/Pandas without executor delegation

**Phase mapping:** Phase 1 (Foundation) -- establish the endpoint pattern template early.

**Confidence:** MEDIUM -- the dataset is small enough that this may never manifest, but the correct pattern costs nothing to implement.

---

## Phase-Specific Warnings

| Phase Topic | Likely Pitfall | Mitigation | Severity |
|-------------|---------------|------------|----------|
| Foundation / Scaffolding | CORS misconfiguration (#7), NumPy serialization (#5) | Set up Pydantic models + CORS config in initial scaffold | High |
| Foundation / Data Layer | No update path (#10), async/sync mismatch (#12) | Configurable data path, correct endpoint patterns | Medium |
| Analysis Engine | Overfitting (#2), confirmation bias (#3), wrong decay (#4) | Statistical corrections, diversity constraints, configurable decay | Critical |
| Analysis Engine | Machine independence (#11) | Honest framing, combined-analysis option | High |
| Strategy Implementation | Gambler's fallacy framing (#1), correlated strategies (#3) | Disclaimers, diversity enforcement, randomization component | Critical |
| Frontend / UI | Dashboard overload (#6), chart performance (#8) | Progressive disclosure, lazy loading, memoization | High |
| Frontend / UI | Hardcoded Korean (#9) | Labels file from day one | Low |
| Integration Testing | NumPy serialization (#5), CORS (#7) | End-to-end JSON serialization tests | High |

---

## Meta-Pitfall: The Honesty Problem

The deepest pitfall in lottery prediction projects is the tension between what the user wants to hear ("this tool gives you an edge") and what statistics says ("lottery draws are random and independent"). Every design decision should err on the side of honesty:

- Call it "number selection tool" not "prediction engine"
- Show analysis as "historical patterns" not "future probabilities"
- Include a visible methodology disclaimer on every results page
- Frame time-decay as "user preference for recency" not "statistical model"

This is not just an ethical nicety -- it protects the project from being dismissed as yet another lottery scam tool by anyone with basic statistics knowledge.

---

## Sources

### Statistical Foundations
- [Gambler's Fallacy - Wikipedia](https://en.wikipedia.org/wiki/Gambler's_fallacy)
- [Predicting Lotto Numbers: A Natural Experiment on Gambler's Fallacy](https://homepage.univie.ac.at/jean-robert.tyran/media/files/RevisionNaturalExperimentLotto_JulyJR.pdf)
- [The Number of Available Sample Observations Modulates Gambler's Fallacy](https://www.nature.com/articles/s41598-024-84929-5)
- [Statistical Auditing and Randomness Test of Lotto Games](https://arxiv.org/abs/0806.4595)
- [Statistical Randomness Test for Korean Lotto Game](https://www.researchgate.net/publication/263402352_Statistical_randomness_test_for_Korean_lotto_game)
- [Chi-Square and the Lottery](https://lstats0.tripod.com/_TheLottery.pdf)

### Multiple Testing Correction
- [Multiple Comparisons: Bonferroni and FDR](https://physiology.med.cornell.edu/people/banfelder/qbio/resources_2008/1.5_Bonferroni_FDR.pdf)
- [False Discovery Rate - Columbia University](https://www.publichealth.columbia.edu/research/population-health-methods/false-discovery-rate)

### Apophenia and Confirmation Bias
- [Apophenia - Wikipedia](https://en.wikipedia.org/wiki/Apophenia)
- [Apophenia: Perceiving Meaningful Patterns in Random Data](https://www.renascence.io/journal/apophenia-perceiving-meaningful-patterns-in-random-data)
- [Apophenia Explained - MasterClass 2026](https://www.masterclass.com/articles/how-to-avoid-apophenia-bias)

### Time Decay Weighting
- [Forward Decay: A Practical Time Decay Model for Streaming Systems](https://dimacs.rutgers.edu/~graham/pubs/papers/fwddecay.pdf)
- [The Math of Weighting Past Results - Fangraphs](https://tht.fangraphs.com/the-math-of-weighting-past-results/)
- [Optimisation of Decay Factor in Time Weighted Models](https://www.tandfonline.com/doi/pdf/10.1080/1331677X.2010.11517402)

### React + FastAPI Integration
- [FastAPI CORS Documentation](https://fastapi.tiangolo.com/tutorial/cors/)
- [FastAPI + NumPy JSON Serialization Issue #15085](https://github.com/fastapi/fastapi/issues/15085)
- [Developing SPA with FastAPI and React - TestDriven.io](https://testdriven.io/blog/fastapi-react/)
- [Not All CORS Errors Are CORS Errors](https://dev.to/jakubstetz/not-all-cors-errors-are-cors-errors-njn)

### Dashboard UX
- [Effective Dashboard Design Principles 2025 - UXPin](https://www.uxpin.com/studio/blog/dashboard-design-principles/)
- [Why Dashboards Fail - Orbix Studio](https://medium.com/@orbix.studiollc/why-dashboards-fail-and-how-thoughtful-ux-can-turn-data-into-action-7b5d88b283c3)
- [UX Strategies for Real-Time Dashboards - Smashing Magazine](https://www.smashingmagazine.com/2025/09/ux-strategies-real-time-dashboards/)

### Chart Performance
- [Recharts Performance Guide](https://recharts.github.io/en-US/guide/performance/)
- [Recharts Large Data Issue #1146](https://github.com/recharts/recharts/issues/1146)
- [Best React Chart Libraries 2025 - LogRocket](https://blog.logrocket.com/best-react-chart-libraries-2025/)

### Legal/Ethical
- [Is It Illegal to Use AI for Lottery Predictions?](https://mems21.org/is-it-illegal-to-use-ai-for-lottery-predictions-what-the-law-says)
- [AI Lottery Prediction App: Fun or Fraud?](https://reelmind.ai/blog/ai-lottery-prediction-app-fun-or-fraud)
