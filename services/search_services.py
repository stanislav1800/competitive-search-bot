from aiohttp import ClientSession

from services.providers.base import SearchResult
from services.providers.github import GitHubProvider
from services.providers.stack_overflow import StackOverflowProvider
from services.providers.wikipedia import WikipediaProviders


async def get_resources(request: str) -> dict[str, list[SearchResult]]:
    results = {}

    async with ClientSession(
            headers={
                "User-Agent": "competitive-search-bot/0.1 (https://github.com/<аккаунт>/competitive-search-bot)",
            }
        ) as session:
        providers = [WikipediaProviders(session), GitHubProvider(session), StackOverflowProvider(session)]

        for provider in providers:
            result = await provider.get(request)
            results[provider.name] = result

        return results
