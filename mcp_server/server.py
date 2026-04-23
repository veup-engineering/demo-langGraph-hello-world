"""MCP server exposing tools that wrap the Django REST API.

Run standalone:

    python -m server          (from within this directory)
    python mcp_server/server.py

It listens on http://127.0.0.1:8001/sse by default. The LangGraph agent
connects to it via langchain-mcp-adapters' SSE transport.

Configuration (env vars):
    MCP_HOST              default 127.0.0.1
    MCP_PORT              default 8001
    DJANGO_API_BASE_URL   default http://127.0.0.1:8000
    MCP_API_TOKEN         optional DRF token for authenticated API access
"""
from __future__ import annotations

import os
from typing import Any

import httpx
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

load_dotenv()

API_BASE = os.environ.get("DJANGO_API_BASE_URL", "http://127.0.0.1:8000").rstrip("/")
API_TOKEN = os.environ.get("MCP_API_TOKEN", "")
HOST = os.environ.get("MCP_HOST", "127.0.0.1")
PORT = int(os.environ.get("MCP_PORT", "8001"))


def _headers() -> dict[str, str]:
    h = {"Accept": "application/json"}
    if API_TOKEN:
        h["Authorization"] = f"Token {API_TOKEN}"
    return h


async def _get(path: str, params: dict | None = None) -> Any:
    url = f"{API_BASE}{path}"
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, params=params or {}, headers=_headers(), timeout=15)
        resp.raise_for_status()
        return resp.json()


# FastMCP wires tool definitions, dispatch, and the SSE/HTTP transport.
mcp = FastMCP("django-knowledge", host=HOST, port=PORT)


@mcp.tool()
async def search_knowledge_base(query: str) -> dict:
    """Search the company knowledge base for articles relevant to a query.

    Use this tool when the user asks about policies, account help, support
    contact, billing, shipping, or general "how do I..." questions.

    Args:
        query: A natural-language search query.

    Returns:
        A dict with keys ``query``, ``count``, and ``results`` (a list of
        articles each containing ``id``, ``title``, ``category``, ``body``).
    """
    return await _get("/api/articles/search/", {"q": query})


@mcp.tool()
async def list_articles(category: str | None = None) -> list:
    """List all knowledge-base articles, optionally filtered by category.

    Categories include: ``account``, ``billing``, ``shipping``.
    """
    params = {"category": category} if category else None
    return await _get("/api/articles/", params)


@mcp.tool()
async def search_products(query: str) -> dict:
    """Search the product catalog for items matching a query.

    Use this when the user asks about specific products, what we sell,
    pricing, or recommendations.
    """
    return await _get("/api/products/search/", {"q": query})


@mcp.tool()
async def list_products(category: str | None = None) -> list:
    """List all products, optionally filtered by category.

    Categories include: ``hardware``, ``kits``, ``parts``.
    """
    params = {"category": category} if category else None
    return await _get("/api/products/", params)


if __name__ == "__main__":
    print(
        f"[mcp] starting SSE server on http://{HOST}:{PORT}/sse "
        f"-> Django API at {API_BASE}"
    )
    mcp.run(transport="sse")
