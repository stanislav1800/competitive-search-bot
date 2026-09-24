from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import LinkPreviewOptions, Message

from formatters import format_text
from services.search_services import SearchService
from states import Search

router = Router()


@router.message(Search.search)
async def find_result(msg: Message, state: FSMContext, search: SearchService):
    if msg.text:
        message = await msg.reply("🔎 Ищу…")
        responses = await search.search(msg.text)
        await message.edit_text(format_text(responses), parse_mode="HTML", link_preview_options=LinkPreviewOptions(is_disabled=True))
        await state.clear()
    else:
        await msg.reply("Введите текст")
