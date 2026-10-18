"""Central configuration. Everything comes from environment variables so the
same code runs in dev (SQLite, no email) and production (Postgres, SMTP)."""

import os


def _get(name: str, default: str = "") -> str:
    return os.environ.get(name, default)


def _get_int(name: str, default: int) -> int:
    try:
        return int(_get(name, "") or default)
    except ValueError:
        return default


class Settings:
    APP_NAME = "Rizz Edits Studio API"
    DATABASE_URL = _get("DATABASE_URL", "sqlite:///./rizz_studio.db")
    ALLOWED_ORIGINS = [
        origin.strip()
        for origin in _get("ALLOWED_ORIGINS", "").split(",")
        if origin.strip()
    ]
    ADMIN_API_KEY = _get("ADMIN_API_KEY", "")
    RESEND_API_KEY = _get("RESEND_API_KEY", "")
    RESEND_FROM = _get("RESEND_FROM", "")
    SMTP_HOST = _get("SMTP_HOST", "")
    SMTP_PORT = _get_int("SMTP_PORT", 587)
    SMTP_USER = _get("SMTP_USER", "")
    SMTP_PASSWORD = _get("SMTP_PASSWORD", "")
    SMTP_FROM = _get("SMTP_FROM", "") or _get("SMTP_USER", "")
    NOTIFY_TO = _get("NOTIFY_TO", "")
    RATE_LIMIT_PER_MINUTE = _get_int("RATE_LIMIT_PER_MINUTE", 20)


settings = Settings()
