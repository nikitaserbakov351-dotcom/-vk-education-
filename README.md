# Веб-мессенджер на FastAPI

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688?logo=fastapi&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0%20async-D71F00)
![WebSockets](https://img.shields.io/badge/WebSockets-realtime-4A154B)
![Tests](https://github.com/nikitaserbakov351-dotcom/-vk-education-/actions/workflows/tests.yml/badge.svg)

Учебный проект, выполненный в рамках образовательной программы VK: веб-мессенджер с доставкой сообщений в реальном времени, JWT-авторизацией WebSocket-соединений и хранением истории в асинхронной базе данных.

## Ключевые возможности

- **Обмен сообщениями в реальном времени** — двунаправленный канал на WebSockets: сообщения и системные события доставляются всем участникам без перезагрузки страницы.
- **JWT-авторизация WebSocket** — соединение устанавливается только с одноразовым токеном, полученным через REST-эндпоинт `/login`; недействительный токен отклоняется с кодом 1008.
- **История сообщений** — вся переписка сохраняется в SQLite и отдаётся новым участникам при входе.
- **Адаптивный интерфейс** — Tailwind CSS, эффект glassmorphism, ванильный JS без фреймворков.
- **Автотесты и CI** — pytest-покрытие REST-эндпоинтов, JWT-авторизации и WebSocket-канала (включая отклонение недействительных токенов); GitHub Actions запускается на каждый push.
- **Автозапуск в один клик** — при ручном запуске сервер поднимается на порту 8080 и сам открывает интерфейс в браузере.

## Технологический стек

| Слой | Технологии |
|---|---|
| Бэкенд | Python 3.10+, FastAPI, Uvicorn |
| База данных | SQLAlchemy 2.0 (async), aiosqlite, SQLite |
| Реальное время | WebSockets, PyJWT (HS256) |
| Фронтенд | HTML5, Tailwind CSS, ванильный JavaScript |

## Быстрый старт

```bash
git clone https://github.com/nikitaserbakov351-dotcom/-vk-education-.git
cd -vk-education-

python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt

python main.py                   # сервер: http://127.0.0.1:8080
```

Для запуска тестов:

```bash
pip install -r requirements-dev.txt
pytest -v
```

Опционально задайте переменную окружения `SECRET_KEY` — ключ подписи JWT. По умолчанию используется development-значение.

## Особенности реализации

**Асинхронный доступ к БД.** Все операции записи и чтения истории вынесены в изолированные асинхронные сессии (SQLAlchemy + aiosqlite). Это исключает ошибку `database is locked` при одновременной отправке сообщений от нескольких пользователей.

**Жизненный цикл приложения.** Создание таблиц и автозапуск браузера вынесены в lifespan-обработчик FastAPI — современная альтернатива устаревшим событиям `on_event`.

**Разделение ответственности.** Логика соединений изолирована в классе `ConnectionManager` (подключение, отключение, рассылка), модели данных — в SQLAlchemy-моделях, маршруты — в `main.py`.

## Структура проекта

```
├── main.py                    # маршруты REST/WebSocket, lifespan, точка входа
├── database.py                # async-движок и фабрика сессий SQLAlchemy
├── models.py                  # ORM-модели: User, Message
├── ws_manager.py              # менеджер WebSocket-соединений и рассылки
├── index.html                 # одностраничный интерфейс мессенджера
├── conftest.py                # тестовая конфигурация (БД, ключ подписи)
├── test_messenger.py          # pytest: REST, JWT, WebSocket
├── .github/workflows/tests.yml
└── requirements.txt           # зависимости (+ requirements-dev.txt для тестов)
```

## Развитие проекта

- [ ] Личные сообщения и несколько чатов (сейчас поле `chat_id` уже заложено в модель)
- [ ] Регистрация с паролем и refresh-токены
- [ ] Индикаторы «онлайн» и «печатает»
- [ ] Dockerfile для воспроизводимого деплоя

## Автор

Проект подготовлен **Щербаков Никита Олегович** ([@TheSheinAir](https://github.com/TheSheinAir)) — другие работы смотрите в [профиле GitHub](https://github.com/TheSheinAir?tab=repositories).
