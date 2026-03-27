# Phase 7: Prediction History & Review - Research

**Researched:** 2026-03-27
**Domain:** localStorage persistence, comparison logic, Claude API integration (backend proxy), accordion UI
**Confidence:** HIGH

## Summary

Phase 7 adds prediction history management with four distinct capabilities: (1) saving prediction results to localStorage with round number and machine metadata, (2) entering actual winning numbers and computing automatic match analysis, (3) generating AI-powered reflection memos via Claude API through the FastAPI backend, and (4) feeding those reflections back into future predictions for the same machine.

The phase is frontend-heavy (localStorage, comparison UI, history table, accordion) with a single backend addition (POST /api/reflect endpoint calling the Anthropic Python SDK). The project already uses TanStack React Query for server state and native fetch for API calls -- the AI reflection endpoint fits cleanly into this pattern using `useMutation`. The localStorage layer is entirely new; no persistence exists in the current codebase.

**Primary recommendation:** Build a typed `useLocalStorage<T>` hook with lazy initialization for React 19 safety. Use the `anthropic` Python SDK (v0.86.0) with `claude-haiku-4-5` model for cost-effective reflection generation through a sync FastAPI endpoint. Keep all comparison logic in pure TypeScript utility functions (no backend needed for match counting).

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- **D-01:** localStorage with JSON storage -- no database
- **D-02:** "Save prediction" button click to save -- not automatic, user selects which results to keep
- **D-03:** Round number input required on save -- serves as matching key for winning number comparison
- **D-04:** Storage schema: `{ roundNumber, machine, date, predictions: [{ strategy, games: number[][] }], actualNumbers?: number[], comparison?: {...}, aiReflection?: string }`
- **D-05:** 6 number input fields (1-45 range) -- auto-advance to next field, input validation
- **D-06:** Comparison results in table format -- per-strategy 5-game match counts/matched numbers with strategy hit rate summary
- **D-07:** Matched numbers displayed as plain numbers in table cells (no LottoBall component reuse)
- **D-08:** History list as table -- columns: round | machine | date | best match | reflection memo status
- **D-09:** Table row click expands accordion -- shows all 25 games + comparison + reflection in-place
- **D-10:** Newest-first sort (descending), no pagination (localStorage data is limited)
- **D-11:** Reflection memos are AI-generated (Claude API), NOT user-written
- **D-12:** AI reflection content: overestimated numbers, missed number patterns, per-strategy performance analysis, specific adjustment suggestions for next prediction
- **D-13:** Next prediction feeds same-machine reflections into Claude API prompt for weight adjustment suggestions, applies to prediction parameters
- **D-14:** Only same-machine reflections are fed back (other machines ignored)
- **D-15:** Claude API failure falls back to default prediction logic (no AI adjustment)
- **D-16:** Strategy performance summary section -- average hit rate, best hit record, total prediction count per strategy in table
- **D-17:** Failure analysis: auto-derived from comparison -- missed numbers (actually won but not predicted) and overestimated numbers (frequently predicted but never drawn), shown as number lists

### Claude's Discretion
- localStorage key naming convention
- Comparison table styling details (colors, highlights)
- Accordion animation presence
- AI reflection prompt design details
- Optional chart inclusion in strategy performance report
- Save button position and design

### Deferred Ideas (OUT OF SCOPE)
None -- discussion stayed within phase scope
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| HIST-01 | Save 25 games with round/machine/strategy/date to local storage | localStorage hook + typed schema (D-04), save button with round number input (D-02, D-03) |
| HIST-02 | Enter actual winning numbers, auto-compare with predictions (match count, per-strategy hit rate) | 6-field number input (D-05), pure TS comparison utility, table display (D-06) |
| HIST-03 | Strategy performance report (which strategy matched best) | Aggregate across all history entries, table format (D-16) |
| HIST-04 | Failed prediction analysis -- missed and overestimated numbers | Derived from comparison data (D-17), pure TS utility |
| HIST-05 | Reflection memo generation (reinterpreted: AI auto-generates via Claude API, NOT user-written) | Anthropic SDK v0.86.0, claude-haiku-4-5 model, POST /api/reflect endpoint (D-11, D-12) |
| HIST-06 | Feed reflections into next prediction (reinterpreted: Claude API prompt includes past reflections for weight adjustment) | Same-machine filter (D-14), fallback on API failure (D-15), modified predict endpoint (D-13) |
| HIST-07 | History list view (round-by-round timeline with accordion detail) | Table with accordion expand (D-08, D-09, D-10) |
</phase_requirements>

## Standard Stack

### Core (New Dependencies)
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| anthropic | ^0.86.0 | Claude API Python SDK | Official Anthropic SDK. Sync client for FastAPI sync endpoints. Required for AI reflection generation (HIST-05, HIST-06). |

### Already Installed (Reuse)
| Library | Version | Purpose | Reuse For |
|---------|---------|---------|-----------|
| @tanstack/react-query | ^5.95.2 | Server state | `useMutation` for AI reflection API call |
| React | ^19.2.4 | UI framework | All new components |
| Tailwind CSS | ^4.2.2 | Styling | Table, accordion, input field styling |
| FastAPI | ^0.135.2 | Backend API | New POST /api/reflect endpoint |
| Pydantic | ^2.12.5 | Schema validation | Request/response models for reflect endpoint |

### No New Frontend Dependencies
The phase requires NO new npm packages. localStorage is a browser API. Comparison logic is pure TypeScript. Accordion behavior uses native HTML details/summary or React state toggle. All needed libraries are already installed.

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Raw localStorage | usehooks-ts useLocalStorage | Adds a dependency for a single hook. Custom hook is <30 lines and matches project conventions. |
| claude-haiku-4-5 | claude-sonnet-4-6 | 3x more expensive ($3/$15 vs $1/$5 per MTok). Haiku is sufficient for structured reflection generation. |
| Sync Anthropic client | Async Anthropic client | Project pattern uses sync def for CPU/IO-bound endpoints. Async adds complexity for a single API call. |

**Installation:**
```bash
# Backend only -- add anthropic SDK
cd backend && uv add anthropic
```

## Architecture Patterns

### Recommended Project Structure
```
frontend/src/
  components/
    history/
      HistorySection.tsx         # Container: orchestrates history UI
      SavePredictionButton.tsx   # Save button + round number input modal/inline
      WinningNumberInput.tsx     # 6-field number input with auto-advance
      ComparisonTable.tsx        # Per-strategy match results table
      HistoryTable.tsx           # History list table with accordion rows
      HistoryRow.tsx             # Single expandable row
      StrategyPerformance.tsx    # Aggregate performance report
      FailureAnalysis.tsx        # Missed/overestimated numbers display
      AiReflection.tsx           # AI reflection memo display
  hooks/
    useHistoryStorage.ts         # localStorage CRUD hook
    useComparison.ts             # Comparison logic hook (pure computation)
    useReflection.ts             # AI reflection mutation hook
  lib/
    comparison.ts                # Pure comparison utility functions
    historyStorage.ts            # localStorage adapter (typed, versioned)
  types/
    history.ts                   # History-specific TypeScript types

backend/app/
  schemas/
    reflection.py                # Pydantic models for reflect endpoint
  services/
    reflection_service.py        # Claude API integration logic
  api/
    routes.py                    # Add POST /api/reflect route
  config.py                      # Add ANTHROPIC_API_KEY setting
```

### Pattern 1: Typed localStorage Adapter
**What:** A module that wraps localStorage with JSON parse/stringify, TypeScript generics, and error handling.
**When to use:** All localStorage read/write operations.
**Example:**
```typescript
// frontend/src/lib/historyStorage.ts
const STORAGE_KEY = 'lottery-prediction-history';

export type SavedPrediction = {
  id: string;                    // crypto.randomUUID()
  roundNumber: number;
  machine: string;
  date: string;                  // ISO date string
  predictions: {
    strategy: string;
    games: number[][];
  }[];
  actualNumbers?: number[];
  comparison?: ComparisonResult;
  aiReflection?: string;
};

export function loadHistory(): SavedPrediction[] {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    return raw ? (JSON.parse(raw) as SavedPrediction[]) : [];
  } catch {
    return [];
  }
}

export function saveHistory(entries: SavedPrediction[]): void {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(entries));
}
```

### Pattern 2: React 19-Safe useLocalStorage Hook
**What:** A custom hook that wraps the storage adapter with React state, using lazy initialization to avoid render-time side effects.
**When to use:** Components that need reactive localStorage data.
**Example:**
```typescript
// frontend/src/hooks/useHistoryStorage.ts
import { useState, useCallback } from 'react';
import { loadHistory, saveHistory, type SavedPrediction } from '../lib/historyStorage';

export function useHistoryStorage() {
  // Lazy initialization -- function form avoids localStorage access during render
  const [entries, setEntries] = useState<SavedPrediction[]>(() => loadHistory());

  const addEntry = useCallback((entry: SavedPrediction) => {
    setEntries(prev => {
      const next = [entry, ...prev]; // newest first
      saveHistory(next);
      return next;
    });
  }, []);

  const updateEntry = useCallback((id: string, patch: Partial<SavedPrediction>) => {
    setEntries(prev => {
      const next = prev.map(e => e.id === id ? { ...e, ...patch } : e);
      saveHistory(next);
      return next;
    });
  }, []);

  return { entries, addEntry, updateEntry };
}
```

### Pattern 3: Pure Comparison Utility
**What:** Stateless functions that compute match results between predicted and actual numbers.
**When to use:** When user submits actual winning numbers.
**Example:**
```typescript
// frontend/src/lib/comparison.ts
export type GameComparison = {
  strategy: string;
  gameIndex: number;
  predicted: number[];
  matchedNumbers: number[];
  matchCount: number;
};

export type ComparisonResult = {
  games: GameComparison[];
  strategyHitRates: { strategy: string; avgMatches: number; bestMatch: number }[];
  missedNumbers: number[];      // in actual but rarely predicted
  overestimatedNumbers: number[]; // frequently predicted but not in actual
};

export function comparePredictions(
  predictions: { strategy: string; games: number[][] }[],
  actualNumbers: number[],
): ComparisonResult {
  const games: GameComparison[] = [];
  for (const pred of predictions) {
    for (let i = 0; i < pred.games.length; i++) {
      const matched = pred.games[i].filter(n => actualNumbers.includes(n));
      games.push({
        strategy: pred.strategy,
        gameIndex: i + 1,
        predicted: pred.games[i],
        matchedNumbers: matched,
        matchCount: matched.length,
      });
    }
  }
  // ... compute strategyHitRates, missedNumbers, overestimatedNumbers
  return { games, strategyHitRates, missedNumbers, overestimatedNumbers };
}
```

### Pattern 4: Backend AI Reflection Endpoint
**What:** A sync FastAPI endpoint that calls the Anthropic SDK to generate reflection memos.
**When to use:** After comparison is complete, user triggers AI reflection generation.
**Example:**
```python
# backend/app/services/reflection_service.py
import anthropic
from app.config import settings

def generate_reflection(
    machine: str,
    round_number: int,
    comparison_data: dict,
    past_reflections: list[str] | None = None,
) -> str:
    """Generate AI reflection memo from comparison results."""
    client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)

    prompt = f"""당신은 로또 예측 분석가입니다. 다음 예측 결과를 분석하고 반성 메모를 생성하세요.

호기: {machine}
회차: {round_number}
비교 결과: {comparison_data}

다음 항목을 포함하여 분석하세요:
1. 과대평가한 번호 (많이 예측했지만 당첨되지 않은 번호)
2. 누락한 번호 패턴 (당첨되었지만 예측하지 못한 번호의 특성)
3. 전략별 성과 분석
4. 다음 예측을 위한 구체적 조정 제안"""

    if past_reflections:
        prompt += f"\n\n과거 반성 메모 참고:\n" + "\n---\n".join(past_reflections)

    message = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text
```

### Pattern 5: Accordion Row with React State
**What:** Table row that expands to show detail on click, using conditional rendering.
**When to use:** History table rows (D-09).
**Example:**
```typescript
// Simple accordion without external dependencies
function HistoryRow({ entry }: { entry: SavedPrediction }) {
  const [expanded, setExpanded] = useState(false);
  return (
    <>
      <tr onClick={() => setExpanded(!expanded)} className="cursor-pointer hover:bg-surface">
        <td>{entry.roundNumber}</td>
        <td>{entry.machine}</td>
        <td>{entry.date}</td>
        <td>{/* best match */}</td>
        <td>{entry.aiReflection ? 'O' : '-'}</td>
      </tr>
      {expanded && (
        <tr>
          <td colSpan={5}>
            {/* Full 25 games, comparison, reflection */}
          </td>
        </tr>
      )}
    </>
  );
}
```

### Anti-Patterns to Avoid
- **Accessing localStorage during render:** Always use lazy initialization `useState(() => loadHistory())`. Direct localStorage.getItem in component body causes React 19 concurrent mode issues.
- **Storing comparison results in backend:** Comparison is pure math on 25 x 6 numbers vs 6 numbers. Keep it client-side. No network round-trip needed.
- **Calling Claude API from frontend:** API keys must never be exposed to the browser. Always proxy through the FastAPI backend.
- **Using async def for the reflect endpoint:** The project consistently uses sync def for IO/CPU-bound work. Anthropic SDK has a sync client. Stay consistent.
- **Using Opus model for reflection generation:** Reflection memos are structured, formulaic text. Haiku 4.5 ($1/$5 per MTok) is more than sufficient and 5x cheaper than Opus ($5/$25).

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| AI text generation | Custom LLM integration | `anthropic` Python SDK | Handles retries, rate limiting, error types, streaming. Well-tested. |
| UUID generation | Custom ID generator | `crypto.randomUUID()` | Built into all modern browsers. Unique per entry. |
| Number input auto-advance | Complex keydown handlers | `input.maxLength=2` + onInput advance | Simple DOM API. Focus next sibling on complete input. |
| JSON schema validation (backend) | Manual dict checking | Pydantic models | Already used everywhere in the project. |

**Key insight:** This phase has no complex algorithmic problems. The hardest part is the prompt engineering for AI reflections and the UX of the 6-number input. Both are design problems, not engineering problems.

## Common Pitfalls

### Pitfall 1: localStorage Quota Exceeded
**What goes wrong:** localStorage has a ~5MB limit. If users save hundreds of predictions with full comparison data, it could fill up.
**Why it happens:** Each SavedPrediction with comparison and reflection is ~2-5KB. 1000 entries = ~5MB.
**How to avoid:** Each entry is small (25 games x 6 numbers = 150 numbers + metadata). At ~3KB per entry, 1000+ entries fit easily. Add a try/catch on setItem and show a user-friendly error if quota is exceeded.
**Warning signs:** QuotaExceededError exception from localStorage.setItem.

### Pitfall 2: ANTHROPIC_API_KEY Not Configured
**What goes wrong:** Backend starts but /api/reflect endpoint fails with authentication error.
**Why it happens:** User hasn't set the API key in environment or .env file.
**How to avoid:** Make the API key optional in config. If not set, the reflect endpoint returns a clear error message ("API key not configured"). Frontend handles this gracefully by showing the comparison without AI reflection.
**Warning signs:** 401/403 from Anthropic API, or config validation error at startup.

### Pitfall 3: React State vs localStorage Sync
**What goes wrong:** Multiple browser tabs show stale data. Or state and localStorage diverge after an error.
**Why it happens:** localStorage is not reactive. Changes in one tab don't notify others.
**How to avoid:** For this localhost-only app, single-tab usage is the expected case. The hook writes to both state and localStorage on every mutation. No cross-tab sync needed (per scope -- localhost only, single user).
**Warning signs:** Data visible in DevTools localStorage but not in UI.

### Pitfall 4: Number Input Validation Edge Cases
**What goes wrong:** Users enter 0, 46, duplicate numbers, or non-numeric characters.
**Why it happens:** Free-form number input without constraints.
**How to avoid:** Validate on input: 1-45 range, no duplicates across 6 fields, numeric only. Disable "compare" button until all 6 valid unique numbers are entered.
**Warning signs:** NaN in comparison results, duplicate numbers in actual set.

### Pitfall 5: Claude API Latency Blocking UI
**What goes wrong:** User clicks "generate reflection" and UI freezes for 2-5 seconds.
**Why it happens:** Claude API call takes 1-3 seconds. If not handled asynchronously in the UI, it blocks interaction.
**How to avoid:** Use `useMutation` from TanStack Query. Show loading spinner during API call. The button should show "AI analyzing..." state. This is already the established pattern (see usePrediction.ts).
**Warning signs:** No loading indicator, UI appears frozen.

### Pitfall 6: Prompt Injection via Comparison Data
**What goes wrong:** Malformed comparison data could manipulate the Claude prompt.
**Why it happens:** Comparison data is serialized into the prompt string.
**How to avoid:** The comparison data originates from the user's own localStorage (client-side only, localhost app). Risk is minimal. Still, serialize comparison data as structured JSON rather than free text in the prompt.
**Warning signs:** Unexpected AI reflection content.

## Code Examples

### Winning Number Input with Auto-Advance
```typescript
// frontend/src/components/history/WinningNumberInput.tsx
import { useRef, useState, useCallback } from 'react';

export function WinningNumberInput({
  onSubmit,
}: {
  onSubmit: (numbers: number[]) => void;
}) {
  const [values, setValues] = useState<string[]>(Array(6).fill(''));
  const inputRefs = useRef<(HTMLInputElement | null)[]>([]);

  const handleChange = useCallback((index: number, value: string) => {
    // Allow only digits
    const cleaned = value.replace(/\D/g, '');
    const num = parseInt(cleaned, 10);

    // Validate range 1-45
    if (cleaned && (num < 1 || num > 45)) return;

    setValues(prev => {
      const next = [...prev];
      next[index] = cleaned;
      return next;
    });

    // Auto-advance on 2-digit entry or valid single digit > 4
    if (cleaned.length === 2 || (cleaned.length === 1 && num > 4)) {
      inputRefs.current[index + 1]?.focus();
    }
  }, []);

  const numbers = values.map(v => parseInt(v, 10)).filter(n => !isNaN(n));
  const isValid = numbers.length === 6
    && numbers.every(n => n >= 1 && n <= 45)
    && new Set(numbers).size === 6;

  return (
    <div className="flex items-center gap-2">
      {Array.from({ length: 6 }, (_, i) => (
        <input
          key={i}
          ref={el => { inputRefs.current[i] = el; }}
          type="text"
          inputMode="numeric"
          maxLength={2}
          value={values[i]}
          onChange={e => handleChange(i, e.target.value)}
          className="w-12 h-12 text-center border border-border rounded-lg text-lg font-bold"
          placeholder={String(i + 1)}
        />
      ))}
      <button
        onClick={() => onSubmit(numbers.sort((a, b) => a - b))}
        disabled={!isValid}
        className="px-4 py-2 bg-accent text-white rounded-lg disabled:opacity-50"
      >
        비교
      </button>
    </div>
  );
}
```

### Reflection API Call Hook
```typescript
// frontend/src/hooks/useReflection.ts
import { useMutation } from '@tanstack/react-query';
import { API_BASE } from '../lib/api';

type ReflectRequest = {
  machine: string;
  roundNumber: number;
  comparisonData: object;
  pastReflections?: string[];
};

async function fetchReflection(req: ReflectRequest): Promise<string> {
  const res = await fetch(`${API_BASE}/reflect`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      machine: req.machine,
      round_number: req.roundNumber,
      comparison_data: req.comparisonData,
      past_reflections: req.pastReflections,
    }),
  });
  if (!res.ok) throw new Error(`Reflection failed: HTTP ${res.status}`);
  const data = await res.json() as { reflection: string };
  return data.reflection;
}

export function useReflection() {
  return useMutation<string, Error, ReflectRequest>({
    mutationFn: fetchReflection,
  });
}
```

### Backend Reflect Endpoint (Pydantic Schema)
```python
# backend/app/schemas/reflection.py
from pydantic import BaseModel

class ReflectRequest(BaseModel):
    machine: str
    round_number: int
    comparison_data: dict       # Serialized ComparisonResult from frontend
    past_reflections: list[str] | None = None

class ReflectResponse(BaseModel):
    reflection: str
    model: str                  # Which Claude model was used
```

### Backend Config Extension
```python
# backend/app/config.py -- additions
import os

class Settings:
    # ... existing settings ...
    ANTHROPIC_API_KEY: str | None = os.environ.get("ANTHROPIC_API_KEY")
    REFLECTION_MODEL: str = "claude-haiku-4-5"
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| crypto.randomUUID() polyfill | Native browser API | 2022+ | No polyfill needed, all modern browsers support it |
| useEffect for localStorage sync | Lazy useState initializer | React 18+ | Avoids hydration issues and render-time side effects |
| Anthropic SDK v0.x completions | SDK v0.86.0 messages.create | 2024+ | Messages API is the standard. Completions API deprecated. |
| Claude 3 Haiku ($0.25/MTok) | Claude Haiku 4.5 ($1/MTok) | 2025 | Claude 3 Haiku retires April 2026. Use Haiku 4.5. |

**Deprecated/outdated:**
- `anthropic.Completion` API: Use `messages.create()` instead
- Claude 3 Haiku model: Retires April 19, 2026. Use `claude-haiku-4-5`

## Open Questions

1. **Claude API Key Distribution**
   - What we know: The key must be in the backend environment. User needs an Anthropic API key.
   - What's unclear: Should we provide a UI to enter the API key, or require it as an environment variable?
   - Recommendation: Environment variable only (ANTHROPIC_API_KEY). This is a developer tool running on localhost. Add clear error messaging if key is missing. Document setup in a comment or startup log.

2. **Reflection Feedback Loop Mechanics**
   - What we know: D-13 says "feed reflections into prediction parameters." The existing predict endpoint takes `{ machine, strategy }` only.
   - What's unclear: How exactly to modify prediction behavior based on AI reflection. Two approaches: (a) Add an optional `adjustments` field to predict request that biases weights, or (b) Have the backend reflect endpoint return structured weight adjustments that the frontend passes to predict.
   - Recommendation: Approach (b) -- the reflect endpoint returns both the text memo AND structured suggestions (e.g., "increase weight for numbers [3,7,15], decrease for [22,33,41]"). The predict endpoint accepts an optional `weight_adjustments` parameter. This keeps the reflect/predict cycle explicit and testable.

3. **How Many Past Reflections to Include in Prompt**
   - What we know: D-14 says same-machine only. Could be 0 to many reflections.
   - What's unclear: How many to include before the prompt gets too long.
   - Recommendation: Include the most recent 3 reflections for the same machine. Keeps prompt under 2000 tokens. Older reflections have diminishing relevance.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python 3.13 | Backend | Yes | 3.13.12 | -- |
| uv | Package management | Yes | 0.8.14 | pip install |
| Node.js | Frontend | Yes | v25.8.1 | -- |
| anthropic SDK | AI reflection | No (not installed) | Will install 0.86.0 | -- |
| ANTHROPIC_API_KEY | AI reflection | Unknown | -- | Graceful degradation -- reflection features disabled, core history/comparison still works |

**Missing dependencies with no fallback:**
- None. All blocking dependencies are available or installable.

**Missing dependencies with fallback:**
- ANTHROPIC_API_KEY: If not set, AI reflection (HIST-05, HIST-06) degrades gracefully. History saving, comparison, and performance reports (HIST-01 through HIST-04, HIST-07) work without it.

## Project Constraints (from CLAUDE.md)

- **Use FastAPI, not Flask** -- new endpoint must be in existing FastAPI router
- **Use uv, not pip** -- `uv add anthropic` for backend dependency
- **No database** -- localStorage only per D-01 and CLAUDE.md "No MongoDB/PostgreSQL"
- **No Docker** -- localhost only
- **Native fetch, not axios** -- TanStack Query wraps fetch
- **TanStack Query + useState for state management** -- no Redux/Zustand
- **Korean UI** -- per Phase 5 D-09
- **Sync def for endpoints** -- consistent with existing predict/data/heatmap patterns
- **Container + Presentational component pattern** -- established in Phase 5
- **bg-card rounded-xl border card pattern** -- established in Phase 6 ChartCard
- **Tailwind v4 utility classes** -- no CSS modules or styled-components

## Sources

### Primary (HIGH confidence)
- [Anthropic Client SDKs docs](https://platform.claude.com/docs/en/api/client-sdks) -- Python SDK usage, model names, messages.create pattern
- [anthropic PyPI](https://pypi.org/project/anthropic/) -- Confirmed v0.86.0 latest, March 18 2026
- Existing codebase files: `frontend/src/hooks/usePrediction.ts`, `frontend/src/lib/api.ts`, `backend/app/api/routes.py`, `backend/app/config.py` -- established patterns

### Secondary (MEDIUM confidence)
- [Anthropic API Pricing](https://platform.claude.com/docs/en/about-claude/pricing) -- Haiku 4.5 at $1/$5 per MTok, cost-effective for reflection generation
- [localStorage React best practices](https://medium.com/@roman_j/mastering-state-persistence-with-local-storage-in-react-a-complete-guide-1cf3f56ab15c) -- Lazy initialization, React 19 safety
- [useLocalStorage TypeScript patterns](https://usehooks-ts.com/react-hook/use-local-storage) -- Hook design reference

### Tertiary (LOW confidence)
- None. All findings verified against primary or secondary sources.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH -- anthropic SDK version verified via PyPI. All other dependencies already installed and working.
- Architecture: HIGH -- extends existing patterns (container/presentational, useMutation, sync FastAPI endpoints). No new paradigms.
- Pitfalls: HIGH -- localStorage limits are well-documented. API key management is standard practice. React 19 lazy init is documented.
- AI integration: MEDIUM -- prompt design for Korean-language reflection memos needs iteration. claude-haiku-4-5 capability for this specific task is assumed sufficient but untested.

**Research date:** 2026-03-27
**Valid until:** 2026-04-27 (stable -- no fast-moving dependencies)
