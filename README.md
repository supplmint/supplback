# Health App - Backend & Frontend

Полнофункциональное приложение для управления здоровьем с интеграцией Telegram WebApp.

## Структура проекта

- `app/` - Python (FastAPI) бэкенд
- `frontend/` - React + TypeScript фронтенд
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

## Frontend (React + TypeScript + Vite)

### Быстрый старт

```bash
cd frontend
npm install
cp .env.example .env
# Настройте VITE_API_BASE_URL в .env
npm run dev
```

### Развёртывание на Firebase Hosting

```bash
# Установите Firebase CLI
npm install -g firebase-tools

# Войдите в Firebase
firebase login

# Соберите проект
cd frontend
npm run build

# Деплой
cd ..
firebase deploy --only hosting
```

Или используйте скрипт:
```bash
cd frontend
npm run deploy
```

## Технологии

### Backend
- Python 3.11+
- FastAPI
- PostgreSQL (Supabase)
- SQLAlchemy
- Telegram WebApp Authentication (HMAC-SHA256)

### Frontend
- React 18
- TypeScript
- Vite
- Firebase (Storage, Hosting)
- Telegram WebApp SDK

## Лицензия

ISC
