# Phase 7: Prediction History & Review - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-03-27
**Phase:** 07-prediction-history-review
**Areas discussed:** 로컬 저장 방식, 당첨번호 입력 & 비교 UI, 이력 타임라인 레이아웃, 반성/대책 메모 시스템

---

## 로컬 저장 방식

### 저장 타이밍

| Option | Description | Selected |
|--------|-------------|----------|
| 예측 즉시 자동 저장 | "번호 예측" 클릭 후 결과가 나오면 자동으로 localStorage에 저장 | |
| "저장" 버튼 클릭 시 | 예측 결과 아래에 "예측 저장" 버튼 추가. 사용자가 원하는 결과만 선택적 저장 | ✓ |
| 회차번호 입력 후 저장 | 예측 시 회차번호를 입력받고, 해당 회차에 매핑하여 저장 | |

**User's choice:** "저장" 버튼 클릭 시
**Notes:** 없음

### 회차번호 처리

| Option | Description | Selected |
|--------|-------------|----------|
| 저장 시 회차번호 입력 | "예측 저장" 버튼 클릭 시 회차번호 입력 필드 표시 | ✓ |
| 자동 추정 (최신 회차+1) | 데이터의 마지막 회차에서 +1한 값을 자동 추정 | |
| 회차번호 없이 날짜만 | 회차 없이 날짜 + 호기로만 기록 | |

**User's choice:** 저장 시 회차번호 입력
**Notes:** 없음

---

## 당첨번호 입력 & 비교 UI

### 입력 방식

| Option | Description | Selected |
|--------|-------------|----------|
| 6개 숫자 필드 | 6개의 숫자 입력 필드 (1-45). 한 번호 입력 후 자동 다음 필드 이동 | ✓ |
| 한 줄 입력 | 콤마/공백으로 구분된 6개 번호를 한 줄로 입력 | |
| 로또공 클릭 선택 | 45개 번호를 로또공 모양으로 표시, 6개 클릭 선택 | |

**User's choice:** 6개 숫자 필드
**Notes:** 없음

### 비교 결과 시각화

| Option | Description | Selected |
|--------|-------------|----------|
| 로또공 색상 하이라이트 | 예측 번호 중 당첨번호와 일치하는 공을 강조 색상으로 표시 + 게임당 일치 개수 | |
| 테이블 형식 | 전략별 5게임의 일치 개수/일치 번호를 테이블로 정리 | ✓ |
| 둘 다 (공 + 테이블) | 로또공 하이라이트로 시각적 표시 + 아래에 전략별 성과 요약 테이블 | |

**User's choice:** 테이블 형식
**Notes:** 없음

---

## 이력 타임라인 레이아웃

### 목록 형식

| Option | Description | Selected |
|--------|-------------|----------|
| 카드 목록 | 회차별 카드로 세로 나열 — 각 카드에 회차, 호기, 날짜, 전략별 일치율 요약 | |
| 테이블 목록 | 회차 / 호기 / 날짜 / 전략별 적중률 / 반성메모 여부 테이블 | ✓ |
| 타임라인 형식 | 세로 타임라인으로 시간순 표시. 예측 → 결과 → 반성 흐름이 시각적 | |

**User's choice:** 테이블 목록
**Notes:** 없음

### 상세 보기

| Option | Description | Selected |
|--------|-------------|----------|
| 아코디언 펼침 | 테이블 행 클릭 시 아래로 펼쳐지는 상세 패널 — 25게임 전체 + 비교결과 + 반성메모 | ✓ |
| 모달 팝업 | 클릭 시 모달 창으로 상세 표시 | |
| 별도 페이지 | 이력 상세 별도 페이지로 이동 (React Router) | |

**User's choice:** 아코디언 펼침
**Notes:** 없음

---

## 반성/대책 메모 시스템

### 메모 작성 주체 (핵심 변경)

**User's choice:** AI(Claude API)가 비교 결과를 분석하여 자동 생성 — 사용자가 작성하지 않음
**Notes:** 원래 HIST-05는 "자유 텍스트 메모 작성"이었으나, 사용자가 AI 자동 생성으로 변경 요청

### AI 반성 메모 예측 반영 방식

| Option | Description | Selected |
|--------|-------------|----------|
| 프롬프트 기반 반영 | 반성 메모를 LLM API(Claude)에 프롬프트로 전달하여 예측 조정 제안을 받고 반영 | ✓ |
| 규칙 기반 자동 반영 | "과대평가 번호의 가중치 감소" 같은 통계적 규칙을 자동 적용 | |
| Phase 7에서는 기록만 | AI 반성메모 자동생성 + 저장만 하고, 예측 반영은 별도 phase로 분리 | |

**User's choice:** 프롬프트 기반 반영
**Notes:** 동일 호기의 반성 메모만 해당 주 예측에 반영. 다른 호기의 반성은 무시.

---

## Claude's Discretion

- localStorage 키 네이밍
- 비교 테이블 세부 스타일링
- 아코디언 애니메이션
- AI 프롬프트 설계
- 전략 성과 리포트 차트 여부

## Deferred Ideas

None — discussion stayed within phase scope
