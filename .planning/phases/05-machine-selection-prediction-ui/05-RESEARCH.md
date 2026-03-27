# Phase 5: Machine Selection & Prediction UI - Research

**Researched:** 2026-03-27
**Domain:** React frontend -- machine selection cards, API integration, prediction results display
**Confidence:** HIGH

## Summary

Phase 5 transforms the placeholder `App.tsx` (currently a health-check card) into the primary user-facing UI: three machine selection cards, a "predict" button, and 25-game results organized by strategy. The backend APIs are fully built (POST /api/predict, GET /api/data), so this phase is purely frontend work -- React components, API integration, and styling with existing Tailwind v4 design tokens.

The key technical decisions are straightforward: install `@tanstack/react-query` (v5.95) for server state management, create a component hierarchy (MachineCard, LottoBall, StrategySection, GameRow), and wire the 5-strategy prediction calls to the existing POST /api/predict endpoint. The lotto ball color coding follows Dong-Haeng Bokgwon (Korean lottery commission) official colors which are locked in CONTEXT.md.

**Primary recommendation:** Use TanStack React Query v5 with custom hooks (useMachineInfo, usePrediction) wrapping native fetch. Build small, composable components. No routing needed -- this is a single-page layout.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- **D-01:** 호기 번호 카드 3개 가로 나열 -- 각 카드에 호기 번호 + 추첨 횟수 + 최근 회차 표시
- **D-02:** 선택 시 카드 테두리 색상 변경 (blue-500 액센트)
- **D-03:** 호기 정보(추첨 횟수, 최근 회차)는 백엔드 API에서 가져옴
- **D-04:** 전략별 섹션으로 수직 스크롤 -- 전략명 헤더 + 5게임 가로 나열
- **D-05:** 5개 섹션: Frequency(빈도) -> Pattern(패턴) -> Range(구간) -> Balance(밸런스) -> Composite(종합)
- **D-06:** 로또공 모양 원형 배지 + 동행복권 색상 코딩
  - 1-10: 노랑 (#ffc107)
  - 11-20: 파랑 (#2196f3)
  - 21-30: 빨강 (#f44336)
  - 31-40: 회색 (#9e9e9e)
  - 41-45: 초록 (#4caf50)
- **D-07:** 번호는 2자리 패딩 (03, 07 등)
- **D-08:** 전략명은 영어+한국어 병기 -- Frequency (빈도), Pattern (패턴), Range (구간), Balance (밸런스), Composite (종합)
- **D-09:** UI 전체 한국어 -- "호기 선택", "번호 예측", "예측 결과" 등
- **D-10:** 페이지 제목: "로또 예측기" (한국어로 변경)

### Claude's Discretion
- React 컴포넌트 분리 구조 (MachineCard, GameRow, LottoBall 등)
- API 호출 hooks 설계 (usePrediction 등)
- 로딩 상태 표시 방식
- "번호 예측" 버튼 위치와 스타일

### Deferred Ideas (OUT OF SCOPE)
None -- discussion stayed within phase scope
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| MACH-01 | 사용자가 1호기/2호기/3호기 중 하나를 선택할 수 있다 | MachineCard component with selectedMachine state; three cards in a row with click handler |
| MACH-02 | 선택된 호기에 따라 모든 분석과 예측이 해당 호기 데이터만 사용한다 | selectedMachine passed as parameter to POST /api/predict request body |
| MACH-03 | 호기 선택 시 해당 호기의 총 추첨 횟수와 최근 추첨일이 표시된다 | GET /api/data?machine=X returns total_draws and draws list (latest round from last element) |
| UI-01 | 상단 영역은 깔끔 모던 스타일 (호기 선택 + 예측 결과 카드) | Tailwind v4 utility classes with existing design tokens (surface, card, accent, border) |
</phase_requirements>

## Standard Stack

### Core (already installed)
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| React | ^19.2.4 | UI framework | Already installed, project foundation |
| TypeScript | ~5.9.3 | Type safety | Already installed as devDep |
| Tailwind CSS | ^4.2.2 | Styling | Already installed with @tailwindcss/vite plugin |
| Vite | ^8.0.1 | Build tool | Already installed and configured |

### To Install
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| @tanstack/react-query | ^5.95.2 | Server state / data fetching | De facto standard for React data fetching. Handles caching, loading/error states, background refetch. Eliminates manual useState+useEffect fetch pattern. Listed in project CLAUDE.md stack. |

### NOT Needed for Phase 5
| Library | Reason |
|---------|--------|
| React Router | Single-page layout, no routes needed in Phase 5 |
| Recharts | Charts are Phase 6 (Dashboard) |
| Axios | Native fetch + TanStack Query is sufficient per project decision |
| Any state management (Redux/Zustand) | TanStack Query manages server state; React useState for local UI state (selectedMachine) |

**Installation:**
```bash
cd frontend && npm install @tanstack/react-query
```

**Version verification:** `@tanstack/react-query` latest is 5.95.2 (verified via npm view on 2026-03-27).

## Architecture Patterns

### Recommended Project Structure
```
frontend/src/
├── components/
│   ├── MachineCard.tsx      # Single machine card (호기 번호 + 추첨 횟수 + 최근 회차)
│   ├── MachineSelector.tsx  # Three cards container with selection state
│   ├── LottoBall.tsx        # Single lotto number circle with color coding
│   ├── GameRow.tsx          # One game = 6 LottoBalls in a row
│   ├── StrategySection.tsx  # Strategy header + 5 GameRows
│   └── PredictionResults.tsx # All 5 strategy sections vertically stacked
├── hooks/
│   ├── useMachineInfo.ts    # GET /api/data?machine=X -> extract metadata
│   └── usePrediction.ts     # POST /api/predict for all 5 strategies
├── lib/
│   └── api.ts               # API base URL, fetch wrappers, types
├── types/
│   └── lottery.ts           # TypeScript interfaces matching backend schemas
├── App.tsx                  # Main layout: MachineSelector + PredictionResults
├── main.tsx                 # Entry point (add QueryClientProvider)
├── index.css                # Existing Tailwind @theme tokens + new lotto colors
└── vite-env.d.ts            # Existing
```

### Pattern 1: TanStack Query Provider Setup
**What:** Wrap app in QueryClientProvider at the entry point
**When to use:** Required for all useQuery/useMutation hooks to work
**Example:**
```typescript
// main.tsx
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 min -- data is static JSON, rarely changes
      retry: 1,
    },
  },
})

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <QueryClientProvider client={queryClient}>
      <App />
    </QueryClientProvider>
  </StrictMode>,
)
```

### Pattern 2: Custom Hook for Machine Info (useQuery)
**What:** Lightweight hook to get machine metadata from the existing GET /api/data endpoint
**When to use:** MachineCard needs total_draws and latest round_number
**Example:**
```typescript
// hooks/useMachineInfo.ts
import { useQuery } from '@tanstack/react-query'
import { API_BASE } from '../lib/api'

interface MachineInfo {
  machine: string
  totalDraws: number
  latestRound: number
}

export function useMachineInfo(machine: string) {
  return useQuery<MachineInfo>({
    queryKey: ['machineInfo', machine],
    queryFn: async () => {
      const res = await fetch(`${API_BASE}/data?machine=${encodeURIComponent(machine)}`)
      if (!res.ok) throw new Error(`HTTP ${res.status}`)
      const data = await res.json()
      return {
        machine: data.machine,
        totalDraws: data.total_draws,
        latestRound: data.draws.length > 0
          ? data.draws[data.draws.length - 1].round_number
          : 0,
      }
    },
    staleTime: Infinity, // Static data, never refetch
  })
}
```

### Pattern 3: useMutation for Prediction (POST)
**What:** useMutation for triggering prediction -- POST is a side-effect, not a query
**When to use:** "번호 예측" button triggers 5 parallel prediction calls
**Example:**
```typescript
// hooks/usePrediction.ts
import { useMutation } from '@tanstack/react-query'
import { API_BASE } from '../lib/api'

const STRATEGIES = ['frequency', 'pattern', 'range', 'balance', 'composite'] as const

interface PredictResponse {
  games: number[][]
  strategy: string
  machine: string
}

export function usePrediction() {
  return useMutation({
    mutationFn: async (machine: string): Promise<PredictResponse[]> => {
      const results = await Promise.all(
        STRATEGIES.map(strategy =>
          fetch(`${API_BASE}/predict`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ machine, strategy }),
          }).then(res => {
            if (!res.ok) throw new Error(`HTTP ${res.status}`)
            return res.json()
          })
        )
      )
      return results
    },
  })
}
```

### Pattern 4: Lotto Ball Color Mapping
**What:** Pure function mapping number to Dong-Haeng Bokgwon official color
**When to use:** LottoBall component uses this for background color
**Example:**
```typescript
// lib/lottoBallColor.ts
export function getLottoBallColor(num: number): string {
  if (num >= 1 && num <= 10) return '#ffc107'   // 노랑
  if (num >= 11 && num <= 20) return '#2196f3'  // 파랑
  if (num >= 21 && num <= 30) return '#f44336'  // 빨강
  if (num >= 31 && num <= 40) return '#9e9e9e'  // 회색
  if (num >= 41 && num <= 45) return '#4caf50'  // 초록
  return '#9e9e9e' // fallback
}

export function formatNumber(num: number): string {
  return num.toString().padStart(2, '0')
}
```

### Anti-Patterns to Avoid
- **useEffect+useState for fetching:** Do NOT replicate the current App.tsx pattern (raw fetch in useEffect). Use TanStack Query hooks instead -- they handle loading, error, caching automatically.
- **Fetching all draws just for metadata:** The GET /api/data endpoint returns the full draws array. For machine info (card display), extract only total_draws and the last draw's round_number. Consider caching aggressively (staleTime: Infinity) since this data is static.
- **Inline styles for lotto ball colors:** Define the 5 lotto ball colors as Tailwind @theme custom properties or use inline style only for the background-color (since these are dynamic per-ball). Tailwind cannot generate classes for arbitrary hex colors at build time, so inline `style={{ backgroundColor }}` is correct here.
- **Sequential API calls:** The 5 strategy predictions are independent. Use Promise.all to call them in parallel, not sequentially.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Data fetching with loading/error states | Custom useState+useEffect+try/catch pattern | TanStack React Query useQuery/useMutation | Handles caching, deduplication, retry, loading/error states, background refetch. The current App.tsx pattern would become unmanageable with 3 machine info queries + 5 prediction mutations. |
| Request deduplication | Manual ref tracking | TanStack Query queryKey deduplication | If multiple components request same machine info, Query deduplicates automatically |
| Number formatting | Manual string concatenation | `String.padStart(2, '0')` | Native JS, no library needed, but use a utility function to avoid repetition |

**Key insight:** The current App.tsx has 20 lines of manual fetch+state management for a single endpoint. Phase 5 needs 3 machine info queries + 5 parallel prediction calls. TanStack Query eliminates the complexity explosion.

## Common Pitfalls

### Pitfall 1: GET /api/data Returns Full Draws Array
**What goes wrong:** Fetching all draws (134-147 LotteryDraw objects with numbers, ratios, etc.) just to display total_draws and latest round on the machine card. This is ~50KB per machine.
**Why it happens:** The only existing endpoint that provides machine metadata is GET /api/data, which returns everything.
**How to avoid:** Two options: (a) Accept the overhead -- data is static and cached with staleTime: Infinity, so it's fetched once per session. 3 requests x ~50KB = ~150KB total, acceptable for localhost. (b) Add a lightweight GET /api/machines endpoint that returns just `[{machine, total_draws, latest_round}]` in a single call. Option (a) is simpler and sufficient for localhost.
**Recommendation:** Use option (a) -- fetch via GET /api/data for each machine and extract metadata. The overhead is negligible for localhost, and it avoids a backend change.

### Pitfall 2: Lotto Ball Color as Tailwind Classes Won't Work
**What goes wrong:** Trying to use `bg-[#ffc107]` arbitrary value classes in Tailwind -- these work in dev but may be purged in production builds if not used elsewhere.
**Why it happens:** Tailwind JIT generates classes found in source files, but dynamic string concatenation (`bg-[${color}]`) is never detected.
**How to avoid:** Use inline `style={{ backgroundColor: getLottoBallColor(num) }}` for the ball color. Use Tailwind classes for everything else (size, shape, text color, font weight).
**Warning signs:** Balls appearing with no background color in production build.

### Pitfall 3: Korean Text Encoding
**What goes wrong:** API request body containing Korean strings (e.g., "1호기") gets mangled.
**Why it happens:** Missing Content-Type header or incorrect encoding.
**How to avoid:** Always set `headers: { 'Content-Type': 'application/json' }` on POST requests. JSON.stringify handles Korean UTF-8 correctly. The fetch API defaults to UTF-8 for JSON bodies.
**Warning signs:** 400 errors from backend with "Unknown machine" message.

### Pitfall 4: Multiple Rapid "번호 예측" Clicks
**What goes wrong:** User clicks predict button multiple times while loading, triggering duplicate API calls.
**Why it happens:** No debounce or loading-state-based button disable.
**How to avoid:** Disable the predict button when `mutation.isPending` is true. Show a loading spinner or text change ("예측 중...") during the mutation.
**Warning signs:** Multiple identical prediction results appearing, UI flickering.

### Pitfall 5: TypeScript Strict Mode + verbatimModuleSyntax
**What goes wrong:** Type-only imports/exports cause build errors.
**Why it happens:** tsconfig.app.json has `"verbatimModuleSyntax": true` and `"erasableSyntaxOnly": true`. This means you must use `import type { X }` for type-only imports.
**How to avoid:** Always use `import type` for interfaces/types that are only used for type checking. Use regular `import` for values that exist at runtime.
**Warning signs:** `TS1286: ESM syntax is not allowed in a CommonJS module when 'verbatimModuleSyntax' is enabled` or similar errors.

## Code Examples

### Machine Card Component Pattern
```typescript
// components/MachineCard.tsx
interface MachineCardProps {
  machineId: string       // "1호기", "2호기", "3호기"
  totalDraws: number
  latestRound: number
  isSelected: boolean
  onSelect: () => void
  isLoading: boolean
}

export function MachineCard({
  machineId, totalDraws, latestRound, isSelected, onSelect, isLoading
}: MachineCardProps) {
  return (
    <button
      onClick={onSelect}
      className={`
        flex-1 p-4 rounded-xl border-2 bg-card transition-colors cursor-pointer
        ${isSelected ? 'border-accent shadow-md' : 'border-border hover:border-accent/50'}
      `}
    >
      <p className="text-2xl font-bold text-text-primary">{machineId}</p>
      {isLoading ? (
        <p className="text-sm text-text-secondary mt-2">로딩 중...</p>
      ) : (
        <>
          <p className="text-sm text-text-secondary mt-2">
            추첨 횟수: {totalDraws}회
          </p>
          <p className="text-sm text-text-secondary">
            최근 회차: {latestRound}회
          </p>
        </>
      )}
    </button>
  )
}
```

### Lotto Ball Component Pattern
```typescript
// components/LottoBall.tsx
import { getLottoBallColor, formatNumber } from '../lib/lottoBallColor'

interface LottoBallProps {
  number: number
}

export function LottoBall({ number }: LottoBallProps) {
  return (
    <span
      className="inline-flex items-center justify-center w-10 h-10 rounded-full text-sm font-bold text-white shadow-sm"
      style={{ backgroundColor: getLottoBallColor(number) }}
    >
      {formatNumber(number)}
    </span>
  )
}
```

### Strategy Section Pattern
```typescript
// components/StrategySection.tsx
import { GameRow } from './GameRow'

const STRATEGY_LABELS: Record<string, string> = {
  frequency: 'Frequency (빈도)',
  pattern: 'Pattern (패턴)',
  range: 'Range (구간)',
  balance: 'Balance (밸런스)',
  composite: 'Composite (종합)',
}

interface StrategySectionProps {
  strategy: string
  games: number[][]
}

export function StrategySection({ strategy, games }: StrategySectionProps) {
  return (
    <section className="bg-card rounded-xl border border-border p-4">
      <h3 className="text-lg font-bold text-text-primary mb-3">
        {STRATEGY_LABELS[strategy] ?? strategy}
      </h3>
      <div className="space-y-2">
        {games.map((game, i) => (
          <GameRow key={i} numbers={game} gameIndex={i + 1} />
        ))}
      </div>
    </section>
  )
}
```

### App Layout Pattern
```typescript
// App.tsx (overall structure)
export default function App() {
  const [selectedMachine, setSelectedMachine] = useState<string | null>(null)
  const prediction = usePrediction()

  const handlePredict = () => {
    if (selectedMachine) {
      prediction.mutate(selectedMachine)
    }
  }

  return (
    <div className="min-h-screen bg-surface">
      <div className="max-w-4xl mx-auto px-4 py-8">
        {/* Header */}
        <h1 className="text-2xl font-bold text-text-primary mb-6">로또 예측기</h1>

        {/* Machine Selection */}
        <MachineSelector
          selectedMachine={selectedMachine}
          onSelectMachine={setSelectedMachine}
        />

        {/* Predict Button */}
        <button
          onClick={handlePredict}
          disabled={!selectedMachine || prediction.isPending}
          className="..."
        >
          {prediction.isPending ? '예측 중...' : '번호 예측'}
        </button>

        {/* Results */}
        {prediction.data && (
          <PredictionResults results={prediction.data} />
        )}
      </div>
    </div>
  )
}
```

## Existing API Contracts

Verified from backend source code:

### GET /api/data?machine={machine}
- **Request:** Query parameter `machine` = "1호기" | "2호기" | "3호기"
- **Response (MachineDataResponse):**
```json
{
  "machine": "1호기",
  "total_draws": 134,
  "draws": [
    {
      "round_number": 800,
      "machine": "1호기",
      "numbers": [3, 7, 15, 23, 31, 42],
      "odd_even_ratio": "3:3",
      "high_low_ratio": "3:3",
      "ac_value": 9,
      "tail_sum": 21,
      "total_sum": 121
    }
  ]
}
```

### POST /api/predict
- **Request body:** `{"machine": "1호기", "strategy": "frequency"}`
- **Valid strategies:** "frequency", "pattern", "range", "balance", "composite"
- **Response (PredictResponse):**
```json
{
  "games": [[3, 7, 15, 23, 31, 42], ...],
  "strategy": "frequency",
  "machine": "1호기"
}
```
- **Error:** 400 for invalid machine/strategy, 503 if data not loaded

### Machine Data (from new_res.json)
| Machine | Total Draws | Latest Round |
|---------|-------------|--------------|
| 1호기 | 134 | 1209 |
| 2호기 | 136 | 1213 |
| 3호기 | 147 | 1216 |

## Design Token Integration

### Existing Tokens (from index.css @theme)
```css
--color-surface: #f8fafc;     /* Page background */
--color-card: #ffffff;         /* Card surfaces */
--color-accent: #3b82f6;       /* blue-500 -- selected card border */
--color-destructive: #ef4444;  /* Error states */
--color-text-primary: #0f172a; /* Headings, body */
--color-text-secondary: #64748b; /* Labels, metadata */
--color-border: #e2e8f0;       /* Card borders */
--color-success: #22c55e;      /* Success states */
```

### New Tokens Needed (lotto ball colors)
These 5 colors are NOT Tailwind design tokens -- they are data-driven colors that vary per ball. Use inline `style={{ backgroundColor }}` rather than adding to @theme, since they map to dynamic data values, not design system roles.

```typescript
// Lotto ball colors (Dong-Haeng Bokgwon official)
const LOTTO_COLORS = {
  yellow: '#ffc107',  // 1-10
  blue: '#2196f3',    // 11-20
  red: '#f44336',     // 21-30
  gray: '#9e9e9e',    // 31-40
  green: '#4caf50',   // 41-45
}
```

### Spacing (from UI-SPEC)
- Card padding: 16px (md / p-4) or 24px (lg / p-6)
- Section gaps: 24px (lg / space-y-6)
- Element gaps: 8px (sm / space-y-2 or gap-2)
- Ball gaps: 4px-8px (xs-sm / gap-1 or gap-2)

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| useEffect+fetch+useState | TanStack Query useQuery/useMutation | v5 stable (Oct 2023, still current) | Eliminates 60-70% of data fetching boilerplate. Object-based API: `useQuery({ queryKey, queryFn })` |
| Tailwind config file (v3) | Tailwind @theme directive (v4) | v4 (Jan 2025) | No tailwind.config.js needed. Design tokens in CSS. Already set up in this project. |
| React class components | Functional components + hooks | React 16.8+ (2019) | Project already uses functional components |

**Deprecated/outdated:**
- useEffect for data fetching: Not deprecated per se, but TanStack Query is the standard pattern for React 19 apps with server data
- Tailwind v3 config: Project uses v4 @theme, do not create a tailwind.config.js

## Open Questions

1. **Machine info endpoint efficiency**
   - What we know: GET /api/data returns full draws array (~50KB per machine). We only need total_draws and latest round for the card display.
   - What's unclear: Whether adding a lightweight /api/machines summary endpoint is worth the backend change.
   - Recommendation: Use GET /api/data as-is with aggressive caching (staleTime: Infinity). The data is fetched once per session, and ~150KB total is negligible for localhost. This avoids a backend code change in a frontend-focused phase.

2. **"번호 예측" button placement**
   - What we know: D-09 says the button text is "번호 예측". Position is Claude's discretion.
   - Recommendation: Place directly below the machine selector cards, centered, with accent color background. Disabled (grayed out) when no machine is selected.

3. **Loading state design**
   - What we know: Loading state design is Claude's discretion.
   - Recommendation: Simple approach -- button text changes to "예측 중..." with a subtle pulse animation (Tailwind `animate-pulse`). No full-page spinner (that's Phase 8 UI-04 polish scope).

## Project Constraints (from CLAUDE.md)

- **Stack:** React 19, Vite 8, Tailwind CSS v4, TypeScript, TanStack React Query v5
- **Fetch:** Use native fetch, NOT axios (per project decision)
- **State:** TanStack Query for server state + React useState for local UI state. No Redux/Zustand.
- **Styling:** Tailwind v4 utility-first with @theme tokens. No CSS Modules, no styled-components.
- **No component library:** No shadcn, no Material UI. Custom components with Tailwind.
- **Workflow:** Follow GSD workflow -- no direct repo edits outside GSD commands.
- **Read before Write/Edit:** Always use Read tool before modifying files.
- **Absolute paths only** in tool operations.

## Sources

### Primary (HIGH confidence)
- Backend source code: `backend/app/api/routes.py`, `backend/app/schemas/lottery.py` -- verified API contracts directly
- Backend source code: `backend/app/services/data_loader.py` -- verified data structure and machine filtering
- Frontend source code: `frontend/package.json`, `frontend/src/App.tsx` -- verified current state
- `new_res.json` -- verified machine statistics (134/136/147 draws)
- `.planning/phases/05-machine-selection-prediction-ui/05-CONTEXT.md` -- all locked decisions
- `.planning/phases/01-foundation-data-layer/01-UI-SPEC.md` -- design tokens, spacing, typography

### Secondary (MEDIUM confidence)
- [TanStack Query v5 Official Docs - useQuery](https://tanstack.com/query/v5/docs/framework/react/reference/useQuery) -- API reference
- [TanStack Query v5 Official Docs - useMutation](https://tanstack.com/query/v5/docs/react/reference/useMutation) -- mutation patterns
- [TanStack Query v5 Migration Guide](https://tanstack.com/query/v5/docs/framework/react/guides/migrating-to-v5) -- v5 object-based API
- npm registry: `@tanstack/react-query` version 5.95.2 confirmed latest

### Tertiary (LOW confidence)
- None

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH -- all libraries verified in package.json and npm registry, project CLAUDE.md specifies exact stack
- Architecture: HIGH -- component patterns follow standard React + TanStack Query conventions, backend APIs verified from source
- Pitfalls: HIGH -- identified from direct source code analysis (API response sizes, TypeScript config, Tailwind JIT behavior)

**Research date:** 2026-03-27
**Valid until:** 2026-04-27 (30 days -- stable stack, no fast-moving dependencies)
