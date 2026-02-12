from __future__ import annotations

import asyncio
from dataclasses import dataclass
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from typing import Any
from urllib.request import urlopen
import xml.etree.ElementTree as ET


@dataclass(frozen=True)
class RawArticle:
    source_name: str
    title: str
    link: str
    description: str
    published_at: datetime
    country: str
    city: str
    category: str


class RSSFetcher:
    async def fetch_many(self, feeds: list[dict[str, str]]) -> list[RawArticle]:
        tasks = [self._fetch(feed) for feed in feeds]
        nested = await asyncio.gather(*tasks)
        return [item for group in nested for item in group]

    async def _fetch(self, feed: dict[str, str]) -> list[RawArticle]:
        xml_text = await asyncio.to_thread(self._load_feed, feed["url"])
        return self._parse_feed(xml_text, feed)

    def _load_feed(self, url: str) -> str:
        with urlopen(url, timeout=10) as response:  # nosec B310
            return response.read().decode("utf-8", errors="ignore")

    def _parse_feed(self, xml_text: str, feed: dict[str, str]) -> list[RawArticle]:
        root = ET.fromstring(xml_text)
        articles: list[RawArticle] = []
        for item in root.findall(".//item"):
            title = (item.findtext("title") or "").strip()
            link = (item.findtext("link") or "").strip()
            description = (item.findtext("description") or "").strip()
            pub_date = (item.findtext("pubDate") or "").strip()
            if not title or not link:
                continue
            published = _parse_date(pub_date)
            articles.append(
                RawArticle(
                    source_name=feed.get("source_name", "unknown"),
                    title=title,
                    link=link,
                    description=description,
                    published_at=published,
                    country=feed.get("country", "global"),
                    city=feed.get("city", "global"),
                    category=feed.get("category", "general"),
                )
            )
        return articles


def _parse_date(value: str) -> datetime:
    if not value:
        return datetime.now(timezone.utc)
    try:
        parsed = parsedate_to_datetime(value)
    except (TypeError, ValueError):
        return datetime.now(timezone.utc)
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)
