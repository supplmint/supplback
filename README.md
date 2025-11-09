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

### Переменные окружения

Создайте файл `.env` с следующими переменными:

```env
# Server
NODE_ENV=production
PORT=3000

# Telegram Bot Token
BOT_TOKEN=your_bot_token_here

# Database (Supabase) - способ 1: Connection string (РЕКОМЕНДУЕТСЯ)
# Скопируйте из Supabase: Settings > Database > Connection string > Connection pooling
DATABASE_URL=postgresql://postgres.xxxxx:[PASSWORD]@aws-0-us-east-1.pooler.supabase.com:5432/postgres

# Database (Supabase) - способ 2: Отдельные параметры (альтернатива)
# PGHOST=db.xxxxx.supabase.co
# PGPORT=5432
# PGDATABASE=postgres
# PGUSER=postgres.xxxxx
# PGPASSWORD=your_password
```

**Как получить DATABASE_URL из Supabase:**
1. Откройте проект в Supabase
2. Перейдите в **Settings** > **Database**
3. Найдите секцию **Connection string**
4. Выберите **Connection pooling** (рекомендуется) или **Direct connection**
5. Скопируйте строку подключения и вставьте в `DATABASE_URL`
6. Замените `[YOUR-PASSWORD]` на ваш пароль базы данных

### API Endpoints

- `GET /health` - проверка здоровья сервера (не требует аутентификации)
- `GET /api/me` - получить/создать пользователя (требует аутентификацию)
- `POST /api/me` - обновить профиль (требует аутентификацию)
- `POST /api/analyses/summary` - обновить анализы (требует аутентификацию)
- `POST /api/reco/basic` - обновить рекомендации (требует аутентификацию)
- `POST /api/notify-upload` - уведомить о загрузке файла (требует аутентификацию)

### Развёртывание на Render.com

1. Подключите репозиторий к Render.com
2. Выберите тип сервиса: **Web Service**
3. Настройки:
   - **Runtime**: Python 3
   - **Build Command**: `pip install --upgrade pip && pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Установите переменные окружения в панели Render:
   - `NODE_ENV=production`
   - `BOT_TOKEN` - токен вашего Telegram бота
   - `DATABASE_URL` - connection string из Supabase (см. инструкцию выше)
     - Или используйте отдельные параметры: `PGHOST`, `PGPORT`, `PGDATABASE`, `PGUSER`, `PGPASSWORD`
5. `PORT` устанавливается автоматически Render.com

### Настройка базы данных (Supabase)

Выполните SQL из `migrations/supabase_init.sql` в Supabase SQL Editor для создания таблицы `health_app`.

## Технологии

- Python 3.11+
- FastAPI
- PostgreSQL (Supabase)
- SQLAlchemy
- Telegram WebApp Authentication (HMAC-SHA256)

## Лицензия

ISC
