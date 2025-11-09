# Health App - Backend

Backend приложения для управления здоровьем с интеграцией Telegram WebApp.

## Технологии

- Node.js + Express
- PostgreSQL
- TypeScript
- Telegram WebApp Authentication (HMAC-SHA256)

## Быстрый старт

```bash
npm install
cp .env.example .env
# Настройте переменные окружения в .env
npm run migrate
npm run dev
```

## API Endpoints

### GET /health
Проверка здоровья сервера.

### GET /api/me (требует аутентификацию)
Получить или создать пользователя. Возвращает `tgid` и `profile`.

### POST /api/me (требует аутентификацию)
Обновить профиль пользователя. Принимает `{ profile: {...} }`.

### POST /api/analyses/summary (требует аутентификацию)
Обновить анализы пользователя. Принимает `{ analyses: {...} }`.

### POST /api/reco/basic (требует аутентификацию)
Обновить рекомендации пользователя. Принимает `{ recommendations: {...} }`.

### POST /api/notify-upload (требует аутентификацию)
Уведомить о загрузке файла. Принимает `{ fileName: string, mime: string, size: number }`.

## Аутентификация

Все защищённые маршруты требуют заголовок `x-telegram-initdata` с данными инициализации Telegram WebApp.

Сервер проверяет подпись данных используя HMAC-SHA256 алгоритм и извлекает `tgid` из поля `user.id`.

## База данных

Таблица `health_app` хранит:
- `tgid` - уникальный идентификатор Telegram пользователя
- `profile` - JSONB с данными профиля
- `analyses` - JSONB с анализами
- `recommendations` - JSONB с рекомендациями
- `created_at`, `updated_at` - временные метки

## Развёртывание

Развёртывается на Render или другом Node.js хостинге.

## Лицензия

ISC
