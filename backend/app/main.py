import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import games, recommendations, steam
from app.core.config import settings
from app.ml.cf_model import cf_model

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    cf_model.load()
    if cf_model.available:
        logger.info("CF model preloaded successfully")
    yield

app = FastAPI(title="GREC", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.cors_origin],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(games.router)
app.include_router(recommendations.router)
app.include_router(steam.router)

@app.get("/health", tags=["health"])
def health_check():
    return {"status": "ok"}