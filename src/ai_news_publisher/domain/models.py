from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from hashlib import sha1
from typing import Iterable


@dataclass(frozen=True)
class SourceLink:
    source_name: str
    url: str
    published_at: datetime


@dataclass
class Event:
    event_id: str
    slug: str
    title: str
    category: str
    country: str
    city: str
    occurred_at: datetime
    confidence: float
    source_diversity: int
    source_count: int
    embedding: list[float]
    source_links: list[SourceLink]
    summary: dict[str, str]
    status: str
    bias_indicator: str
    ai_generated_notice: str = "AI-generated summary. Source links provided for verification."


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def make_slug(title: str) -> str:
    base = "-".join(title.lower().split())[:60].strip("-")
    suffix = sha1(title.encode("utf-8")).hexdigest()[:8]
    return f"{base}-{suffix}"


def average(vectors: Iterable[list[float]]) -> list[float]:
    items = list(vectors)
    if not items:
        return []
    dim = len(items[0])
    sums = [0.0] * dim
    for vector in items:
        for i, value in enumerate(vector):
            sums[i] += value
    return [value / len(items) for value in sums]
