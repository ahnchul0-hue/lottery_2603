from fastapi import APIRouter, HTTPException, Query

from app.main import data_store
from app.schemas.lottery import (
    HealthResponse,
    MachineDataResponse,
    PredictRequest,
    PredictResponse,
)
from app.schemas.reflection import ReflectRequest, ReflectResponse
from app.schemas.statistics import HeatmapResponse
from app.services.reflection_service import generate_reflection
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
        raise HTTPException(status_code=503, detail="데이터가 아직 로드되지 않았습니다")
    try:
        draws = loader.get_draws_for_machine(machine)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"유효하지 않은 호기입니다: {machine}. 사용 가능: 1호기, 2호기, 3호기",
        )
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
        raise HTTPException(status_code=503, detail="데이터가 아직 로드되지 않았습니다")

    try:
        draws = loader.get_draws_for_machine(request.machine)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"유효하지 않은 호기입니다: {request.machine}. 사용 가능: 1호기, 2호기, 3호기",
        )

    try:
        strategy = get_strategy(request.strategy)
    except KeyError:
        raise HTTPException(
            status_code=400,
            detail=f"유효하지 않은 전략입니다: {request.strategy}. 사용 가능: frequency, pattern, range, balance, composite",
        )

    decay_engine = data_store.get("decay_engine")
    if decay_engine is None:
        raise HTTPException(status_code=503, detail="감쇠 엔진이 초기화되지 않았습니다")

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
        raise HTTPException(status_code=503, detail="데이터가 아직 로드되지 않았습니다")

    rows = compute_heatmap_data(loader._by_machine)
    return HeatmapResponse(rows=rows)


@router.post("/reflect", response_model=ReflectResponse)
def create_reflection(request: ReflectRequest):
    """Generate AI reflection memo from prediction comparison results.

    Uses sync def -- Claude API call is IO-bound, consistent with existing endpoint pattern.
    Per D-11: AI auto-generates reflection, not user-written.
    Per D-12: Analysis includes overestimated numbers, missed patterns, strategy performance, adjustment suggestions.
    Per D-14: Only same-machine reflections are fed back (frontend filters before sending).
    Per D-15: Returns 503 if ANTHROPIC_API_KEY is not configured (graceful degradation).
    """
    try:
        reflection = generate_reflection(
            machine=request.machine,
            round_number=request.round_number,
            comparison_data=request.comparison_data,
            past_reflections=request.past_reflections,
        )
    except ValueError:
        # API key not configured -- graceful degradation per D-15
        raise HTTPException(
            status_code=503,
            detail="AI 반성 기능을 사용할 수 없습니다 (API 키 미설정)",
        )
    except Exception as e:
        # Claude API errors (auth, rate limit, network)
        raise HTTPException(
            status_code=502,
            detail=f"AI 반성 생성에 실패했습니다: {str(e)}",
        )

    return ReflectResponse(
        reflection=reflection,
        model="claude-haiku-4-5",
    )
