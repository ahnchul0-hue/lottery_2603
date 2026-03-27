from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.services.data_loader import DataLoader
from app.services.decay_engine import DecayEngine

data_store: dict = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: load and validate data
    loader = DataLoader(settings.DATA_PATH)
    loader.load_and_validate()
    data_store["loader"] = loader
    data_store["decay_engine"] = DecayEngine()
    print(f"Loaded {loader.total_records} lottery records, decay engine ready (halflife={data_store['decay_engine'].halflife})")
    yield
    # Shutdown: cleanup
    data_store.clear()


app = FastAPI(
    title="Lottery Predictor API",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS middleware added immediately after app creation (before routes)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

from app.api.routes import router  # noqa: E402

app.include_router(router, prefix="/api")
