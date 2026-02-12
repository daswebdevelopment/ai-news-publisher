from ai_news_publisher.monitoring import MonitoringStore


def test_monitoring_store_tracks_ai_calls_and_costs():
    store = MonitoringStore(cost_spike_multiplier=2.0, recent_window=5)

    for _ in range(6):
        store.record_ai_call(
            provider="test",
            model="m1",
            prompt_tokens=100,
            completion_tokens=50,
            estimated_cost_usd=0.001,
        )

    snapshot = store.snapshot()
    assert snapshot["ai_calls"] == 6
    assert snapshot["total_tokens"] == 900
    assert snapshot["total_estimated_cost_usd"] == 0.006


def test_monitoring_store_alerts_on_cost_spike():
    store = MonitoringStore(cost_spike_multiplier=2.0, recent_window=5)

    for _ in range(5):
        store.record_ai_call(
            provider="test",
            model="m1",
            prompt_tokens=100,
            completion_tokens=50,
            estimated_cost_usd=0.001,
        )

    store.record_ai_call(
        provider="test",
        model="m1",
        prompt_tokens=100,
        completion_tokens=50,
        estimated_cost_usd=0.003,
    )

    snapshot = store.snapshot()
    assert snapshot["alerts"]
    assert "Cost spike detected" in snapshot["alerts"][0]


def test_monitoring_store_tracks_failures():
    store = MonitoringStore()
    store.record_ingestion_failure("rss timeout")
    store.record_publishing_failure("digest failed")

    snapshot = store.snapshot()
    assert snapshot["ingestion_failures"] == 1
    assert snapshot["publishing_failures"] == 1
