
from .base import SearchProviders, SearchResult


class GitHubProvider(SearchProviders):
    url: str = "https://api.github.com/search/repositories"

    async def get(self, query: str) -> list[SearchResult] | None:
        params = {
            "q": query,
            "per_page": 5,
        }
        async with self.session.get(self.url, params=params) as resp:
            resp.raise_for_status()
            data = await resp.json()
            if "items" in data:
                return [
                    SearchResult(
                        title=item["full_name"],
                        description=item["description"],
                        url=item["html_url"],
                        source="GitHub",
                    )
                    for item in data["items"]
                ]
