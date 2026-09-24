from dataclasses import dataclass
from html import escape

from .base import SearchProviders, SearchResult


@dataclass
class StackOverflowResult(SearchResult):
    answer_count: int
    score: int
    is_answered: bool

    def render(self) -> str:
        status = "✅ Есть принятый ответ" if self.is_answered else "❓ Без принятого ответа"
        return (
            f'<a href="{self.url}"><b>{escape(self.title)}</b></a>\n'
            f"👍 {self.score} · 💬 {self.answer_count} · {status}\n"
        )


class StackOverflowProvider(SearchProviders):
    url: str = "https://api.stackexchange.com/2.3/search/advanced"
    name: str = "StackOverflow"

    async def _fetch(self, query: str) -> list[StackOverflowResult]:
        params = {
            "q": query,
            "order": "desc",
            "sort": "relevance",
            "site": "stackoverflow",
            "pagesize": 5
        }

        async with self.session.get(self.url, params=params, timeout=30) as resp:
            if resp.status == 200:
                data = await resp.json()
                return [
                    StackOverflowResult(
                        title=item["title"],
                        url=item["link"],
                        source=self.name,
                        answer_count=item["answer_count"],
                        score=item["score"],
                        is_answered=item["is_answered"],
                    )
                    for item in data["items"]
                ]
            else:
                resp.raise_for_status()