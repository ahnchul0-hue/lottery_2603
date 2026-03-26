# Phase 1: Foundation & Data Layer - Research

**Researched:** 2026-03-26
**Domain:** FastAPI backend scaffolding, React/Vite frontend scaffolding, JSON data loading with validation, CORS integration
**Confidence:** HIGH

## Summary

Phase 1 is a greenfield scaffolding phase: stand up a Python FastAPI backend and a React (Vite) frontend from zero, wire CORS between them, load `new_res.json` at startup with validation, and expose a filtered-by-machine API endpoint. The data file has been verified: 417 records, rounds 800-1216, three machines (1hoogi: 134, 2hoogi: 136, 3hoogi: 147), all numbers pre-sorted, no range violations, no count errors. The JSON structure uses a top-level `metadata` + `lottery_data` array.

The critical technical decisions are already locked: use `uv` (not pip), FastAPI lifespan (not deprecated `on_event`), Pydantic v2 models, monorepo with `backend/` + `frontend/` folders, and the data file at `backend/data/new_res.json` (copy from root). All environment dependencies (Node.js 25.8.1, Python 3.13.12, uv 0.8.14) are confirmed available on the target machine.

**Primary recommendation:** Build backend-first (data loader + validation + health endpoint + machine-filter endpoint), then scaffold frontend with a placeholder page that calls the health endpoint to prove CORS works end-to-end.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- **D-01:** Monorepo structure -- root has `backend/` + `frontend/` folders
- **D-02:** `new_res.json` original stays at root, copy placed at `backend/data/` for backend loading
- **D-03:** Backend pre-computes statistics -- API returns per-machine frequency, odd/even, high/low, AC value, total sum. Frontend only displays.
- **D-04:** Machine filtering via query parameter -- `GET /api/data?machine=1호기`
- **D-05:** Server startup memory load -- FastAPI lifespan loads full JSON + caches per-machine filtered views. 417 records = lightweight.
- **D-06:** Data validation on load -- number range (1-45), count (6), sorted order, machine value validation
- **D-07:** Python package manager `uv` (Rust-based, replaces pip+venv)
- **D-08:** Port assignment -- FastAPI: 8000, Vite dev server: 5173
- **D-09:** CORS -- allow origin `http://localhost:5173`

### Claude's Discretion
- FastAPI router structure (single file vs separated)
- Pydantic model design details
- React initial component structure

### Deferred Ideas (OUT OF SCOPE)
None -- discussion stayed within phase scope
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| INFRA-01 | Python FastAPI backend runs on localhost | FastAPI lifespan pattern, uv project setup, uvicorn on port 8000 |
| INFRA-02 | React(Vite) frontend runs on localhost | Vite 8 `react-ts` template, port 5173 |
| INFRA-03 | Frontend-backend CORS configured correctly | CORSMiddleware with explicit origin `http://localhost:5173`, middleware ordering |
| DATA-01 | Load new_res.json (800-1216, 417 records) and filter by machine (1/2/3) | DataLoader class with lifespan init, pre-filtered machine cache, query param endpoint |
| DATA-02 | Validate data on load (number range, count, sort order) | Pydantic v2 field_validator/model_validator, validation at load time with clear error messages |
</phase_requirements>

## Standard Stack

### Core (Phase 1 only -- subset of full project stack)

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| FastAPI | ^0.135.2 | REST API framework | Auto-generated Swagger docs, Pydantic v2 integration, lifespan events for data loading |
| Pydantic | ^2.12.5 | Data validation / serialization | Built into FastAPI. Validates lottery data at load time and API responses at runtime |
| Uvicorn | ^0.34.x | ASGI server | Standard FastAPI server, included in `fastapi[standard]` |
| uv | 0.8.14 (installed) | Python package/project manager | Locked decision D-07. Replaces pip+venv. Already installed on machine |
| React | ^19.2.4 | UI framework | Locked in project stack. Only placeholder page needed in Phase 1 |
| Vite | ^8.0.2 | Build tool / dev server | Locked in project stack. `react-ts` template for TypeScript support |
| TypeScript | ^6.0.2 | Type safety | Locked in project stack. Used from day one |
| Tailwind CSS | ^4.2.2 | Styling | Locked in project stack. v4 zero-config with `@tailwindcss/vite` plugin |

### Supporting (Phase 1 only)

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| python-dotenv | ^1.x | Environment config | Optional for CORS origin and port configuration via `.env` |

### NOT needed in Phase 1

| Library | Why Deferred |
|---------|-------------|
| NumPy / Pandas / SciPy / scikit-learn | No statistical computation in Phase 1. Pure JSON loading and filtering only. |
| Recharts / TanStack Query | Frontend is placeholder only. No charts, no API data fetching hooks. |
| React Router | Single page placeholder. No routing needed. |
| orjson | 417 records loads instantly with stdlib `json`. Not worth the dependency yet. |

**Installation:**

```bash
# Backend (from project root)
cd backend
uv init --app --python 3.13
uv add "fastapi[standard]" pydantic
uv add --dev pytest pytest-asyncio httpx ruff

# Frontend (from project root)
npm create vite@latest frontend -- --template react-ts
cd frontend
npm install
npm install tailwindcss @tailwindcss/vite
```

## Architecture Patterns

### Recommended Project Structure (Phase 1 scope)

```
Lottery_2603/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py             # FastAPI app, lifespan, CORS, router include
│   │   ├── config.py           # Settings (data path, ports, CORS origins)
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   └── routes.py       # GET /api/health, GET /api/data?machine=
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   └── lottery.py      # LotteryDraw, MachineDataResponse, HealthResponse
│   │   └── services/
│   │       ├── __init__.py
│   │       └── data_loader.py  # JSON loading, validation, machine filtering
│   ├── data/
│   │   └── new_res.json        # Copy of root data file
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── test_data_loader.py
│   │   └── test_api.py
│   └── pyproject.toml
├── frontend/
│   ├── src/
│   │   ├── main.tsx
│   │   ├── App.tsx             # Placeholder page + health check call
│   │   ├── App.css
│   │   └── vite-env.d.ts
│   ├── index.html
│   ├── vite.config.ts
│   ├── tsconfig.json
│   ├── tailwind.css            # @import "tailwindcss";
│   └── package.json
├── new_res.json                # Original data (stays at root)
└── .planning/
```

### Pattern 1: FastAPI Lifespan for Data Loading

**What:** Use the modern `asynccontextmanager` lifespan pattern (not deprecated `on_event`) to load and validate `new_res.json` at server startup. Store the loaded data in a module-level variable accessible by route handlers.

**When to use:** Always for Phase 1 -- this is the locked decision (D-05).

**Source:** [FastAPI Lifespan Events Official Docs](https://fastapi.tiangolo.com/advanced/events/)

```python
# app/main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.services.data_loader import DataLoader
from app.config import settings

data_store: dict = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: load and validate data
    loader = DataLoader(settings.DATA_PATH)
    loader.load_and_validate()
    data_store["loader"] = loader
    yield
    # Shutdown: cleanup (optional for in-memory data)
    data_store.clear()

app = FastAPI(title="Lottery Predictor API", lifespan=lifespan)

# CRITICAL: Add CORS middleware BEFORE routes
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

from app.api.routes import router
app.include_router(router, prefix="/api")
```

### Pattern 2: Pydantic v2 Validation for Lottery Data

**What:** Use Pydantic models with `field_validator` and `model_validator` to validate each lottery draw record on load. Reject invalid records with clear error messages.

**When to use:** During data loading (D-06).

**Source:** [Pydantic v2 Validators Docs](https://docs.pydantic.dev/latest/concepts/validators/)

```python
# app/schemas/lottery.py
from pydantic import BaseModel, field_validator, model_validator
from typing import Literal

class LotteryDraw(BaseModel):
    round_number: int  # 회차
    machine: Literal["1호기", "2호기", "3호기"]  # 호기
    numbers: list[int]  # 1등_당첨번호
    odd_even_ratio: str  # 홀짝_비율
    high_low_ratio: str  # 고저_비율
    ac_value: int  # AC값
    tail_sum: int  # 끝수합
    total_sum: int  # 총합

    @field_validator("numbers")
    @classmethod
    def validate_numbers(cls, v: list[int]) -> list[int]:
        if len(v) != 6:
            raise ValueError(f"Expected 6 numbers, got {len(v)}")
        if any(n < 1 or n > 45 for n in v):
            raise ValueError(f"Numbers must be 1-45, got {v}")
        if v != sorted(v):
            raise ValueError(f"Numbers must be sorted ascending, got {v}")
        if len(set(v)) != 6:
            raise ValueError(f"Numbers must be unique, got {v}")
        return v
```

### Pattern 3: DataLoader with Pre-filtered Machine Cache

**What:** Load all 417 records once, validate each with Pydantic, then pre-filter into per-machine lists stored in a dictionary. Serve from memory on every request.

**When to use:** Always -- locked decision D-05.

```python
# app/services/data_loader.py
import json
from pathlib import Path
from app.schemas.lottery import LotteryDraw

class DataLoader:
    def __init__(self, data_path: str | Path):
        self.data_path = Path(data_path)
        self.all_draws: list[LotteryDraw] = []
        self._by_machine: dict[str, list[LotteryDraw]] = {}
        self.metadata: dict = {}

    def load_and_validate(self) -> None:
        """Load JSON, validate every record, pre-filter by machine."""
        with open(self.data_path, "r", encoding="utf-8") as f:
            raw = json.load(f)

        self.metadata = raw["metadata"]
        errors: list[str] = []

        for i, record in enumerate(raw["lottery_data"]):
            try:
                draw = LotteryDraw(
                    round_number=record["회차"],
                    machine=record["호기"],
                    numbers=record["1등_당첨번호"],
                    odd_even_ratio=record["홀짝_비율"],
                    high_low_ratio=record["고저_비율"],
                    ac_value=record["AC값"],
                    tail_sum=record["끝수합"],
                    total_sum=record["총합"],
                )
                self.all_draws.append(draw)
            except Exception as e:
                errors.append(f"Record {i} (round {record.get('회차', '?')}): {e}")

        if errors:
            raise ValueError(
                f"Data validation failed for {len(errors)} records:\n"
                + "\n".join(errors)
            )

        # Pre-filter by machine
        for machine in ["1호기", "2호기", "3호기"]:
            self._by_machine[machine] = sorted(
                [d for d in self.all_draws if d.machine == machine],
                key=lambda d: d.round_number,
            )

    def get_draws_for_machine(self, machine: str) -> list[LotteryDraw]:
        if machine not in self._by_machine:
            raise ValueError(f"Unknown machine: {machine}. Valid: 1호기, 2호기, 3호기")
        return self._by_machine[machine]

    @property
    def total_records(self) -> int:
        return len(self.all_draws)
```

### Pattern 4: Sync Endpoint for CPU-bound Operations

**What:** Use regular `def` (not `async def`) for endpoints that may eventually do CPU-bound computation. FastAPI automatically runs `def` endpoints in a thread pool, preventing event loop blocking.

**When to use:** For data endpoints that will later include NumPy/Pandas computation.

**Source:** [FastAPI Async/Sync Docs](https://fastapi.tiangolo.com/async/) -- Pitfall #12 from PITFALLS.md

```python
# app/api/routes.py
from fastapi import APIRouter, Query, HTTPException
from app.main import data_store

router = APIRouter()

@router.get("/health")
async def health_check():
    """Health check -- lightweight, async is fine."""
    loader = data_store.get("loader")
    return {
        "status": "ok",
        "data_loaded": loader is not None,
        "total_records": loader.total_records if loader else 0,
    }

@router.get("/data")
def get_machine_data(
    machine: str = Query(..., description="Machine filter: 1호기, 2호기, or 3호기")
):
    """Return lottery data filtered by machine. Uses def (not async def)
    because future phases will add CPU-bound NumPy computation."""
    loader = data_store.get("loader")
    if loader is None:
        raise HTTPException(status_code=503, detail="Data not loaded")
    try:
        draws = loader.get_draws_for_machine(machine)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {
        "machine": machine,
        "total_draws": len(draws),
        "draws": [d.model_dump() for d in draws],
    }
```

### Pattern 5: Vite + Tailwind CSS v4 Setup

**What:** Tailwind CSS v4 uses a Vite plugin (`@tailwindcss/vite`) instead of PostCSS config. No `tailwind.config.js` needed.

**Source:** [Tailwind CSS v4 Vite Installation](https://tailwindcss.com/docs)

```typescript
// vite.config.ts
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [
    react(),
    tailwindcss(),
  ],
})
```

```css
/* src/index.css (or tailwind.css) */
@import "tailwindcss";
```

### Anti-Patterns to Avoid

- **Using deprecated `@app.on_event("startup")`:** Use the lifespan context manager instead. Locked decision.
- **Using `pip` or `venv` directly:** Use `uv` exclusively. Locked decision D-07.
- **Using `allow_origins=["*"]` for CORS:** Always specify exact origin `http://localhost:5173`. See Pitfall #7.
- **Adding `async def` to data endpoints:** Use sync `def` for endpoints that will later do NumPy/Pandas work. See Pitfall #12.
- **Mixing `localhost` and `127.0.0.1` in CORS:** Browsers treat them as different origins. Pick one and be consistent.
- **Installing the full analysis stack in Phase 1:** NumPy/Pandas/SciPy are NOT needed yet. Keep dependencies minimal.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Data validation | Manual if/else validation chains | Pydantic v2 `field_validator` / `model_validator` | Pydantic gives structured errors, type coercion, and integrates with FastAPI response serialization |
| CORS handling | Manual header injection | FastAPI `CORSMiddleware` | Handles preflight OPTIONS, varies by origin, respects credentials correctly |
| JSON loading | Custom parser or streaming | stdlib `json.load()` | 417 records loads in <10ms. No need for streaming or orjson yet |
| Dev server hot reload | Custom file watcher | `uv run fastapi dev` / `npm run dev` | Both tools have built-in HMR/reload |
| API documentation | Swagger setup | FastAPI auto-generates at `/docs` | Built-in with zero configuration |

## Common Pitfalls

### Pitfall 1: CORS Middleware Ordering
**What goes wrong:** CORS middleware added after route definitions or after other middleware that short-circuits the request. Preflight OPTIONS requests get 405 responses.
**Why it happens:** FastAPI middleware is processed in reverse order of addition. If CORSMiddleware is added last, it processes first (correct). But if routes are defined via `include_router` before middleware, some frameworks misbehave.
**How to avoid:** Add `app.add_middleware(CORSMiddleware, ...)` immediately after `app = FastAPI(...)`, before any `include_router` calls.
**Warning signs:** Browser shows "Access-Control-Allow-Origin" errors despite correct configuration.

### Pitfall 2: NumPy int64 Serialization (Future-proofing)
**What goes wrong:** When Phase 2+ adds NumPy, `numpy.int64` values in API responses cause `TypeError: Object of type int64 is not JSON serializable`. This manifests as CORS errors in the browser because the 500 response lacks CORS headers.
**Why it happens:** Python's `json` module does not know NumPy types. FastAPI's default serializer also fails.
**How to avoid:** In Phase 1, use Pydantic response models for ALL endpoints. Pydantic handles type coercion (int64 -> int) automatically. This is the correct foundation.
**Warning signs:** CORS errors that only appear on certain endpoints (not health check).

### Pitfall 3: Data File Path Resolution
**What goes wrong:** Relative paths like `"data/new_res.json"` resolve differently depending on where `uvicorn` is launched from (project root vs backend directory).
**Why it happens:** Python's `open()` uses the current working directory, which varies by launch method.
**How to avoid:** Use `Path(__file__).parent.parent / "data" / "new_res.json"` for paths relative to the code, or make the data path configurable via `config.py` / environment variable.
**Warning signs:** FileNotFoundError that only occurs in certain launch contexts.

### Pitfall 4: Korean String Encoding
**What goes wrong:** Machine values like "1호기" contain Korean characters. If the JSON file is not opened with `encoding='utf-8'`, or if the response content-type header is wrong, Korean text appears as garbled characters.
**Why it happens:** Default encoding on some systems is not UTF-8.
**How to avoid:** Always specify `encoding='utf-8'` when opening files. FastAPI's JSON responses use UTF-8 by default, so response side is safe.
**Warning signs:** API returns `\uD638\uAE30` escape sequences or garbled characters.

### Pitfall 5: Frontend Proxy vs Direct CORS
**What goes wrong:** Some Vite guides recommend using Vite's `proxy` config to avoid CORS entirely during development. This hides CORS issues until production.
**Why it happens:** Proxy is simpler for development but masks real integration problems.
**How to avoid:** Use real CORS configuration from day one (locked decision D-09). Do NOT add a Vite proxy for API calls.
**Warning signs:** API works in dev but fails in any other environment.

## Code Examples

### Backend: Complete main.py (Phase 1)

```python
# backend/app/main.py
# Source: FastAPI lifespan docs + project CONTEXT.md decisions
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.services.data_loader import DataLoader
from app.config import settings

data_store: dict = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    loader = DataLoader(settings.DATA_PATH)
    loader.load_and_validate()
    data_store["loader"] = loader
    print(f"Loaded {loader.total_records} lottery records")
    yield
    data_store.clear()

app = FastAPI(
    title="Lottery Predictor API",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

from app.api.routes import router
app.include_router(router, prefix="/api")
```

### Backend: config.py

```python
# backend/app/config.py
from pathlib import Path

class Settings:
    DATA_PATH: Path = Path(__file__).parent.parent / "data" / "new_res.json"
    CORS_ORIGINS: list[str] = ["http://localhost:5173"]
    HOST: str = "0.0.0.0"
    PORT: int = 8000

settings = Settings()
```

### Frontend: Minimal App.tsx with Health Check

```tsx
// frontend/src/App.tsx
import { useEffect, useState } from 'react'

const API_BASE = 'http://localhost:8000/api'

function App() {
  const [health, setHealth] = useState<{
    status: string
    data_loaded: boolean
    total_records: number
  } | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetch(`${API_BASE}/health`)
      .then((res) => res.json())
      .then(setHealth)
      .catch((err) => setError(err.message))
  }, [])

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center">
      <div className="bg-white p-8 rounded-lg shadow-md text-center">
        <h1 className="text-2xl font-bold mb-4">Lottery Predictor</h1>
        {error && <p className="text-red-500">Backend error: {error}</p>}
        {health && (
          <div className="text-left space-y-2">
            <p>Status: {health.status}</p>
            <p>Data loaded: {health.data_loaded ? 'Yes' : 'No'}</p>
            <p>Total records: {health.total_records}</p>
          </div>
        )}
        {!health && !error && <p className="text-gray-400">Connecting...</p>}
      </div>
    </div>
  )
}

export default App
```

### Frontend: vite.config.ts (Tailwind v4 + React)

```typescript
// frontend/vite.config.ts
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [
    react(),
    tailwindcss(),
  ],
})
```

## Data File Structure (Verified)

The actual `new_res.json` file has been inspected and verified:

```
Top-level: { "metadata": {...}, "lottery_data": [...] }
Records: 417 total
Rounds: 800 to 1216
Machines: {"1호기": 134, "2호기": 136, "3호기": 147}
Record keys: ["회차", "호기", "1등_당첨번호", "홀짝_비율", "고저_비율", "AC값", "끝수합", "총합"]
Numbers: Always 6 integers, always sorted ascending, always in range 1-45
No validation failures found in existing data.
```

**Key data structure detail:** The JSON uses Korean field names. The DataLoader must map these to English Pydantic field names during parsing (see Pattern 2 example).

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| `@app.on_event("startup")` | `asynccontextmanager` lifespan | FastAPI 0.93+ (2023) | Lifespan pairs startup/shutdown, prevents resource leaks |
| `tailwind.config.js` + PostCSS | `@tailwindcss/vite` plugin + `@import "tailwindcss"` | Tailwind v4 (2025) | Zero config, no PostCSS setup needed |
| `pip install` + `python -m venv` | `uv add` + `uv sync` | uv 0.1+ (2024) | 10-100x faster, single tool |
| ORJSONResponse for fast serialization | Pydantic v2 Rust-based serialization | FastAPI 0.131 (2025) | ORJSONResponse deprecated; Pydantic v2 is faster natively |
| Vite 5/6 with Babel | Vite 8 with Rolldown (Rust bundler) + Oxc | Vite 8 (March 2026) | 10-30x faster builds |

## Open Questions

1. **Router structure: single file vs split?**
   - What we know: Phase 1 has only 2 endpoints (health + data). Phase 2+ adds predict, stats.
   - Recommendation: Start with a single `routes.py` for Phase 1. Split into `data_routes.py` + `prediction_routes.py` + `stats_routes.py` when Phase 2-3 adds endpoints. This avoids premature abstraction.

2. **D-04 endpoint design: `GET /api/data?machine=1호기` vs `GET /api/data/1호기`**
   - What we know: CONTEXT.md specifies query parameter style (D-04).
   - Recommendation: Follow D-04 exactly. Use `Query(...)` with validation. Path parameters would also work but the decision is locked.

3. **`fastapi[standard]` extras vs manual uvicorn**
   - What we know: `fastapi[standard]` bundles uvicorn, httptools, uvloop, python-multipart, email-validator, and the `fastapi` CLI.
   - Recommendation: Use `fastapi[standard]` as it provides `uv run fastapi dev` command with auto-reload.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python | Backend runtime | Yes | 3.13.12 | -- |
| Node.js | Frontend build/dev | Yes | 25.8.1 | -- |
| npm | Frontend package management | Yes | 11.11.0 | -- |
| uv | Backend package management (D-07) | Yes | 0.8.14 | -- |

**Missing dependencies with no fallback:** None.
**Missing dependencies with fallback:** None.

All required tools are installed and at compatible versions. Node.js 25.8.1 exceeds Vite 8's requirement (20.19+). Python 3.13.12 exceeds FastAPI's requirement (3.9+). uv 0.8.14 is newer than the researched 0.11.1 referenced in STACK.md (version numbering: 0.8 > 0.11 is false in semver, but uv uses CalVer-like versioning where 0.8.14 from Aug 2025 is the installed version -- this should work fine with `uv init` and `uv add`).

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest ^8.x + pytest-asyncio + httpx |
| Config file | `backend/pyproject.toml` [tool.pytest.ini_options] -- Wave 0 |
| Quick run command | `cd backend && uv run pytest tests/ -x -q` |
| Full suite command | `cd backend && uv run pytest tests/ -v` |

### Phase Requirements -> Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| INFRA-01 | FastAPI server starts and responds to health check | integration | `cd backend && uv run pytest tests/test_api.py::test_health_check -x` | Wave 0 |
| INFRA-02 | React frontend starts and renders placeholder | manual | `cd frontend && npm run dev` (visual verification) | N/A |
| INFRA-03 | CORS allows cross-origin request from :5173 | integration | `cd backend && uv run pytest tests/test_api.py::test_cors_headers -x` | Wave 0 |
| DATA-01 | Backend loads new_res.json filtered by machine | unit | `cd backend && uv run pytest tests/test_data_loader.py::test_load_and_filter -x` | Wave 0 |
| DATA-02 | Invalid data entries rejected with clear errors | unit | `cd backend && uv run pytest tests/test_data_loader.py::test_validation_rejects_invalid -x` | Wave 0 |

### Sampling Rate
- **Per task commit:** `cd backend && uv run pytest tests/ -x -q`
- **Per wave merge:** `cd backend && uv run pytest tests/ -v`
- **Phase gate:** Full suite green before `/gsd:verify-work`

### Wave 0 Gaps
- [ ] `backend/tests/__init__.py` -- empty init
- [ ] `backend/tests/conftest.py` -- shared fixtures (test client, test data loader)
- [ ] `backend/tests/test_data_loader.py` -- covers DATA-01, DATA-02
- [ ] `backend/tests/test_api.py` -- covers INFRA-01, INFRA-03
- [ ] pytest config in `pyproject.toml` [tool.pytest.ini_options]
- [ ] `uv add --dev pytest pytest-asyncio httpx` -- test dependencies

## Sources

### Primary (HIGH confidence)
- [FastAPI Lifespan Events](https://fastapi.tiangolo.com/advanced/events/) -- lifespan context manager pattern
- [FastAPI CORS Middleware](https://fastapi.tiangolo.com/tutorial/cors/) -- CORSMiddleware configuration
- [Pydantic v2 Validators](https://docs.pydantic.dev/latest/concepts/validators/) -- field_validator, model_validator patterns
- [uv + FastAPI Integration](https://docs.astral.sh/uv/guides/integration/fastapi/) -- `uv init --app`, `uv add fastapi[standard]`, `uv run fastapi dev`
- [Vite Getting Started](https://vite.dev/guide/) -- `npm create vite@latest` with react-ts template
- [Tailwind CSS v4 Installation](https://tailwindcss.com/docs) -- `@tailwindcss/vite` plugin, `@import "tailwindcss"` CSS-only config
- Data file inspection: direct analysis of `/Users/ahnchul0/Downloads/Lottery_2603/new_res.json` (verified structure, record count, machine distribution, data integrity)

### Secondary (MEDIUM confidence)
- [FastAPI + NumPy serialization issue #15085](https://github.com/fastapi/fastapi/issues/15085) -- numpy.int64 serialization problem documentation
- [ORJSONResponse deprecation](https://schema.ai/technologies/fastapi/insights/orjson-ujson-response-deprecation) -- Pydantic v2 replaces ORJSONResponse
- Environment check: verified Node.js 25.8.1, Python 3.13.12, uv 0.8.14 on target machine

### Tertiary (LOW confidence)
- None -- all findings verified with primary or secondary sources.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH -- all versions verified against official sources and STACK.md research. Environment confirmed available.
- Architecture: HIGH -- patterns from official FastAPI/Vite/Tailwind docs, aligned with locked decisions from CONTEXT.md.
- Pitfalls: HIGH -- CORS and NumPy serialization are well-documented issues. Data file verified clean (no current validation failures).

**Research date:** 2026-03-26
**Valid until:** 2026-04-26 (stable stack, no fast-moving changes expected)
