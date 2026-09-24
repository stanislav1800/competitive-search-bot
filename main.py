import asyncio
import logging

from logging_config import setup_logging
from setup import init_bot

logger = logging.getLogger(__name__)


async def main():
    bot, dp = await init_bot()
    logger.info("Starting bot...")
    await dp.start_polling(bot)
    logger.info("Bot stopped")


if __name__ == "__main__":
    setup_logging()
    asyncio.run(main())
