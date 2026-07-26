"""Database mapping wrappers and serialization helper."""

from __future__ import annotations

from typing import Any, Dict


class DatabaseConnection:
    """Wrapper that manages SQLite and Postgres dialect differences."""

    def __init__(self, raw: Any, *, postgres: bool) -> None:
        self.raw = raw
        self.is_postgres = postgres

    def execute(self, query: str, params: tuple[Any, ...] = ()) -> Any:
        """Execute a SQL query, converting placeholders if Postgres is used."""
        if self.is_postgres:
            query = query.replace("?", "%s")
        return self.raw.execute(query, params)

    def execute_script(self, script: str) -> None:
        """Execute a multi-statement SQL script."""
        if not self.is_postgres:
            self.raw.executescript(script)
            return
        for statement in script.split(";"):
            if statement.strip():
                self.raw.execute(statement)

    def commit(self) -> None:
        """Commit the current transaction."""
        self.raw.commit()

    def close(self) -> None:
        """Close the database connection."""
        self.raw.close()


def serialize(row: Any) -> Dict[str, Any]:
    """Convert a database Row object into a standard Python dictionary."""
    return dict(row)
