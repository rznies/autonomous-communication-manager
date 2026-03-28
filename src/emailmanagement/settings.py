from __future__ import annotations

import os
import tempfile
from dataclasses import dataclass


def _parse_csv(value: str | None, default: tuple[str, ...]) -> tuple[str, ...]:
    if value is None:
        return default

    items = tuple(part.strip() for part in value.split(",") if part.strip())
    return items or default


@dataclass(frozen=True)
class AppSettings:
    environment: str
    db_path: str
    cors_origins: tuple[str, ...]
    mutation_api_key: str | None
    has_write_scope: bool
    docs_enabled: bool
    release_version: str
    build_sha: str | None

    @property
    def requires_api_key(self) -> bool:
        return bool(self.mutation_api_key)

    @property
    def auth_mode(self) -> str:
        return "x-acm-api-key" if self.requires_api_key else "none"

    @classmethod
    def from_env(cls) -> "AppSettings":
        environment = (
            os.getenv("ACM_ENV", "development").strip().lower() or "development"
        )
        default_db_path = os.path.join(tempfile.gettempdir(), "acm_api_state.db")
        if environment in {"staging", "production"}:
            default_db_path = os.path.join(os.getcwd(), "data", "acm_api_state.db")

        cors_default = ("http://localhost:5173",)
        docs_default = environment != "production"

        return cls(
            environment=environment,
            db_path=os.getenv("ACM_DB_PATH", default_db_path),
            cors_origins=_parse_csv(os.getenv("ACM_CORS_ORIGINS"), cors_default),
            mutation_api_key=os.getenv("ACM_MUTATION_API_KEY") or None,
            has_write_scope=os.getenv("ACM_HAS_WRITE_SCOPE", "false").lower() == "true",
            docs_enabled=os.getenv("ACM_ENABLE_DOCS", str(docs_default).lower()).lower()
            == "true",
            release_version=os.getenv("ACM_RELEASE_VERSION", "0.1.0"),
            build_sha=os.getenv("ACM_BUILD_SHA") or None,
        )
