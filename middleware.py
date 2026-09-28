from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.dispatcher.flags import get_flag
from aiogram.types import Message
from limits import RateLimitItem
from limits.aio.strategies import RateLimiter


class RateLimitMiddleware(BaseMiddleware):
    def __init__(self, limiter: RateLimiter, warn_limit: RateLimitItem):
        self.limiter = limiter
        self.warn_limit = warn_limit

    async def __call__(self, handler: Callable[[Message, dict[str, Any]], Awaitable[Any]], event: Message, data: dict[str, Any]) -> Any:
        limit: RateLimitItem | None = get_flag(data, "rate_limit")
        if limit is None or event.from_user is None:
            return await handler(event, data)

        key = data["handler"].callback.__name__
        user_id = event.from_user.id

        if await self.limiter.hit(limit, key, user_id):
            return await handler(event, data)

        if await self.limiter.hit(self.warn_limit, f"{key}:warn", user_id):
            await event.answer("Слишком часто, подождите немного")
        return None


class ActiveSearchMiddleware(BaseMiddleware):
    def __init__(self, limiter: RateLimiter, warn_limit: RateLimitItem):
        self.limiter = limiter
        self.warn_limit = warn_limit
        self.active: set[int] = set()

    async def __call__(self, handler: Callable[[Message, dict[str, Any]], Awaitable[Any]], event: Message, data: dict[str, Any]) -> Any:
        single_active: bool | None = get_flag(data, "single_active", default=False)

        if not single_active or event.from_user is None:
            return await handler(event, data)
        
        key = data["handler"].callback.__name__
        user_id = event.from_user.id        
        if user_id in self.active:
            if await self.limiter.hit(self.warn_limit,  f"{key}:active_warn", user_id):
                await event.answer("Предыдущий поиск ещё выполняется, дождитесь результата")
            return None

        self.active.add(user_id)
        try:
            return await handler(event, data)
        finally:
            self.active.discard(user_id)
