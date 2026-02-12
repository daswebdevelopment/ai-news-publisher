from __future__ import annotations

from dataclasses import dataclass

from ai_news_publisher.domain.models import Event


@dataclass(frozen=True)
class Location:
    country: str
    state: str | None = None
    city: str | None = None


class LocalizationService:
    def __init__(self) -> None:
        self._cache: dict[str, str] = {}

    def local_impact(self, event: Event, location: Location) -> str:
        cache_key = f"{event.event_id}:{location.country}:{location.state}:{location.city}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        is_relevant = location.country.lower() == event.country.lower() or (
            location.city and location.city.lower() == event.city.lower()
        )
        if not is_relevant:
            text = "No direct local impact identified at this time."
        else:
            locality = ", ".join(part for part in [location.city, location.state, location.country] if part)
            text = f"Why this matters to YOU: Expected spillover effects for residents and organizations in {locality}."
        self._cache[cache_key] = text
        return text
