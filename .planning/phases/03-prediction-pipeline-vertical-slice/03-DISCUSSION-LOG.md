# Phase 3: Prediction Pipeline (Vertical Slice) - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.

**Date:** 2026-03-26
**Phase:** 03-prediction-pipeline-vertical-slice
**Areas discussed:** Number Selection Algorithm, API Design, Game Diversity

---

## Number Selection Algorithm

| Option | Description | Selected |
|--------|-------------|----------|
| 확률적 선택 | 가중 빈도를 확률로 변환, random.choices로 선택 | ✓ |
| 상위 N개에서 조합 | 빈도 상위 15-20개에서 6개 랜덤 선택 | |

**User's choice:** 확률적 선택 (Recommended)

---

## API Design

| Option | Description | Selected |
|--------|-------------|----------|
| JSON body | POST {"machine": "1호기", "strategy": "frequency"} | ✓ |
| Query params | POST /api/predict?machine=1호기&strategy=frequency | |

**User's choice:** JSON body (Recommended)

---

## Game Diversity

| Option | Description | Selected |
|--------|-------------|----------|
| 최소 차이 보장 | 4개 이상 겹치면 재생성, 최대 100회 시도 | ✓ |
| 완전 중복만 차단 | 똑같은 6개만 차단 | |

**User's choice:** 최소 차이 보장 (Recommended)

---

## Claude's Discretion

- Strategy ABC 메서드 시그니처
- 테스트 전략
- Pydantic 요청/응답 모델

## Deferred Ideas

None
