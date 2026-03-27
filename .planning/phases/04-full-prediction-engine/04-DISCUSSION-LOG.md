# Phase 4: Full Prediction Engine - Discussion Log

> **Audit trail only.**

**Date:** 2026-03-27
**Phase:** 04-full-prediction-engine
**Areas discussed:** Pattern Strategy, Range Strategy, Composite Weights, 25-Game Diversity

---

## Pattern Strategy

| Option | Description | Selected |
|--------|-------------|----------|
| 쌍+연속+끝수 통합 | 최빈 쌍 포함 + 연속번호 + 끝수 분포 종합 | |
| 쌍 중심 | 최빈 쌍 기반으로 나머지 채우기 | |
| Claude에게 맡김 | 리서치 기반 결정 | ✓ |

**User's choice:** Claude에게 맡김

---

## Range Strategy

| Option | Description | Selected |
|--------|-------------|----------|
| 호기별 구간 비율 반영 | 실제 구간대 출현 비율로 구간별 추출 수 결정 | ✓ |
| 균등 구간 배분 | 각 구간 1-2개씩 균등 추출 | |

**User's choice:** 호기별 구간 비율 반영 (Recommended)

---

## Composite Strategy Weights

| Option | Description | Selected |
|--------|-------------|----------|
| 30/25/20/25 | 리서치 추천 배분 | |
| 균등 25/25/25/25 | 동등 영향력 | |
| 빈도 중심 40/20/20/20 | 빈도에 더 큰 영향력 | ✓ |

**User's choice:** 빈도 중심 40/20/20/20

---

## 25-Game Diversity

| Option | Description | Selected |
|--------|-------------|----------|
| 전략 내 다양성만 | 각 전략 내 5게임만 4+ 겹침 차단 | ✓ |
| 전체 25게임 다양성 | 25게임 전체에서 4+ 겹침 차단 | |

**User's choice:** 전략 내 다양성만 (Recommended)

---

## Claude's Discretion

- 패턴 전략 구체적 알고리즘
- 밸런스 전략 홀짝/고저 동시 충족 방법
- 종합 전략 점수 통합 방식
- 테스트 전략

## Deferred Ideas

None
