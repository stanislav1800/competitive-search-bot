import asyncio
import json
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from http import HTTPStatus

from aiohttp import (
    ClientConnectionError,
    ClientError,
    ClientResponseError,
    ClientSession,
)
from tenacity import (
    AsyncRetrying,
    before_sleep_log,
    retry_if_exception,
    stop_after_attempt,
    stop_after_delay,
    wait_exponential,
)

from services.errors import SearchError, SourceUnavailable

logger = logging.getLogger(__name__)


@dataclass
class SearchResult(ABC):
    title: str
    url: str
    source: str

    @abstractmethod
    def render(self) -> str: ...


@dataclass
class ProviderResponse:
    source: str
    items: list[SearchResult] = field(default_factory=list)
    error: str | None = None

    @property
    def ok(self) -> bool:
        return self.error is None


class SearchProviders(ABC):
    base_url: str
    name: str

    def __init__(self, session: ClientSession, base_url: str | None = None):
        self.session = session
        if base_url is not None:
            self.base_url = base_url

    async def search(self, query: str) -> ProviderResponse:
        response = ProviderResponse(self.name)
        try:
            async for attempt in AsyncRetrying(
                stop=stop_after_attempt(3) | stop_after_delay(10),
                wait=wait_exponential(multiplier=0.5, max=2),
                retry=retry_if_exception(self._is_transient),
                before_sleep=before_sleep_log(logger, logging.WARNING),
                reraise=True,
            ):
                with attempt:
                    async with asyncio.timeout(4):
                        response.items = await self._fetch(query)
        except SearchError as e:
            logger.warning("%s: %s", self.name, e)
            response.error = e.user_message
        except (TimeoutError, ClientError, json.JSONDecodeError) as e:
            logger.warning("%s: %r", self.name, e)
            response.error = SourceUnavailable.user_message
        except Exception:
            logger.exception("Неожиданная ошибка в %s", self.name)
            response.error = SourceUnavailable.user_message
        return response

    @abstractmethod
    async def _fetch(self, query: str) -> list[SearchResult]: ...

    async def setup(self) -> None: ...

    @staticmethod
    def _is_transient(exc: BaseException) -> bool:
        if isinstance(exc, ClientResponseError):
            return exc.status >= HTTPStatus.INTERNAL_SERVER_ERROR
        return isinstance(exc, (TimeoutError, ClientConnectionError))
