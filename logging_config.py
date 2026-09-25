import logging
import os
from logging.handlers import TimedRotatingFileHandler


def setup_logging(level: str = "INFO", dirs: str | None = None) -> None:
    handlers = []
    file_error = None
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    console = logging.StreamHandler()
    console.setFormatter(formatter)
    handlers.append(console)

    if dirs is not None:
        try:
            file = TimedRotatingFileHandler(
                filename=os.path.join(dirs, "bot.log"),
                when="midnight",
                backupCount=30,
                encoding="utf-8",
            )
            file.setFormatter(formatter)
            handlers.append(file)
        except OSError as e:
            file_error = f"Логирование в файл отключено: {e}"

    logging.basicConfig(level=level, handlers=handlers)
    
    if file_error:
        logging.getLogger(__name__).warning(file_error)
