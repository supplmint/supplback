# Health App - Backend & Frontend

Полнофункциональное приложение для управления здоровьем с интеграцией Telegram WebApp.

## Структура проекта

- `backend/` - Node.js + Express + PostgreSQL бэкенд
- `frontend/` - React + TypeScript фронтенд

## Backend

Смотрите [backend/README.md](./backend/README.md) для деталей.

### Быстрый старт

```bash
cd backend
npm install
cp .env.example .env
# Настройте переменные окружения в .env
npm run migrate
npm run dev
```

## Frontend

Смотрите [frontend/README.md](./frontend/README.md) для деталей.

### Быстрый старт

```bash
cd frontend
npm install
cp .env.example .env
# Настройте VITE_API_BASE_URL в .env
npm run dev
```

## Технологии

### Backend
- Node.js + Express
- PostgreSQL
- TypeScript
- Telegram WebApp Authentication (HMAC-SHA256)

### Frontend
- React 18
- TypeScript
- Vite
- Telegram WebApp SDK

## Развёртывание

### Backend
Развёртывается на Render или другом Node.js хостинге.

### Frontend
Развёртывается на Firebase Hosting.

## Лицензия

ISC

