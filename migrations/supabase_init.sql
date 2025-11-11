-- Создание таблицы health_app
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

-- Создание индекса для быстрого поиска по tgid
CREATE INDEX IF NOT EXISTS idx_health_app_tgid ON health_app(tgid);

-- Функция для автоматического обновления updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Триггер для автоматического обновления updated_at при изменении записи
DROP TRIGGER IF EXISTS update_health_app_updated_at ON health_app;
CREATE TRIGGER update_health_app_updated_at
    BEFORE UPDATE ON health_app
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

