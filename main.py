from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional
import json as _json
import re as _re
import time as _time
import urllib.request

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

import database as db

STATIC_DIR = Path(__file__).resolve().parent / "static"

# Boutique Chariow « Hub Digital » (storefront)
CHARIOW_STORE_ID = "store_n3h4zjjty54r"
CHARIOW_STORE_URL = "https://qxcvjkbl.mychariow.market"
CHARIOW_PRODUCTS_URL = f"https://api-edge.chariow.com/storefront/{CHARIOW_STORE_ID}/products"
STORE_CACHE_TTL = 600  # secondes
_store_cache = {"data": None, "at": 0.0}


def _strip_html(value: str, limit: int = 160) -> str:
    if not value:
        return ""
    text = _re.sub(r"<[^>]+>", " ", value)
    text = _re.sub(r"\s+", " ", text).strip()
    return text[:limit] + ("…" if len(text) > limit else "")

VALID_STATUSES = ("todo", "in_progress", "done")


@asynccontextmanager
async def lifespan(app: FastAPI):
    db.init_db()
    yield


app = FastAPI(title="Agent Arena Backend + DB", version="2.0.0", lifespan=lifespan)


# ---------- Modèles ----------
class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = ""
    status: Optional[str] = "todo"


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None


class EchoPayload(BaseModel):
    message: str
    source: Optional[str] = None


class ChatPayload(BaseModel):
    message: str


# ---------- Site vitrine Hub Digital (fusionné) ----------
app.mount("/assets", StaticFiles(directory=STATIC_DIR / "assets"), name="assets")


@app.get("/", response_class=HTMLResponse)
def home():
    return (STATIC_DIR / "index.html").read_text(encoding="utf-8")


@app.get("/taches", response_class=HTMLResponse)
def dashboard_page():
    return (STATIC_DIR / "taches.html").read_text(encoding="utf-8")


@app.get("/chat.css", response_class=FileResponse)
def chat_css():
    return FileResponse(STATIC_DIR / "chat.css")


@app.get("/chat.js", response_class=FileResponse)
def chat_js():
    return FileResponse(STATIC_DIR / "chat.js")


# ---------- Santé / infos ----------
@app.get("/health")
def health():
    return {"status": "ok", "service": "agent-arena-backend", "db": "sqlite", "time": datetime.now(timezone.utc).isoformat()}


@app.get("/api/time")
def server_time():
    return {"utc": datetime.now(timezone.utc).isoformat(), "timezone": "UTC"}


@app.get("/api/info")
def info():
    return {
        "name": "Agent Arena Backend",
        "version": "2.0.0",
        "framework": "FastAPI",
        "database": "SQLite (data.db)",
        "endpoints": [
            "/ (site Hub Digital)", "/taches (tableau de bord)", "/assets/* (css/js)",
            "/health", "/api/time", "/api/info", "/api/echo (POST)",
            "/tasks (GET, POST)", "/tasks/{id} (GET, PUT, DELETE)", "/stats (GET)",
        ],
    }


@app.post("/api/echo")
def echo(payload: EchoPayload, request: Request):
    return {
        "received": payload.message,
        "source": payload.source,
        "client": request.client.host if request.client else None,
        "echoed_at": datetime.now(timezone.utc).isoformat(),
    }


# ---------- CRUD Tâches ----------
@app.get("/tasks")
def list_tasks(status: Optional[str] = None):
    conn = db.get_conn()
    if status:
        if status not in VALID_STATUSES:
            raise HTTPException(400, f"status invalide, valeurs possibles : {', '.join(VALID_STATUSES)}")
        rows = conn.execute("SELECT * FROM tasks WHERE status = ? ORDER BY id DESC", (status,)).fetchall()
    else:
        rows = conn.execute("SELECT * FROM tasks ORDER BY id DESC").fetchall()
    return {"count": len(rows), "tasks": [dict(r) for r in rows]}


@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    conn = db.get_conn()
    row = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    if row is None:
        raise HTTPException(404, "Tâche introuvable")
    return dict(row)


@app.post("/tasks", status_code=201)
def create_task(task: TaskCreate):
    if task.status not in VALID_STATUSES:
        raise HTTPException(400, f"status invalide, valeurs possibles : {', '.join(VALID_STATUSES)}")
    conn = db.get_conn()
    cur = conn.execute(
        "INSERT INTO tasks (title, description, status) VALUES (?, ?, ?)",
        (task.title, task.description or "", task.status or "todo"),
    )
    conn.commit()
    row = conn.execute("SELECT * FROM tasks WHERE id = ?", (cur.lastrowid,)).fetchone()
    return dict(row)


@app.put("/tasks/{task_id}")
def update_task(task_id: int, task: TaskUpdate):
    conn = db.get_conn()
    existing = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    if existing is None:
        raise HTTPException(404, "Tâche introuvable")

    title = task.title if task.title is not None else existing["title"]
    description = task.description if task.description is not None else existing["description"]
    status = task.status if task.status is not None else existing["status"]
    if status not in VALID_STATUSES:
        raise HTTPException(400, f"status invalide, valeurs possibles : {', '.join(VALID_STATUSES)}")

    conn.execute(
        "UPDATE tasks SET title = ?, description = ?, status = ?, updated_at = datetime('now') WHERE id = ?",
        (title, description, status, task_id),
    )
    conn.commit()
    row = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    return dict(row)


@app.delete("/tasks/{task_id}")
def delete_task(task_id: int):
    conn = db.get_conn()
    existing = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    if existing is None:
        raise HTTPException(404, "Tâche introuvable")
    conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    return {"deleted": task_id}


# ---------- Statistiques ----------
@app.get("/stats")
def stats():
    conn = db.get_conn()
    total = conn.execute("SELECT COUNT(*) AS n FROM tasks").fetchone()["n"]
    rows = conn.execute("SELECT status, COUNT(*) AS n FROM tasks GROUP BY status").fetchall()
    return {"total": total, "by_status": {r["status"]: r["n"] for r in rows}}


# ---------- Boutique Chariow (proxy produits) ----------
@app.get("/boutique/produits")
def boutique_produits():
    """Proxy vers l'API storefront Chariow, avec cache court en mémoire."""
    now = _time.time()
    if _store_cache["data"] is not None and now - _store_cache["at"] < STORE_CACHE_TTL:
        return _store_cache["data"]

    def _build(payload: dict) -> dict:
        items = []
        for p in payload.get("data", []):
            pricing = p.get("pricing") or {}
            effective = pricing.get("effective") or pricing.get("price") or {}
            items.append({
                "id": p.get("id"),
                "name": p.get("name"),
                "type": p.get("type"),
                "price": effective.get("formatted"),
                "currency": effective.get("currency"),
                "category": (p.get("category") or {}).get("label"),
                "thumbnail": (p.get("pictures") or {}).get("thumbnail"),
                "description": _strip_html(p.get("description")),
                "is_free": p.get("is_free"),
                "url": CHARIOW_STORE_URL + "/products",
            })
        return {
            "store": {
                "name": "Hub Digital",
                "url": CHARIOW_STORE_URL,
                "products_url": CHARIOW_STORE_URL + "/products",
                "description": "Solutions digitales et ressources pour entreprendre, créer et grandir.",
            },
            "count": len(items),
            "products": items,
        }

    try:
        req = urllib.request.Request(
            CHARIOW_PRODUCTS_URL,
            headers={"User-Agent": "HubDigital-Site/1.0", "Accept": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            payload = _json.loads(resp.read().decode("utf-8"))
        data = _build(payload)
        _store_cache["data"] = data
        _store_cache["at"] = now
        return data
    except Exception as exc:  # noqa: BLE001 — fallback cache puis erreur propre
        if _store_cache["data"] is not None:
            return _store_cache["data"]
        return {
            "store": {"name": "Hub Digital", "url": CHARIOW_STORE_URL, "products_url": CHARIOW_STORE_URL + "/products"},
            "count": 0,
            "products": [],
            "error": str(exc),
        }


# ---------- Chat « Hub Digital IA » ----------
CHAT_AGENT_URL = "https://hub-digital-agent-hub-digital-agent.up.railway.app/"


def _local_chat_reply(message: str) -> str:
    """Assistant local (FAQ Hub Digital) — utilisé quand l'agent Railway est indisponible."""
    m = message.lower()

    # Détection simple de la langue (le français est la langue par défaut du site)
    ar_words = ("مرحبا", "سلام", "عليكم", "شكرا", "بوتيك", "متجر", "منتج", "سعر", "خدمات", "اتصال", "مهام")
    en_words = ("hello", " hi", "how", "what", "thank", "price", " buy", "the ", "your", "help", "cost", "much", "dashboard")
    fr_words = ("bonjour", "salut", "merci", "combien", "comment", "quel", "quelle", "quoi", "vos", "nos", "notre",
                "boutique", "prix", "tache", "tâche", "tableau", "contacter", "contact", "service", "offre", "tarif")

    if any(w in m for w in ar_words):
        lang = "ar"
    elif any(w in m for w in en_words) and not any(w in m for w in fr_words):
        lang = "en"
    else:
        lang = "fr"

    topics = [
        (
            ("bonjour", "salut", "bonsoir", "salam", "hello", "hi", "مرحبا", "سلام"),
            "Bonjour 👋 Je suis l'assistant de Hub Digital. Je peux vous renseigner sur nos services, notre boutique et nos contacts. Comment puis-je vous aider ?",
            "Hello 👋 I'm the Hub Digital assistant. I can tell you about our services, store and contacts. How can I help?",
            "مرحباً 👋 أنا مساعد Hub Digital. يمكنني إخبارك عن خدماتنا ومتجرنا وطرق التواصل. كيف أساعدك؟",
        ),
        (
            ("service", "offre", "prestation", "branding", "storytelling", "e-commerce", "marketing", "stratégie", "خدمات"),
            "Nous proposons : 🎨 Branding & Identité, 📖 Storytelling, 💻 Solutions digitales, 📈 Stratégie de croissance et 🛒 E-commerce. Que voulez-vous approfondir ?",
            "We offer: 🎨 Branding & Identity, 📖 Storytelling, 💻 Digital solutions, 📈 Growth strategy and 🛒 E-commerce. What would you like to know more about?",
            "نقدم: 🎨 الهوية البصرية، 📖 سرد القصص، 💻 الحلول الرقمية، 📈 استراتيجية النمو و 🛒 التجارة الإلكترونية.",
        ),
        (
            ("boutique", "produit", "produits", "prix", "acheter", "chariow", "shop", "store", "product", "buy",
             "combien", "tarif", "coûte", "coute", "startpack", "visionai", "kit", "cost", "how much", "متجر", "منتج", "سعر", "كم"),
            "🛍️ Notre boutique est dans la section « Boutique » du site et sur qxcvjkbl.mychariow.market. Vous y trouverez guides et kits digitaux : StartPack Digital, VisionAI, kits IA et marketing…",
            "🛍️ Our store is in the « Boutique » section and at qxcvjkbl.mychariow.market — guides and digital kits: StartPack Digital, VisionAI, AI & marketing kits…",
            "🛍️ متجرنا موجود في قسم « المتجر » وعلى الرابط qxcvjkbl.mychariow.market — أدلة وعدة رقمية: StartPack Digital و VisionAI وغيرها.",
        ),
        (
            ("contact", "email", "mail", "téléphone", "tel", "joindre", "adresse", "اتصال", "بريد"),
            "📬 Vous pouvez nous écrire à contact@hubdigital.com ou utiliser le formulaire « Contact » en bas de la page.",
            "📬 You can email us at contact@hubdigital.com or use the « Contact » form at the bottom of the page.",
            "📬 يمكنك مراسلتنا على contact@hubdigital.com أو استخدام نموذج « اتصل بنا » أسفل الصفحة.",
        ),
        (
            ("tache", "tâche", "tableau de bord", "dashboard", "لوحة", "مهام"),
            "🗂️ Le tableau de bord est accessible via le menu « Tableau de bord » (ou /taches). Vous pouvez y gérer vos tâches en temps réel.",
            "🗂️ The dashboard is available in the « Dashboard » menu (or /taches). You can manage your tasks in real time.",
            "🗂️ لوحة التحكم متاحة من قائمة « لوحة التحكم » (أو /taches). يمكنك إدارة مهامك في الوقت الفعلي.",
        ),
        (
            ("à propos", "a propos", "qui êtes", "hub digital", "about", "من أنت", "هب ديجيتال"),
            "🚀 Hub Digital est la vitrine numérique d'un projet innovant qui connecte créativité et technologie, pensé pour le marché africain et international.",
            "🚀 Hub Digital is the digital showcase of an innovative project connecting creativity and technology, built for the African and international market.",
            "🚀 Hub Digital هو الواجهة الرقمية لمشروع مبتكر يربط الإبداع بالتكنولوجيا، مصمم للسوق الإفريقي والدولي.",
        ),
        (
            ("merci", "thank", "شكرا"),
            "Avec plaisir ! 😊 N'hésitez pas si vous avez d'autres questions.",
            "You're welcome! 😊 Feel free to ask anything else.",
            "على الرحب والسعة! 😊 لا تتردد في طرح أي سؤال آخر.",
        ),
    ]

    for keys, fr, en, ar in topics:
        if any(k in m for k in keys):
            return {"fr": fr, "en": en, "ar": ar}[lang]

    return {
        "fr": "Je ne suis pas sûr de comprendre 🤔 Posez-moi une question sur nos services, notre boutique ou nos contacts.",
        "en": "I'm not sure I understand 🤔 Ask me about our services, store or contacts.",
        "ar": "لست متأكداً من فهمي لسؤالك 🤔 اسألني عن خدماتنا أو متجرنا أو طرق التواصل.",
    }[lang]


@app.post("/api/chat")
def chat(payload: ChatPayload):
    """Point d'entrée du widget « Hub Digital IA »."""
    message = (payload.message or "").strip()
    if not message:
        return {"reply": "…", "source": "empty"}

    # 1) Tenter l'agent distant (Railway), s'il est disponible
    try:
        req = urllib.request.Request(
            CHAT_AGENT_URL,
            data=_json.dumps({"message": message}).encode("utf-8"),
            headers={"Content-Type": "application/json", "User-Agent": "HubDigital-Site/1.0"},
        )
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = _json.loads(resp.read().decode("utf-8"))
        reply = data.get("reply") or data.get("response") or data.get("answer")
        if isinstance(reply, str) and reply.strip():
            return {"reply": reply, "source": "agent"}
    except Exception:
        pass

    # 2) Sinon, assistant local (toujours disponible)
    return {"reply": _local_chat_reply(message), "source": "local"}

