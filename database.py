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
