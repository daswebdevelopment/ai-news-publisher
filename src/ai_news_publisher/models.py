from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any
from urllib.parse import urlparse


@dataclass(frozen=True)
class NewsItem:
    title: str
    source: str
    url: str
    summary: str
    published_at: datetime
    category: str = "general"

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "NewsItem":
        if not isinstance(data, dict):
            raise ValueError("Each item must be an object/dictionary")

        title = _clean_required_text(data, "title")
        source = _clean_required_text(data, "source")
        url = _clean_required_text(data, "url")
        summary = _clean_required_text(data, "summary")
        _validate_http_url(url)

        published_at = _parse_published_at(data.get("published_at"))
        category = _clean_optional_text(data.get("category"), default="general").lower()

        return cls(
            title=title,
            source=source,
            url=url,
            summary=summary,
            published_at=published_at,
            category=category,
        )


def _clean_required_text(data: dict[str, Any], field: str) -> str:
    value = data.get(field)
    if value is None:
        raise ValueError(f"Missing required field: {field}")
    if not isinstance(value, str):
        raise ValueError(f"Field '{field}' must be a string")

    text = value.strip()
    if not text:
        raise ValueError(f"Field '{field}' must be a non-empty string")

    return text


def _clean_optional_text(value: Any, default: str) -> str:
    if value is None:
        return default
    if not isinstance(value, str):
        raise ValueError("Field 'category' must be a string")

    text = value.strip()
    return text or default


def _validate_http_url(url: str) -> None:
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError("Field 'url' must be a valid absolute HTTP(S) URL")


def _parse_published_at(raw_published_at: Any) -> datetime:
    if raw_published_at is None:
        raise ValueError("Missing required field: published_at")

    published_text = str(raw_published_at).strip()
    if not published_text:
        raise ValueError("Field 'published_at' must be a non-empty string")

    try:
        published_at = datetime.fromisoformat(published_text.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError("Field 'published_at' must be a valid ISO-8601 datetime") from exc

    # Normalize timestamps to timezone-aware UTC so sorting/comparison is stable.
    if published_at.tzinfo is None:
        return published_at.replace(tzinfo=timezone.utc)

    return published_at.astimezone(timezone.utc)
