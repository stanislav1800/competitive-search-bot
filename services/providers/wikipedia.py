from dataclasses import dataclass
from html import escape, unescape
import re

from .base import SearchProviders, SearchResult

@dataclass
class WikipediaResult(SearchResult):
    description: str

    def render(self) -> str:
        text = f'<a href="{self.url}"><b>{escape(self.title)}</b></a>\n'
        if self.description:
            description = unescape(self.description)
            description = re.sub(r"</?span[^>]*>", "", description)
            description = escape(description)
            text += f"{description}\n"
        return text


class WikipediaProviders(SearchProviders):
    url: str = "https://en.wikipedia.org/w/api.php"
    name: str = "Wikipedia"

    async def get(self, query: str) -> list[WikipediaResult] | None:
        params = {
            "action": "query",
            "format": "json",
            "list": "search",
            "srsearch": query,
            "srlimit": 5,
        }

        async with self.session.get(self.url, params=params, timeout=30) as resp:
            resp.raise_for_status()
            data = await resp.json()

            if "query" in data:
                return [
                    WikipediaResult(
                        title=data["title"],
                        url=f"https://en.wikipedia.org/?curid={data['pageid']}",
                        source=self.name,
                        description=data["snippet"],
                    ) 
                    for data in data["query"]["search"]
                ]
