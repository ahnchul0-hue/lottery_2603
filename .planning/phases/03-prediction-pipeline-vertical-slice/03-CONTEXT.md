# Phase 3: Prediction Pipeline (Vertical Slice) - Context

**Gathered:** 2026-03-26
**Status:** Ready for planning

<domain>
## Phase Boundary

빈도 전략(Frequency Strategy) 1개를 end-to-end로 구현하여 API 요청 → 전략 실행 → 5게임 반환까지의 전체 파이프라인을 증명. Strategy Pattern ABC를 확립하여 Phase 4의 4개 추가 전략이 동일 인터페이스를 따르도록 함.

Requirements: PRED-01, PRED-06

</domain>

<decisions>
## Implementation Decisions

### Number Selection Algorithm
- **D-01:** 확률적 선택 — DecayEngine의 가중 빈도를 확률로 변환하여 `random.choices(population, weights, k=6)`로 6개 번호 선택
- **D-02:** 중복 번호 처리 — choices가 중복을 반환할 수 있으므로, 6개 고유 번호가 나올 때까지 반복 선택 (또는 비복원 추출 방식)
- **D-03:** 결과는 항상 오름차순 정렬

### API Design
- **D-04:** POST /api/predict — JSON body: `{"machine": "1호기", "strategy": "frequency"}`
- **D-05:** 응답 형식: `{"games": [[3,7,15,23,31,42], ...], "strategy": "frequency", "machine": "1호기"}`
- **D-06:** 유효하지 않은 machine/strategy → 400 에러 반환

### Game Diversity
- **D-07:** 최소 차이 보장 — 새 게임이 기존 게임과 4개 이상 같은 번호를 가지면 재생성. 최대 100회 시도
- **D-08:** 100회 시도 후에도 다양성 미충족 시 가장 다양한 결과 사용

### Strategy Pattern
- **D-09:** ABC(Abstract Base Class)로 PredictionStrategy 인터페이스 정의 — `generate(draws, weights) -> list[list[int]]`
- **D-10:** FrequencyStrategy가 첫 번째 구현체
- **D-11:** 전략 모듈 위치: `backend/app/strategies/`

### Claude's Discretion
- Strategy ABC의 정확한 메서드 시그니처
- 테스트 전략 (유닛 + API 통합)
- Pydantic 요청/응답 모델 설계

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Existing Code
- `backend/app/services/decay_engine.py` — DecayEngine 클래스, 가중 빈도 계산 (Phase 3의 핵심 입력)
- `backend/app/services/data_loader.py` — DataLoader, 호기별 데이터 제공
- `backend/app/api/routes.py` — 기존 API 라우트 (health, data)
- `backend/app/schemas/lottery.py` — LotteryDraw 스키마
- `backend/app/config.py` — Settings (DECAY_HALFLIFE=30)

### Research
- `.planning/research/ARCHITECTURE.md` — Strategy Pattern, 빌드 순서
- `.planning/research/FEATURES.md` — 5전략 구조, 생성 방법론
- `.planning/research/PITFALLS.md` — 다양성 부족, 과적합 위험

### Prior Phases
- `.planning/phases/01-foundation-data-layer/01-CONTEXT.md` — 모노레포, 백엔드 사전계산
- `.planning/phases/02-time-decay-engine/02-CONTEXT.md` — halflife=30, 번호 빈도만 감쇠

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `DecayEngine.compute_weighted_frequencies(draws)` → `dict[int, float]` — 번호별 가중 빈도 (1-45)
- `DataLoader.get_draws_for_machine(machine)` → `list[LotteryDraw]`
- 기존 API 라우터 패턴 (`routes.py`)
- 기존 테스트 패턴 (`test_data_loader.py`, `test_decay_engine.py`)

### Established Patterns
- 서비스: `backend/app/services/` (DataLoader, DecayEngine)
- 스키마: `backend/app/schemas/` (Pydantic 모델)
- 라우트: `backend/app/api/routes.py`
- 설정: `backend/app/config.py` (Settings 클래스)

### Integration Points
- `DecayEngine` → `FrequencyStrategy`: 가중 빈도를 전략에 전달
- `routes.py` → Strategy: POST /api/predict 엔드포인트 추가
- `data_store` dict → Strategy: lifespan에서 전략 엔진도 초기화

</code_context>

<specifics>
## Specific Ideas

- Strategy Pattern ABC를 Phase 4에서 확장 가능하도록 깔끔하게 설계
- 확률적 선택으로 매번 다른 결과 생성 (deterministic 아님)
- 다양성 검증: 게임 간 4개 이상 중복 시 재생성

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 03-prediction-pipeline-vertical-slice*
*Context gathered: 2026-03-26*
