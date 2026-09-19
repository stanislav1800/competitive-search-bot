from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from states import Search

router = Router()

@router.message(Search.search)
async def find_result(msg: Message, state: FSMContext):
    request = msg.text
    await state.update_data(request=request)
    await msg.reply("Запрос в работе")
