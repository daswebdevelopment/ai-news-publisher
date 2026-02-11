from __future__ import annotations

from collections import defaultdict
from datetime import date

from .models import NewsItem


def normalize_items(raw_items: list[dict]) -> list[NewsItem]:
    """Convert raw dictionaries into validated NewsItem objects.

    Duplicate URLs are collapsed by keeping the most recently published story,
    and items are sorted by publication time descending.
    """

    latest_by_url: dict[str, NewsItem] = {}

    for raw in raw_items:
        item = NewsItem.from_dict(raw)
        existing = latest_by_url.get(item.url)
        if existing is None or item.published_at > existing.published_at:
            latest_by_url[item.url] = item

    normalized = list(latest_by_url.values())
    normalized.sort(key=lambda item: item.published_at, reverse=True)
    return normalized


def generate_markdown_digest(items: list[NewsItem], digest_date: date | None = None) -> str:
    """Render normalized items into a grouped markdown digest."""

    digest_date = digest_date or date.today()
    grouped: dict[str, list[NewsItem]] = defaultdict(list)
    for item in items:
        grouped[item.category].append(item)

    lines = [f"# AI News Digest - {digest_date.isoformat()}", ""]
    for category in sorted(grouped):
        lines.append(f"## {category.title()}")
        lines.append("")
        for item in grouped[category]:
            stamp = item.published_at.strftime("%Y-%m-%d %H:%M")
            lines.append(f"- [{item.title}]({item.url}) — **{item.source}** ({stamp})")
            lines.append(f"  - {item.summary}")
        lines.append("")

    if len(lines) == 2:
        lines.extend(["_No stories available._", ""])

    return "\n".join(lines).rstrip() + "\n"
