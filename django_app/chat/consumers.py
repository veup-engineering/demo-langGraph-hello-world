"""WebSocket consumer for the chat interface.

Handles the async chat flow over a WebSocket connection so the long-running
LangGraph agent call does not block a sync Django worker thread.

Protocol (JSON):
    Client -> Server:  {"message": "..."}
    Server -> Client:  {"reply": "..."}  or  {"error": "..."}
"""
from __future__ import annotations

import json
import logging

from channels.generic.websocket import AsyncWebsocketConsumer

from agent.runner import run_agent_async

logger = logging.getLogger(__name__)


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        if self.scope["user"].is_anonymous:
            await self.close()
            return
        await self.accept()

    async def receive(self, text_data=None, bytes_data=None):
        try:
            payload = json.loads(text_data or "{}")
        except json.JSONDecodeError:
            await self.send(json.dumps({"error": "invalid json"}))
            return

        message = (payload.get("message") or "").strip()
        if not message:
            await self.send(json.dumps({"error": "message is required"}))
            return

        try:
            reply = await run_agent_async(message, user=self.scope["user"])
        except Exception as exc:
            logger.exception("agent failed")
            await self.send(
                json.dumps({"error": f"agent failed: {exc.__class__.__name__}: {exc}"})
            )
            return

        await self.send(json.dumps({"reply": reply}))
