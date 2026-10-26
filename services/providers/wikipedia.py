import re
from dataclasses import dataclass
from html import escape, unescape

from .base import SearchProviders, SearchResult, shorten


@dataclass
class WikipediaResult(SearchResult):
    description: str

    def render(self) -> str:
        text = f'<a href="{self.url}"><b>{escape(self.title)}</b></a>\n'
        if self.description:
            description = unescape(self.description)
            description = re.sub(r"</?span[^>]*>", "", description)
            description = escape(shorten(description))
            text += f"{description}\n"
        return text


class WikipediaProviders(SearchProviders):
    base_url: str = "https://en.wikipedia.org"
    name: str = "Wikipedia"

    async def _fetch(self, query: str) -> list[WikipediaResult]:
        params = {
            "action": "query",
            "format": "json",
            "list": "search",
            "srsearch": query,
            "srlimit": 5,
        }

        async with self.session.get(f"{self.base_url}/w/api.php", params=params, timeout=30) as resp:
            resp.raise_for_status()
            data = await resp.json()
            return [
                WikipediaResult(
                    title=data["title"],
                    url=f"{self.base_url}/?curid={data['pageid']}",
                    source=self.name,
                    description=data["snippet"],
                ) 
                for data in data["query"]["search"]
            ]
