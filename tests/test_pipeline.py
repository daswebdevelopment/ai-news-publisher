from datetime import date

import pytest

from ai_news_publisher.pipeline import generate_markdown_digest, normalize_items


def test_normalize_items_deduplicates_by_keeping_newest_and_sorts_descending() -> None:
    raw = [
        {
            "title": "Older story",
            "source": "Source A",
            "url": "https://example.com/1",
            "summary": "Summary 1",
            "published_at": "2026-01-01T09:00:00+00:00",
            "category": "research",
        },
        {
            "title": "Newest story",
            "source": "Source B",
            "url": "https://example.com/2",
            "summary": "Summary 2",
            "published_at": "2026-01-02T09:00:00+00:00",
            "category": "product",
        },
        {
            "title": "Updated duplicate should be kept",
            "source": "Source C",
            "url": "https://example.com/2",
            "summary": "Summary duplicate",
            "published_at": "2026-01-03T09:00:00+00:00",
            "category": "product",
        },
    ]

    items = normalize_items(raw)

    assert [item.url for item in items] == ["https://example.com/2", "https://example.com/1"]
    assert [item.title for item in items] == ["Updated duplicate should be kept", "Older story"]


def test_normalize_items_requires_fields() -> None:
    with pytest.raises(ValueError, match="Missing required field: title"):
        normalize_items([
            {
                "source": "Nowhere",
                "url": "https://example.com/missing-title",
                "summary": "Summary",
                "published_at": "2026-01-01T00:00:00Z",
            }
        ])


def test_normalize_items_rejects_whitespace_only_required_text() -> None:
    with pytest.raises(ValueError, match="Field 'title' must be a non-empty string"):
        normalize_items([
            {
                "title": "   ",
                "source": "Nowhere",
                "url": "https://example.com/blank-title",
                "summary": "Summary",
                "published_at": "2026-01-01T00:00:00Z",
            }
        ])


def test_normalize_items_rejects_invalid_url() -> None:
    with pytest.raises(ValueError, match=r"valid absolute HTTP\(S\) URL"):
        normalize_items([
            {
                "title": "Bad url",
                "source": "Nowhere",
                "url": "example.com/no-scheme",
                "summary": "Summary",
                "published_at": "2026-01-01T00:00:00Z",
            }
        ])


def test_normalize_items_rejects_invalid_datetime() -> None:
    with pytest.raises(ValueError, match="published_at"):
        normalize_items([
            {
                "title": "Bad date",
                "source": "Nowhere",
                "url": "https://example.com/bad-date",
                "summary": "Oops",
                "published_at": "not-a-date",
            }
        ])


def test_normalize_items_accepts_mixed_naive_and_aware_datetimes() -> None:
    items = normalize_items(
        [
            {
                "title": "Naive",
                "source": "Source A",
                "url": "https://example.com/naive",
                "summary": "No timezone provided",
                "published_at": "2026-01-01T10:00:00",
            },
            {
                "title": "Aware",
                "source": "Source B",
                "url": "https://example.com/aware",
                "summary": "UTC timestamp",
                "published_at": "2026-01-01T09:30:00+00:00",
            },
        ]
    )

    assert [item.title for item in items] == ["Naive", "Aware"]


def test_normalize_items_rejects_non_object_entries() -> None:
    with pytest.raises(ValueError, match="object/dictionary"):
        normalize_items(["not-an-object"])


def test_generate_markdown_digest_groups_by_category() -> None:
    items = normalize_items(
        [
            {
                "title": "Research update",
                "source": "Lab",
                "url": "https://example.com/research",
                "summary": "New benchmark",
                "published_at": "2026-01-01T09:00:00+00:00",
                "category": "research",
            },
            {
                "title": "Product launch",
                "source": "Vendor",
                "url": "https://example.com/product",
                "summary": "New assistant feature",
                "published_at": "2026-01-02T10:00:00+00:00",
                "category": "product",
            },
        ]
    )

    digest = generate_markdown_digest(items, digest_date=date(2026, 1, 5))

    assert "# AI News Digest - 2026-01-05" in digest
    assert "## Product" in digest
    assert "## Research" in digest
    assert "[Product launch](https://example.com/product)" in digest
