import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import games, recommendations

app = FastAPI(title="GREC")

cors_origin = os.getenv("CORS_ORIGIN", "http://localhost:5173")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[cors_origin],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(games.router)
app.include_router(recommendations.router)


@app.get("/health", tags=["health"])
def health_check():
    return {"status": "ok"}