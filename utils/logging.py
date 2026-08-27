import logging
import sys
from logging import DEBUG

from config import settings
from loguru import logger


class InterceptHandler(logging.Handler):
    def emit(self, record):

        if not settings.log_hypercorn and (record.name.startswith("hypercorn") or record.name.startswith("quart")):
            return
        if not settings.log_discord and record.name.startswith("discord"):
            return
        if not settings.log_sql and record.name.startswith("aiosqlite"):
            return

        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        if record.name == "hypercorn.access" or "access":
            level = settings.hypercorn_level_override

        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1
        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())

def create_logging_list():
    list_logger = [
        "quart",
        "quart.app",
        "quart.server",
        "hypercorn.access",
        "hypercorn.error",
        "discord",
        "discord.http",
        "discord.gateway",
        "discord.websocket",
        "aiosqlite",
        "lurkr"
    ]
    return list_logger

def setup_logging():
    logger.remove(0)

    logger.add(sink=sys.stderr, level=settings.logging_level, format=settings.loguru_fmt)

    logging.root.handlers = [InterceptHandler()]
    logging.root.setLevel(settings.root_log_level)

    list_of_loggers = create_logging_list()

    for name in list_of_loggers:
        logg = logging.getLogger(name)
        logg.handlers = []
        logg.propagate = True
        logg.setLevel(DEBUG)

