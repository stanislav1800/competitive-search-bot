
from .base import SearchProviders, SearchResult


class StackOverflowProvider(SearchProviders):
    url: str = "https://api.stackexchange.com/2.3/search/advanced"
    name: str = "StackOverflow"

    async def get(self, query: str) -> list[SearchResult] | None:
        params = {
            "q": query,
            "order": "desc",
            "sort": "relevance",
            "site": "stackoverflow",
            "pagesize": 5
        }

        async with self.session.get(self.url, params=params) as resp:
            resp.raise_for_status()
            data = await resp.json()

            if "items" in data:
                
                return [
                    SearchResult(
                        title=item["title"],
                        url=item["link"],
                        source=self.name,
                        extra={
                            "answer_count": item["answer_count"],
                            "score": item["score"],
                            "is_answered": item["is_answered"],
                        }
                    )
                    for item in data["items"]
                ]
