from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import LinkPreviewOptions, Message

from formatters import format_text
from services.search_services import get_resources
from states import Search

router = Router()

@router.message(Search.search)
async def find_result(msg: Message, state: FSMContext):
    request = msg.text
    await state.update_data(request=request)

    items = await get_resources(request)
    text = format_text(items)

    await msg.reply(text, parse_mode="HTML", link_preview_options=LinkPreviewOptions(is_disabled=True))
