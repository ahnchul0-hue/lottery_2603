# Phase 6: Statistics Dashboard - Research

**Researched:** 2026-03-27
**Domain:** React data visualization with Recharts + CSS Grid heatmap, frontend statistical computation, FastAPI backend endpoint
**Confidence:** HIGH

## Summary

This phase builds a statistics dashboard below the existing prediction results, displaying 6 chart sections for the selected machine's lottery data. The core challenge is computing statistics from the already-fetched `draws` array (via `fetchMachineData`) on the frontend using `useMemo`, and building one new backend endpoint for the 3x45 heatmap deviation data.

The dashboard uses **Recharts** (BarChart, PieChart/RadarChart) for 5 of the 6 chart types, and a **CSS Grid with inline background colors** for the heatmap (DASH-03). Recharts is specified in CLAUDE.md but is NOT currently installed in `frontend/package.json` -- it must be added as a dependency in this phase. The existing codebase has strong patterns (Container+Presentational separation, useQuery hooks, Tailwind v4 @theme tokens, LottoBall component) that this phase extends.

**Primary recommendation:** Install Recharts 3.8.x, create a `useStatistics` hook computing all frontend stats via `useMemo` from the cached `fetchMachineData` response, build one new `GET /api/statistics/heatmap` backend endpoint, and compose 6 chart card components inside a `StatisticsDashboard` container rendered below `PredictionResults` in `App.tsx`.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- **D-01:** All charts laid out in vertical scroll below prediction results
- **D-02:** Chart order: Number Frequency (DASH-01) -> Hot/Cold (DASH-02) -> Heatmap (DASH-03) -> Odd/Even & High/Low (DASH-04) -> Range Distribution (DASH-05) -> Sum Range & AC Value (DASH-06)
- **D-03:** "통계 분석" section header + horizontal border-t separator between prediction area and dashboard
- **D-04:** Hybrid approach -- simple stats (frequency, Hot/Cold, odd/even, high/low, range distribution) computed in frontend JS with useMemo
- **D-05:** Heatmap 3x45 deviation data only from backend new API endpoint (GET /api/statistics/heatmap)
- **D-06:** Frontend stats computed from already-fetched draws array (no additional API calls)
- **D-07:** Hover tooltips only -- Recharts default Tooltip component
- **D-08:** No click filtering or cross-chart interaction -- read-only dashboard
- **D-09:** Red-blue diverging color scheme for heatmap -- high frequency = red, low frequency = blue, expected = white/gray
- **D-10:** Heatmap built with HTML CSS Grid (not Recharts) -- 3 rows (machines) x 45 columns (numbers), 135 cells with background color + hover tooltip
- **D-11:** Deviation values computed on backend and served via API

### Claude's Discretion
- Chart card styling (bg-card, rounded, shadow etc. following existing patterns)
- Specific Recharts configuration (axis labels, colors, legend placement)
- useMemo hook structure (single useStatistics hook vs per-chart hooks)
- Hot/Cold number display format (LottoBall component reuse vs table)
- Sum range and AC value chart type (histogram vs line vs bar)

### Deferred Ideas (OUT OF SCOPE)
None -- discussion stayed within phase scope
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| DASH-01 | Bar chart showing number frequency (1-45) for selected machine | Recharts BarChart with 45 bars, data from useMemo over draws array. Each bar = number, value = raw count. XAxis dataKey=number, YAxis=count. |
| DASH-02 | Hot/Cold number lists showing top 10 most/least frequent | Sort frequency array, take top 10 (hot) and bottom 10 (cold). Display with LottoBall component reuse. Pure frontend computation. |
| DASH-03 | Heatmap grid (3x45) showing per-machine frequency deviation | CSS Grid with 3 rows x 45 columns. Backend endpoint computes expected vs actual deviation. Red-blue diverging scale via inline backgroundColor. |
| DASH-04 | Odd/even ratio and high/low ratio distribution charts | Parse "3:3" string format from draws. Count distribution of ratios (0:6 through 6:0 = 7 categories). Recharts BarChart or PieChart. |
| DASH-05 | Number range distribution chart (zones 1-9, 10-19, 20-29, 30-39, 40-45) | Count numbers per zone across all draws. Recharts BarChart with 5 zone categories. Frontend computation from draws array. |
| DASH-06 | Sum range and AC value distribution | Histogram of total_sum (range 56-229) and bar chart of ac_value (range 2-5). Both fields already in LotteryDraw type. Frontend computation. |
| UI-02 | Bottom area has data-analysis dashboard style (charts, statistics) | Distinct visual section with "통계 분석" header, border-t separator, darker/distinct card styling for data-analysis aesthetic. |
</phase_requirements>

## Standard Stack

### Core (Must Install)
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| recharts | ^3.8.1 | Data visualization | Specified in CLAUDE.md. Declarative React chart components built on D3+SVG. Best DX for bar/line/pie charts. NOT currently installed -- must add. |

### Already Available (No Install Needed)
| Library | Version | Purpose | Status |
|---------|---------|---------|--------|
| @tanstack/react-query | ^5.95.2 | Data fetching for heatmap API | Installed, used by useMachineInfo |
| tailwindcss | ^4.2.2 | Styling chart cards, heatmap grid | Installed, @theme tokens defined |
| react | ^19.2.4 | Component framework | Installed |
| FastAPI | ^0.135.2 | Backend API for heatmap endpoint | Installed |
| Pydantic | ^2.12.5 | Schema validation for heatmap response | Installed |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Recharts for heatmap | CSS Grid (chosen) | D-10 locks this: Recharts has no native heatmap. CSS Grid with inline colors is simpler and more appropriate for 3x45 fixed grid. |
| Recharts BarChart for ratios | PieChart | PieChart works for proportions but BarChart better shows 7-category distributions (0:6 through 6:0). Discretion area. |
| Single useStatistics hook | Per-chart hooks | Single hook avoids re-traversing draws array multiple times. Recommended. |

**Installation:**
```bash
cd frontend && npm install recharts
```

**Version verification:** Recharts 3.8.1 confirmed current on npm (checked 2026-03-27).

## Architecture Patterns

### Recommended Project Structure
```
frontend/src/
  components/
    dashboard/
      StatisticsDashboard.tsx    # Container: orchestrates all chart sections
      FrequencyBarChart.tsx       # DASH-01: BarChart for number frequency
      HotColdNumbers.tsx          # DASH-02: Hot/Cold lists with LottoBall
      HeatmapGrid.tsx             # DASH-03: CSS Grid heatmap
      RatioDistribution.tsx       # DASH-04: Odd/even + High/low charts
      RangeDistribution.tsx       # DASH-05: Zone distribution chart
      SumAcDistribution.tsx       # DASH-06: Total sum + AC value charts
      ChartCard.tsx               # Shared card wrapper (bg-card, rounded, border)
  hooks/
    useStatistics.ts             # Frontend stats computation (useMemo)
    useHeatmapData.ts            # useQuery for heatmap API
  types/
    statistics.ts                # Types for computed statistics
  lib/
    api.ts                       # Add fetchHeatmapData function

backend/app/
  api/
    routes.py                    # Add GET /api/statistics/heatmap endpoint
  schemas/
    statistics.py                # Pydantic schemas for heatmap response
  services/
    statistics_service.py        # Heatmap deviation computation
```

### Pattern 1: Frontend Statistics Computation via useMemo
**What:** Compute all simple statistics (frequency, hot/cold, ratios, ranges, sum/AC distributions) from the already-cached draws array using React useMemo, avoiding extra API calls.
**When to use:** When data is already fetched by another hook and computations are O(n) on ~130-150 records.
**Example:**
```typescript
// useStatistics.ts
import { useMemo } from 'react'
import type { LotteryDraw } from '../types/lottery'

export function useStatistics(draws: LotteryDraw[]) {
  const frequency = useMemo(() => {
    const freq: Record<number, number> = {}
    for (let n = 1; n <= 45; n++) freq[n] = 0
    for (const draw of draws) {
      for (const num of draw.numbers) freq[num]++
    }
    return freq
  }, [draws])

  const hotNumbers = useMemo(() => {
    return Object.entries(frequency)
      .sort(([, a], [, b]) => b - a)
      .slice(0, 10)
      .map(([num]) => Number(num))
  }, [frequency])

  const coldNumbers = useMemo(() => {
    return Object.entries(frequency)
      .sort(([, a], [, b]) => a - b)
      .slice(0, 10)
      .map(([num]) => Number(num))
  }, [frequency])

  // ... more computed stats
  return { frequency, hotNumbers, coldNumbers, /* ... */ }
}
```

### Pattern 2: Container + Presentational Dashboard
**What:** StatisticsDashboard container receives selectedMachine, fetches data, computes stats, passes to presentational chart components.
**When to use:** Following existing MachineSelector/PredictionResults pattern.
**Example:**
```typescript
// StatisticsDashboard.tsx
export function StatisticsDashboard({ machine }: { machine: string }) {
  const { data } = useQuery({
    queryKey: ['machineData', machine],
    queryFn: () => fetchMachineData(machine),
    staleTime: Infinity,
  })
  const stats = useStatistics(data?.draws ?? [])
  const heatmap = useHeatmapData()

  return (
    <section>
      <h2 className="text-lg font-bold text-text-primary mb-4">통계 분석</h2>
      <div className="space-y-6">
        <ChartCard title="번호 빈도"><FrequencyBarChart data={stats.frequencyData} /></ChartCard>
        <ChartCard title="Hot / Cold 번호"><HotColdNumbers hot={stats.hotNumbers} cold={stats.coldNumbers} /></ChartCard>
        {/* ... */}
      </div>
    </section>
  )
}
```

### Pattern 3: CSS Grid Heatmap with Diverging Color Scale
**What:** 3-row (machines) x 45-column (numbers) grid where each cell's background color represents deviation from expected frequency.
**When to use:** D-09/D-10 lock this pattern for DASH-03.
**Example:**
```typescript
// HeatmapGrid.tsx
function deviationToColor(deviation: number, maxDeviation: number): string {
  // Normalize to -1..+1 range
  const normalized = Math.max(-1, Math.min(1, deviation / maxDeviation))
  if (normalized > 0) {
    // Red for over-represented
    const intensity = Math.round(normalized * 200)
    return `rgb(${200 + Math.round(normalized * 55)}, ${200 - intensity}, ${200 - intensity})`
  } else {
    // Blue for under-represented
    const intensity = Math.round(Math.abs(normalized) * 200)
    return `rgb(${200 - intensity}, ${200 - intensity}, ${200 + Math.round(Math.abs(normalized) * 55)})`
  }
}

// Grid layout: grid-cols-45 is not a default Tailwind class
// Use inline style: gridTemplateColumns: 'repeat(45, 1fr)'
```

### Pattern 4: ChartCard Wrapper
**What:** Shared card component wrapping each chart section with consistent styling.
**When to use:** Every chart section needs the same visual treatment.
**Example:**
```typescript
// ChartCard.tsx -- follows existing bg-card rounded-xl border pattern from StrategySection
export function ChartCard({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <section className="bg-card rounded-xl border border-border p-4">
      <h3 className="text-base font-semibold text-text-primary mb-3">{title}</h3>
      {children}
    </section>
  )
}
```

### Anti-Patterns to Avoid
- **Making separate API calls per chart:** D-06 explicitly forbids this. All frontend stats derive from the already-fetched draws array.
- **Using Recharts for heatmap:** D-10 locks CSS Grid. Recharts has no native heatmap component.
- **Computing stats inline in JSX:** Wrap in useMemo to avoid re-computation on every render.
- **Hardcoding 45 Tailwind column classes:** `grid-cols-45` does not exist in Tailwind. Use inline `gridTemplateColumns`.
- **Fetching machineData again:** The data is already cached by TanStack Query from MachineSelector. Use the same queryKey `['machineInfo', machine]` or `['machineData', machine]` to hit the cache.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Bar charts | Custom SVG bars | Recharts BarChart | Handles axes, tooltips, responsive sizing, animations automatically |
| Responsive charts | Manual resize listeners | Recharts ResponsiveContainer | Built-in width/height auto-adjustment |
| Data fetching + caching | Manual fetch + state | TanStack Query useQuery | Already installed, handles caching, staleTime, loading/error states |
| Color mapping for lotto balls | New color function | Existing `getLottoBallColor()` | Already implemented per D-06 in Phase 5 |

**Key insight:** Most complexity is in data transformation (draws -> chart data), not in rendering. The `useMemo` hooks do the heavy lifting; Recharts and CSS Grid handle display.

## Common Pitfalls

### Pitfall 1: Recharts Not Installed
**What goes wrong:** Build fails with module not found error for recharts imports.
**Why it happens:** Recharts was specified in CLAUDE.md project stack but never added to package.json (no dashboard existed until now).
**How to avoid:** First task must install recharts: `cd frontend && npm install recharts`
**Warning signs:** Any import from 'recharts' will fail without installation.

### Pitfall 2: TanStack Query Cache Key Mismatch
**What goes wrong:** Dashboard makes a separate fetch for machine data instead of hitting the cache.
**Why it happens:** Using a different queryKey than the existing `useMachineInfo` hook.
**How to avoid:** The existing `useMachineInfo` hook transforms the response (only returns machine/totalDraws/latestRound). For the dashboard, create a new `useMachineDraws` hook with queryKey `['machineDraws', machine]` that returns the full `draws` array. Or refactor to share the same `fetchMachineData` call. TanStack Query deduplicates based on queryKey -- if the same queryKey+queryFn is used, it returns cached data.
**Warning signs:** Network tab shows duplicate `/api/data` requests.

### Pitfall 3: Heatmap Grid Column Overflow
**What goes wrong:** 45 columns in CSS Grid cause horizontal overflow or tiny unreadable cells.
**Why it happens:** 45 columns at reasonable cell sizes exceed container width (max-w-4xl = 896px -> ~20px per cell).
**How to avoid:** Accept ~19-20px cells (896px / 45 = ~19.9px). Use `overflow-x-auto` as fallback. Number labels can appear in tooltip on hover (D-07) rather than in each cell.
**Warning signs:** Layout breaks at narrower viewports.

### Pitfall 4: Odd/Even Ratio String Parsing
**What goes wrong:** Treating "3:3" as a string instead of parsing to numeric values.
**Why it happens:** `odd_even_ratio` and `high_low_ratio` are strings like "3:3" in the LotteryDraw type.
**How to avoid:** Parse with `const [odd, even] = ratio.split(':').map(Number)`. All possible values are "0:6" through "6:0" (7 categories, confirmed from data analysis).
**Warning signs:** Chart shows string labels instead of numeric categories.

### Pitfall 5: Recharts 3.0 CartesianGrid Requires Axis ID
**What goes wrong:** CartesianGrid does not render or throws warning.
**Why it happens:** Recharts 3.0 requires `xAxisId`/`yAxisId` matching on CartesianGrid when multiple axes exist.
**How to avoid:** For simple charts with one X and one Y axis, this is not an issue. Only matters with dual-axis charts. Keep charts simple per D-08.
**Warning signs:** Console warnings about mismatched axis IDs.

### Pitfall 6: Backend Heatmap Endpoint Missing Data Store Access
**What goes wrong:** New heatmap endpoint cannot access `data_store` or `decay_engine`.
**Why it happens:** The `data_store` dict is imported from `app.main` -- new endpoints in `routes.py` follow the same pattern.
**How to avoid:** Follow exact pattern of existing `get_machine_data` endpoint: `loader = data_store.get("loader")` with null check.
**Warning signs:** 503 errors from the heatmap endpoint.

## Code Examples

### Recharts BarChart for Number Frequency (DASH-01)
```typescript
// Source: Recharts official docs + CLAUDE.md specification
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'

type FrequencyData = { number: number; count: number }[]

export function FrequencyBarChart({ data }: { data: FrequencyData }) {
  return (
    <ResponsiveContainer width="100%" height={300}>
      <BarChart data={data}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="number" tick={{ fontSize: 10 }} />
        <YAxis />
        <Tooltip />
        <Bar dataKey="count" fill="#3b82f6" />
      </BarChart>
    </ResponsiveContainer>
  )
}
```

### Backend Heatmap Deviation Computation (DASH-03)
```python
# Source: Project pattern from decay_engine.py + data_loader.py
from app.schemas.lottery import LotteryDraw

def compute_heatmap_data(
    all_draws: list[LotteryDraw],
    by_machine: dict[str, list[LotteryDraw]],
) -> list[dict]:
    """Compute per-machine per-number frequency deviation from expected.

    Expected frequency for number N in machine M:
      expected = total_draws_for_M * (6 / 45)
    Deviation = (actual - expected) / expected  (normalized percentage)
    """
    machines = ["1호기", "2호기", "3호기"]
    result = []
    for machine in machines:
        draws = by_machine.get(machine, [])
        total = len(draws)
        expected_per_number = total * (6 / 45)  # ~17.9 for 134 draws

        freq = {n: 0 for n in range(1, 46)}
        for draw in draws:
            for num in draw.numbers:
                freq[num] += 1

        deviations = {}
        for num in range(1, 46):
            if expected_per_number > 0:
                deviations[num] = (freq[num] - expected_per_number) / expected_per_number
            else:
                deviations[num] = 0.0

        result.append({
            "machine": machine,
            "deviations": deviations,
            "total_draws": total,
        })
    return result
```

### Heatmap CSS Grid Cell Rendering (DASH-03)
```typescript
// Source: D-09/D-10 decisions
type HeatmapRow = {
  machine: string
  deviations: Record<string, number>
  total_draws: number
}

function deviationToColor(dev: number): string {
  // Clamp to [-1, 1] for color interpolation
  const clamped = Math.max(-1, Math.min(1, dev))
  if (clamped >= 0) {
    // White -> Red (over-represented)
    const r = 255
    const g = Math.round(255 * (1 - clamped))
    const b = Math.round(255 * (1 - clamped))
    return `rgb(${r},${g},${b})`
  } else {
    // White -> Blue (under-represented)
    const abs = Math.abs(clamped)
    const r = Math.round(255 * (1 - abs))
    const g = Math.round(255 * (1 - abs))
    const b = 255
    return `rgb(${r},${g},${b})`
  }
}

// Grid: style={{ display: 'grid', gridTemplateColumns: 'auto repeat(45, 1fr)' }}
// First column = machine label, then 45 number columns
```

### Data Shapes for Charts

```typescript
// statistics.ts -- types for computed statistics
export type NumberFrequency = { number: number; count: number }

export type RatioDistribution = { ratio: string; count: number }

export type ZoneDistribution = {
  zone: string  // "1-9", "10-19", "20-29", "30-39", "40-45"
  count: number
  percentage: number
}

export type SumDistribution = { range: string; count: number }

export type AcDistribution = { acValue: number; count: number }

export type HeatmapData = {
  machine: string
  deviations: Record<string, number>
  total_draws: number
}[]
```

### Data Analysis Results (from actual data)

Key data points that inform chart design:
- **Machine draw counts:** 1호기=134, 2호기=136, 3호기=147 (total 417)
- **AC value range:** 2-5 (only 4 distinct values -- simple bar chart, not histogram)
- **Total sum range:** 56-229 (wide range -- histogram with bins recommended)
- **Odd/Even ratios:** 7 categories: "0:6", "1:5", "2:4", "3:3", "4:2", "5:1", "6:0"
- **High/Low ratios:** Same 7 categories as odd/even
- **Expected frequency per number per machine:** ~17.9 (134 * 6/45) to ~19.6 (147 * 6/45)

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Recharts 2.x API | Recharts 3.x API | 2025 | CartesianGrid axis matching, Tooltip portal prop, TooltipContentProps type update |
| `<Customized>` wrapper required | Direct custom components in charts | Recharts 3.0 | Simpler code for custom chart elements |
| Recharts TreeMap for heatmap attempts | CSS Grid with inline colors | N/A | CSS Grid is more appropriate for fixed-size grids with custom color logic |

**Deprecated/outdated:**
- Recharts 2.x `CategoricalChartState` -- removed in 3.0, use hooks instead
- `alwaysShow` and `isFront` props on reference elements -- removed in 3.0

## Open Questions

1. **Histogram Bin Size for Total Sum Distribution (DASH-06)**
   - What we know: total_sum ranges from 56 to 229, 134-147 data points per machine
   - What's unclear: Optimal bin width for the histogram (10-unit bins give ~17 bars, 20-unit bins give ~9 bars)
   - Recommendation: Use 20-unit bins (60-79, 80-99, ..., 200-229) for readability. 8-9 bars is digestible. This is Claude's discretion.

2. **TanStack Query Cache Sharing Strategy**
   - What we know: `useMachineInfo` already fetches machine data with staleTime=Infinity. Dashboard needs the full `draws` array.
   - What's unclear: Whether to reuse the same queryKey or create a separate one
   - Recommendation: Create `useMachineDraws(machine)` with queryKey `['machineData', machine]` that returns `draws`. This is a different queryKey from `['machineInfo', machine]`, but TanStack Query efficiently caches both since they call the same API. Alternatively, consolidate into one hook but that changes Phase 5 code.

3. **Heatmap Tooltip Implementation**
   - What we know: D-07 says hover tooltips only, D-10 says CSS Grid not Recharts
   - What's unclear: Tooltip implementation for CSS Grid cells (Recharts Tooltip won't work here)
   - Recommendation: Use `title` attribute on each cell div for native browser tooltip, or a simple absolute-positioned div on hover with CSS. Keep it lightweight per D-08 (no complex interactions).

## Project Constraints (from CLAUDE.md)

- **Recharts** is the specified charting library (not D3, not Chart.js, not Nivo)
- **TanStack Query** for data fetching (not axios, not SWR)
- **Tailwind CSS v4** for styling (not CSS Modules, not Styled Components)
- **TypeScript** with `export type` pattern (verbatimModuleSyntax)
- **FastAPI** with sync def for CPU-bound endpoints
- **Pydantic v2** for API response schemas
- **Korean UI** text (Phase 5 D-09 decision)
- **No database** -- data from static JSON loaded at startup
- **Container + Presentational** component separation pattern (established in Phase 5)
- **native fetch** + JSON response pattern (no axios)
- **8-point spacing** system, Slate palette, blue-500 accent (from index.css @theme)

## Sources

### Primary (HIGH confidence)
- Project codebase: `frontend/src/` and `backend/app/` -- all existing patterns verified by reading source files
- `frontend/package.json` -- confirmed Recharts NOT installed (must add)
- Data analysis of `backend/data/new_res.json` -- confirmed machine counts, value ranges, ratio categories
- npm registry -- confirmed recharts@3.8.1 is latest (2026-03-27)

### Secondary (MEDIUM confidence)
- [Recharts 3.0 Migration Guide](https://github.com/recharts/recharts/wiki/3.0-migration-guide) -- breaking changes and new API
- [Recharts BarChart API](https://recharts.github.io/en-US/api/BarChart/) -- component props reference
- [Recharts Examples](https://recharts.github.io/en-US/examples/) -- official examples gallery

### Tertiary (LOW confidence)
- CSS Grid heatmap patterns from web search -- general approach confirmed, specific implementation details are straightforward

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - Recharts specified in CLAUDE.md, version verified on npm, all other deps already installed
- Architecture: HIGH - Extends well-established Container+Presentational pattern from Phase 5, data types and API patterns all verified from source code
- Pitfalls: HIGH - Based on actual code analysis (missing Recharts install, data format verification, cache key analysis)
- Data shapes: HIGH - Verified by analyzing actual new_res.json data (417 records, machine counts, value ranges)

**Research date:** 2026-03-27
**Valid until:** 2026-04-27 (stable -- all deps are mature, data is static)
