import asyncio

from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from states import Search

router = Router()


@router.message(Search.search)
async def find_result(msg: Message, state: FSMContext, queue: asyncio.Queue):
    if msg.text:
        try:
            message = await msg.reply(f"🔎 Ищу… (в очереди: {queue.qsize()})")
            queue.put_nowait((msg.text, msg.chat.id, message.message_id))
        except asyncio.QueueFull:
            await msg.reply("Бот сейчас загружен попробуйте позже")
        await state.clear()
    else:
        await msg.reply("Введите текст")
