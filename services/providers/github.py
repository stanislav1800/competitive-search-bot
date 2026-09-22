import logging

from aiohttp import ClientSession
from aiolimiter import AsyncLimiter

from .base import SearchProviders, SearchResult

logger = logging.getLogger(__name__)

class GitHubProvider(SearchProviders):
    url: str = "https://api.github.com/search/repositories"
    name: str = "GitHub"

    def __init__(self, session: ClientSession, token: str | None = None) -> None:
        super().__init__(session)
        self.token = token
        self.limiter = AsyncLimiter(10, 60)
        self.headers = {
            "Authorization": f"token {self.token}",
            **self.session.headers
        }

    async def _check_token(self) -> bool:
        async with self.session.get("https://api.github.com/user", headers=self.headers) as resp:
            if resp.status == 200:
                data = await resp.json()
                logger.info(f"Токен валиден, пользователь: {data['login']}")
                return True
            elif resp.status == 401:
                logger.info("Токен невалиден или истёк")
                return False
            else:
                resp.raise_for_status()
                   
    async def get(self, query: str) -> list[SearchResult] | None:
        params = {
            "q": query,
            "per_page": 5,
        }

        async with self.limiter:
            async with self.session.get(self.url, params=params, headers=self.headers) as resp:
                if resp.status == 200:
                    data = await resp.json()

                    if "items" in data:
                        return [
                            SearchResult(
                                title=item["full_name"],
                                url=item["html_url"],
                                source=self.name,
                                extra={
                                    "stars": item["stargazers_count"],
                                    "language": item["language"],
                                    "description": item["description"],
                                }
                            )
                            for item in data["items"]
                        ]
                    
                else:
                    resp.raise_for_status()

    async def setup(self) -> None:
        if await self._check_token():
            self.limiter = AsyncLimiter(30, 60)
