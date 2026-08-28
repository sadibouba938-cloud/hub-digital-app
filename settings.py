"""Configuration via variables d'environnement (Railway / .env)."""
from __future__ import annotations

import os
from urllib.parse import urlparse


def _clean(value: str) -> str:
    value = (value or "").strip()
    # L'utilisateur a parfois collé [https://x](https://x)
    if value.startswith("[") and "](" in value and value.endswith(")"):
        value = value[value.find("](") + 2 : -1]
    if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
        value = value[1:-1]
    return value.strip()


def env(name: str, default: str = "") -> str:
    return _clean(os.environ.get(name, default))


def env_bool(name: str, default: bool = False) -> bool:
    raw = env(name, "true" if default else "false").lower()
    return raw in {"1", "true", "yes", "on"}


def _is_placeholder(value: str) -> bool:
    if not value:
        return True
    low = value.lower()
    return low.startswith("ta_cle") or "your_" in low or low in {"changeme", "xxx", "todo"}


ARENA_API_KEY = env("ARENA_API_KEY")
ARENA_API_URL = env("ARENA_API_URL", "https://api.openai.com/v1/chat/completions")
OPENAI_API_KEY = env("OPENAI_API_KEY")
OPENAI_API_URL = env("OPENAI_API_URL", "https://api.openai.com/v1/chat/completions")
FRONTEND_URL = env("FRONTEND_URL", "https://hub-digital-appt-production.up.railway.app").rstrip("/")
DEBUG_MODE = env_bool("DEBUG_MODE", False)

ARENA_READY = bool(ARENA_API_KEY) and not _is_placeholder(ARENA_API_KEY)
OPENAI_READY = bool(OPENAI_API_KEY) and not _is_placeholder(OPENAI_API_KEY)


def cors_origins() -> list[str]:
    extras = env("CORS_ORIGINS")
    origins = {FRONTEND_URL, "http://localhost:8000", "http://127.0.0.1:8000"}
    if extras:
        origins.update(o.strip().rstrip("/") for o in extras.split(",") if o.strip())
    parsed = urlparse(FRONTEND_URL)
    if parsed.hostname:
        origins.add(f"{parsed.scheme}://{parsed.hostname}")
    return [o for o in origins if o]


def public_config() -> dict:
    return {
        "frontend_url": FRONTEND_URL,
        "debug": DEBUG_MODE,
        "llm": {
            "arena": ARENA_READY,
            "openai_fallback": OPENAI_READY,
        },
    }
