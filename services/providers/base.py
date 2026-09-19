from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

from aiohttp import ClientSession


@dataclass
class SearchResult:
    title: str
    url: str
    source: str
    extra: dict[str, Any] = field(default_factory=dict)



class SearchProviders(ABC):
    url: str
    name: str

    def __init__(self, session: ClientSession):
        self.session = session

    @abstractmethod
    async def get(self) -> SearchResult:
        pass
