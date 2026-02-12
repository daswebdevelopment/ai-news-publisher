from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from ai_news_publisher.infrastructure.email import EmailSender
from ai_news_publisher.services.digest import DailyDigest, DigestConfig, DigestService
from ai_news_publisher.services.publishing import PublishingService


@dataclass
class EmailDigestService:
    publishing_service: PublishingService
    digest_service: DigestService
    email_sender: EmailSender

    def send_daily_digest(
        self,
        recipient: str,
        digest_date: date | None = None,
        config: DigestConfig | None = None,
        category: str | None = None,
        country: str | None = None,
        city: str | None = None,
    ) -> DailyDigest:
        events = self.publishing_service.list_events(category=category, country=country, city=city)
        digest = self.digest_service.generate_daily_digest(events=events, digest_date=digest_date, config=config)
        self.email_sender.send_email(
            recipient=recipient,
            subject=digest.subject,
            text_body=digest.text_body,
            html_body=digest.html_body,
        )
        return digest
