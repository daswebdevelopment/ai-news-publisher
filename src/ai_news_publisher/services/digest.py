from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from html import escape
from typing import Iterable

from ai_news_publisher.domain.models import Event


@dataclass(frozen=True)
class DigestConfig:
    max_events: int = 10


@dataclass(frozen=True)
class DailyDigest:
    subject: str
    text_body: str
    html_body: str
    included_event_ids: list[str]


class DigestService:
    """Builds reusable daily email digests from existing event summaries.

    This service only consumes already-generated summaries and never performs
    additional AI calls.
    """

    def generate_daily_digest(
        self,
        events: Iterable[Event],
        digest_date: date | None = None,
        config: DigestConfig | None = None,
    ) -> DailyDigest:
        cfg = config or DigestConfig()
        digest_date = digest_date or date.today()

        ordered = sorted(events, key=lambda e: (e.confidence, e.occurred_at), reverse=True)
        selected = ordered[: max(cfg.max_events, 0)]

        grouped: dict[str, list[Event]] = {}
        for event in selected:
            grouped.setdefault(event.category.lower(), []).append(event)

        subject = f"Daily AI News Digest — {digest_date.isoformat()}"

        if not selected:
            empty_text = "No important events were identified for today."
            empty_html = "<p>No important events were identified for today.</p>"
            return DailyDigest(subject=subject, text_body=empty_text, html_body=empty_html, included_event_ids=[])

        text_lines = [f"Daily AI News Digest ({digest_date.isoformat()})", ""]
        html_parts = [
            "<html><body>",
            f"<h1>Daily AI News Digest <small>{escape(digest_date.isoformat())}</small></h1>",
        ]

        for category in sorted(grouped):
            text_lines.append(f"{category.title()}")
            text_lines.append("-" * len(category))
            html_parts.append(f"<h2>{escape(category.title())}</h2>")
            html_parts.append("<ul>")

            for event in grouped[category]:
                why = event.summary.get("why_it_matters", "Why this matters: updates may affect local and global stakeholders.")
                happened = event.summary.get("what_happened", event.title)
                text_lines.append(f"• {event.title} [{event.country}/{event.city}] (confidence: {event.confidence:.2f})")
                text_lines.append(f"  What happened: {happened}")
                text_lines.append(f"  Why this matters: {why}")
                text_lines.append("")

                html_parts.append("<li>")
                html_parts.append(f"<strong>{escape(event.title)}</strong> <em>({escape(event.country)}/{escape(event.city)})</em> — confidence {event.confidence:.2f}")
                html_parts.append(f"<p><strong>What happened:</strong> {escape(happened)}</p>")
                html_parts.append(f"<p><strong>Why this matters:</strong> {escape(why)}</p>")
                html_parts.append("</li>")

            html_parts.append("</ul>")

        text_lines.append(selected[0].ai_generated_notice)
        html_parts.append(f"<p><small>{escape(selected[0].ai_generated_notice)}</small></p>")
        html_parts.append("</body></html>")

        return DailyDigest(
            subject=subject,
            text_body="\n".join(text_lines).strip() + "\n",
            html_body="\n".join(html_parts),
            included_event_ids=[e.event_id for e in selected],
        )
