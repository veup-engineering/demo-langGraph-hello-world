"""Chat web UI views.

The chat page is a server-rendered template. The actual chat communication
happens over a WebSocket handled by the ChatConsumer in consumers.py.
"""
from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def chat_page(request):
    return render(request, "chat/chat.html", {"user": request.user})
