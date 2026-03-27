---
phase: 06-statistics-dashboard
verified: 2026-03-27T04:45:00Z
status: passed
score: 5/5 must-haves verified
re_verification: false
---

# Phase 6: Statistics Dashboard Verification Report

**Phase Goal:** Users can view machine-specific statistical analysis through interactive charts and visualizations below the prediction area
**Verified:** 2026-03-27T04:45:00Z
**Status:** passed
**Re-verification:** No -- initial verification

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | A bar chart shows number frequency (1-45) for the selected machine | VERIFIED | `FrequencyBarChart.tsx` renders Recharts BarChart with 45 bars (dataKey="number", dataKey="count"), fed from `useStatistics` frequencyData which counts all 45 numbers from draws array via useMemo |
| 2 | Hot/Cold number lists display the top 10 most and least frequent numbers for the selected machine | VERIFIED | `HotColdNumbers.tsx` renders two rows of `LottoBall` components; `useStatistics` derives hotNumbers (top 10 by count desc) and coldNumbers (bottom 10 by count asc) from frequencyData |
| 3 | A heatmap grid (3x45) shows per-machine frequency deviation from expected values | VERIFIED | `HeatmapGrid.tsx` renders CSS Grid with `gridTemplateColumns: 'auto repeat(45, 1fr)'` and 3 machine rows; backend `compute_heatmap_data` computes (actual-expected)/expected for 45 numbers across 3 machines (134/136/147 draws); `deviationToColor` maps deviations to red-blue color scale; legend shows labels in Korean |
| 4 | Charts display odd/even ratio, high/low ratio, range distribution, sum range, and AC value distribution for the selected machine | VERIFIED | `RatioDistribution.tsx` renders side-by-side odd/even (7 categories) and high/low (7 categories) bar charts; `RangeDistribution.tsx` renders 5-zone bar chart; `SumAcDistribution.tsx` renders sum histogram and AC value chart in 60/40 split; all data computed by `useStatistics` hook from draws array |
| 5 | The dashboard section is visually distinct from the prediction area with a data-analysis aesthetic | VERIFIED | `App.tsx` line 48: `border-t border-border mt-8 pt-8` separator div with `h2` "통계 분석" header; `ChartCard.tsx` provides `bg-card rounded-xl border border-border p-4` card wrapper with `text-base font-bold` title; 6 ChartCard sections in vertical layout with `space-y-6` |

**Score:** 5/5 truths verified

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `frontend/src/types/statistics.ts` | TypeScript types for chart data | VERIFIED | 826 bytes, exports 8 types: NumberFrequency, RatioDistribution, ZoneDistribution, SumDistribution, AcDistribution, HeatmapRow, HeatmapData, StatisticsResult |
| `frontend/src/hooks/useStatistics.ts` | Frontend statistics computation | VERIFIED | 4070 bytes, exports useStatistics with 8 useMemo computations, cascaded dependency chain |
| `frontend/src/hooks/useHeatmapData.ts` | TanStack Query hook for heatmap | VERIFIED | 309 bytes, useQuery with queryKey=['heatmap'], fetchHeatmapData, staleTime: Infinity |
| `frontend/src/components/dashboard/ChartCard.tsx` | Card wrapper for chart sections | VERIFIED | 326 bytes, bg-card rounded-xl border border-border p-4, text-base font-bold title |
| `frontend/src/components/dashboard/FrequencyBarChart.tsx` | Recharts BarChart for frequency | VERIFIED | 1006 bytes, 45-bar BarChart with custom Korean tooltip, fill="#3b82f6" |
| `frontend/src/components/dashboard/HotColdNumbers.tsx` | Hot/Cold LottoBall display | VERIFIED | 687 bytes, two rows of LottoBall components with Korean sub-labels |
| `frontend/src/components/dashboard/HeatmapGrid.tsx` | CSS Grid heatmap | VERIFIED | 3715 bytes, deviationToColor helper, 3x45 grid, red-blue scale, selected machine highlight, Korean legend |
| `frontend/src/components/dashboard/RatioDistribution.tsx` | Odd/even and high/low ratio charts | VERIFIED | 1835 bytes, side-by-side BarCharts, fill="#3b82f6" + fill="#8b5cf6" |
| `frontend/src/components/dashboard/RangeDistribution.tsx` | Zone distribution chart | VERIFIED | 1065 bytes, 5-zone BarChart with count+percentage tooltip |
| `frontend/src/components/dashboard/SumAcDistribution.tsx` | Sum + AC distribution charts | VERIFIED | 2269 bytes, 60/40 split layout, sum histogram + AC bar chart |
| `frontend/src/components/dashboard/StatisticsDashboard.tsx` | Container orchestrating 6 sections | VERIFIED | 2435 bytes, calls useStatistics + useHeatmapData, renders 6 ChartCard sections in correct order |
| `backend/app/schemas/statistics.py` | Pydantic schemas for heatmap | VERIFIED | 332 bytes, HeatmapRow(BaseModel) + HeatmapResponse(BaseModel) |
| `backend/app/services/statistics_service.py` | Heatmap deviation computation | VERIFIED | 1223 bytes, compute_heatmap_data returns 3 rows x 45 deviations |
| `backend/app/api/routes.py` (modified) | Heatmap endpoint | VERIFIED | GET /api/statistics/heatmap, response_model=HeatmapResponse, sync def, loader null-check |
| `frontend/src/lib/api.ts` (modified) | fetchHeatmapData function | VERIFIED | Fetches `${API_BASE}/statistics/heatmap`, error handling, returns HeatmapData |
| `frontend/src/App.tsx` (modified) | Dashboard integration | VERIFIED | Imports StatisticsDashboard, renders with border-t separator, "통계 분석" h2 header, machine={selectedMachine} |
| `frontend/package.json` (modified) | Recharts dependency | VERIFIED | "recharts": "^3.8.1" in dependencies |

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| App.tsx | StatisticsDashboard.tsx | `<StatisticsDashboard machine={selectedMachine}` | WIRED | Line 52, always rendered (not conditional on prediction) |
| StatisticsDashboard.tsx | useStatistics.ts | `useStatistics(data?.draws ?? [])` | WIRED | Line 27 |
| StatisticsDashboard.tsx | useHeatmapData.ts | `useHeatmapData()` | WIRED | Line 28 |
| StatisticsDashboard.tsx | FrequencyBarChart.tsx | `<FrequencyBarChart data={stats.frequencyData}` | WIRED | Line 46 |
| StatisticsDashboard.tsx | HotColdNumbers.tsx | `<HotColdNumbers hot={stats.hotNumbers} cold={stats.coldNumbers}` | WIRED | Line 50 |
| StatisticsDashboard.tsx | HeatmapGrid.tsx | `<HeatmapGrid data={heatmap.data?.rows ?? []}` | WIRED | Line 54-56 |
| StatisticsDashboard.tsx | RatioDistribution.tsx | `<RatioDistribution oddEven={stats.oddEvenDist} highLow={stats.highLowDist}` | WIRED | Line 61-64 |
| StatisticsDashboard.tsx | RangeDistribution.tsx | `<RangeDistribution data={stats.zoneDist}` | WIRED | Line 67 |
| StatisticsDashboard.tsx | SumAcDistribution.tsx | `<SumAcDistribution sumData={stats.sumDist} acData={stats.acDist}` | WIRED | Line 70-73 |
| useHeatmapData.ts | /api/statistics/heatmap | `fetchHeatmapData` in api.ts | WIRED | api.ts line 34: `fetch(${API_BASE}/statistics/heatmap)` |
| routes.py | statistics_service.py | `compute_heatmap_data(loader._by_machine)` | WIRED | routes.py line 101 |
| useStatistics.ts | types/statistics.ts | `import type` | WIRED | Lines 3-9 |

### Data-Flow Trace (Level 4)

| Artifact | Data Variable | Source | Produces Real Data | Status |
|----------|---------------|--------|--------------------|--------|
| StatisticsDashboard | data?.draws | fetchMachineData via useQuery | Yes -- fetches from `/api/data?machine=X`, backend filters from 417-record JSON | FLOWING |
| StatisticsDashboard | stats (8 fields) | useStatistics(draws) | Yes -- useMemo computations on real draws array, no hardcoded data | FLOWING |
| StatisticsDashboard | heatmap.data | useHeatmapData via useQuery | Yes -- fetches from `/api/statistics/heatmap`, backend computes from real data (134/136/147 draws) | FLOWING |
| HeatmapGrid | data (HeatmapRow[]) | props from StatisticsDashboard | Yes -- real deviation data from backend computation | FLOWING |
| FrequencyBarChart | data (NumberFrequency[]) | props from StatisticsDashboard | Yes -- 45-element array from useStatistics frequency computation | FLOWING |
| HotColdNumbers | hot, cold (number[]) | props from StatisticsDashboard | Yes -- derived from frequency sort in useStatistics | FLOWING |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| Backend heatmap returns 3x45 data | `uv run python -c "...compute_heatmap_data..."` | 3 rows (134/136/147 draws), 45 float deviations each | PASS |
| TypeScript compiles with zero errors | `npx tsc --noEmit` | No output (zero errors) | PASS |
| Frontend builds successfully | `npm run build` | Built in 164ms, 586.90 kB JS output | PASS |
| Recharts is installed | `package.json` contains recharts | "recharts": "^3.8.1" | PASS |
| All 6 commits exist in git | `git log --oneline` for 6 hashes | All 6 found with correct messages | PASS |

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|------------|-------------|--------|----------|
| DASH-01 | 06-02 | 호기별 번호 출현 빈도 바 차트 (1-45번) | SATISFIED | FrequencyBarChart.tsx renders 45-bar Recharts BarChart with useStatistics frequencyData |
| DASH-02 | 06-02 | 호기별 Hot/Cold 번호 상위 10개 | SATISFIED | HotColdNumbers.tsx renders top/bottom 10 LottoBall components from useStatistics hot/coldNumbers |
| DASH-03 | 06-01, 06-02 | 호기별 번호 편중 히트맵 (3x45 그리드) | SATISFIED | Backend compute_heatmap_data + HeatmapGrid.tsx CSS Grid with deviationToColor red-blue scale |
| DASH-04 | 06-03 | 호기별 홀짝/고저 비율 분포 차트 | SATISFIED | RatioDistribution.tsx side-by-side bar charts, 7 categories each, accent+violet fills |
| DASH-05 | 06-01, 06-03 | 호기별 번호 구간대 분포 차트 | SATISFIED | RangeDistribution.tsx 5-zone BarChart with count+percentage from useStatistics zoneDist |
| DASH-06 | 06-03 | 호기별 총합 범위 및 AC값 분포 | SATISFIED | SumAcDistribution.tsx 60/40 split with sum histogram and AC value bar chart |
| UI-02 | 06-02 | 하단 데이터 분석 대시보드 스타일 | SATISFIED | App.tsx border-t separator, "통계 분석" h2 header, ChartCard wrappers, space-y-6 layout |

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| (none) | - | - | - | No TODO/FIXME/placeholder/stub patterns found |

Note: `return null` in tooltip components (5 instances) are standard Recharts tooltip guard clauses, not stubs.

### Human Verification Required

### 1. Visual Chart Rendering

**Test:** Open http://localhost:5173, select a machine, verify all 6 chart sections render correctly
**Expected:** 6 ChartCard sections visible: frequency bar chart (45 blue bars), hot/cold LottoBall rows (10 each), heatmap grid (3x45 colored cells with legend), odd/even + high/low side-by-side charts, 5-zone range bars, sum histogram + AC bars
**Why human:** Visual rendering, chart layout proportions, color correctness, and responsive behavior cannot be verified programmatically

### 2. Machine Switching Updates All Charts

**Test:** Select different machines (1/2/3) and observe chart data changes
**Expected:** All 6 charts update with different data for each machine; heatmap highlights the selected machine row
**Why human:** Interactive behavior requires browser observation

### 3. Tooltip Interactions

**Test:** Hover over bars in frequency chart, ratio charts, range chart, and sum/AC charts
**Expected:** Tooltips appear with Korean labels: "{N}번: {M}회", "{비율}: {M}회", "{구간}: {M}회 ({P}%)", "AC {N}: {M}회"
**Why human:** Hover interactions require browser testing

### 4. Dashboard Visual Separation

**Test:** Verify the "통계 분석" section is visually distinct from the prediction area above
**Expected:** Clear border-t separator line between prediction results and dashboard, section header "통계 분석" is prominent, chart cards have consistent styling
**Why human:** Visual distinction and aesthetic judgment require human review

### Gaps Summary

No gaps found. All 5 observable truths are verified. All 17 artifacts exist, are substantive (not stubs), and are fully wired. All 12 key links are connected. All 6 data flows produce real data from the 417-record dataset. All 7 requirements (DASH-01 through DASH-06, UI-02) are satisfied. No anti-patterns detected. TypeScript compiles cleanly. Build succeeds. All 6 commits verified in git history.

---

_Verified: 2026-03-27T04:45:00Z_
_Verifier: Claude (gsd-verifier)_
