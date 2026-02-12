from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from ai_news_publisher.domain.models import Event
from ai_news_publisher.monitoring import monitoring_store


class AIClient(Protocol):
    def summarize_event(self, event: Event) -> dict[str, str]: ...


@dataclass
class TemplateAIClient:
    model_name: str = "template-v1"

    def summarize_event(self, event: Event) -> dict[str, str]:
        headline = f"{event.source_count} sources report related developments in {event.category}."
        return {
            "what_happened": headline,
            "where_when": f"Reported around {event.city}, {event.country} at {event.occurred_at.isoformat()}.",
            "why_it_matters": "This may influence policy, business decisions, and local planning.",
            "what_next": "Expect updates as additional sources confirm details.",
            "status": "Confirmed" if event.confidence >= 0.65 else "Developing",
            "bias_indicator": "medium" if event.source_diversity < 2 else "low",
        }


class SummaryService:
    def __init__(self, client: AIClient | None = None) -> None:
        self.client = client or TemplateAIClient()
        self._cache: dict[str, dict[str, str]] = {}

    @staticmethod
    def _estimate_tokens(summary: dict[str, str]) -> tuple[int, int]:
        prompt_tokens = 120
        completion_tokens = max(40, sum(len(v.split()) for v in summary.values()))
        return prompt_tokens, completion_tokens

    @staticmethod
    def _estimate_cost_usd(prompt_tokens: int, completion_tokens: int) -> float:
        # Lightweight estimate tuned for low-cost LLM routing policies.
        return round(prompt_tokens * 0.0000002 + completion_tokens * 0.0000006, 6)

    def summarize(self, event: Event) -> dict[str, str]:
        if event.event_id in self._cache:
            return self._cache[event.event_id]

        payload = self.client.summarize_event(event)
        required = {"what_happened", "where_when", "why_it_matters", "what_next", "status", "bias_indicator"}
        missing = required - set(payload)
        if missing:
            raise ValueError(f"Summary payload missing fields: {sorted(missing)}")

        prompt_tokens, completion_tokens = self._estimate_tokens(payload)
        monitoring_store.record_ai_call(
            provider="internal-template",
            model=getattr(self.client, "model_name", "unknown"),
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            estimated_cost_usd=self._estimate_cost_usd(prompt_tokens, completion_tokens),
        )

        self._cache[event.event_id] = payload
        return payload
