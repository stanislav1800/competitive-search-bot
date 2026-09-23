import logging

from aiohttp import ClientSession
import asyncio

from services.providers.base import SearchResult, SearchProviders

logger = logging.getLogger(__name__)

class SearchService:
    def __init__(self, session: ClientSession, providers: list[SearchProviders]) -> None:
        self.session = session
        self.providers = providers

    async def start(self) -> None:
        await asyncio.gather(*[provider.setup() for provider in self.providers], return_exceptions=True)

    async def search(self, request: str) -> dict[str, list[SearchResult]]:
        results = {}

        responds = await asyncio.gather(*[provider.get(request) for provider in self.providers], return_exceptions=True)

        for provider, respond in zip(self.providers, responds):
                results[provider.name] = respond

        return results
