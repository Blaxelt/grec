import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from app.api.routes import games, recommendations, steam
from app.ml.cf_model import cf_model

load_dotenv()

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    cf_model.load()
    if cf_model.available:
        logger.info("CF model preloaded successfully")
    yield

app = FastAPI(title="GREC", lifespan=lifespan)

cors_origin = os.getenv("CORS_ORIGIN", "http://localhost:5173")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[cors_origin],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(games.router)
app.include_router(recommendations.router)
app.include_router(steam.router)

@app.get("/health", tags=["health"])
def health_check():
    return {"status": "ok"}