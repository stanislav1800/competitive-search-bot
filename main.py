import asyncio
import logging

from aiogram import Bot, Dispatcher

from config import settings
from handlers import comands, search
from logging_config import setup_logging

logger = logging.getLogger(__name__)


async def main():
    bot = Bot(token=settings.token)
    dp = Dispatcher()

    dp.include_routers(
        comands.router,
        search.router,
    )

    logger.info("Starting bot...")
    try:
        await dp.start_polling(bot)
    finally:
        logger.info("Bot stopped")


if __name__ == "__main__":
    setup_logging()
    asyncio.run(main())
