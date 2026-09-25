import asyncio
import logging

from services.providers.base import ProviderResponse, SearchProviders

logger = logging.getLogger(__name__)


class SearchService:
    def __init__(self, providers: list[SearchProviders]) -> None:
        self.providers = providers

    async def start(self) -> None:
        await asyncio.gather(*(provider.setup() for provider in self.providers), return_exceptions=True)

    async def search(self, query: str) -> list[ProviderResponse]:
        return await asyncio.gather(*(provider.search(query) for provider in self.providers))
