"""One-shot bootstrapper: create a demo user and a DRF auth token.

Run with:  python bootstrap_demo.py
"""
import os
import secrets

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "chatproject.settings")
django.setup()

from django.contrib.auth import get_user_model  # noqa: E402
from rest_framework.authtoken.models import Token  # noqa: E402

User = get_user_model()

USERNAME = "demo"
PASSWORD = "demo12345"

user, created = User.objects.get_or_create(
    username=USERNAME,
    defaults={"email": "demo@example.com", "is_staff": True, "is_superuser": True},
)
if created:
    user.set_password(PASSWORD)
    user.save()
    print(f"created user '{USERNAME}' (password: {PASSWORD})")
else:
    print(f"user '{USERNAME}' already exists")

token, _ = Token.objects.get_or_create(user=user)
print(f"DRF token for {USERNAME}: {token.key}")

env_path = os.path.join(os.path.dirname(__file__), ".env")
existing = ""
if os.path.exists(env_path):
    with open(env_path, "r", encoding="utf-8") as f:
        existing = f.read()

if "MCP_API_TOKEN" not in existing:
    with open(env_path, "a", encoding="utf-8") as f:
        if existing and not existing.endswith("\n"):
            f.write("\n")
        f.write(f"MCP_API_TOKEN={token.key}\n")
    print(f"wrote MCP_API_TOKEN to {env_path}")
else:
    print(f"{env_path} already contains MCP_API_TOKEN — leaving it alone")

# Make sure a SECRET for inter-process auth exists too
if "DJANGO_SECRET_KEY" not in existing:
    secret = secrets.token_urlsafe(32)
    # don't overwrite django's hardcoded one — just provide a value if user wants it
    print(f"(optional) you can set DJANGO_SECRET_KEY={secret}")
