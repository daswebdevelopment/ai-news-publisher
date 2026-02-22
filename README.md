# AI News Publisher

Automated event-based news publishing system with Python/FastAPI backend and minimal Next.js frontend.

## What this project does
- Ingests RSS feeds asynchronously.
- Clusters similar stories into normalized **events** using embeddings.
- Stores only event metadata, source links, embeddings, and AI-generated summaries.
- Exposes read-only publishing APIs with filters and localization impact.
- Generates automated daily email digests with topic grouping and configurable length.
- Generates SEO metadata and structured JSON-LD for event pages.
- Adds lightweight monitoring for AI usage, cost spikes, and failure counters.

## Architecture
- Backend: FastAPI (`src/ai_news_publisher/api`)
- Event pipeline: `services/ingestion.py`, `services/summarization.py`, `services/localization.py`
- Database schema: `src/ai_news_publisher/db/schema.sql` (PostgreSQL + pgvector)
- Frontend: Next.js (`frontend/`)

## Quick start
### Python backend
```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
uvicorn ai_news_publisher.main:app --reload
```

### Run tests
```bash
pytest
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

## Environment variables
- `DATABASE_URL`: PostgreSQL DSN
- `OPENAI_API_KEY`: optional if replacing template summarizer with OpenAI client
- `PUBLISHER_BASE_URL`: canonical URL host for SEO tags
- `EMBEDDING_DIMENSIONS`: embedding vector size (default 16)
- `DIGEST_MAX_EVENTS`: max events to include in a daily digest
- `SMTP_HOST`, `SMTP_PORT`, `SMTP_USERNAME`, `SMTP_PASSWORD`: SMTP provider settings
- `DIGEST_SENDER_EMAIL`: sender identity for digest emails
- `AI_COST_SPIKE_MULTIPLIER`: alert threshold multiplier vs rolling average cost
- `AI_COST_WINDOW`: rolling window size for cost-spike checks

## API overview
- `GET /health`
- `GET /api/events?category=&country=&city=`
- `GET /api/events/{slug}`
- `GET /api/events/{slug}/local-impact?country=&state=&city=`
- `POST /api/digest/send?recipient=&max_events=&category=&country=&city=`
- `GET /health/detailed`
- `GET /api/monitoring`

All payloads include `ai_generated_notice` and do not expose raw scraped text.
