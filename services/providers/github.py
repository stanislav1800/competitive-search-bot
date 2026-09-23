from html import escape
import logging
from dataclasses import dataclass

from aiohttp import ClientSession
from aiolimiter import AsyncLimiter

from .base import SearchProviders, SearchResult

logger = logging.getLogger(__name__)


@dataclass
class GitHubResult(SearchResult):
    stars: int
    language: str | None
    description: str | None

    def render(self) -> str:
        text = f'<a href="{self.url}"><b>{escape(self.title)}</b></a>\n'
        if self.description:
            text += f"{escape(self.description)}\n"
        text += f"⭐ {self.stars}"
        if self.language:
            text += f" · {escape(self.language)}"
        text += "\n"
        return text


class GitHubProvider(SearchProviders):
    url: str = "https://api.github.com/search/repositories"
    name: str = "GitHub"

    def __init__(self, session: ClientSession, token: str | None = None) -> None:
        super().__init__(session)
        self.token = token
        self._limiter = AsyncLimiter(10, 60)
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
                   
    async def get(self, query: str) -> list[GitHubResult] | None:
        params = {
            "q": query,
            "per_page": 5,
        }

        async with self._limiter:
            async with self.session.get(self.url, params=params, headers=self.headers, timeout=30) as resp:
                if resp.status == 200:
                    data = await resp.json()

                    if "items" in data:
                        return [
                            GitHubResult(
                                title=item["full_name"],
                                url=item["html_url"],
                                source=self.name,
                                stars=item["stargazers_count"],
                                language=item["language"],
                                description=item["description"],
                            )
                            for item in data["items"]
                        ]
                    
                else:
                    resp.raise_for_status()

    async def setup(self) -> None:
        if await self._check_token():
            self._limiter = AsyncLimiter(30, 60)
