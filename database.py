"""Couche d'accès à la base de données SQLite."""
import sqlite3
from pathlib import Path

# Le fichier de base vit dans le workspace => il persiste entre les sessions.
DB_PATH = Path(__file__).resolve().parent / "data.db"


def get_conn() -> sqlite3.Connection:
    """Ouvre une connexion SQLite avec row_factory pour accéder aux colonnes par nom."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    return conn


def init_db() -> None:
    """Crée le schéma si nécessaire (idempotent)."""
    with get_conn() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS tasks (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                title       TEXT    NOT NULL,
                description TEXT    NOT NULL DEFAULT '',
                status      TEXT    NOT NULL DEFAULT 'todo'
                            CHECK (status IN ('todo', 'in_progress', 'done')),
                created_at  TEXT    NOT NULL DEFAULT (datetime('now')),
                updated_at  TEXT    NOT NULL DEFAULT (datetime('now'))
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS leads (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                name        TEXT    NOT NULL DEFAULT '',
                email       TEXT    NOT NULL DEFAULT '',
                phone       TEXT    NOT NULL DEFAULT '',
                source      TEXT    NOT NULL DEFAULT 'manual',
                status      TEXT    NOT NULL DEFAULT 'new',
                notes       TEXT    NOT NULL DEFAULT '',
                meta_id     TEXT,
                created_at  TEXT    NOT NULL DEFAULT (datetime('now'))
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS orders (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                chariow_sale_id TEXT,
                customer_email  TEXT    NOT NULL DEFAULT '',
                customer_name   TEXT    NOT NULL DEFAULT '',
                product_name    TEXT    NOT NULL DEFAULT '',
                amount          TEXT    NOT NULL DEFAULT '',
                status          TEXT    NOT NULL DEFAULT 'pending',
                access_granted  INTEGER NOT NULL DEFAULT 0,
                raw_json        TEXT    NOT NULL DEFAULT '',
                created_at      TEXT    NOT NULL DEFAULT (datetime('now')),
                updated_at      TEXT    NOT NULL DEFAULT (datetime('now'))
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS campaigns (
                id               INTEGER PRIMARY KEY AUTOINCREMENT,
                name             TEXT    NOT NULL,
                objective        TEXT    NOT NULL DEFAULT 'OUTCOME_TRAFFIC',
                daily_budget     INTEGER NOT NULL DEFAULT 500,
                status           TEXT    NOT NULL DEFAULT 'draft',
                meta_campaign_id TEXT,
                message          TEXT    NOT NULL DEFAULT '',
                created_at       TEXT    NOT NULL DEFAULT (datetime('now'))
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS conversations (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                channel     TEXT    NOT NULL DEFAULT 'web',
                external_id TEXT,
                author      TEXT    NOT NULL DEFAULT '',
                inbound     TEXT    NOT NULL DEFAULT '',
                outbound    TEXT    NOT NULL DEFAULT '',
                sent        INTEGER NOT NULL DEFAULT 0,
                created_at  TEXT    NOT NULL DEFAULT (datetime('now'))
            )
            """
        )
