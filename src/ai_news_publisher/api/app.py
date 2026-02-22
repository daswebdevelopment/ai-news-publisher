from __future__ import annotations

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse

from ai_news_publisher.infrastructure.repository import InMemoryEventRepository
from ai_news_publisher.config import settings
from ai_news_publisher.infrastructure.email import EmailSettings, SMTPEmailSender
from ai_news_publisher.services.digest import DigestConfig, DigestService
from ai_news_publisher.services.email_digest import EmailDigestService
from ai_news_publisher.seo import build_seo_metadata
from ai_news_publisher.services.localization import LocalizationService, Location
from ai_news_publisher.services.publishing import PublishingService
from ai_news_publisher.monitoring import monitoring_store

app = FastAPI(title="AI News Publisher API", version="1.0.0")
repository = InMemoryEventRepository()
publishing_service = PublishingService(repository)
localization_service = LocalizationService()
email_digest_service = EmailDigestService(
    publishing_service=publishing_service,
    digest_service=DigestService(),
    email_sender=SMTPEmailSender(
        EmailSettings(
            host=settings.smtp_host,
            port=settings.smtp_port,
            username=settings.smtp_username,
            password=settings.smtp_password,
            sender=settings.digest_sender_email,
        )
    ),
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/health/detailed")
def detailed_health() -> dict[str, object]:
    snapshot = monitoring_store.snapshot()
    return {
        "status": "ok",
        "monitoring": snapshot,
    }


@app.get("/api/events")
def list_events(
    category: str | None = Query(default=None),
    country: str | None = Query(default=None),
    city: str | None = Query(default=None),
):
    events = publishing_service.list_events(category=category, country=country, city=city)
    payload = []
    for event in events:
        payload.append(
            {
                "slug": event.slug,
                "title": event.title,
                "category": event.category,
                "country": event.country,
                "city": event.city,
                "summary": event.summary,
                "confidence": event.confidence,
                "status": event.status,
                "ai_generated_notice": event.ai_generated_notice,
            }
        )
    response = JSONResponse({"events": payload})
    response.headers["Cache-Control"] = "public, max-age=300"
    return response


@app.get("/api/events/{slug}")
def event_detail(slug: str):
    event = publishing_service.get_event(slug)
    if not event:
        monitoring_store.record_publishing_failure(f"event_not_found:{slug}")
        raise HTTPException(status_code=404, detail="Event not found")
    response = JSONResponse(
        {
            "slug": event.slug,
            "title": event.title,
            "summary": event.summary,
            "confidence": event.confidence,
            "status": event.status,
            "bias_indicator": event.bias_indicator,
            "source_links": [link.url for link in event.source_links],
            "ai_generated_notice": event.ai_generated_notice,
            "seo": build_seo_metadata(event),
        }
    )
    response.headers["Cache-Control"] = "public, max-age=600"
    return response


@app.get("/api/events/{slug}/local-impact")
def local_impact(slug: str, country: str, state: str | None = None, city: str | None = None):
    event = publishing_service.get_event(slug)
    if not event:
        monitoring_store.record_publishing_failure(f"event_not_found:{slug}")
        raise HTTPException(status_code=404, detail="Event not found")
    impact = localization_service.local_impact(event, Location(country=country, state=state, city=city))
    return {"slug": slug, "local_impact": impact, "ai_generated_notice": event.ai_generated_notice}


@app.post("/api/digest/send")
def send_digest(
    recipient: str,
    max_events: int | None = None,
    category: str | None = Query(default=None),
    country: str | None = Query(default=None),
    city: str | None = Query(default=None),
):
    config = DigestConfig(max_events=max_events if max_events is not None else settings.digest_max_events)
    try:
        digest = email_digest_service.send_daily_digest(
            recipient=recipient,
            config=config,
            category=category,
            country=country,
            city=city,
        )
    except Exception as exc:
        monitoring_store.record_publishing_failure(f"digest_send_failed:{exc}")
        raise HTTPException(status_code=500, detail="Failed to send digest") from exc

    return {
        "sent": True,
        "recipient": recipient,
        "subject": digest.subject,
        "included_event_ids": digest.included_event_ids,
    }


@app.get("/api/monitoring")
def monitoring_snapshot() -> dict[str, object]:
    return monitoring_store.snapshot()
