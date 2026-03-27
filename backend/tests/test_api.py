import pytest


@pytest.mark.anyio
async def test_health_check(client):
    """GET /api/health returns 200 with correct data."""
    resp = await client.get("/api/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert data["data_loaded"] is True
    assert data["total_records"] == 417


@pytest.mark.anyio
async def test_cors_headers(client):
    """CORS allows requests from http://localhost:5173."""
    resp = await client.options(
        "/api/health",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert resp.headers.get("access-control-allow-origin") == "http://localhost:5173"


@pytest.mark.anyio
async def test_get_data_machine_1(client):
    """GET /api/data?machine=1호기 returns 200 with 134 draws."""
    resp = await client.get("/api/data", params={"machine": "1호기"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["machine"] == "1호기"
    assert data["total_draws"] == 134


@pytest.mark.anyio
async def test_get_data_invalid_machine(client):
    """GET /api/data?machine=4호기 returns 400."""
    resp = await client.get("/api/data", params={"machine": "4호기"})
    assert resp.status_code == 400


@pytest.mark.anyio
async def test_get_data_missing_param(client):
    """GET /api/data (no machine param) returns 422."""
    resp = await client.get("/api/data")
    assert resp.status_code == 422


# --- POST /api/predict integration tests ---


@pytest.mark.anyio
async def test_predict_frequency_success(client):
    """POST /api/predict with valid machine and strategy returns 200 with 5 games."""
    resp = await client.post(
        "/api/predict", json={"machine": "1호기", "strategy": "frequency"}
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["strategy"] == "frequency"
    assert data["machine"] == "1호기"
    assert isinstance(data["games"], list)
    assert len(data["games"]) == 5


@pytest.mark.anyio
async def test_predict_response_valid_numbers(client):
    """Each game has exactly 6 unique numbers in [1, 45], sorted ascending."""
    resp = await client.post(
        "/api/predict", json={"machine": "1호기", "strategy": "frequency"}
    )
    assert resp.status_code == 200
    data = resp.json()
    for game in data["games"]:
        assert len(game) == 6, f"Expected 6 numbers, got {len(game)}"
        assert all(1 <= n <= 45 for n in game), f"Numbers out of range: {game}"
        assert game == sorted(game), f"Numbers not sorted: {game}"
        assert len(set(game)) == 6, f"Duplicate numbers: {game}"


@pytest.mark.anyio
async def test_predict_diversity(client):
    """No pair of games shares 4 or more numbers (MAX_OVERLAP=3)."""
    resp = await client.post(
        "/api/predict", json={"machine": "1호기", "strategy": "frequency"}
    )
    assert resp.status_code == 200
    games = resp.json()["games"]
    for i in range(len(games)):
        for j in range(i + 1, len(games)):
            shared = len(set(games[i]) & set(games[j]))
            assert shared <= 3, (
                f"Games {i} and {j} share {shared} numbers: {games[i]} & {games[j]}"
            )


@pytest.mark.anyio
async def test_predict_all_machines(client):
    """POST /api/predict works for each of 1호기, 2호기, 3호기."""
    for machine in ["1호기", "2호기", "3호기"]:
        resp = await client.post(
            "/api/predict", json={"machine": machine, "strategy": "frequency"}
        )
        assert resp.status_code == 200, f"Failed for machine={machine}"
        data = resp.json()
        assert data["machine"] == machine
        assert len(data["games"]) == 5


@pytest.mark.anyio
async def test_predict_invalid_machine(client):
    """POST /api/predict with invalid machine returns 422 (Pydantic Literal validation)."""
    resp = await client.post(
        "/api/predict", json={"machine": "4호기", "strategy": "frequency"}
    )
    assert resp.status_code == 422


@pytest.mark.anyio
async def test_predict_invalid_strategy(client):
    """POST /api/predict with invalid strategy returns 422 (Pydantic Literal validation)."""
    resp = await client.post(
        "/api/predict", json={"machine": "1호기", "strategy": "nonexistent"}
    )
    assert resp.status_code == 422


@pytest.mark.anyio
async def test_predict_missing_body(client):
    """POST /api/predict with no JSON body returns 422."""
    resp = await client.post("/api/predict")
    assert resp.status_code == 422


# --- Phase 4 integration tests: all 5 strategies ---


@pytest.mark.anyio
async def test_predict_pattern_success(client):
    """POST /api/predict with strategy=pattern returns 200 + 5 valid games."""
    resp = await client.post(
        "/api/predict", json={"machine": "1호기", "strategy": "pattern"}
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["strategy"] == "pattern"
    assert len(data["games"]) == 5


@pytest.mark.anyio
async def test_predict_range_success(client):
    """POST /api/predict with strategy=range returns 200 + 5 valid games."""
    resp = await client.post(
        "/api/predict", json={"machine": "1호기", "strategy": "range"}
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["strategy"] == "range"
    assert len(data["games"]) == 5


@pytest.mark.anyio
async def test_predict_balance_success(client):
    """POST /api/predict with strategy=balance returns 200 + 5 valid games."""
    resp = await client.post(
        "/api/predict", json={"machine": "1호기", "strategy": "balance"}
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["strategy"] == "balance"
    assert len(data["games"]) == 5


@pytest.mark.anyio
async def test_predict_composite_success(client):
    """POST /api/predict with strategy=composite returns 200 + 5 valid games."""
    resp = await client.post(
        "/api/predict", json={"machine": "1호기", "strategy": "composite"}
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["strategy"] == "composite"
    assert len(data["games"]) == 5


@pytest.mark.anyio
@pytest.mark.parametrize(
    "strategy,machine",
    [
        (s, m)
        for s in ["frequency", "pattern", "range", "balance", "composite"]
        for m in ["1호기", "2호기", "3호기"]
    ],
)
async def test_predict_all_strategies_all_machines(client, strategy, machine):
    """POST /api/predict succeeds for every (strategy, machine) combo (PRED-07)."""
    resp = await client.post(
        "/api/predict", json={"machine": machine, "strategy": strategy}
    )
    assert resp.status_code == 200, (
        f"Failed for strategy={strategy}, machine={machine}"
    )
    data = resp.json()
    assert data["strategy"] == strategy
    assert data["machine"] == machine
    assert len(data["games"]) == 5


@pytest.mark.anyio
@pytest.mark.parametrize(
    "strategy",
    ["frequency", "pattern", "range", "balance", "composite"],
)
async def test_predict_all_strategies_valid_numbers(client, strategy):
    """For each strategy, verify 6 unique sorted numbers in [1,45] per game."""
    resp = await client.post(
        "/api/predict", json={"machine": "1호기", "strategy": strategy}
    )
    assert resp.status_code == 200
    data = resp.json()
    for game in data["games"]:
        assert len(game) == 6, f"[{strategy}] Expected 6 numbers, got {len(game)}"
        assert all(1 <= n <= 45 for n in game), (
            f"[{strategy}] Numbers out of range: {game}"
        )
        assert game == sorted(game), f"[{strategy}] Numbers not sorted: {game}"
        assert len(set(game)) == 6, f"[{strategy}] Duplicate numbers: {game}"


@pytest.mark.anyio
async def test_no_identical_games_across_full_prediction(client):
    """For one machine, all 5 strategies x 5 games = 25 games, no two identical (D-11)."""
    all_games_as_tuples: list[tuple[int, ...]] = []
    for strategy in ["frequency", "pattern", "range", "balance", "composite"]:
        resp = await client.post(
            "/api/predict", json={"machine": "1호기", "strategy": strategy}
        )
        assert resp.status_code == 200
        games = resp.json()["games"]
        for game in games:
            all_games_as_tuples.append(tuple(game))

    assert len(all_games_as_tuples) == 25, (
        f"Expected 25 games, got {len(all_games_as_tuples)}"
    )
    unique_games = set(all_games_as_tuples)
    assert len(unique_games) == 25, (
        f"Expected 25 unique games, got {len(unique_games)}. "
        f"Duplicates detected among 5 strategies x 5 games."
    )
