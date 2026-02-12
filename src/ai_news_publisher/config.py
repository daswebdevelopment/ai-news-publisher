from __future__ import annotations

from dataclasses import dataclass
import os


@dataclass(frozen=True)
class Settings:
    app_name: str = "AI News Publisher"
    database_url: str = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/ai_news")
    openai_api_key: str | None = os.getenv("OPENAI_API_KEY")
    embedding_dimensions: int = int(os.getenv("EMBEDDING_DIMENSIONS", "16"))
    similarity_threshold: float = float(os.getenv("EVENT_SIMILARITY_THRESHOLD", "0.80"))
    base_url: str = os.getenv("PUBLISHER_BASE_URL", "https://news.example.com")
    digest_max_events: int = int(os.getenv("DIGEST_MAX_EVENTS", "10"))
    smtp_host: str = os.getenv("SMTP_HOST", "smtp.mailgun.org")
    smtp_port: int = int(os.getenv("SMTP_PORT", "587"))
    smtp_username: str | None = os.getenv("SMTP_USERNAME")
    smtp_password: str | None = os.getenv("SMTP_PASSWORD")
    digest_sender_email: str = os.getenv("DIGEST_SENDER_EMAIL", "digest@example.com")


settings = Settings()
