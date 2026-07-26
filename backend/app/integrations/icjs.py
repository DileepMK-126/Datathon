"""Governed ICJS adapter.

The public ICJS site describes a secured, stakeholder API gateway, not a public
case-data endpoint. This adapter is intentionally inert until an authorised
agency supplies the contract, endpoint, client credentials, legal basis, and
encryption key through the deployment secret store.
"""

from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timezone
from typing import Any

import httpx
from cryptography.fernet import Fernet

from ..db.connection import connection


class ICJSConfigurationError(RuntimeError):
    pass


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def configured() -> bool:
    return os.getenv("ICJS_ENABLED", "false").lower() in {"1", "true", "yes"}


def configuration_status() -> dict[str, Any]:
    required = ("ICJS_BASE_URL", "ICJS_TOKEN_URL", "ICJS_CLIENT_ID", "ICJS_CLIENT_SECRET", "ICJS_LEGAL_BASIS", "DATA_ENCRYPTION_KEY")
    missing = [name for name in required if not os.getenv(name)]
    return {"enabled": configured(), "ready": configured() and not missing, "missing": missing, "records_are_encrypted": bool(os.getenv("DATA_ENCRYPTION_KEY")), "mode": "authorised connector" if configured() else "disabled"}


def _fernet() -> Fernet:
    key = os.getenv("DATA_ENCRYPTION_KEY")
    if not key:
        raise ICJSConfigurationError("DATA_ENCRYPTION_KEY must be provided by the secret manager")
    try:
        return Fernet(key.encode())
    except (ValueError, TypeError) as exc:
        raise ICJSConfigurationError("DATA_ENCRYPTION_KEY is not a valid Fernet key") from exc


def _minimise(record: dict[str, Any]) -> dict[str, Any]:
    """Keep only the analytical fields approved for Sentinel's staging boundary."""
    external_id = str(record.get("fir_number") or record.get("case_id") or record.get("id") or "")
    if not external_id:
        raise ValueError("ICJS record has no agreed external case identifier")
    return {
        "external_id": external_id,
        "crime_type": record.get("crime_type"),
        "occurred_at": record.get("occurred_at"),
        "zone_reference": record.get("zone_id") or record.get("police_station_code"),
        "latitude": record.get("latitude"),
        "longitude": record.get("longitude"),
        "source_version": record.get("version"),
    }


def _access_token(client: httpx.Client) -> str:
    response = client.post(
        os.environ["ICJS_TOKEN_URL"],
        data={"grant_type": "client_credentials", "client_id": os.environ["ICJS_CLIENT_ID"], "client_secret": os.environ["ICJS_CLIENT_SECRET"]},
    )
    response.raise_for_status()
    return response.json()["access_token"]


def sync_cases() -> dict[str, Any]:
    status = configuration_status()
    if not status["ready"]:
        raise ICJSConfigurationError(f"ICJS connector is not ready: {', '.join(status['missing'])}")
    encrypted = _fernet()
    started_at = utc_now()
    with connection() as conn:
        run = conn.execute("INSERT INTO integration_sync_runs(source_system, started_at, status, legal_basis) VALUES (?, ?, ?, ?)", ("ICJS", started_at, "running", os.environ["ICJS_LEGAL_BASIS"]))
        run_id = run.lastrowid if hasattr(run, "lastrowid") else None

    try:
        with httpx.Client(timeout=20.0, verify=True) as client:
            token = _access_token(client)
            path = os.getenv("ICJS_CASES_PATH", "/v1/cases")
            response = client.get(f"{os.environ['ICJS_BASE_URL'].rstrip('/')}{path}", headers={"Authorization": f"Bearer {token}", "Accept": "application/json"})
            response.raise_for_status()
            payload = response.json()
        records = payload.get("items", payload) if isinstance(payload, dict) else payload
        if not isinstance(records, list):
            raise ValueError("ICJS response must be a record list or an object with an items list")
        accepted = 0
        with connection() as conn:
            for record in records:
                minimized = _minimise(record)
                canonical = json.dumps(record, sort_keys=True, separators=(",", ":"))
                fingerprint = hashlib.sha256(canonical.encode()).hexdigest()
                cipher_text = encrypted.encrypt(canonical.encode()).decode()
                existing = conn.execute("SELECT id FROM integration_staging WHERE source_system = ? AND external_id = ? AND payload_hash = ?", ("ICJS", minimized["external_id"], fingerprint)).fetchone()
                if existing:
                    continue
                conn.execute(
                    """INSERT INTO integration_staging(source_system, external_id, payload_hash, encrypted_payload, minimized_json, classification, legal_basis, received_at, status)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    ("ICJS", minimized["external_id"], fingerprint, cipher_text, json.dumps(minimized, separators=(",", ":")), "restricted", os.environ["ICJS_LEGAL_BASIS"], utc_now(), "pending_review"),
                )
                accepted += 1
            conn.execute("UPDATE integration_sync_runs SET finished_at = ?, status = ?, record_count = ? WHERE started_at = ? AND source_system = ?", (utc_now(), "completed", accepted, started_at, "ICJS"))
        return {"status": "completed", "received": len(records), "staged": accepted, "legal_basis": os.environ["ICJS_LEGAL_BASIS"], "raw_payloads_encrypted": True}
    except Exception:
        with connection() as conn:
            conn.execute("UPDATE integration_sync_runs SET finished_at = ?, status = ? WHERE started_at = ? AND source_system = ?", (utc_now(), "failed", started_at, "ICJS"))
        raise
