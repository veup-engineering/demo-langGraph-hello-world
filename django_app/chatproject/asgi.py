"""ASGI config for chatproject.

Routes HTTP requests through standard Django views (sync) and WebSocket
connections through Django Channels consumers.
"""

import os

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "chatproject.settings")

# Initialize Django ASGI application early to ensure apps are loaded before
# importing consumers.
django_asgi_app = get_asgi_application()

from chat.routing import websocket_urlpatterns  # noqa: E402

application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        "websocket": AuthMiddlewareStack(
            URLRouter(websocket_urlpatterns)
        ),
    }
)
