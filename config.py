import asyncio
import logging
from typing import Optional

import discord
from dotenv import find_dotenv, load_dotenv
from loguru import logger
from os import environ
from pathlib import Path

cwd_abs = Path(__file__).parent
load_dotenv(find_dotenv())

# js wanted a short name
def eval(k: str):
    return environ.get(k.upper()) or environ.get(k.lower()) or environ.get(k)

logging_level = "DEBUG"
log_discord = False
log_hypercorn = False
log_sql = True
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

bot_token = eval("bot_token")
api_token = eval("api_token")
lurkr_api_key = eval("lurkr_api_key")
authorized_guild = 1237911337057648790

bot_administrators = [
    1086979130572165231
]

apiClient: Optional[discord.Client] = None

def setApiClient(bot: discord.Client):
    global apiClient
    apiClient = bot