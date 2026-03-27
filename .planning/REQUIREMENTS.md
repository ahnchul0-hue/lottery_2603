# Requirements — Lottery Predictor v1

## v1 Requirements

### Machine Selection (호기 선택)
- [x] **MACH-01**: 사용자가 1호기/2호기/3호기 중 하나를 선택할 수 있다
- [x] **MACH-02**: 선택된 호기에 따라 모든 분석과 예측이 해당 호기 데이터만 사용한다
- [x] **MACH-03**: 호기 선택 시 해당 호기의 총 추첨 횟수와 최근 추첨일이 표시된다

### Prediction Engine (예측 엔진)
- [x] **PRED-01**: 빈도 전략 — 호기별 번호 출현 빈도에 시간 감쇠 가중치를 적용하여 5게임 생성
- [x] **PRED-02**: 패턴 전략 — 호기별 최빈 쌍, 연속번호, 끝수 패턴을 분석하여 5게임 생성
- [x] **PRED-03**: 구간 전략 — 호기별 번호 구간대(1-9/10-19/20-29/30-39/40-45) 분포를 반영하여 5게임 생성
- [x] **PRED-04**: 밸런스 전략 — 호기별 홀짝/고저 비율 경향을 반영하여 5게임 생성
- [x] **PRED-05**: 종합 전략 — 위 4가지 전략을 가중 평균하여 5게임 생성
- [x] **PRED-06**: 각 전략에서 생성되는 6개 번호가 1-45 범위 내 중복 없이 오름차순 정렬된다
- [x] **PRED-07**: 25게임 간 최소 다양성 보장 (동일 번호 세트 없음)

### Time Decay (시간 감쇠)
- [x] **DECAY-01**: 지수 감쇠 가중치를 적용한다 (최신 회차 = 높은 가중치, 과거 회차 = 낮은 가중치)
- [x] **DECAY-02**: 감쇠 파라미터(halflife)는 기본값 50으로 설정되며 코드 레벨에서 조정 가능하다

### Analysis Dashboard (분석 대시보드)
- [x] **DASH-01**: 호기별 번호 출현 빈도 바 차트를 표시한다 (1-45번 전체)
- [x] **DASH-02**: 호기별 Hot/Cold 번호 상위 10개를 표시한다
- [x] **DASH-03**: 호기별 번호 편중 히트맵을 표시한다 (3x45 그리드, 기대빈도 대비 편차)
- [x] **DASH-04**: 호기별 홀짝/고저 비율 분포를 차트로 표시한다
- [x] **DASH-05**: 호기별 번호 구간대 분포를 차트로 표시한다
- [x] **DASH-06**: 호기별 총합 범위 및 AC값 분포를 표시한다

### Data Layer (데이터)
- [x] **DATA-01**: new_res.json (800~1216회, 417건)을 로드하여 호기별로 필터링한다
- [x] **DATA-02**: 데이터 로드 시 유효성 검증을 수행한다 (번호 범위, 개수, 정렬)

### UI/UX
- [x] **UI-01**: 상단 영역은 깔끔 모던 스타일 (호기 선택 + 예측 결과 카드)
- [x] **UI-02**: 하단 영역은 데이터 분석 대시보드 스타일 (차트, 통계)
- [ ] **UI-03**: 다크/라이트 모드를 지원한다
- [ ] **UI-04**: 예측 진행 중 로딩 애니메이션을 표시한다
- [ ] **UI-05**: 통계적 면책조항을 표시한다 ("분석 도구이며 당첨 보장 아님")

### Prediction History & Review (예측 기록 및 검증)
- [ ] **HIST-01**: 매 예측 시 생성된 25게임 번호를 회차/호기/전략/날짜와 함께 로컬 저장한다
- [ ] **HIST-02**: 실제 당첨번호를 입력하면 예측 번호와 자동 비교 분석한다 (일치 개수, 전략별 적중률)
- [ ] **HIST-03**: 전략별 성과 리포트를 생성한다 (어떤 전략이 가장 잘 맞았는지)
- [ ] **HIST-04**: 예측 실패 분석 — 빠뜨린 번호 패턴, 과대평가한 번호를 기록한다
- [ ] **HIST-05**: 반성/대책 메모를 기록할 수 있다 (자유 텍스트)
- [ ] **HIST-06**: 과거 반성/대책 내용을 다음 예측 시 참고 자료로 표시한다
- [ ] **HIST-07**: 예측 이력 목록을 볼 수 있다 (회차별 예측 → 결과 → 반성 타임라인)

### Infrastructure (인프라)
- [x] **INFRA-01**: Python FastAPI 백엔드가 localhost에서 실행된다
- [x] **INFRA-02**: React(Vite) 프론트엔드가 localhost에서 실행된다
- [x] **INFRA-03**: 프론트엔드-백엔드 간 CORS가 올바르게 설정된다

## v2 Requirements (Deferred)

- 모바일 반응형 레이아웃
- 슬라이딩 윈도우 설정 (분석 범위 조절)
- 번호 쌍 분석 (최빈 쌍 표시)
- 번호 갭 트래킹 (마지막 출현 이후 경과)
- 전략 설명 카드 (각 전략의 작동 방식 설명)
- 결과 인쇄/내보내기
- 호기 비교 뷰 (3호기 나란히 비교)
- 감쇠 파라미터 UI 슬라이더

## Out of Scope

- 당첨 보장 또는 확률 표시 — 오해 유발, 윤리적 문제
- 로또 구매 자동화 — 번호 추천까지만
- 사용자 계정/로그인 — 불필요
- 원격 배포 (Vercel 등) — 로컬 실행만
- 딥러닝/AI 예측 — 417건으로 부족, 과대포장
- 실시간 데이터 업데이트 — JSON 수동 업데이트

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| INFRA-01 | Phase 1: Foundation & Data Layer | Complete |
| INFRA-02 | Phase 1: Foundation & Data Layer | Complete |
| INFRA-03 | Phase 1: Foundation & Data Layer | Complete |
| DATA-01 | Phase 1: Foundation & Data Layer | Complete |
| DATA-02 | Phase 1: Foundation & Data Layer | Complete |
| DECAY-01 | Phase 2: Time Decay Engine | Complete |
| DECAY-02 | Phase 2: Time Decay Engine | Complete |
| PRED-01 | Phase 3: Prediction Pipeline (Vertical Slice) | Complete |
| PRED-06 | Phase 3: Prediction Pipeline (Vertical Slice) | Complete |
| PRED-02 | Phase 4: Full Prediction Engine | Complete |
| PRED-03 | Phase 4: Full Prediction Engine | Complete |
| PRED-04 | Phase 4: Full Prediction Engine | Complete |
| PRED-05 | Phase 4: Full Prediction Engine | Complete |
| PRED-07 | Phase 4: Full Prediction Engine | Complete |
| MACH-01 | Phase 5: Machine Selection & Prediction UI | Complete |
| MACH-02 | Phase 5: Machine Selection & Prediction UI | Complete |
| MACH-03 | Phase 5: Machine Selection & Prediction UI | Complete |
| UI-01 | Phase 5: Machine Selection & Prediction UI | Complete |
| DASH-01 | Phase 6: Statistics Dashboard | Complete |
| DASH-02 | Phase 6: Statistics Dashboard | Complete |
| DASH-03 | Phase 6: Statistics Dashboard | Complete |
| DASH-04 | Phase 6: Statistics Dashboard | Complete |
| DASH-05 | Phase 6: Statistics Dashboard | Complete |
| DASH-06 | Phase 6: Statistics Dashboard | Complete |
| UI-02 | Phase 6: Statistics Dashboard | Complete |
| HIST-01 | Phase 7: Prediction History & Review | Pending |
| HIST-02 | Phase 7: Prediction History & Review | Pending |
| HIST-03 | Phase 7: Prediction History & Review | Pending |
| HIST-04 | Phase 7: Prediction History & Review | Pending |
| HIST-05 | Phase 7: Prediction History & Review | Pending |
| HIST-06 | Phase 7: Prediction History & Review | Pending |
| HIST-07 | Phase 7: Prediction History & Review | Pending |
| UI-03 | Phase 8: UI/UX Polish | Pending |
| UI-04 | Phase 8: UI/UX Polish | Pending |
| UI-05 | Phase 8: UI/UX Polish | Pending |

---
*Last updated: 2026-03-26 after roadmap creation*
