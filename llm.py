"""Appels LLM : Arena d'abord, puis OpenAI, puis FAQ locale."""
from __future__ import annotations

import json
import urllib.error
import urllib.request

import settings


SYSTEM_PROMPT = (
    "Tu es l'assistant Hub Digital (Sénégal / Afrique). "
    "Tu aides sur les services (branding, storytelling, e-commerce, stratégie), "
    "la boutique Chariow https://qxcvjkbl.mychariow.market, les commandes de produits digitaux, "
    "et le tableau de bord. Réponds dans la langue de l'utilisateur, de façon courte et concrète."
)


def _chat_completions(url: str, api_key: str, message: str, timeout: int = 20) -> str:
    payload = {
        "model": settings.env("LLM_MODEL", "gpt-4o-mini"),
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": message},
        ],
        "temperature": 0.4,
        "max_tokens": 400,
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
            "User-Agent": "HubDigital-Agent/1.0",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    choices = data.get("choices") or []
    if not choices:
        text = data.get("reply") or data.get("output") or data.get("answer") or ""
        return str(text).strip()
    return ((choices[0].get("message") or {}).get("content") or "").strip()


def generate_reply(message: str) -> tuple[str, str]:
    """Retourne (texte, source)."""
    if settings.ARENA_READY:
        try:
            text = _chat_completions(settings.ARENA_API_URL, settings.ARENA_API_KEY, message)
            if text:
                return text, "arena"
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, json.JSONDecodeError, OSError):
            pass
    if settings.OPENAI_READY:
        try:
            text = _chat_completions(settings.OPENAI_API_URL, settings.OPENAI_API_KEY, message)
            if text:
                return text, "openai"
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, json.JSONDecodeError, OSError):
            pass
    return "", "none"
