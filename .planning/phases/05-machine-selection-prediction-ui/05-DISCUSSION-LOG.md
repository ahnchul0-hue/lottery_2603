# Phase 5: Machine Selection & Prediction UI - Discussion Log

> **Audit trail only.**

**Date:** 2026-03-27
**Phase:** 05-machine-selection-prediction-ui
**Areas discussed:** Machine Selection, Result Layout, Number Style, Korean Copy

---

## Machine Selection Design

| Option | Description | Selected |
|--------|-------------|----------|
| 호기 번호 카드 | 큰 카드 3개 나란히, 호기번호+추첨횟수+최근회차 | ✓ |
| 미니멀 버튼 | 작은 필 버튼 3개, 선택 후 정보 표시 | |

**User's choice:** 호기 번호 카드 (Recommended)

## Result Card Layout

| Option | Description | Selected |
|--------|-------------|----------|
| 전략별 섹션 | 전략명 헤더 + 5게임 가로, 5섹션 세로 스크롤 | ✓ |
| 탭 스위치 | 전략별 탭, 한 화면에 5게임 | |
| 그리드 테이블 | 5열 x 5행 테이블 | |

**User's choice:** 전략별 섹션 (Recommended)

## Number Display Style

| Option | Description | Selected |
|--------|-------------|----------|
| 로또공 + 색상 코딩 | 동행복권 스타일 원형 배지, 구간별 색상 | ✓ |
| 단순 숫자 칩 | 배경색 없이 숫자만 나열 | |

**User's choice:** 로또공 모양 + 색상 코딩 (Recommended)

## Korean Copy

| Option | Description | Selected |
|--------|-------------|----------|
| 한국어 전략명 | 빈도 전략 / 패턴 전략 등 | |
| 영어+한국어 병기 | Frequency (빈도) / Pattern (패턴) 등 | ✓ |
| 영어만 | Frequency / Pattern 등 | |

**User's choice:** 영어+한국어 병기

## Claude's Discretion

- React 컴포넌트 분리 구조
- API 호출 hooks 설계
- 로딩 상태 표시 방식
- "번호 예측" 버튼 위치/스타일

## Deferred Ideas

None
