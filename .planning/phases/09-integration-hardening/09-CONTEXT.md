# Phase 9: Integration & Hardening - Context

**Gathered:** 2026-03-27
**Status:** Ready for planning

<domain>
## Phase Boundary

전체 앱 통합 검증 + 에지 케이스 처리 + 에러 응답 개선 + pytest 백엔드 통합 테스트. 마지막 phase로서 모든 기능이 함께 동작하는지 확인하고 견고하게 만드는 작업.

Requirements: (cross-cutting — validates all prior requirements work together)

</domain>

<decisions>
## Implementation Decisions

### Error Handling (Success Criteria 2)
- **D-01:** 기존 5개 API 엔드포인트의 입력 검증 강화 — 잘못된 호기명, 잘못된 전략명, 범위 밖 파라미터에 대해 명확한 한국어 에러 메시지 반환
- **D-02:** 글로벌 exception handler 추가하지 않음 — 각 엔드포인트에서 개별적으로 검증. 기존 FastAPI HTTPException 패턴 유지
- **D-03:** React Error Boundary 추가하지 않음 — 현재 범위 밖. TanStack Query의 onError 콜백으로 에러 표시

### Integration Testing (Success Criteria 3)
- **D-04:** pytest + httpx로 FastAPI 백엔드 통합 테스트 — CLAUDE.md에 pytest 이미 명시
- **D-05:** 테스트 커버리지: 전체 사용자 플로우를 API 레벨에서 검증
  - GET /api/health — 서버 상태 확인
  - GET /api/data?machine=X — 호기별 데이터 조회 (유효/무효 호기)
  - POST /api/predict — 5개 전략 예측 (유효/무효 입력)
  - GET /api/statistics/heatmap — 히트맵 데이터 조회
  - POST /api/reflect — AI 반성 생성 (API 키 없을 때 503 확인)
- **D-06:** 프론트엔드 E2E 테스트(Playwright) 작성하지 않음 — 범위 밖, 백엔드 테스트에 집중

### Edge Case Handling (Success Criteria 1)
- **D-07:** 호기 빠른 전환 시 TanStack Query cancelQueries로 진행 중인 mutation 취소 + 이전 쿼리 캐시 무효화
- **D-08:** 빈 데이터/빈 결과 처리 — 존재하지 않는 호기 선택 시 적절한 에러 메시지 표시
- **D-09:** 동시 API 요청 관리 — 예측 중 호기 전환 시 이전 예측 취소 후 새 예측 시작

### Claude's Discretion
- 테스트 파일 구조 (단일 파일 vs 모듈별 분리)
- 에러 메시지 한국어 문구 세부 내용
- TanStack Query 캐시 무효화의 구체적 구현 방식
- 테스트에서의 mock/fixture 설계

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Backend API (테스트 대상)
- `backend/app/api/routes.py` — 전체 5개 엔드포인트 (검증 강화 + 테스트 대상)
- `backend/app/schemas/lottery.py` — PredictRequest, MachineDataResponse 등
- `backend/app/schemas/statistics.py` — HeatmapResponse
- `backend/app/schemas/reflection.py` — ReflectRequest, ReflectResponse
- `backend/app/main.py` — FastAPI app, lifespan, data_store
- `backend/app/config.py` — Settings (ANTHROPIC_API_KEY 포함)

### Frontend (엣지 케이스 처리)
- `frontend/src/App.tsx` — 메인 페이지 (호기 전환 로직)
- `frontend/src/hooks/usePrediction.ts` — 예측 mutation (취소 로직 추가 대상)
- `frontend/src/hooks/useMachineInfo.ts` — 머신 데이터 쿼리
- `frontend/src/hooks/useStatistics.ts` — 통계 계산

### Data
- `backend/new_res.json` — 417건 로또 데이터 (테스트 데이터 소스)

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- FastAPI TestClient (httpx 기반) — pytest-asyncio 불필요, sync 엔드포인트이므로
- TanStack Query: queryClient.cancelQueries(), queryClient.invalidateQueries() 내장 메서드
- 기존 Pydantic 모델로 요청/응답 자동 검증

### Established Patterns
- FastAPI HTTPException(status_code=400, detail="...") 패턴
- sync def 엔드포인트 (CPU-bound)
- useMutation / useQuery 훅 패턴

### Integration Points
- `conftest.py`: FastAPI TestClient 설정
- `App.tsx`: selectedMachine 변경 시 쿼리 취소/무효화 로직 추가
- `usePrediction.ts`: AbortController 또는 mutation 취소 로직

</code_context>

<specifics>
## Specific Ideas

- pytest로 "행복한 경로" + "에러 경로" 모두 테스트
- 잘못된 호기명("4호기"), 잘못된 전략명("invalid"), 빈 body 등 에지 케이스
- reflect 엔드포인트는 ANTHROPIC_API_KEY 없을 때 503 반환 확인 (mock 불필요, 실제 동작 테스트)
- 프론트엔드 호기 전환 시 진행 중인 예측을 취소하여 stale 데이터 방지

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 09-integration-hardening*
*Context gathered: 2026-03-27*
