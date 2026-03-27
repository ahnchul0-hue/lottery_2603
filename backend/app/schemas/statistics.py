from pydantic import BaseModel


class HeatmapRow(BaseModel):
    machine: str  # "1호기", "2호기", "3호기"
    deviations: dict[str, float]  # {"1": 0.123, "2": -0.05, ...} keys "1"-"45"
    total_draws: int  # number of draws for this machine


class HeatmapResponse(BaseModel):
    rows: list[HeatmapRow]  # exactly 3 rows
