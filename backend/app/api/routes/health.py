from fastapi import APIRouter
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app.core.db import engine
from app.ml.cf_model import cf_model

router = APIRouter(tags=["health"])

@router.get("/health")
def health_check():
    db_status = "ok"
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception as exc:
        db_status = f"error: {exc}"

    cf_status = "loaded" if cf_model.available else "unavailable"

    healthy = db_status == "ok"
    payload = {
        "status": "ok" if healthy else "error",
        "db": db_status,
        "cf_model": cf_status,
    }

    return JSONResponse(content=payload, status_code=200 if healthy else 503)