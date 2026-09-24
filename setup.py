import asyncio

from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from aiohttp import ClientSession

from config import settings
from handlers import comands, search
from services.providers.github import GitHubProvider
from services.providers.stack_overflow import StackOverflowProvider
from services.providers.wikipedia import WikipediaProviders
from services.search_services import SearchService
from worker import worker


async def init_bot() -> tuple[Bot, Dispatcher]:
    bot = Bot(token=settings.token)
    dp = Dispatcher()
    dp.include_routers(
        comands.router,
        search.router,
    )
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    return bot, dp


async def on_startup(bot: Bot, dispatcher: Dispatcher):
    session = ClientSession(
        headers={
            "User-Agent": "competitive-search-bot/0.1 (https://github.com/stanislav1800/competitive-search-bot)",
        }
    )

    providers = [
        WikipediaProviders(session), 
        GitHubProvider(session, settings.git_token), 
        StackOverflowProvider(session)
    ]
    search_service = SearchService(session, providers)
    await search_service.start()
    await set_commands(bot)

    queue = asyncio.Queue(50)
    workers = [asyncio.create_task(worker(queue, bot, search_service)) for _ in range(4)]

    dispatcher["session"] = session
    dispatcher["workers"] = workers
    dispatcher["queue"] = queue


async def on_shutdown(dispatcher: Dispatcher):
    workers: list[asyncio.Task] = dispatcher["workers"]
    queue: asyncio.Queue = dispatcher["queue"]
    for _ in range(len(workers)):
        queue.put_nowait(None)

    session: ClientSession = dispatcher["session"]
    await session.close()


async def set_commands(bot: Bot):
    await bot.set_my_commands(
        [
            BotCommand(command="start", description="Старт"),
            BotCommand(command="search", description="Поиск данных по различным источникам"),
        ]
    )
