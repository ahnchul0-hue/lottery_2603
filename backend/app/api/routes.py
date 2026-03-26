from fastapi import APIRouter, HTTPException, Query

from app.main import data_store
from app.schemas.lottery import HealthResponse, MachineDataResponse

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
