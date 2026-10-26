# Competitive Search Bot

Telegram-бот, который по одному запросу одновременно ищет материалы в нескольких независимых источниках и присылает объединённый результат. Сейчас подключены **Wikipedia**, **GitHub** и **StackOverflow**.

## Возможности

- `/start` — приветствие и краткая справка.
- `/search <запрос>` — параллельный поиск во всех источниках, до 5 результатов из каждого:
  - **Wikipedia** — заголовок статьи и фрагмент текста;
  - **GitHub** — репозиторий, описание, количество звёзд и язык;
  - **StackOverflow** — вопрос, рейтинг, число ответов и наличие принятого ответа.
- Если поиск длится дольше 0,5 с, бот сразу отвечает «🔎 Ищу…» и потом заменяет это сообщение результатом.
- Ответ форматируется в HTML и при необходимости разбивается на несколько сообщений (лимит Telegram — 4096 символов, считается в UTF-16).
- Если один источник упал, остальные результаты всё равно приходят, а для упавшего показывается понятная ошибка.

## Устойчивость и ограничения нагрузки

| Механизм | Где | Что делает |
|---|---|---|
| Rate limit на пользователя | `middleware.py` → `RateLimitMiddleware` | не больше 5 запросов `/search` в минуту на пользователя (moving window, `limits`) |
| Один активный поиск | `middleware.py` → `ActiveSearchMiddleware` | пока предыдущий поиск пользователя не завершился, новый не запускается |
| Глобальный семафор | `services/search_services.py` | не больше `MAX_CONCURRENT_SEARCHES` поисков одновременно, остальные получают «Бот перегружен» |
| Лимитер GitHub | `services/providers/github.py` | `aiolimiter`: 1 запрос / 6 с без токена, 1 запрос / 2 с с валидным токеном |
| Повторы | `services/providers/base.py` | `tenacity`: 1 повтор при таймауте, ошибке соединения или 5xx |
| Таймаут | `services/providers/base.py` | 3 с на одну попытку запроса к источнику |
| Кэш | `services/providers/base.py` | `TTLCache` на 1000 запросов с TTL 10 минут для каждого провайдера |
| Ограничение длины запроса | `handlers/comands.py` | максимум 256 символов |

Предупреждения «слишком часто» и «предыдущий поиск ещё выполняется» отправляются не чаще одного раза в 10 секунд, чтобы бот сам не превращался в спам.

## Архитектура

```
Telegram → Middlewares → Handler (/search) → SearchService → провайдеры → внешние API
                                                    │
                                    asyncio.gather по всем провайдерам
                                                    ↓
                               list[ProviderResponse] → formatters → сообщения
```

- **`SearchProviders`** (`services/providers/base.py`) — базовый класс провайдера. Он берёт на себя кэш, повторы, таймауты и превращение исключений в `ProviderResponse.error`. Наследнику достаточно реализовать `_fetch(query)` и, если нужно, `setup()`.
- **`SearchResult`** — результат поиска; каждый провайдер задаёт свой dataclass с методом `render()`, который возвращает HTML-фрагмент.
- **`SearchService`** — опрашивает всех провайдеров конкурентно и ограничивает общее число одновременных поисков.
- **`services/errors.py`** — иерархия `SearchError` с сообщениями для пользователя (`SourceUnavailable`, `SourceRateLimited`, `ServiceOverloaded`).
- Общая `aiohttp.ClientSession` и `SearchService` создаются в `on_startup` (`setup.py`) и передаются в хендлеры через DI aiogram.

### Как добавить новый источник

1. Создать файл в `services/providers/`, описать dataclass-наследник `SearchResult` с `render()`.
2. Унаследоваться от `SearchProviders`, задать `name` и `base_url`, реализовать `_fetch()`.
3. Добавить экземпляр провайдера в список `providers` в `setup.py`.

## Технологии

- Python 3.12+
- [aiogram 3](https://docs.aiogram.dev/) — Telegram Bot API
- aiohttp — HTTP-клиент
- aiolimiter, limits — ограничение частоты запросов
- tenacity — повторы запросов
- cachetools — TTL-кэш
- python-dotenv — конфигурация из `.env`
- ruff — линтер (dev)
- [uv](https://docs.astral.sh/uv/) — управление зависимостями
- Docker, Docker Compose — развёртывание

## Установка и запуск

```bash
git clone https://github.com/stanislav1800/competitive-search-bot.git
cd competitive-search-bot
uv sync
cp .env.example .env   # заполнить переменные
uv run main.py
```

### Docker

```bash
cp .env.example .env   # заполнить переменные
docker compose up -d --build
```

- Переменные берутся из `.env` через `env_file`, сам файл в образ не копируется.
- `LOG_DIRS` из `.env` задаёт директорию логов на хосте (если не задана — `./logs`). Она монтируется в контейнер как `/app/logs`, и внутри контейнера бот пишет логи туда.
- Контейнер перезапускается автоматически (`restart: unless-stopped`).
- Бот работает через long polling, открывать порты не нужно.

Полезные команды:

```bash
docker compose logs -f bot    # логи в реальном времени
docker compose restart bot    # перезапуск
docker compose down           # остановка
```

## Конфигурация

Переменные окружения (файл `.env`):

| Переменная | Обязательна | По умолчанию | Описание |
|---|---|---|---|
| `BOT_TOKEN` | да | — | токен Telegram-бота от [@BotFather](https://t.me/BotFather) |
| `GIT_TOKEN` | нет | — | токен GitHub; проверяется при старте и ускоряет лимит запросов к GitHub с 1/6 с до 1/2 с |
| `LOG_LEVEL` | нет | `INFO` | уровень логирования |
| `LOG_DIRS` | нет | — | директория для файла `bot.log` (ротация в полночь, хранится 30 файлов); без неё логи пишутся только в консоль |
| `WIKIPEDIA_URL` | нет | `https://en.wikipedia.org` | базовый URL Wikipedia |
| `GITHUB_URL` | нет | `https://api.github.com` | базовый URL GitHub API |
| `STACK_OVERFLOW_URL` | нет | `https://api.stackexchange.com` | базовый URL StackExchange API |
| `MAX_CONCURRENT_SEARCHES` | нет | `20` | сколько поисков бот выполняет одновременно |

## Структура проекта

```
├── main.py                  # точка входа: логирование и запуск polling
├── setup.py                 # сборка Bot/Dispatcher, middlewares, startup/shutdown
├── config.py                # настройки из переменных окружения
├── logging_config.py        # консольный и файловый логгер
├── middleware.py            # rate limit и «один активный поиск»
├── Dockerfile               # образ на базе uv + Python 3.12
├── docker-compose.yml       # запуск бота в контейнере
├── formatters.py            # HTML-форматирование и разбивка на сообщения
├── handlers
│   └── comands.py           # /start и /search
└── services
    ├── errors.py            # ошибки с сообщениями для пользователя
    ├── search_services.py   # SearchService
    └── providers
        ├── base.py          # базовый провайдер: кэш, повторы, таймауты
        ├── github.py
        ├── stack_overflow.py
        └── wikipedia.py
```

## Разработка

```bash
uv run ruff check .
uv run ruff format .
```
