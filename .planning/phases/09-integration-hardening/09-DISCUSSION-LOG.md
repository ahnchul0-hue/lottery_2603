# Phase 9: Integration & Hardening - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.

**Date:** 2026-03-27
**Phase:** 09-integration-hardening
**Areas discussed:** 에러 처리 범위, 통합 테스트 범위, 엣지 케이스 처리

---

## 에러 처리 범위

| Option | Description | Selected |
|--------|-------------|----------|
| 기존 엔드포인트 검증 강화 | 기존 5개 API의 입력 검증/에러 메시지를 더 명확하게 | ✓ |
| 글로벌 에러 핸들러 추가 | FastAPI 미들웨어로 글로벌 exception handler 추가 | |
| 프론트엔드 Error Boundary | React Error Boundary 컴포넌트 추가 | |

**User's choice:** 기존 엔드포인트 검증 강화

---

## 통합 테스트 범위

| Option | Description | Selected |
|--------|-------------|----------|
| pytest 백엔드 테스트 | pytest + httpx로 FastAPI 엔드포인트 통합 테스트 | ✓ |
| Playwright E2E | 브라우저 E2E 테스트 | |
| 수동 플로우 체크리스트 | 자동화 없이 수동 검증 항목 문서화 | |

**User's choice:** pytest 백엔드 테스트

---

## 엣지 케이스 처리

| Option | Description | Selected |
|--------|-------------|----------|
| TanStack Query 취소 + 무효화 | 호기 전환 시 cancelQueries + invalidateQueries | ✓ |
| 디바운스 처리 | 호기 선택에 300ms 디바운스 적용 | |
| 현재 상태 유지 | staleTime=Infinity 캐싱으로 충분 | |

**User's choice:** TanStack Query 취소 + 무효화

---

## Claude's Discretion

- 테스트 파일 구조, 에러 메시지 문구, 캐시 무효화 구현 세부사항

## Deferred Ideas

None
