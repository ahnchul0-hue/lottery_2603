# Phase 2: Time Decay Engine - Context

**Gathered:** 2026-03-26
**Status:** Ready for planning

<domain>
## Phase Boundary

지수 감쇠 가중치 모듈을 독립적으로 구현하여, 최신 회차에 높은 가중치/과거 회차에 낮은 가중치를 부여하는 재사용 가능한 엔진 구축.

Requirements: DECAY-01, DECAY-02

</domain>

<decisions>
## Implementation Decisions

### Decay Function
- **D-01:** 지수 감쇠 함수 사용 — `weight = 0.5 ^ (draws_since / halflife)`
- **D-02:** halflife 기본값 = **30** (공격적 설정 — ~7개월 전 데이터가 50% 가치)
- **D-03:** halflife는 코드 레벨에서 변경 가능하도록 설정 파라미터화 (config.py에 DECAY_HALFLIFE)

### Weight Application Scope
- **D-04:** 감쇠 가중치는 **번호 빈도(1-45 각 번호의 출현 빈도)**에만 적용
- **D-05:** 홀짝/고저/구간/총합/AC값 등 기타 통계는 단순 비율 유지 (감쇠 미적용)

### Module Design
- **D-06:** 독립 모듈로 구현 — `backend/app/services/decay_engine.py`
- **D-07:** DataLoader에서 데이터를 받아 가중치를 계산하는 구조 (DataLoader → DecayEngine)
- **D-08:** 입력: 호기별 필터된 LotteryDraw 리스트, 출력: 번호별(1-45) 가중 빈도 딕셔너리

### Claude's Discretion
- DecayEngine 클래스 vs 함수 기반 설계
- 테스트 전략 (단위 테스트 범위)
- numpy 사용 여부 (순수 Python으로도 가능)

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Existing Code
- `backend/app/services/data_loader.py` — DataLoader 클래스, 감쇠 엔진의 입력 데이터 소스
- `backend/app/schemas/lottery.py` — LotteryDraw Pydantic 모델, 감쇠 계산의 데이터 스키마
- `backend/app/config.py` — Settings 클래스, DECAY_HALFLIFE 설정 추가 위치

### Research
- `.planning/research/STACK.md` — pandas ewm, numpy 등 기술 스택
- `.planning/research/ARCHITECTURE.md` — Strategy Pattern, 감쇠 가중치 설계
- `.planning/research/PITFALLS.md` — 시간 감쇠 파라미터화 주의점

### Prior Phase
- `.planning/phases/01-foundation-data-layer/01-CONTEXT.md` — Phase 1 결정사항 (모노레포, 백엔드 사전계산 등)

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `DataLoader.get_by_machine()` — 호기별 필터된 LotteryDraw 리스트 반환
- `LotteryDraw.round_number` — 회차 번호 (가중치 계산의 기준)
- `Settings` (config.py) — 설정 관리 클래스

### Established Patterns
- 서비스 레이어: `backend/app/services/` 디렉토리에 독립 모듈
- Pydantic 스키마: `backend/app/schemas/` 디렉토리
- 테스트: `backend/tests/` 디렉토리, pytest 사용

### Integration Points
- `data_loader.py` → `decay_engine.py`: DataLoader가 제공하는 LotteryDraw 리스트를 입력으로 사용
- `config.py`: DECAY_HALFLIFE 설정 추가
- 향후 Phase 3의 Strategy가 DecayEngine의 가중 빈도를 소비

</code_context>

<specifics>
## Specific Ideas

- 사용자가 공격적 감쇠(halflife=30)를 선택함 — 최근 데이터를 더 강조하고 싶어함
- 번호 빈도에만 적용하고 나머지 통계는 단순 비율 유지 — 과도한 복잡성 회피
- Phase 3의 Strategy Pattern과 자연스럽게 연결되도록 인터페이스 설계 필요

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 02-time-decay-engine*
*Context gathered: 2026-03-26*
