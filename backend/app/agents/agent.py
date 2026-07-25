import logging

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langchain_core.tools import BaseTool
from langchain.agents import create_agent

from app.agents.schemas import ChatMessage
from app.core.config import settings

logger = logging.getLogger(__name__)

RECURSION_LIMIT = 10

SYSTEM_PROMPT = """You are GREC's game advisor, a friendly assistant that helps users discover video games.

Rules:
- Use the provided tools to look up real games and recommendations from the database. Never invent games, app_ids, or details.
- When you recommend games, briefly explain why each one fits the user's request, grounded in the tool results (genres, tags, description, review score).
- Keep answers concise and conversational. Present games as a short list.
- If a tool finds nothing because a specific game isn't in the database, you may answer using your own general knowledge about
  that game instead. Clearly say the info isn't from GREC's database.
- If a personalized-recommendations tool is available, prefer it when the user asks for picks tailored to their taste.
- If the user's request is vague, ask one short clarifying question instead of guessing wildly."""


def run_chat(
    tools: list[BaseTool],
    history: list[ChatMessage],
    message: str,
) -> str:
    """Run the game-advisor agent and return its reply text."""
    agent = create_agent(settings.chat_model, tools=tools, system_prompt=SYSTEM_PROMPT)

    messages: list[BaseMessage] = [
        HumanMessage(content=m.content) if m.role == "user" else AIMessage(content=m.content)
        for m in history
    ]
    messages.append(HumanMessage(content=message))

    result = agent.invoke(
        {"messages": messages},
        config={"recursion_limit": RECURSION_LIMIT},
    )

    final = result["messages"][-1]
    content = final.content
    # Some models return a list of content blocks instead of a plain string.
    if isinstance(content, list):
        content = "".join(
            block.get("text", "") if isinstance(block, dict) else str(block)
            for block in content
        )
    return content
