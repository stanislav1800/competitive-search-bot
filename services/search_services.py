from aiohttp import ClientSession

from services.providers.github import GitHubProvider
from services.providers.wikipedia import WikipediaProviders


async def get_wikipedia(request: str, session: ClientSession) -> list:
    wikipedia_providers = WikipediaProviders(session)
    results = await wikipedia_providers.get(request)
    return results if results is not None else []

async def get_github(request: str, session: ClientSession) -> list:
    github_provider = GitHubProvider(session)
    results = await github_provider.get(request)
    return results if results is not None else []

async def get_resources(request: str) -> str:
    async with ClientSession(
            headers={
                "User-Agent": "competitive-search-bot/0.1 (https://github.com/<аккаунт>/competitive-search-bot)",
            }
        ) as session:
        wiki_items = await get_wikipedia(request, session)
        git_items = await get_github(request, session)
        items = wiki_items + git_items
        text = "\n".join([f"""
название статьи: {item.title}
описание: {item.description}
ссылка: {item.url}
название источника: {item.source}
"""
            for item in items
        ])
        return text
