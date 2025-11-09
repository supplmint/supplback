# Health App Backend

Backend для Health App с аутентификацией через Telegram WebApp.

## Технологии

- Node.js + Express
- PostgreSQL
- TypeScript
- Telegram WebApp Authentication (HMAC-SHA256)

## Установка

1. Установите зависимости:
```bash
npm install
```

2. Создайте файл `.env` на основе `.env.example`:
```bash
cp .env.example .env
```

3. Заполните переменные окружения в `.env`:
- `BOT_TOKEN` - токен Telegram бота
- `PGHOST`, `PGPORT`, `PGDATABASE`, `PGUSER`, `PGPASSWORD` - параметры подключения к PostgreSQL

4. Выполните миграцию базы данных:
```bash
npm run migrate
```

Или вручную:
```bash
psql "postgres://user:pass@host:port/db" -f db/migrate.sql
```

## Запуск

Разработка:
```bash
npm run dev
```

Сборка:
```bash
npm run build
```

Продакшн:
```bash
npm start
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

