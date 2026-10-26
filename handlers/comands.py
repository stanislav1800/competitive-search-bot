import asyncio

from aiogram import F, Router
from aiogram.filters import Command, CommandObject, CommandStart
from aiogram.types import LinkPreviewOptions, Message, ReplyParameters
from limits import RateLimitItemPerMinute

from formatters import format_messages
from services.errors import SearchError
from services.search_services import SearchService

router = Router()

SEARCH_PLACEHOLDER_DELAY = 0.5
MAX_QUERY_LENGTH = 256


@router.message(CommandStart())
async def cmd_start(msg: Message):
    await msg.answer("Бот для поиска информацию в нескольких независимых источниках. Для поиска воспользуйтесь командой /search")


@router.message(
    Command(commands=["search"], magic=F.args), 
    flags={"rate_limit": RateLimitItemPerMinute(5), "single_active": True},
)
async def cmd_search_args(msg: Message, command: CommandObject, search: SearchService):
    if len(command.args) > MAX_QUERY_LENGTH:
        await msg.answer(f"Запрос слишком длинный, максимум {MAX_QUERY_LENGTH} символов")
        return

    reply = ReplyParameters(message_id=msg.message_id, quote=command.args)
    task = asyncio.create_task(search.search(command.args))

    done, _ = await asyncio.wait({task}, timeout=SEARCH_PLACEHOLDER_DELAY)
    placeholder = None
    if not done:
        placeholder = await msg.answer("🔎 Ищу…", reply_parameters=reply)

    try:
        responses = await task
    except SearchError as e:
        texts, options = [e.user_message], {}
    else:
        texts = format_messages(responses)
        options = {"parse_mode": "HTML", "link_preview_options": LinkPreviewOptions(is_disabled=True)}

    first, *rest = texts
    if placeholder is None:
        await msg.answer(first, reply_parameters=reply, **options)
    else:
        await placeholder.edit_text(first, **options)
    for text in rest:
        await msg.answer(text, **options)


@router.message(Command(commands=["search"]))
async def cmd_search(msg: Message):
    await msg.answer("Введите запрос вместе с командой\nПример:\n/search Python aiogram 3")
