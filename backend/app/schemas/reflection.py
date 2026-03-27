from pydantic import BaseModel


class ReflectRequest(BaseModel):
    machine: str
    round_number: int
    comparison_data: dict
    past_reflections: list[str] | None = None


class ReflectResponse(BaseModel):
    reflection: str
    model: str
