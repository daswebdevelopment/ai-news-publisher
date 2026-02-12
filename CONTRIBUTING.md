# Contributing Guide

## Project layout
- `src/ai_news_publisher/api`: FastAPI read-only publishing API.
- `src/ai_news_publisher/services`: ingestion, summarization, localization, publishing logic.
- `src/ai_news_publisher/infrastructure`: RSS fetchers, embeddings, repositories.
- `src/ai_news_publisher/domain`: domain models.
- `src/ai_news_publisher/db`: PostgreSQL + pgvector schema.
- `frontend/`: minimal Next.js frontend.
- `tests/`: unit tests.

## Coding standards
- Python: type hints required, small pure functions, idempotent service methods.
- FastAPI: read-only public endpoints must include caching headers.
- Next.js: mobile-first components, SSR-friendly data paths.
- Never store raw scraped article text. Persist only metadata, source links, embeddings, AI summaries.
- Never copy headlines verbatim in generated summaries.

## Testing requirements
- Add unit tests for any service or endpoint logic changes.
- Run `pytest` locally before opening PR.

## Commit format
Use conventional commits:
- `feat: ...`
- `fix: ...`
- `test: ...`
- `docs: ...`

## Security and privacy
- Keep API keys in env variables (`OPENAI_API_KEY`, `DATABASE_URL`).
- Do not commit secrets.
- Public APIs must remain read-only.

## AI agent behavior
- Implement complete code, no TODO placeholders.
- Keep modules decoupled and reusable.
- Ensure deterministic, idempotent behavior where possible.
