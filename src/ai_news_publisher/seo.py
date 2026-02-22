from __future__ import annotations

from ai_news_publisher.config import settings
from ai_news_publisher.domain.models import Event


def build_seo_metadata(event: Event, location_suffix: str | None = None) -> dict[str, object]:
    suffix = f" - {location_suffix}" if location_suffix else ""
    canonical = f"{settings.base_url}/events/{event.slug}"
    title = f"{event.title}{suffix} | AI News Publisher"
    description = event.summary["what_happened"][:155]
    og_image = f"{settings.base_url}/og/{event.slug}.png"
    return {
        "title": title,
        "description": description,
        "canonical_url": canonical,
        "open_graph": {"title": title, "description": description, "url": canonical, "image": og_image},
        "twitter": {"card": "summary_large_image", "title": title, "description": description},
        "json_ld": {
            "@context": "https://schema.org",
            "@type": "NewsArticle",
            "headline": title,
            "description": description,
            "datePublished": event.occurred_at.isoformat(),
            "mainEntityOfPage": canonical,
        },
    }
