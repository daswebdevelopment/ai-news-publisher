from datetime import date, datetime, timezone

from ai_news_publisher.domain.models import Event, SourceLink
from ai_news_publisher.infrastructure.email import InMemoryEmailSender
from ai_news_publisher.infrastructure.repository import InMemoryEventRepository
from ai_news_publisher.services.digest import DigestConfig, DigestService
from ai_news_publisher.services.email_digest import EmailDigestService
from ai_news_publisher.services.publishing import PublishingService


def _event(event_id: str, category: str, confidence: float, city: str) -> Event:
    return Event(
        event_id=event_id,
        slug=f"slug-{event_id}",
        title=f"{category} Event {event_id}",
        category=category,
        country="US",
        city=city,
        occurred_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
        confidence=confidence,
        source_diversity=2,
        source_count=2,
        embedding=[0.1] * 16,
        source_links=[SourceLink("A", f"https://example.com/{event_id}", datetime(2026, 1, 1, tzinfo=timezone.utc))],
        summary={
            "what_happened": f"What happened for {event_id}",
            "where_when": "US",
            "why_it_matters": f"Impact for {event_id}",
            "what_next": "Next",
        },
        status="Confirmed",
        bias_indicator="low",
    )


def test_digest_generation_groups_topics_and_limits_length():
    service = DigestService()
    events = [
        _event("1", "tech", 0.90, "Austin"),
        _event("2", "climate", 0.95, "Miami"),
        _event("3", "tech", 0.70, "Austin"),
    ]

    digest = service.generate_daily_digest(events, digest_date=date(2026, 1, 2), config=DigestConfig(max_events=2))

    assert digest.subject == "Daily AI News Digest — 2026-01-02"
    assert digest.included_event_ids == ["2", "1"]
    assert "Climate" in digest.text_body
    assert "Tech" in digest.text_body
    assert "Why this matters:" in digest.text_body
    assert "<html><body>" in digest.html_body


def test_email_digest_service_sends_email_with_reused_summaries():
    repo = InMemoryEventRepository()
    repo.upsert_events([_event("10", "policy", 0.88, "Boston")])

    sender = InMemoryEmailSender()
    service = EmailDigestService(
        publishing_service=PublishingService(repo),
        digest_service=DigestService(),
        email_sender=sender,
    )

    digest = service.send_daily_digest(
        recipient="user@example.com",
        digest_date=date(2026, 1, 3),
        config=DigestConfig(max_events=5),
    )

    assert digest.included_event_ids == ["10"]
    assert len(sender.sent) == 1
    assert sender.sent[0]["recipient"] == "user@example.com"
    assert "What happened for 10" in sender.sent[0]["text_body"]
