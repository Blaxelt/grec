import logging

from fastapi import APIRouter, HTTPException
from langgraph.errors import GraphRecursionError
from sqlmodel import Session

from app.agents.agent import run_chat
from app.agents.schemas import ChatRequest, ChatResponse
from app.agents.tools import make_tools
from app.core.config import settings
from app.core.db import engine
from app.models import GameRecommendation

logger = logging.getLogger(__name__)

router = APIRouter(tags=["chat"])

RATE_LIMIT_REPLY = (
    "I'm getting a lot of questions right now and need a short break "
    "(rate limit reached). Please try again in a moment!"
)

RECURSION_LIMIT_REPLY = (
    "I couldn't settle on a recommendation this time. Could you name a game "
    "you enjoyed, or tell me a genre or theme you're in the mood for?"
)


@router.post("/chat", response_model=ChatResponse)
def chat(body: ChatRequest):
    """Chat with the game-advisor agent."""
    if not settings.chat_model:
        raise HTTPException(status_code=503, detail="Chat assistant is not configured")

    collector: dict[int, GameRecommendation] = {}
    # Fresh session per tool call: LangGraph runs parallel tool calls
    # concurrently, and a SQLAlchemy Session is not thread-safe.
    tools = make_tools(lambda: Session(engine), collector, body.app_ids, body.hours_played)

    try:
        reply = run_chat(tools, body.history, body.message)
    except GraphRecursionError:
        logger.warning("Chat agent hit recursion limit without finishing.")
        return ChatResponse(reply=RECURSION_LIMIT_REPLY, games=[])
    except Exception as e:
        logger.exception("Chat agent failed")
        message = str(e).lower()
        if "resource_exhausted" in message or "rate limit" in message or "429" in message:
            return ChatResponse(reply=RATE_LIMIT_REPLY, games=[])
        raise HTTPException(status_code=500, detail="Chat assistant is currently unavailable") from e

    return ChatResponse(reply=reply, games=list(collector.values()))
