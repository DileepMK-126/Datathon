"""Database connection manager supporting SQLite and PostgreSQL."""

from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from ..core.config import settings
from ..core.database import DatabaseConnection

APP_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = APP_ROOT / "data"
SQLITE_PATH = DATA_DIR / "sentinel.db"


@contextmanager
def connection() -> Iterator[DatabaseConnection]:
    """Provide a transactional scope around database connections."""
    url = settings.DATABASE_URL
    if url and url.startswith(("postgres://", "postgresql://")):
        import psycopg
        from psycopg.rows import dict_row

        raw = psycopg.connect(url, row_factory=dict_row)
        conn = DatabaseConnection(raw, postgres=True)
    else:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        raw = sqlite3.connect(SQLITE_PATH)
        raw.row_factory = sqlite3.Row
        conn = DatabaseConnection(raw, postgres=False)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.raw.rollback()
        raise
    finally:
        conn.close()
