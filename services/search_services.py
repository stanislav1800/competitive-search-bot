import asyncio
import logging

from services.errors import ServiceOverloaded
from services.providers.base import ProviderResponse, SearchProviders

logger = logging.getLogger(__name__)


class SearchService:
    def __init__(self, providers: list[SearchProviders], max_concurrent: int = 20) -> None:
        self.providers = providers
        self._semaphore = asyncio.Semaphore(max_concurrent)

    async def start(self) -> None:
        await asyncio.gather(*(provider.setup() for provider in self.providers), return_exceptions=True)

    async def search(self, query: str) -> list[ProviderResponse]:
        if self._semaphore.locked():
            logger.warning("Все слоты поиска заняты")
            raise ServiceOverloaded()
        
        async with self._semaphore:
            return await asyncio.gather(*(provider.search(query) for provider in self.providers))
