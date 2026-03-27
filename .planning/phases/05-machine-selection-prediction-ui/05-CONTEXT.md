# Phase 5: Machine Selection & Prediction UI - Context

**Gathered:** 2026-03-27
**Status:** Ready for planning

<domain>
## Phase Boundary

호기 선택 카드 UI + "번호 예측" 버튼 + 5전략 x 5게임 = 25게임 결과를 전략별 섹션으로 표시하는 프론트엔드 구현. 상단 깔끔 모던 영역.

Requirements: MACH-01, MACH-02, MACH-03, UI-01

</domain>

<decisions>
## Implementation Decisions

### Machine Selection Design
- **D-01:** 호기 번호 카드 3개 가로 나열 — 각 카드에 호기 번호 + 추첨 횟수 + 최근 회차 표시
- **D-02:** 선택 시 카드 테두리 색상 변경 (blue-500 액센트)
- **D-03:** 호기 정보(추첨 횟수, 최근 회차)는 백엔드 API에서 가져옴

### Result Card Layout
- **D-04:** 전략별 섹션으로 수직 스크롤 — 전략명 헤더 + 5게임 가로 나열
- **D-05:** 5개 섹션: Frequency(빈도) → Pattern(패턴) → Range(구간) → Balance(밸런스) → Composite(종합)

### Number Display Style
- **D-06:** 로또공 모양 원형 배지 + 동행복권 색상 코딩
  - 1-10: 노랑 (#ffc107)
  - 11-20: 파랑 (#2196f3)
  - 21-30: 빨강 (#f44336)
  - 31-40: 회색 (#9e9e9e)
  - 41-45: 초록 (#4caf50)
- **D-07:** 번호는 2자리 패딩 (03, 07 등)

### Korean Copy
- **D-08:** 전략명은 영어+한국어 병기
  - Frequency (빈도)
  - Pattern (패턴)
  - Range (구간)
  - Balance (밸런스)
  - Composite (종합)
- **D-09:** UI 전체 한국어 — "호기 선택", "번호 예측", "예측 결과" 등
- **D-10:** 페이지 제목: "로또 예측기" (한국어로 변경)

### Claude's Discretion
- React 컴포넌트 분리 구조 (MachineCard, GameRow, LottoBall 등)
- API 호출 hooks 설계 (usePrediction 등)
- 로딩 상태 표시 방식
- "번호 예측" 버튼 위치와 스타일

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Existing Code
- `frontend/src/App.tsx` — 현재 placeholder (Phase 1 health check)
- `frontend/src/index.css` — Tailwind v4 @theme 디자인 토큰
- `frontend/src/main.tsx` — React entry point
- `frontend/vite.config.ts` — Vite + Tailwind 설정
- `backend/app/api/routes.py` — POST /api/predict, GET /api/data, GET /api/health

### UI-SPEC
- `.planning/phases/01-foundation-data-layer/01-UI-SPEC.md` — 디자인 토큰 (Slate 팔레트, blue-500 액센트, 8-point spacing)

### Prior Phases
- `.planning/phases/01-foundation-data-layer/01-CONTEXT.md` — 모노레포, 포트 8000/5173
- `.planning/phases/03-prediction-pipeline-vertical-slice/03-CONTEXT.md` — POST /api/predict JSON body

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- Tailwind CSS v4 디자인 토큰 (--color-*, --spacing-*, --font-*)
- Vite + React + TypeScript 설정 완료
- Backend API 완성: POST /api/predict, GET /api/data?machine=X

### Established Patterns
- CSS custom properties via @theme in index.css
- Tailwind utility-first 스타일링

### Integration Points
- `App.tsx`: placeholder를 실제 UI로 교체
- API base URL: http://localhost:8000
- POST /api/predict body: {"machine": "1호기", "strategy": "frequency"}
- 응답: {"games": [[...], ...], "strategy": "frequency", "machine": "1호기"}

</code_context>

<specifics>
## Specific Ideas

- 동행복권 스타일 로또공 색상 코딩 (노/파/빨/회/초)
- 카드 3개 나란히 배치, 선택 시 파란 테두리
- 전략별 섹션이 세로로 스크롤, 각 섹션에 전략명 헤더
- "번호 예측" 버튼 클릭 시 5개 전략 한 번에 호출하여 25게임 표시

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 05-machine-selection-prediction-ui*
*Context gathered: 2026-03-27*
