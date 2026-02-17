from fastapi import FastAPI

from app.api.routes import recommendations

app = FastAPI(title="GREC")

app.include_router(recommendations.router)