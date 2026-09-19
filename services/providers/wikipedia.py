
from .base import SearchProviders, SearchResult


class WikipediaProviders(SearchProviders):
    url = "https://ru.wikipedia.org/w/api.php"

    async def get(self, query: str) -> list[SearchResult] | None:
        params = {
            "action": "query",
            "format": "json",
            "formatversion": 2,
            "generator": "search",
            "gsrsearch": query,
            "gsrlimit": 5,
            "prop": "extracts|info",
            "exintro": 1,
            "explaintext": 1,
            "exchars": 300,
            "inprop": "url",
        }
        async with self.session.get(self.url, params=params) as resp:
            resp.raise_for_status()
            data = await resp.json()
            if "query" in data:
                pages = data["query"]["pages"]
                return [
                    SearchResult(
                        title=data["title"],
                        description=data["extract"],
                        url=data["fullurl"],
                        source="Wikipedia"
                    ) 
                    for data in pages
                ]
