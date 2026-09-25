import asyncio
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from aiohttp import ClientError, ClientResponseError, ClientSession

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


class ProviderError(Exception):
    user_message = "Сервис временно недоступен"


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
            async with asyncio.timeout(10):
                items = await self._fetch(query)
                response.items = items
        except ProviderError as e:
            logger.warning("%s: %s", self.name, e)
            response.error = e.user_message
        except TimeoutError:
            logger.warning("%s: таймаут", self.name)
            response.error = f"{self.name} сейчас перегружен"
        except ClientResponseError as e:
            logger.warning("%s: HTTP %s", self.name, e.status)
            response.error = "Сервис временно недоступен"
        except ClientError:
            logger.warning("%s: сетевая ошибка", self.name, exc_info=True)
            response.error = "Сервис недоступен"
        except Exception:
            logger.exception("Неожиданная ошибка в %s", self.name)
            response.error = "Сервис временно недоступен"
        return response

    @abstractmethod
    async def _fetch(self, query: str) -> list[SearchResult]: ...

    async def setup(self) -> None: ...
