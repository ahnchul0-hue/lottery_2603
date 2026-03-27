# Phase 6: Statistics Dashboard - Context

**Gathered:** 2026-03-27
**Status:** Ready for planning

<domain>
## Phase Boundary

선택된 호기의 통계 분석을 인터랙티브 차트와 시각화로 표시하는 대시보드. 예측 영역 하단에 위치하며, 6개 차트 섹션(번호 빈도, Hot/Cold, 히트맵, 홀짝/고저, 구간분포, 총합/AC값)을 세로 스크롤로 제공.

Requirements: DASH-01, DASH-02, DASH-03, DASH-04, DASH-05, DASH-06, UI-02

</domain>

<decisions>
## Implementation Decisions

### Dashboard Layout
- **D-01:** 모든 차트를 세로 스크롤로 나열 — 예측 결과 아래로 자연스럽게 스크롤
- **D-02:** 차트 순서: 번호 빈도(DASH-01) → Hot/Cold(DASH-02) → 히트맵(DASH-03) → 홀짝/고저(DASH-04) → 구간분포(DASH-05) → 총합/AC값(DASH-06)
- **D-03:** 예측 영역과 대시보드 사이에 "통계 분석" 섹션 헤더 + 수평 구분선(border-t)으로 시각적 구분

### Statistical Computation Location
- **D-04:** 하이브리드 방식 — 간단한 계산(빈도, Hot/Cold, 홀짝비율, 고저비율, 구간분포)은 프론트엔드 JS에서 useMemo로 계산
- **D-05:** 히트맵 3x45 편차 데이터만 백엔드 새 API 엔드포인트(GET /api/statistics/heatmap)에서 계산
- **D-06:** 프론트엔드 통계 계산은 이미 fetchMachineData로 받은 draws 배열을 활용 (추가 API 호출 불필요)

### Chart Interaction
- **D-07:** 호버 툴팁만 — Recharts 기본 Tooltip 컴포넌트 활용. 바/포인트에 마우스 올리면 상세 수치 표시
- **D-08:** 클릭 필터링이나 차트 간 연동 없음 — 단순하고 직관적인 읽기 전용 대시보드

### Heatmap Design (DASH-03)
- **D-09:** 빨강-파랑 diverging 색상 스킴 — 편중(많이 나온 번호)=빨간색, 부족(적게 나온 번호)=파란색, 기대치=흰색/회색
- **D-10:** HTML CSS Grid로 직접 구현 (Recharts 미사용) — 3행(호기) x 45열(번호), 135개 셀에 배경색 + 호버 툴팁
- **D-11:** 편차값은 백엔드에서 계산하여 전달 (기대빈도 대비 실제 출현 횟수의 편차)

### Claude's Discretion
- 차트 카드 스타일링 (bg-card, rounded, shadow 등 기존 패턴 따름)
- 각 차트의 세부 Recharts 설정 (축 라벨, 색상, 범례 위치)
- useMemo 훅 분리 구조 (단일 useStatistics 훅 vs 차트별 개별 훅)
- Hot/Cold 번호 표시 형식 (LottoBall 컴포넌트 재사용 vs 테이블 형식)
- 총합 범위와 AC값 분포의 구체적 차트 타입 (히스토그램 vs 라인 vs 바)

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Existing Frontend Code
- `frontend/src/App.tsx` — 현재 예측 페이지 레이아웃 (대시보드는 이 아래에 추가)
- `frontend/src/types/lottery.ts` — LotteryDraw 타입 (numbers, odd_even_ratio, high_low_ratio, ac_value, tail_sum, total_sum 필드)
- `frontend/src/lib/api.ts` — fetchMachineData (GET /api/data) — draws 배열 반환
- `frontend/src/hooks/useMachineInfo.ts` — useQuery 패턴 참고
- `frontend/src/components/LottoBall.tsx` — 로또공 컴포넌트 (Hot/Cold 표시에 재사용 가능)
- `frontend/src/lib/lottoBallColor.ts` — 번호별 색상 매핑 (D-06)

### Backend API
- `backend/app/api/routes.py` — 기존 엔드포인트 패턴 (새 히트맵 API 추가 위치)
- `backend/app/schemas/lottery.py` — Pydantic 스키마 패턴
- `backend/app/services/` — 서비스 레이어 패턴

### Design Tokens
- `frontend/src/index.css` — Tailwind v4 @theme (Slate 팔레트, blue-500 액센트, 8-point spacing)

### Prior Phase Decisions
- `.planning/phases/05-machine-selection-prediction-ui/05-CONTEXT.md` — D-06 로또공 색상, D-09 한국어 UI

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `LottoBall` 컴포넌트: Hot/Cold 번호 표시에 재사용 가능
- `getLottoBallColor()`: 번호별 색상 매핑 함수
- `fetchMachineData()`: 이미 전체 draws 데이터 반환 — 프론트엔드 통계 계산의 데이터 소스
- `useMachineInfo` 훅: useQuery 패턴 참고하여 통계용 훅 설계
- TanStack React Query: 이미 설치/설정 완료

### Established Patterns
- Tailwind v4 유틸리티 클래스 스타일링
- TypeScript export type 패턴 (verbatimModuleSyntax)
- Container + Presentational 컴포넌트 분리 (MachineSelector/PredictionResults 패턴)
- native fetch + JSON 응답 패턴

### Integration Points
- `App.tsx`: PredictionResults 아래에 StatisticsDashboard 컴포넌트 추가
- 선택된 호기(selectedMachine) state가 App.tsx에서 관리됨 — 대시보드에 props로 전달
- API_BASE = 'http://localhost:8000/api' — 새 히트맵 엔드포인트 추가

</code_context>

<specifics>
## Specific Ideas

- 히트맵은 Recharts가 아닌 HTML CSS Grid로 직접 구현 (3x45 = 135 셀)
- 빨강-파랑 diverging 색상으로 편중/부족 직관적 표현
- 호기별 번호 출현 빈도 바 차트는 45개 바가 가로로 나열 (1-45번)
- Hot/Cold는 상위 10개 번호를 LottoBall 컴포넌트로 시각적 표시
- 대시보드는 호기를 선택하면 자동으로 해당 호기 통계로 업데이트 (예측과 동일한 selectedMachine 사용)

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 06-statistics-dashboard*
*Context gathered: 2026-03-27*
