from typing import Literal

from pydantic import BaseModel, field_validator


class LotteryDraw(BaseModel):
    round_number: int  # 회차
    machine: Literal["1호기", "2호기", "3호기"]  # 호기
    numbers: list[int]  # 1등_당첨번호
    odd_even_ratio: str  # 홀짝_비율
    high_low_ratio: str  # 고저_비율
    ac_value: int  # AC값
    tail_sum: int  # 끝수합
    total_sum: int  # 총합

    @field_validator("numbers")
    @classmethod
    def validate_numbers(cls, v: list[int]) -> list[int]:
        if len(v) != 6:
            raise ValueError(f"Expected 6 numbers, got {len(v)}")
        if any(n < 1 or n > 45 for n in v):
            raise ValueError(f"Numbers must be 1-45, got {v}")
        if v != sorted(v):
            raise ValueError(f"Numbers must be sorted ascending, got {v}")
        if len(set(v)) != 6:
            raise ValueError(f"Numbers must be unique, got {v}")
        return v


class HealthResponse(BaseModel):
    status: str
    data_loaded: bool
    total_records: int


class MachineDataResponse(BaseModel):
    machine: str
    total_draws: int
    draws: list[LotteryDraw]


class PredictRequest(BaseModel):
    machine: Literal["1호기", "2호기", "3호기"]
    strategy: Literal["frequency", "pattern", "range", "balance"]  # Phase 4 strategies


class PredictResponse(BaseModel):
    games: list[list[int]]  # 5 games, each 6 sorted unique numbers
    strategy: str
    machine: str
