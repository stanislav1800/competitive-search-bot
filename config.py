import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    token: str = os.environ["BOT_TOKEN"]
    git_token: str = os.environ["GIT_TOKEN"]


settings = Settings()
