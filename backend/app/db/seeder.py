"""Database schemas definition and execution seeding trigger."""

from __future__ import annotations

from .connection import connection
from .synthetic_generator import seed_demo_data
from ..core.config import settings
from ..core.security import ensure_bootstrap_user


def initialize_database() -> None:
    """Create the SQLite/PostGIS schema and seed a reproducible demo dataset once."""
    with connection() as conn:
        if conn.is_postgres:
            conn.execute("CREATE EXTENSION IF NOT EXISTS postgis")
            conn.execute_script(
                """
                CREATE TABLE IF NOT EXISTS zones (id TEXT PRIMARY KEY, name TEXT NOT NULL, lat DOUBLE PRECISION NOT NULL, lng DOUBLE PRECISION NOT NULL, patrol_coverage DOUBLE PRECISION NOT NULL);
                CREATE TABLE IF NOT EXISTS cases (id TEXT PRIMARY KEY, zone_id TEXT NOT NULL REFERENCES zones(id), opened_at TEXT NOT NULL, status TEXT NOT NULL, summary TEXT NOT NULL, crime_type TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS incidents (id TEXT PRIMARY KEY, case_id TEXT NOT NULL REFERENCES cases(id), zone_id TEXT NOT NULL REFERENCES zones(id), crime_type TEXT NOT NULL, occurred_at TEXT NOT NULL, latitude DOUBLE PRECISION NOT NULL, longitude DOUBLE PRECISION NOT NULL, geom geometry(Point, 4326) NOT NULL, source TEXT NOT NULL, narrative TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS case_entities (id BIGSERIAL PRIMARY KEY, case_id TEXT NOT NULL REFERENCES cases(id), entity_type TEXT NOT NULL, normalized_value TEXT NOT NULL, display_value TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS source_records (id BIGSERIAL PRIMARY KEY, case_id TEXT NOT NULL REFERENCES cases(id), source_system TEXT NOT NULL, record_type TEXT NOT NULL, recorded_at TEXT NOT NULL, payload_json TEXT NOT NULL, confidence DOUBLE PRECISION NOT NULL);
                CREATE TABLE IF NOT EXISTS zone_context (zone_id TEXT PRIMARY KEY REFERENCES zones(id), population_band TEXT NOT NULL, traffic_index DOUBLE PRECISION NOT NULL, event_factor TEXT NOT NULL, unemployment_index DOUBLE PRECISION NOT NULL, updated_at TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password_hash TEXT NOT NULL, role TEXT NOT NULL CHECK(role IN ('analyst','supervisor','admin')), active BOOLEAN NOT NULL DEFAULT TRUE, created_at TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS audit_events (id BIGSERIAL PRIMARY KEY, occurred_at TEXT NOT NULL, actor TEXT NOT NULL, role TEXT NOT NULL, action TEXT NOT NULL, resource TEXT NOT NULL, outcome TEXT NOT NULL, request_id TEXT NOT NULL, detail_json TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS integration_sync_runs (id BIGSERIAL PRIMARY KEY, source_system TEXT NOT NULL, started_at TEXT NOT NULL, finished_at TEXT, status TEXT NOT NULL, record_count INTEGER NOT NULL DEFAULT 0, legal_basis TEXT);
                CREATE TABLE IF NOT EXISTS integration_staging (id BIGSERIAL PRIMARY KEY, source_system TEXT NOT NULL, external_id TEXT NOT NULL, payload_hash TEXT NOT NULL, encrypted_payload TEXT NOT NULL, minimized_json TEXT NOT NULL, classification TEXT NOT NULL, legal_basis TEXT NOT NULL, received_at TEXT NOT NULL, status TEXT NOT NULL, UNIQUE(source_system, external_id, payload_hash));
                CREATE INDEX IF NOT EXISTS idx_incident_zone_time ON incidents(zone_id, occurred_at);
                CREATE INDEX IF NOT EXISTS idx_incident_geom ON incidents USING GIST (geom);
                CREATE INDEX IF NOT EXISTS idx_entity_value ON case_entities(normalized_value);
                CREATE INDEX IF NOT EXISTS idx_source_case ON source_records(case_id, recorded_at DESC);
                CREATE INDEX IF NOT EXISTS idx_audit_occurred ON audit_events(occurred_at DESC);
                """
            )
        else:
            conn.execute_script(
                """
                PRAGMA foreign_keys = ON;
                CREATE TABLE IF NOT EXISTS zones (id TEXT PRIMARY KEY, name TEXT NOT NULL, lat REAL NOT NULL, lng REAL NOT NULL, patrol_coverage REAL NOT NULL);
                CREATE TABLE IF NOT EXISTS cases (id TEXT PRIMARY KEY, zone_id TEXT NOT NULL REFERENCES zones(id), opened_at TEXT NOT NULL, status TEXT NOT NULL, summary TEXT NOT NULL, crime_type TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS incidents (id TEXT PRIMARY KEY, case_id TEXT NOT NULL REFERENCES cases(id), zone_id TEXT NOT NULL REFERENCES zones(id), crime_type TEXT NOT NULL, occurred_at TEXT NOT NULL, latitude REAL NOT NULL, longitude REAL NOT NULL, source TEXT NOT NULL, narrative TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS case_entities (id INTEGER PRIMARY KEY AUTOINCREMENT, case_id TEXT NOT NULL REFERENCES cases(id), entity_type TEXT NOT NULL, normalized_value TEXT NOT NULL, display_value TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS source_records (id INTEGER PRIMARY KEY AUTOINCREMENT, case_id TEXT NOT NULL REFERENCES cases(id), source_system TEXT NOT NULL, record_type TEXT NOT NULL, recorded_at TEXT NOT NULL, payload_json TEXT NOT NULL, confidence REAL NOT NULL);
                CREATE TABLE IF NOT EXISTS zone_context (zone_id TEXT PRIMARY KEY REFERENCES zones(id), population_band TEXT NOT NULL, traffic_index REAL NOT NULL, event_factor TEXT NOT NULL, unemployment_index REAL NOT NULL, updated_at TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password_hash TEXT NOT NULL, role TEXT NOT NULL CHECK(role IN ('analyst','supervisor','admin')), active INTEGER NOT NULL DEFAULT 1, created_at TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS audit_events (id INTEGER PRIMARY KEY AUTOINCREMENT, occurred_at TEXT NOT NULL, actor TEXT NOT NULL, role TEXT NOT NULL, action TEXT NOT NULL, resource TEXT NOT NULL, outcome TEXT NOT NULL, request_id TEXT NOT NULL, detail_json TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS integration_sync_runs (id INTEGER PRIMARY KEY AUTOINCREMENT, source_system TEXT NOT NULL, started_at TEXT NOT NULL, finished_at TEXT, status TEXT NOT NULL, record_count INTEGER NOT NULL DEFAULT 0, legal_basis TEXT);
                CREATE TABLE IF NOT EXISTS integration_staging (id INTEGER PRIMARY KEY AUTOINCREMENT, source_system TEXT NOT NULL, external_id TEXT NOT NULL, payload_hash TEXT NOT NULL, encrypted_payload TEXT NOT NULL, minimized_json TEXT NOT NULL, classification TEXT NOT NULL, legal_basis TEXT NOT NULL, received_at TEXT NOT NULL, status TEXT NOT NULL, UNIQUE(source_system, external_id, payload_hash));
                CREATE INDEX IF NOT EXISTS idx_incident_zone_time ON incidents(zone_id, occurred_at);
                CREATE INDEX IF NOT EXISTS idx_entity_value ON case_entities(normalized_value);
                CREATE INDEX IF NOT EXISTS idx_source_case ON source_records(case_id, recorded_at DESC);
                CREATE INDEX IF NOT EXISTS idx_audit_occurred ON audit_events(occurred_at DESC);
                """
            )
        
        incidents_count = conn.execute("SELECT COUNT(*) AS count FROM incidents").fetchone()["count"]
        if incidents_count < 15000 and settings.SEED_DEMO_DATA:
            conn.execute("DELETE FROM incidents")
            conn.execute("DELETE FROM case_entities")
            conn.execute("DELETE FROM source_records")
            conn.execute("DELETE FROM cases")
            conn.execute("DELETE FROM zone_context")
            conn.execute("DELETE FROM zones")
            seed_demo_data(conn)
        ensure_bootstrap_user(conn)
