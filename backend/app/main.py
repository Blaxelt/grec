from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import games, recommendations

app = FastAPI(title="GREC")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(games.router)
app.include_router(recommendations.router)