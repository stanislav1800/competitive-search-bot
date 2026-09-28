from aiogram import F, Router
from aiogram.filters import Command, CommandObject, CommandStart
from aiogram.types import LinkPreviewOptions, Message, ReplyParameters
from limits import RateLimitItemPerMinute

from formatters import format_text
from services.errors import SearchError
from services.search_services import SearchService

router = Router()


@router.message(CommandStart())
async def cmd_start(msg: Message):
    await msg.answer("Бот для поиска информацию в нескольких независимых источниках. Для поиска воспользуйтесь командой /search")


@router.message(
    Command(commands=["search"], magic=F.args), 
    flags={"rate_limit": RateLimitItemPerMinute(5), "single_active": True},
)
async def cmd_search_args(msg: Message, command: CommandObject, search: SearchService):
    message = await msg.answer("🔎 Ищу…", reply_parameters=ReplyParameters(message_id=msg.message_id, quote=command.args))
    try:
        responses = await search.search(command.args)
    except SearchError as e:
        await message.edit_text(e.user_message)
        return
    await message.edit_text(format_text(responses), parse_mode="HTML", link_preview_options=LinkPreviewOptions(is_disabled=True))


@router.message(Command(commands=["search"]))
async def cmd_search(msg: Message):
    await msg.answer("Введите запрос вместе с командой\nПример:\n/search Python aiogram 3")
