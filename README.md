# Health App - Backend

Backend приложения для управления здоровьем с интеграцией Telegram WebApp.

## Структура проекта

- `app/` - Python (FastAPI) бэкенд
- `migrations/` - SQL миграции для базы данных

## Backend (Python + FastAPI)

### Быстрый старт

```bash
# Установка зависимостей
pip install -r requirements.txt

# Настройка переменных окружения
cp .env.example .env
# Заполните переменные в .env

# Запуск
uvicorn app.main:app --host 0.0.0.0 --port 3000
```

### API Endpoints

- `GET /health` - проверка здоровья сервера
- `GET /api/me` - получить/создать пользователя (требует аутентификацию)
- `POST /api/me` - обновить профиль (требует аутентификацию)
- `POST /api/analyses/summary` - обновить анализы (требует аутентификацию)
- `POST /api/reco/basic` - обновить рекомендации (требует аутентификацию)
- `POST /api/notify-upload` - уведомить о загрузке файла (требует аутентификацию)

### Развёртывание на Render

Развёртывается на Render.com с Python runtime.

## Технологии

- Python 3.11+
- FastAPI
- PostgreSQL (Supabase)
- SQLAlchemy
- Telegram WebApp Authentication (HMAC-SHA256)

## Лицензия

ISC
