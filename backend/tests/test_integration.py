"""Comprehensive integration test suite for all 5 API endpoints.

Covers:
- Korean error message validation (Task 1 hardening)
- Heatmap endpoint coverage
- Reflect endpoint coverage
- Full user flow sequential tests
- Edge cases (empty string, partial body)
"""

import pytest


# === Section 1: GET /api/health (서버 상태 확인) ===


@pytest.mark.anyio
async def test_health_returns_200_with_loaded_data(client):
    """서버 상태 확인: 200 응답과 데이터 로드 상태 검증."""
    resp = await client.get("/api/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert data["data_loaded"] is True
    assert data["total_records"] == 417


# === Section 2: GET /api/data (호기별 데이터 조회) ===


@pytest.mark.anyio
async def test_data_valid_machine_1(client):
    """1호기 데이터 조회: 200 응답, 134개 추첨 기록."""
    resp = await client.get("/api/data", params={"machine": "1호기"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["machine"] == "1호기"
    assert data["total_draws"] == 134
    assert isinstance(data["draws"], list)


@pytest.mark.anyio
async def test_data_valid_machine_2(client):
    """2호기 데이터 조회: 200 응답, 추첨 기록 존재."""
    resp = await client.get("/api/data", params={"machine": "2호기"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["machine"] == "2호기"
    assert data["total_draws"] > 0


@pytest.mark.anyio
async def test_data_valid_machine_3(client):
    """3호기 데이터 조회: 200 응답, 추첨 기록 존재."""
    resp = await client.get("/api/data", params={"machine": "3호기"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["machine"] == "3호기"
    assert data["total_draws"] > 0


@pytest.mark.anyio
async def test_data_invalid_machine_returns_400(client):
    """유효하지 않은 호기(4호기) 조회: 400 응답, 한국어 에러 메시지."""
    resp = await client.get("/api/data", params={"machine": "4호기"})
    assert resp.status_code == 400
    detail = resp.json()["detail"]
    assert "유효하지 않은 호기" in detail
    assert "4호기" in detail


@pytest.mark.anyio
async def test_data_empty_machine_returns_400(client):
    """빈 문자열 호기 조회: 400 응답, 한국어 에러 메시지."""
    resp = await client.get("/api/data", params={"machine": ""})
    assert resp.status_code == 400
    detail = resp.json()["detail"]
    assert "유효하지 않은 호기" in detail


@pytest.mark.anyio
async def test_data_missing_param_returns_422(client):
    """machine 파라미터 누락: 422 응답 (FastAPI 필수 파라미터)."""
    resp = await client.get("/api/data")
    assert resp.status_code == 422


# === Section 3: POST /api/predict (예측 - 유효/무효 입력) ===


@pytest.mark.anyio
@pytest.mark.parametrize(
    "strategy",
    ["frequency", "pattern", "range", "balance", "composite"],
)
async def test_predict_all_strategies_succeed(client, strategy):
    """모든 전략 성공 검증: 1호기로 5개 전략 각각 200 응답, 5게임 유효 번호."""
    resp = await client.post(
        "/api/predict", json={"machine": "1호기", "strategy": strategy}
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["strategy"] == strategy
    assert data["machine"] == "1호기"
    assert len(data["games"]) == 5
    for game in data["games"]:
        assert len(game) == 6
        assert all(1 <= n <= 45 for n in game)
        assert game == sorted(game)
        assert len(set(game)) == 6


@pytest.mark.anyio
@pytest.mark.parametrize("machine", ["1호기", "2호기", "3호기"])
async def test_predict_all_machines_succeed(client, machine):
    """모든 호기 성공 검증: frequency 전략으로 3개 호기 각각 200 응답."""
    resp = await client.post(
        "/api/predict", json={"machine": machine, "strategy": "frequency"}
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["machine"] == machine
    assert len(data["games"]) == 5


@pytest.mark.anyio
async def test_predict_invalid_machine_returns_422(client):
    """유효하지 않은 호기(4호기) 예측: 422 응답 (Pydantic Literal 검증)."""
    resp = await client.post(
        "/api/predict", json={"machine": "4호기", "strategy": "frequency"}
    )
    assert resp.status_code == 422


@pytest.mark.anyio
async def test_predict_invalid_strategy_returns_422(client):
    """유효하지 않은 전략 예측: 422 응답 (Pydantic Literal 검증)."""
    resp = await client.post(
        "/api/predict", json={"machine": "1호기", "strategy": "nonexistent"}
    )
    assert resp.status_code == 422


@pytest.mark.anyio
async def test_predict_empty_body_returns_422(client):
    """빈 요청 본문 예측: 422 응답."""
    resp = await client.post("/api/predict")
    assert resp.status_code == 422


@pytest.mark.anyio
async def test_predict_partial_body_returns_422(client):
    """부분적 요청 본문 예측 (strategy 누락): 422 응답."""
    resp = await client.post("/api/predict", json={"machine": "1호기"})
    assert resp.status_code == 422


@pytest.mark.anyio
async def test_predict_games_are_valid(client):
    """예측 게임 유효성 상세 검증: 각 게임 6개 번호, 1-45 범위, 정렬, 중복 없음."""
    resp = await client.post(
        "/api/predict", json={"machine": "1호기", "strategy": "frequency"}
    )
    assert resp.status_code == 200
    data = resp.json()
    for i, game in enumerate(data["games"]):
        assert len(game) == 6, f"Game {i}: expected 6 numbers, got {len(game)}"
        assert all(1 <= n <= 45 for n in game), f"Game {i}: numbers out of range {game}"
        assert game == sorted(game), f"Game {i}: not sorted {game}"
        assert len(set(game)) == 6, f"Game {i}: duplicates in {game}"


# === Section 4: GET /api/statistics/heatmap (히트맵) ===


@pytest.mark.anyio
async def test_heatmap_returns_3_rows(client):
    """히트맵 데이터: 200 응답, 정확히 3개 행 (3개 호기)."""
    resp = await client.get("/api/statistics/heatmap")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["rows"]) == 3


@pytest.mark.anyio
async def test_heatmap_row_structure(client):
    """히트맵 행 구조 검증: machine(문자열), deviations(45개 키), total_draws(정수)."""
    resp = await client.get("/api/statistics/heatmap")
    assert resp.status_code == 200
    data = resp.json()
    for row in data["rows"]:
        assert isinstance(row["machine"], str)
        assert isinstance(row["deviations"], dict)
        assert len(row["deviations"]) == 45
        for key in range(1, 46):
            assert str(key) in row["deviations"]
        assert isinstance(row["total_draws"], int)
        assert row["total_draws"] > 0


@pytest.mark.anyio
async def test_heatmap_machines_complete(client):
    """히트맵 호기 완전성: 정확히 1호기, 2호기, 3호기 포함."""
    resp = await client.get("/api/statistics/heatmap")
    assert resp.status_code == 200
    data = resp.json()
    machines = {row["machine"] for row in data["rows"]}
    assert machines == {"1호기", "2호기", "3호기"}


# === Section 5: POST /api/reflect (AI 반성 - API 키 없을 때 503) ===


@pytest.mark.anyio
async def test_reflect_without_api_key_returns_503(client):
    """API 키 미설정 시 반성 요청: 503 응답, 한국어 에러 메시지."""
    from app.config import settings

    original_key = settings.ANTHROPIC_API_KEY
    settings.ANTHROPIC_API_KEY = None
    try:
        resp = await client.post(
            "/api/reflect",
            json={
                "machine": "1호기",
                "round_number": 1200,
                "comparison_data": {"matched": [1, 2, 3], "missed": [4, 5, 6]},
            },
        )
        assert resp.status_code == 503
        detail = resp.json()["detail"]
        assert "API 키" in detail or "사용할 수 없습니다" in detail
    finally:
        settings.ANTHROPIC_API_KEY = original_key


@pytest.mark.anyio
async def test_reflect_missing_body_returns_422(client):
    """빈 요청 본문 반성: 422 응답."""
    resp = await client.post("/api/reflect")
    assert resp.status_code == 422


# === Section 6: Full user flow simulation (전체 사용자 플로우) ===


@pytest.mark.anyio
async def test_full_user_flow_machine_1(client):
    """전체 사용자 플로우 시뮬레이션 (1호기): health -> data -> predict -> heatmap."""
    # Step 1: Health check
    resp = await client.get("/api/health")
    assert resp.status_code == 200
    assert resp.json()["data_loaded"] is True

    # Step 2: Get data for 1호기
    resp = await client.get("/api/data", params={"machine": "1호기"})
    assert resp.status_code == 200
    assert resp.json()["machine"] == "1호기"

    # Step 3: Predict with frequency strategy
    resp = await client.post(
        "/api/predict", json={"machine": "1호기", "strategy": "frequency"}
    )
    assert resp.status_code == 200
    assert len(resp.json()["games"]) == 5

    # Step 4: Predict with all 5 strategies
    for strategy in ["frequency", "pattern", "range", "balance", "composite"]:
        resp = await client.post(
            "/api/predict", json={"machine": "1호기", "strategy": strategy}
        )
        assert resp.status_code == 200, f"Failed for strategy={strategy}"

    # Step 5: Heatmap
    resp = await client.get("/api/statistics/heatmap")
    assert resp.status_code == 200
    assert len(resp.json()["rows"]) == 3


@pytest.mark.anyio
async def test_full_flow_all_machines(client):
    """전체 플로우 - 모든 호기: 각 호기별 데이터 조회 + 5개 전략 예측 성공."""
    for machine in ["1호기", "2호기", "3호기"]:
        # Get data
        resp = await client.get("/api/data", params={"machine": machine})
        assert resp.status_code == 200, f"Data failed for {machine}"
        assert resp.json()["total_draws"] > 0

        # Predict all 5 strategies
        for strategy in ["frequency", "pattern", "range", "balance", "composite"]:
            resp = await client.post(
                "/api/predict", json={"machine": machine, "strategy": strategy}
            )
            assert resp.status_code == 200, f"Predict failed for {machine}/{strategy}"
            data = resp.json()
            assert len(data["games"]) == 5
            for game in data["games"]:
                assert len(game) == 6
                assert all(1 <= n <= 45 for n in game)
