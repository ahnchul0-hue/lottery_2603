# Phase 6: Statistics Dashboard - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-03-27
**Phase:** 06-statistics-dashboard
**Areas discussed:** 대시보드 레이아웃, 통계 계산 위치, 차트 인터랙션 수준, 히트맵 디자인

---

## 대시보드 레이아웃

| Option | Description | Selected |
|--------|-------------|----------|
| 세로 스크롤 | 모든 차트를 세로로 나열. 예측 결과 아래로 자연스럽게 스크롤. 단순하고 모바일 친화적 | ✓ |
| 탭 기반 그룹화 | 2~3개 탭으로 그룹화 (빈도분석/분포분석/종합통계). 한 번에 보이는 차트 수 줄임 | |
| 2칸 그리드 | 작은 차트들을 2칸 그리드로 배치. 한 눈에 더 많은 정보 표시. 히트맵만 full-width | |

**User's choice:** 세로 스크롤
**Notes:** 없음

### 영역 구분

| Option | Description | Selected |
|--------|-------------|----------|
| 섹션 헤더 + 구분선 | '통계 분석' 헤더 텍스트 + 수평 구분선(border-t). 간결하고 쉽게 구분 | ✓ |
| 배경색 대비 | 예측 영역은 bg-surface, 대시보드는 약간 다른 배경색으로 영역 구분 | |
| 섹션 헤더 + 배경색 둘 다 | 헤더 텍스트 + 배경색 대비 모두 사용 | |

**User's choice:** 섹션 헤더 + 구분선
**Notes:** 없음

---

## 통계 계산 위치

| Option | Description | Selected |
|--------|-------------|----------|
| 프론트엔드 계산 | draws 데이터가 이미 있으므로 JS에서 직접 계산. 새 API 불필요 | |
| 백엔드 API 추가 | 새 GET /api/statistics?machine=X 엔드포인트 추가. 서버에서 NumPy/Pandas로 계산 | |
| 하이브리드 | 간단한 계산은 프론트엔드, 복잡한 분석은 백엔드 API | ✓ |

**User's choice:** 하이브리드
**Notes:** 히트맵 3x45 편차 데이터만 백엔드 API, 나머지(빈도/비율/구간/총합/AC값)는 프론트엔드

---

## 차트 인터랙션 수준

| Option | Description | Selected |
|--------|-------------|----------|
| 호버 툴팁 | 바/셀/포인트에 마우스 올리면 상세 수치 툴팁 표시. Recharts 기본 Tooltip | ✓ |
| 툴팁 + 번호 하이라이트 | 호버시 툴팁 + 해당 번호의 바/셀 강조 표시 | |
| 툴팁 + 클릭 필터링 | 바를 클릭하면 해당 번호가 포함된 회차 목록 표시 등 드릴다운 상세 분석 | |

**User's choice:** 호버 툴팁
**Notes:** 없음

---

## 히트맵 디자인 (DASH-03)

### 색상 스킴

| Option | Description | Selected |
|--------|-------------|----------|
| 빨강-파랑 대비 | 편중=빨간색, 부족=파란색, 기대치=흰색/회색. 직관적인 diverging 색상 | ✓ |
| 녹색-노란-빨강 (신호등) | 부족=녹색, 기대치=노란, 편중=빨강. 온도 감각의 전통적 히트맵 색상 | |
| 단색 그라데이션 | 연한 파랑~진한 파랑 단색 그라데이션. 단순하지만 편차 방향 구분 어려움 | |

**User's choice:** 빨강-파랑 대비
**Notes:** 없음

### 구현 방식

| Option | Description | Selected |
|--------|-------------|----------|
| HTML 그리드 | CSS Grid/Flexbox + div로 직접 구현. 135개 셀에 색상 + 툴팁. 가볍고 완전한 디자인 제어 | ✓ |
| Recharts ScatterChart | ScatterChart + 커스텀 Cell로 히트맵 흉내. 통일성 있지만 커스터마이징 많이 필요 | |
| SVG 직접 그리기 | SVG rect 요소로 직접 그리기. 완전한 자유도지만 구현량 많음 | |

**User's choice:** HTML 그리드
**Notes:** 없음

---

## Claude's Discretion

- 차트 카드 스타일링 (기존 패턴 따름)
- 각 차트의 세부 Recharts 설정
- 통계 계산 훅 분리 구조
- Hot/Cold 표시 형식
- 총합/AC값 차트 타입

## Deferred Ideas

None — discussion stayed within phase scope
