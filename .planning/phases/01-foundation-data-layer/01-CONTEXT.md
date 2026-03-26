# Phase 1: Foundation & Data Layer - Context

**Gathered:** 2026-03-26
**Status:** Ready for planning

<domain>
## Phase Boundary

FastAPI 백엔드와 React(Vite) 프론트엔드를 기동하고, `new_res.json`(800~1216회, 417건)을 로드하여 호기별로 필터링된 데이터를 API로 제공하는 기반 구축.

Requirements: INFRA-01, INFRA-02, INFRA-03, DATA-01, DATA-02

</domain>

<decisions>
## Implementation Decisions

### Project Structure
- **D-01:** 모노레포 구조 사용 — 루트에 `backend/` + `frontend/` 폴더
- **D-02:** `new_res.json` 원본은 루트에 유지, `backend/data/`에 복사본 배치하여 백엔드에서 로드

### API Response Design
- **D-03:** 백엔드에서 통계값 사전계산 — API가 호기별 빈도, 홀짝, 고저, AC값, 총합 등 통계를 계산하여 응답. 프론트엔드는 표시만 담당
- **D-04:** 호기 필터링은 쿼리 파라미터로 — `GET /api/data?machine=1호기`

### Data Loading
- **D-05:** 서버 시작 시 메모리 로드 — FastAPI lifespan에서 JSON 전체 로드 + 호기별 필터 캐시. 417건이라 경량
- **D-06:** 데이터 유효성 검증 — 로드 시 번호 범위(1-45), 개수(6), 정렬, 호기값 검증

### Development Environment
- **D-07:** Python 패키지 관리자 `uv` 사용 (Rust 기반, pip+venv 대체)
- **D-08:** 포트 설정 — FastAPI: 8000, Vite dev server: 5173
- **D-09:** CORS 설정 — `http://localhost:5173`을 허용 origin으로 설정

### Claude's Discretion
- FastAPI 라우터 구조 (단일 파일 vs 분리)
- Pydantic 모델 설계 상세
- React 초기 컴포넌트 구조

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Data
- `new_res.json` — 800~1216회 로또 당첨번호 + 호기 + 통계 (417건, 메인 데이터)
- `.planning/research/STACK.md` — FastAPI, React, uv 등 기술 스택 상세
- `.planning/research/ARCHITECTURE.md` — 컴포넌트 경계, 데이터 플로우, 빌드 순서
- `.planning/research/PITFALLS.md` — NumPy int64 직렬화, CORS 설정 등 함정

### Project
- `.planning/PROJECT.md` — 프로젝트 비전, 핵심 가치
- `.planning/REQUIREMENTS.md` — v1 요구사항 전체 (35건)

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- 없음 (greenfield)

### Established Patterns
- 없음 (greenfield)

### Integration Points
- `new_res.json` — 기존 데이터 파일, 백엔드에서 로드할 주요 데이터 소스

</code_context>

<specifics>
## Specific Ideas

- 모노레포 구조는 Preview에서 보여준 트리 구조 그대로 따를 것
- FastAPI lifespan 이벤트로 데이터 로드 (deprecated `on_event` 대신)
- 리서치에서 권장한 대로 Pydantic v2 모델 사용

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 01-foundation-data-layer*
*Context gathered: 2026-03-26*
