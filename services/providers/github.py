
from .base import SearchProviders, SearchResult


class GitHubProvider(SearchProviders):
    url: str = "https://api.github.com/search/repositories"
    name: str = "GitHub"

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
