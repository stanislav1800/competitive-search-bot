from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from services.search_services import get_resources
from states import Search

router = Router()

@router.message(Search.search)
async def find_result(msg: Message, state: FSMContext):
    request = msg.text
    await state.update_data(request=request)
    text = await get_resources(request)
    if text is None:
        text = "По данной теме ничего не найдено"
    await msg.reply(text, parse_mode="HTML")
