from aiogram import F, Router
from aiogram.filters import Command, CommandObject, CommandStart
from aiogram.types import LinkPreviewOptions, Message, ReplyParameters
from limits import RateLimitItemPerMinute, RateLimitItemPerSecond
from limits.aio.storage import MemoryStorage
from limits.aio.strategies import MovingWindowRateLimiter

from formatters import format_text
from services.errors import SearchError
from services.search_services import SearchService

router = Router()
limiter = MovingWindowRateLimiter(MemoryStorage())
limit = RateLimitItemPerMinute(5)
warn_limit = RateLimitItemPerSecond(1, 10)
active_search_users: set[int] = set()


@router.message(CommandStart())
async def cmd_start(msg: Message):
    await msg.answer("Бот для поиска информацию в нескольких независимых источниках. Для поиска воспользуйтесь командой /search")


@router.message(Command(commands=["search"], magic=F.args))
async def cmd_search_args(msg: Message, command: CommandObject, search: SearchService):
    user_id = msg.from_user.id
    if user_id in active_search_users:
        if await limiter.hit(warn_limit, "active_search_warn", user_id):
            await msg.answer("Предыдущий поиск ещё выполняется, дождитесь результата")
        return
    
    active_search_users.add(user_id)
    try:
        if not await limiter.hit(limit, "cmd_search", user_id):
            if await limiter.hit(warn_limit, "cmd_search_warn", user_id):
                await msg.answer("Слишком часто, подождите немного")
            return
        
        message = await msg.answer("🔎 Ищу…", reply_parameters=ReplyParameters(message_id=msg.message_id, quote=command.args))
        try:
            responses = await search.search(command.args)
        except SearchError as e:
            await message.edit_text(e.user_message)
            return
        await message.edit_text(format_text(responses), parse_mode="HTML", link_preview_options=LinkPreviewOptions(is_disabled=True))
    finally:
        active_search_users.discard(user_id)


@router.message(Command(commands=["search"]))
async def cmd_search(msg: Message):
    await msg.answer("Введите запрос вместе с командой\nПример:\n/search Python aiogram 3")
