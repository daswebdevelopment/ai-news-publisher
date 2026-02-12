from __future__ import annotations

from ai_news_publisher.infrastructure.repository import EventRepository


class PublishingService:
    def __init__(self, repository: EventRepository) -> None:
        self.repository = repository

    def list_events(self, category: str | None = None, country: str | None = None, city: str | None = None) -> list:
        events = self.repository.list_events()
        if category:
            events = [e for e in events if e.category.lower() == category.lower()]
        if country:
            events = [e for e in events if e.country.lower() == country.lower()]
        if city:
            events = [e for e in events if e.city.lower() == city.lower()]
        return events

    def get_event(self, slug: str):
        return self.repository.get_by_slug(slug)
