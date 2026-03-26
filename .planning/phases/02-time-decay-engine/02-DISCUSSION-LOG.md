# Phase 2: Time Decay Engine - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-03-26
**Phase:** 02-time-decay-engine
**Areas discussed:** Decay Function, Weight Application Scope, Module Design

---

## Decay Function

| Option | Description | Selected |
|--------|-------------|----------|
| 지수 감쇠 | weight = 0.5^(draws_since/halflife). 자연스러운 감쇠, pandas ewm 지원 | ✓ |
| 선형 감쇠 | weight = max(0, 1 - draws_since/window). 단순하지만 절대점 존재 | |

**User's choice:** 지수 감쇠 (Recommended)

| Option | Description | Selected |
|--------|-------------|----------|
| 50 | ~1년 전 50% 가치. 최근성과 히스토리 균형 | |
| 30 (공격적) | ~7개월 전 50% 가치. 최근 데이터 강조 | ✓ |
| 100 (보수적) | ~2년 전 50% 가치. 히스토리 엄중 | |

**User's choice:** 30 (공격적)
**Notes:** 사용자가 최근 데이터를 더 중시하는 공격적 접근 선호

---

## Weight Application Scope

| Option | Description | Selected |
|--------|-------------|----------|
| 모든 통계 | 번호 빈도 + 홀짝/고저/구간/총합/AC 모두 가중치 적용 | |
| 번호 빈도만 | 각 번호(1-45) 출현 빈도에만 가중치. 나머지는 단순 비율 | ✓ |

**User's choice:** 번호 빈도만

---

## Module Design

| Option | Description | Selected |
|--------|-------------|----------|
| 독립 모듈 | backend/app/services/decay_engine.py로 분리 | ✓ |
| DataLoader 확장 | DataLoader 클래스에 감쇠 메서드 추가 | |

**User's choice:** 독립 모듈 (Recommended)

---

## Claude's Discretion

- DecayEngine 클래스 vs 함수 기반 설계
- 테스트 전략
- numpy 사용 여부

## Deferred Ideas

None
