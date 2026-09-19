from aiohttp import ClientSession

from services.providers.wikipedia import WikipediaProviders


async def get_wikipedia(request: str, session: ClientSession) -> str:
    wikipedia_providers = WikipediaProviders(session)
    results = await wikipedia_providers.get(request)
    if results:
        text = "\n".join([f"""
название статьи: {result.title}
описание: {result.description}
ссылка: {result.url}
название источника: {result.source}
"""
            for result in results
        ])
        return text


async def get_resources(request: str) -> str:
    async with ClientSession(
            headers={
                "User-Agent": "competitive-search-bot/0.1 (https://github.com/<аккаунт>/competitive-search-bot)",
            }
        ) as session:
        return await get_wikipedia(request, session)
