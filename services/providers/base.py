from abc import ABC, abstractmethod
import asyncio
from dataclasses import dataclass, field
import logging

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
    url: str
    name: str

    def __init__(self, session: ClientSession):
        self.session = session

    async def search(self, query: str) -> ProviderResponse:
        try:
            async with asyncio.timeout(10):
                items = await self._fetch(query)
                return ProviderResponse(self.name, items=items)
        except ProviderError as e:
            logger.warning("%s: %s", self.name, e)
            return ProviderResponse(self.name, error=e.user_message)
        except asyncio.TimeoutError:
            logger.warning("%s: таймаут", self.name)
            return ProviderResponse(self.name, error=f"{self.name} сейчас перегружен")
        except ClientResponseError as e:
            logger.warning("%s: HTTP %s", self.name, e.status)
            return ProviderResponse(self.name, error="Сервис временно недоступен")
        except ClientError:
            logger.warning("%s: сетевая ошибка", self.name, exc_info=True)
            return ProviderResponse(self.name, error="Сервис недоступен")
        except Exception:
            logger.exception("Неожиданная ошибка в %s", self.name)
            return ProviderResponse(self.name, error="Сервис временно недоступен")

    @abstractmethod
    async def _fetch(self, query: str) -> list[SearchResult]: ...

    async def setup(self) -> None: ...
