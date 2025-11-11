CREATE TABLE IF NOT EXISTS health_app (
  id BIGSERIAL PRIMARY KEY,
  tgid TEXT UNIQUE NOT NULL,
  profile JSONB DEFAULT '{}'::jsonb,
  analyses JSONB DEFAULT '{}'::jsonb,
  recommendations JSONB DEFAULT '{}'::jsonb,
  allanalize JSONB DEFAULT '{}'::jsonb,
  rekom JSONB DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_health_app_tgid ON health_app(tgid);

