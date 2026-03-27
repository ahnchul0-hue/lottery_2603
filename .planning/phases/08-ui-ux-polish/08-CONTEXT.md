# Phase 8: UI/UX Polish - Context

**Gathered:** 2026-03-27
**Status:** Ready for planning

<domain>
## Phase Boundary

다크/라이트 모드 토글 + 로딩 애니메이션 + 통계적 면책조항. 앱의 완성도를 높이는 UI/UX 마무리 작업.

Requirements: UI-03, UI-04, UI-05

</domain>

<decisions>
## Implementation Decisions

### Dark/Light Mode (UI-03)
- **D-01:** 다크 모드를 기본값으로 설정 — 차트/대시보드가 다크 배경에서 더 잘 보임
- **D-02:** 페이지 우상단에 해/달 아이콘 토글 버튼 배치 — 항상 접근 가능, 공간 최소 차지
- **D-03:** localStorage에 테마 설정 저장 — 페이지 새로고침 시 유지 (키: 'lottery-theme')
- **D-04:** Tailwind v4 @theme 토큰을 다크/라이트 두 세트로 확장 — `<html class="dark">` 클래스로 전환
- **D-05:** Recharts 차트 색상도 테마에 맞게 전환 — CSS 변수 기반으로 차트 fill/stroke 색상 반응

### Loading Animation (UI-04)
- **D-06:** "번호 예측" 버튼에 스피너 표시 + 버튼 비활성화 — 클릭 후 결과 나올 때까지
- **D-07:** 결과 영역에 "예측 중..." 텍스트 표시 — 스피너와 함께 사용자에게 진행 상태 안내
- **D-08:** CSS 애니메이션 스피너 (Tailwind animate-spin) — 외부 라이브러리 불필요

### Disclaimer (UI-05)
- **D-09:** Claude's Discretion — 면책조항 위치, 스타일, 문구는 Claude가 적절히 결정

### Claude's Discretion
- 면책조항 위치 (페이지 하단/상단/플로팅)와 문구
- 다크 모드 색상 팔레트 구체 값 (기존 Slate 팔레트의 다크 변환)
- 토글 버튼의 아이콘 디자인 (SVG 직접 vs emoji)
- 스피너의 크기와 색상
- 테마 전환 시 트랜지션 애니메이션 여부

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Design Tokens
- `frontend/src/index.css` — Tailwind v4 @theme 토큰 (다크 모드 확장 대상)

### Existing Components
- `frontend/src/App.tsx` — 페이지 레이아웃 (토글 버튼 추가 위치, 로딩 상태 위치)
- `frontend/src/hooks/usePrediction.ts` — isPending 상태 (로딩 표시에 활용)
- `frontend/src/components/dashboard/` — 차트 컴포넌트 (다크 모드 대응 필요)

### Prior Phase Decisions
- `.planning/phases/05-machine-selection-prediction-ui/05-CONTEXT.md` — D-09 한국어 UI
- `.planning/phases/06-statistics-dashboard/06-CONTEXT.md` — Recharts 차트 패턴

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `usePrediction` 훅: `isPending` 상태로 로딩 감지 가능 (TanStack Query useMutation)
- Tailwind v4 @theme: CSS custom properties 기반 — `dark:` variant로 쉽게 확장
- `localStorage`: Phase 7에서 이미 사용 중 — 테마 저장에도 동일 패턴

### Established Patterns
- Tailwind v4 유틸리티 클래스
- bg-surface, bg-card, text-primary 등 시맨틱 토큰 이미 사용 중
- animate-spin 등 Tailwind 내장 애니메이션 활용 가능

### Integration Points
- `App.tsx`: 테마 토글 버튼 추가 (우상단), 로딩 상태 표시
- `index.css`: @theme 블록에 다크 모드 토큰 추가
- `<html>` 엘리먼트: dark 클래스 토글

</code_context>

<specifics>
## Specific Ideas

- 다크 모드가 기본 → 첫 방문자는 다크 모드로 시작
- 해/달 아이콘 토글로 직관적 전환
- 차트가 다크 배경에서 더 눈에 띄므로 다크 기본이 적합
- 스피너는 CSS만으로 구현 (tailwind animate-spin)

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 08-ui-ux-polish*
*Context gathered: 2026-03-27*
