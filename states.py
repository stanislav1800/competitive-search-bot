from aiogram.fsm.state import State, StatesGroup


class Search(StatesGroup):
    search = State()
