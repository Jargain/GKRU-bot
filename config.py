import asyncio
import logging
import types
from typing import Optional, Literal, Dict

import discord
from dotenv import find_dotenv, load_dotenv
from loguru import logger
from os import environ
from pathlib import Path
from enum import Enum
from simplefilesettings.json import JSONClass

cwd_abs = Path(__file__).parent
dv_path = find_dotenv()
logger.info(f"Loading .env from: {dv_path}")
load_dotenv(dv_path)

class mode(Enum):
    TESTING = 1,
    DEBUG = 2,
    LIVE = 3

# js wanted a short name
def get_env_var(k: str):
    return environ.get(k.upper()) or environ.get(k.lower()) or environ.get(k)

current_mode = mode.LIVE

class _Settings(JSONClass):

    logging_level: str = "DEBUG" if current_mode == mode.LIVE else "DEBUG"
    log_discord: bool = True if current_mode == mode.DEBUG else False
    log_hypercorn: bool = True if current_mode == mode.DEBUG else False
    log_sql: bool = True if current_mode == mode.DEBUG else False

    hypercorn_level_override: str = "DEBUG"
    root_log_level: Literal[10] = logging.DEBUG
    loguru_fmt: str = "<le>{time:hh:mm:ss:A}</le> | <magenta>{level}</magenta> | {name} |<w>{message}</w>"

    schema_migrations_dir: str = f"{cwd_abs}/server/db/schema_migrations"
    db_path: str = f"{cwd_abs}/main.db"

    cogs_dir: str = f"{cwd_abs}/bot/cogs"

    retry_CD_s: int = 20
    max_retry: int = 4

    bot_token : str = str(get_env_var("bot_token") if current_mode == mode.LIVE else get_env_var("testing_bot_token"))
    authorized_guild : int = 1532717797292113971 if current_mode == mode.LIVE else 1237911337057648790

    lurkr_tick: int = 10
    lurkr_xp: int = 4
    lurkr_afk : bool = False
    lurkr_api_key : str = str(get_env_var("lurkr_api_key"))
    lurkr_guilds : list[int] = [authorized_guild]
    lurkr_updatechannel: int = 1539970407115919470 if current_mode == mode.LIVE else 1540825740386377828

    bot_administrators: list[int] = [
        1086979130572165231
    ]

    logging_channel : int = 1541927704096415825
    permission_integer_roles : Dict[str, int] = {}
    event_channels : list[int] = []
    warn_logs_channel : int = 1541956022057574450


settings = _Settings()

settings.authorized_guild = 1532717797292113971 if current_mode == mode.LIVE else 1237911337057648790
settings.bot_token = str(get_env_var("bot_token") if current_mode == mode.LIVE else get_env_var("testing_bot_token"))
settings.lurkr_updatechannel = 1539970407115919470 if current_mode == mode.LIVE else 1540825740386377828
settings.lurkr_guilds = [settings.authorized_guild]

settings.logging_level = "DEBUG" if current_mode == mode.LIVE else "DEBUG"
settings.log_discord = True if current_mode == mode.DEBUG else False
settings.log_hypercorn = True if current_mode == mode.DEBUG else False
settings.log_sql = True if current_mode == mode.DEBUG else False


lurkr_close = lambda: None
api_shutdown = asyncio.Event()

apiClient: Optional[discord.Client] = None

def setApiClient(bot: discord.Client):
    global apiClient
    apiClient = bot