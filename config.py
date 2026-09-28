import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    token: str = os.environ["BOT_TOKEN"]
    git_token: str | None = os.getenv("GIT_TOKEN")
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    log_dirs: str | None = os.getenv("LOG_DIRS")
    wikipedia_url: str | None = os.getenv("WIKIPEDIA_URL")
    github_url: str | None = os.getenv("GITHUB_URL")
    stack_overflow_url: str | None = os.getenv("STACK_OVERFLOW_URL")
    max_concurrent_searches: int = int(os.getenv("MAX_CONCURRENT_SEARCHES") or 20)


settings = Settings()
