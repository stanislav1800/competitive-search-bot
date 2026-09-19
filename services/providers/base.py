from abc import ABC, abstractmethod
from dataclasses import dataclass

from aiohttp import ClientSession


@dataclass
class SearchResult:
    title: str
    description: str
    url: str
    source: str


class SearchProviders(ABC):

    def __init__(self, session: ClientSession):
        self.session = session

    @abstractmethod
    async def get(self) -> SearchResult:
        pass
