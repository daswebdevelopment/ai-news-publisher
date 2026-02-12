from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha1

from ai_news_publisher.config import settings
from ai_news_publisher.domain.models import Event, SourceLink, average, make_slug
from ai_news_publisher.infrastructure.embeddings import DeterministicEmbedder, cosine_similarity
from ai_news_publisher.infrastructure.repository import EventRepository
from ai_news_publisher.infrastructure.rss import RSSFetcher, RawArticle
from ai_news_publisher.services.summarization import SummaryService
from ai_news_publisher.monitoring import monitoring_store


@dataclass
class IngestionService:
    repository: EventRepository
    fetcher: RSSFetcher
    summary_service: SummaryService
    embedder: DeterministicEmbedder

    async def ingest(self, feeds: list[dict[str, str]]) -> list[Event]:
        try:
            articles = await self.fetcher.fetch_many(feeds)
            clusters = self._cluster_articles(articles)
            events = [self._to_event(cluster) for cluster in clusters]
            self.repository.upsert_events(events)
            return events
        except Exception as exc:
            monitoring_store.record_ingestion_failure(str(exc))
            raise

    def _cluster_articles(self, articles: list[RawArticle]) -> list[list[RawArticle]]:
        clusters: list[list[RawArticle]] = []
        vectors: list[list[float]] = []
        for article in articles:
            vector = self.embedder.embed(f"{article.title} {article.description}")
            best_idx = -1
            best_score = -1.0
            for idx, cluster_vec in enumerate(vectors):
                score = cosine_similarity(vector, cluster_vec)
                if score > best_score:
                    best_score, best_idx = score, idx
            if best_score >= settings.similarity_threshold and best_idx >= 0:
                clusters[best_idx].append(article)
                vectors[best_idx] = average([
                    self.embedder.embed(f"{a.title} {a.description}") for a in clusters[best_idx]
                ])
            else:
                clusters.append([article])
                vectors.append(vector)
        return clusters

    def _to_event(self, cluster: list[RawArticle]) -> Event:
        primary = max(cluster, key=lambda a: a.published_at)
        source_count = len(cluster)
        source_diversity = len({a.source_name for a in cluster})
        time_spread_hours = (max(a.published_at for a in cluster) - min(a.published_at for a in cluster)).total_seconds() / 3600 if source_count > 1 else 0
        time_consistency = 1.0 if time_spread_hours <= 24 else 0.5
        confidence = min(1.0, round(0.35 + 0.2 * source_count + 0.2 * source_diversity + 0.25 * time_consistency, 3))
        embedding = average([self.embedder.embed(f"{a.title} {a.description}") for a in cluster])
        event_id = sha1("|".join(sorted(a.link for a in cluster)).encode("utf-8")).hexdigest()[:16]
        event = Event(
            event_id=event_id,
            slug=make_slug(self._build_event_title(cluster, primary.category, primary.city, primary.country)),
            title=self._build_event_title(cluster, primary.category, primary.city, primary.country),
            category=primary.category,
            country=primary.country,
            city=primary.city,
            occurred_at=primary.published_at,
            confidence=confidence,
            source_diversity=source_diversity,
            source_count=source_count,
            embedding=embedding,
            source_links=[SourceLink(a.source_name, a.link, a.published_at) for a in cluster],
            summary={},
            status="Developing",
            bias_indicator="unknown",
        )
        summary = self.summary_service.summarize(event)
        event.summary = {
            "what_happened": summary["what_happened"],
            "where_when": summary["where_when"],
            "why_it_matters": summary["why_it_matters"],
            "what_next": summary["what_next"],
        }
        event.status = summary["status"]
        event.bias_indicator = summary["bias_indicator"]
        return event

    @staticmethod
    def _build_event_title(cluster: list[RawArticle], category: str, city: str, country: str) -> str:
        """Generate a neutral event title without copying a source headline verbatim."""

        source_count = len(cluster)
        return f"{category.title()} event update from {city}, {country} ({source_count} sources)"


def build_ingestion_service(repository: EventRepository) -> IngestionService:
    return IngestionService(
        repository=repository,
        fetcher=RSSFetcher(),
        summary_service=SummaryService(),
        embedder=DeterministicEmbedder(settings.embedding_dimensions),
    )
