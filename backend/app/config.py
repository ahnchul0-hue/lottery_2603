from pathlib import Path


class Settings:
    DATA_PATH: Path = Path(__file__).parent.parent / "data" / "new_res.json"
    CORS_ORIGINS: list[str] = ["http://localhost:5173"]
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DECAY_HALFLIFE: int = 30


settings = Settings()
