"""LangGraph agent that answers chat messages via RAG over the Django API.

The agent uses a ReAct-style loop:
  1. Receives the user message + a system prompt explaining the available tools.
  2. Calls MCP tools (search_knowledge_base, search_products, ...) to retrieve
     context from the Django API.
  3. Synthesizes a final answer grounded in those tool results.

The MCP tools are loaded over SSE from the running mcp_server process. The
LLM is a local Ollama instance configured in Django settings.
"""
from __future__ import annotations

import logging
from typing import Any

from django.conf import settings
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_ollama import ChatOllama
from langgraph.prebuilt import create_react_agent

logger = logging.getLogger(__name__)


SYSTEM_PROMPT = """\
You are a helpful customer-support assistant for Acme Corp.

You have access to tools that search a company knowledge base and a product
catalog. ALWAYS use the tools to look up factual information before answering
questions about policies, accounts, billing, shipping, products, or pricing.
Never invent product names, prices, or policies.

When you answer:
- Cite the article title or product name you used.
- If the tools return nothing relevant, say so honestly.
- Keep answers concise (3-6 sentences) unless the user asks for detail.
"""


def _build_llm() -> ChatOllama:
    return ChatOllama(
        base_url=settings.OLLAMA_BASE_URL,
        model=settings.OLLAMA_MODEL,
        temperature=0.2,
    )


async def run_agent_async(message: str, user: Any | None = None) -> str:
    """Run the agent asynchronously — called from the WebSocket consumer.

    Connects to the MCP server over SSE, builds a ReAct agent, and returns
    the final reply text.
    """
    client = MultiServerMCPClient(
        {
            "django-knowledge": {
                "url": settings.MCP_SERVER_URL,
                "transport": "sse",
            }
        }
    )
    tools = await client.get_tools()
    logger.info("loaded %d MCP tools: %s", len(tools), [t.name for t in tools])

    agent = create_react_agent(_build_llm(), tools)

    result: dict[str, Any] = await agent.ainvoke(
        {
            "messages": [
                SystemMessage(content=SYSTEM_PROMPT),
                HumanMessage(content=message),
            ]
        }
    )

    messages = result.get("messages", [])
    if not messages:
        return "(no response)"
    final = messages[-1]
    content = getattr(final, "content", None)
    if isinstance(content, list):
        # Some providers return content as a list of parts
        parts = [p.get("text", "") if isinstance(p, dict) else str(p) for p in content]
        return "".join(parts).strip() or "(no response)"
    return (content or "").strip() or "(no response)"
