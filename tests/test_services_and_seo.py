from datetime import datetime, timezone

from ai_news_publisher.domain.models import Event, SourceLink
from ai_news_publisher.seo import build_seo_metadata
from ai_news_publisher.services.localization import LocalizationService, Location
from ai_news_publisher.services.summarization import SummaryService
from ai_news_publisher.monitoring import monitoring_store


def _event() -> Event:
    return Event(
        event_id="evt1",
        slug="sample-event",
        title="Sample Event",
        category="tech",
        country="US",
        city="Austin",
        occurred_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
        confidence=0.8,
        source_diversity=2,
        source_count=2,
        embedding=[0.1] * 16,
        source_links=[SourceLink("A", "https://a.com", datetime(2026, 1, 1, tzinfo=timezone.utc))],
        summary={"what_happened": "A major AI event happened.", "where_when": "Austin", "why_it_matters": "Impact", "what_next": "More updates"},
        status="Confirmed",
        bias_indicator="low",
    )


def test_summary_service_cache_and_structure():
    service = SummaryService()
    event = _event()
    first = service.summarize(event)
    second = service.summarize(event)
    assert first is second
    assert set(first) == {"what_happened", "where_when", "why_it_matters", "what_next", "status", "bias_indicator"}


def test_localization_fallback_and_cache():
    service = LocalizationService()
    event = _event()
    first = service.local_impact(event, Location(country="IN", city="Pune"))
    second = service.local_impact(event, Location(country="IN", city="Pune"))
    assert first == "No direct local impact identified at this time."
    assert first is second


def test_seo_metadata_contains_json_ld_and_social_tags():
    metadata = build_seo_metadata(_event(), "Austin")
    assert metadata["canonical_url"].endswith("/events/sample-event")
    assert metadata["open_graph"]["title"].startswith("Sample Event")
    assert metadata["json_ld"]["@type"] == "NewsArticle"


def test_summary_service_records_ai_usage_once_per_event():
    service = SummaryService()
    event = _event()
    before = monitoring_store.snapshot()["ai_calls"]

    service.summarize(event)
    service.summarize(event)

    after = monitoring_store.snapshot()["ai_calls"]
    assert after == before + 1
