from pathlib import Path
from typing import Any, List, Optional

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


REPO_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Comma-separated origins; env BACKEND_CORS_ORIGINS overrides in production.
    backend_cors_origins: str = (
        "http://localhost:3000,https://dentnav.vercel.app"
    )
    # Matches production + preview deploys (https://<anything>.vercel.app).
    # Env CORS_ORIGIN_REGEX. Empty string on Railway would otherwise disable regex — see validator.
    cors_origin_regex: Optional[str] = r"^https://[^/]+\.vercel\.app$"
    # OAuth redirects; override FRONTEND_BASE_URL on Railway (e.g. https://dentnav.vercel.app).
    frontend_base_url: str = "http://localhost:3000"
    database_url: str = "postgresql://postgres:postgres@localhost:5432/dentnav?schema=public"

    # Questionnaire source from S3.
    aws_region: str = "us-east-1"
    aws_s3_bucket: str = ""
    aws_s3_questionnaire_key: str = ""

    # Google OAuth settings
    google_client_id: str = ""
    google_client_secret: str = ""
    google_redirect_uri: str = ""

    # Groq LLM settings for pathway analysis
    groq_api_key: str = ""
    groq_model: str = "llama-3.3-70b-versatile"

    @field_validator("cors_origin_regex", mode="before")
    @classmethod
    def _cors_regex_empty_means_default(cls, v: Any) -> Any:
        # Railway UI sometimes sets CORS_ORIGIN_REGEX to blank, which would drop Vercel previews.
        if v == "":
            return r"^https://[^/]+\.vercel\.app$"
        return v

    @property
    def cors_origins(self) -> List[str]:
        return [origin.strip() for origin in self.backend_cors_origins.split(",") if origin.strip()]

    @property
    def cors_origin_regex_effective(self) -> Optional[str]:
        if self.cors_origin_regex is None:
            return None
        s = self.cors_origin_regex.strip()
        return s or None

    @property
    def analysis_mock_path(self) -> Path:
        candidates = [
            REPO_ROOT / "data" / "analysis-mock.json",
            Path("/app/data/analysis-mock.json"),
            Path("/data/analysis-mock.json"),
        ]
        for candidate in candidates:
            if candidate.exists():
                return candidate
        return candidates[0]

    @property
    def has_google_oauth_config(self) -> bool:
        return bool(self.google_client_id and self.google_client_secret and self.google_redirect_uri)

    @property
    def has_groq_config(self) -> bool:
        return bool(self.groq_api_key)


settings = Settings()
