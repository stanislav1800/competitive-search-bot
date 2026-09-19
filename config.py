import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass
class Settings:
    token: str = os.environ["BOT_TOKEN"]


settings = Settings()
