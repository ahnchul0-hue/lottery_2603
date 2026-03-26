# Lottery Predictor — 호기별 로또 번호 예측 웹앱

## What This Is

사용자가 로또 추첨기(1호기/2호기/3호기)를 선택하면, 호기별 역대 당첨 데이터를 분석하여 5가지 전략 x 5게임 = **총 25게임의 예측 번호**를 제공하는 웹 애플리케이션.

## Core Value

**호기별 특성 기반 예측**: 단순 랜덤이 아닌, 각 호기의 통계적 특성(편중 번호, 빈도, 패턴)을 심층 분석하고 시간 감쇠 가중치를 적용하여 의미 있는 번호 조합을 생성한다.

## Context

### 데이터 소스
- `new_res.json`: 800~1216회차 로또 당첨번호 + 호기 정보 (417건)
- 각 항목: 회차, 호기, 당첨번호 6개, 홀짝비율, 고저비율, AC값, 끝수합, 총합

### 핵심 개념
- **호기(추첨기)**: 로또 추첨에 사용되는 3대의 기계. 4~5회씩 로테이션으로 운영
- **시간 감쇠 가중치**: 최신 회차 → 높은 가중치, 과거 회차 → 낮은 가중치. 최근에 나온 번호일수록 다시 나올 가능성이 높다고 판단
- **5세트 전략**: 서로 다른 분석 관점으로 다양성 있는 번호 조합 생성

### 이전 분석 결과 (대화에서 확인)
- 카이제곱 검정상 호기 간 번호 분포에 통계적 유의차 없음 (174회 표본)
- 그러나 관찰된 경향성 존재:
  - 1호기: 10(x2.9), 37, 38, 30 편중, AC=5 비율 높음 (번호 분산)
  - 2호기: 7(x1.9), 26(x2.3) 편중, 총합 변동폭 큼
  - 3호기: 35, 15(x2.1), 43(x2.3) 편중, 같은 끝수 비율 높음(79.7%)
- 호기별 최빈 쌍: 1호기(22,38), 2호기(7,26), 3호기(13,45)

## Requirements

### Validated

(None yet — ship to validate)

### Active

- [ ] 호기 선택 UI (1호기/2호기/3호기)
- [ ] 호기별 역대 데이터 분석 엔진
- [ ] 시간 감쇠 가중치 적용 (최신 회차 → 높은 가중치)
- [ ] 5가지 전략별 번호 생성
  - 빈도 전략: 호기별 번호 출현 빈도 + 가중치
  - 패턴 전략: 호기별 최빈 쌍/연속번호/끝수 패턴
  - 구간 전략: 호기별 구간대(1-9, 10-19, 20-29, 30-39, 40-45) 분포
  - 홀짝밸런스 전략: 호기별 홀짝/고저 비율 경향 반영
  - 종합 전략: 위 4가지 전략 종합 가중 평균
- [ ] 전략당 5게임 생성 (총 25게임)
- [ ] 예측 결과 표시 UI
- [ ] 호기별 통계 분석 대시보드
- [ ] 방법론 리서치 후 사전 제안/확인 프로세스

### Out of Scope

- 실제 당첨 보장/확률 표시 — 예측 도구일 뿐
- 로또 구매 자동화 — 번호 추천까지만
- 사용자 계정/로그인 — 불필요
- 원격 배포 — 로컬 실행만

## Tech Stack

- **Frontend**: React (Vite)
- **Backend**: Python (FastAPI or Flask)
- **Data**: `new_res.json` (정적 JSON)
- **Deployment**: localhost 로컬 실행

## User Flow

1. 웹 접속 (localhost)
2. 호기 선택 (1호기 / 2호기 / 3호기 버튼)
3. "번호 예측" 클릭
4. 분석 진행 → 5세트 x 5게임 = 25게임 결과 표시
5. 하단에 호기별 통계 분석 대시보드 확인 가능

## UI Design

- **상단**: 깔끔 모던 — 호기 선택 + 예측 결과 카드
- **하단**: 데이터 분석 대시보드 — 차트, 통계, 호기별 비교

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| React + Python 분리 | 프론트 UX와 데이터 분석 최적화 분리 | — Pending |
| 시간 감쇠 가중치 방식 | 최신 데이터의 유의미성 반영 | — 리서치 후 결정 |
| 5전략 구조 | 다양한 분석 관점으로 번호 다양성 확보 | — 리서치 후 결정 |

## Methodology

**방법론 확정 프로세스:**
1. `/loop` 20회로 호기별 특성 심층 분석 수행
2. 리서치를 통해 시간 감쇠/가중치 방법론 탐색
3. 방법론 제안서를 사용자에게 제시
4. 사용자 확인 후 구현 착수

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd:transition`):
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone** (via `/gsd:complete-milestone`):
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-03-26 after initialization*
