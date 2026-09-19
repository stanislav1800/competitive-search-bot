from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from states import Search

router = Router()


@router.message(CommandStart())
async def cmd_start(msg: Message):
    pass

@router.message(Command(commands=["search"]))
async def cmd_search(msg: Message, state: FSMContext):
    await state.clear()
    await msg.answer("Введите запрос для поиска")
    await state.set_state(Search.search)
