from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass
from datetime import datetime, timezone
import logging
import os
from threading import Lock

logger = logging.getLogger("ai_news_publisher")
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s %(levelname)s %(name)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
logger.setLevel(logging.INFO)


@dataclass(frozen=True)
class AICallRecord:
    provider: str
    model: str
    prompt_tokens: int
    completion_tokens: int
    estimated_cost_usd: float
    timestamp: datetime


class MonitoringStore:
    """In-memory lightweight observability store for logs, counters, and AI cost."""

    def __init__(self, cost_spike_multiplier: float | None = None, recent_window: int | None = None) -> None:
        self._lock = Lock()
        self._ai_calls: deque[AICallRecord] = deque(maxlen=1000)
        self._ingestion_failures = 0
        self._publishing_failures = 0
        self._alerts: deque[str] = deque(maxlen=200)
        self._cost_spike_multiplier = cost_spike_multiplier or float(os.getenv("AI_COST_SPIKE_MULTIPLIER", "2.0"))
        resolved_window = recent_window or int(os.getenv("AI_COST_WINDOW", "50"))
        self._recent_window = max(5, resolved_window)
        self._event_counters: dict[str, int] = defaultdict(int)

    def record_ai_call(
        self,
        provider: str,
        model: str,
        prompt_tokens: int,
        completion_tokens: int,
        estimated_cost_usd: float,
    ) -> None:
        with self._lock:
            record = AICallRecord(
                provider=provider,
                model=model,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                estimated_cost_usd=estimated_cost_usd,
                timestamp=datetime.now(timezone.utc),
            )
            self._ai_calls.append(record)
            self._event_counters["ai_calls"] += 1
            self._check_cost_spike_unlocked(record)

        logger.info(
            "AI call provider=%s model=%s prompt_tokens=%d completion_tokens=%d estimated_cost_usd=%.6f",
            provider,
            model,
            prompt_tokens,
            completion_tokens,
            estimated_cost_usd,
        )

    def _check_cost_spike_unlocked(self, latest: AICallRecord) -> None:
        recent = list(self._ai_calls)[-self._recent_window :]
        if len(recent) < 5:
            return

        baseline = sum(r.estimated_cost_usd for r in recent[:-1]) / max(len(recent) - 1, 1)
        if baseline <= 0:
            return

        if latest.estimated_cost_usd >= baseline * self._cost_spike_multiplier:
            message = (
                f"Cost spike detected: latest={latest.estimated_cost_usd:.6f} "
                f"baseline={baseline:.6f} model={latest.model}"
            )
            self._alerts.append(message)
            self._event_counters["alerts"] += 1
            logger.warning(message)

    def record_ingestion_failure(self, reason: str) -> None:
        with self._lock:
            self._ingestion_failures += 1
            self._event_counters["ingestion_failures"] += 1
        logger.error("Ingestion failure: %s", reason)

    def record_publishing_failure(self, reason: str) -> None:
        with self._lock:
            self._publishing_failures += 1
            self._event_counters["publishing_failures"] += 1
        logger.error("Publishing failure: %s", reason)

    def snapshot(self) -> dict[str, object]:
        with self._lock:
            total_tokens = sum(r.prompt_tokens + r.completion_tokens for r in self._ai_calls)
            total_cost = sum(r.estimated_cost_usd for r in self._ai_calls)
            return {
                "ai_calls": len(self._ai_calls),
                "total_tokens": total_tokens,
                "total_estimated_cost_usd": round(total_cost, 6),
                "ingestion_failures": self._ingestion_failures,
                "publishing_failures": self._publishing_failures,
                "alerts": list(self._alerts),
                "event_counters": dict(self._event_counters),
                "last_updated": datetime.now(timezone.utc).isoformat(),
            }


monitoring_store = MonitoringStore()
