# Phase 4: Full Prediction Engine - Context

**Gathered:** 2026-03-27
**Status:** Ready for planning

<domain>
## Phase Boundary

나머지 4개 전략(패턴/구간/밸런스/종합)을 구현하고 POST /api/predict에서 모든 전략을 지원하여 5전략 x 5게임 = 25게임 완성. Phase 3에서 확립된 Strategy Pattern ABC와 동일한 인터페이스를 따름.

Requirements: PRED-02, PRED-03, PRED-04, PRED-05, PRED-07

</domain>

<decisions>
## Implementation Decisions

### Pattern Strategy (PRED-02)
- **D-01:** Claude's Discretion — 호기별 최빈 쌍, 연속번호, 끝수 패턴을 어떻게 조합할지는 리서치/플래너에게 위임
- **D-02:** 리서치에서 발견된 호기별 데이터 활용: 1호기(22,38), 2호기(7,26), 3호기(13,45) 최빈 쌍 등

### Range Strategy (PRED-03)
- **D-03:** 호기별 구간 비율 반영 — 각 호기의 실제 구간대(1-9/10-19/20-29/30-39/40-45) 출현 비율에 따라 구간별 추출 번호 수를 결정한 후, 구간 내에서 랜덤 선택
- **D-04:** 구간별 번호 수는 비율을 반올림하여 합계가 6이 되도록 조정

### Balance Strategy (PRED-04)
- **D-05:** 호기별 홀짝/고저 비율 경향을 반영하여 번호 생성
- **D-06:** 홀짝 비율과 고저 비율을 동시에 만족하는 번호 세트 생성

### Composite Strategy (PRED-05)
- **D-07:** 가중치 배분 — 빈도 40% / 패턴 20% / 구간 20% / 밸런스 20%
- **D-08:** 4개 전략의 번호별 점수를 가중 평균하여 확률로 변환 후 선택
- **D-09:** 종합 전략은 다른 4개 전략에 의존하므로 마지막에 구현

### Diversity (PRED-07)
- **D-10:** 전략 내 다양성만 관리 — 각 전략 내 5게임에서 4+ 겹침 차단 (Phase 3 방식 유지)
- **D-11:** 전략 간 다양성은 자연스럽게 보장됨 (알고리즘이 다르므로)

### Claude's Discretion
- 패턴 전략의 구체적 알고리즘 설계
- 밸런스 전략에서 홀짝/고저를 동시에 만족시키는 방법
- 종합 전략에서 4개 전략 점수를 통합하는 정확한 방식
- 테스트 전략 (각 전략별 유닛 테스트)

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Existing Code (MUST READ)
- `backend/app/strategies/base.py` — PredictionStrategy ABC (Phase 3에서 확립)
- `backend/app/strategies/frequency.py` — FrequencyStrategy 구현 (참조 패턴)
- `backend/app/strategies/__init__.py` — STRATEGY_MAP 레지스트리
- `backend/app/services/decay_engine.py` — DecayEngine (가중 빈도 계산)
- `backend/app/services/data_loader.py` — DataLoader (호기별 데이터)
- `backend/app/api/routes.py` — POST /api/predict (확장 대상)
- `backend/app/schemas/lottery.py` — PredictRequest/PredictResponse 스키마

### Research
- `.planning/research/FEATURES.md` — 5전략 구조, 생성 방법론
- `.planning/research/ARCHITECTURE.md` — Strategy Pattern 설계
- `.planning/research/PITFALLS.md` — 다양성 부족 위험

### Prior Phases
- `.planning/phases/03-prediction-pipeline-vertical-slice/03-CONTEXT.md` — Strategy ABC, 확률적 선택, 다양성 규칙

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `PredictionStrategy` ABC: `generate(draws, weighted_frequencies) -> list[list[int]]`
- `FrequencyStrategy`: 참조 구현체 — 확률적 선택, _select_unique, diversity enforcement
- `STRATEGY_MAP`: 전략 레지스트리 dict
- `get_strategy(name)`: 전략 조회 함수
- DecayEngine, DataLoader: 데이터 파이프라인

### Established Patterns
- 각 전략은 `strategies/` 디렉토리에 독립 파일
- `__init__.py`에서 STRATEGY_MAP에 등록
- `generate()` 메서드가 `list[list[int]]` (5게임) 반환
- 게임 내 다양성은 4+ 겹침 시 재생성, 최대 100회

### Integration Points
- `strategies/__init__.py`: 4개 신규 전략 등록
- `routes.py`: strategy 파라미터 검증에 새 전략명 포함 (자동 — STRATEGY_MAP 기반)
- PredictRequest의 strategy Literal 타입에 새 전략명 추가

</code_context>

<specifics>
## Specific Ideas

- 사용자가 빈도 전략에 가장 높은 가중치(40%)를 원함 — 빈도 중심 접근
- 패턴 전략은 Claude 재량에 맡김 — 리서치에서 최적 방법 결정
- 각 전략이 FrequencyStrategy와 동일한 인터페이스를 따라야 함 (drop-in replacement)

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 04-full-prediction-engine*
*Context gathered: 2026-03-27*
