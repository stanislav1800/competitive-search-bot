import asyncio

from aiogram import Bot, Dispatcher

from config import settings
from handlers import comands, search


async def main():
    bot = Bot(token=settings.token)
    dp = Dispatcher()

    dp.include_routers(
        comands.router,
        search.router,
    )

    print("Starting bot...")
    try:
        await dp.start_polling(bot)
    finally:
        print("Bot stopped")


if __name__ == "__main__":
    asyncio.run(main())
