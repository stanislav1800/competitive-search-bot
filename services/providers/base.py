from abc import ABC, abstractmethod
from dataclasses import dataclass

from aiohttp import ClientSession


@dataclass
class SearchResult(ABC):
    title: str
    url: str
    source: str

    @abstractmethod
    def render(self) -> str: ...


class SearchProviders(ABC):
    url: str
    name: str

    def __init__(self, session: ClientSession):
        self.session = session

    @abstractmethod
    async def get(self) -> SearchResult: ...

    async def setup(self) -> None: ...
