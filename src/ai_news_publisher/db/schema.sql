CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS events (
  event_id TEXT PRIMARY KEY,
  slug TEXT UNIQUE NOT NULL,
  title TEXT NOT NULL,
  category TEXT NOT NULL,
  country TEXT NOT NULL,
  city TEXT NOT NULL,
  occurred_at TIMESTAMPTZ NOT NULL,
  confidence DOUBLE PRECISION NOT NULL,
  source_diversity INT NOT NULL,
  source_count INT NOT NULL,
  summary JSONB NOT NULL,
  status TEXT NOT NULL,
  bias_indicator TEXT NOT NULL,
  ai_generated_notice TEXT NOT NULL,
  embedding VECTOR(16) NOT NULL,
  source_links JSONB NOT NULL
);

CREATE INDEX IF NOT EXISTS events_embedding_idx ON events USING ivfflat (embedding vector_cosine_ops);
CREATE INDEX IF NOT EXISTS events_filters_idx ON events (category, country, city);
