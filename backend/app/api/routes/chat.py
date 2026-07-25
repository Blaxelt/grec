import logging

from fastapi import APIRouter, HTTPException

from app.agents.agent import run_chat
from app.agents.schemas import ChatRequest, ChatResponse
from app.agents.tools import make_tools
from app.api.deps import SessionDep
from app.core.config import settings
from app.models import GameRecommendation

logger = logging.getLogger(__name__)

router = APIRouter(tags=["chat"])

RATE_LIMIT_REPLY = (
    "I'm getting a lot of questions right now and need a short break "
    "(rate limit reached). Please try again in a moment!"
)


@router.post("/chat", response_model=ChatResponse)
def chat(session: SessionDep, body: ChatRequest):
    """Chat with the game-advisor agent."""
    if not settings.chat_model:
        raise HTTPException(status_code=503, detail="Chat assistant is not configured")

    collector: dict[int, GameRecommendation] = {}
    tools = make_tools(session, collector, body.app_ids, body.hours_played)

    try:
        reply = run_chat(tools, body.history, body.message)
    except Exception as e:
        logger.exception("Chat agent failed")
        message = str(e).lower()
        if "resource_exhausted" in message or "rate limit" in message or "429" in message:
            return ChatResponse(reply=RATE_LIMIT_REPLY, games=[])
        raise HTTPException(status_code=500, detail="Chat assistant is currently unavailable") from e

    return ChatResponse(reply=reply, games=list(collector.values()))
