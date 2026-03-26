# Technology Stack

**Project:** Lottery Predictor (호기별 로또 번호 예측 웹앱)
**Researched:** 2026-03-26
**Overall Confidence:** HIGH

## Recommended Stack

### Frontend Core

| Technology | Version | Purpose | Why | Confidence |
|------------|---------|---------|-----|------------|
| React | ^19.2.4 | UI framework | Mature ecosystem, component model ideal for dashboard UI. v19 stable with hooks, concurrent features. Specified in project requirements. | HIGH |
| Vite | ^8.0.2 | Build tool / dev server | Vite 8 ships Rolldown (Rust bundler) for 10-30x faster builds. First-class React support via `@vitejs/plugin-react` v6 (uses Oxc, no Babel dependency). Specified in project requirements. | HIGH |
| TypeScript | ^6.0.2 | Type safety | TS 6.0 is current stable. Catches bugs at compile time, improves DX with autocompletion. Essential for data-heavy apps where type mismatches cause silent errors. | HIGH |
| Tailwind CSS | ^4.2.2 | Styling | v4 eliminates config files, 5x faster builds. `@tailwindcss/vite` plugin for tight Vite integration. Zero-config CSS-first approach. Ideal for rapid dashboard styling without writing custom CSS. | HIGH |

### Frontend Libraries

| Library | Version | Purpose | Why | Confidence |
|---------|---------|---------|-----|------------|
| Recharts | ^3.8.0 | Data visualization / charts | Built on D3+SVG, fully declarative React components. Best DX for bar charts, line charts, pie charts, heatmaps needed for lottery statistics. No low-level D3 wiring needed. | HIGH |
| @tanstack/react-query | ^5.95 | Server state / data fetching | Automatic caching, background refetch, loading/error states. Eliminates boilerplate for API calls to FastAPI backend. De facto standard for React data fetching. | HIGH |
| React Router | ^7.x | Client-side routing | Standard routing for React SPAs. Minimal use here (dashboard vs. prediction views) but enables clean URL structure. | MEDIUM |

### Backend Core

| Technology | Version | Purpose | Why | Confidence |
|------------|---------|---------|-----|------------|
| Python | ^3.12 | Runtime | Required for scipy/numpy/pandas/sklearn ecosystem. 3.12 is stable with performance improvements. 3.13+ also acceptable. | HIGH |
| FastAPI | ^0.135.2 | REST API framework | **Use FastAPI, not Flask.** Auto-generated Swagger docs for frontend integration. Pydantic v2 for request/response validation. Async support. 4x throughput over Flask. Type hints align with data science code patterns. | HIGH |
| Pydantic | ^2.12.5 | Data validation / serialization | Built into FastAPI. Validates API request/response models. Ensures lottery data structures are correct at runtime. | HIGH |
| Uvicorn | ^0.34.x | ASGI server | Standard production server for FastAPI. Async event loop. | HIGH |
| uv | ^0.11.1 | Package/project manager | **Use uv, not pip/venv.** 10-100x faster dependency resolution. Replaces pip + venv + pyenv in one tool. Rust-based. 2026 standard for Python project management. | HIGH |

### Data Analysis / Statistical Libraries

| Library | Version | Purpose | Why | Confidence |
|---------|---------|---------|-----|------------|
| NumPy | ^2.4.3 | Numerical computation | Foundation for all scientific Python. Array operations, random number generation, mathematical functions. Required by pandas/scipy/sklearn. | HIGH |
| Pandas | ^3.0.1 | Data manipulation / analysis | Load/filter/aggregate `new_res.json` data by 호기. `DataFrame.ewm()` for exponential weighted moving averages (time decay). GroupBy for per-machine statistics. v3.0 is major release (Jan 2026). | HIGH |
| SciPy | ^1.17.1 | Statistical testing | `scipy.stats` for chi-squared tests, frequency analysis, probability distributions. Already used in prior analysis (chi-squared test on machine distributions). | HIGH |
| scikit-learn | ^1.8.0 | Machine learning models | Random Forest for feature importance, clustering for number group patterns. Not for "predicting" lottery numbers, but for identifying statistical patterns in historical data. | HIGH |

### Supporting Python Libraries

| Library | Version | Purpose | When to Use | Confidence |
|---------|---------|---------|-------------|------------|
| statsmodels | ^0.14.6 | Exponential smoothing | `SimpleExpSmoothing` and `ExponentialSmoothing` for formal time decay weighting beyond pandas ewm. Use when you need fitted decay parameters rather than manually tuned alpha. | MEDIUM |
| python-dotenv | ^1.x | Environment config | Loading `.env` for CORS origins, port config. Lightweight, no overhead. | HIGH |
| orjson | ^3.x | Fast JSON parsing | 3-10x faster than stdlib `json` for loading `new_res.json` (417 records). Optional but recommended for response serialization. | MEDIUM |

### Developer Tooling

| Tool | Version | Purpose | Why | Confidence |
|------|---------|---------|-----|------------|
| ESLint | ^9.x | JS/TS linting | Flat config (eslint.config.js). Catches errors, enforces style. | HIGH |
| Prettier | ^3.x | Code formatting | Consistent formatting across frontend code. | HIGH |
| Ruff | ^0.11.x | Python linting + formatting | Replaces flake8 + black + isort. Rust-based, 10-100x faster. 2026 standard for Python. | HIGH |
| pytest | ^8.x | Python testing | Standard test framework. Use with pytest-asyncio for FastAPI tests. | HIGH |

## Time Decay Weighting: Recommended Approach

This is a core technical decision for the project. Use **exponential decay weighting** via `pandas.DataFrame.ewm()`.

### Why Exponential Decay (not linear, not step-function)

| Method | Formula | Pros | Cons | Verdict |
|--------|---------|------|------|---------|
| **Exponential decay** | `weight = alpha * (1-alpha)^(t)` | Smooth, mathematically grounded, built into pandas, configurable via halflife/span/alpha | Requires tuning alpha parameter | **USE THIS** |
| Linear decay | `weight = 1 - (t / N)` | Simple to understand | Arbitrary cutoff at N, poor tail behavior, recent data not emphasized enough | Too simplistic |
| Step function | `weight = 1 if recent else 0.5` | Very simple | Loses nuance, hard boundary between "recent" and "old" | Too crude |
| Inverse time | `weight = 1 / (1 + t)` | No parameters | Decays too slowly for recent emphasis | Poor fit |

### Implementation Pattern

```python
import pandas as pd

# halflife=50 means: data from 50 rounds ago has half the weight of the latest
# Tune this parameter based on how many rounds each 호기 appears in
weights = df.groupby('호기')['회차'].transform(
    lambda x: pd.Series(range(len(x)), index=x.index).ewm(halflife=50).mean()
)

# Or directly with alpha (0.02 = gentle decay, 0.1 = aggressive decay)
weights = pd.Series(range(len(df))).ewm(alpha=0.05).mean()
```

### Recommended Parameters

- **halflife=50**: A draw from ~50 rounds ago has half the weight. Given 호기 rotation (4-5 draws each), this covers roughly 10-12 호기-specific appearances.
- **alpha=0.05**: Gentle exponential decay. Tunes the sensitivity to recent data.
- These should be configurable via API parameters so the frontend can expose tuning controls later.

## Alternatives Considered

| Category | Recommended | Alternative | Why Not |
|----------|-------------|-------------|---------|
| Backend framework | FastAPI | Flask | Flask lacks auto-docs, validation, async. 4x slower. More boilerplate for API-only service. |
| Backend framework | FastAPI | Django REST Framework | Overkill. Django's ORM/admin/auth is unnecessary for static JSON analysis. Heavy dependency. |
| Charting | Recharts | D3.js | D3 is too low-level for this project's bar/line/pie charts. Recharts provides the same visuals with 5x less code. |
| Charting | Recharts | Chart.js (react-chartjs-2) | Canvas-based, loses SVG interactivity (hover, click on bars). Recharts has better React integration and declarative API. |
| Charting | Recharts | Nivo | Good alternative, but Recharts has larger community, more examples, simpler API for standard chart types. |
| HTTP client | fetch (native) | Axios | For this project's simple GET/POST calls, native fetch + TanStack Query is sufficient. No need for Axios's 11.7kB overhead. TanStack Query handles retries, caching, error states. |
| Package manager | uv | pip + venv | pip is 10-100x slower. uv handles Python version management, virtual environments, and dependencies in one tool. |
| Python linter | Ruff | flake8 + black + isort | Ruff replaces all three, runs 10-100x faster (Rust), single config. |
| Styling | Tailwind CSS | CSS Modules | Tailwind v4 is faster to iterate with utility classes. Dashboard-heavy apps benefit from consistent spacing/color system without writing custom CSS. |
| Styling | Tailwind CSS | Styled Components | Runtime CSS-in-JS has performance overhead. Tailwind compiles away at build time. |
| State management | TanStack Query (server) + React useState (local) | Redux / Zustand | This app's state is server-driven (API responses). No complex client-side state to manage. TanStack Query IS the state management for server data. |

## What NOT to Use

| Technology | Why Avoid |
|------------|-----------|
| Create React App | Deprecated. Vite is the standard. |
| Next.js | SSR/SSG unnecessary for localhost-only tool. Adds complexity without benefit. |
| TensorFlow / PyTorch | Deep learning is overkill for 417 data points. scikit-learn + scipy covers all needed statistical analysis. Neural networks need 10,000+ samples minimum. |
| Redux | No complex client-side state. TanStack Query + useState covers everything. |
| MongoDB / PostgreSQL | Data is a static JSON file (417 records). No database needed. Load JSON directly. |
| Docker | Out of scope per requirements (localhost only). Adds setup complexity for no gain. |
| Celery / task queues | Analysis completes in <1s for 417 records. No async job processing needed. |

## Project Structure

```
Lottery_2603/
├── frontend/                   # React + Vite + TypeScript
│   ├── src/
│   │   ├── components/         # UI components
│   │   ├── hooks/              # Custom hooks (useQuery wrappers)
│   │   ├── pages/              # Page-level components
│   │   ├── types/              # TypeScript type definitions
│   │   └── lib/                # Utility functions
│   ├── vite.config.ts
│   ├── tailwind.css
│   ├── tsconfig.json
│   └── package.json
├── backend/                    # Python + FastAPI
│   ├── app/
│   │   ├── main.py             # FastAPI app, CORS, routes
│   │   ├── models.py           # Pydantic request/response models
│   │   ├── analysis/           # Analysis engines
│   │   │   ├── frequency.py    # Frequency strategy
│   │   │   ├── pattern.py      # Pattern strategy
│   │   │   ├── section.py      # Section/range strategy
│   │   │   ├── balance.py      # Odd/even balance strategy
│   │   │   └── combined.py     # Combined strategy
│   │   ├── core/
│   │   │   ├── data_loader.py  # JSON data loading
│   │   │   └── time_decay.py   # Exponential decay weighting
│   │   └── stats/
│   │       └── dashboard.py    # Dashboard statistics endpoints
│   ├── tests/
│   ├── pyproject.toml
│   └── uv.lock
├── new_res.json                # Lottery data (800-1216 rounds)
└── .planning/                  # Project planning
```

## Installation Commands

### Frontend

```bash
# Create Vite React TypeScript project
npm create vite@latest frontend -- --template react-ts
cd frontend

# Core dependencies
npm install react@^19.2.4 react-dom@^19.2.4

# UI and charting
npm install recharts@^3.8.0 @tailwindcss/vite@^4.2.2 tailwindcss@^4.2.2

# Data fetching
npm install @tanstack/react-query@^5.95.0

# Routing (optional, minimal use)
npm install react-router@^7

# Dev dependencies
npm install -D typescript@^6.0.2 @types/react @types/react-dom eslint prettier
```

### Backend

```bash
# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Initialize Python project
cd backend
uv init --python 3.12

# Core dependencies
uv add fastapi[standard]@^0.135.2 uvicorn@^0.34.0 pydantic@^2.12.5

# Data analysis
uv add numpy@^2.4.3 pandas@^3.0.1 scipy@^1.17.1 scikit-learn@^1.8.0

# Optional but recommended
uv add orjson@^3.10 python-dotenv@^1.0

# Dev dependencies
uv add --dev pytest@^8.0 pytest-asyncio httpx ruff
```

## Version Compatibility Matrix

| Frontend | Requires | Backend | Requires |
|----------|----------|---------|----------|
| Vite 8 | Node.js 20.19+ or 22.12+ | FastAPI 0.135 | Python 3.9+ (recommend 3.12) |
| React 19.2 | Vite 7+ or 8 | Pandas 3.0 | NumPy 2.1+ |
| Recharts 3.8 | React 18+ or 19 | SciPy 1.17 | NumPy 2.1+ |
| TanStack Query 5.95 | React 18+ or 19 | scikit-learn 1.8 | NumPy 2.1+, SciPy 1.6+ |
| Tailwind 4.2 | Vite 5+ | Pydantic 2.12 | Python 3.9+ |
| TypeScript 6.0 | Node.js 18+ | uv 0.11 | Any OS (Rust binary) |

## Sources

- [Vite 8.0 Release](https://vite.dev/blog/announcing-vite8) - Confirmed Vite 8.0 with Rolldown, March 2026
- [React Versions](https://react.dev/versions) - Confirmed React 19.2.4 latest
- [FastAPI PyPI](https://pypi.org/project/fastapi/) - Confirmed 0.135.2 latest
- [Recharts npm](https://www.npmjs.com/package/recharts) - Confirmed 3.8.0 latest
- [TanStack Query](https://tanstack.com/query/latest) - Confirmed v5.95
- [NumPy PyPI](https://pypi.org/project/numpy/) - Confirmed 2.4.3 latest
- [Pandas 3.0.0 Release](https://pandas.pydata.org/docs/whatsnew/v3.0.0.html) - Major release Jan 2026
- [SciPy PyPI](https://pypi.org/project/SciPy/) - Confirmed 1.17.1 latest
- [scikit-learn PyPI](https://pypi.org/project/scikit-learn/) - Confirmed 1.8.0 latest
- [Tailwind CSS v4.0](https://tailwindcss.com/blog/tailwindcss-v4) - Confirmed v4 with Vite plugin
- [uv Documentation](https://docs.astral.sh/uv/) - Confirmed 0.11.1, Rust-based package manager
- [Pandas ewm() documentation](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.ewm.html) - Time decay via exponential weighted moving average
- [TypeScript 6.0](https://devblogs.microsoft.com/typescript/announcing-typescript-6-0/) - Confirmed TS 6.0 latest stable
- [FastAPI vs Flask comparison (2026)](https://docs.kanaries.net/articles/fastapi-vs-flask) - Performance benchmarks
- [Recharts vs D3 vs Chart.js comparison](https://querio.ai/blogs/charting-library-for-react) - Charting library analysis
