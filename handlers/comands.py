from aiogram import Router
from aiogram.filters import Command, CommandObject, CommandStart
from aiogram.types import LinkPreviewOptions, Message, ReplyParameters

from formatters import format_text
from services.search_services import SearchService

router = Router()


@router.message(CommandStart())
async def cmd_start(msg: Message):
    await msg.answer("Бот для поиска информацию в нескольких независимых источниках. Для поиска воспользуйтесь командой /search")


@router.message(Command(commands=["search"]))
async def cmd_search(msg: Message, command: CommandObject, search: SearchService):
    if command.args:
        message = await msg.answer("🔎 Ищу…", reply_parameters=ReplyParameters(message_id=msg.message_id, quote=command.args))
        responses = await search.search(command.args)
        await message.edit_text(format_text(responses), parse_mode="HTML", link_preview_options=LinkPreviewOptions(is_disabled=True))
    else:
        await msg.answer("Введите запрос вместе с командой\nПример: /search Python aiogram 3")

