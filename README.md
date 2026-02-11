# AI News Publisher

`ai-news-publisher` provides a small, runnable pipeline to normalize AI news items and generate a publish-ready markdown digest.

## What is implemented

- Input validation for required text fields, URL format, and timestamp format.
- Timestamp normalization to UTC (naive timestamps are treated as UTC).
- Story normalization into a typed model.
- URL de-duplication (most recently published duplicate wins).
- Reverse-chronological sorting.
- Markdown digest generation grouped by category.
- CLI command to transform JSON input into a digest file with clear validation errors.

## Quick Start

### 1) Create and activate a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
```

### 2) Install the package in editable mode

```bash
pip install -e .
```

### 3) Create an input file

Example `sample_news.json`:

```json
[
  {
    "title": "New model release",
    "source": "Example AI Blog",
    "url": "https://example.com/model-release",
    "summary": "A new family of models was announced.",
    "published_at": "2026-01-20T10:30:00+00:00",
    "category": "product"
  },
  {
    "title": "Benchmark update",
    "source": "Research Weekly",
    "url": "https://example.com/benchmark-update",
    "summary": "Researchers published a new evaluation result.",
    "published_at": "2026-01-19T14:00:00+00:00",
    "category": "research"
  }
]
```

### 4) Generate a digest

```bash
ai-news-publisher sample_news.json --output digest.md
```

The command prints a summary and writes the formatted digest to `digest.md`.

## Development

Run tests:

```bash
pytest
```

## License

This project is licensed under the terms in [LICENSE](LICENSE).
