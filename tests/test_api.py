from datetime import datetime, timezone

import pytest

fastapi = pytest.importorskip("fastapi")
from fastapi.testclient import TestClient

from ai_news_publisher.api.app import app, repository
from ai_news_publisher.domain.models import Event, SourceLink


client = TestClient(app)


def setup_module(module):
    repository.upsert_events([
        Event(
            event_id="evt2",
            slug="chip-event",
            title="Chip Event",
            category="tech",
            country="US",
            city="Austin",
            occurred_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
            confidence=0.9,
            source_diversity=2,
            source_count=2,
            embedding=[0.1] * 16,
            source_links=[SourceLink("A", "https://a.com/1", datetime(2026, 1, 1, tzinfo=timezone.utc))],
            summary={"what_happened": "AI summary", "where_when": "US", "why_it_matters": "Impact", "what_next": "Soon"},
            status="Confirmed",
            bias_indicator="low",
        )
    ])


def test_list_events_with_filters_and_cache_header():
    response = client.get("/api/events?category=tech&country=US")
    assert response.status_code == 200
    assert response.headers["cache-control"] == "public, max-age=300"
    body = response.json()
    assert len(body["events"]) == 1
    assert "ai_generated_notice" in body["events"][0]


def test_event_detail_never_exposes_raw_content_and_has_seo():
    response = client.get("/api/events/chip-event")
    assert response.status_code == 200
    payload = response.json()
    assert "raw_text" not in payload
    assert "seo" in payload
    assert payload["seo"]["json_ld"]["@type"] == "NewsArticle"


def test_local_impact_endpoint():
    response = client.get("/api/events/chip-event/local-impact?country=US&city=Austin")
    assert response.status_code == 200
    assert "Why this matters to YOU" in response.json()["local_impact"]


def test_send_digest_endpoint(monkeypatch):
    sent = {}

    class StubDigestService:
        def send_daily_digest(self, recipient, digest_date=None, config=None, category=None, country=None, city=None):
            sent["recipient"] = recipient
            sent["max_events"] = config.max_events if config else None
            return type("Digest", (), {"subject": "Daily AI News Digest", "included_event_ids": ["evt2"]})()

    monkeypatch.setattr("ai_news_publisher.api.app.email_digest_service", StubDigestService())
    response = client.post("/api/digest/send?recipient=user@example.com&max_events=3")
    assert response.status_code == 200
    body = response.json()
    assert body["sent"] is True
    assert body["recipient"] == "user@example.com"
    assert body["included_event_ids"] == ["evt2"]
    assert sent["max_events"] == 3


def test_detailed_health_and_monitoring_snapshot_endpoints():
    health = client.get("/health/detailed")
    assert health.status_code == 200
    payload = health.json()
    assert payload["status"] == "ok"
    assert "monitoring" in payload
    assert "ai_calls" in payload["monitoring"]

    monitoring = client.get("/api/monitoring")
    assert monitoring.status_code == 200
    m_payload = monitoring.json()
    assert "total_estimated_cost_usd" in m_payload


def test_send_digest_endpoint_failure_is_tracked(monkeypatch):
    class FailingDigestService:
        def send_daily_digest(self, *args, **kwargs):
            raise RuntimeError("smtp down")

    monkeypatch.setattr("ai_news_publisher.api.app.email_digest_service", FailingDigestService())
    before = client.get("/api/monitoring").json()["publishing_failures"]

    response = client.post("/api/digest/send?recipient=user@example.com")
    assert response.status_code == 500

    after = client.get("/api/monitoring").json()["publishing_failures"]
    assert after >= before + 1
