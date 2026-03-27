from fastapi import APIRouter, HTTPException, Query

from app.main import data_store
from app.schemas.lottery import (
    HealthResponse,
    MachineDataResponse,
    PredictRequest,
    PredictResponse,
)
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
