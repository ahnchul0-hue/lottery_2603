# Phase 1: Foundation & Data Layer - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-03-26
**Phase:** 01-foundation-data-layer
**Areas discussed:** Project Structure, API Response, Data Loading, Development Environment

---

## Project Structure

| Option | Description | Selected |
|--------|-------------|----------|
| 모노레포 | 루트에 backend/ + frontend/ 폴더. 하나의 git 저장소로 관리 간편 | ✓ |
| 플랫 구조 | 루트에 Python+React 혼합. 간단하지만 커지면 복잡 | |
| Claude에게 맡김 | 리서치 결과 기반으로 최적 구조 결정 | |

**User's choice:** 모노레포 (Recommended)
**Notes:** Preview에서 보여준 트리 구조 확인 후 선택

---

## API Response Design

| Option | Description | Selected |
|--------|-------------|----------|
| 백엔드 사전계산 | API가 호기별 통계를 계산해서 내려줌. 프론트는 표시만 | ✓ |
| 프론트엔드 계산 | API는 원데이터만, 프론트에서 JS로 통계 계산 | |
| Claude에게 맡김 | 리서치 결과 기반 결정 | |

**User's choice:** 백엔드 사전계산 (Recommended)
**Notes:** None

---

## Data Loading Strategy

| Option | Description | Selected |
|--------|-------------|----------|
| 서버 시작 시 메모리 | FastAPI 기동 시 JSON 전체 로드 + 호기별 필터 캐시 | ✓ |
| 요청마다 읽기 | API 호출 시마다 JSON 파일 읽기 | |
| Claude에게 맡김 | 리서치 결과 기반 결정 | |

**User's choice:** 서버 시작 시 메모리 (Recommended)
**Notes:** 417건이라 경량

---

## Development Environment

| Option | Description | Selected |
|--------|-------------|----------|
| uv | Rust 기반, pip+venv 대체, 10-100배 빠름 | ✓ |
| pip + venv | 전통적, 별도 설치 불필요 | |

**User's choice:** uv (Recommended)

| Option | Description | Selected |
|--------|-------------|----------|
| 8000 / 5173 | FastAPI 기본 8000, Vite 기본 5173 | ✓ |
| 직접 지정 | 다른 포트 | |

**User's choice:** 8000 / 5173 (Recommended)
**Notes:** None

---

## Claude's Discretion

- FastAPI 라우터 구조 (단일 파일 vs 분리)
- Pydantic 모델 설계 상세
- React 초기 컴포넌트 구조

## Deferred Ideas

None
