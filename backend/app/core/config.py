"""Core settings and environment configuration validation."""

from __future__ import annotations

import os
from typing import List


class Settings:
    # General API Configuration
    PROJECT_NAME: str = "Sentinel Intelligence API"
    VERSION: str = "1.1.0"
    
    # Database
    DATABASE_URL: str | None = os.getenv("DATABASE_URL") or None
    SEED_DEMO_DATA: bool = os.getenv("SEED_DEMO_DATA", "true").lower() in {"1", "true", "yes"}

    # Security & Auth
    AUTH_REQUIRED: bool = os.getenv("AUTH_REQUIRED", "false").lower() in {"1", "true", "yes"}
    JWT_TTL_MINUTES: int = int(os.getenv("JWT_TTL_MINUTES", "30"))
    BOOTSTRAP_ADMIN_USERNAME: str = os.getenv("BOOTSTRAP_ADMIN_USERNAME", "sentinel-admin")
    BOOTSTRAP_ADMIN_PASSWORD: str | None = os.getenv("BOOTSTRAP_ADMIN_PASSWORD")

    # CORS Origins
    CORS_ORIGINS: List[str] = os.getenv(
        "CORS_ORIGINS", 
        "http://localhost:5173,http://127.0.0.1:5173,http://localhost:8080"
    ).split(",")

    # ICJS Ingestion Integration config
    ICJS_ENABLED: bool = os.getenv("ICJS_ENABLED", "false").lower() in {"1", "true", "yes"}
    ICJS_BASE_URL: str | None = os.getenv("ICJS_BASE_URL")
    ICJS_TOKEN_URL: str | None = os.getenv("ICJS_TOKEN_URL")
    ICJS_CLIENT_ID: str | None = os.getenv("ICJS_CLIENT_ID")
    ICJS_CLIENT_SECRET: str | None = os.getenv("ICJS_CLIENT_SECRET")
    ICJS_LEGAL_BASIS: str | None = os.getenv("ICJS_LEGAL_BASIS")
    DATA_ENCRYPTION_KEY: str | None = os.getenv("DATA_ENCRYPTION_KEY")
    ICJS_CASES_PATH: str = os.getenv("ICJS_CASES_PATH", "/v1/cases")

    @property
    def jwt_secret(self) -> str:
        secret = os.getenv("JWT_SECRET")
        if secret:
            return secret
        if self.AUTH_REQUIRED:
            raise RuntimeError("JWT_SECRET must be configured when AUTH_REQUIRED=true")
        return "development-only-not-for-production"


settings = Settings()
