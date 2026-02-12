import asyncio
from datetime import datetime, timezone

from ai_news_publisher.infrastructure.embeddings import DeterministicEmbedder
from ai_news_publisher.infrastructure.repository import InMemoryEventRepository
from ai_news_publisher.infrastructure.rss import RawArticle
from ai_news_publisher.services.ingestion import IngestionService
from ai_news_publisher.services.summarization import SummaryService


class StubFetcher:
    async def fetch_many(self, feeds):
        return [
            RawArticle("A", "AI chip launch", "https://a.com/1", "new ai chip announced", datetime(2026, 1, 1, tzinfo=timezone.utc), "US", "Austin", "tech"),
            RawArticle("B", "AI chip launch", "https://b.com/1", "new ai chip announced", datetime(2026, 1, 1, 1, tzinfo=timezone.utc), "US", "Austin", "tech"),
            RawArticle("C", "Flood warning", "https://c.com/1", "rain and flood warning", datetime(2026, 1, 2, tzinfo=timezone.utc), "US", "Miami", "climate"),
        ]


def test_ingestion_clusters_and_scores_confidence():
    service = IngestionService(
        repository=InMemoryEventRepository(),
        fetcher=StubFetcher(),
        summary_service=SummaryService(),
        embedder=DeterministicEmbedder(16),
    )

    events = asyncio.run(service.ingest([{"url": "unused"}]))

    assert len(events) == 2
    tech_event = next(e for e in events if e.category == "tech")
    assert tech_event.source_count == 2
    assert tech_event.source_diversity == 2
    assert 0.65 <= tech_event.confidence <= 1.0
    assert "what_happened" in tech_event.summary
