import asyncio
import logging
import types
from typing import Optional

import discord
from dotenv import find_dotenv, load_dotenv
from loguru import logger
from os import environ
from pathlib import Path
from enum import Enum

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

current_mode = mode.DEBUG

logging_level = "DEBUG" if current_mode == mode.LIVE else "DEBUG"
log_discord = True if current_mode == mode.DEBUG else False
log_hypercorn = True if current_mode == mode.DEBUG else False
log_sql = True if current_mode == mode.DEBUG else False

hypercorn_level_override = "DEBUG"
root_log_level = logging.DEBUG
loguru_fmt = "<le>{time:hh:mm:ss:A}</le> | <magenta>{level}</magenta> | {name} |<w>{message}</w>"

schema_migrations_dir = f"{cwd_abs}/server/db/schema_migrations"
db_path = f"{cwd_abs}/main.db"

cogs_dir = f"{cwd_abs}/bot/cogs"

retry_CD_s = 20
max_retry = 4

api_shutdown = asyncio.Event()
bind_addr = "127.0.0.1:5667"

bot_token= get_env_var("bot_token") if current_mode == mode.LIVE else get_env_var("testing_bot_token")

api_token = get_env_var("api_token")
authorized_guild = 1467227640573460733 if current_mode == mode.LIVE else 1237911337057648790

lurkr_tick = 10
lurkr_xp = 4
lurkr_afk = False
lurkr_api_key = get_env_var("lurkr_api_key")
lurkr_guilds = [authorized_guild]
lurkr_close = lambda: None

bot_administrators = [
    1086979130572165231
]


apiClient: Optional[discord.Client] = None

def setApiClient(bot: discord.Client):
    global apiClient
    apiClient = bot