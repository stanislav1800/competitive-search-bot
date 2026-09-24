import asyncio
import logging

from aiogram import Bot
from aiogram.types import LinkPreviewOptions

from formatters import format_text
from services.search_services import SearchService

logger = logging.getLogger(__name__)


async def worker(queue: asyncio.Queue, bot: Bot, service: SearchService) -> None:
    while True:
        data = await queue.get()
        if data is None:
            break
        query, chat_id, message_id = data
        try:
            responses = await service.search(query)
            await bot.edit_message_text(format_text(responses), chat_id=chat_id, message_id=message_id, parse_mode="HTML", link_preview_options=LinkPreviewOptions(is_disabled=True))
        except Exception:
            logger.exception(f"Ошибка при формировании отчета по запросу '{query}' для пользователя {chat_id}")
            await bot.edit_message_text("Произошла ошибка при формировании отчета", chat_id=chat_id, message_id=message_id)
        finally:
            queue.task_done()
        