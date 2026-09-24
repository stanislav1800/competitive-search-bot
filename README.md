# Бот для поиска материалов
Telegram-бот для поиска интересующих материалов в разных источниках при помощи API разных сервисов. В данный момент реализован сбор данных с таких источников как: Wikipedia, GitHub, StackOverflow

## Функционал
По команде /search пользователь присылает запрос (информация которая его интересует), дальше бот одновременно ищет в трёх источниках и присылает объединённый результат

## Технологии
В данном проекте используется
- aiogram 3
- aiohttp
- aiolimiter
- python-dotenv

## Архитектура
цепочка Telegram → Handler → SearchService → провайдеры → API → общий результат, конкурентный опрос через gather, ограничение нагрузки семафором и лимитером для GitHub

## Установка и запуск
Для запуска проекта достаточно 
``` bash
git clone <url репозитория>
cd <папка проекта>
uv sync
# создать .env на основе .env.example
uv run main.py
```

## Структура проекта
```
├── config.py
├── formatters.py
├── handlers
│   ├── comands.py
│   ├── __init__.py
│   └── search.py
├── logging_config.py
├── main.py
├── pyproject.toml
├── README.md
├── services
│   ├── __init__.py
│   ├── providers
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── github.py
│   │   ├── stack_overflow.py
│   │   └── wikipedia.py
│   └── search_services.py
├── setup.py
├── states.py
└── uv.lock
```
