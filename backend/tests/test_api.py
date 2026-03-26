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
