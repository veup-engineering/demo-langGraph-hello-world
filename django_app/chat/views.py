"""Chat web UI views.

The chat page is a server-rendered template; the chat_send endpoint accepts
JSON, runs it through the LangGraph agent, and returns the agent's reply.

chat_send is an async view so the agent can await MCP tool calls without
blocking a worker thread.  The sync views (chat_page) and all /api/ endpoints
remain synchronous — Django's ASGI handler runs them in a threadpool
automatically.
"""
from __future__ import annotations

import json
import logging

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from agent.runner import run_agent_async

logger = logging.getLogger(__name__)


@login_required
def chat_page(request):
    return render(request, "chat/chat.html", {"user": request.user})


@login_required
@require_http_methods(["POST"])
async def chat_send(request):
    try:
        payload = json.loads(request.body or b"{}")
    except json.JSONDecodeError:
        return JsonResponse({"error": "invalid json"}, status=400)

    message = (payload.get("message") or "").strip()
    if not message:
        return JsonResponse({"error": "message is required"}, status=400)

    try:
        reply = await run_agent_async(message, user=request.user)
    except Exception as exc:
        logger.exception("agent failed")
        return JsonResponse(
            {"error": f"agent failed: {exc.__class__.__name__}: {exc}"},
            status=500,
        )

    return JsonResponse({"reply": reply})
