-- Добавление колонки rekom в таблицу health_app
ALTER TABLE health_app 
ADD COLUMN IF NOT EXISTS rekom JSONB DEFAULT '{}'::jsonb;

