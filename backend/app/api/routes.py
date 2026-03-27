from fastapi import APIRouter, HTTPException, Query

from app.main import data_store
from app.schemas.lottery import (
    HealthResponse,
    MachineDataResponse,
    PredictRequest,
    PredictResponse,
)
from app.schemas.statistics import HeatmapResponse
from app.services.statistics_service import compute_heatmap_data
from app.strategies import get_strategy

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check -- lightweight, async is fine."""
    loader = data_store.get("loader")
    return HealthResponse(
        status="ok",
        data_loaded=loader is not None,
        total_records=loader.total_records if loader else 0,
    )


@router.get("/data", response_model=MachineDataResponse)
def get_machine_data(
    machine: str = Query(
        ..., description="Machine filter: 1호기, 2호기, or 3호기"
    ),
):
    """Return lottery data filtered by machine.

    Uses def (not async def) because future phases will add
    CPU-bound NumPy computation.
    """
    loader = data_store.get("loader")
    if loader is None:
        raise HTTPException(status_code=503, detail="Data not loaded")
    try:
        draws = loader.get_draws_for_machine(machine)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return MachineDataResponse(
        machine=machine,
        total_draws=len(draws),
        draws=draws,
    )


@router.post("/predict", response_model=PredictResponse)
def predict_numbers(request: PredictRequest):
    """Generate prediction numbers using specified strategy.

    Uses sync def because number generation involves CPU-bound random sampling.
    Per D-04: POST /api/predict with JSON body {"machine": "1호기", "strategy": "frequency"}
    Per D-05: Returns {"games": [...], "strategy": "frequency", "machine": "1호기"}
    """
    loader = data_store.get("loader")
    if loader is None:
        raise HTTPException(status_code=503, detail="Data not loaded")

    try:
        draws = loader.get_draws_for_machine(request.machine)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    try:
        strategy = get_strategy(request.strategy)
    except KeyError as e:
        raise HTTPException(status_code=400, detail=str(e))

    decay_engine = data_store.get("decay_engine")
    if decay_engine is None:
        raise HTTPException(status_code=503, detail="Decay engine not initialized")

    weighted_freq = decay_engine.compute_weighted_frequencies(draws)
    games = strategy.generate(draws, weighted_freq)

    return PredictResponse(
        games=games,
        strategy=request.strategy,
        machine=request.machine,
    )


@router.get("/statistics/heatmap", response_model=HeatmapResponse)
def get_heatmap_data():
    """Return per-machine per-number frequency deviation from expected.

    Uses sync def -- CPU-bound computation, consistent with existing pattern.
    Per D-05: Heatmap 3x45 deviation data from backend endpoint.
    Per D-11: Deviation = (actual - expected) / expected.
    """
    loader = data_store.get("loader")
    if loader is None:
        raise HTTPException(status_code=503, detail="Data not loaded")

    rows = compute_heatmap_data(loader._by_machine)
    return HeatmapResponse(rows=rows)
