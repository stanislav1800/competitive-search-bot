from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from aiohttp import ClientSession
from limits import RateLimitItemPerSecond
from limits.aio.storage import MemoryStorage
from limits.aio.strategies import MovingWindowRateLimiter

from config import settings
from handlers import comands
from middleware import ActiveSearchMiddleware, RateLimitMiddleware
from services.providers.github import GitHubProvider
from services.providers.stack_overflow import StackOverflowProvider
from services.providers.wikipedia import WikipediaProviders
from services.search_services import SearchService


async def init_bot() -> tuple[Bot, Dispatcher]:
    bot = Bot(token=settings.token)
    dp = Dispatcher()
    dp.include_routers(
        comands.router,
    )
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    limiter = MovingWindowRateLimiter(MemoryStorage())
    warn_limit = RateLimitItemPerSecond(1, 10)
    dp.message.middleware(ActiveSearchMiddleware(limiter, warn_limit))
    dp.message.middleware(RateLimitMiddleware(limiter, warn_limit))

    return bot, dp


async def on_startup(bot: Bot, dispatcher: Dispatcher):
    session = ClientSession(
        headers={
            "User-Agent": "competitive-search-bot/0.1 (https://github.com/stanislav1800/competitive-search-bot)",
        }
    )

    providers = [
        WikipediaProviders(session, settings.wikipedia_url),
        GitHubProvider(session, settings.github_url, settings.git_token),
        StackOverflowProvider(session, settings.stack_overflow_url),
    ]
    search_service = SearchService(providers)
    await search_service.start()
    await set_commands(bot)

    dispatcher["session"] = session
    dispatcher["search"] = search_service


async def on_shutdown(dispatcher: Dispatcher):
    session: ClientSession = dispatcher["session"]
    await session.close()


async def set_commands(bot: Bot):
    await bot.set_my_commands(
        [
            BotCommand(command="start", description="Старт"),
            BotCommand(command="search", description="Поиск данных по различным источникам"),
        ]
    )
