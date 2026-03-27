# Phase 7: Prediction History & Review - Context

**Gathered:** 2026-03-27
**Status:** Ready for planning

<domain>
## Phase Boundary

예측 결과 로컬 저장(localStorage), 실제 당첨번호 입력/비교, 전략별 성과 추적, AI 자동 반성 메모 생성(Claude API), 반성 메모를 다음 예측에 프롬프트로 반영하는 시스템. 이력 테이블 + 아코디언 상세 UI.

Requirements: HIST-01, HIST-02, HIST-03, HIST-04, HIST-05, HIST-06, HIST-07

</domain>

<decisions>
## Implementation Decisions

### Local Storage
- **D-01:** localStorage에 JSON으로 저장 — 데이터베이스 없음 (CLAUDE.md)
- **D-02:** "예측 저장" 버튼 클릭 시 저장 — 자동 저장 아님, 사용자가 원하는 결과만 선택적 저장
- **D-03:** 저장 시 회차번호 입력 필수 — 숫자 입력 필드 표시, 당첨번호 비교의 매칭 키로 사용
- **D-04:** 저장 데이터 구조: { roundNumber, machine, date, predictions: [{ strategy, games: number[][] }], actualNumbers?: number[], comparison?: {...}, aiReflection?: string }

### Winning Number Input & Comparison
- **D-05:** 6개 숫자 입력 필드 (1-45 범위) — 한 번호 입력 후 자동 다음 필드 이동, 입력 검증 포함
- **D-06:** 비교 결과는 테이블 형식 — 전략별 5게임의 일치 개수/일치 번호를 테이블로 정리. 전략별 적중률 요약 포함
- **D-07:** 일치 번호는 숫자로 표시 (LottoBall 컴포넌트 재사용 없이 테이블 셀에 번호 나열)

### History Timeline
- **D-08:** 이력 목록은 테이블 형식 — 회차 | 호기 | 날짜 | 최고 적중 | 반성메모 여부 컬럼
- **D-09:** 테이블 행 클릭 시 아코디언 펼침 — 25게임 전체 + 비교 결과 + 반성 메모를 제자리에서 확인
- **D-10:** 최신순 정렬 (내림차순), 페이지네이션 없이 전체 표시 (localStorage 데이터양 제한적)

### AI Reflection System (HIST-05, HIST-06 재해석)
- **D-11:** 반성 메모는 사용자가 작성하지 않음 — AI(Claude API)가 비교 결과를 분석하여 자동 생성
- **D-12:** AI 반성 메모 내용: 과대평가한 번호, 누락한 번호 패턴, 전략별 성과 분석, 다음 예측을 위한 구체적 조정 제안
- **D-13:** 다음 예측 시 반성 메모 반영: 동일 호기의 과거 반성 메모를 프롬프트에 포함하여 Claude API에 가중치 조정 제안을 요청, 그 결과를 예측 파라미터에 반영
- **D-14:** 반영 조건: 동일 호기의 반성 메모만 해당 주 예측에 반영. 다른 호기의 반성은 무시
- **D-15:** Claude API 호출 실패 시 기본 예측 로직으로 fallback — AI 반영 없이 기존 통계 기반 예측 유지

### Strategy Performance Report (HIST-03)
- **D-16:** 전략별 성과 요약 섹션 — 전체 이력 기반으로 각 전략의 평균 적중률, 최고 적중 기록, 총 예측 횟수를 테이블로 표시
- **D-17:** 실패 분석 (HIST-04): 비교 결과에서 자동 도출 — 빠뜨린 번호(실제 당첨인데 예측 안 한 번호)와 과대평가 번호(많이 예측했는데 안 나온 번호)를 번호 목록으로 표시

### Claude's Discretion
- localStorage 키 네이밍 규칙
- 비교 테이블의 세부 스타일링 (색상, 하이라이트)
- 아코디언 애니메이션 여부
- AI 반성 메모의 프롬프트 설계 세부사항
- 전략 성과 리포트의 차트 포함 여부 (선택적)
- 예측 저장 버튼 위치와 디자인

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Existing Frontend Code
- `frontend/src/App.tsx` — 현재 페이지 레이아웃 (이력 섹션 추가 위치)
- `frontend/src/types/lottery.ts` — PredictResponse, STRATEGIES, MACHINE_IDS 타입
- `frontend/src/hooks/usePrediction.ts` — 예측 결과 획득 훅 (저장 데이터 소스)
- `frontend/src/lib/api.ts` — API 패턴 (Claude API 호출 추가 위치)
- `frontend/src/components/LottoBall.tsx` — 번호 표시 컴포넌트
- `frontend/src/components/StrategySection.tsx` — 전략별 결과 표시 패턴

### Backend
- `backend/app/api/routes.py` — API 라우트 패턴 (AI 반성 생성 엔드포인트 추가)
- `backend/app/config.py` — 설정 패턴 (Claude API key 설정)

### Prior Phase Decisions
- `.planning/phases/05-machine-selection-prediction-ui/05-CONTEXT.md` — D-06 로또공 색상, D-09 한국어 UI, D-10 페이지 제목
- `.planning/phases/06-statistics-dashboard/06-CONTEXT.md` — D-03 섹션 구분 패턴 (border-t + 헤더)

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `PredictResponse` 타입: 예측 저장 데이터의 핵심 구조
- `STRATEGIES` / `STRATEGY_LABELS` 상수: 전략별 표시에 재사용
- `LottoBall` 컴포넌트: 번호 비교 결과 표시에 선택적 재사용 가능
- TanStack React Query: 이미 설치/설정 완료 — AI API 호출에 useMutation 활용

### Established Patterns
- Container + Presentational 컴포넌트 분리
- Tailwind v4 유틸리티 클래스 스타일링
- native fetch + JSON 응답 패턴
- bg-card rounded-xl border 카드 패턴 (ChartCard)

### Integration Points
- `App.tsx`: 대시보드 아래에 이력 섹션 추가
- 예측 결과(PredictResponse[])를 저장 함수에 전달
- selectedMachine state 활용 — 동일 호기 반성 메모 필터링
- Backend: Claude API 호출을 위한 새 엔드포인트 필요 (POST /api/reflect)

</code_context>

<specifics>
## Specific Ideas

- AI 반성 메모는 사용자가 아닌 Claude API가 자동 생성 — HIST-05의 "자유 텍스트"를 AI 자동 생성으로 재해석
- 다음 예측 시 동일 호기의 반성 메모를 프롬프트에 포함하여 가중치 조정 — HIST-06의 "참고 자료 표시"를 "실제 예측 반영"으로 확장
- 비교 후 바로 AI 반성 생성 → 저장 → 다음 예측 시 자동 로드 플로우
- 회차번호는 저장 시 필수 입력 — 당첨번호 매칭의 키
- Claude API key는 환경변수 또는 설정에서 관리

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 07-prediction-history-review*
*Context gathered: 2026-03-27*
