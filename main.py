import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiohttp import ClientSession

from config import settings
from handlers import comands, search
from logging_config import setup_logging
from services.providers.github import GitHubProvider
from services.providers.stack_overflow import StackOverflowProvider
from services.providers.wikipedia import WikipediaProviders
from services.search_services import SearchService

logger = logging.getLogger(__name__)


async def main():
    bot = Bot(token=settings.token)
    dp = Dispatcher()

    async with ClientSession(
            headers={
                "User-Agent": "competitive-search-bot/0.1 (https://github.com/stanislav1800/competitive-search-bot)",
            }
        ) as session:
        providers = [WikipediaProviders(session), GitHubProvider(session, settings.git_token), StackOverflowProvider(session)]
        search_service = SearchService(session, providers)
        await search_service.start()

        dp.include_routers(
            comands.router,
            search.router,
        )

        logger.info("Starting bot...")
        try:
            await dp.start_polling(bot, search=search_service)
        finally:
            logger.info("Bot stopped")


if __name__ == "__main__":
    setup_logging()
    asyncio.run(main())
