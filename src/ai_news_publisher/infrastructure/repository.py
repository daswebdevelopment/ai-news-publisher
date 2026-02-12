from __future__ import annotations

from dataclasses import asdict

from ai_news_publisher.domain.models import Event


class EventRepository:
    def upsert_events(self, events: list[Event]) -> None:
        raise NotImplementedError

    def list_events(self) -> list[Event]:
        raise NotImplementedError

    def get_by_slug(self, slug: str) -> Event | None:
        raise NotImplementedError


class InMemoryEventRepository(EventRepository):
    def __init__(self) -> None:
        self._events_by_slug: dict[str, Event] = {}

    def upsert_events(self, events: list[Event]) -> None:
        for event in events:
            self._events_by_slug[event.slug] = event

    def list_events(self) -> list[Event]:
        return sorted(self._events_by_slug.values(), key=lambda e: e.occurred_at, reverse=True)

    def get_by_slug(self, slug: str) -> Event | None:
        return self._events_by_slug.get(slug)


POSTGRES_SCHEMA_SQL = """
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS events (
  event_id TEXT PRIMARY KEY,
  slug TEXT UNIQUE NOT NULL,
  title TEXT NOT NULL,
  category TEXT NOT NULL,
  country TEXT NOT NULL,
  city TEXT NOT NULL,
  occurred_at TIMESTAMPTZ NOT NULL,
  confidence DOUBLE PRECISION NOT NULL,
  source_diversity INT NOT NULL,
  source_count INT NOT NULL,
  summary JSONB NOT NULL,
  status TEXT NOT NULL,
  bias_indicator TEXT NOT NULL,
  ai_generated_notice TEXT NOT NULL,
  embedding VECTOR(16) NOT NULL,
  source_links JSONB NOT NULL
);

CREATE INDEX IF NOT EXISTS events_embedding_idx ON events USING ivfflat (embedding vector_cosine_ops);
CREATE INDEX IF NOT EXISTS events_category_country_city_idx ON events (category, country, city);
"""
