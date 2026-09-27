import logging
from dataclasses import dataclass
from html import escape
from http import HTTPStatus

from aiohttp import ClientSession
from aiolimiter import AsyncLimiter

from services.errors import SourceRateLimited
from services.providers.base import SearchProviders, SearchResult

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
    base_url: str = "https://api.github.com"
    name: str = "GitHub"

    def __init__(
        self, 
        session: ClientSession, 
        base_url: str | None = None, 
        token: str | None = None,
    ) -> None:
        super().__init__(session, base_url)
        self.token = token
        self._limiter = AsyncLimiter(1, 6)
        self.headers = self.session.headers
        if token is not None:
            self.headers = {
                "Authorization": f"token {self.token}",
                **self.session.headers
            }

    async def _check_token(self) -> bool:
        headers = {
            "Authorization": f"token {self.token}",
            **self.session.headers
        }
        async with self.session.get(f"{self.base_url}/user", headers=headers) as resp:
            if resp.status == HTTPStatus.OK:
                data = await resp.json()
                logger.info(f"Токен валиден, пользователь: {data['login']}")
                self.headers = headers
                return True
            elif resp.status == HTTPStatus.UNAUTHORIZED:
                logger.info("Токен невалиден или истёк")
                return False
            resp.raise_for_status()

    async def _fetch(self, query: str) -> list[GitHubResult]:
        params = {
            "q": query,
            "per_page": 5,
        }

        async with self._limiter:                                                                           # noqa: SIM117
            async with self.session.get(f"{self.base_url}/search/repositories", params=params, headers=self.headers, timeout=30) as resp:
                if resp.status == HTTPStatus.TOO_MANY_REQUESTS or (resp.status == HTTPStatus.FORBIDDEN and resp.headers.get("X-RateLimit-Remaining") == "0"):
                    raise SourceRateLimited()
                resp.raise_for_status()
                data = await resp.json()
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

    async def setup(self) -> None:
        if await self._check_token():
            self._limiter = AsyncLimiter(1, 2)
