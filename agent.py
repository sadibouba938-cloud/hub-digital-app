"""Hub Digital Agent — Meta Marketing API + Chariow + CRM (APIs officielles)."""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from typing import Any, Optional

GRAPH = "https://graph.facebook.com/v21.0"
CHARIOW_API = "https://api.chariow.com/v1"


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def env(name: str, default: str = "") -> str:
    return (os.environ.get(name) or default).strip()


def connection_status() -> dict[str, Any]:
    meta_token = bool(env("META_ACCESS_TOKEN"))
    chariow = bool(env("CHARIOW_API_KEY"))
    return {
        "meta": {
            "connected": meta_token,
            "ad_account_id": env("META_AD_ACCOUNT_ID") or None,
            "page_id": env("META_PAGE_ID") or None,
            "app_id_set": bool(env("META_APP_ID")),
            "mode": "live" if meta_token else "sandbox",
            "hint": None
            if meta_token
            else "Ajoutez META_ACCESS_TOKEN, META_AD_ACCOUNT_ID, META_PAGE_ID (App Meta + Business Manager).",
        },
        "chariow": {
            "connected": chariow,
            "storefront": "https://qxcvjkbl.mychariow.market",
            "mode": "live" if chariow else "storefront_public",
            "hint": None
            if chariow
            else "Ajoutez CHARIOW_API_KEY pour valider les ventes (API v1 + Pulse sale.completed).",
        },
        "limits": [
            "Meta n'autorise pas de piloter Business Suite comme un humain : uniquement Marketing API, Messenger, Lead Ads.",
            "Créer des pubs réelles exige un compte pub actif, une app en mode Live et souvent une revue Meta.",
            "Les messages Messenger automatiques nécessitent une Page + webhook vérifié.",
        ],
    }


def _http_json(url: str, method: str = "GET", data: Optional[dict] = None, headers: Optional[dict] = None) -> dict:
    body = None
    hdrs = {"User-Agent": "HubDigital-Agent/1.0", "Accept": "application/json"}
    if headers:
        hdrs.update(headers)
    if data is not None:
        body = json.dumps(data).encode("utf-8")
        hdrs.setdefault("Content-Type", "application/json")
    req = urllib.request.Request(url, data=body, headers=hdrs, method=method)
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            raw = resp.read().decode("utf-8")
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as exc:
        err_body = exc.read().decode("utf-8", errors="replace")
        try:
            parsed = json.loads(err_body)
        except json.JSONDecodeError:
            parsed = {"error": err_body}
        parsed["_http_status"] = exc.code
        raise RuntimeError(json.dumps(parsed, ensure_ascii=False)) from exc


def meta_create_campaign(name: str, objective: str, daily_budget_cents: int, status: str = "PAUSED") -> dict:
    """Crée une campagne Ads via Marketing API, ou un brouillon si pas de token."""
    token = env("META_ACCESS_TOKEN")
    account = env("META_AD_ACCOUNT_ID")
    if not token or not account:
        return {
            "ok": False,
            "mode": "draft",
            "message": "Token Meta absent : campagne enregistrée en brouillon uniquement.",
        }
    if not account.startswith("act_"):
        account = f"act_{account}"
    params = urllib.parse.urlencode(
        {
            "name": name,
            "objective": objective,
            "status": status,
            "special_ad_categories": "[]",
            "daily_budget": str(daily_budget_cents),
            "access_token": token,
        }
    )
    url = f"{GRAPH}/{account}/campaigns?{params}"
    result = _http_json(url, method="POST")
    return {"ok": True, "mode": "live", "meta": result}


def meta_send_message(psid: str, text: str) -> dict:
    token = env("META_PAGE_ACCESS_TOKEN") or env("META_ACCESS_TOKEN")
    if not token:
        return {"ok": False, "mode": "draft", "message": "Pas de token Page : réponse enregistrée localement."}
    payload = {
        "recipient": {"id": psid},
        "messaging_type": "RESPONSE",
        "message": {"text": text[:2000]},
    }
    url = f"{GRAPH}/me/messages?access_token={urllib.parse.quote(token)}"
    result = _http_json(url, method="POST", data=payload)
    return {"ok": True, "mode": "live", "meta": result}


def chariow_sales(email: Optional[str] = None) -> dict:
    key = env("CHARIOW_API_KEY")
    if not key:
        return {"ok": False, "sales": [], "message": "CHARIOW_API_KEY manquante."}
    qs = f"?customer_email={urllib.parse.quote(email)}" if email else ""
    data = _http_json(
        f"{CHARIOW_API}/sales{qs}",
        headers={"Authorization": f"Bearer {key}"},
    )
    return {"ok": True, "sales": data.get("data") or data.get("sales") or []}


def chariow_verify_sale(sale_id: str) -> dict:
    key = env("CHARIOW_API_KEY")
    if not key:
        return {"ok": False, "message": "CHARIOW_API_KEY manquante — validation manuelle uniquement."}
    data = _http_json(
        f"{CHARIOW_API}/sales/{urllib.parse.quote(sale_id)}",
        headers={"Authorization": f"Bearer {key}"},
    )
    sale = data.get("data") or data
    status = (sale.get("status") or "").lower()
    return {
        "ok": status in ("completed", "paid", "success"),
        "status": status,
        "sale": sale,
    }


def suggested_reply(message: str) -> str:
    m = (message or "").lower()
    if any(w in m for w in ("prix", "tarif", "combien", "price")):
        return (
            "Nos kits digitaux sont sur la boutique Hub Digital : "
            "https://qxcvjkbl.mychariow.market/products — dites-moi le produit qui vous intéresse."
        )
    if any(w in m for w in ("commande", "achat", "paiement", "reçu", "accès")):
        return (
            "Pour valider votre commande digitale, envoyez l'e-mail utilisé au paiement "
            "et le nom du produit. Je vérifie ensuite sur Chariow."
        )
    if any(w in m for w in ("bonjour", "salut", "hello", "salam")):
        return "Bonjour 👋 Hub Digital à votre écoute. Produit, pub ou commande : comment puis-je aider ?"
    return (
        "Merci pour votre message. Un conseiller Hub Digital reviendra vers vous. "
        "Boutique : https://qxcvjkbl.mychariow.market"
    )
