import logging
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path


def setup_logging(level: str = "INFO") -> None:
    Path("logs").mkdir(exist_ok=True)

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    console = logging.StreamHandler()
    console.setFormatter(formatter)

    file = TimedRotatingFileHandler(
        filename="logs/bot.log",
        when="midnight",
        backupCount=30,
        encoding="utf-8",
    )
    file.setFormatter(formatter)

    logging.basicConfig(level=level, handlers=[console, file])
