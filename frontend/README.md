# Health App Frontend

Фронтенд приложение для Health App, интегрированное с Telegram WebApp.

## Технологии

- React 18
- TypeScript
- Vite
- React Router
- Axios
- Telegram WebApp SDK

## Установка

1. Установите зависимости:
```bash
npm install
```

2. Создайте файл `.env` на основе `.env.example`:
```bash
cp .env.example .env
```

3. Настройте переменные окружения:
- `VITE_API_BASE_URL` - URL бэкенда (по умолчанию: http://localhost:3000)

## Запуск

Разработка:
```bash
npm run dev
```

Сборка для продакшена:
```bash
npm run build
```

Превью продакшен сборки:
```bash
npm run preview
```

## Развёртывание на Firebase Hosting

1. Соберите проект:
```bash
npm run build
```

2. Установите Firebase CLI:
```bash
npm install -g firebase-tools
```

3. Инициализируйте Firebase:
```bash
firebase init hosting
```

4. Укажите `dist` как директорию для публикации

5. Деплой:
```bash
firebase deploy --only hosting
```

## Структура проекта

```
src/
├── api/              # API клиенты
├── pages/            # Страницы приложения
├── utils/            # Утилиты (Telegram интеграция)
├── types/            # TypeScript типы
├── App.tsx           # Главный компонент
└── main.tsx          # Точка входа
```

## Интеграция с Telegram

Приложение автоматически:
- Инициализирует Telegram WebApp при загрузке
- Добавляет заголовок `x-telegram-initdata` ко всем запросам к API
- Использует тему Telegram для стилизации

## API Endpoints

Все запросы автоматически включают заголовок `x-telegram-initdata` для аутентификации.

- `GET /health` - проверка здоровья бэкенда
- `GET /api/me` - получить профиль пользователя
- `POST /api/me` - обновить профиль
- `POST /api/analyses/summary` - обновить анализы
- `POST /api/reco/basic` - обновить рекомендации
- `POST /api/notify-upload` - уведомить о загрузке файла

