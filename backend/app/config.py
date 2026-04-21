from pathlib import Path
from typing import Any

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

_BACKEND_DIR = Path(__file__).resolve().parent.parent
_MONOREPO_ROOT = _BACKEND_DIR.parent
# Monorepo `.env` then `backend/.env` (backend wins on duplicate keys). Docker sets
# vars in the process env; optional files are skipped if missing.
_ENV_FILES = tuple(
    p
    for p in (_MONOREPO_ROOT / ".env", _BACKEND_DIR / ".env")
    if p.is_file()
)
REPO_ROOT = _BACKEND_DIR


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=_ENV_FILES if _ENV_FILES else (".env",),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    backend_cors_origins: str = "http://localhost:3000,https://dentnav.vercel.app"
    cors_origin_regex: str | None = r"^https://[^/]+\.vercel\.app$"
    frontend_base_url: str = "http://localhost:3000"
    database_url: str = "postgresql://postgres:postgres@localhost:15432/dentnav"

    aws_region: str = "us-east-1"
    aws_s3_bucket: str = ""
    aws_s3_questionnaire_key: str = ""

    questionnaire_local_path: Path = REPO_ROOT / "data" / "questionnaire.v1.json"

    google_client_id: str = ""
    google_client_secret: str = ""
    google_redirect_uri: str = ""

    openai_api_key: str = ""
    openai_model: str = "gpt-4.1"

    @field_validator("cors_origin_regex", mode="before")
    @classmethod
    def _cors_regex_empty_means_default(cls, v: Any) -> Any:
        if v == "":
            return r"^https://[^/]+\.vercel\.app$"
        return v

    @property
    def cors_origins(self) -> list[str]:
        return [o.strip() for o in self.backend_cors_origins.split(",") if o.strip()]

    @property
    def cors_origin_regex_effective(self) -> str | None:
        if self.cors_origin_regex is None:
            return None
        s = self.cors_origin_regex.strip()
        return s or None

    @property
    def analysis_mock_path(self) -> Path:
        for candidate in (
            REPO_ROOT / "data" / "analysis-mock.json",
            Path("/app/data/analysis-mock.json"),
        ):
            if candidate.exists():
                return candidate
        return REPO_ROOT / "data" / "analysis-mock.json"

    @property
    def has_google_oauth_config(self) -> bool:
        return bool(
            self.google_client_id and self.google_client_secret and self.google_redirect_uri
        )

    @property
    def has_openai_config(self) -> bool:
        return bool(self.openai_api_key)


settings = Settings()
